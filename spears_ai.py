"""spears_ai.py - Spears the Dungeon Lord: room generation, adaptation, and his armies.

Each enemy UNIT is a dictionary with stats and a list of MODELS.
Each model is a small dictionary: {"pos": [col, row], "hp": wounds left}.
"""
import random

import chambers
import combat
import logbook
import movement

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASIC_UNITS = ["Orc Brutes", "Goblin Slingers", "Wolf Riders"]
COHERENCY = 2

BANNERS = {
    "none": "Spears watches from the dark... and sends his Orc Brutes.",
    "melee": "Spears notices your blades... he sends the Iron Guard and Slingers!",
    "ranged": "Spears notices your archers... he sends Wolf Riders!",
    "loot": "Spears notices your greed... trapped chests and Shade Stalkers await!",
    "clump": "Spears notices you huddling... Bomb Flingers and hidden pits!",
    "rest": "Spears notices you resting... the Doom Track lurches forward!",
    "final": "The Throne of Spears! His Warlord rises to meet you!",
    "side": "A side chamber... something glints in the dark.",
}


# ---------------------------------------------------------------- adaptation

def spears_counter(memory):
    """receives Spears's memory dictionary; returns the party habit he will punish next: "melee", "ranged", "loot", "clump", "rest" or "none"."""
    scores = {"melee": memory["melee_hits"], "ranged": memory["ranged_hits"],
              "loot": memory["chests_opened"] * 3, "clump": memory["clumped"] * 2}
    best = "none"
    best_score = 3
    for habit in scores:
        if scores[habit] > best_score:
            best = habit
            best_score = scores[habit]
    return best


def fade_memory(memory):
    """receives Spears's memory; halves every count so newer habits matter more; returns the memory."""
    for key in memory:
        memory[key] = memory[key] // 2
    return memory


def unit_plan(counter, step, kind):
    """receives the habit to counter, how far along the main path this chamber is and its kind; returns the list of unit type names Spears deploys."""
    if counter == "melee":
        plan = ["Iron Guard", "Goblin Slingers"]
    elif counter == "ranged":
        plan = ["Wolf Riders", "Wolf Riders"]
    elif counter == "loot":
        plan = ["Shade Stalkers", "Orc Brutes"]
    elif counter == "clump":
        plan = ["Bomb Flingers", "Orc Brutes"]
    else:
        plan = ["Orc Brutes", "Goblin Slingers"]
    if kind == "side" or kind == "start":
        return plan[:1]
    if step >= 6:
        plan.append(random.choice(BASIC_UNITS))
    return plan


# ---------------------------------------------------------------- room generation

def pick_style(styles, counter):
    """receives the room styles and the habit to counter; returns a random style that matches (or any normal style)."""
    matches = []
    spares = []
    for style in styles:
        if style["counters"] == counter:
            matches.append(style)
        elif style["counters"] != "final":
            spares.append(style)
    if len(matches) > 0:
        return random.choice(matches)
    return random.choice(spares)


def build_dungeon(game):
    """receives the game; plans the whole dungeon, starts the map as solid rock and carves the boss arena (its outline is known from the start); returns how many chambers were planned."""
    data = game["data"]
    dungeon = data["dungeon"]
    cols = dungeon["cell_cols"] * dungeon["cell_width"]
    rows = dungeon["cell_rows"] * dungeon["cell_height"]
    game["seed"] = random.randint(1, 999999)
    game["grid"] = chambers.blank_map(cols, rows)
    game["known"] = chambers.blank_map(cols, rows)
    game["seen"] = movement.blank_grid(game["grid"], False)
    game["plan"] = chambers.plan_dungeon(dungeon)
    game["owners"] = chambers.owner_grid(game["grid"], game["plan"])
    game["doors"] = []
    game["units"] = []
    boss = boss_chamber(game)
    result = chambers.carve_arena(game["grid"], boss["zone"], data["arena"])
    boss["tiles"] = result[0]
    boss["markers"] = result[1]
    boss["name"] = "Throne of Spears"
    return len(game["plan"])


