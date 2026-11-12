"""test_frodo.py - assert tests for the core game functions.

Run with:  python test_frodo.py
These tests do not open a window. They write a few lines to frodo_log.txt.
"""
import os
import random

import cards
import chambers
import combat
import frodo_game
import ui
import game_data
import logbook
import movement
import savegame
import spears_ai


def make_test_game():
    """receives nothing; returns a small game with Frodo and Brother Biscuit standing in the first chamber of a freshly dug dungeon, for testing."""
    data = game_data.load_dungeon("dungeon_data.txt")
    game = game_data.new_game(data, ["Frodo", "Brother Biscuit"])
    frodo_game.start_dungeon(game)
    game["fx"] = []
    return game


def test_load_dungeon():
    """receives nothing; checks that dungeon_data.txt loads fully and a missing file returns None; returns True."""
    data = game_data.load_dungeon("dungeon_data.txt")
    assert data is not None
    assert "Orc Brutes" in data["units"]
    assert data["units"]["Orc Brutes"]["models"] == 3
    assert len(data["styles"]) >= 2 and data["dungeon"]["main"] >= 2
    assert len(data["arena"]) == 14
    for row in data["arena"]:
        assert len(row) == 16, row
    assert "W" in "".join(data["arena"])
    for style in data["styles"]:
        assert style["shape"] in ["rect", "ell", "round", "cross", "cave"], style["name"]
    assert len(data["cards"]["Frodo"]) == 8
    assert data["cards"]["Frodo"][0]["action"]["kind"] == "attack"
    assert data["heroes"]["Frodo"]["move"] == 4
    assert len(data["items"]) > 0
    assert game_data.load_dungeon("no_such_file.txt") is None
    return True


def test_combat():
    """receives nothing; checks draw_modifier, calc_damage, apply_damage and sort_turn_order; returns True."""
    assert combat.calc_damage(3, "x2", 1) == 5
    assert combat.calc_damage(3, "null", 0) == 0
    assert combat.calc_damage(2, "+1", 0) == 3
    assert combat.calc_damage(2, "-2", 1) == 0
    deck = combat.build_modifier_deck()
    discard = []
    assert len(deck) == 20
    card = combat.draw_modifier(deck, discard)
    assert card in ["+0", "+1", "-1", "+2", "-2", "x2", "null"]
    assert len(deck) == 19 and len(discard) == 1
    for count in range(25):
        combat.draw_modifier(deck, discard)
    assert len(deck) + len(discard) == 20
    target = {"hp": 5}
    assert combat.apply_damage(target, 3) == 2
    assert combat.apply_damage(target, 9) == 0
    heroes = [{"name": "A", "init": 40, "exhausted": False}, {"name": "B", "init": 10, "exhausted": True}]
    units = [{"name": "U", "init": 20, "models": [1]}]
    order = combat.sort_turn_order(heroes, units)
    assert order[0][3] == "U" and order[1][3] == "A" and len(order) == 2
    return True


def test_cards():
    """receives nothing; checks the 3-card hand, choose_card, finish_card, drawing and reshuffling, play_card, walking, is_exhausted, wane_elements and search_poi; returns True."""
    game = make_test_game()
    frodo = game["heroes"][0]
    assert len(frodo["hand"]) == cards.HAND_SIZE and len(frodo["deck"]) == 8 - cards.HAND_SIZE
    assert cards.choose_card(frodo, "No Such Card") is None
    first = frodo["hand"][0]
    card = cards.choose_card(frodo, first["name"])
    assert card is first and len(frodo["hand"]) == 2
    assert cards.finish_card(frodo, card) == 3 and len(frodo["discard"]) == 1 and len(frodo["deck"]) == 4
    for turn in range(10):
        played = cards.choose_card(frodo, frodo["hand"][0]["name"])
        cards.finish_card(frodo, played)
        total = len(frodo["hand"]) + len(frodo["deck"]) + len(frodo["discard"])
        assert len(frodo["hand"]) == 3 and total == 8
    frodo["hand"] = [game["data"]["cards"]["Frodo"][2]]
    frodo["moves_left"] = 0
    assert frodo_game.play_card(game, frodo, "Zoomies", frodo["pos"]) == "move"
    assert frodo["moves_left"] == 4 and frodo["acted"] and len(frodo["hand"]) == 3
    tiles = movement.move_targets(game, frodo)[0]
    assert len(tiles) > 0
    frodo_game.hero_move(game, frodo, tiles[0])
    assert frodo["pos"] == tiles[0] and frodo["moves_left"] < 4
    assert not cards.is_exhausted(frodo)
    frodo["hp"] = 0
    assert cards.is_exhausted(frodo)
    elements = {"fire": 2, "frost": 1, "light": 0}
    assert cards.wane_elements(elements) == 1
    assert elements == {"fire": 1, "frost": 0, "light": 0}
    item = cards.search_poi(frodo, game["data"]["items"], 1)
    assert item["rarity"] == 1 and item["name"] in frodo["items"]
    return True


