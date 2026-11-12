"""game_data.py - reads dungeon_data.txt and builds the starting game state."""
import random

import cards
import combat


def clean_value(text):
    """receives one value from the data file; returns an int if it is a number, otherwise the text with _ turned into spaces."""
    try:
        return int(text)
    except ValueError:
        return text.replace("_", " ")


def parse_fields(text):
    """receives text like "move=3 role=melee"; returns a dictionary such as {"move": 3, "role": "melee"}."""
    fields = {}
    for pair in text.split():
        pieces = pair.split("=")
        if len(pieces) == 2:
            fields[pieces[0]] = clean_value(pieces[1])
    return fields


def parse_action(text):
    """receives text like "attack:3:1"; returns an action dictionary with kind, amount and range."""
    pieces = str(text).split(":")
    action = {"kind": pieces[0], "amount": 0, "range": 1}
    try:
        action["amount"] = int(pieces[1])
        action["range"] = int(pieces[2])
    except (ValueError, IndexError):
        pass
    return action


def make_card(owner, fields):
    """receives the hero name and the fields of a CARD line; returns a card dictionary with its one action."""
    card = {"name": fields["name"], "owner": owner}
    card["action"] = parse_action(fields["action"])
    card["element"] = fields["element"]
    return card


def store_record(data, kind, name, fields):
    """receives the data so far, a record kind, its name and its fields; stores it in the right place and returns the kind."""
    if kind == "CARD":
        if name in data["cards"]:
            data["cards"][name].append(make_card(name, fields))
        return kind
    fields["name"] = name
    if kind == "UNIT":
        data["units"][name] = fields
    elif kind == "HERO":
        data["heroes"][name] = fields
        data["cards"][name] = []
    elif kind == "ITEM":
        data["items"].append(fields)
    elif kind == "SETTING":
        data["settings"] = fields
    elif kind == "DUNGEON":
        data["dungeon"] = fields
    elif kind == "STYLE":
        data["styles"].append(fields)
    return kind


def read_line(data, line):
    """receives the data so far and one line of the file; stores the line if it is a record and returns True if it was one."""
    if line == "" or line.startswith("#"):
        return False
    parts = line.split("|")
    if len(parts) < 3:
        return False
    if parts[0].strip() == "ARENA":
        data["arena"].append(parts[2].strip())
        return True
    try:
        store_record(data, parts[0].strip(), parts[1].strip(), parse_fields(parts[2]))
    except (KeyError, ValueError):
        return False
    return True


def load_dungeon(filename):
    """receives the data file name; returns a dictionary of units, styles, the dungeon plan settings, the arena drawing, cards, items, heroes and settings, or None if the file cannot be opened."""
    data = {"units": {}, "styles": [], "dungeon": {}, "arena": [], "cards": {}, "items": [], "heroes": {},
            "settings": {}}
    try:
        data_file = open(filename, "r")
    except OSError:
        return None
    for line in data_file:
        read_line(data, line.strip())
    data_file.close()
    return data


def make_hero(data, name):
    """receives the loaded data and a hero name; returns a fresh hero dictionary with a full hand of cards."""
    info = data["heroes"][name]
    hero = {"name": name, "kind": info["kind"], "title": info["title"], "blurb": info["blurb"]}
    hero["hp"] = info["hp"]
    hero["max_hp"] = info["hp"]
    hero["pos"] = [1, 1]
    hero["deck"] = []
    for card in data["cards"][name]:
        hero["deck"].append(card)
    random.shuffle(hero["deck"])
    hero.update({"hand": [], "discard": [], "items": [], "init": 99, "shield": 0, "armor": 0})
    hero.update({"attack_bonus": 0, "bonus_move": 0, "resting": False, "exhausted": False})
    hero.update({"move": info["move"], "speed": info["speed"], "moves_left": 0, "acted": False})
    cards.refill_hand(hero)
    return hero


def new_memory():
    """receives nothing; returns Spears's memory dictionary with every count at 0."""
    return {"melee_hits": 0, "ranged_hits": 0, "chests_opened": 0, "tiles_moved": 0,
            "clumped": 0}


def new_stats():
    """receives nothing; returns the stats dictionary used for the end summary, all at 0."""
    return {"rounds": 0, "damage_dealt": 0, "damage_taken": 0, "cards_played": 0,
            "loot_found": 0, "rooms_cleared": 0, "enemies_slain": 0}


def new_game(data, party):
    """receives the loaded data and the list of chosen hero names; returns the whole starting game dictionary."""
    settings = data["settings"]
    game = {"running": True, "data": data, "heroes": [], "units": [], "inventory": []}
    for name in party:
        game["heroes"].append(make_hero(data, name))
    game.update({"grid": [], "seen": [], "known": [], "spawns": [], "door": None, "room_name": ""})
    game.update({"depth": 0, "plan": [], "doors": [], "chamber": 0, "boss_door": None, "rarity": 1})
    game.update({"doom": 0, "doom_max": settings["doom_max"], "warlord_dead": False})
    game.update({"memory": new_memory(), "stats": new_stats(), "counter": "none"})
    game.update({"elements": {"fire": 0, "frost": 0, "light": 0}})
    game.update({"hero_deck": combat.build_modifier_deck(), "hero_discard": []})
    game.update({"enemy_deck": combat.build_modifier_deck(), "enemy_discard": []})
    game.update({"log": [], "round_log": [], "fx": [], "order": [], "turn_name": ""})
    game.update({"round": 0, "unit_count": 0, "room_units": 0})
    game.update({"seed": 0, "boss_phase": 0, "moves": [], "owners": []})
    return game


def find_hero(game, name):
    """receives the game and a hero name; returns that hero's dictionary, or None."""
    for hero in game["heroes"]:
        if hero["name"] == name:
            return hero
    return None


def place_party(game, starts):
    """receives the game and the room's start tiles; stands each living hero on one and returns how many were placed."""
    placed = 0
    for hero in game["heroes"]:
        if not hero["exhausted"] and placed < len(starts):
            hero["pos"] = [starts[placed][0], starts[placed][1]]
            placed += 1
    return placed
