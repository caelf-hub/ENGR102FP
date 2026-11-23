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
    """Team-written. [Owner: Guilherme] receives Spears's memory dictionary; returns the party habit he will punish next: "melee", "ranged", "loot", "clump", "rest" or "none".

    Called by: frodo_game.enter_room
    Decides: if scores[habit] > best_score
    Loops: for habit in scores
    Why: Scores each party habit from Spears's memory (melee hits, ranged hits, chests x3, huddling x2). The
        highest score above 3 is the habit he counters; if nothing scores above 3 the answer is 'none'.
    """
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
    """Team-written. [Owner: Guilherme] receives Spears's memory; halves every count so newer habits matter more; returns the memory.

    Called by: frodo_game.enter_room
    Loops: for key in memory
    """
    for key in memory:
        memory[key] = memory[key] // 2
    return memory


def unit_plan(counter, step, kind):
    """Team-written. [Owner: Guilherme] receives the habit to counter, how far along the main path this chamber is and its kind; returns the list of unit type names Spears deploys.

    Called by: deploy_room
    Decides: if counter == "melee"; if counter == "ranged"; if counter == "loot"; if counter == "clump"; if
        kind == "side" or kind == "start"; if step >= 6
    """
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
    """Team-written. [Owner: Guilherme] receives the room styles and the habit to counter; returns a random style that matches (or any normal style).

    Called by: generate_room
    Decides: if style["counters"] == counter; if style["counters"] != "final"; if len(matches) > 0
    Loops: for style in styles
    """
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
    """Team-written. [Owner: Guilherme] receives the game; plans the whole dungeon, starts the map as solid rock and carves the boss arena (its outline is known from the start); returns how many chambers were planned.

    Called by: frodo_game.start_dungeon
    Uses: chambers.blank_map, movement.blank_grid, chambers.plan_dungeon, chambers.owner_grid, boss_chamber,
        chambers.carve_arena
    """
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
    """Team-written. [Owner: Guilherme] receives the game; returns the boss arena's chamber dictionary.

    Called by: build_dungeon, summon_guards
    Decides: if chamber["kind"] == "boss"
    Loops: for chamber in game["plan"]
    """
    for chamber in game["plan"]:
        if chamber["kind"] == "boss":
            return chamber
    return game["plan"][len(game["plan"]) - 1]


def chamber_at(game, tile):
    """Team-written. [Owner: Guilherme] receives the game and a tile; returns the chamber whose zone holds that tile, or None.

    Called by: nobody in the game (only the tests, or not used)
    Decides: if number < 0
    """
    number = game["owners"][tile[1]][tile[0]]
    if number < 0:
        return None
    return game["plan"][number]


def door_at(game, tile):
    """Team-written. [Owner: Guilherme] receives the game and a tile; returns the door record {"tile", "from", "to"} on that tile, or None.

    Called by: frodo_game.step_on_tile
    Decides: if door["tile"] == tile
    Loops: for door in game["doors"]
    """
    for door in game["doors"]:
        if door["tile"] == tile:
            return door
    return None


def place_letters(grid, free, letter, count):
    """Team-written. [Owner: Guilherme] receives the map grid, the list of free floor tiles, a tile letter and a count; puts that letter on random free tiles (removing them from the list); returns how many were placed.

    Called by: furnish, apply_preparations
    Loops: while placed < count and len(free) > 0
    """
    placed = 0
    while placed < count and len(free) > 0:
        tile = free.pop(random.randrange(len(free)))
        grid[tile[1]][tile[0]] = letter
        placed += 1
    return placed


