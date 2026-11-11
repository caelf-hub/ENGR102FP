"""combat.py - attack modifier decks, damage maths and turn order."""
import random


def build_modifier_deck():
    """receives nothing; returns a shuffled list of 20 attack modifier cards."""
    counts = {"+0": 6, "+1": 5, "-1": 5, "+2": 1, "-2": 1, "x2": 1, "null": 1}
    deck = []
    for name in counts:
        for copy in range(counts[name]):
            deck.append(name)
    random.shuffle(deck)
    return deck


def draw_modifier(deck, discard):
    """receives a modifier deck and its discard pile; returns the card drawn (like "+1", "x2" or "null")."""
    if len(deck) == 0:
        for card in discard:
            deck.append(card)
        discard.clear()
        random.shuffle(deck)
    if len(deck) == 0:
        return "+0"
    card = deck.pop(random.randrange(len(deck)))
    discard.append(card)
    return card


def calc_damage(base, modifier, shield):
    """receives the base attack, the modifier card and the target's shield; returns the damage dealt (never below 0)."""
    if modifier == "null":
        damage = 0
    elif modifier == "x2":
        damage = base * 2
    else:
        try:
            damage = base + int(modifier)
        except ValueError:
            damage = base
    damage = damage - shield
    if damage < 0:
        damage = 0
    return damage


def apply_damage(target, damage):
    """receives a hero or enemy model dictionary and a damage number; lowers its hp and returns the hp left."""
    target["hp"] = target["hp"] - damage
    if target["hp"] < 0:
        target["hp"] = 0
    return target["hp"]


def roll_attack(game, side, base, shield):
    """receives the game, "hero" or "enemy", the base attack and the shield; draws a modifier and returns [damage, modifier]."""
    if side == "hero":
        modifier = draw_modifier(game["hero_deck"], game["hero_discard"])
    else:
        modifier = draw_modifier(game["enemy_deck"], game["enemy_discard"])
    damage = calc_damage(base, modifier, shield)
    game["fx"].append({"kind": "mod", "text": modifier, "side": side})
    return [damage, modifier]


def sort_turn_order(heroes, units):
    """receives the heroes and enemy units; returns a list of [initiative, tie, kind, name] sorted lowest first."""
    order = []
    for hero in heroes:
        if not hero["exhausted"]:
            order.append([hero["init"], 0, "hero", hero["name"]])
    for unit in units:
        if len(unit["models"]) > 0:
            order.append([unit["init"], 1, "unit", unit["name"]])
    order.sort()
    return order
