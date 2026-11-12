# Frodo and the Dungeon Lord

A turn-based dungeon crawler written in Python with pygame.

You are Frodo, a small white Maltese in a knight's helmet, and you lead a party of up to four
heroes through a dungeon of about 12 chambers that is different every game. Spears, the Dungeon
Lord, is played by the computer. He digs each new chamber to counter the way you have been
playing, and he acts in the dark where you cannot see him.

- **Win:** reach the Throne of Spears and destroy his Warlord.
- **Lose:** every hero is exhausted, or the Doom Track (the crimson bar, top right) fills up.

## What you need

- Python 3.10 or newer (built and tested on Python 3.12, Windows 11)
- pygame 2

## Commands

Open a terminal in this folder (the one that contains `frodo_game.py`). Run every command from
here, because the game opens its files by name.

**1. Check Python is installed**

```bash
python --version
```

**2. Install pygame (once)**

```bash
python -m pip install pygame
```

**3. Run the game**

```bash
python frodo_game.py
```

**4. Run the tests (optional)**

```bash
python test_frodo.py
```

It should end with `All 6 test groups passed.`

If `python` is not found on Windows, use `py` instead (`py frodo_game.py`). On Mac or Linux use
`python3` and `python3 -m pip install pygame`.

## How to play, in one minute

The full rules are in the game: choose **Rules** on the title screen, or press `F1` any time.

Heroes and enemies take turns in the order shown at the top left. On a hero's turn:

1. **Walk** - the tiles the hero can reach glow blue, each with its step count. Click one (or drag
   the hero onto it) and the hero walks there tile by tile. Left-over moves can be used later in
   the same turn.
2. **Play one card** - the hero holds 3 cards (bottom of the screen). Each card is one action.
   Drag one onto a glowing enemy to attack, onto a glowing hero to heal, or onto the hero itself
   for a shield or a dash. (Or click the card, then click the target.) A new card is drawn
   straight away.
3. **End turn** - click *End turn* (or press `E`).

Everything you can do glows; a bad drop snaps back and says why. A quick-start card opens with
every new game, gold bubbles point at what to try during the first round, and a TIP strip under
the map gives advice for what is happening.

**Starting a game:** choose *New Game*, then add at least 2 companions to Frodo's party (up to 3).
*Continue* loads a saved game.

### The dungeon

- You only see chambers you have opened. Inside them you see the room's shape and grid, but
  enemies and objects only near your heroes (walls block the view).
- A chamber's doors stay sealed until every enemy in it is destroyed. Then they glow as exits:
  walk a hero onto one and the chamber behind it is dug out and revealed, joined by a corridor.
- Most chambers lead on along the main path. Some also have a side door to an optional chamber
  with extra loot, which costs rounds (and every round raises Doom).
- The door to the boss arena, the Throne of Spears, wears a red skull. At half health the Warlord
  summons his guard; near death he becomes enraged.
- Spears never changes the chamber you are in, but between rounds he may secretly prepare a
  chamber ahead with an extra trap, trapped chest or guard.
- Enemies walk, strike and shoot on screen, with a caption saying what each one does.
- Stand on a chest or shrine to loot it. Every time a door opens, the party heals a little.

### Controls

| Action | Mouse | Keyboard |
|---|---|---|
| Walk | click a blue tile, or drag the hero onto it | arrows + `Enter`, or `M`, type a number, then an arrow key |
| Play a card | drag it onto a glowing target, or click it then the target | `1`-`3`, then arrows + `Enter`; `Esc` puts it back |
| End turn | *End turn* button | `E` |
| Menu | buttons at the bottom right | `F1` Rules, `F2` Status, `F3` Save, `F9` Quit |
| Speed up enemy turns | | hold `Space` |
| Pop-up question | click Yes / No | `Y` / `N` |
| Zoom the map | mouse wheel over the map | `+` / `-` |
| Pan the map | hold the right button and drag | `W` `A` `S` `D` |
| See the whole dungeon | | `Home` |
| Scroll the combat log | mouse wheel over the log | |
| Full screen | | `F11` |

Hover the mouse over any hero, enemy or object on the map to see its details.

## Files

| File | What it is |
|---|---|
| `frodo_game.py` | **Run this.** The main loop that plays the game round by round. |
| `dungeon_data.txt` | All game content: heroes, cards, enemy units, items, the dungeon plan, room styles, the boss arena. Plain text, easy to edit. |
| `game_data.py` | Reads `dungeon_data.txt` and sets up a new game. |
| `cards.py` | Hero cards: the 3-card hand, drawing, discard, elements, loot. |
| `combat.py` | Attack modifier deck, damage, turn order. |
| `spears_ai.py` | Spears: generating each chamber, adapting to the party, enemy units, morale, the boss, Doom. |
| `chambers.py` | Plans the dungeon and carves the random chamber shapes, doors and corridors. |
| `movement.py` | Tiles, walking, pathing, fog of war. |
| `logbook.py` | Combat log, `frodo_log.txt`, end summary, win/lose check. |
| `savegame.py` | Saves the whole game to a `.sav` file and loads it back. |
| `ui.py` | The window: layout, camera, drag and drop, keyboard, hints, screens. |
| `art.py` | Colours, figures, icons, cards, panels. |
| `scenery.py` | Paints the dungeon: floor, walls, shadows, light. |
| `test_frodo.py` | Tests for the game rules. |
| `TEAM_GUIDE.md` | Where to change things in the code. |
| `REQUIREMENTS_CHECK.md` | Where each project requirement is met in the code. |

Files the game creates while you play:

- `frodo_log.txt` - every round's actions, plus a summary at the end. It is overwritten each new game.
- `autosave.sav` - the game saves itself here every time a chamber door opens.
- `<name>.sav` - a saved game, written when you choose *Save* (`F3`) and type a name.

To load a save, choose **Continue** on the title screen and click it.

## Changing the game

Most changes need no code. Open `dungeon_data.txt` and edit a line:

- Easier or harder: hero `hp`, unit `attack` / `wounds` / `models`, or `doom_max`.
- Bigger or smaller dungeon: the `DUNGEON` line (`main` chambers to the boss, `sides` optional ones).
- New cards, items, units or room styles: copy an existing line and change it.
- The boss arena: the `ARENA` rows at the bottom of the file.

`TEAM_GUIDE.md` lists where everything else lives.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Run: pip install pygame` | pygame is missing. Run `python -m pip install pygame`. |
| `Could not open dungeon_data.txt` | Run the command from inside this folder, and keep all the files together. |
| `python` is not recognised | Use `py` (Windows) or `python3` (Mac / Linux). |
| The window is too big or too small | Press `F11` for full screen, or resize the window; the game scales to fit. |
| The map is too dark | Raise `DARK_LIGHT` at the top of `scenery.py`. |

## Credits

All art is drawn in code. No images, sounds or fonts are downloaded. The rules are inspired by
card-driven dungeon crawlers and tabletop wargames, written in our own words.