def furnish(game, room, style, counter):
    """Team-written. [Owner: Guilherme] receives the game, the new room, its style and the habit to counter; fills the chamber with chests, traps, cover and shrines, twisted to punish that habit (side chambers get an extra chest); returns how many floor tiles are still empty.

    Called by: generate_room
    Uses: movement.tile_distance, place_letters
    Decides: if tile not in room["starts"] and movement.tile_distance(til...; if room["kind"] == "side"; if
        counter == "loot" and random.randint(1, 2) == 1; if counter == "clump"; if counter == "ranged"; if
        counter == "rest"
    Loops: for tile in room["tiles"]; for number in range(chests)
    """
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
    """Team-written. [Owner: Guilherme] receives the game, the new room and the habit to counter; Spears deploys his units in the far half of the chamber; returns how many units were placed.

    Called by: generate_room
    Uses: unit_plan, chambers.far_tiles, movement.hero_tiles, movement.model_tiles, add_unit
    Decides: if len(room["tiles"]) < 26; if len(room["tiles"]) < 18
    Loops: for type_name in plan
    """
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
    """Team-written. [Owner: Guilherme] receives the game, a room, a unit type, a spawn tile and the tiles already taken; makes the unit, stands it around the spawn and adds it to the room; returns the unit (None if no model fitted).

    Called by: deploy_room, deploy_boss, apply_preparations, summon_guards
    Uses: make_unit, place_models
    Decides: if len(unit["models"]) == 0
    """
    game["unit_count"] += 1
    unit = make_unit(game["data"], type_name, game["unit_count"])
    unit["chamber"] = room["id"]
    place_models(game["grid"], unit, spawn, taken)
    if len(unit["models"]) == 0:
        return None
    room["units"].append(unit)
    return unit


def deploy_boss(game, room):
    """Team-written. [Owner: Guilherme] receives the game and the boss arena room; stands the Warlord at his mark and his guards at theirs; returns how many units were placed.

    Called by: generate_room
    Uses: movement.hero_tiles, movement.model_tiles, add_unit
    Loops: for index in range(min(len(guards), len(markers["G"])))
    """
    markers = room["markers"]
    taken = movement.hero_tiles(game["heroes"]) + movement.model_tiles(game["units"])
    add_unit(game, room, "Warlord", markers["W"][0], taken)
    guards = ["Iron Guard", "Orc Brutes"]
    for index in range(min(len(guards), len(markers["G"]))):
        add_unit(game, room, guards[index], markers["G"][index], taken)
    game["spawns"] = room["tiles"]
    return len(room["units"])


def place_exits(game, chamber):
    """Team-written. [Owner: Guilherme] receives the game and a freshly carved chamber; puts a sealed door in its wall towards every chamber that branches off it; returns the door to the main path (or None).

    Called by: generate_room
    Uses: chambers.children, chambers.box_center, chambers.zone_box, nearest_tile, chambers.pick_door
    Decides: if child["kind"] == "boss"; if tile is None; if child["kind"] == "boss"; if child["kind"] !=
        "side"
    Loops: for child in chambers.children(game["plan"], chamber["i...
    """
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
    """Team-written. [Owner: Guilherme] receives a list of tiles and a point; returns the tile closest to the point.

    Called by: place_exits
    Uses: movement.tile_distance
    Decides: if movement.tile_distance(tile, point) < movement.tile_dista...
    Loops: for tile in tiles
    """
    best = tiles[0]
    for tile in tiles:
        if movement.tile_distance(tile, point) < movement.tile_distance(best, point):
            best = tile
    return best


def connect_chamber(game, chamber):
    """Team-written. [Owner: Guilherme] receives the game and the chamber being entered; digs a corridor from the door that leads to it and swings that door open for good; returns the door tile, or None for the first chamber.

    Called by: generate_room
    Uses: chambers.dig_corridor
    Decides: if door["to"] == chamber["id"]
    Loops: for door in game["doors"]
    """
    for door in game["doors"]:
        if door["to"] == chamber["id"]:
            allowed = [-1, door["from"], door["to"]]
            chambers.dig_corridor(game["grid"], door["tile"], chamber["tiles"], game["owners"], allowed)
            game["grid"][door["tile"][1]][door["tile"][0]] = "d"
            return door["tile"]
    return None