def boss_chamber(game):
    """receives the game; returns the boss arena's chamber dictionary."""
    for chamber in game["plan"]:
        if chamber["kind"] == "boss":
            return chamber
    return game["plan"][len(game["plan"]) - 1]


def chamber_at(game, tile):
    """receives the game and a tile; returns the chamber whose zone holds that tile, or None."""
    number = game["owners"][tile[1]][tile[0]]
    if number < 0:
        return None
    return game["plan"][number]


def door_at(game, tile):
    """receives the game and a tile; returns the door record {"tile", "from", "to"} on that tile, or None."""
    for door in game["doors"]:
        if door["tile"] == tile:
            return door
    return None


def place_letters(grid, free, letter, count):
    """receives the map grid, the list of free floor tiles, a tile letter and a count; puts that letter on random free tiles (removing them from the list); returns how many were placed."""
    placed = 0
    while placed < count and len(free) > 0:
        tile = free.pop(random.randrange(len(free)))
        grid[tile[1]][tile[0]] = letter
        placed += 1
    return placed


def furnish(game, room, style, counter):
    """receives the game, the new room, its style and the habit to counter; fills the chamber with chests, traps, cover and shrines, twisted to punish that habit (side chambers get an extra chest); returns how many floor tiles are still empty."""
    free = []
    for tile in room["tiles"]:
        if tile not in room["starts"] and movement.tile_distance(tile, room["origin"]) > 1:
            free.append(tile)
    chests = style["chests"]
    if room["kind"] == "side":
        chests += 1
    for number in range(chests):
        if counter == "loot" and random.randint(1, 2) == 1:
            place_letters(game["grid"], free, "X", 1)
        else:
            place_letters(game["grid"], free, "C", 1)
    place_letters(game["grid"], free, "T", style["traps"])
    place_letters(game["grid"], free, "P", style["shrines"])
    if counter == "clump":
        place_letters(game["grid"], free, "H", 3)
    elif counter == "ranged":
        place_letters(game["grid"], free, "~", 2)
    elif counter == "rest":
        room["doom"] = 2
    place_letters(game["grid"], free, "~", style["cover"])
    return len(free)


def deploy_room(game, room, counter):
    """receives the game, the new room and the habit to counter; Spears deploys his units in the far half of the chamber; returns how many units were placed."""
    plan = unit_plan(counter, room["step"], room["kind"])
    if len(room["tiles"]) < 26:
        plan = plan[:2]
    if len(room["tiles"]) < 18:
        plan = plan[:1]
    spots = chambers.far_tiles(room["tiles"], room["origin"])
    taken = movement.hero_tiles(game["heroes"]) + list(room["starts"]) + movement.model_tiles(game["units"])
    for type_name in plan:
        add_unit(game, room, type_name, random.choice(spots), taken)
    game["spawns"] = spots
    return len(room["units"])


def add_unit(game, room, type_name, spawn, taken):
    """receives the game, a room, a unit type, a spawn tile and the tiles already taken; makes the unit, stands it around the spawn and adds it to the room; returns the unit (None if no model fitted)."""
    game["unit_count"] += 1
    unit = make_unit(game["data"], type_name, game["unit_count"])
    unit["chamber"] = room["id"]
    place_models(game["grid"], unit, spawn, taken)
    if len(unit["models"]) == 0:
        return None
    room["units"].append(unit)
    return unit


def deploy_boss(game, room):
    """receives the game and the boss arena room; stands the Warlord at his mark and his guards at theirs; returns how many units were placed."""
    markers = room["markers"]
    taken = movement.hero_tiles(game["heroes"]) + movement.model_tiles(game["units"])
    add_unit(game, room, "Warlord", markers["W"][0], taken)
    guards = ["Iron Guard", "Orc Brutes"]
    for index in range(min(len(guards), len(markers["G"]))):
        add_unit(game, room, guards[index], markers["G"][index], taken)
    game["spawns"] = room["tiles"]
    return len(room["units"])


