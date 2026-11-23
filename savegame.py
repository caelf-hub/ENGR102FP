"""savegame.py - writes the whole game to a .sav file and reads it back.

A save file is plain text, one record per line, in the same style as dungeon_data.txt:
    KIND | name | key=value key=value ...
Lists are written with "/" between items, tiles as "col,row", and "_" stands for a space.
Everything is read back with split(), never with json.

Files: autosave.sav (written every time a door opens) and <name>.sav (written with Save / F3).
"""
import os

import chambers
import game_data
import movement

EMPTY = "-"


# ================================================================ writing values

def word(text):
    """Team-written. [Owner: Yassin] receives some text; returns it with spaces turned into _ so it fits in one key=value pair.

    Called by: names_text, record, game_line, chamber_line, unit_line
    """
    return str(text).replace(" ", "_").replace("|", "/")


def tile_text(tile):
    """Team-written. [Owner: Yassin] receives a tile [col, row] (or None); returns it written as "col,row" (or "-").

    Called by: tiles_text, game_line, hero_line, unit_line, save_lines
    Decides: if tile is None
    """
    if tile is None:
        return EMPTY
    return str(tile[0]) + "," + str(tile[1])


def tiles_text(tiles):
    """Team-written. [Owner: Yassin] receives a list of tiles; returns them written as "c,r/c,r/..." (or "-" if empty).

    Called by: game_line, chamber_line
    Uses: tile_text
    Decides: if len(tiles) == 0
    Loops: for tile in tiles
    """
    if len(tiles) == 0:
        return EMPTY
    parts = []
    for tile in tiles:
        parts.append(tile_text(tile))
    return "/".join(parts)


def names_text(names):
    """Team-written. [Owner: Yassin] receives a list of names; returns them written as "a_b/c_d" (or "-" if empty).

    Called by: card_names, game_line, hero_line, chamber_line
    Uses: word
    Decides: if len(names) == 0
    Loops: for name in names
    """
    if len(names) == 0:
        return EMPTY
    parts = []
    for name in names:
        parts.append(word(name))
    return "/".join(parts)


def card_names(pile):
    """Team-written. [Owner: Yassin] receives a list of cards; returns their names written with names_text().

    Called by: hero_line
    Uses: names_text
    Loops: for card in pile
    """
    names = []
    for card in pile:
        names.append(card["name"])
    return names_text(names)


def yes_no(value):
    """Team-written. [Owner: Yassin] receives True or False; returns "yes" or "no".

    Called by: game_line, hero_line, chamber_line
    Decides: if value
    """
    if value:
        return "yes"
    return "no"


def record(kind, name, pairs):
    """Team-written. [Owner: Yassin] receives a record kind, a name and a list of [key, value] pairs; returns one save-file line.

    Called by: game_line, hero_line, chamber_line, unit_line, number_line, save_lines
    Uses: word
    Loops: for pair in pairs
    """
    fields = []
    for pair in pairs:
        fields.append(pair[0] + "=" + str(pair[1]))
    return kind + " | " + word(name) + " | " + " ".join(fields)


# ================================================================ reading values

def read_tile(text):
    """Team-written. [Owner: Yassin] receives text like "3,4" (or "-"); returns the tile [3, 4] (or None).

    Called by: read_tiles, load_hero, load_unit, load_game_line, load_record
    Decides: if text == EMPTY
    """
    text = str(text)
    if text == EMPTY:
        return None
    pieces = text.split(",")
    return [int(pieces[0]), int(pieces[1])]


def read_tiles(text):
    """Team-written. [Owner: Yassin] receives text like "3,4/5,6" (or "-"); returns the list of tiles.

    Called by: load_chamber, load_game_line
    Uses: read_tile
    Decides: if text == EMPTY
    Loops: for piece in text.split("/")
    """
    text = str(text)
    tiles = []
    if text == EMPTY:
        return tiles
    for piece in text.split("/"):
        tiles.append(read_tile(piece))
    return tiles


def read_names(text):
    """Team-written. [Owner: Yassin] receives text like "Heroic Yap/Fetch" (or "-"); returns the list of names.

    Called by: read_pile, load_hero, load_chamber, load_unit, load_game_line
    Decides: if text == EMPTY
    """
    text = str(text)
    if text == EMPTY:
        return []
    return text.split("/")


def is_yes(value):
    """Team-written. [Owner: Yassin] receives "yes" or "no"; returns True for "yes".

    Called by: load_hero, load_chamber, load_game_line
    """
    return str(value) == "yes"


# ================================================================ the game as lines