def make_unit(data, type_name, number):
    """AI-assisted: [Owner: Guilherme] receives the data, a unit type name and a unit number; returns a new unit dictionary with no models placed yet.

    Called by: add_unit
    """
    unit = dict(data["units"][type_name])
    unit["type"] = type_name
    unit["name"] = type_name + " " + LETTERS[number % 26]
    unit["start_models"] = unit["models"]
    unit["models"] = []
    unit["init"] = 50
    unit["goal"] = [0, 0]
    return unit


def place_models(grid, unit, spawn, taken):
    """AI-assisted: [Owner: Guilherme] receives the grid, a unit, a spawn tile and the tiles already taken; stands the unit's models on and around the spawn; returns how many were placed.

    Called by: add_unit
    Uses: movement.reachable_tiles
    Decides: if len(unit["models"]) == unit["start_models"]; if tile not in taken
    Loops: for tile in tiles
    """
    tiles = [spawn] + movement.reachable_tiles(grid, spawn, COHERENCY, [], [], False)
    for tile in tiles:
        if len(unit["models"]) == unit["start_models"]:
            break
        if tile not in taken:
            unit["models"].append({"pos": [tile[0], tile[1]], "hp": unit["wounds"]})
            taken.append(tile)
    return len(unit["models"])


def generate_room(game, number, counter):
    """Team-written. [Owner: Guilherme] receives the game, the number of the chamber being opened and the party habit Spears wants to counter; carves the chamber (the arena is already carved), furnishes it and deploys his units; returns the room dictionary.

    Called by: frodo_game.enter_room
    Uses: pick_style, chambers.carve_chamber, connect_chamber, place_exits, chambers.far_cluster,
        deploy_boss, furnish, deploy_room, apply_preparations
    Decides: if kind == "boss"; if kind == "side"; if kind != "boss"; if kind == "side"; if entry is None;
        if far_from is None
    Why: Picks a style that counters the habit (side chambers lean towards loot), carves it, digs the
        corridor from its door, places the exits, then furnishes it and deploys enemies. The boss arena is
        carved at the start and gets the Warlord instead.
    """
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
        apply_preparations(game, room, chamber)
    return room


# ---------------------------------------------------------------- unit helpers

def find_unit(units, name):
    """Team-written. [Owner: Guilherme] receives the unit list and a unit name; returns that unit, or None if it has been destroyed.

    Called by: frodo_game.take_turn
    Decides: if unit["name"] == name
    Loops: for unit in units
    """
    for unit in units:
        if unit["name"] == name:
            return unit
    return None


def unit_visible(game, unit):
    """Team-written. [Owner: Guilherme] receives the game and a unit; returns True if the party can see at least one of its models right now.

    Called by: frodo_game.spears_phase, unit_charge, break_unit, unit_morale
    Decides: if game["seen"][model["pos"][1]][model["pos"][0]]
    Loops: for model in unit["models"]
    """
    for model in unit["models"]:
        if game["seen"][model["pos"][1]][model["pos"][0]]:
            return True
    return False


def pick_initiative(unit):
    """Team-written. [Owner: Guilherme] receives a unit; returns a random activation initiative that suits its role (fast units go early, heavy ones late).

    Called by: frodo_game.prepare_heroes
    Decides: if unit["role"] == "fast"; if unit["role"] == "ranged"; if unit["role"] == "heavy"
    """
    if unit["role"] == "fast":
        return random.randint(10, 35)
    elif unit["role"] == "ranged":
        return random.randint(25, 55)
    elif unit["role"] == "heavy":
        return random.randint(55, 90)
    else:
        return random.randint(35, 75)


