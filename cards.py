"""cards.py - hero cards: choosing, using halves, resting, exhaustion, elements, loot."""
import random

HAND_SIZE = 3


def find_card(pile, name):
    """receives a list of cards and a card name; returns that card, or None if it is not there."""
    for card in pile:
        if card["name"] == name:
            return card
    return None


def choose_card(hero, name):
    """receives a hero and a card name; takes that card out of the hand and returns it (None if it is not in the hand)."""
    card = find_card(hero["hand"], name)
    if card is not None:
        hero["hand"].remove(card)
    return card


def finish_card(hero, card):
    """receives a hero and the card they just played; puts it on the discard pile and draws a new card; returns how many cards are now in hand."""
    hero["discard"].append(card)
    return refill_hand(hero)


def draw_card(hero):
    """receives a hero; moves the top card of their deck into their hand (shuffling the discard pile back into the deck first if the deck is empty); returns the card drawn, or None."""
    if len(hero["deck"]) == 0:
        for card in hero["discard"]:
            hero["deck"].append(card)
        hero["discard"] = []
        random.shuffle(hero["deck"])
    if len(hero["deck"]) == 0:
        return None
    card = hero["deck"].pop()
    hero["hand"].append(card)
    return card


def refill_hand(hero):
    """receives a hero; draws cards until they hold HAND_SIZE (or run out); returns how many cards are in hand."""
    while len(hero["hand"]) < HAND_SIZE:
        if draw_card(hero) is None:
            break
    return len(hero["hand"])


def is_exhausted(hero):
    """receives a hero; returns True if the hero has no hp left."""
    return hero["hp"] <= 0


def heal_hero(hero, amount):
    """receives a hero and a heal amount; raises hp (not past max) and returns how much was healed."""
    before = hero["hp"]
    hero["hp"] = hero["hp"] + amount
    if hero["hp"] > hero["max_hp"]:
        hero["hp"] = hero["max_hp"]
    return hero["hp"] - before


def use_element(elements, name):
    """receives the elements dictionary and an element name; if it is glowing, uses it up and returns 1 (bonus), otherwise starts it glowing and returns 0."""
    if name not in elements:
        return 0
    if elements[name] > 0:
        elements[name] = 0
        return 1
    elements[name] = 2
    return 0


def wane_elements(elements):
    """receives the elements dictionary; lowers every glowing element by 1 and returns how many are still glowing."""
    glowing = 0
    for name in elements:
        if elements[name] > 0:
            elements[name] = elements[name] - 1
        if elements[name] > 0:
            glowing += 1
    return glowing


def search_poi(hero, items, max_rarity):
    """receives the searching hero, the item list and the best rarity allowed; adds a random item to the hero and returns it (None if nothing fits)."""
    choices = []
    for item in items:
        if item["rarity"] <= max_rarity:
            choices.append(item)
    if len(choices) == 0:
        return None
    item = random.choice(choices)
    hero["items"].append(item["name"])
    return item


def cheese_feast(game, amount):
    """receives the game and a heal amount; Frodo heals that much, everyone else heals 1; returns a message."""
    for hero in game["heroes"]:
        if hero["exhausted"]:
            continue
        elif hero["kind"] == "leader":
            heal_hero(hero, amount)
        else:
            heal_hero(hero, 1)
    return "Frodo shares the cheese. Everyone feels braver."


def apply_item(game, hero, item):
    """receives the game, a hero and an item; applies the item's effect and returns a message about it."""
    pieces = item["effect"].split(":")
    kind = pieces[0]
    amount = int(pieces[1])
    if kind == "heal":
        return hero["name"] + " heals " + str(heal_hero(hero, amount)) + "."
    elif kind == "attack":
        hero["attack_bonus"] += amount
        return hero["name"] + " gets +" + str(amount) + " attack."
    elif kind == "armor":
        hero["armor"] = 1
        return hero["name"] + " now blocks 1 damage from every hit."
    elif kind == "move":
        hero["move"] += amount
        return hero["name"] + " can now walk " + str(hero["move"]) + " tiles a turn."
    elif kind == "doom":
        game["doom"] = max(0, game["doom"] - amount)
        return "The Doom Track slips back " + str(amount) + "."
    else:
        return cheese_feast(game, amount)