def game_line(game):
    """Team-written. [Owner: Yassin] receives the game; returns the GAME line with all the single values (round, doom, chamber, ...).

    Called by: save_lines
    Uses: yes_no, word, tile_text, tiles_text, names_text, record
    """
    pairs = [["round", game["round"]], ["depth", game["depth"]], ["doom", game["doom"]],
             ["doom_max", game["doom_max"]], ["seed", game["seed"]], ["chamber", game["chamber"]],
             ["rarity", game["rarity"]], ["boss_phase", game["boss_phase"]], ["unit_count", game["unit_count"]],
             ["warlord_dead", yes_no(game["warlord_dead"])], ["counter", game["counter"]],
             ["room_name", word(game["room_name"])], ["door", tile_text(game["door"])],
             ["boss_door", tile_text(game["boss_door"])], ["spawns", tiles_text(game["spawns"])],
             ["inventory", names_text(game["inventory"])], ["chambers", len(game["plan"])],
             ["difficulty", game["difficulty"]], ["enemy_bonus", game["enemy_bonus"]]]
    return record("GAME", "game", pairs)


def hero_line(hero):
    """Team-written. [Owner: Yassin] receives a hero; returns their HERO line (health, place, stats, cards and items).

    Called by: save_lines
    Uses: tile_text, yes_no, card_names, names_text, record
    """
    pairs = [["hp", hero["hp"]], ["max_hp", hero["max_hp"]], ["pos", tile_text(hero["pos"])],
             ["move", hero["move"]], ["speed", hero["speed"]], ["attack_bonus", hero["attack_bonus"]],
             ["armor", hero["armor"]], ["exhausted", yes_no(hero["exhausted"])],
             ["hand", card_names(hero["hand"])], ["deck", card_names(hero["deck"])],
             ["discard", card_names(hero["discard"])], ["items", names_text(hero["items"])]]
    return record("HERO", hero["name"], pairs)


def chamber_line(chamber):
    """Team-written. [Owner: Yassin] receives a planned chamber; returns its CHAMBER line.

    Called by: save_lines
    Uses: yes_no, tiles_text, word, names_text, record
    Decides: if parent is None; if letter in markers
    Loops: for letter in ["W", "G"]
    """
    parent = chamber["parent"]
    if parent is None:
        parent = -1
    zone = chamber["zone"]
    markers = chamber["markers"]
    pairs = [["kind", chamber["kind"]], ["parent", parent], ["step", chamber["step"]],
             ["carved", yes_no(chamber["carved"])], ["cleared", yes_no(chamber["cleared"])],
             ["zone", str(zone[0]) + "," + str(zone[1]) + "," + str(zone[2]) + "," + str(zone[3])],
             ["cells", tiles_text(chamber["cells"])], ["name", word(chamber["name"]) or EMPTY],
             ["tiles", tiles_text(chamber["tiles"])], ["prepared", names_text(chamber["prepared"])]]
    for letter in ["W", "G"]:
        if letter in markers:
            pairs.append(["marks_" + letter, tiles_text(markers[letter])])
    return record("CHAMBER", chamber["id"], pairs)


def unit_line(unit):
    """Team-written. [Owner: Yassin] receives an enemy unit; returns its UNIT line (stats, chamber and every model's tile and wounds).

    Called by: save_lines
    Uses: tile_text, word, record
    Loops: for model in unit["models"]; for key in ["move", "attack", "toughness", "wounds", ...
    """
    models = []
    for model in unit["models"]:
        models.append(tile_text(model["pos"]) + "," + str(model["hp"]))
    pairs = [["type", word(unit["type"])], ["chamber", unit["chamber"]]]
    for key in ["move", "attack", "toughness", "wounds", "leadership", "range", "aoe", "start_models", "init"]:
        pairs.append([key, unit[key]])
    pairs.append(["goal", tile_text(unit["goal"])])
    pairs.append(["models", "/".join(models) or EMPTY])
    return record("UNIT", unit["name"], pairs)


def number_line(kind, values):
    """Team-written. [Owner: Yassin] receives a record kind and a dictionary of whole numbers (memory, stats, elements); returns its line.

    Called by: save_lines
    Uses: record
    Loops: for key in values
    """
    pairs = []
    for key in values:
        pairs.append([key, values[key]])
    return record(kind, "values", pairs)


def raw_line(kind, name, text):
    """Team-written. [Owner: Yassin] receives a record kind, a name and some text; returns a line that keeps the text exactly (for modifier decks and the log).

    Called by: save_lines
    """
    return kind + " | " + name + " | " + str(text).replace("|", "/")