def pick_target(game, unit):
    """Team-written. [Owner: Guilherme] receives the game and a unit; returns the hero Spears wants dead most (weak and close), or None if no hero stands.

    Called by: frodo_game.spears_phase
    Uses: movement.tile_distance
    Decides: if len(unit["models"]) == 0; if hero["exhausted"]; if score < best_score
    Loops: for hero in game["heroes"]
    Why: Scores every standing hero as hp x 2 + distance and picks the lowest, so Spears goes for weak
        heroes that are close.
    """
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
    """Team-written. [Owner: Guilherme] receives a unit, one of its models and a tile; returns True if the model would be within 2 tiles of another model of the unit there.

    Called by: best_tile
    Uses: movement.tile_distance
    Decides: if len(unit["models"]) < 2; if other is not model and movement.tile_distance(tile, other...
    Loops: for other in unit["models"]
    """
    if len(unit["models"]) < 2:
        return True
    for other in unit["models"]:
        if other is not model and movement.tile_distance(tile, other["pos"]) <= COHERENCY:
            break
    else:
        return False
    return True


def goal_tile(game, unit, target):
    """Team-written. [Owner: Guilherme] receives the game, a unit and its target hero; returns the tile the unit heads for (heavy units hold the door until heroes come close).

    Called by: move_unit
    Uses: movement.tile_distance
    Decides: if unit["role"] == "heavy" and far and game["door"] is not None
    """
    leader = unit["models"][0]["pos"]
    far = movement.tile_distance(leader, target["pos"]) > 6
    if unit["role"] == "heavy" and far and game["door"] is not None:
        return game["door"]
    return target["pos"]


def is_flank(game, unit, tile):
    """Team-written. [Owner: Guilherme] receives the game, a unit and a tile next to its goal; returns True if another enemy model stands on the opposite side (a flank).

    Called by: tile_score
    Uses: movement.model_at
    """
    goal = unit["goal"]
    opposite = [goal[0] * 2 - tile[0], goal[1] * 2 - tile[1]]
    return movement.model_at(game["units"], opposite) is not None


def ranged_score(steps, reach):
    """Team-written. [Owner: Guilherme] receives the distance to the target and the shooting range; returns a score (low is good) for keeping a safe shooting distance.

    Called by: tile_score
    Decides: if steps < 3; if steps <= reach
    """
    if steps < 3:
        return 20 + (3 - steps) * 5
    elif steps <= reach:
        return reach - steps
    else:
        return 10 + (steps - reach) * 10


def tile_score(game, unit, tile, steps_map):
    """Team-written. [Owner: Guilherme] receives the game, a unit, a tile and the step map from the goal; returns how good that tile is (low is good).

    Called by: best_tile
    Uses: ranged_score, is_flank
    Decides: if steps < 0; if unit["role"] == "ranged"; if steps == 1 and is_flank(game, unit, tile)
    """
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
    """Team-written. [Owner: Guilherme] receives the game, a unit, one model, the step map from the goal and a move limit; returns the best tile that keeps coherency.

    Called by: move_unit
    Uses: movement.hero_tiles, movement.model_tiles, movement.reachable_tiles, tile_score, coherency_ok
    Decides: if not coherency_ok(unit, model, best); if not coherency_ok(unit, model, tile); if score <
        best_score
    Loops: for tile in options
    """
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
    """Team-written. [Owner: Guilherme] receives the game, a unit, its target hero and a move limit; moves every model toward the goal (remembering where each came from, for the animation); returns how many models moved.

    Called by: frodo_game.spears_phase, unit_charge
    Uses: goal_tile, movement.step_map, best_tile
    Decides: if tile != model["pos"]
    Loops: for model in unit["models"]
    Why: Builds a distance map from the unit's goal; each model then steps to the best tile it can reach
        that keeps it within 2 tiles of another model of its unit (coherency).
    """
    unit["goal"] = goal_tile(game, unit, target)
    steps_map = movement.step_map(game["grid"], unit["goal"], [], True)
    moved = 0
    for model in unit["models"]:
        tile = best_tile(game, unit, model, steps_map, steps)
        if tile != model["pos"]:
            game["moves"].append({"model": model, "from": list(model["pos"])})
            model["pos"] = [tile[0], tile[1]]
            moved += 1
    return moved