def place_exits(game, chamber):
    """receives the game and a freshly carved chamber; puts a sealed door in its wall towards every chamber that branches off it; returns the door to the main path (or None)."""
    main_door = None
    for child in chambers.children(game["plan"], chamber["id"]):
        aim = chambers.box_center(chambers.zone_box(game["grid"], child["zone"]))
        if child["kind"] == "boss":
            aim = nearest_tile(child["tiles"], chambers.box_center(chambers.zone_box(game["grid"], chamber["zone"])))
        tile = chambers.pick_door(game["grid"], chamber["tiles"], aim)
        if tile is None:
            continue
        game["grid"][tile[1]][tile[0]] = "D"
        game["doors"].append({"tile": tile, "from": chamber["id"], "to": child["id"]})
        if child["kind"] == "boss":
            game["boss_door"] = tile
        if child["kind"] != "side":
            main_door = tile
    return main_door


def nearest_tile(tiles, point):
    """receives a list of tiles and a point; returns the tile closest to the point."""
    best = tiles[0]
    for tile in tiles:
        if movement.tile_distance(tile, point) < movement.tile_distance(best, point):
            best = tile
    return best


def connect_chamber(game, chamber):
    """receives the game and the chamber being entered; digs a corridor from the door that leads to it and swings that door open for good; returns the door tile, or None for the first chamber."""
    for door in game["doors"]:
        if door["to"] == chamber["id"]:
            allowed = [-1, door["from"], door["to"]]
            chambers.dig_corridor(game["grid"], door["tile"], chamber["tiles"], game["owners"], allowed)
            game["grid"][door["tile"][1]][door["tile"][0]] = "d"
            return door["tile"]
    return None


def make_unit(data, type_name, number):
    """receives the data, a unit type name and a unit number; returns a new unit dictionary with no models placed yet."""
    unit = dict(data["units"][type_name])
    unit["type"] = type_name
    unit["name"] = type_name + " " + LETTERS[number % 26]
    unit["start_models"] = unit["models"]
    unit["models"] = []
    unit["init"] = 50
    unit["goal"] = [0, 0]
    return unit


def place_models(grid, unit, spawn, taken):
    """receives the grid, a unit, a spawn tile and the tiles already taken; stands the unit's models on and around the spawn; returns how many were placed."""
    tiles = [spawn] + movement.reachable_tiles(grid, spawn, COHERENCY, [], [], False)
    for tile in tiles:
        if len(unit["models"]) == unit["start_models"]:
            break
        if tile not in taken:
            unit["models"].append({"pos": [tile[0], tile[1]], "hp": unit["wounds"]})
            taken.append(tile)
    return len(unit["models"])


def generate_room(game, number, counter):
    """receives the game, the number of the chamber being opened and the party habit Spears wants to counter; carves the chamber (the arena is already carved), furnishes it and deploys his units; returns the room dictionary."""
    chamber = game["plan"][number]
    kind = chamber["kind"]
    if kind == "boss":
        counter = "final"
    elif kind == "side":
        counter = random.choice(["loot", counter])
    if kind != "boss":
        style = pick_style(game["data"]["styles"], counter)
        chamber["name"] = style["name"]
        chamber["tiles"] = chambers.carve_chamber(game["grid"], chamber["zone"], style)
    chamber["carved"] = True
    entry = connect_chamber(game, chamber)
    banner = BANNERS[counter]
    if kind == "side":
        banner = BANNERS["side"]
    room = {"id": number, "kind": kind, "step": chamber["step"], "name": chamber["name"], "tiles": chamber["tiles"],
            "units": [], "doom": 0, "banner": banner, "entry": entry, "starts": [], "origin": entry,
            "markers": chamber["markers"]}
    game["door"] = place_exits(game, chamber)
    if entry is None:
        far_from = game["door"]
        if far_from is None:
            far_from = chamber["tiles"][0]
        room["starts"] = chambers.far_cluster(chamber["tiles"], far_from, 4)
        room["origin"] = room["starts"][0]
    if kind == "boss":
        deploy_boss(game, room)
    else:
        furnish(game, room, style, counter)
        deploy_room(game, room, counter)
    return room