def map_lines(kind, grid):
    """Team-written. [Owner: Yassin] receives a record kind and a grid of letters; returns one line per row.

    Called by: save_lines
    Loops: for row in grid
    """
    lines = []
    for row in grid:
        lines.append(kind + " | row | " + "".join(row))
    return lines


def save_lines(game):
    """Team-written. [Owner: Yassin] receives the game; returns every line of its save file.

    Called by: save_game
    Uses: game_line, hero_line, chamber_line, record, tile_text, unit_line, number_line, raw_line, map_lines
    Loops: for hero in game["heroes"]; for chamber in game["plan"]; for door in game["doors"]; for unit in
        game["units"]
    Why: One line per record (GAME, HERO, CHAMBER, DOOR, UNIT, MEMORY, STATS, ...) in the same 'KIND | name
        | key=value' style as dungeon_data.txt, read back later with split().
    """
    lines = ["# Frodo and the Dungeon Lord - saved game", game_line(game)]
    for hero in game["heroes"]:
        lines.append(hero_line(hero))
    for chamber in game["plan"]:
        lines.append(chamber_line(chamber))
    for door in game["doors"]:
        lines.append(record("DOOR", "door", [["tile", tile_text(door["tile"])], ["from", door["from"]],
                                             ["to", door["to"]]]))
    for unit in game["units"]:
        lines.append(unit_line(unit))
    lines.append(number_line("MEMORY", game["memory"]))
    lines.append(number_line("STATS", game["stats"]))
    lines.append(number_line("ELEMENTS", game["elements"]))
    for name in ["hero_deck", "hero_discard", "enemy_deck", "enemy_discard"]:
        lines.append(raw_line("MODS", name, "/".join(game[name]) or EMPTY))
    lines = lines + map_lines("GRID", game["grid"]) + map_lines("KNOWN", game["known"])
    for text in game["log"][-30:]:
        lines.append(raw_line("LOG", "line", text))
    return lines


def save_game(game, name):
    """Team-written. [Owner: Yassin] receives the game and a file name (without .sav); writes the whole game to name.sav; returns True if it worked.

    Called by: frodo_game.enter_room, frodo_game.save_game
    Uses: save_lines
    Loops: for line in save_lines(game)
    Why: Writes every line from save_lines() to name.sav. try/except OSError returns False instead of
        crashing if the file cannot be written.
    """
    try:
        save_file = open(name + ".sav", "w")
        for line in save_lines(game):
            save_file.write(line + "\n")
        save_file.close()
        return True
    except OSError:
        return False


# ================================================================ reading the game back

def find_in_deck(data, owner, name):
    """Team-written. [Owner: Yassin] receives the loaded data, a hero name and a card name; returns that hero's card dictionary.

    Called by: read_pile
    Decides: if card["name"] == name
    Loops: for card in data["cards"][owner]
    """
    for card in data["cards"][owner]:
        if card["name"] == name:
            return card
    raise KeyError(name)


def read_pile(data, owner, text):
    """Team-written. [Owner: Yassin] receives the loaded data, a hero name and a list of card names as text; returns the list of cards.

    Called by: load_hero
    Uses: read_names, find_in_deck
    Loops: for name in read_names(text)
    """
    pile = []
    for name in read_names(text):
        pile.append(find_in_deck(data, owner, name))
    return pile


def load_hero(game, data, name, fields):
    """Team-written. [Owner: Yassin] receives the game, the data, a hero name and the fields of their HERO line; puts the saved values on that hero; returns the hero.

    Called by: load_record
    Uses: game_data.find_hero, read_tile, is_yes, read_pile, read_names
    Loops: for key in ["hp", "max_hp", "move", "speed", "attack_...
    """
    hero = game_data.find_hero(game, name)
    for key in ["hp", "max_hp", "move", "speed", "attack_bonus", "armor"]:
        hero[key] = fields[key]
    hero["pos"] = read_tile(fields["pos"])
    hero["exhausted"] = is_yes(fields["exhausted"])
    hero["hand"] = read_pile(data, name, fields["hand"])
    hero["deck"] = read_pile(data, name, fields["deck"])
    hero["discard"] = read_pile(data, name, fields["discard"])
    hero["items"] = read_names(fields["items"])
    return hero


