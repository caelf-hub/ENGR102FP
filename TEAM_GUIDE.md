# Team guide - where to change things

Run the game with `python frodo_game.py`. Run the tests with `python test_frodo.py`.

## The files

| File | What it does |
|---|---|
| `frodo_game.py` | Entry point. `main()` has the round-by-round `while` loop. `play_round()` is one round. |
| `dungeon_data.txt` | All the numbers and content: heroes, cards, enemy units, items, rooms, settings. |
| `game_data.py` | Reads `dungeon_data.txt` and builds the starting `game` dictionary. |
| `combat.py` | Modifier deck, damage maths, turn order. |
| `cards.py` | The 3-card hand: playing a card, drawing a new one, reshuffling the discard pile; elements, loot. |
| `spears_ai.py` | Spears: generating and furnishing each chamber, adapting to the party, unit phases, morale, Doom, preparing chambers ahead. |
| `savegame.py` | Writes the game to a `.sav` file in our own plain-text format and reads it back. |
| `chambers.py` | Plans the dungeon (main path, side chambers, boss block) and carves chamber shapes, doors and corridors. |
| `movement.py` | Tiles, reachable tiles, pathing, fog of war (`refresh_vision`). |
| `logbook.py` | Combat log, `frodo_log.txt`, summary, win/lose check. |
| `ui.py` | The window: layout, panels, drag and drop, keyboard, typed boxes, screens. |
| `art.py` | The look: palette, textures, figures, tiles, icons, cards. |
| `scenery.py` | Paints the dungeon room: flagstones, puddles, 3D wall faces, shadows, the light map, torches. |
| `test_frodo.py` | Assert tests for the game rules. |

## Common changes

| I want to... | Change this |
|---|---|
| Make the game easier or harder | `dungeon_data.txt`: hero `hp`, unit `attack` / `wounds` / `models`, `doom_max` on the `SETTING` line |
| Change how many rooms there are | `rooms=` on the `SETTING` line |
| Add or edit a hero card | A `CARD` line in `dungeon_data.txt`: `action=kind:amount:range` (attack, heal, shield or move). Each hero has a deck of 8; any number works |
| Change how far or how early a hero acts | `move=` and `speed=` on the `HERO` line |
| Make the dungeon bigger or smaller | The `DUNGEON` line in `dungeon_data.txt`: `cell_cols` x `cell_rows` cells of `cell_width` x `cell_height` tiles, `main` chambers on the way to the boss, `sides` optional chambers |
| Change the boss arena | The `ARENA` rows at the bottom of `dungeon_data.txt` (16 wide, 14 tall; `W` Warlord, `G` guards, `Y` throne, `B` brazier) |
| Change the boss fight | `boss_check()`, `summon_guards()` and `enrage()` at the bottom of `spears_ai.py`, and the `Warlord` UNIT line |
| Change healing between chambers | `BREATHER_HEAL` and `RECOVER` at the top of `frodo_game.py` |
| Change zoom limits or pan speed | `MIN_ZOOM_LIMIT`, `MAX_ZOOM` and `glide_camera()` in `ui.py` |
| Add a kind of room | A `STYLE` line in `dungeon_data.txt` (shape, pillars, chests, traps, cover, shrines, and which habit it counters) |
| Add a new room shape | A `shape_...` function in `chambers.py`, then name it in `shape_tiles()` |
| Add an enemy unit type | A `UNIT` line, then name it in `unit_plan()` in `spears_ai.py`. Reuse a `look=` or paint a new one in `art.py` |
| Add an item | An `ITEM` line. New effect kinds go in `apply_item()` in `cards.py` |
| Add a hero | A `HERO` line plus 8 `CARD` lines. A new `kind=` also needs a `paint_...` function and a `CLASS_COLORS` entry in `art.py` |
| Change how many cards a hero holds | `HAND_SIZE` at the top of `cards.py` (the bottom strip fits 3; a bigger hand needs a smaller `card_rect()` in `ui.py`) |
| Change how far heroes see | `SIGHT` at the top of `movement.py` |
| Change how Spears adapts | `spears_counter()`, `unit_plan()` and `adapt_grid()` in `spears_ai.py` |
| Change a color | The palette at the top of `art.py` |
| Change the dungeon's look (wall height, stone colors, darkness) | The numbers at the top of `scenery.py` (`RISE`, `FLOOR_STONE`, `FACE_STONE`, `DARK_LIGHT`) |
| Make the room brighter or dimmer | `light_color()` in `scenery.py` |
| Change where a panel sits | The layout numbers and `..._rect()` functions at the top of `ui.py` |
| Change the rules text | The `RULES` list near the bottom of `ui.py` |

## How the pieces talk to each other

- Everything about the current game lives in one dictionary called `game` (made in `new_game()` in `game_data.py`).
- Game logic never draws. It adds sentences with `logbook.say()` and asks for effects by appending to `game["fx"]`.
- On a hero's turn `frodo_game.hero_turn()` loops: `ui.get_hero_action()` waits for the player and returns one request (`move`, `card`, `menu` or `end`), and `do_request()` carries it out. The turn ends on `end`.
- A hero has `moves_left` (from `move=`) and may play one card (`acted`). `movement.move_targets()` gives the tiles they can walk to with step counts; `movement.action_targets()` gives where a card can be dropped.
- The dungeon is one map. `spears_ai.build_dungeon()` plans it (`game["plan"]`) and carves the boss arena at the start; `spears_ai.generate_room()` carves each other chamber only when its door is opened. Every door is recorded in `game["doors"]` as `{tile, from, to}`. Door letters: `D` sealed, `E` unsealed, `d` opened.
- Every enemy unit remembers its chamber (`unit["chamber"]`). When the last one dies, `check_room_clear()` unseals that chamber's doors.
- The camera: `ui.UI["cam"]` is the map point in the middle of the window and `ui.UI["zoom"]` the zoom. `tile_rect()` and `tile_at()` convert between tiles and the screen, so zoom works everywhere.
- Fog of war: `game["seen"]` is what heroes can see right now, `game["known"]` is what the party remembers.
  Things Spears does where nobody can see go to the file log with `logbook.note()`, not to the screen.

## Before handing in

- Fill in the header line at the top of `frodo_game.py`.
- Every function is tagged `AI-assisted`. Change a tag to `Team-written` only for functions your team wrote or rewrote.
- Line numbers in `REQUIREMENTS_CHECK.md` shift when the code changes. Recheck them after your edits.

## Saves, Spears and enemy turns

- `savegame.save_game(game, name)` writes `name.sav`; `savegame.load_game(data, name)` reads it back (None if it is broken). If you add a new value to the `game` dictionary that must survive a save, add it to `game_line()` and `load_game_line()` in `savegame.py`.
- The game autosaves to `autosave.sav` in `frodo_game.enter_room()`.
- Spears never edits the chamber the party is in. `spears_ai.reinforce()` adds "trap", "guard" or "trapped chest" to a chamber's `prepared` list, and `apply_preparations()` places them when that chamber is opened.
- Enemy moves are recorded in `game["moves"]` and attacks as `strike` effects in `game["fx"]`; `ui.play_moves()` and `ui.wait_effects()` animate them, and `ui.caption()` shows what the unit is doing.
- Tips: `ui.situation_tip()` picks the tip under the map; the quick-start card is `ui.draw_quickstart()`.