# ---------------------------------------------------------------- unit helpers

def find_unit(units, name):
    """receives the unit list and a unit name; returns that unit, or None if it has been destroyed."""
    for unit in units:
        if unit["name"] == name:
            return unit
    return None


def unit_visible(game, unit):
    """receives the game and a unit; returns True if the party can see at least one of its models right now."""
    for model in unit["models"]:
        if game["seen"][model["pos"][1]][model["pos"][0]]:
            return True
    return False


def pick_initiative(unit):
    """receives a unit; returns a random activation initiative that suits its role (fast units go early, heavy ones late)."""
    if unit["role"] == "fast":
        return random.randint(10, 35)
    elif unit["role"] == "ranged":
        return random.randint(25, 55)
    elif unit["role"] == "heavy":
        return random.randint(55, 90)
    else:
        return random.randint(35, 75)


def pick_target(game, unit):
    """receives the game and a unit; returns the hero Spears wants dead most (weak and close), or None if no hero stands."""
    best = None
    best_score = 9999
    if len(unit["models"]) == 0:
        return None
    for hero in game["heroes"]:
        if hero["exhausted"]:
            continue
        score = hero["hp"] * 2 + movement.tile_distance(hero["pos"], unit["models"][0]["pos"])
        if score < best_score:
            best = hero
            best_score = score
    return best


def coherency_ok(unit, model, tile):
    """receives a unit, one of its models and a tile; returns True if the model would be within 2 tiles of another model of the unit there."""
    if len(unit["models"]) < 2:
        return True
    for other in unit["models"]:
        if other is not model and movement.tile_distance(tile, other["pos"]) <= COHERENCY:
            break
    else:
        return False
    return True


def goal_tile(game, unit, target):
    """receives the game, a unit and its target hero; returns the tile the unit heads for (heavy units hold the door until heroes come close)."""
    leader = unit["models"][0]["pos"]
    far = movement.tile_distance(leader, target["pos"]) > 6
    if unit["role"] == "heavy" and far and game["door"] is not None:
        return game["door"]
    return target["pos"]


def is_flank(game, unit, tile):
    """receives the game, a unit and a tile next to its goal; returns True if another enemy model stands on the opposite side (a flank)."""
    goal = unit["goal"]
    opposite = [goal[0] * 2 - tile[0], goal[1] * 2 - tile[1]]
    return movement.model_at(game["units"], opposite) is not None


def ranged_score(steps, reach):
    """receives the distance to the target and the shooting range; returns a score (low is good) for keeping a safe shooting distance."""
    if steps < 3:
        return 20 + (3 - steps) * 5
    elif steps <= reach:
        return reach - steps
    else:
        return 10 + (steps - reach) * 10


def tile_score(game, unit, tile, steps_map):
    """receives the game, a unit, a tile and the step map from the goal; returns how good that tile is (low is good)."""
    steps = steps_map[tile[1]][tile[0]]
    if steps < 0:
        steps = 99
    if unit["role"] == "ranged":
        return ranged_score(steps, unit["range"])
    score = steps * 10
    if steps == 1 and is_flank(game, unit, tile):
        score = score - 3
    return score


def best_tile(game, unit, model, steps_map, steps):
    """receives the game, a unit, one model, the step map from the goal and a move limit; returns the best tile that keeps coherency."""
    blocked = movement.hero_tiles(game["heroes"])
    occupied = movement.model_tiles(game["units"])
    options = movement.reachable_tiles(game["grid"], model["pos"], steps, blocked, occupied, False)
    best = model["pos"]
    best_score = tile_score(game, unit, best, steps_map)
    if not coherency_ok(unit, model, best):
        best_score = 9999
    for tile in options:
        if not coherency_ok(unit, model, tile):
            continue
        score = tile_score(game, unit, tile, steps_map)
        if score < best_score:
            best = tile
            best_score = score
    return best