def choose_victim(game, model, reach, target):
    """Team-written. [Owner: Guilherme] receives the game, a model, its reach and the unit's target; returns the hero this model attacks (the target if in reach, else the weakest in reach, else None).

    Called by: unit_shoot, unit_fight
    Uses: movement.tile_distance
    Decides: if not target["exhausted"] and movement.tile_distance(model[...; if hero["exhausted"] or
        movement.tile_distance(model["pos"],...; if victim is None or hero["hp"] < victim["hp"]
    Loops: for hero in game["heroes"]
    """
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
    """Team-written. [Owner: Guilherme] receives the game, the attacking unit and the hero; returns 1 if the hero is behind cover from a shot, else 0.

    Called by: unit_attack
    Decides: if unit["role"] == "ranged" and spot == "~"
    """
    spot = game["grid"][hero["pos"][1]][hero["pos"][0]]
    if unit["role"] == "ranged" and spot == "~":
        return 1
    return 0


def hero_falls(game, hero):
    """Team-written. [Owner: Guilherme] receives the game and a hero with no hp; marks the hero exhausted and returns a message.

    Called by: frodo_game.spring_trap, frodo_game.mark_exhausted, splash, unit_attack
    Uses: logbook.say
    Decides: if hero["kind"] == "leader"
    """
    hero["exhausted"] = True
    if hero["kind"] == "leader":
        return logbook.say(game, "Frodo is exhausted! The party fights on without him.")
    return logbook.say(game, hero["name"] + " is exhausted and leaves the fight!")


def splash(game, unit, hero):
    """Team-written. [Owner: Guilherme] receives the game, an area-attack unit and the hero it hit; deals 1 damage to heroes next to that hero; returns how many were splashed.

    Called by: unit_attack
    Uses: movement.tile_distance, combat.apply_damage, feel_hit, logbook.add_float, hero_falls
    Decides: if other["exhausted"] or not near; if other["hp"] <= 0
    Loops: for other in game["heroes"]
    """
    count = 0
    for other in game["heroes"]:
        near = movement.tile_distance(other["pos"], hero["pos"]) == 1
        if other["exhausted"] or not near:
            continue
        combat.apply_damage(other, unit["aoe"])
        feel_hit(game, other, unit["aoe"], "")
        game["stats"]["damage_taken"] += unit["aoe"]
        logbook.add_float(game, other["pos"], "-" + str(unit["aoe"]), "crimson")
        count += 1
        if other["hp"] <= 0:
            hero_falls(game, other)
    return count


def feel_hit(game, hero, damage, modifier):
    """Team-written. [Owner: Guilherme] receives the game, a hero who was just hit, the damage and the modifier card; asks the screen to flash the hero's portrait, and to shake on a big hit; returns the damage.

    Called by: frodo_game.spring_trap, splash, unit_attack
    Decides: if damage > 0; if damage >= 4 or modifier == "x2"
    """
    if damage > 0:
        game["fx"].append({"kind": "hurt", "name": hero["name"]})
    if damage >= 4 or modifier == "x2":
        game["fx"].append({"kind": "shake", "power": min(10, 3 + damage)})
    return damage


def unit_attack(game, unit, model, hero):
    """Team-written. [Owner: Guilherme] receives the game, a unit, one of its models and a hero; resolves one enemy attack and returns the damage dealt.

    Called by: unit_shoot, unit_fight
    Uses: cover_bonus, combat.roll_attack, combat.apply_damage, feel_hit, logbook.say, logbook.add_float,
        splash, hero_falls
    Decides: if unit["aoe"] > 0; if unit["range"] > 1; if unit["aoe"] > 0 and damage > 0; if hero["hp"] <= 0
    Why: The hero's shield, armour and cover reduce the hit; game['enemy_bonus'] comes from the difficulty.
        Bomb units also splash heroes next to the target. A hero at 0 HP falls.
    """
    shield = hero["shield"] + hero["armor"] + cover_bonus(game, unit, hero)
    style = "melee"
    if unit["aoe"] > 0:
        style = "bomb"
    elif unit["range"] > 1:
        style = "ranged"
    game["fx"].append({"kind": "strike", "from": list(model["pos"]), "to": list(hero["pos"]), "style": style})
    result = combat.roll_attack(game, "enemy", max(0, unit["attack"] + game["enemy_bonus"]), shield)
    damage = result[0]
    combat.apply_damage(hero, damage)
    feel_hit(game, hero, damage, result[1])
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
    """Team-written. [Owner: Guilherme] receives the game, a ranged unit and its target; every model in range shoots; returns the total damage.

    Called by: frodo_game.spears_phase
    Uses: choose_victim, unit_attack
    Decides: if victim is not None
    Loops: for model in unit["models"]
    """
    total = 0
    for model in unit["models"]:
        victim = choose_victim(game, model, unit["range"], target)
        if victim is not None:
            total += unit_attack(game, unit, model, victim)
    return total