def load_chamber(game, data, number, fields):
    """Team-written. [Owner: Yassin] receives the game, the data, a chamber number and the fields of its CHAMBER line; adds that chamber to the plan; returns it.

    Called by: load_record
    Uses: chambers.make_chamber, read_tiles, is_yes, read_names
    Decides: if parent == -1; if "marks_" + letter in fields
    Loops: for piece in str(fields["zone"]).split(","); for letter in ["W", "G"]
    """
    zone = []
    for piece in str(fields["zone"]).split(","):
        zone.append(int(piece))
    parent = fields["parent"]
    if parent == -1:
        parent = None
    chamber = chambers.make_chamber(number, fields["kind"], read_tiles(fields["cells"]), parent, data["dungeon"])
    chamber.update({"zone": zone, "step": fields["step"], "carved": is_yes(fields["carved"])})
    chamber.update({"cleared": is_yes(fields["cleared"]), "tiles": read_tiles(fields["tiles"])})
    chamber["name"] = str(fields["name"]).replace(EMPTY, "")
    chamber["prepared"] = read_names(fields["prepared"])
    for letter in ["W", "G"]:
        if "marks_" + letter in fields:
            chamber["markers"][letter] = read_tiles(fields["marks_" + letter])
    game["plan"].append(chamber)
    return chamber


def load_unit(game, data, name, fields):
    """Team-written. [Owner: Yassin] receives the game, the data, a unit name and the fields of its UNIT line; rebuilds the unit with its models; returns it.

    Called by: load_record
    Uses: read_tile, read_names
    Loops: for key in ["move", "attack", "toughness", "wounds", ...; for piece in
        read_names(fields["models"])
    """
    unit = dict(data["units"][fields["type"]])
    unit.update({"type": fields["type"], "name": name, "chamber": fields["chamber"]})
    for key in ["move", "attack", "toughness", "wounds", "leadership", "range", "aoe", "start_models", "init"]:
        unit[key] = fields[key]
    unit["goal"] = read_tile(fields["goal"])
    unit["models"] = []
    for piece in read_names(fields["models"]):
        numbers = piece.split(",")
        unit["models"].append({"pos": [int(numbers[0]), int(numbers[1])], "hp": int(numbers[2])})
    game["units"].append(unit)
    return unit


def load_game_line(game, fields):
    """Team-written. [Owner: Yassin] receives the game and the fields of the GAME line; puts the saved single values back; returns the round number.

    Called by: load_record
    Uses: is_yes, read_tile, read_tiles, read_names
    Loops: for key in ["round", "depth", "doom", "doom_max", "se...
    """
    for key in ["round", "depth", "doom", "doom_max", "seed", "chamber", "rarity", "boss_phase", "unit_count"]:
        game[key] = fields[key]
    game["warlord_dead"] = is_yes(fields["warlord_dead"])
    game["counter"] = fields["counter"]
    game["room_name"] = str(fields["room_name"])
    game["door"] = read_tile(fields["door"])
    game["boss_door"] = read_tile(fields["boss_door"])
    game["spawns"] = read_tiles(fields["spawns"])
    game["inventory"] = read_names(fields["inventory"])
    game["difficulty"] = str(fields["difficulty"])
    game["enemy_bonus"] = fields["enemy_bonus"]
    return game["round"]


def load_raw(game, kind, name, text):
    """Team-written. [Owner: Yassin] receives the game and a GRID, KNOWN, MODS or LOG record; puts it back; returns the kind.

    Called by: build_game
    Decides: if kind == "GRID"; if kind == "KNOWN"; if kind == "MODS"; if text != EMPTY
    """
    if kind == "GRID":
        game["grid"].append(list(text))
    elif kind == "KNOWN":
        game["known"].append(list(text))
    elif kind == "MODS":
        game[name] = []
        if text != EMPTY:
            game[name] = text.split("/")
    else:
        game["log"].append(text)
    return kind


def load_record(game, data, kind, name, fields):
    """Team-written. [Owner: Yassin] receives the game, the data and one parsed key=value record; puts it back in the right place; returns the kind.

    Called by: build_game
    Uses: load_game_line, load_hero, load_chamber, read_tile, load_unit
    Decides: if kind == "GAME"; if kind == "HERO"; if kind == "CHAMBER"; if kind == "DOOR"; if kind ==
        "UNIT"; if kind == "MEMORY"
    """
    if kind == "GAME":
        load_game_line(game, fields)
    elif kind == "HERO":
        load_hero(game, data, name, fields)
    elif kind == "CHAMBER":
        load_chamber(game, data, int(name), fields)
    elif kind == "DOOR":
        game["doors"].append({"tile": read_tile(fields["tile"]), "from": fields["from"], "to": fields["to"]})
    elif kind == "UNIT":
        load_unit(game, data, name, fields)
    elif kind == "MEMORY":
        game["memory"].update(fields)
    elif kind == "STATS":
        game["stats"].update(fields)
    elif kind == "ELEMENTS":
        game["elements"].update(fields)
    return kind