# ---------------------------------------------------------------- unit phases

def move_unit(game, unit, target, steps):
    """receives the game, a unit, its target hero and a move limit; moves every model toward the goal and returns how many models moved."""
    unit["goal"] = goal_tile(game, unit, target)
    steps_map = movement.step_map(game["grid"], unit["goal"], [], True)
    moved = 0
    for model in unit["models"]:
        tile = best_tile(game, unit, model, steps_map, steps)
        if tile != model["pos"]:
            model["pos"] = [tile[0], tile[1]]
            moved += 1
    return moved


def choose_victim(game, model, reach, target):
    """receives the game, a model, its reach and the unit's target; returns the hero this model attacks (the target if in reach, else the weakest in reach, else None)."""
    if not target["exhausted"] and movement.tile_distance(model["pos"], target["pos"]) <= reach:
        return target
    victim = None
    for hero in game["heroes"]:
        if hero["exhausted"] or movement.tile_distance(model["pos"], hero["pos"]) > reach:
            continue
        if victim is None or hero["hp"] < victim["hp"]:
            victim = hero
    return victim


def cover_bonus(game, unit, hero):
    """receives the game, the attacking unit and the hero; returns 1 if the hero is behind cover from a shot, else 0."""
    spot = game["grid"][hero["pos"][1]][hero["pos"][0]]
    if unit["role"] == "ranged" and spot == "~":
        return 1
    return 0


def hero_falls(game, hero):
    """receives the game and a hero with no hp; marks the hero exhausted and returns a message."""
    hero["exhausted"] = True
    if hero["kind"] == "leader":
        return logbook.say(game, "Frodo is exhausted! The party fights on without him.")
    return logbook.say(game, hero["name"] + " is exhausted and leaves the fight!")


def splash(game, unit, hero):
    """receives the game, an area-attack unit and the hero it hit; deals 1 damage to heroes next to that hero; returns how many were splashed."""
    count = 0
    for other in game["heroes"]:
        near = movement.tile_distance(other["pos"], hero["pos"]) == 1
        if other["exhausted"] or not near:
            continue
        combat.apply_damage(other, unit["aoe"])
        game["stats"]["damage_taken"] += unit["aoe"]
        logbook.add_float(game, other["pos"], "-" + str(unit["aoe"]), "crimson")
        count += 1
        if other["hp"] <= 0:
            hero_falls(game, other)
    return count


def unit_attack(game, unit, model, hero):
    """receives the game, a unit, one of its models and a hero; resolves one enemy attack and returns the damage dealt."""
    shield = hero["shield"] + hero["armor"] + cover_bonus(game, unit, hero)
    result = combat.roll_attack(game, "enemy", unit["attack"], shield)
    damage = result[0]
    combat.apply_damage(hero, damage)
    game["stats"]["damage_taken"] += damage
    game["seen"][model["pos"][1]][model["pos"][0]] = True
    logbook.say(game, unit["name"] + " hits " + hero["name"] + " (" + result[1] + ") for "
                + str(damage) + ".")
    logbook.add_float(game, hero["pos"], "-" + str(damage), "crimson")
    if unit["aoe"] > 0 and damage > 0:
        splash(game, unit, hero)
    if hero["hp"] <= 0:
        hero_falls(game, hero)
    return damage


def unit_shoot(game, unit, target):
    """receives the game, a ranged unit and its target; every model in range shoots; returns the total damage."""
    total = 0
    for model in unit["models"]:
        victim = choose_victim(game, model, unit["range"], target)
        if victim is not None:
            total += unit_attack(game, unit, model, victim)
    return total


def touching_hero(game, unit):
    """receives the game and a unit; returns True if any of its models stands next to a hero."""
    for model in unit["models"]:
        for tile in movement.hero_tiles(game["heroes"]):
            if movement.tile_distance(model["pos"], tile) == 1:
                return True
    return False