def touching_hero(game, unit):
    """Team-written. [Owner: Guilherme] receives the game and a unit; returns True if any of its models stands next to a hero.

    Called by: unit_charge
    Uses: movement.hero_tiles, movement.tile_distance
    Decides: if movement.tile_distance(model["pos"], tile) == 1
    Loops: for model in unit["models"]; for tile in movement.hero_tiles(game["heroes"])
    """
    for model in unit["models"]:
        for tile in movement.hero_tiles(game["heroes"]):
            if movement.tile_distance(model["pos"], tile) == 1:
                return True
    return False


def nearest_gap(unit, target):
    """Team-written. [Owner: Guilherme] receives a unit and its target hero; returns how many tiles the closest model must cross to stand next to the hero.

    Called by: unit_charge
    Uses: movement.tile_distance
    Decides: if distance < gap
    Loops: for model in unit["models"]
    """
    gap = 99
    for model in unit["models"]:
        distance = movement.tile_distance(model["pos"], target["pos"]) - 1
        if distance < gap:
            gap = distance
    return gap


def unit_charge(game, unit, target):
    """Team-written. [Owner: Guilherme] receives the game, a melee unit and its target; rolls a charge distance and moves in if it is enough; returns True on a successful charge.

    Called by: frodo_game.spears_phase
    Uses: touching_hero, nearest_gap, move_unit, logbook.tell, unit_visible
    Decides: if touching_hero(game, unit) or target["exhausted"]; if unit["role"] == "fast"; if
        nearest_gap(unit, target) <= roll
    Why: Rolls 1-6 (+2 for fast units). If the closest model can reach the target with that roll, the unit
        moves in; otherwise the charge falls short. No charge if already next to a hero.
    """
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
    """Team-written. [Owner: Guilherme] receives the game, a unit and its target; every model next to a hero attacks; returns the total damage.

    Called by: frodo_game.spears_phase
    Uses: choose_victim, unit_attack
    Decides: if victim is not None
    Loops: for model in unit["models"]
    """
    total = 0
    for model in unit["models"]:
        victim = choose_victim(game, model, 1, target)
        if victim is not None:
            total += unit_attack(game, unit, model, victim)
    return total


# ---------------------------------------------------------------- morale and losses

def morale_test(leadership, roll):
    """Team-written. [Owner: Guilherme] receives a unit's leadership and a 2d6 roll; returns True if the unit holds (roll is leadership or less).

    Called by: unit_morale
    Why: The 2d6 morale rule in one line: the unit passes when roll <= leadership.
    """
    return roll <= leadership


def check_room_clear(game, number):
    """Team-written. [Owner: Guilherme] receives the game and a chamber number; if none of that chamber's units are left, unseals all its doors and returns True.

    Called by: frodo_game.install_room, destroy_unit
    Uses: logbook.say
    Decides: if chamber["cleared"]; if unit["chamber"] == number; if door["from"] == number and
        game["grid"][tile[1]][tile[0]]...; if opened > 0
    Loops: for unit in game["units"]; for door in game["doors"]
    """
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
    """Team-written. [Owner: Guilherme] receives the game, a unit with no models left and the tile where it fell; removes the unit, maybe drops loot, and returns True if loot dropped.

    Called by: remove_model
    Uses: logbook.say, check_room_clear
    Decides: if unit["type"] == "Warlord"; if dropped
    """
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
    """Team-written. [Owner: Guilherme] receives the game, a unit and a dead or fleeing model; removes the model and returns how many models the unit has left.

    Called by: frodo_game.hero_attack, break_unit
    Uses: destroy_unit
    Decides: if len(unit["models"]) == 0
    """
    tile = model["pos"]
    game["fx"].append({"kind": "puff", "tile": list(tile)})
    unit["models"].remove(model)
    game["stats"]["enemies_slain"] += 1
    if len(unit["models"]) == 0:
        destroy_unit(game, unit, tile)
    return len(unit["models"])