def check_dungeon(game):
    """receives a game that has just started; checks the plan, the first chamber's doors and that opening a door carves a reachable chamber; returns True."""
    plan = game["plan"]
    kinds = []
    for chamber in plan:
        kinds.append(chamber["kind"])
    assert kinds.count("start") == 1 and kinds.count("boss") == 1 and len(plan) >= 8
    boss = spears_ai.boss_chamber(game)
    assert len(boss["tiles"]) > 100 and len(boss["markers"]["W"]) == 1
    assert game["known"][boss["tiles"][0][1]][boss["tiles"][0][0]] == "#"
    assert len(game["units"]) >= 1
    first_doors = []
    for door in game["doors"]:
        if door["from"] == 0:
            first_doors.append(door)
    assert len(first_doors) == len(chambers.children(plan, 0))
    game["units"] = []
    spears_ai.check_room_clear(game, 0)
    door = first_doors[0]
    assert game["grid"][door["tile"][1]][door["tile"][0]] == "E"
    game["heroes"][0]["pos"] = list(door["tile"])
    frodo_game.step_on_tile(game, game["heroes"][0])
    assert game["depth"] == 2 and game["grid"][door["tile"][1]][door["tile"][0]] == "d"
    steps = movement.step_map(game["grid"], game["heroes"][1]["pos"], [], False)
    for unit in game["units"]:
        assert unit["chamber"] == door["to"]
        for model in unit["models"]:
            assert steps[model["pos"][1]][model["pos"][0]] > 0
    return True


def test_spears():
    """receives nothing; checks spears_counter, morale_test, advance_doom, generate_room and coherency; returns True."""
    memory = game_data.new_memory()
    assert spears_ai.spears_counter(memory) == "none"
    memory["melee_hits"] = 10
    memory["ranged_hits"] = 4
    assert spears_ai.spears_counter(memory) == "melee"
    memory["chests_opened"] = 5
    assert spears_ai.spears_counter(memory) == "loot"
    assert spears_ai.morale_test(7, 7)
    assert spears_ai.morale_test(7, 2)
    assert not spears_ai.morale_test(7, 8)
    assert spears_ai.advance_doom(3, 1, 20) == 4
    assert spears_ai.advance_doom(19, 5, 20) == 20
    for seed in range(25):
        random.seed(seed)
        game = make_test_game()
        check_dungeon(game)
    random.seed(3)
    game = make_test_game()
    boss = spears_ai.boss_chamber(game)
    frodo_game.enter_room(game, boss["id"])
    lord = spears_ai.warlord(game)
    assert lord is not None and len(game["units"]) >= 2
    lord["models"][0]["hp"] = lord["wounds"] // 2
    assert spears_ai.boss_check(game, lord) == 1
    lord["models"][0]["hp"] = 1
    attack = lord["attack"]
    assert spears_ai.boss_check(game, lord) == 2 and lord["attack"] == attack + 2
    return True


def test_movement():
    """receives nothing; checks reachable tiles, walls and pathing; returns True."""
    grid = [list("#####"), list("#..##"), list("#.#.#"), list("#...#"), list("#####")]
    tiles = movement.reachable_tiles(grid, [1, 1], 2, [], [], False)
    assert [2, 1] in tiles and [1, 3] in tiles and [3, 3] not in tiles
    path = movement.find_path(grid, [1, 1], [3, 2], [], False)
    assert len(path) == 6 and path[0] == [1, 1] and path[5] == [3, 2]
    assert movement.find_path(grid, [1, 1], [3, 1], [], False) == []
    assert movement.tile_distance([1, 1], [3, 2]) == 3
    game = make_test_game()
    frodo = game["heroes"][0]
    assert movement.refresh_vision(game) > 0
    assert game["seen"][frodo["pos"][1]][frodo["pos"][0]]
    assert game["known"][frodo["pos"][1]][frodo["pos"][0]] == "."
    for hero in game["heroes"]:
        hero["exhausted"] = True
    assert movement.refresh_vision(game) == 0
    walled = [list("#####"), list("#.#.#"), list("#####")]
    small = {"grid": walled, "seen": movement.blank_grid(walled, False), "known": movement.blank_grid(walled, "#"),
             "heroes": [{"pos": [1, 1], "exhausted": False}]}
    movement.refresh_vision(small)
    assert small["seen"][1][1] and not small["seen"][1][3]
    tiles = chambers.box_tiles([1, 1, 4, 3])
    assert len(tiles) == 12 and len(chambers.connected(tiles)) == 12
    assert len(chambers.shape_tiles("round", [1, 1, 6, 6])) < 36
    return True