def nearest_gap(unit, target):
    """receives a unit and its target hero; returns how many tiles the closest model must cross to stand next to the hero."""
    gap = 99
    for model in unit["models"]:
        distance = movement.tile_distance(model["pos"], target["pos"]) - 1
        if distance < gap:
            gap = distance
    return gap


def unit_charge(game, unit, target):
    """receives the game, a melee unit and its target; rolls a charge distance and moves in if it is enough; returns True on a successful charge."""
    if touching_hero(game, unit) or target["exhausted"]:
        return False
    roll = random.randint(1, 6)
    if unit["role"] == "fast":
        roll += 2
    if nearest_gap(unit, target) <= roll:
        move_unit(game, unit, target, roll)
        logbook.tell(game, True, unit["name"] + " charges! (rolled " + str(roll) + ")")
        return True
    else:
        logbook.tell(game, unit_visible(game, unit), unit["name"] + " tries to charge but falls short (rolled "
                     + str(roll) + ").")
        return False


def unit_fight(game, unit, target):
    """receives the game, a unit and its target; every model next to a hero attacks; returns the total damage."""
    total = 0
    for model in unit["models"]:
        victim = choose_victim(game, model, 1, target)
        if victim is not None:
            total += unit_attack(game, unit, model, victim)
    return total


# ---------------------------------------------------------------- morale and losses

def morale_test(leadership, roll):
    """receives a unit's leadership and a 2d6 roll; returns True if the unit holds (roll is leadership or less)."""
    return roll <= leadership


def check_room_clear(game, number):
    """receives the game and a chamber number; if none of that chamber's units are left, unseals all its doors and returns True."""
    chamber = game["plan"][number]
    if chamber["cleared"]:
        return True
    for unit in game["units"]:
        if unit["chamber"] == number:
            return False
    chamber["cleared"] = True
    game["stats"]["rooms_cleared"] += 1
    opened = 0
    for door in game["doors"]:
        tile = door["tile"]
        if door["from"] == number and game["grid"][tile[1]][tile[0]] == "D":
            game["grid"][tile[1]][tile[0]] = "E"
            opened += 1
    if opened > 0:
        logbook.say(game, chamber["name"] + " is clear. Its doors unseal - walk a hero onto one to go on!")
    return True


def destroy_unit(game, unit, tile):
    """receives the game, a unit with no models left and the tile where it fell; removes the unit, maybe drops loot, and returns True if loot dropped."""
    game["units"].remove(unit)
    logbook.say(game, unit["name"] + " is destroyed!")
    if unit["type"] == "Warlord":
        game["warlord_dead"] = True
    dropped = random.randint(1, 100) <= 35 and game["grid"][tile[1]][tile[0]] == "."
    if dropped:
        game["grid"][tile[1]][tile[0]] = "C"
        logbook.say(game, "They dropped a chest!")
    check_room_clear(game, unit["chamber"])
    return dropped


def remove_model(game, unit, model):
    """receives the game, a unit and a dead or fleeing model; removes the model and returns how many models the unit has left."""
    tile = model["pos"]
    unit["models"].remove(model)
    game["stats"]["enemies_slain"] += 1
    if len(unit["models"]) == 0:
        destroy_unit(game, unit, tile)
    return len(unit["models"])


def safest_tile(game, model, steps):
    """receives the game, a model and a move limit; returns the reachable tile farthest from every hero."""
    heroes = movement.hero_tiles(game["heroes"])
    options = movement.reachable_tiles(game["grid"], model["pos"], steps, heroes,
                                       movement.model_tiles(game["units"]), False)
    best = model["pos"]
    best_gap = -1
    for tile in [model["pos"]] + options:
        gap = 99
        for hero_tile in heroes:
            gap = min(gap, movement.tile_distance(tile, hero_tile))
        if gap > best_gap:
            best = tile
            best_gap = gap
    return best