def safest_tile(game, model, steps):
    """Team-written. [Owner: Guilherme] receives the game, a model and a move limit; returns the reachable tile farthest from every hero.

    Called by: fall_back
    Uses: movement.hero_tiles, movement.reachable_tiles, movement.model_tiles, movement.tile_distance
    Decides: if gap > best_gap
    Loops: for tile in [model["pos"]] + options; for hero_tile in heroes
    """
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
    """Team-written. [Owner: Guilherme] receives the game and a broken unit; every model runs away from the heroes (remembering where each came from, for the animation); returns how many models moved.

    Called by: break_unit
    Uses: safest_tile
    Decides: if tile != model["pos"]
    Loops: for model in unit["models"]
    """
    moved = 0
    for model in unit["models"]:
        tile = safest_tile(game, model, unit["move"])
        if tile != model["pos"]:
            game["moves"].append({"model": model, "from": list(model["pos"])})
            model["pos"] = [tile[0], tile[1]]
            moved += 1
    return moved


def break_unit(game, unit):
    """Team-written. [Owner: Guilherme] receives the game and a unit that failed morale; it randomly loses a model or falls back; returns what happened.

    Called by: unit_morale
    Uses: unit_visible, logbook.tell, remove_model, fall_back
    Decides: if visible; if random.randint(1, 2) == 1
    """
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
    """Team-written. [Owner: Guilherme] receives the game and a unit; if it is below half strength it rolls 2d6 against leadership; returns True if the unit holds.

    Called by: frodo_game.spears_phase
    Uses: unit_visible, morale_test, logbook.tell, break_unit
    Decides: if alive == 0 or unit["start_models"] < 2 or alive * 2 >= un...; if
        morale_test(unit["leadership"], roll)
    Why: Only units below half their starting models test. Roll 2d6: roll <= leadership holds; otherwise
        break_unit() makes one model flee or the unit falls back.
    """
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
    """Team-written. [Owner: Guilherme] receives the Doom Track value, how much to add and the track's end; returns the new value (never past the end).

    Called by: frodo_game.install_room, frodo_game.spring_trap, frodo_game.end_round
    Decides: if doom > doom_max
    """
    doom = doom + amount
    if doom > doom_max:
        doom = doom_max
    return doom


def prepare_ahead(game, chamber):
    """Team-written. [Owner: Guilherme] receives the game and a chamber the party has not opened yet; Spears secretly adds a trap, a guard or a trapped chest to it; returns what he added.

    Called by: reinforce
    Uses: logbook.note
    """
    choice = random.choice(["trap", "guard", "trapped chest"])
    chamber["prepared"].append(choice)
    logbook.note(game, "Spears prepares a " + choice + " in a chamber ahead (unseen by the party).")
    return choice


