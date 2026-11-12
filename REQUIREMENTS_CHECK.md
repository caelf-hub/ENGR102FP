# REQUIREMENTS_CHECK - Frodo and the Dungeon Lord

Line numbers were generated from the code. They shift if a file is edited.

## The 12 requirements

| # | Requirement | Where it is satisfied |
|---|---|---|
| 1 | One `while` loop runs the game round by round until win, lose or quit | `frodo_game.py` > `main()` line 484; the loop itself is at `frodo_game.py` line 494 |
| 2 | Menu each round with rules, status and quit | `frodo_game.py` > `use_menu()` line 248 (Rules, Status, Save and Quit are buttons and F-keys on every hero's turn, every round; handled from `frodo_game.py` > `do_request()` line 219); the buttons are set up in `ui.py` > `turn_buttons()` line 1552; `ui.py` > `show_rules()` line 2162; `ui.py` > `show_status()` line 2206 |
| 3 | `random` drives decks, rooms, Spears choices, charge and morale rolls, lost cards | modifier deck: `combat.py` line 25; room style: `spears_ai.py` line 82; dungeon plan: `chambers.py` line 99, `chambers.py` > `random_walk()` line 123; chamber size and shape: `chambers.py` > `shrink_box()` line 40; boss phases: `spears_ai.py` > `boss_check()` line 761; unit choice: `spears_ai.py` line 66; unit initiative: `spears_ai.py` > `pick_initiative()` line 324; charge roll: `spears_ai.py` line 540; morale 2d6: `spears_ai.py` line 665; reinforcements: `spears_ai.py` line 704; shuffling each hero's deck: `cards.py` line 35 and `game_data.py` line 110; hero turn order: `frodo_game.py` line 359 |
| 4 | A list changed with append/insert AND remove/pop | hand: `.remove()` at `cards.py` line 19, `.append()` at `cards.py` line 39, `.pop()` at `cards.py` line 38; models in a unit: `.append()` at `spears_ai.py` line 265, `.remove()` at `spears_ai.py` line 608; enemy units: `spears_ai.py` line 593; path: `.insert()` at `movement.py` line 101; inventory: `frodo_game.py` line 106 |
| 5 | A dictionary changed during play | `spears_memory` is `game["memory"]`: `frodo_game.py` line 160, halved in `spears_ai.py` > `fade_memory()` line 44; elements: `cards.py` > `use_element()` line 65 and `cards.py` > `wane_elements()` line 76; hero and model dictionaries: `combat.py` > `apply_damage()` line 47; stats: `frodo_game.py` line 438 |
| 6 | At least three `if` statements with `elif`/`else` | `combat.py` > `calc_damage()` line 30; `frodo_game.py` > `step_on_tile()` line 115; `frodo_game.py` > `play_card()` line 196; `spears_ai.py` > `unit_plan()` line 51; `frodo_game.py` > `do_request()` line 219; `art.py` > `draw_feature()` line 958; `cards.py` > `apply_item()` line 112 |
| 7 | At least three loops, including a `for` and a loop with `else` | `for` with `else`: `logbook.py` > `check_game_over()` line 98, `spears_ai.py` > `coherency_ok()` line 352; plain `for`: `combat.py` > `sort_turn_order()` line 66; `while`: `movement.py` > `step_map()` line 54, `frodo_game.py` > `hero_turn()` line 234 |
| 8 | Every function has a tagged docstring; at least 3 take parameters and return a value | See the table below (498 functions, all tagged). Examples: `combat.py` > `calc_damage()` line 30, `spears_ai.py` > `morale_test()` line 565, `spears_ai.py` > `advance_doom()` line 678, `movement.py` > `reachable_tiles()` line 69 |
| 9 | try/except around things that can fail | opening the data file: `game_data.py` line 92; numbers in the data file: `game_data.py` line 12; typed number box: `ui.py` line 1438; modifier maths: `combat.py` line 39; log file: `logbook.py` line 58; average with 0 rounds: `logbook.py` line 69; missing pygame: `frodo_game.py` line 10 |
| 10 | Write `frodo_log.txt`: each round plus a calculated summary | `logbook.py` > `write_log()` line 48, called at the end of every round from `frodo_game.py` > `end_round()` line 430; `logbook.py` > `write_summary()` line 63 calculates the averages, called from `frodo_game.py` > `finish_game()` line 448 |
| 11 | Read a team-made data file with `split()` (not json/csv) | `game_data.py` > `load_dungeon()` line 86 opens `dungeon_data.txt`; `game_data.py` > `read_line()` line 69 uses `split("\|")`; `game_data.py` > `parse_fields()` line 16 uses `split()` and `split("=")`; `game_data.py` > `parse_action()` line 26 uses `split(":")` |
| 12 | Visual: the pygame window | `ui.py` > `init()` line 62 opens the 1280x720 window with `pygame.SCALED`; `ui.py` > `draw_game()` line 1336 draws every frame; `ui.py` > `show_map()` line 559 draws the dungeon |

## Other rules

- No classes, lambdas, decorators or comprehensions in any file (checked with a script).
- Files are opened by name only: `dungeon_data.txt`, `frodo_log.txt`, and `<name>.txt` for a typed save name.
- `input()` is never used. The two typed fields are drawn in the window by `ui.py` > `ask_text()` line 1472: "How many tiles to move?" (`ui.py` > `typed_move()` line 1638) and "Name your save file" (`frodo_game.py` > `save_game()` line 344). Bad input is caught by `ui.py` > `check_number()` line 1432 and `ui.py` > `check_name()` line 1445, which show a message and ask again.
- Missing pygame prints `Run: pip install pygame` (`frodo_game.py` line 11).
- Functions longer than 30 lines: `generate_room` in `spears_ai.py` (34), `test_cards` in `test_frodo.py` (32), `test_saves` in `test_frodo.py` (33).

## Tags - read this before handing in

The AI assistant wrote every function. The brief says every docstring must start with `Team-written:` or `AI-assisted:`. Functions listed below as `(no tag)` have had their tag removed and need one before hand-in. Use `Team-written` only for a function your team wrote or rewrote itself.

## Every function and its tag

| File | Function | Line | Tag | Parameters | Returns a value |
|---|---|---|---|---|---|
| `frodo_game.py` | `install_room` | 31 | (no tag) | 2 | yes |
| `frodo_game.py` | `catch_breath` | 50 | (no tag) | 1 | yes |
| `frodo_game.py` | `enter_room` | 61 | (no tag) | 2 | yes |
| `frodo_game.py` | `start_dungeon` | 78 | (no tag) | 1 | yes |
| `frodo_game.py` | `spring_trap` | 89 | (no tag) | 2 | yes |
| `frodo_game.py` | `open_chest` | 101 | (no tag) | 3 | yes |
| `frodo_game.py` | `step_on_tile` | 115 | (no tag) | 2 | yes |
| `frodo_game.py` | `hero_move` | 135 | (no tag) | 3 | yes |
| `frodo_game.py` | `record_hit` | 152 | (no tag) | 3 | yes |
| `frodo_game.py` | `hero_attack` | 164 | (no tag) | 5 | yes |
| `frodo_game.py` | `hero_heal` | 185 | (no tag) | 4 | yes |
| `frodo_game.py` | `play_card` | 196 | (no tag) | 4 | yes |
| `frodo_game.py` | `do_request` | 219 | (no tag) | 3 | yes |
| `frodo_game.py` | `hero_turn` | 234 | (no tag) | 2 | yes |
| `frodo_game.py` | `use_menu` | 248 | (no tag) | 2 | yes |
| `frodo_game.py` | `damage_words` | 263 | (no tag) | 2 | yes |
| `frodo_game.py` | `health_now` | 275 | (no tag) | 1 | yes |
| `frodo_game.py` | `spears_phase` | 283 | (no tag) | 2 | yes |
| `frodo_game.py` | `take_turn` | 315 | (no tag) | 2 | yes |
| `frodo_game.py` | `start_round` | 335 | (no tag) | 1 | yes |
| `frodo_game.py` | `save_game` | 344 | (no tag) | 1 | yes |
| `frodo_game.py` | `set_initiative` | 357 | (no tag) | 2 | yes |
| `frodo_game.py` | `prepare_heroes` | 363 | (no tag) | 1 | yes |
| `frodo_game.py` | `play_round` | 375 | (no tag) | 1 | yes |
| `frodo_game.py` | `cleanup_cards` | 393 | (no tag) | 1 | yes |
| `frodo_game.py` | `mark_exhausted` | 403 | (no tag) | 1 | yes |
| `frodo_game.py` | `count_clumping` | 416 | (no tag) | 1 | yes |
| `frodo_game.py` | `end_round` | 430 | (no tag) | 1 | yes |
| `frodo_game.py` | `finish_game` | 448 | (no tag) | 2 | yes |
| `frodo_game.py` | `open_game` | 457 | (no tag) | 2 | yes |
| `frodo_game.py` | `choose_game` | 471 | (no tag) | 1 | yes |
| `frodo_game.py` | `main` | 484 | (no tag) | 0 | no |
| `game_data.py` | `clean_value` | 8 | (no tag) | 1 | yes |
| `game_data.py` | `parse_fields` | 16 | (no tag) | 1 | yes |
| `game_data.py` | `parse_action` | 26 | (no tag) | 1 | yes |
| `game_data.py` | `make_card` | 38 | (no tag) | 2 | yes |
| `game_data.py` | `store_record` | 46 | (no tag) | 4 | yes |
| `game_data.py` | `read_line` | 69 | (no tag) | 2 | yes |
| `game_data.py` | `load_dungeon` | 86 | (no tag) | 1 | yes |
| `game_data.py` | `make_hero` | 100 | (no tag) | 2 | yes |
| `game_data.py` | `new_memory` | 118 | (no tag) | 0 | yes |
| `game_data.py` | `new_stats` | 124 | (no tag) | 0 | yes |
| `game_data.py` | `new_game` | 130 | (no tag) | 2 | yes |
| `game_data.py` | `find_hero` | 149 | (no tag) | 2 | yes |
| `game_data.py` | `place_party` | 157 | (no tag) | 2 | yes |
| `combat.py` | `build_modifier_deck` | 5 | (no tag) | 0 | yes |
| `combat.py` | `draw_modifier` | 16 | (no tag) | 2 | yes |
| `combat.py` | `calc_damage` | 30 | (no tag) | 3 | yes |
| `combat.py` | `apply_damage` | 47 | (no tag) | 2 | yes |
| `combat.py` | `roll_attack` | 55 | (no tag) | 4 | yes |
| `combat.py` | `sort_turn_order` | 66 | (no tag) | 2 | yes |
| `cards.py` | `find_card` | 7 | (no tag) | 2 | yes |
| `cards.py` | `choose_card` | 15 | (no tag) | 2 | yes |
| `cards.py` | `finish_card` | 23 | (no tag) | 2 | yes |
| `cards.py` | `draw_card` | 29 | (no tag) | 1 | yes |
| `cards.py` | `refill_hand` | 43 | (no tag) | 1 | yes |
| `cards.py` | `is_exhausted` | 51 | (no tag) | 1 | yes |
| `cards.py` | `heal_hero` | 56 | (no tag) | 2 | yes |
| `cards.py` | `use_element` | 65 | (no tag) | 2 | yes |
| `cards.py` | `wane_elements` | 76 | (no tag) | 1 | yes |
| `cards.py` | `search_poi` | 87 | (no tag) | 3 | yes |
| `cards.py` | `cheese_feast` | 100 | (no tag) | 2 | yes |
| `cards.py` | `apply_item` | 112 | (no tag) | 3 | yes |
| `spears_ai.py` | `spears_counter` | 31 | (no tag) | 1 | yes |
| `spears_ai.py` | `fade_memory` | 44 | (no tag) | 1 | yes |
| `spears_ai.py` | `unit_plan` | 51 | (no tag) | 3 | yes |
| `spears_ai.py` | `pick_style` | 72 | (no tag) | 2 | yes |
| `spears_ai.py` | `build_dungeon` | 86 | (no tag) | 1 | yes |
| `spears_ai.py` | `boss_chamber` | 108 | (no tag) | 1 | yes |
| `spears_ai.py` | `chamber_at` | 116 | (no tag) | 2 | yes |
| `spears_ai.py` | `door_at` | 124 | (no tag) | 2 | yes |
| `spears_ai.py` | `place_letters` | 132 | (no tag) | 4 | yes |
| `spears_ai.py` | `furnish` | 142 | (no tag) | 4 | yes |
| `spears_ai.py` | `deploy_room` | 168 | (no tag) | 3 | yes |
| `spears_ai.py` | `add_unit` | 183 | (no tag) | 5 | yes |
| `spears_ai.py` | `deploy_boss` | 195 | (no tag) | 2 | yes |
| `spears_ai.py` | `place_exits` | 207 | (no tag) | 2 | yes |
| `spears_ai.py` | `nearest_tile` | 226 | (no tag) | 2 | yes |
| `spears_ai.py` | `connect_chamber` | 235 | (no tag) | 2 | yes |
| `spears_ai.py` | `make_unit` | 246 | (no tag) | 3 | yes |
| `spears_ai.py` | `place_models` | 258 | (no tag) | 4 | yes |
| `spears_ai.py` | `generate_room` | 270 | (no tag) | 3 | yes |
| `spears_ai.py` | `find_unit` | 308 | (no tag) | 2 | yes |
| `spears_ai.py` | `unit_visible` | 316 | (no tag) | 2 | yes |
| `spears_ai.py` | `pick_initiative` | 324 | (no tag) | 1 | yes |
| `spears_ai.py` | `pick_target` | 336 | (no tag) | 2 | yes |
| `spears_ai.py` | `coherency_ok` | 352 | (no tag) | 3 | yes |
| `spears_ai.py` | `goal_tile` | 364 | (no tag) | 3 | yes |
| `spears_ai.py` | `is_flank` | 373 | (no tag) | 3 | yes |
| `spears_ai.py` | `ranged_score` | 380 | (no tag) | 2 | yes |
| `spears_ai.py` | `tile_score` | 390 | (no tag) | 4 | yes |
| `spears_ai.py` | `best_tile` | 403 | (no tag) | 5 | yes |
| `spears_ai.py` | `move_unit` | 424 | (no tag) | 4 | yes |
| `spears_ai.py` | `choose_victim` | 438 | (no tag) | 4 | yes |
| `spears_ai.py` | `cover_bonus` | 451 | (no tag) | 3 | yes |
| `spears_ai.py` | `hero_falls` | 459 | (no tag) | 2 | yes |
| `spears_ai.py` | `splash` | 467 | (no tag) | 3 | yes |
| `spears_ai.py` | `unit_attack` | 483 | (no tag) | 4 | yes |
| `spears_ai.py` | `unit_shoot` | 507 | (no tag) | 3 | yes |
| `spears_ai.py` | `touching_hero` | 517 | (no tag) | 2 | yes |
| `spears_ai.py` | `nearest_gap` | 526 | (no tag) | 2 | yes |
| `spears_ai.py` | `unit_charge` | 536 | (no tag) | 3 | yes |
| `spears_ai.py` | `unit_fight` | 553 | (no tag) | 3 | yes |
| `spears_ai.py` | `morale_test` | 565 | (no tag) | 2 | yes |
| `spears_ai.py` | `check_room_clear` | 570 | (no tag) | 2 | yes |
| `spears_ai.py` | `destroy_unit` | 591 | (no tag) | 3 | yes |
| `spears_ai.py` | `remove_model` | 605 | (no tag) | 3 | yes |
| `spears_ai.py` | `safest_tile` | 615 | (no tag) | 3 | yes |
| `spears_ai.py` | `fall_back` | 632 | (no tag) | 2 | yes |
| `spears_ai.py` | `break_unit` | 644 | (no tag) | 2 | yes |
| `spears_ai.py` | `unit_morale` | 660 | (no tag) | 2 | yes |
| `spears_ai.py` | `advance_doom` | 678 | (no tag) | 3 | yes |
| `spears_ai.py` | `prepare_ahead` | 686 | (no tag) | 2 | yes |
| `spears_ai.py` | `reinforce` | 694 | (no tag) | 1 | yes |
| `spears_ai.py` | `apply_preparations` | 710 | (no tag) | 3 | yes |
| `spears_ai.py` | `warlord` | 732 | (no tag) | 1 | yes |
| `spears_ai.py` | `summon_guards` | 740 | (no tag) | 2 | yes |
| `spears_ai.py` | `enrage` | 754 | (no tag) | 1 | yes |
| `spears_ai.py` | `boss_check` | 761 | (no tag) | 2 | yes |
| `movement.py` | `tile_distance` | 11 | (no tag) | 2 | yes |
| `movement.py` | `in_bounds` | 16 | (no tag) | 3 | yes |
| `movement.py` | `is_floor` | 21 | (no tag) | 4 | yes |
| `movement.py` | `blank_grid` | 34 | (no tag) | 2 | yes |
| `movement.py` | `can_enter` | 45 | (no tag) | 5 | yes |
| `movement.py` | `step_map` | 54 | (no tag) | 4 | yes |
| `movement.py` | `reachable_tiles` | 69 | (no tag) | 6 | yes |
| `movement.py` | `lower_neighbor` | 81 | (no tag) | 2 | yes |
| `movement.py` | `find_path` | 92 | (no tag) | 5 | yes |
| `movement.py` | `hero_tiles` | 105 | (no tag) | 1 | yes |
| `movement.py` | `model_tiles` | 114 | (no tag) | 1 | yes |
| `movement.py` | `hero_at` | 123 | (no tag) | 2 | yes |
| `movement.py` | `model_at` | 131 | (no tag) | 2 | yes |
| `movement.py` | `learn_outline` | 140 | (no tag) | 1 | yes |
| `movement.py` | `shown_letter` | 159 | (no tag) | 1 | yes |
| `movement.py` | `lit_floor` | 168 | (no tag) | 1 | yes |
| `movement.py` | `wall_in_view` | 180 | (no tag) | 4 | yes |
| `movement.py` | `refresh_vision` | 189 | (no tag) | 1 | yes |
| `movement.py` | `enemy_targets` | 205 | (no tag) | 3 | yes |
| `movement.py` | `friend_targets` | 214 | (no tag) | 3 | yes |
| `movement.py` | `move_targets` | 223 | (no tag) | 2 | yes |
| `movement.py` | `action_targets` | 235 | (no tag) | 3 | yes |
| `movement.py` | `is_valid_drop` | 245 | (no tag) | 2 | yes |
| `movement.py` | `drop_message` | 250 | (no tag) | 4 | yes |
| `logbook.py` | `say` | 4 | (no tag) | 2 | yes |
| `logbook.py` | `note` | 11 | (no tag) | 2 | yes |
| `logbook.py` | `tell` | 17 | (no tag) | 3 | yes |
| `logbook.py` | `add_float` | 24 | (no tag) | 4 | yes |
| `logbook.py` | `add_banner` | 30 | (no tag) | 2 | yes |
| `logbook.py` | `start_log` | 36 | (no tag) | 1 | yes |
| `logbook.py` | `write_log` | 48 | (no tag) | 2 | yes |
| `logbook.py` | `write_summary` | 63 | (no tag) | 1 | yes |
| `logbook.py` | `summary_lines` | 83 | (no tag) | 1 | yes |
| `logbook.py` | `check_game_over` | 98 | (no tag) | 4 | yes |
| `logbook.py` | `status_lines` | 112 | (no tag) | 1 | yes |
| `logbook.py` | `hero_line` | 124 | (no tag) | 1 | yes |
| `ui.py` | `init` | 62 | AI-assisted | 0 | yes |
| `ui.py` | `set_message` | 75 | AI-assisted | 1 | yes |
| `ui.py` | `tile_rect` | 81 | AI-assisted | 1 | yes |
| `ui.py` | `tile_center` | 94 | AI-assisted | 1 | yes |
| `ui.py` | `tile_at` | 100 | AI-assisted | 1 | yes |
| `ui.py` | `hero_block_rect` | 112 | AI-assisted | 1 | yes |
| `ui.py` | `card_rect` | 117 | AI-assisted | 1 | yes |
| `ui.py` | `hero_at_pixel` | 122 | AI-assisted | 2 | yes |
| `ui.py` | `moved_far` | 133 | AI-assisted | 2 | yes |
| `ui.py` | `selected_hero` | 138 | AI-assisted | 1 | yes |
| `ui.py` | `find_by_name` | 145 | AI-assisted | 2 | yes |
| `ui.py` | `make_button` | 155 | AI-assisted | 3 | yes |
| `ui.py` | `set_buttons` | 160 | AI-assisted | 1 | yes |
| `ui.py` | `button_at` | 172 | AI-assisted | 2 | yes |
| `ui.py` | `tile_letter` | 182 | AI-assisted | 3 | yes |
| `ui.py` | `min_zoom` | 191 | AI-assisted | 0 | yes |
| `ui.py` | `clamp_camera` | 198 | AI-assisted | 0 | yes |
| `ui.py` | `view_rect` | 211 | AI-assisted | 0 | yes |
| `ui.py` | `visible_box` | 218 | AI-assisted | 0 | yes |
| `ui.py` | `tile_middle` | 228 | AI-assisted | 1 | yes |
| `ui.py` | `follow` | 233 | AI-assisted | 1 | yes |
| `ui.py` | `frame_tiles` | 244 | AI-assisted | 2 | yes |
| `ui.py` | `show_chamber` | 264 | AI-assisted | 2 | yes |
| `ui.py` | `fit_view` | 270 | AI-assisted | 1 | yes |
| `ui.py` | `zoom_by` | 280 | AI-assisted | 2 | yes |
| `ui.py` | `glide_camera` | 293 | AI-assisted | 0 | no |
| `ui.py` | `camera_event` | 316 | AI-assisted | 2 | yes |
| `ui.py` | `camera_key` | 338 | AI-assisted | 2 | yes |
| `ui.py` | `seen_letters` | 352 | AI-assisted | 1 | yes |
| `ui.py` | `room_art` | 363 | AI-assisted | 2 | yes |
| `ui.py` | `draw_features` | 378 | AI-assisted | 2 | yes |
| `ui.py` | `draw_ripples` | 398 | AI-assisted | 2 | yes |
| `ui.py` | `draw_highlights` | 411 | AI-assisted | 0 | yes |
| `ui.py` | `light_sources` | 425 | AI-assisted | 1 | yes |
| `ui.py` | `draw_flames` | 438 | AI-assisted | 3 | yes |
| `ui.py` | `draw_lighting` | 455 | AI-assisted | 2 | yes |
| `ui.py` | `visible_models` | 466 | AI-assisted | 2 | yes |
| `ui.py` | `draw_coherency` | 475 | AI-assisted | 1 | no |
| `ui.py` | `draw_model_token` | 486 | AI-assisted | 2 | no |
| `ui.py` | `draw_figures` | 497 | AI-assisted | 1 | yes |
| `ui.py` | `draw_hero_token` | 516 | AI-assisted | 2 | no |
| `ui.py` | `draw_cursor` | 529 | AI-assisted | 0 | no |
| `ui.py` | `paint_world` | 537 | AI-assisted | 3 | yes |
| `ui.py` | `show_map` | 559 | AI-assisted | 1 | yes |
| `ui.py` | `draw_zoom_hint` | 589 | AI-assisted | 0 | no |
| `ui.py` | `draw_boss_bar` | 598 | AI-assisted | 1 | yes |
| `ui.py` | `tooltip_lines` | 615 | AI-assisted | 2 | yes |
| `ui.py` | `draw_tooltip` | 634 | AI-assisted | 1 | yes |
| `ui.py` | `draw_doom` | 655 | AI-assisted | 1 | yes |
| `ui.py` | `draw_elements` | 669 | AI-assisted | 1 | no |
| `ui.py` | `draw_tracker_entry` | 688 | AI-assisted | 3 | no |
| `ui.py` | `draw_top_bar` | 714 | AI-assisted | 1 | no |
| `ui.py` | `hero_status` | 732 | AI-assisted | 2 | yes |
| `ui.py` | `draw_portrait` | 744 | AI-assisted | 2 | no |
| `ui.py` | `draw_hero_block` | 751 | AI-assisted | 2 | no |
| `ui.py` | `draw_party_panel` | 771 | AI-assisted | 1 | no |
| `ui.py` | `log_color` | 778 | AI-assisted | 1 | yes |
| `ui.py` | `draw_log` | 786 | AI-assisted | 1 | yes |
| `ui.py` | `draw_message` | 807 | AI-assisted | 0 | no |
| `ui.py` | `dragging_card` | 818 | AI-assisted | 1 | yes |
| `ui.py` | `draw_pile` | 824 | AI-assisted | 1 | no |
| `ui.py` | `draw_hand` | 837 | AI-assisted | 1 | yes |
| `ui.py` | `phase_hint` | 860 | AI-assisted | 0 | yes |
| `ui.py` | `draw_bottom` | 866 | AI-assisted | 1 | yes |
| `ui.py` | `effect_start` | 881 | AI-assisted | 0 | yes |
| `ui.py` | `add_floater` | 886 | AI-assisted | 3 | yes |
| `ui.py` | `add_strike` | 893 | AI-assisted | 1 | yes |
| `ui.py` | `consume_fx` | 907 | AI-assisted | 1 | yes |
| `ui.py` | `fade_list` | 929 | AI-assisted | 1 | yes |
| `ui.py` | `draw_mod_card` | 939 | AI-assisted | 0 | no |
| `ui.py` | `draw_banner` | 951 | AI-assisted | 0 | no |
| `ui.py` | `draw_effects` | 970 | AI-assisted | 0 | no |
| `ui.py` | `lerp` | 991 | AI-assisted | 3 | yes |
| `ui.py` | `draw_slash` | 996 | AI-assisted | 2 | no |
| `ui.py` | `draw_strike` | 1006 | AI-assisted | 2 | no |
| `ui.py` | `draw_strikes` | 1034 | AI-assisted | 0 | yes |
| `ui.py` | `caption` | 1045 | AI-assisted | 3 | no |
| `ui.py` | `draw_caption` | 1057 | AI-assisted | 0 | yes |
| `ui.py` | `model_paths` | 1076 | AI-assisted | 1 | yes |
| `ui.py` | `play_moves` | 1093 | AI-assisted | 1 | yes |
| `ui.py` | `place_model` | 1115 | AI-assisted | 4 | no |
| `ui.py` | `fast_forward` | 1124 | AI-assisted | 0 | yes |
| `ui.py` | `wait_effects` | 1131 | AI-assisted | 1 | no |
| `ui.py` | `draw_path` | 1140 | AI-assisted | 3 | yes |
| `ui.py` | `preview_words` | 1150 | AI-assisted | 4 | yes |
| `ui.py` | `draw_preview` | 1166 | AI-assisted | 3 | yes |
| `ui.py` | `draw_drag` | 1183 | AI-assisted | 1 | yes |
| `ui.py` | `exit_open` | 1204 | AI-assisted | 1 | yes |
| `ui.py` | `heal_tip` | 1215 | AI-assisted | 2 | yes |
| `ui.py` | `reach_tip` | 1227 | AI-assisted | 2 | yes |
| `ui.py` | `loot_tip` | 1239 | AI-assisted | 2 | yes |
| `ui.py` | `situation_tip` | 1247 | AI-assisted | 1 | yes |
| `ui.py` | `draw_tip` | 1267 | AI-assisted | 1 | yes |
| `ui.py` | `hint_for` | 1280 | AI-assisted | 2 | yes |
| `ui.py` | `draw_hint` | 1301 | AI-assisted | 1 | yes |
| `ui.py` | `learn_hint` | 1328 | AI-assisted | 1 | yes |
| `ui.py` | `draw_game` | 1336 | AI-assisted | 1 | no |
| `ui.py` | `common_event` | 1355 | AI-assisted | 2 | no |
| `ui.py` | `present` | 1370 | AI-assisted | 1 | yes |
| `ui.py` | `frame` | 1387 | AI-assisted | 1 | yes |
| `ui.py` | `pause` | 1393 | AI-assisted | 2 | no |
| `ui.py` | `move_cursor` | 1404 | AI-assisted | 2 | yes |
| `ui.py` | `clear_input` | 1416 | AI-assisted | 0 | no |
| `ui.py` | `dim_screen` | 1425 | AI-assisted | 0 | no |
| `ui.py` | `check_number` | 1432 | AI-assisted | 3 | yes |
| `ui.py` | `check_name` | 1445 | AI-assisted | 1 | yes |
| `ui.py` | `draw_text_box` | 1455 | AI-assisted | 3 | no |
| `ui.py` | `ask_text` | 1472 | AI-assisted | 5 | yes |
| `ui.py` | `type_loop` | 1482 | AI-assisted | 5 | yes |
| `ui.py` | `ask_yes_no` | 1510 | AI-assisted | 2 | yes |
| `ui.py` | `ask_direction` | 1533 | AI-assisted | 1 | yes |
| `ui.py` | `confirm_quit` | 1547 | AI-assisted | 1 | yes |
| `ui.py` | `turn_buttons` | 1552 | AI-assisted | 0 | yes |
| `ui.py` | `show_moves` | 1558 | AI-assisted | 2 | yes |
| `ui.py` | `show_targets` | 1567 | AI-assisted | 2 | yes |
| `ui.py` | `refresh_glow` | 1575 | AI-assisted | 2 | yes |
| `ui.py` | `hand_card_at` | 1583 | AI-assisted | 2 | yes |
| `ui.py` | `pick_card` | 1592 | AI-assisted | 2 | yes |
| `ui.py` | `card_request` | 1606 | AI-assisted | 3 | yes |
| `ui.py` | `move_request` | 1616 | AI-assisted | 3 | yes |
| `ui.py` | `tile_request` | 1624 | AI-assisted | 3 | yes |
| `ui.py` | `typed_move` | 1638 | AI-assisted | 2 | yes |
| `ui.py` | `turn_button` | 1654 | AI-assisted | 3 | yes |
| `ui.py` | `turn_mouse_down` | 1667 | AI-assisted | 3 | yes |
| `ui.py` | `turn_mouse_up` | 1685 | AI-assisted | 3 | yes |
| `ui.py` | `turn_key` | 1701 | AI-assisted | 3 | yes |
| `ui.py` | `turn_intro` | 1721 | AI-assisted | 1 | yes |
| `ui.py` | `get_hero_action` | 1731 | AI-assisted | 2 | yes |
| `ui.py` | `draw_title` | 1762 | AI-assisted | 2 | no |
| `ui.py` | `title_screen` | 1781 | AI-assisted | 1 | yes |
| `ui.py` | `save_rect` | 1800 | AI-assisted | 1 | yes |
| `ui.py` | `draw_load_screen` | 1805 | AI-assisted | 2 | no |
| `ui.py` | `hover_border` | 1826 | AI-assisted | 1 | yes |
| `ui.py` | `load_screen` | 1833 | AI-assisted | 0 | yes |
| `ui.py` | `recruit_rect` | 1853 | AI-assisted | 1 | yes |
| `ui.py` | `draw_recruit` | 1858 | AI-assisted | 4 | no |
| `ui.py` | `draw_party_screen` | 1882 | AI-assisted | 5 | no |
| `ui.py` | `toggle_recruit` | 1906 | AI-assisted | 2 | yes |
| `ui.py` | `party_event` | 1917 | AI-assisted | 3 | yes |
| `ui.py` | `party_screen` | 1934 | AI-assisted | 1 | yes |
| `ui.py` | `title_flow` | 1959 | AI-assisted | 2 | yes |
| `ui.py` | `draw_legend` | 2057 | AI-assisted | 1 | no |
| `ui.py` | `quick_panel` | 2067 | AI-assisted | 3 | yes |
| `ui.py` | `quick_pictures` | 2079 | AI-assisted | 1 | no |
| `ui.py` | `draw_quickstart` | 2095 | AI-assisted | 1 | no |
| `ui.py` | `show_quickstart` | 2121 | AI-assisted | 1 | no |
| `ui.py` | `draw_rules_page` | 2136 | AI-assisted | 1 | no |
| `ui.py` | `show_rules` | 2162 | AI-assisted | 0 | yes |
| `ui.py` | `memory_line` | 2183 | AI-assisted | 1 | yes |
| `ui.py` | `draw_status_box` | 2191 | AI-assisted | 1 | no |
| `ui.py` | `show_status` | 2206 | AI-assisted | 1 | yes |
| `ui.py` | `draw_end` | 2219 | AI-assisted | 2 | no |
| `ui.py` | `end_screen` | 2240 | AI-assisted | 2 | yes |
| `art.py` | `pick_font` | 66 | AI-assisted | 3 | yes |
| `art.py` | `make_fonts` | 74 | AI-assisted | 0 | yes |
| `art.py` | `setup` | 89 | AI-assisted | 1 | yes |
| `art.py` | `build_overlays` | 105 | AI-assisted | 1 | no |
| `art.py` | `stamp` | 119 | AI-assisted | 2 | no |
| `art.py` | `clamp` | 124 | AI-assisted | 1 | yes |
| `art.py` | `tint` | 129 | AI-assisted | 2 | yes |
| `art.py` | `pulse` | 134 | AI-assisted | 0 | yes |
| `art.py` | `noise_tile` | 141 | AI-assisted | 4 | yes |
| `art.py` | `blotchy` | 151 | AI-assisted | 3 | yes |
| `art.py` | `crack` | 165 | AI-assisted | 3 | no |
| `art.py` | `floor_tile` | 178 | AI-assisted | 2 | yes |
| `art.py` | `wall_tile` | 196 | AI-assisted | 2 | yes |
| `art.py` | `fill_texture` | 215 | AI-assisted | 2 | yes |
| `art.py` | `build_panel` | 228 | AI-assisted | 3 | yes |
| `art.py` | `panel` | 247 | AI-assisted | 3 | yes |
| `art.py` | `shade` | 258 | AI-assisted | 3 | yes |
| `art.py` | `vignette` | 266 | AI-assisted | 1 | yes |
| `art.py` | `torch_glow` | 279 | AI-assisted | 3 | no |
| `art.py` | `draw_backdrop` | 291 | AI-assisted | 0 | no |
| `art.py` | `text` | 309 | AI-assisted | 6 | yes |
| `art.py` | `text_outline` | 323 | AI-assisted | 6 | yes |
| `art.py` | `wrap_text` | 330 | AI-assisted | 3 | yes |
| `art.py` | `ribbon` | 346 | AI-assisted | 5 | no |
| `art.py` | `divider` | 356 | AI-assisted | 3 | no |
| `art.py` | `draw_plate` | 366 | AI-assisted | 3 | yes |
| `art.py` | `draw_button` | 387 | AI-assisted | 1 | yes |
| `art.py` | `draw_bar` | 395 | AI-assisted | 4 | no |
| `art.py` | `draw_pips` | 409 | AI-assisted | 4 | no |
| `art.py` | `draw_skull` | 417 | AI-assisted | 4 | no |
| `art.py` | `medallion` | 430 | AI-assisted | 5 | no |
| `art.py` | `icon_attack` | 440 | AI-assisted | 4 | no |
| `art.py` | `icon_move` | 448 | AI-assisted | 4 | no |
| `art.py` | `icon_heal` | 455 | AI-assisted | 4 | no |
| `art.py` | `icon_shield` | 463 | AI-assisted | 4 | no |
| `art.py` | `icon_element` | 471 | AI-assisted | 4 | no |
| `art.py` | `draw_icon` | 493 | AI-assisted | 5 | yes |
| `art.py` | `mini_card` | 508 | AI-assisted | 4 | no |
| `art.py` | `paint_frodo` | 518 | AI-assisted | 4 | no |
| `art.py` | `paint_frodo_helmet` | 537 | AI-assisted | 4 | no |
| `art.py` | `paint_frodo_face` | 548 | AI-assisted | 4 | no |
| `art.py` | `paint_body` | 558 | AI-assisted | 6 | no |
| `art.py` | `paint_tank` | 570 | AI-assisted | 4 | no |
| `art.py` | `paint_archer` | 584 | AI-assisted | 4 | no |
| `art.py` | `paint_mage` | 598 | AI-assisted | 4 | no |
| `art.py` | `paint_rogue` | 611 | AI-assisted | 4 | no |
| `art.py` | `paint_orc` | 624 | AI-assisted | 4 | no |
| `art.py` | `paint_goblin` | 637 | AI-assisted | 4 | no |
| `art.py` | `paint_guard` | 649 | AI-assisted | 4 | no |
| `art.py` | `paint_wolf` | 664 | AI-assisted | 4 | no |
| `art.py` | `paint_bomber` | 681 | AI-assisted | 4 | no |
| `art.py` | `paint_shade` | 696 | AI-assisted | 4 | no |
| `art.py` | `paint_warlord` | 708 | AI-assisted | 4 | no |
| `art.py` | `paint_figure` | 726 | AI-assisted | 5 | yes |
| `art.py` | `outlined` | 755 | AI-assisted | 2 | yes |
| `art.py` | `sprite` | 766 | AI-assisted | 2 | yes |
| `art.py` | `draw_base` | 777 | AI-assisted | 4 | no |
| `art.py` | `draw_hero` | 789 | AI-assisted | 4 | yes |
| `art.py` | `draw_model` | 797 | AI-assisted | 4 | yes |
| `art.py` | `draw_floor` | 810 | AI-assisted | 2 | no |
| `art.py` | `draw_wall` | 815 | AI-assisted | 2 | no |
| `art.py` | `draw_door` | 820 | AI-assisted | 2 | no |
| `art.py` | `draw_boss_mark` | 844 | AI-assisted | 1 | no |
| `art.py` | `draw_throne` | 855 | AI-assisted | 1 | no |
| `art.py` | `draw_brazier` | 873 | AI-assisted | 1 | no |
| `art.py` | `draw_open_door` | 886 | AI-assisted | 1 | no |
| `art.py` | `draw_chest` | 897 | AI-assisted | 1 | no |
| `art.py` | `draw_trap` | 913 | AI-assisted | 1 | no |
| `art.py` | `draw_shrine` | 927 | AI-assisted | 1 | no |
| `art.py` | `draw_cover` | 942 | AI-assisted | 1 | no |
| `art.py` | `draw_feature` | 958 | AI-assisted | 3 | yes |
| `art.py` | `glow_rect` | 981 | AI-assisted | 3 | no |
| `art.py` | `action_words` | 994 | AI-assisted | 1 | yes |
| `art.py` | `draw_card` | 1008 | AI-assisted | 4 | yes |
| `art.py` | `draw_modifier` | 1031 | AI-assisted | 4 | no |
| `scenery.py` | `is_wall` | 35 | (no tag) | 3 | yes |
| `scenery.py` | `layer` | 42 | (no tag) | 2 | yes |
| `scenery.py` | `soft_blob` | 47 | (no tag) | 7 | no |
| `scenery.py` | `grain` | 54 | (no tag) | 0 | yes |
| `scenery.py` | `add_grain` | 67 | (no tag) | 1 | no |
| `scenery.py` | `slab_fits` | 77 | (no tag) | 4 | yes |
| `scenery.py` | `pick_size` | 86 | (no tag) | 4 | yes |
| `scenery.py` | `slab_plan` | 95 | (no tag) | 3 | yes |
| `scenery.py` | `scratch` | 113 | (no tag) | 5 | no |
| `scenery.py` | `paint_slab` | 123 | (no tag) | 3 | no |
| `scenery.py` | `paint_puddle` | 144 | (no tag) | 3 | yes |
| `scenery.py` | `paint_debris` | 159 | (no tag) | 3 | no |
| `scenery.py` | `random_spot` | 174 | AI-assisted | 3 | yes |
| `scenery.py` | `paint_floor` | 179 | AI-assisted | 4 | yes |
| `scenery.py` | `floor_base` | 200 | AI-assisted | 3 | yes |
| `scenery.py` | `paint_grid_hints` | 210 | (no tag) | 2 | yes |
| `scenery.py` | `gradient` | 231 | (no tag) | 4 | yes |
| `scenery.py` | `cached_gradient` | 251 | AI-assisted | 4 | yes |
| `scenery.py` | `paint_wall_shadows` | 259 | (no tag) | 2 | no |
| `scenery.py` | `paint_rock_top` | 283 | (no tag) | 5 | no |
| `scenery.py` | `brick_tint` | 304 | (no tag) | 2 | yes |
| `scenery.py` | `paint_course` | 309 | (no tag) | 5 | no |
| `scenery.py` | `paint_damp` | 321 | (no tag) | 5 | no |
| `scenery.py` | `paint_face` | 333 | (no tag) | 5 | yes |
| `scenery.py` | `has_torch` | 355 | (no tag) | 2 | yes |
| `scenery.py` | `paint_sconce` | 360 | (no tag) | 3 | no |
| `scenery.py` | `near_floor` | 367 | AI-assisted | 3 | yes |
| `scenery.py` | `tile_dice` | 376 | AI-assisted | 3 | yes |
| `scenery.py` | `paint_walls` | 381 | AI-assisted | 3 | yes |
| `scenery.py` | `build_room` | 403 | AI-assisted | 2 | yes |
| `scenery.py` | `light_color` | 415 | AI-assisted | 5 | yes |
| `scenery.py` | `light_grid` | 427 | AI-assisted | 4 | yes |
| `scenery.py` | `draw_flame` | 436 | AI-assisted | 4 | no |
| `scenery.py` | `draw_ripple` | 449 | (no tag) | 3 | no |
| `chambers.py` | `blank_map` | 18 | AI-assisted | 2 | yes |
| `chambers.py` | `zone_box` | 26 | AI-assisted | 2 | yes |
| `chambers.py` | `box_center` | 35 | AI-assisted | 1 | yes |
| `chambers.py` | `shrink_box` | 40 | AI-assisted | 1 | yes |
| `chambers.py` | `box_tiles` | 51 | AI-assisted | 1 | yes |
| `chambers.py` | `cell_zone` | 62 | AI-assisted | 2 | yes |
| `chambers.py` | `cell_neighbors` | 78 | AI-assisted | 2 | yes |
| `chambers.py` | `touches` | 89 | AI-assisted | 3 | yes |
| `chambers.py` | `boss_block` | 97 | AI-assisted | 1 | yes |
| `chambers.py` | `far_cell` | 104 | AI-assisted | 2 | yes |
| `chambers.py` | `random_walk` | 123 | AI-assisted | 4 | yes |
| `chambers.py` | `main_path` | 139 | AI-assisted | 3 | yes |
| `chambers.py` | `make_chamber` | 150 | AI-assisted | 5 | yes |
| `chambers.py` | `add_sides` | 157 | AI-assisted | 4 | yes |
| `chambers.py` | `plan_dungeon` | 180 | AI-assisted | 1 | yes |
| `chambers.py` | `children` | 203 | AI-assisted | 2 | yes |
| `chambers.py` | `owner_grid` | 212 | AI-assisted | 2 | yes |
| `chambers.py` | `shape_ell` | 225 | AI-assisted | 1 | yes |
| `chambers.py` | `shape_round` | 240 | AI-assisted | 1 | yes |
| `chambers.py` | `shape_cross` | 254 | AI-assisted | 1 | yes |
| `chambers.py` | `shape_cave` | 271 | AI-assisted | 1 | yes |
| `chambers.py` | `connected` | 281 | AI-assisted | 1 | yes |
| `chambers.py` | `shape_tiles` | 297 | AI-assisted | 2 | yes |
| `chambers.py` | `is_open_floor` | 315 | AI-assisted | 2 | yes |
| `chambers.py` | `add_pillars` | 324 | AI-assisted | 2 | yes |
| `chambers.py` | `carve_chamber` | 341 | AI-assisted | 3 | yes |
| `chambers.py` | `carve_arena` | 351 | AI-assisted | 3 | yes |
| `chambers.py` | `inside` | 375 | AI-assisted | 3 | yes |
| `chambers.py` | `open_sides` | 380 | AI-assisted | 2 | yes |
| `chambers.py` | `pick_door` | 391 | AI-assisted | 3 | yes |
| `chambers.py` | `can_dig` | 409 | AI-assisted | 4 | yes |
| `chambers.py` | `find_corridor` | 425 | AI-assisted | 2 | yes |
| `chambers.py` | `dig_corridor` | 447 | AI-assisted | 5 | yes |
| `chambers.py` | `far_cluster` | 463 | AI-assisted | 3 | yes |
| `chambers.py` | `far_tiles` | 481 | AI-assisted | 2 | yes |
| `savegame.py` | `word` | 21 | AI-assisted | 1 | yes |
| `savegame.py` | `tile_text` | 26 | AI-assisted | 1 | yes |
| `savegame.py` | `tiles_text` | 33 | AI-assisted | 1 | yes |
| `savegame.py` | `names_text` | 43 | AI-assisted | 1 | yes |
| `savegame.py` | `card_names` | 53 | AI-assisted | 1 | yes |
| `savegame.py` | `yes_no` | 61 | AI-assisted | 1 | yes |
| `savegame.py` | `record` | 68 | AI-assisted | 3 | yes |
| `savegame.py` | `read_tile` | 78 | AI-assisted | 1 | yes |
| `savegame.py` | `read_tiles` | 87 | AI-assisted | 1 | yes |
| `savegame.py` | `read_names` | 98 | AI-assisted | 1 | yes |
| `savegame.py` | `is_yes` | 106 | AI-assisted | 1 | yes |
| `savegame.py` | `game_line` | 113 | AI-assisted | 1 | yes |
| `savegame.py` | `hero_line` | 125 | AI-assisted | 1 | yes |
| `savegame.py` | `chamber_line` | 135 | AI-assisted | 1 | yes |
| `savegame.py` | `unit_line` | 153 | AI-assisted | 1 | yes |
| `savegame.py` | `number_line` | 166 | AI-assisted | 2 | yes |
| `savegame.py` | `raw_line` | 174 | AI-assisted | 3 | yes |
| `savegame.py` | `map_lines` | 179 | AI-assisted | 2 | yes |
| `savegame.py` | `save_lines` | 187 | AI-assisted | 1 | yes |
| `savegame.py` | `save_game` | 210 | AI-assisted | 2 | yes |
| `savegame.py` | `find_in_deck` | 224 | AI-assisted | 3 | yes |
| `savegame.py` | `read_pile` | 232 | AI-assisted | 3 | yes |
| `savegame.py` | `load_hero` | 240 | AI-assisted | 4 | yes |
| `savegame.py` | `load_chamber` | 254 | AI-assisted | 4 | yes |
| `savegame.py` | `load_unit` | 274 | AI-assisted | 4 | yes |
| `savegame.py` | `load_game_line` | 289 | AI-assisted | 2 | yes |
| `savegame.py` | `load_raw` | 303 | AI-assisted | 4 | yes |
| `savegame.py` | `load_record` | 318 | AI-assisted | 5 | yes |
| `savegame.py` | `read_save` | 339 | AI-assisted | 1 | yes |
| `savegame.py` | `party_names` | 355 | AI-assisted | 1 | yes |
| `savegame.py` | `build_game` | 364 | AI-assisted | 2 | yes |
| `savegame.py` | `load_game` | 380 | AI-assisted | 2 | yes |
| `savegame.py` | `list_saves` | 396 | AI-assisted | 0 | yes |
| `savegame.py` | `save_summary` | 412 | AI-assisted | 1 | yes |
| `test_frodo.py` | `make_test_game` | 21 | (no tag) | 0 | yes |
| `test_frodo.py` | `test_load_dungeon` | 30 | (no tag) | 0 | yes |
| `test_frodo.py` | `test_combat` | 51 | (no tag) | 0 | yes |
| `test_frodo.py` | `test_cards` | 76 | (no tag) | 0 | yes |
| `test_frodo.py` | `check_dungeon` | 110 | (no tag) | 1 | yes |
| `test_frodo.py` | `test_spears` | 141 | (no tag) | 0 | yes |
| `test_frodo.py` | `test_movement` | 173 | (no tag) | 0 | yes |
| `test_frodo.py` | `test_logbook` | 201 | (no tag) | 0 | yes |
| `test_frodo.py` | `hand_names` | 219 | (no tag) | 1 | yes |
| `test_frodo.py` | `test_saves` | 228 | (no tag) | 0 | yes |
| `test_frodo.py` | `test_spears_ahead` | 263 | (no tag) | 0 | yes |
| `test_frodo.py` | `run_tests` | 292 | (no tag) | 0 | yes |