def fall_back(game, unit):
    """receives the game and a broken unit; every model runs away from the heroes; returns how many models moved."""
    moved = 0
    for model in unit["models"]:
        tile = safest_tile(game, model, unit["move"])
        if tile != model["pos"]:
            model["pos"] = [tile[0], tile[1]]
            moved += 1
    return moved


def break_unit(game, unit):
    """receives the game and a unit that failed morale; it randomly loses a model or falls back; returns what happened."""
    tile = unit["models"][0]["pos"]
    visible = unit_visible(game, unit)
    if visible:
        game["fx"].append({"kind": "break", "tile": [tile[0], tile[1]]})
    if random.randint(1, 2) == 1:
        logbook.tell(game, visible, unit["name"] + " breaks! One of them flees the dungeon.")
        remove_model(game, unit, unit["models"][len(unit["models"]) - 1])
        return "flee"
    else:
        logbook.tell(game, visible, unit["name"] + " breaks and falls back!")
        fall_back(game, unit)
        return "fall back"


def unit_morale(game, unit):
    """receives the game and a unit; if it is below half strength it rolls 2d6 against leadership; returns True if the unit holds."""
    alive = len(unit["models"])
    if alive == 0 or unit["start_models"] < 2 or alive * 2 >= unit["start_models"]:
        return True
    roll = random.randint(1, 6) + random.randint(1, 6)
    visible = unit_visible(game, unit)
    if morale_test(unit["leadership"], roll):
        logbook.tell(game, visible, unit["name"] + " holds its nerve (rolled " + str(roll) + ").")
        return True
    logbook.tell(game, visible, unit["name"] + " fails morale (rolled " + str(roll) + " over "
                 + str(unit["leadership"]) + ").")
    break_unit(game, unit)
    return False


# ---------------------------------------------------------------- doom and reinforcements

def advance_doom(doom, amount, doom_max):
    """receives the Doom Track value, how much to add and the track's end; returns the new value (never past the end)."""
    doom = doom + amount
    if doom > doom_max:
        doom = doom_max
    return doom


def deploy_unit(game):
    """receives the game; Spears deploys a fresh unit at a free spawn tile of the chamber the party is fighting in; returns a message ("" if he could not)."""
    taken = movement.model_tiles(game["units"]) + movement.hero_tiles(game["heroes"])
    for spawn in game["spawns"]:
        if spawn not in taken:
            break
    else:
        return ""
    room = {"id": game["chamber"], "units": []}
    unit = add_unit(game, room, random.choice(BASIC_UNITS), spawn, taken)
    if unit is None:
        return ""
    game["units"].append(unit)
    game["event_tile"] = spawn
    return "Spears reinforces! " + unit["name"] + " march in."


def dark_floor(game):
    """receives the game; returns the empty floor tiles of the current chamber that no hero can see right now."""
    taken = movement.hero_tiles(game["heroes"]) + movement.model_tiles(game["units"])
    tiles = []
    for tile in game["plan"][game["chamber"]]["tiles"]:
        hidden = not game["seen"][tile[1]][tile[0]]
        if game["grid"][tile[1]][tile[0]] == "." and hidden and tile not in taken:
            tiles.append(tile)
    return tiles


def spring_new_trap(game):
    """receives the game; Spears arms a new trap, in the dark if he can, otherwise near a hero; returns a message ("" if no room)."""
    standing = movement.hero_tiles(game["heroes"])
    options = dark_floor(game)
    if len(options) == 0 and len(standing) > 0:
        taken = standing + movement.model_tiles(game["units"])
        options = movement.reachable_tiles(game["grid"], random.choice(standing), 2, [], taken, False)
    random.shuffle(options)
    for tile in options:
        if game["grid"][tile[1]][tile[0]] == ".":
            game["grid"][tile[1]][tile[0]] = "T"
            game["event_tile"] = tile
            return "Spears arms a new trap!"
    return ""


