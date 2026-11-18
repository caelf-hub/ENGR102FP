# Frodo and the Dungeon Lord

A turn-based dungeon crawler in Python and pygame, made for our intro-programming final (Mini-Project 6).

You are Frodo, a small white Maltese in a knight's helmet, leading 2 or 3 companions through a dungeon of
about 12 chambers that is different every game. Spears, the Dungeon Lord, is played by the computer: he
builds every new chamber to counter the way you play.

- **Win:** reach the Throne of Spears (the red-skull door) and destroy his Warlord.
- **Lose:** every hero falls, or the Doom Track (the crimson bar, top right) fills up.

---

## Contents

1. [Run it](#1-run-it)
2. [Play it in two minutes](#2-play-it-in-two-minutes)
3. [For teammates: how the code fits together](#3-for-teammates-how-the-code-fits-together)
4. [Who owns what](#4-who-owns-what)
5. [Function tags and academic honesty](#5-function-tags-and-academic-honesty)
6. [How to explain any function to a grader](#6-how-to-explain-any-function-to-a-grader)
7. [The data file](#7-the-data-file)
8. [Saves](#8-saves)
9. [Tests](#9-tests)
10. [Before we hand in](#10-before-we-hand-in)
11. [Files](#11-files)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Run it

Open a terminal **in this folder** (the one with `frodo_game.py`). The game opens its files by name, so
always run it from here.

Check Python (3.10 or newer):

```bash
python --version
```

Install pygame (once):

```bash
python -m pip install pygame
```

Play:

```bash
python frodo_game.py
```

Run the tests (should end with `All 8 test groups passed.`):

```bash
python test_frodo.py
```

On Windows, if `python` is not found, use `py`. On Mac or Linux, use `python3`.

---

## 2. Play it in two minutes

The game teaches itself: a **Quick Start card** opens with every new game, gold **hint bubbles** point at
what to try during the first round, a **TIP strip** under the map gives advice for what is happening, and
hovering over almost anything shows a tooltip. The full rules are behind **Rules** (or `F1`).

**Starting:** *New Game* -> add at least 2 companions to Frodo -> pick **Easy**, **Normal** or **Hard**
-> *Begin*. *Continue* loads a saved game.

**A hero's turn** (heroes and enemies take turns in the order shown at the top left):

1. **Walk** - reachable tiles glow blue with their step count. Click one, or drag the hero onto it.
2. **Play one card** - each hero holds 3 cards. Drag one onto a glowing target: an enemy (attack), a hero
   (heal), or the hero itself (shield or dash). A new card is drawn straight away.
3. **End turn** - click *End turn* or press `E`.

**The dungeon:** you only see chambers you have opened. Defeat every enemy in a chamber and its doors
glow as EXITs; walk onto one to open the next chamber. Side doors lead to optional chambers with extra
loot (but every round raises Doom). Spears never changes the chamber you are in, but between rounds he may
secretly add a trap, trapped chest or guard to a chamber ahead. Enemies walk, strike and shoot on screen
with a caption saying what they do; hold `Space` to speed them up.

**Controls**

| Action | Mouse | Keyboard |
|---|---|---|
| Walk | click a blue tile, or drag the hero | arrows + `Enter`, or `M` then type a number and an arrow |
| Play a card | drag it onto a glowing target (or click card, then target) | `1`-`3`, arrows + `Enter`, `Esc` cancels |
| End turn | *End turn* | `E` |
| Menu | buttons, bottom right | `F1` Rules, `F2` Status, `F3` Save, `F9` Quit |
| Zoom / pan the map | wheel / right-drag | `+` `-` / `W` `A` `S` `D`, `Home` = whole map |
| Speed up enemy turns | | hold `Space` |
| Pop-up questions | Yes / No | `Y` / `N` |
| Full screen | | `F11` |

---

## 3. For teammates: how the code fits together

Everything about one game lives in **one dictionary called `game`** (built by `game_data.new_game()`).
Heroes, enemy units, chambers and cards are dictionaries inside it; the map is a list of lists of letters.
There are no classes.

**The call flow, from the top:**

```
frodo_game.main()                       <- the ONE round-by-round while loop
  choose_game()  ->  ui.title_flow()     title, party select, difficulty, Continue
  open_game()    ->  start_dungeon()     spears_ai.build_dungeon() plans the map, enter_room(0)
  while game is running and nobody has won or lost:
      play_round()
          start_round(), prepare_heroes()          roll turn order
          for each entry in turn order: take_turn()
              hero  -> hero_turn()                 loops ui.get_hero_action() -> do_request()
                         do_request(): move -> hero_move()      card -> play_card()
              enemy -> spears_phase()              move, shoot / charge + fight, morale
          end_round()                              shields reset, Spears prepares, Doom +1, log
      logbook.check_game_over()
  finish_game()  ->  ui.end_screen()   Play again or Quit
```

**The golden rules of the code**

- **Logic never draws.** Game files change the `game` dictionary and add sentences with `logbook.say()`.
  When something should appear on screen they add an effect to `game["fx"]` (a float, strike, puff,
  sparkle, shake, banner). `ui.py` turns those into animation.
- **`ui.py` waits for the player and returns what they chose** (for example `ui.get_hero_action()` returns
  `{"type": "move", "tile": [5, 3]}`); the game files then carry it out.
- **Map letters:** `#` rock, `.` floor, `D` sealed door, `E` unsealed EXIT, `d` open doorway, `C` chest,
  `X` trapped chest, `T` trap, `H` hidden pit, `P` shrine, `~` cover, `Y` throne, `B` brazier.
- **Tiles** are `[col, row]`, and the letter at a tile is `game["grid"][row][col]`.

[`docs/TEAM_GUIDE.md`](docs/TEAM_GUIDE.md) is the cookbook: "I want to change X, edit Y".

---

## 4. Who owns what

Every game-logic function names its owner at the start of its docstring, like this:

```python
def calc_damage(base, modifier, shield):
    """[Owner: Mahad] receives the base attack, the modifier card and the target's shield; returns the damage dealt (never below 0)."""
```

The owner is the person who must be able to **explain** that function to a grader, and who may rewrite it.
**[`docs/OWNERS.md`](docs/OWNERS.md) lists every function, its owner and what it does.**

| Owner | Area | Files | Functions |
|---|---|---|---|
| **Team** | The core loop and the tests - everyone should know these | `frodo_game.py`: `main`, `choose_game`, `open_game`, `play_round`, `take_turn`, `hero_turn`, `do_request`, `finish_game`; all of `test_frodo.py` | 20 |
| **Cael** | Heroes, cards and the turn | rest of `frodo_game.py`, `cards.py`, `game_data.py` | 52 |
| **Guilherme** | Spears and his armies | `spears_ai.py` | 57 |
| **Mahad** | The dungeon, combat maths and the log | `chambers.py`, `combat.py`, `logbook.py` | 53 |
| **Yassin** | Movement, fog of war and saving | `movement.py`, `savegame.py` | 58 |
| **AI (no owner)** | Art and interface: drawing, animation, drag and drop, screens | `ui.py`, `art.py`, `scenery.py` | 281 |

**Start here** - the functions each person should know best:

- **Team:** `main`, `play_round`, `take_turn`, `hero_turn`, `do_request` (`frodo_game.py`).
- **Cael:** `play_card`, `hero_move`, `hero_attack`, `step_on_tile`, `end_round` (`frodo_game.py`);
  `draw_card`, `finish_card` (`cards.py`); `load_dungeon`, `new_game` (`game_data.py`).
- **Guilherme:** `spears_counter`, `generate_room`, `reinforce`, `move_unit`, `unit_charge`, `unit_attack`,
  `unit_morale`, `morale_test`, `boss_check` (`spears_ai.py`).
- **Mahad:** `plan_dungeon`, `carve_chamber`, `pick_door`, `dig_corridor` (`chambers.py`);
  `draw_modifier`, `calc_damage`, `sort_turn_order` (`combat.py`); `check_game_over`, `write_summary`
  (`logbook.py`).
- **Yassin:** `step_map`, `reachable_tiles`, `find_path`, `refresh_vision` (`movement.py`);
  `save_game`, `save_lines`, `load_game`, `build_game` (`savegame.py`).

---

## 5. Function tags and academic honesty

The brief says every function's docstring must **start** with its tag: `Team-written:` or `AI-assisted:`.

- **Interface and art** (`ui.py`, `art.py`, `scenery.py`) start with `AI-assisted:`.
- **Game logic** currently starts with `[Owner: name]`, with no tag in front.
- Every function in the project was written with the AI assistant. A function's tag should only become
  `Team-written:` once its owner has rewritten it themselves (their own logic, their own words) and
  `python test_frodo.py` still passes.
- [`docs/REQUIREMENTS_CHECK.md`](docs/REQUIREMENTS_CHECK.md) shows, for each of the 12 requirements, the
  file, function and line that meets it, plus every function and its tag.

---

## 6. How to explain any function to a grader

Every docstring is written as **"receives ...; returns ..."** so you can read it out loud:

1. **What it receives** - the parameters, in plain words.
2. **What it does** - the middle of the docstring.
3. **What it returns** - the end of the docstring.
4. Then walk through the body: most functions are under 15 lines and do one job.
5. Know which function calls it (search the project for its name) and why.

Example - `combat.calc_damage(3, "x2", 1)`: receives a base attack of 3, the modifier card "x2" and a shield
of 1; "x2" doubles the attack to 6; the shield blocks 1; returns 5.

---

## 7. The data file

`dungeon_data.txt` holds all the game content and is read line by line with `split()` (never json):

```
KIND | name | key=value key=value ...
```

| Kind | What it sets |
|---|---|
| `SETTING` | Doom Track length |
| `DIFFICULTY` | Easy / Normal / Hard: extra hero HP, extra Doom steps, enemy damage |
| `HERO` | each hero's HP, move (tiles per turn), speed (turn order) |
| `CARD` | each hero's 8 cards: `action=kind:amount:range`, `element=` |
| `UNIT` | enemy unit types: models, move, attack, toughness, wounds, leadership, role, range |
| `ITEM` | loot and its effect |
| `DUNGEON` | map size in cells, main chambers to the boss, side chambers |
| `STYLE` | chamber styles: shape, pillars, chests, traps, cover, shrines, which habit they counter |
| `ARENA` | the hand-drawn boss throne room (16 x 14) |

Easiest balance knobs: hero `hp`, unit `attack` / `wounds`, `doom_max`, the `DIFFICULTY` lines.

---

## 8. Saves

- The game saves itself to `autosave.sav` every time a door opens.
- `F3` asks for a name (one of the typed input boxes the brief asks for) and writes `<name>.sav`.
- *Continue* on the title screen lists the saves, newest first. A loaded game restarts the round it was
  saved in.
- `.sav` files are plain text in the same `KIND | name | key=value` style as the data file
  (`savegame.py`). They are ignored by git.

---

## 9. Tests

`python test_frodo.py` runs 8 groups of `assert` tests: loading the data, combat maths, the 3-card hand,
Spears and the dungeon generator, Spears only preparing chambers ahead, save and load, movement and fog
of war, and the log / win-lose check. Run it after every change.

---

## 10. Before we hand in

- [ ] Fill in the header line at the top of `frodo_game.py` (team, members, section).
- [ ] Every docstring starts with the tag the brief asks for (`Team-written:` or `AI-assisted:`).
- [ ] Each owner can explain their functions (see section 6).
- [ ] Tags are honest: `Team-written:` only on functions we actually rewrote.
- [ ] `python test_frodo.py` passes.
- [ ] Play one full game on Easy from the title screen to the end screen.

---

## 11. Files

| File | What it is |
|---|---|
| `frodo_game.py` | **Run this.** `main()` and the round-by-round loop, hero actions, the enemy phase. |
| `dungeon_data.txt` | All game content (heroes, cards, units, items, dungeon, styles, arena, difficulty). |
| `game_data.py` | Reads `dungeon_data.txt`; builds a new `game` dictionary. |
| `cards.py` | The 3-card hand, drawing and reshuffling, elements, loot. |
| `combat.py` | Attack modifier deck, damage, turn order. |
| `spears_ai.py` | Spears: building chambers, adapting, enemy phases, morale, the boss, Doom. |
| `chambers.py` | Plans the dungeon and carves chamber shapes, doors and corridors. |
| `movement.py` | Tiles, walking, pathing, fog of war. |
| `logbook.py` | Combat log, `frodo_log.txt`, end summary, win / lose check. |
| `savegame.py` | Saving and loading `.sav` files. |
| `ui.py` | The window: camera, drag and drop, turns, tooltips, tips, screens, animation. |
| `art.py` | Colours, fonts, figures, icons, cards, panels (all drawn in code). |
| `scenery.py` | Paints the dungeon: floor, walls, shadows, light. |
| `test_frodo.py` | The tests. |
| `docs/OWNERS.md` | Every function, its owner and what it does. |
| `docs/TEAM_GUIDE.md` | Where to change things. |
| `docs/REQUIREMENTS_CHECK.md` | Where each project requirement is met. |
| `LICENSE` | The project's licence. |

The code, `dungeon_data.txt`, `frodo_log.txt` and the `.sav` files all stay in the top folder next to
`frodo_game.py`: the brief requires every file the game opens to be in that folder, opened by name only.
Only documentation lives in `docs/`.

Made while playing: `frodo_log.txt` (each round, plus a summary) and `.sav` save files.

---

## 12. Troubleshooting

| Problem | Fix |
|---|---|
| `Run: pip install pygame` | Run `python -m pip install pygame`. |
| `Could not open dungeon_data.txt` | Run the game from inside this folder. |
| `python` is not recognised | Use `py` (Windows) or `python3` (Mac / Linux). |
| Window too big or small | `F11` for full screen, or resize; the game scales to fit. |
| Map too dark | Raise `DARK_LIGHT` at the top of `scenery.py`. |
| A save will not load | It may be from an older version of the game; start a new game. |

All art is drawn in code - no downloaded images, sounds or fonts. The rules are inspired by card-driven
dungeon crawlers and tabletop wargames, written in our own words.
