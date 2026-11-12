"""logbook.py - the combat log, frodo_log.txt, the end summary and the win/lose check."""


def say(game, text):
    """receives the game and a sentence; adds it to the on-screen log and this round's file log; returns the sentence."""
    game["log"].append(text)
    game["round_log"].append(text)
    return text


def note(game, text):
    """receives the game and a sentence the party cannot see happening; writes it only to the file log; returns the sentence."""
    game["round_log"].append(text)
    return text


def tell(game, visible, text):
    """receives the game, whether the party can see the event, and a sentence; shows it on screen only if visible, but always logs it to the file; returns the sentence."""
    if visible:
        return say(game, text)
    return note(game, text + " (unseen)")


def add_float(game, tile, text, color):
    """receives the game, a tile, some text and a color name; asks the screen to float that text over the tile."""
    game["fx"].append({"kind": "float", "tile": [tile[0], tile[1]], "text": text, "color": color})
    return text


def add_banner(game, text):
    """receives the game and a sentence; asks the screen to show it as a Spears banner; returns the sentence."""
    game["fx"].append({"kind": "banner", "text": text})
    return text


def start_log(party):
    """receives the list of hero names; starts a fresh frodo_log.txt and returns True if the file could be written."""
    try:
        log_file = open("frodo_log.txt", "w")
        log_file.write("FRODO AND THE DUNGEON LORD - adventure log\n")
        log_file.write("Party: " + ", ".join(party) + "\n")
        log_file.close()
        return True
    except OSError:
        return False


def write_log(lines, round_number):
    """receives this round's sentences and the round number; appends them to frodo_log.txt and returns how many lines were written."""
    written = 0
    try:
        log_file = open("frodo_log.txt", "a")
        log_file.write("\n--- Round " + str(round_number) + " ---\n")
        for line in lines:
            log_file.write(line + "\n")
            written += 1
        log_file.close()
    except OSError:
        written = 0
    return written


def write_summary(stats):
    """receives the stats dictionary; works out the averages, appends the summary to frodo_log.txt and returns the summary dictionary."""
    summary = dict(stats)
    try:
        summary["average_dealt"] = round(stats["damage_dealt"] / stats["rounds"], 1)
        summary["average_taken"] = round(stats["damage_taken"] / stats["rounds"], 1)
    except ZeroDivisionError:
        summary["average_dealt"] = 0
        summary["average_taken"] = 0
    try:
        log_file = open("frodo_log.txt", "a")
        log_file.write("\n=== SUMMARY ===\n")
        for line in summary_lines(summary):
            log_file.write(line + "\n")
        log_file.close()
    except OSError:
        summary["saved"] = False
    return summary


def summary_lines(summary):
    """receives the summary dictionary; returns the list of sentences shown at the end and written to the log."""
    lines = []
    lines.append("Rounds played: " + str(summary["rounds"]))
    lines.append("Rooms cleared: " + str(summary["rooms_cleared"]))
    lines.append("Damage dealt: " + str(summary["damage_dealt"]))
    lines.append("Damage taken: " + str(summary["damage_taken"]))
    lines.append("Average damage dealt per round: " + str(summary["average_dealt"]))
    lines.append("Average damage taken per round: " + str(summary["average_taken"]))
    lines.append("Enemy models slain: " + str(summary["enemies_slain"]))
    lines.append("Cards played: " + str(summary["cards_played"]))
    lines.append("Loot found: " + str(summary["loot_found"]))
    return lines


def check_game_over(heroes, doom, doom_max, warlord_dead):
    """receives the heroes, the Doom Track, its end and whether the Warlord is dead; returns "win", "lose" or "" (keep playing)."""
    if warlord_dead:
        return "win"
    elif doom >= doom_max:
        return "lose"
    for hero in heroes:
        if not hero["exhausted"]:
            break
    else:
        return "lose"
    return ""


def status_lines(game):
    """receives the game; returns a list of sentences describing the party, the room and the Doom Track."""
    lines = []
    lines.append("Round " + str(game["round"]) + " - in " + game["room_name"] + " ("
                 + str(game["depth"]) + " of " + str(len(game["plan"])) + " chambers explored)")
    lines.append("Doom Track: " + str(game["doom"]) + " of " + str(game["doom_max"]))
    for hero in game["heroes"]:
        lines.append(hero_line(hero))
    lines.append("Enemy units here: " + str(len(game["units"])))
    return lines


def hero_line(hero):
    """receives a hero; returns one sentence with the hero's hp, cards and items."""
    line = hero["name"] + ": HP " + str(hero["hp"]) + "/" + str(hero["max_hp"])
    line += ", move " + str(hero["move"]) + ", deck " + str(len(hero["deck"])) + ", discard "
    line += str(len(hero["discard"]))
    if hero["exhausted"]:
        line += " (EXHAUSTED)"
    if len(hero["items"]) > 0:
        line += " - items: " + ", ".join(hero["items"])
    return line