def all_connected(game):
    """receives the game; returns True if every hero, every enemy and every door of opened chambers can still be walked to."""
    standing = movement.hero_tiles(game["heroes"])
    if len(standing) == 0:
        return True
    steps = movement.step_map(game["grid"], standing[0], [], True)
    spots = standing + movement.model_tiles(game["units"])
    for door in game["doors"]:
        if game["plan"][door["from"]]["carved"]:
            spots.append(door["tile"])
    for tile in spots:
        if steps[tile[1]][tile[0]] < 0:
            return False
    return True


def shift_tile(game):
    """receives the game; Spears turns one empty floor tile of the current chamber into rubble if nobody gets walled off; returns a message ("" if he could not)."""
    grid = game["grid"]
    taken = movement.hero_tiles(game["heroes"]) + movement.model_tiles(game["units"])
    tiles = game["plan"][game["chamber"]]["tiles"]
    for attempt in range(20):
        tile = random.choice(tiles)
        if grid[tile[1]][tile[0]] != "." or tile in taken:
            continue
        grid[tile[1]][tile[0]] = "#"
        game["event_tile"] = tile
        if all_connected(game):
            tiles.remove(tile)
            return "The dungeon shifts! Spears drops rubble into the room."
        grid[tile[1]][tile[0]] = "."
    return ""


def reinforce(game):
    """receives the game; after a round Spears may deploy a unit (once per chamber), arm a trap or shift a tile in the chamber the party is fighting in; returns a message ("" if he waits)."""
    chamber = game["plan"][game["chamber"]]
    if chamber["cleared"] or chamber["kind"] == "boss" or random.randint(1, 4) != 1:
        return ""
    choice = random.choice(["deploy", "trap", "shift"])
    if choice == "deploy" and not chamber["reinforced"]:
        chamber["reinforced"] = True
        message = deploy_unit(game)
    elif choice == "trap":
        message = spring_new_trap(game)
    else:
        message = shift_tile(game)
    if message == "":
        return ""
    tile = game["event_tile"]
    if game["seen"][tile[1]][tile[0]]:
        logbook.say(game, message)
        logbook.add_banner(game, message)
    else:
        logbook.note(game, message + " (unseen by the party)")
        logbook.say(game, "Something stirs in the dark...")
        logbook.add_banner(game, "Something stirs in the dark...")
    return message


# ---------------------------------------------------------------- the boss

def warlord(game):
    """receives the game; returns the Warlord's unit if he is on the map, else None."""
    for unit in game["units"]:
        if unit["type"] == "Warlord":
            return unit
    return None


def summon_guards(game, unit):
    """receives the game and the Warlord; his guards rush in at the free guard marks of the arena; returns a message."""
    room = {"id": unit["chamber"], "units": []}
    taken = movement.hero_tiles(game["heroes"]) + movement.model_tiles(game["units"])
    spots = list(boss_chamber(game)["markers"]["G"]) + [unit["models"][0]["pos"]]
    for spot in spots:
        if spot not in taken:
            break
    add_unit(game, room, "Iron Guard", spot, taken)
    for summoned in room["units"]:
        game["units"].append(summoned)
    return "The Warlord roars! His Iron Guard rush to the throne!"


def enrage(unit):
    """receives the Warlord; he grows stronger and faster; returns a message."""
    unit["attack"] += 2
    unit["move"] += 1
    return "The Warlord is wounded and ENRAGED! +2 attack, +1 move."


def boss_check(game, unit):
    """receives the game and a unit that was just hit; if it is the Warlord, moves him into his next phase at half and at a quarter of his wounds; returns the phase he is in (0, 1 or 2)."""
    if unit["type"] != "Warlord" or len(unit["models"]) == 0:
        return game["boss_phase"]
    left = unit["models"][0]["hp"]
    message = ""
    if game["boss_phase"] == 0 and left * 2 <= unit["wounds"]:
        game["boss_phase"] = 1
        message = summon_guards(game, unit)
    elif game["boss_phase"] == 1 and left * 4 <= unit["wounds"]:
        game["boss_phase"] = 2
        message = enrage(unit)
    if message != "":
        logbook.say(game, message)
        logbook.add_banner(game, message)
    return game["boss_phase"]