def test_logbook():
    """receives nothing; checks check_game_over, write_log and write_summary; returns True."""
    up = [{"exhausted": False}, {"exhausted": True}]
    down = [{"exhausted": True}, {"exhausted": True}]
    assert logbook.check_game_over(up, 3, 20, False) == ""
    assert logbook.check_game_over(up, 3, 20, True) == "win"
    assert logbook.check_game_over(up, 20, 20, False) == "lose"
    assert logbook.check_game_over(down, 3, 20, False) == "lose"
    assert logbook.write_log(["test line one", "test line two"], 0) == 2
    stats = game_data.new_stats()
    stats["rounds"] = 4
    stats["damage_dealt"] = 30
    summary = logbook.write_summary(stats)
    assert summary["average_dealt"] == 7.5
    assert logbook.write_summary(game_data.new_stats())["average_dealt"] == 0
    return True


def hand_names(hero):
    """receives a hero; returns the names of the cards in their hand, deck and discard pile, for comparing."""
    names = []
    for pile in ["hand", "deck", "discard"]:
        for card in hero[pile]:
            names.append(pile + ":" + card["name"])
    return names


def test_saves():
    """receives nothing; checks that a game saved to a file loads back the same, and that a broken file gives None; returns True."""
    random.seed(4)
    game = make_test_game()
    game["round"] = 7
    game["doom"] = 9
    game["heroes"][1]["hp"] = 5
    game["units"][0]["models"][0]["hp"] = 1
    game["plan"][3]["prepared"] = ["trap", "guard"]
    assert savegame.save_game(game, "test_save")
    loaded = savegame.load_game(game["data"], "test_save")
    assert loaded is not None
    assert loaded["round"] == 7 and loaded["doom"] == 9 and loaded["seed"] == game["seed"]
    assert loaded["grid"] == game["grid"] and loaded["known"] == game["known"]
    assert len(loaded["plan"]) == len(game["plan"]) and loaded["plan"][3]["prepared"] == ["trap", "guard"]
    assert loaded["doors"] == game["doors"] and loaded["boss_door"] == game["boss_door"]
    for index in range(len(game["heroes"])):
        old = game["heroes"][index]
        new = loaded["heroes"][index]
        assert new["name"] == old["name"] and new["hp"] == old["hp"] and new["pos"] == old["pos"]
        assert hand_names(new) == hand_names(old)
    assert len(loaded["units"]) == len(game["units"])
    assert loaded["units"][0]["models"][0] == game["units"][0]["models"][0]
    assert loaded["hero_deck"] == game["hero_deck"] and loaded["memory"] == game["memory"]
    assert "test_save" in savegame.list_saves()
    assert "round 7" in savegame.save_summary("test_save")
    broken = open("test_save.sav", "w")
    broken.write("GAME | game | round=oops" + chr(10))
    broken.close()
    assert savegame.load_game(game["data"], "test_save") is None
    assert savegame.load_game(game["data"], "no_such_save") is None
    os.remove("test_save.sav")
    return True


def test_spears_ahead():
    """receives nothing; checks that Spears never changes the chamber the party is in, only chambers ahead, and that his preparations appear when one is opened; returns True."""
    random.seed(6)
    game = make_test_game()
    before = []
    for row in game["grid"]:
        before.append(list(row))
    units = len(game["units"])
    for number in range(40):
        spears_ai.reinforce(game)
    assert game["grid"] == before and len(game["units"]) == units
    prepared = 0
    for chamber in game["plan"]:
        if chamber["carved"] or chamber["kind"] == "boss":
            assert chamber["prepared"] == []
        prepared += len(chamber["prepared"])
    assert prepared > 0
    target = None
    for door in game["doors"]:
        if door["from"] == 0:
            target = game["plan"][door["to"]]
    target["prepared"] = ["guard", "guard", "trap"]
    game["units"] = []
    spears_ai.check_room_clear(game, 0)
    frodo_game.enter_room(game, target["id"])
    assert len(game["units"]) >= 2
    return True


def run_tests():
    """receives nothing; runs every test and prints the results; returns how many passed."""
    tests = [test_load_dungeon, test_combat, test_cards, test_spears, test_spears_ahead, test_saves,
             test_movement, test_logbook]
    passed = 0
    for test in tests:
        test()
        print("passed:", test.__name__)
        passed += 1
    print("All", passed, "test groups passed.")
    return passed


if __name__ == "__main__":
    run_tests()