def read_save(name):
    """Team-written. [Owner: Yassin] receives a save name (without .sav); returns the list of its lines split into [kind, name, rest], or None if the file cannot be opened.

    Called by: load_game, save_summary
    Decides: if len(parts) == 3 and not line.startswith("#")
    Loops: for line in lines
    """
    try:
        save_file = open(name + ".sav", "r")
        lines = save_file.readlines()
        save_file.close()
    except OSError:
        return None
    records = []
    for line in lines:
        parts = line.rstrip("\n").split("|", 2)
        if len(parts) == 3 and not line.startswith("#"):
            records.append([parts[0].strip(), parts[1].strip(), parts[2].strip()])
    return records


def party_names(records):
    """Team-written. [Owner: Yassin] receives the records of a save file; returns the names of the heroes in it.

    Called by: build_game, save_summary
    Decides: if item[0] == "HERO"
    Loops: for item in records
    """
    names = []
    for item in records:
        if item[0] == "HERO":
            names.append(item[1].replace("_", " "))
    return names


def build_game(data, records):
    """Team-written. [Owner: Yassin] receives the loaded data and the records of a save file; builds the whole game from them; returns the game.

    Called by: load_game
    Uses: game_data.new_game, party_names, load_raw, load_record, game_data.parse_fields,
        chambers.owner_grid, movement.blank_grid, movement.refresh_vision
    Decides: if item[0] in ["GRID", "KNOWN", "MODS", "LOG"]
    Loops: for key in ["grid", "known", "log", "plan", "doors", ...; for item in records
    Why: Makes a fresh game with new_game(), then overwrites it record by record. Afterwards it rebuilds
        what is not saved: the owner grid and what the heroes can see.
    """
    game = game_data.new_game(data, party_names(records), "Normal")
    for key in ["grid", "known", "log", "plan", "doors", "units"]:
        game[key] = []
    for item in records:
        if item[0] in ["GRID", "KNOWN", "MODS", "LOG"]:
            load_raw(game, item[0], item[1], item[2])
        else:
            load_record(game, data, item[0], item[1].replace("_", " "), game_data.parse_fields(item[2]))
    game["owners"] = chambers.owner_grid(game["grid"], game["plan"])
    game["seen"] = movement.blank_grid(game["grid"], False)
    movement.refresh_vision(game)
    return game


def load_game(data, name):
    """Team-written. [Owner: Yassin] receives the loaded data and a save name (without .sav); returns the saved game, or None if the file is missing or damaged.

    Called by: frodo_game.open_game
    Uses: read_save, build_game
    Decides: if records is None; if len(game["heroes"]) == 0 or len(game["grid"]) == 0
    Why: Returns None if the file is missing or any line is damaged (try/except KeyError, ValueError,
        IndexError, TypeError), so a bad save never crashes the game.
    """
    records = read_save(name)
    if records is None:
        return None
    try:
        game = build_game(data, records)
    except (KeyError, ValueError, IndexError, TypeError):
        return None
    if len(game["heroes"]) == 0 or len(game["grid"]) == 0:
        return None
    return game


# ================================================================ listing saves

def list_saves():
    """Team-written. [Owner: Yassin] receives nothing; returns the names of the .sav files in this folder, newest first.

    Called by: ui.load_screen
    Decides: if file_name.endswith(".sav")
    Loops: for file_name in os.listdir("."); for index in range(len(found) - 1, -1, -1)
    """
    found = []
    try:
        for file_name in os.listdir("."):
            if file_name.endswith(".sav"):
                found.append([os.path.getmtime(file_name), file_name[:-4]])
    except OSError:
        return []
    found.sort()
    names = []
    for index in range(len(found) - 1, -1, -1):
        names.append(found[index][1])
    return names


def save_summary(name):
    """Team-written. [Owner: Yassin] receives a save name; returns a short line about it, like "round 12 - Kennel - 4 of 12 chambers" ("" if it cannot be read).

    Called by: ui.load_screen
    Uses: read_save, game_data.parse_fields, party_names
    Decides: if records is None; if item[0] == "GAME"
    Loops: for item in records
    """
    records = read_save(name)
    if records is None:
        return ""
    for item in records:
        if item[0] == "GAME":
            fields = game_data.parse_fields(item[2])
            return (str(fields["difficulty"]) + "  -  round " + str(fields["round"]) + "  -  " + str(fields["room_name"]) + "  -  "
                    + str(fields["depth"]) + " of " + str(fields["chambers"]) + " chambers  -  "
                    + ", ".join(party_names(records)))
    return ""