def reinforce(game):
    """Team-written. [Owner: Guilherme] receives the game; after a round Spears may secretly strengthen one chamber the party has not opened yet (never the one they are in); returns what he added ("" if he waits).

    Called by: frodo_game.end_round
    Uses: prepare_ahead, logbook.say, logbook.add_banner
    Decides: if random.randint(1, 3) != 1; if not chamber["carved"] and chamber["kind"] != "boss" and l...;
        if len(ahead) == 0
    Loops: for chamber in game["plan"]
    Why: A 1 in 3 chance after each round. Spears never touches the chamber the party is in: he adds a trap,
        guard or trapped chest to a chamber that has not been opened yet (never the boss arena).
    """
    if random.randint(1, 3) != 1:
        return ""
    ahead = []
    for chamber in game["plan"]:
        if not chamber["carved"] and chamber["kind"] != "boss" and len(chamber["prepared"]) < 3:
            ahead.append(chamber)
    if len(ahead) == 0:
        return ""
    choice = prepare_ahead(game, random.choice(ahead))
    logbook.say(game, "Spears is preparing something in the chambers ahead...")
    logbook.add_banner(game, "Spears is preparing something in the chambers ahead...")
    return choice


def apply_preparations(game, room, chamber):
    """Team-written. [Owner: Guilherme] receives the game, a freshly carved room and its chamber; puts in the traps, guards and trapped chests Spears prepared; returns how many were added.

    Called by: generate_room
    Uses: movement.tile_distance, movement.hero_tiles, movement.model_tiles, place_letters, add_unit
    Decides: if spot == "." and tile not in room["starts"] and movement.t...; if choice == "trap"; if choice
        == "trapped chest"; if len(free) > 0
    Loops: for tile in room["tiles"]; for unit in room["units"]; for choice in chamber["prepared"]
    """
    free = []
    for tile in room["tiles"]:
        spot = game["grid"][tile[1]][tile[0]]
        if spot == "." and tile not in room["starts"] and movement.tile_distance(tile, room["origin"]) > 2:
            free.append(tile)
    taken = movement.hero_tiles(game["heroes"]) + movement.model_tiles(game["units"])
    for unit in room["units"]:
        taken = taken + movement.model_tiles([unit])
    for choice in chamber["prepared"]:
        if choice == "trap":
            place_letters(game["grid"], free, "T", 1)
        elif choice == "trapped chest":
            place_letters(game["grid"], free, "X", 1)
        elif len(free) > 0:
            add_unit(game, room, random.choice(BASIC_UNITS), random.choice(free), taken)
    return len(chamber["prepared"])


# ---------------------------------------------------------------- the boss

def warlord(game):
    """Team-written. [Owner: Guilherme] receives the game; returns the Warlord's unit if he is on the map, else None.

    Called by: nobody in the game (only the tests, or not used)
    Decides: if unit["type"] == "Warlord"
    Loops: for unit in game["units"]
    """
    for unit in game["units"]:
        if unit["type"] == "Warlord":
            return unit
    return None


def summon_guards(game, unit):
    """Team-written. [Owner: Guilherme] receives the game and the Warlord; his guards rush in at the free guard marks of the arena; returns a message.

    Called by: boss_check
    Uses: movement.hero_tiles, movement.model_tiles, boss_chamber, add_unit
    Decides: if spot not in taken
    Loops: for spot in spots; for summoned in room["units"]
    """
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
    """Team-written. [Owner: Guilherme] receives the Warlord; he grows stronger and faster; returns a message.

    Called by: boss_check
    """
    unit["attack"] += 2
    unit["move"] += 1
    return "The Warlord is wounded and ENRAGED! +2 attack, +1 move."


def boss_check(game, unit):
    """Team-written. [Owner: Guilherme] receives the game and a unit that was just hit; if it is the Warlord, moves him into his next phase at half and at a quarter of his wounds; returns the phase he is in (0, 1 or 2).

    Called by: frodo_game.hero_attack
    Uses: summon_guards, enrage, logbook.say, logbook.add_banner
    Decides: if unit["type"] != "Warlord" or len(unit["models"]) == 0; if game["boss_phase"] == 0 and left *
        2 <= unit["wounds"]; if game["boss_phase"] == 1 and left * 4 <= unit["wounds"]; if message != ""
    Why: At half wounds (phase 0 -> 1) the Warlord summons Iron Guard; at a quarter (phase 1 -> 2) he
        enrages: +2 attack, +1 move. Each happens only once.
    """
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
        game["fx"].append({"kind": "shake", "power": 9})
    return game["boss_phase"]
