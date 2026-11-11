# Team: ______  Members: ______  Section: ______  Mini-Project 6
"""frodo_game.py - Frodo and the Dungeon Lord. Run this file to play.

Frodo, a small Maltese in a knight's helmet, leads a party through a dungeon
that Spears the Dungeon Lord builds room by room to counter how you play.
This file holds main() with the round-by-round while loop.
"""
try:
    import pygame
except ImportError:
    print("Run: pip install pygame")
    raise SystemExit

import random

import cards
import combat
import game_data
import logbook
import movement
import spears_ai
import ui

TRAP_DAMAGE = 2
BREATHER_HEAL = 8


# ---------------------------------------------------------------- rooms

def install_room(game, room):
    """receives the game and a freshly generated room; adds its units to the map, makes it the chamber the party is in and returns its name."""
    for unit in room["units"]:
        game["units"].append(unit)
    game["chamber"] = room["id"]
    game["room_name"] = room["name"]
    game["rarity"] = min(3, 1 + room["step"] // 3)
    if room["kind"] == "side":
        game["rarity"] = min(3, game["rarity"] + 1)
    if room["entry"] is None:
        game_data.place_party(game, room["starts"])
    movement.learn_outline(game)
    movement.refresh_vision(game)
    game["doom"] = spears_ai.advance_doom(game["doom"], room["doom"], game["doom_max"])
    spears_ai.check_room_clear(game, room["id"])
    ui.show_chamber(game, room["tiles"])
    return room["name"]


def catch_breath(game):
    """receives the game; when a new chamber opens every standing hero heals; returns how many heroes healed."""
    healed = 0
    for hero in game["heroes"]:
        if not hero["exhausted"]:
            cards.heal_hero(hero, BREATHER_HEAL)
            healed += 1
    logbook.say(game, "The party catches its breath: +" + str(BREATHER_HEAL) + " HP.")
    return healed


def enter_room(game, number):
    """receives the game and the number of the chamber behind the door just opened; Spears carves and fills it from his memory of the party; returns the room's name."""
    if game["depth"] > 0:
        catch_breath(game)
    game["depth"] += 1
    game["counter"] = spears_ai.spears_counter(game["memory"])
    room = spears_ai.generate_room(game, number, game["counter"])
    install_room(game, room)
    spears_ai.fade_memory(game["memory"])
    logbook.say(game, "The party enters " + room["name"] + " (" + room["kind"] + " chamber, "
                + str(game["depth"]) + " of " + str(len(game["plan"])) + " explored).")
    logbook.say(game, room["banner"])
    logbook.add_banner(game, room["banner"])
    return room["name"]


def start_dungeon(game):
    """receives the game; plans and digs the dungeon and puts the party in the first chamber; returns how many chambers were planned."""
    count = spears_ai.build_dungeon(game)
    logbook.say(game, "Spears has dug a dungeon of " + str(count) + " chambers. His throne waits in the dark.")
    enter_room(game, 0)
    return count


# ---------------------------------------------------------------- hero actions

def spring_trap(game, hero):
    """receives the game and the hero who triggered a trap; hurts the hero, pushes the Doom Track and returns the damage."""
    combat.apply_damage(hero, TRAP_DAMAGE)
    game["stats"]["damage_taken"] += TRAP_DAMAGE
    game["doom"] = spears_ai.advance_doom(game["doom"], 1, game["doom_max"])
    logbook.say(game, hero["name"] + " springs a trap! -" + str(TRAP_DAMAGE) + " HP and Doom +1.")
    logbook.add_float(game, hero["pos"], "TRAP -" + str(TRAP_DAMAGE), "crimson")
    if hero["hp"] <= 0:
        spears_ai.hero_falls(game, hero)
    return TRAP_DAMAGE


def open_chest(game, hero, max_rarity):
    """receives the game, the hero and the best rarity allowed; gives the hero an item, applies it and returns the item's name."""
    item = cards.search_poi(hero, game["data"]["items"], max_rarity)
    if item is None:
        return ""
    game["inventory"].append(item["name"])
    game["stats"]["loot_found"] += 1
    game["memory"]["chests_opened"] += 1
    message = cards.apply_item(game, hero, item)
    logbook.say(game, hero["name"] + " finds " + item["name"] + "! " + message)
    logbook.add_float(game, hero["pos"], item["name"], "gold")
    return item["name"]


def step_on_tile(game, hero):
    """receives the game and a hero who just stopped moving; resolves the chest, shrine, trap or door under the hero; returns the tile letter."""
    col = hero["pos"][0]
    row = hero["pos"][1]
    spot = game["grid"][row][col]
    if spot not in "DdE~":
        game["grid"][row][col] = "."
    if spot == "C" or spot == "X":
        open_chest(game, hero, game["rarity"])
        if spot == "X":
            spring_trap(game, hero)
    elif spot == "P":
        open_chest(game, hero, 1)
    elif spot == "T" or spot == "H":
        spring_trap(game, hero)
    elif spot == "E":
        enter_room(game, spears_ai.door_at(game, [col, row])["to"])
    return spot


def hero_move(game, hero, tile):
    """receives the game, a hero and the tile to move to; walks the hero there tile by tile, using up moves; returns how many tiles were moved."""
    blocked = movement.model_tiles(game["units"])
    path = movement.find_path(game["grid"], hero["pos"], tile, blocked, False)
    for step in path:
        hero["pos"] = [step[0], step[1]]
        movement.refresh_vision(game)
        ui.follow(step)
        ui.pause(game, 90)
    moved = max(0, len(path) - 1)
    hero["moves_left"] = max(0, hero["moves_left"] - moved)
    game["memory"]["tiles_moved"] += moved
    step_on_tile(game, hero)
    movement.refresh_vision(game)
    return moved


def record_hit(game, half, damage):
    """receives the game, the attack action and the damage; updates the stats and Spears's memory; returns the memory key used."""
    game["stats"]["damage_dealt"] += damage
    if half["range"] <= 1:
        key = "melee_hits"
    else:
        key = "ranged_hits"
    if damage > 0:
        game["memory"][key] += 1
    return key


def hero_attack(game, hero, half, amount, tile):
    """receives the game, a hero, the attack action, its strength and the target tile; resolves the attack and returns the damage dealt."""
    found = movement.model_at(game["units"], tile)
    if found is None:
        return 0
    unit = found[0]
    model = found[1]
    base = amount + hero["attack_bonus"]
    result = combat.roll_attack(game, "hero", base, unit["toughness"])
    combat.apply_damage(model, result[0])
    record_hit(game, half, result[0])
    logbook.say(game, hero["name"] + " attacks " + unit["name"] + " (" + result[1] + ") for "
                + str(result[0]) + ".")
    logbook.add_float(game, tile, "-" + str(result[0]), "white")
    if model["hp"] <= 0:
        spears_ai.remove_model(game, unit, model)
    else:
        spears_ai.boss_check(game, unit)
    return result[0]


def hero_heal(game, hero, amount, tile):
    """receives the game, the healer, the heal strength and the target tile; heals the hero there and returns how much was healed."""
    friend = movement.hero_at(game["heroes"], tile)
    if friend is None:
        return 0
    healed = cards.heal_hero(friend, amount)
    logbook.say(game, hero["name"] + " heals " + friend["name"] + " for " + str(healed) + ".")
    logbook.add_float(game, tile, "+" + str(healed), "green")
    return healed


def play_card(game, hero, name, tile):
    """receives the game, a hero, the name of a card in their hand and the target tile; plays the card's action there and returns the action kind."""
    card = cards.choose_card(hero, name)
    if card is None:
        return ""
    action = card["action"]
    amount = action["amount"] + cards.use_element(game["elements"], card["element"])
    if action["kind"] == "attack":
        hero_attack(game, hero, action, amount, tile)
    elif action["kind"] == "heal":
        hero_heal(game, hero, amount, tile)
    elif action["kind"] == "move":
        hero["moves_left"] += amount
        logbook.say(game, hero["name"] + " plays " + card["name"] + ": +" + str(amount) + " moves this turn.")
    else:
        hero["shield"] += amount
        logbook.say(game, hero["name"] + " raises a shield of " + str(amount) + ".")
    cards.finish_card(hero, card)
    game["stats"]["cards_played"] += 1
    hero["acted"] = True
    return action["kind"]


def do_request(game, hero, request):
    """receives the game, the hero whose turn it is and what the player asked for; carries it out and returns True if the turn is over."""
    kind = request["type"]
    if kind == "move":
        hero_move(game, hero, request["tile"])
    elif kind == "card":
        play_card(game, hero, request["card"], request["tile"])
        ui.pause(game, 300)
    elif kind == "menu":
        use_menu(game, request["choice"])
    else:
        return True
    return hero["exhausted"] or game["warlord_dead"] or not game["running"]


def hero_turn(game, hero):
    """receives the game and a hero; lets the player walk and play one card until the turn ends; returns how many requests were carried out."""
    hero["moves_left"] = hero["move"] + hero["bonus_move"]
    hero["acted"] = False
    logbook.say(game, hero["name"] + "'s turn: " + str(hero["moves_left"]) + " moves and one card.")
    done = 0
    finished = False
    while not finished:
        request = ui.get_hero_action(game, hero)
        finished = do_request(game, hero, request)
        done += 1
    return done


def use_menu(game, choice):
    """receives the game and a menu choice made during a turn ("rules", "status", "save" or "quit"); shows or does it; returns the choice."""
    if choice == "rules":
        ui.show_rules()
    elif choice == "status":
        ui.show_status(game)
    elif choice == "save":
        save_game(game)
    else:
        game["running"] = False
    return choice


# ---------------------------------------------------------------- Spears's units

def spears_phase(game, unit):
    """receives the game and one enemy unit; runs its phases Move, Shoot, Charge, Fight, Morale; returns the damage it dealt."""
    target = spears_ai.pick_target(game, unit)
    if target is None:
        return 0
    damage = 0
    visible = spears_ai.unit_visible(game, unit)
    logbook.tell(game, visible, unit["name"] + " activates (initiative " + str(unit["init"]) + ").")
    if visible:
        ui.follow(unit["models"][0]["pos"])
    spears_ai.move_unit(game, unit, target, unit["move"])
    ui.pause(game, 350)
    if unit["role"] == "ranged":
        damage += spears_ai.unit_shoot(game, unit, target)
    else:
        if spears_ai.unit_charge(game, unit, target):
            ui.pause(game, 350)
        damage += spears_ai.unit_fight(game, unit, target)
    ui.pause(game, 450)
    spears_ai.unit_morale(game, unit)
    return damage


def take_turn(game, entry):
    """receives the game and one [initiative, tie, kind, name] entry; gives that hero or unit its turn; returns the kind that acted."""
    game["turn_name"] = entry[3]
    movement.refresh_vision(game)
    if entry[2] == "hero":
        hero = game_data.find_hero(game, entry[3])
        if hero["exhausted"]:
            return "skipped"
        else:
            ui.follow(hero["pos"])
            hero_turn(game, hero)
    else:
        unit = spears_ai.find_unit(game["units"], entry[3])
        if unit is not None:
            spears_phase(game, unit)
    return entry[2]


# ---------------------------------------------------------------- the round

def start_round(game):
    """receives the game; resets the things that only last one round and returns the new round number."""
    game["round"] += 1
    game["order"] = []
    game["turn_name"] = ""
    logbook.say(game, "Round " + str(game["round"]) + " begins.")
    return game["round"]


def save_game(game):
    """receives the game; asks the player to type a file name and saves a status report; returns True if a file was written."""
    name = ui.ask_text(game, "Name your save file (letters and numbers):", "name", 0, 0)
    if name is None:
        return False
    saved = logbook.save_status(game, name)
    if saved:
        logbook.say(game, "Status saved to " + name + ".txt")
    else:
        logbook.say(game, "Could not save " + name + ".txt")
    return saved


def set_initiative(game, hero):
    """receives the game and a hero; rolls the hero's turn order for this round (speed plus a small random roll); returns it."""
    hero["init"] = hero["speed"] + random.randint(0, 9)
    return hero["init"]


def prepare_heroes(game):
    """receives the game; rolls turn order for every standing hero and every enemy unit; returns how many heroes will act."""
    acting = 0
    for hero in game["heroes"]:
        if not hero["exhausted"]:
            set_initiative(game, hero)
            acting += 1
    for unit in game["units"]:
        unit["init"] = spears_ai.pick_initiative(unit)
    return acting


def play_round(game):
    """receives the game; plays one full round (turn order, every hero and enemy unit takes a turn, end of round); returns the number of turns taken."""
    start_round(game)
    prepare_heroes(game)
    game["order"] = combat.sort_turn_order(game["heroes"], game["units"])
    taken = 0
    for entry in game["order"]:
        if game["warlord_dead"] or not game["running"]:
            break
        take_turn(game, entry)
        taken += 1
    if game["running"]:
        end_round(game)
    return taken


# ---------------------------------------------------------------- end of round

def cleanup_cards(game):
    """receives the game; clears the bonuses that only last one round (shields); returns how many heroes were reset."""
    reset = 0
    for hero in game["heroes"]:
        hero["shield"] = 0
        hero["bonus_move"] = 0
        reset += 1
    return reset


def mark_exhausted(game):
    """receives the game; marks every hero with no hp or too few cards as exhausted; returns how many heroes still stand."""
    standing = 0
    for hero in game["heroes"]:
        if hero["exhausted"]:
            continue
        elif cards.is_exhausted(hero):
            spears_ai.hero_falls(game, hero)
        else:
            standing += 1
    return standing


def count_clumping(game):
    """receives the game; counts heroes standing next to another hero and tells Spears's memory; returns that count."""
    tiles = movement.hero_tiles(game["heroes"])
    clumped = 0
    for tile in tiles:
        for other in tiles:
            if movement.tile_distance(tile, other) == 1:
                clumped += 1
                break
    if clumped >= 2:
        game["memory"]["clumped"] += 1
    return clumped


def end_round(game):
    """receives the game; runs the end of the round (shields wear off, elements wane, exhaustion, Spears's reinforcements, Doom +1, log file); returns the Doom Track value."""
    cleanup_cards(game)
    cards.wane_elements(game["elements"])
    mark_exhausted(game)
    count_clumping(game)
    spears_ai.reinforce(game)
    game["doom"] = spears_ai.advance_doom(game["doom"], 1, game["doom_max"])
    game["stats"]["rounds"] += 1
    logbook.say(game, "End of round " + str(game["round"]) + ". Doom Track: " + str(game["doom"])
                + "/" + str(game["doom_max"]) + ".")
    logbook.write_log(game["round_log"], game["round"])
    game["round_log"] = []
    return game["doom"]


# ---------------------------------------------------------------- main

def finish_game(game, result):
    """receives the game and "win", "lose" or "" (quit); writes the summary to the log and shows the end screen; returns the summary."""
    logbook.write_log(game["round_log"] + ["Result: " + str(result)], game["round"])
    summary = logbook.write_summary(game["stats"])
    if result != "" and game["running"]:
        ui.end_screen(result, logbook.summary_lines(summary))
    return summary


def main():
    """receives nothing; loads the data, opens the window and runs the game round by round until win, lose or quit; returns nothing."""
    data = game_data.load_dungeon("dungeon_data.txt")
    if data is None:
        print("Could not open dungeon_data.txt - keep it in the same folder as frodo_game.py")
        return
    ui.init()
    party = ui.title_flow(data)
    if len(party) > 0:
        game = game_data.new_game(data, party)
        logbook.start_log(party)
        start_dungeon(game)
        result = ""
        while game["running"] and result == "":
            play_round(game)
            result = logbook.check_game_over(game["heroes"], game["doom"], game["doom_max"],
                                             game["warlord_dead"])
        finish_game(game, result)
    pygame.quit()


if __name__ == "__main__":
    main()
