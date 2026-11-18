# Who owns which function

Generated from the code. Every function was written with AI help and is tagged `AI-assisted:`.
The `[Owner: ...]` after the tag says who on the team must be able to explain it and may rewrite it.
When you rewrite a function yourself, change its tag to `Team-written:` (keep the owner).

| Owner | Area | Functions |
|---|---|---|
| Team | Everyone (the core loop and the tests) | 20 |
| Member 1 | Heroes, cards and the turn | 70 |
| Member 2 | Spears and his armies | 81 |
| Member 3 | The dungeon and saving | 69 |
| AI (no owner) | AI art and interface (stays AI-assisted) | 281 |

## Team - Everyone (the core loop and the tests)

| File | Function | Line | What it does |
|---|---|---|---|
| `frodo_game.py` | `do_request()` | 240 | receives the game, the hero whose turn it is and what the player asked for; carries it out and returns True if the turn is over. |
| `frodo_game.py` | `hero_turn()` | 257 | receives the game and a hero; lets the player walk and play one card until the turn ends; returns how many requests were carried out. |
| `frodo_game.py` | `take_turn()` | 338 | receives the game and one [initiative, tie, kind, name] entry; gives that hero or unit its turn; returns the kind that acted. |
| `frodo_game.py` | `play_round()` | 398 | receives the game; plays one full round (turn order, every hero and enemy unit takes a turn, end of round); returns the number of turns taken. |
| `frodo_game.py` | `finish_game()` | 471 | receives the game and "win", "lose" or "" (quit); writes the summary to the log and shows the end screen; returns True if the player wants to play again. |
| `frodo_game.py` | `open_game()` | 480 | receives the loaded data and what the player chose on the title screen ({"party": [...]} or {"file": name}); returns a ready game, or None if a save could not be loaded. |
| `frodo_game.py` | `choose_game()` | 494 | receives the loaded data; shows the title screens until the player starts a new game or loads one; returns the game (None if they quit). |
| `frodo_game.py` | `main()` | 508 | receives nothing; loads the data, opens the window and runs each game round by round until win, lose or quit (then offers to play again); returns nothing. |
| `test_frodo.py` | `make_test_game()` | 21 | receives nothing; returns a small game with Frodo and Brother Biscuit standing in the first chamber of a freshly dug dungeon, for testing. |
| `test_frodo.py` | `test_load_dungeon()` | 30 | receives nothing; checks that dungeon_data.txt loads fully and a missing file returns None; returns True. |
| `test_frodo.py` | `test_combat()` | 51 | receives nothing; checks draw_modifier, calc_damage, apply_damage and sort_turn_order; returns True. |
| `test_frodo.py` | `test_cards()` | 76 | receives nothing; checks the 3-card hand, choose_card, finish_card, drawing and reshuffling, play_card, walking, is_exhausted, wane_elements and search_poi; returns True. |
| `test_frodo.py` | `check_dungeon()` | 110 | receives a game that has just started; checks the plan, the first chamber's doors and that opening a door carves a reachable chamber; returns True. |
| `test_frodo.py` | `test_spears()` | 141 | receives nothing; checks spears_counter, morale_test, advance_doom, generate_room and coherency; returns True. |
| `test_frodo.py` | `test_movement()` | 173 | receives nothing; checks reachable tiles, walls and pathing; returns True. |
| `test_frodo.py` | `test_logbook()` | 201 | receives nothing; checks check_game_over, write_log and write_summary; returns True. |
| `test_frodo.py` | `hand_names()` | 219 | receives a hero; returns the names of the cards in their hand, deck and discard pile, for comparing. |
| `test_frodo.py` | `test_saves()` | 228 | receives nothing; checks that a game saved to a file loads back the same, and that a broken file gives None; returns True. |
| `test_frodo.py` | `test_spears_ahead()` | 263 | receives nothing; checks that Spears never changes the chamber the party is in, only chambers ahead, and that his preparations appear when one is opened; returns True. |
| `test_frodo.py` | `run_tests()` | 292 | receives nothing; runs every test and prints the results; returns how many passed. |

## Member 1 - Heroes, cards and the turn

| File | Function | Line | What it does |
|---|---|---|---|
| `frodo_game.py` | `install_room()` | 31 | receives the game and a freshly generated room; adds its units to the map, makes it the chamber the party is in and returns its name. |
| `frodo_game.py` | `catch_breath()` | 50 | receives the game; when a new chamber opens every standing hero heals; returns how many heroes healed. |
| `frodo_game.py` | `enter_room()` | 61 | receives the game and the number of the chamber behind the door just opened; Spears carves and fills it from his memory of the party; returns the room's name. |
| `frodo_game.py` | `start_dungeon()` | 78 | receives the game; plans and digs the dungeon and puts the party in the first chamber; returns how many chambers were planned. |
| `frodo_game.py` | `spring_trap()` | 89 | receives the game and the hero who triggered a trap; hurts the hero, pushes the Doom Track and returns the damage. |
| `frodo_game.py` | `open_chest()` | 102 | receives the game, the hero and the best rarity allowed; gives the hero an item, applies it and returns the item's name. |
| `frodo_game.py` | `step_on_tile()` | 117 | receives the game and a hero who just stopped moving; resolves the chest, shrine, trap or door under the hero; returns the tile letter. |
| `frodo_game.py` | `hero_move()` | 138 | receives the game, a hero and the tile to move to; walks the hero there tile by tile (sliding smoothly on screen), using up moves; returns how many tiles were moved. |
| `frodo_game.py` | `record_hit()` | 155 | receives the game, the attack action and the damage; updates the stats and Spears's memory; returns the memory key used. |
| `frodo_game.py` | `hero_attack()` | 167 | receives the game, a hero, the attack action, its strength and the target tile; resolves the attack and returns the damage dealt. |
| `frodo_game.py` | `hero_heal()` | 190 | receives the game, the healer, the heal strength and the target tile; heals the hero there and returns how much was healed. |
| `frodo_game.py` | `strike_style()` | 202 | receives a hero and the attack card they play; returns how the attack looks on screen: "melee", "arrow", "bolt" or "ranged". |
| `frodo_game.py` | `play_card()` | 213 | receives the game, a hero, the name of a card in their hand and the target tile; plays the card's action there and returns the action kind. |
| `frodo_game.py` | `use_menu()` | 271 | receives the game and a menu choice made during a turn ("rules", "status", "save" or "quit"); shows or does it; returns the choice. |
| `frodo_game.py` | `damage_words()` | 286 | receives each hero's health before an enemy attacked and the game; returns words like "hits Pip for 3, Frodo for 2" (or "misses"). |
| `frodo_game.py` | `health_now()` | 298 | receives the game; returns a dictionary of every hero's health right now. |
| `frodo_game.py` | `spears_phase()` | 306 | receives the game and one enemy unit; runs its phases Move, Shoot, Charge, Fight, Morale while the screen shows each step; returns the damage it dealt. |
| `frodo_game.py` | `start_round()` | 358 | receives the game; resets the things that only last one round and returns the new round number. |
| `frodo_game.py` | `save_game()` | 367 | receives the game; asks the player to type a file name and saves the whole game to name.sav; returns True if it was saved. |
| `frodo_game.py` | `set_initiative()` | 380 | receives the game and a hero; rolls the hero's turn order for this round (speed plus a small random roll); returns it. |
| `frodo_game.py` | `prepare_heroes()` | 386 | receives the game; rolls turn order for every standing hero and every enemy unit; returns how many heroes will act. |
| `frodo_game.py` | `cleanup_cards()` | 416 | receives the game; clears the bonuses that only last one round (shields); returns how many heroes were reset. |
| `frodo_game.py` | `mark_exhausted()` | 426 | receives the game; marks every hero with no hp or too few cards as exhausted; returns how many heroes still stand. |
| `frodo_game.py` | `count_clumping()` | 439 | receives the game; counts heroes standing next to another hero and tells Spears's memory; returns that count. |
| `frodo_game.py` | `end_round()` | 453 | receives the game; runs the end of the round (shields wear off, elements wane, exhaustion, Spears's reinforcements, Doom +1, log file); returns the Doom Track value. |
| `cards.py` | `find_card()` | 7 | receives a list of cards and a card name; returns that card, or None if it is not there. |
| `cards.py` | `choose_card()` | 15 | receives a hero and a card name; takes that card out of the hand and returns it (None if it is not in the hand). |
| `cards.py` | `finish_card()` | 23 | receives a hero and the card they just played; puts it on the discard pile and draws a new card; returns how many cards are now in hand. |
| `cards.py` | `draw_card()` | 29 | receives a hero; moves the top card of their deck into their hand (shuffling the discard pile back into the deck first if the deck is empty); returns the card drawn, or None. |
| `cards.py` | `refill_hand()` | 43 | receives a hero; draws cards until they hold HAND_SIZE (or run out); returns how many cards are in hand. |
| `cards.py` | `is_exhausted()` | 51 | receives a hero; returns True if the hero has no hp left. |
| `cards.py` | `heal_hero()` | 56 | receives a hero and a heal amount; raises hp (not past max) and returns how much was healed. |
| `cards.py` | `use_element()` | 65 | receives the elements dictionary and an element name; if it is glowing, uses it up and returns 1 (bonus), otherwise starts it glowing and returns 0. |
| `cards.py` | `wane_elements()` | 76 | receives the elements dictionary; lowers every glowing element by 1 and returns how many are still glowing. |
| `cards.py` | `search_poi()` | 87 | receives the searching hero, the item list and the best rarity allowed; adds a random item to the hero and returns it (None if nothing fits). |
| `cards.py` | `cheese_feast()` | 100 | receives the game and a heal amount; Frodo heals that much, everyone else heals 1; returns a message. |
| `cards.py` | `apply_item()` | 112 | receives the game, a hero and an item; applies the item's effect and returns a message about it. |
| `combat.py` | `build_modifier_deck()` | 5 | receives nothing; returns a shuffled list of 20 attack modifier cards. |
| `combat.py` | `draw_modifier()` | 16 | receives a modifier deck and its discard pile; returns the card drawn (like "+1", "x2" or "null"). |
| `combat.py` | `calc_damage()` | 30 | receives the base attack, the modifier card and the target's shield; returns the damage dealt (never below 0). |
| `combat.py` | `apply_damage()` | 47 | receives a hero or enemy model dictionary and a damage number; lowers its hp and returns the hp left. |
| `combat.py` | `roll_attack()` | 55 | receives the game, "hero" or "enemy", the base attack and the shield; draws a modifier and returns [damage, modifier]. |
| `combat.py` | `sort_turn_order()` | 66 | receives the heroes and enemy units; returns a list of [initiative, tie, kind, name] sorted lowest first. |
| `logbook.py` | `say()` | 4 | receives the game and a sentence; adds it to the on-screen log and this round's file log; returns the sentence. |
| `logbook.py` | `note()` | 11 | receives the game and a sentence the party cannot see happening; writes it only to the file log; returns the sentence. |
| `logbook.py` | `tell()` | 17 | receives the game, whether the party can see the event, and a sentence; shows it on screen only if visible, but always logs it to the file; returns the sentence. |
| `logbook.py` | `add_float()` | 24 | receives the game, a tile, some text and a color name; asks the screen to float that text over the tile. |
| `logbook.py` | `add_banner()` | 30 | receives the game and a sentence; asks the screen to show it as a Spears banner; returns the sentence. |
| `logbook.py` | `start_log()` | 36 | receives the list of hero names; starts a fresh frodo_log.txt and returns True if the file could be written. |
| `logbook.py` | `write_log()` | 48 | receives this round's sentences and the round number; appends them to frodo_log.txt and returns how many lines were written. |
| `logbook.py` | `write_summary()` | 63 | receives the stats dictionary; works out the averages, appends the summary to frodo_log.txt and returns the summary dictionary. |
| `logbook.py` | `summary_lines()` | 83 | receives the summary dictionary; returns the list of sentences shown at the end and written to the log. |
| `logbook.py` | `check_game_over()` | 98 | receives the heroes, the Doom Track, its end and whether the Warlord is dead; returns "win", "lose" or "" (keep playing). |
| `logbook.py` | `status_lines()` | 112 | receives the game; returns a list of sentences describing the party, the room and the Doom Track. |
| `logbook.py` | `hero_line()` | 124 | receives a hero; returns one sentence with the hero's hp, cards and items. |
| `game_data.py` | `clean_value()` | 8 | receives one value from the data file; returns an int if it is a number, otherwise the text with _ turned into spaces. |
| `game_data.py` | `parse_fields()` | 16 | receives text like "move=3 role=melee"; returns a dictionary such as {"move": 3, "role": "melee"}. |
| `game_data.py` | `parse_action()` | 26 | receives text like "attack:3:1"; returns an action dictionary with kind, amount and range. |
| `game_data.py` | `make_card()` | 38 | receives the hero name and the fields of a CARD line; returns a card dictionary with its one action. |
| `game_data.py` | `store_record()` | 46 | receives the data so far, a record kind, its name and its fields; stores it in the right place and returns the kind. |
| `game_data.py` | `read_line()` | 71 | receives the data so far and one line of the file; stores the line if it is a record and returns True if it was one. |
| `game_data.py` | `load_dungeon()` | 88 | receives the data file name; returns a dictionary of units, styles, the dungeon plan settings, the arena drawing, cards, items, heroes and settings, or None if the file cannot be opened. |
| `game_data.py` | `make_hero()` | 102 | receives the loaded data and a hero name; returns a fresh hero dictionary with a full hand of cards. |
| `game_data.py` | `new_memory()` | 120 | receives nothing; returns Spears's memory dictionary with every count at 0. |
| `game_data.py` | `new_stats()` | 126 | receives nothing; returns the stats dictionary used for the end summary, all at 0. |
| `game_data.py` | `find_level()` | 132 | receives the loaded data and a difficulty name; returns that DIFFICULTY record (Normal if the name is unknown). |
| `game_data.py` | `apply_level()` | 140 | receives a new game and a difficulty record; makes heroes tougher or frailer, the Doom Track longer or shorter and enemies hit harder or softer; returns the difficulty name. |
| `game_data.py` | `new_game()` | 151 | receives the loaded data, the list of chosen hero names and the difficulty name; returns the whole starting game dictionary. |
| `game_data.py` | `find_hero()` | 171 | receives the game and a hero name; returns that hero's dictionary, or None. |
| `game_data.py` | `place_party()` | 179 | receives the game and the room's start tiles; stands each living hero on one and returns how many were placed. |

## Member 2 - Spears and his armies

| File | Function | Line | What it does |
|---|---|---|---|
| `spears_ai.py` | `spears_counter()` | 31 | receives Spears's memory dictionary; returns the party habit he will punish next: "melee", "ranged", "loot", "clump", "rest" or "none". |
| `spears_ai.py` | `fade_memory()` | 44 | receives Spears's memory; halves every count so newer habits matter more; returns the memory. |
| `spears_ai.py` | `unit_plan()` | 51 | receives the habit to counter, how far along the main path this chamber is and its kind; returns the list of unit type names Spears deploys. |
| `spears_ai.py` | `pick_style()` | 72 | receives the room styles and the habit to counter; returns a random style that matches (or any normal style). |
| `spears_ai.py` | `build_dungeon()` | 86 | receives the game; plans the whole dungeon, starts the map as solid rock and carves the boss arena (its outline is known from the start); returns how many chambers were planned. |
| `spears_ai.py` | `boss_chamber()` | 108 | receives the game; returns the boss arena's chamber dictionary. |
| `spears_ai.py` | `chamber_at()` | 116 | receives the game and a tile; returns the chamber whose zone holds that tile, or None. |
| `spears_ai.py` | `door_at()` | 124 | receives the game and a tile; returns the door record {"tile", "from", "to"} on that tile, or None. |
| `spears_ai.py` | `place_letters()` | 132 | receives the map grid, the list of free floor tiles, a tile letter and a count; puts that letter on random free tiles (removing them from the list); returns how many were placed. |
| `spears_ai.py` | `furnish()` | 142 | receives the game, the new room, its style and the habit to counter; fills the chamber with chests, traps, cover and shrines, twisted to punish that habit (side chambers get an extra chest); returns how many floor tiles are still empty. |
| `spears_ai.py` | `deploy_room()` | 168 | receives the game, the new room and the habit to counter; Spears deploys his units in the far half of the chamber; returns how many units were placed. |
| `spears_ai.py` | `add_unit()` | 183 | receives the game, a room, a unit type, a spawn tile and the tiles already taken; makes the unit, stands it around the spawn and adds it to the room; returns the unit (None if no model fitted). |
| `spears_ai.py` | `deploy_boss()` | 195 | receives the game and the boss arena room; stands the Warlord at his mark and his guards at theirs; returns how many units were placed. |
| `spears_ai.py` | `place_exits()` | 207 | receives the game and a freshly carved chamber; puts a sealed door in its wall towards every chamber that branches off it; returns the door to the main path (or None). |
| `spears_ai.py` | `nearest_tile()` | 226 | receives a list of tiles and a point; returns the tile closest to the point. |
| `spears_ai.py` | `connect_chamber()` | 235 | receives the game and the chamber being entered; digs a corridor from the door that leads to it and swings that door open for good; returns the door tile, or None for the first chamber. |
| `spears_ai.py` | `make_unit()` | 246 | receives the data, a unit type name and a unit number; returns a new unit dictionary with no models placed yet. |
| `spears_ai.py` | `place_models()` | 258 | receives the grid, a unit, a spawn tile and the tiles already taken; stands the unit's models on and around the spawn; returns how many were placed. |
| `spears_ai.py` | `generate_room()` | 270 | receives the game, the number of the chamber being opened and the party habit Spears wants to counter; carves the chamber (the arena is already carved), furnishes it and deploys his units; returns the room dictionary. |
| `spears_ai.py` | `find_unit()` | 308 | receives the unit list and a unit name; returns that unit, or None if it has been destroyed. |
| `spears_ai.py` | `unit_visible()` | 316 | receives the game and a unit; returns True if the party can see at least one of its models right now. |
| `spears_ai.py` | `pick_initiative()` | 324 | receives a unit; returns a random activation initiative that suits its role (fast units go early, heavy ones late). |
| `spears_ai.py` | `pick_target()` | 336 | receives the game and a unit; returns the hero Spears wants dead most (weak and close), or None if no hero stands. |
| `spears_ai.py` | `coherency_ok()` | 352 | receives a unit, one of its models and a tile; returns True if the model would be within 2 tiles of another model of the unit there. |
| `spears_ai.py` | `goal_tile()` | 364 | receives the game, a unit and its target hero; returns the tile the unit heads for (heavy units hold the door until heroes come close). |
| `spears_ai.py` | `is_flank()` | 373 | receives the game, a unit and a tile next to its goal; returns True if another enemy model stands on the opposite side (a flank). |
| `spears_ai.py` | `ranged_score()` | 380 | receives the distance to the target and the shooting range; returns a score (low is good) for keeping a safe shooting distance. |
| `spears_ai.py` | `tile_score()` | 390 | receives the game, a unit, a tile and the step map from the goal; returns how good that tile is (low is good). |
| `spears_ai.py` | `best_tile()` | 403 | receives the game, a unit, one model, the step map from the goal and a move limit; returns the best tile that keeps coherency. |
| `spears_ai.py` | `move_unit()` | 424 | receives the game, a unit, its target hero and a move limit; moves every model toward the goal (remembering where each came from, for the animation); returns how many models moved. |
| `spears_ai.py` | `choose_victim()` | 438 | receives the game, a model, its reach and the unit's target; returns the hero this model attacks (the target if in reach, else the weakest in reach, else None). |
| `spears_ai.py` | `cover_bonus()` | 451 | receives the game, the attacking unit and the hero; returns 1 if the hero is behind cover from a shot, else 0. |
| `spears_ai.py` | `hero_falls()` | 459 | receives the game and a hero with no hp; marks the hero exhausted and returns a message. |
| `spears_ai.py` | `splash()` | 467 | receives the game, an area-attack unit and the hero it hit; deals 1 damage to heroes next to that hero; returns how many were splashed. |
| `spears_ai.py` | `feel_hit()` | 484 | receives the game, a hero who was just hit, the damage and the modifier card; asks the screen to flash the hero's portrait, and to shake on a big hit; returns the damage. |
| `spears_ai.py` | `unit_attack()` | 493 | receives the game, a unit, one of its models and a hero; resolves one enemy attack and returns the damage dealt. |
| `spears_ai.py` | `unit_shoot()` | 518 | receives the game, a ranged unit and its target; every model in range shoots; returns the total damage. |
| `spears_ai.py` | `touching_hero()` | 528 | receives the game and a unit; returns True if any of its models stands next to a hero. |
| `spears_ai.py` | `nearest_gap()` | 537 | receives a unit and its target hero; returns how many tiles the closest model must cross to stand next to the hero. |
| `spears_ai.py` | `unit_charge()` | 547 | receives the game, a melee unit and its target; rolls a charge distance and moves in if it is enough; returns True on a successful charge. |
| `spears_ai.py` | `unit_fight()` | 564 | receives the game, a unit and its target; every model next to a hero attacks; returns the total damage. |
| `spears_ai.py` | `morale_test()` | 576 | receives a unit's leadership and a 2d6 roll; returns True if the unit holds (roll is leadership or less). |
| `spears_ai.py` | `check_room_clear()` | 581 | receives the game and a chamber number; if none of that chamber's units are left, unseals all its doors and returns True. |
| `spears_ai.py` | `destroy_unit()` | 602 | receives the game, a unit with no models left and the tile where it fell; removes the unit, maybe drops loot, and returns True if loot dropped. |
| `spears_ai.py` | `remove_model()` | 616 | receives the game, a unit and a dead or fleeing model; removes the model and returns how many models the unit has left. |
| `spears_ai.py` | `safest_tile()` | 627 | receives the game, a model and a move limit; returns the reachable tile farthest from every hero. |
| `spears_ai.py` | `fall_back()` | 644 | receives the game and a broken unit; every model runs away from the heroes (remembering where each came from, for the animation); returns how many models moved. |
| `spears_ai.py` | `break_unit()` | 656 | receives the game and a unit that failed morale; it randomly loses a model or falls back; returns what happened. |
| `spears_ai.py` | `unit_morale()` | 672 | receives the game and a unit; if it is below half strength it rolls 2d6 against leadership; returns True if the unit holds. |
| `spears_ai.py` | `advance_doom()` | 690 | receives the Doom Track value, how much to add and the track's end; returns the new value (never past the end). |
| `spears_ai.py` | `prepare_ahead()` | 698 | receives the game and a chamber the party has not opened yet; Spears secretly adds a trap, a guard or a trapped chest to it; returns what he added. |
| `spears_ai.py` | `reinforce()` | 706 | receives the game; after a round Spears may secretly strengthen one chamber the party has not opened yet (never the one they are in); returns what he added ("" if he waits). |
| `spears_ai.py` | `apply_preparations()` | 722 | receives the game, a freshly carved room and its chamber; puts in the traps, guards and trapped chests Spears prepared; returns how many were added. |
| `spears_ai.py` | `warlord()` | 744 | receives the game; returns the Warlord's unit if he is on the map, else None. |
| `spears_ai.py` | `summon_guards()` | 752 | receives the game and the Warlord; his guards rush in at the free guard marks of the arena; returns a message. |
| `spears_ai.py` | `enrage()` | 766 | receives the Warlord; he grows stronger and faster; returns a message. |
| `spears_ai.py` | `boss_check()` | 773 | receives the game and a unit that was just hit; if it is the Warlord, moves him into his next phase at half and at a quarter of his wounds; returns the phase he is in (0, 1 or 2). |
| `movement.py` | `tile_distance()` | 11 | receives two tiles; returns how many up/down/left/right steps apart they are. |
| `movement.py` | `in_bounds()` | 16 | receives the grid and a col/row; returns True if that spot is inside the room. |
| `movement.py` | `is_floor()` | 21 | receives the grid, a col/row and whether sealed doors count as open; returns True if someone can stand there. |
| `movement.py` | `blank_grid()` | 34 | receives the grid and a value; returns a new grid of the same size filled with that value. |
| `movement.py` | `can_enter()` | 45 | receives the grid, the step counts so far, a tile and the blocked tiles; returns True if the search may step onto it. |
| `movement.py` | `step_map()` | 54 | receives the grid, a start tile and blocked tiles; returns a grid of step counts from the start (-1 = cannot be reached). |
| `movement.py` | `reachable_tiles()` | 69 | receives the grid, a start tile, a step limit, tiles that block the way and tiles nobody may stop on; returns the list of tiles that can be reached. |
| `movement.py` | `lower_neighbor()` | 81 | receives the step counts and a tile; returns the neighbor tile that is one step closer to the start. |
| `movement.py` | `find_path()` | 92 | receives the grid, a start tile and a goal tile; returns the list of tiles to walk (start first), or [] if there is no way. |
| `movement.py` | `hero_tiles()` | 105 | receives the hero list; returns the tiles of every hero still standing. |
| `movement.py` | `model_tiles()` | 114 | receives the enemy unit list; returns the tile of every enemy model. |
| `movement.py` | `hero_at()` | 123 | receives the hero list and a tile; returns the standing hero on that tile, or None. |
| `movement.py` | `model_at()` | 131 | receives the unit list and a tile; returns [unit, model] for the enemy on that tile, or None. |
| `movement.py` | `learn_outline()` | 140 | receives the game; adds every floor tile, door, throne and brazier of the chambers the party has opened to what it knows (the shape of the rooms, not their contents); returns how many tiles were learned. |
| `movement.py` | `shown_letter()` | 159 | receives a tile letter; returns the letter the party sees there (hidden pits look like floor, trapped chests like chests). |
| `movement.py` | `lit_floor()` | 168 | receives the game; returns a grid marking every tile a standing hero can see: within SIGHT steps on foot, so walls block the view. |
| `movement.py` | `wall_in_view()` | 180 | receives the game, the lit-floor grid and a wall tile; returns True if a lit floor tile touches that wall (so the wall is lit too). |
| `movement.py` | `refresh_vision()` | 189 | receives the game; works out which tiles the heroes can see right now and remembers what is on them; returns how many tiles are visible. |
| `movement.py` | `enemy_targets()` | 205 | receives the game, a tile and a range; returns the tiles of visible enemy models within range. |
| `movement.py` | `friend_targets()` | 214 | receives the game, a tile and a range; returns the tiles of standing heroes within range. |
| `movement.py` | `move_targets()` | 223 | receives the game and a hero; returns [tiles the hero can walk to with the moves left this turn, steps to each]. |
| `movement.py` | `action_targets()` | 235 | receives the game, a hero and a card's action; returns the list of tiles that card can be dropped on. |
| `movement.py` | `is_valid_drop()` | 245 | receives the tile under the mouse and the allowed tiles; returns True if the drop is allowed. |
| `movement.py` | `drop_message()` | 250 | receives the game, a hero, the card's action (None for walking) and the bad drop tile; returns a friendly message saying why it did not work. |

## Member 3 - The dungeon and saving

| File | Function | Line | What it does |
|---|---|---|---|
| `chambers.py` | `blank_map()` | 18 | receives a width and height in tiles; returns a new map grid that is solid rock everywhere. |
| `chambers.py` | `zone_box()` | 26 | receives the map grid and a zone [x, y, width, height]; returns [left, top, right, bottom], the tiles a chamber may use (always leaving a wall around it). |
| `chambers.py` | `box_center()` | 35 | receives a box [left, top, right, bottom]; returns the tile in its middle. |
| `chambers.py` | `shrink_box()` | 40 | receives a box [left, top, right, bottom]; returns a randomly smaller box inside it, so chambers differ in size and position. |
| `chambers.py` | `box_tiles()` | 51 | receives a box [left, top, right, bottom]; returns the list of every tile inside it. |
| `chambers.py` | `cell_zone()` | 62 | receives the DUNGEON settings and a list of cells [cx, cy]; returns the zone [x, y, width, height] that covers all of them. |
| `chambers.py` | `cell_neighbors()` | 78 | receives the DUNGEON settings and a cell; returns the cells next to it (up, down, left, right) that are on the map. |
| `chambers.py` | `touches()` | 89 | receives the DUNGEON settings, a cell and a list of cells; returns True if the cell is next to any of them. |
| `chambers.py` | `boss_block()` | 97 | receives the DUNGEON settings; returns the 4 cells of a random 2 x 2 block for the boss arena. |
| `chambers.py` | `far_cell()` | 104 | receives the DUNGEON settings and the boss cells; returns a random cell among those farthest from the boss (where the party starts). |
| `chambers.py` | `random_walk()` | 123 | receives the DUNGEON settings, the start cell, the boss cells and a wanted length; walks at random from the start and returns the path if it ends next to the boss at that length, else []. |
| `chambers.py` | `main_path()` | 139 | receives the DUNGEON settings, the boss cells and the start cell; returns a random main path of cells (as close to the wanted length as possible), or [] if none was found. |
| `chambers.py` | `make_chamber()` | 150 | receives a chamber number, its kind ("start", "main", "side" or "boss"), its cells, its parent's number and the DUNGEON settings; returns a new, not yet carved chamber dictionary. |
| `chambers.py` | `add_sides()` | 157 | receives the DUNGEON settings, the plan so far, the main path and the boss cells; adds side chambers in free cells next to the main path; returns how many were added. |
| `chambers.py` | `plan_dungeon()` | 180 | receives the DUNGEON settings; plans the whole dungeon at random (main path, side chambers and boss arena); returns the list of chambers (number 0 is where the party starts). |
| `chambers.py` | `children()` | 203 | receives the plan and a chamber number; returns the chambers whose door is in that chamber's wall. |
| `chambers.py` | `owner_grid()` | 212 | receives the map grid and the plan; returns a grid saying which chamber's zone each tile is in (-1 = no chamber). |
| `chambers.py` | `shape_ell()` | 225 | receives a box; returns its tiles with one random corner block cut away (an L-shaped room). |
| `chambers.py` | `shape_round()` | 240 | receives a box; returns its tiles with the corners clipped off (a rounded room). |
| `chambers.py` | `shape_cross()` | 254 | receives a box; returns the tiles of a plus-shaped room (a wide bar across and a wide bar down). |
| `chambers.py` | `shape_cave()` | 271 | receives a box; returns its tiles with random bites taken out of the edge (a rough cave). |
| `chambers.py` | `connected()` | 281 | receives a list of floor tiles; returns only the tiles that can be walked to from the first one. |
| `chambers.py` | `shape_tiles()` | 297 | receives a shape name and a box; returns the floor tiles of a chamber of that shape (a plain rectangle if the shape came out too small). |
| `chambers.py` | `is_open_floor()` | 315 | receives the floor tiles and one tile; returns True if all eight tiles around it are floor too (a safe spot for a pillar). |
| `chambers.py` | `add_pillars()` | 324 | receives the floor tiles and how many pillars to try for; turns that many open floor tiles back into rock without cutting the room in two; returns how many were placed. |
| `chambers.py` | `carve_chamber()` | 341 | receives the map grid, a zone and a room style; carves a random chamber of that style into the rock; returns its floor tiles. |
| `chambers.py` | `carve_arena()` | 351 | receives the map grid, the boss zone and the arena drawing from dungeon_data.txt; carves the throne hall into the middle of the zone; returns [floor tiles, markers] (markers: "W" warlord, "G" guard spawn spots). |
| `chambers.py` | `inside()` | 375 | receives the map grid and a col/row; returns True if a door or corridor may be there (not on the map's outer edge). |
| `chambers.py` | `open_sides()` | 380 | receives the map grid and a tile; returns how many of the four tiles next to it are not rock. |
| `chambers.py` | `pick_door()` | 391 | receives the map grid, a chamber's floor tiles and a point to aim at; returns the wall tile for a door (closest to the aim), or None. |
| `chambers.py` | `can_dig()` | 409 | receives the map grid, the dig search so far, a tile and the dig rules (door, goal tiles, owner grid, allowed chambers, strict); returns True if the corridor may pass through this rock tile. |
| `chambers.py` | `find_corridor()` | 425 | receives the map grid and the dig rules; returns the list of rock tiles to dig from the door to the new chamber ([] if there is no way). |
| `chambers.py` | `dig_corridor()` | 447 | receives the map grid, the door, the new chamber's tiles, the owner grid and the chamber numbers the corridor may cross; digs the corridor and returns its tiles. |
| `chambers.py` | `far_cluster()` | 463 | receives floor tiles, a point and a count; returns that many tiles huddled together as far from the point as possible (where the party starts). |
| `chambers.py` | `far_tiles()` | 481 | receives floor tiles and a point; returns the tiles in the far half of the chamber from that point (where Spears deploys). |
| `savegame.py` | `word()` | 21 | receives some text; returns it with spaces turned into _ so it fits in one key=value pair. |
| `savegame.py` | `tile_text()` | 26 | receives a tile [col, row] (or None); returns it written as "col,row" (or "-"). |
| `savegame.py` | `tiles_text()` | 33 | receives a list of tiles; returns them written as "c,r/c,r/..." (or "-" if empty). |
| `savegame.py` | `names_text()` | 43 | receives a list of names; returns them written as "a_b/c_d" (or "-" if empty). |
| `savegame.py` | `card_names()` | 53 | receives a list of cards; returns their names written with names_text(). |
| `savegame.py` | `yes_no()` | 61 | receives True or False; returns "yes" or "no". |
| `savegame.py` | `record()` | 68 | receives a record kind, a name and a list of [key, value] pairs; returns one save-file line. |
| `savegame.py` | `read_tile()` | 78 | receives text like "3,4" (or "-"); returns the tile [3, 4] (or None). |
| `savegame.py` | `read_tiles()` | 87 | receives text like "3,4/5,6" (or "-"); returns the list of tiles. |
| `savegame.py` | `read_names()` | 98 | receives text like "Heroic Yap/Fetch" (or "-"); returns the list of names. |
| `savegame.py` | `is_yes()` | 106 | receives "yes" or "no"; returns True for "yes". |
| `savegame.py` | `game_line()` | 113 | receives the game; returns the GAME line with all the single values (round, doom, chamber, ...). |
| `savegame.py` | `hero_line()` | 126 | receives a hero; returns their HERO line (health, place, stats, cards and items). |
| `savegame.py` | `chamber_line()` | 136 | receives a planned chamber; returns its CHAMBER line. |
| `savegame.py` | `unit_line()` | 154 | receives an enemy unit; returns its UNIT line (stats, chamber and every model's tile and wounds). |
| `savegame.py` | `number_line()` | 167 | receives a record kind and a dictionary of whole numbers (memory, stats, elements); returns its line. |
| `savegame.py` | `raw_line()` | 175 | receives a record kind, a name and some text; returns a line that keeps the text exactly (for modifier decks and the log). |
| `savegame.py` | `map_lines()` | 180 | receives a record kind and a grid of letters; returns one line per row. |
| `savegame.py` | `save_lines()` | 188 | receives the game; returns every line of its save file. |
| `savegame.py` | `save_game()` | 211 | receives the game and a file name (without .sav); writes the whole game to name.sav; returns True if it worked. |
| `savegame.py` | `find_in_deck()` | 225 | receives the loaded data, a hero name and a card name; returns that hero's card dictionary. |
| `savegame.py` | `read_pile()` | 233 | receives the loaded data, a hero name and a list of card names as text; returns the list of cards. |
| `savegame.py` | `load_hero()` | 241 | receives the game, the data, a hero name and the fields of their HERO line; puts the saved values on that hero; returns the hero. |
| `savegame.py` | `load_chamber()` | 255 | receives the game, the data, a chamber number and the fields of its CHAMBER line; adds that chamber to the plan; returns it. |
| `savegame.py` | `load_unit()` | 275 | receives the game, the data, a unit name and the fields of its UNIT line; rebuilds the unit with its models; returns it. |
| `savegame.py` | `load_game_line()` | 290 | receives the game and the fields of the GAME line; puts the saved single values back; returns the round number. |
| `savegame.py` | `load_raw()` | 306 | receives the game and a GRID, KNOWN, MODS or LOG record; puts it back; returns the kind. |
| `savegame.py` | `load_record()` | 321 | receives the game, the data and one parsed key=value record; puts it back in the right place; returns the kind. |
| `savegame.py` | `read_save()` | 342 | receives a save name (without .sav); returns the list of its lines split into [kind, name, rest], or None if the file cannot be opened. |
| `savegame.py` | `party_names()` | 358 | receives the records of a save file; returns the names of the heroes in it. |
| `savegame.py` | `build_game()` | 367 | receives the loaded data and the records of a save file; builds the whole game from them; returns the game. |
| `savegame.py` | `load_game()` | 383 | receives the loaded data and a save name (without .sav); returns the saved game, or None if the file is missing or damaged. |
| `savegame.py` | `list_saves()` | 399 | receives nothing; returns the names of the .sav files in this folder, newest first. |
| `savegame.py` | `save_summary()` | 415 | receives a save name; returns a short line about it, like "round 12 - Kennel - 4 of 12 chambers" ("" if it cannot be read). |

## AI art and interface - AI art and interface (stays AI-assisted)

| File | Function | Line | What it does |
|---|---|---|---|
| `ui.py` | `init()` | 68 | receives nothing; opens the 1280x720 window (scaled to fit the screen), builds the art and returns the screen surface. |
| `ui.py` | `set_message()` | 81 | receives a sentence; shows it in the message bar under the map and returns it. |
| `ui.py` | `tile_rect()` | 87 | receives a tile [col, row]; returns its rectangle - on the map picture while the map is being painted, otherwise on the screen (zoomed and panned). |
| `ui.py` | `tile_center()` | 100 | receives a tile [col, row]; returns the [x, y] pixel at its middle. |
| `ui.py` | `tile_at()` | 106 | receives a mouse position; returns the dungeon tile under it (taking zoom and panning into account), or None if it is off the map. |
| `ui.py` | `hero_block_rect()` | 118 | receives a hero's place in the party (0 = Frodo); returns that hero's panel rectangle on the left. |
| `ui.py` | `card_rect()` | 123 | receives a hand card number (0-2); returns its rectangle in the bottom strip. |
| `ui.py` | `hero_at_pixel()` | 128 | receives the game and a mouse position; returns the hero whose portrait or token is there, or None. |
| `ui.py` | `moved_far()` | 139 | receives where a drag started and where it ended; returns True if the mouse really moved (a drag, not a click). |
| `ui.py` | `selected_hero()` | 144 | receives the game; returns the hero whose turn it is (whose cards are shown at the bottom), or None. |
| `ui.py` | `find_by_name()` | 151 | receives a list of heroes or units and a name; returns the one with that name, or None. |
| `ui.py` | `make_button()` | 161 | receives an id, a label and a rectangle; returns a button dictionary. |
| `ui.py` | `set_buttons()` | 166 | receives a list of [id, label]; lays them out at the foot of the right panel (the first one wide on top, the rest two per row) and returns the button list. |
| `ui.py` | `button_at()` | 178 | receives a list of buttons and a mouse position; returns the id of the button there, or "". |
| `ui.py` | `tile_letter()` | 188 | receives the game and a col/row; returns the letter the party SEES there: the real tile if a hero can see it, otherwise what they remember. |
| `ui.py` | `min_zoom()` | 197 | receives nothing; returns the smallest zoom, where the whole dungeon fits in the map window. |
| `ui.py` | `clamp_camera()` | 204 | receives nothing; keeps the zoom in range and the camera over the dungeon; returns the zoom. |
| `ui.py` | `view_rect()` | 217 | receives nothing; returns the part of the dungeon picture (in map pixels) that the map window shows. |
| `ui.py` | `visible_box()` | 224 | receives nothing; returns [left, top, right, bottom], the tiles that are (at least partly) in the map window. |
| `ui.py` | `tile_middle()` | 234 | receives a tile; returns the map-pixel point at its middle. |
| `ui.py` | `follow()` | 239 | receives a tile; glides the camera there if that tile is near the edge of the map window or off it; returns True if the camera moves. |
| `ui.py` | `frame_tiles()` | 250 | receives a list of tiles and the biggest zoom allowed; glides the camera (and zoom) to show all of them; returns the new zoom goal. |
| `ui.py` | `show_chamber()` | 270 | receives the game and a newly opened chamber's tiles; glides the camera to show the chamber and the party; returns the zoom goal. |
| `ui.py` | `fit_view()` | 276 | receives the game; glides the camera out to show every part of the dungeon the party knows about; returns the zoom goal. |
| `ui.py` | `zoom_by()` | 286 | receives a zoom factor and a screen point; zooms in or out keeping the dungeon point under that screen point still; returns the new zoom. |
| `ui.py` | `glide_camera()` | 299 | receives nothing; moves the camera a little toward its goal each frame and pans with WASD; returns nothing. |
| `ui.py` | `camera_event()` | 322 | receives the game and one event; handles mouse-wheel zoom, right-drag panning and the Home / + / - keys; returns True if the event was used up by the camera. |
| `ui.py` | `camera_key()` | 344 | receives the game and a key; Home fits the whole known dungeon, + and - zoom; returns True if the key was a camera key. |
| `ui.py` | `seen_letters()` | 358 | receives the game; returns a grid of the letters the party sees on every tile (real where lit, remembered where dark). |
| `ui.py` | `room_art()` | 369 | receives the game and the letters the party sees; returns the painted dungeon picture, repainting it only when the known walls change. |
| `ui.py` | `draw_features()` | 384 | receives the game and the letters the party sees; draws the chests, traps, shrines, cover, doors, throne and braziers in the map window; returns how many were drawn. |
| `ui.py` | `draw_ripples()` | 404 | receives the game and the room picture; now and then starts a drip ring on a puddle the heroes can see, and draws the rings; returns how many rings are alive. |
| `ui.py` | `draw_highlights()` | 417 | receives nothing; makes every tile you can use glow in the color of what would happen there (blue walk, red attack, green heal), with the step count on walking tiles; returns how many there are. |
| `ui.py` | `light_sources()` | 431 | receives the game; returns the light sources [col, row, strength]: every standing hero's torch, and every brazier the party can see. |
| `ui.py` | `draw_flames()` | 444 | receives the game, the dungeon picture and the light sources; draws the flames of the wall torches and braziers the heroes can see; returns how many burn. |
| `ui.py` | `draw_lighting()` | 461 | receives the game and the dungeon picture; multiplies the map window by the light (warm near heroes and braziers, cold dark elsewhere) and lights the flames; returns how many flames burn. |
| `ui.py` | `visible_models()` | 472 | receives the game and a unit; returns the unit's models that a hero can see right now. |
| `ui.py` | `draw_coherency()` | 481 | receives the visible models of one unit; draws a faint outline around them to show they are one unit; returns nothing. |
| `ui.py` | `draw_model_token()` | 492 | receives an enemy unit and one of its models; draws the model with its wounds; returns nothing. |
| `ui.py` | `draw_figures()` | 503 | receives the game; draws every visible enemy and hero in the map window, row by row from the back of the room to the front, so nearer figures overlap farther ones; returns how many were drawn. |
| `ui.py` | `draw_hero_token()` | 522 | receives the game and a hero; draws the hero on the map with a pulsing ring if it is their turn; returns nothing. |
| `ui.py` | `draw_cursor()` | 537 | receives nothing; draws the keyboard cursor on the map when the arrow keys are in use; returns nothing. |
| `ui.py` | `paint_world()` | 545 | receives the game, the letters the party sees and the dungeon picture; paints the part of the dungeon in view (floor, walls, objects, figures) at full size onto a scratch picture; returns that picture. |
| `ui.py` | `show_map()` | 567 | receives the game; draws the dungeon in the map window: the painted rooms zoomed and panned, then real light and darkness, then glows and markers; returns how many tiles are in view. |
| `ui.py` | `draw_zoom_hint()` | 597 | receives nothing; writes the camera controls and the zoom level in the map window's corner; returns nothing. |
| `ui.py` | `draw_boss_bar()` | 606 | receives the game; once the Warlord is in sight, shows his name, health and phase at the top of the map window; returns True if it was shown. |
| `ui.py` | `tooltip_lines()` | 623 | receives the game and the tile under the mouse; returns the lines of help to show about what is there ([] if nothing). |
| `ui.py` | `card_tip()` | 643 | receives a card; returns the lines that explain exactly what it does. |
| `ui.py` | `tracker_tip()` | 667 | receives the game and one turn-order entry; returns the lines that explain it. |
| `ui.py` | `element_tip()` | 679 | receives the game and an element number (0 fire, 1 frost, 2 light); returns the lines that explain that orb. |
| `ui.py` | `hero_tip()` | 689 | receives a hero; returns the lines that explain their panel. |
| `ui.py` | `panel_tip()` | 698 | receives the game and the mouse position; returns the tooltip lines for whatever panel, card, orb or bar is under it ([] if none). |
| `ui.py` | `draw_tooltip()` | 723 | receives the game; shows a small note about the hero, enemy, feature, card or panel under the mouse; returns how many lines were shown. |
| `ui.py` | `draw_doom()` | 751 | receives the game; draws the Doom Track as a crimson bar with a skull every 10 steps; returns the Doom value. |
| `ui.py` | `draw_elements()` | 765 | receives the game; draws the fire, frost and light medallions (bright = strong, dim ring = waning, dark = gone); returns nothing. |
| `ui.py` | `draw_tracker_entry()` | 784 | receives the game, one [initiative, tie, kind, name] entry and an x position; draws its medallion and initiative number; returns nothing. |
| `ui.py` | `draw_top_bar()` | 810 | receives the game; draws the round, room, initiative tracker, elements and Doom Track; returns nothing. |
| `ui.py` | `hero_status()` | 828 | receives the game and a hero; returns the short status words shown on the hero's panel. |
| `ui.py` | `draw_portrait()` | 840 | receives a hero and the hero's panel rectangle; draws the framed portrait; returns nothing. |
| `ui.py` | `hurt_amount()` | 847 | receives a hero; returns how strongly their panel should flash red right now (1 just hit, fading to 0). |
| `ui.py` | `draw_hero_block()` | 857 | receives the game and a hero's place in the party; draws the hero's panel (portrait, hp bar, deck and discard, status); returns nothing. |
| `ui.py` | `draw_party_panel()` | 883 | receives the game; draws the whole left panel (one block per hero); returns nothing. |
| `ui.py` | `log_color()` | 890 | receives a log sentence; returns the ink color for it (red for Spears and danger, plain otherwise). |
| `ui.py` | `draw_log()` | 898 | receives the game; draws the scrolling combat log on the right; returns how many lines were drawn. |
| `ui.py` | `draw_message()` | 919 | receives nothing; draws the message bar under the map, with Frodo doing the talking; returns nothing. |
| `ui.py` | `dragging_card()` | 930 | receives a hand card number; returns True if that card is being dragged right now. |
| `ui.py` | `draw_pile()` | 936 | receives the acting hero; draws their deck as a small stack of card backs with the deck and discard counts; returns nothing. |
| `ui.py` | `draw_hand()` | 949 | receives the hero whose turn it is; draws their 3 cards (the chosen one lifted in gold, all dimmed once a card is played) and their deck; returns how many cards were drawn. |
| `ui.py` | `phase_hint()` | 972 | receives nothing; returns the lines of help shown in the bottom strip while no hero is taking a turn. |
| `ui.py` | `draw_bottom()` | 978 | receives the game; draws the bottom strip (the acting hero's hand, or hints while enemies act); returns the phase. |
| `ui.py` | `effect_start()` | 993 | receives nothing; returns the frame an effect should start on: now, or when the attacks already on screen have landed. |
| `ui.py` | `add_floater()` | 998 | receives a tile, some words and a color; starts floating text over the tile (after any attack still flying); returns how many floaters exist. |
| `ui.py` | `add_strike()` | 1005 | receives a strike effect from the game (an enemy attack); queues its animation after the ones already playing; returns the frame it ends on. |
| `ui.py` | `consume_fx()` | 1022 | receives the game; turns the effects the game logic asked for into things on screen, in order; returns how many were handled. |
| `ui.py` | `add_feel()` | 1046 | receives a game-feel effect (puff, sparkle, shake or hurt); queues it to start when the attack before it lands; returns the effect kind. |
| `ui.py` | `reset_screen()` | 1060 | receives nothing; clears every effect, caption and banner left from an earlier game; returns nothing. |
| `ui.py` | `fade_list()` | 1069 | receives a list of effects with "start" and "life"; ages the ones that have started and removes the finished ones; returns how many are left. |
| `ui.py` | `draw_mod_card()` | 1079 | receives nothing; flips over and briefly shows the attack modifier card that was just drawn; returns nothing. |
| `ui.py` | `draw_banner()` | 1091 | receives nothing; shows the Spears banner (a crimson ribbon) while it lasts; returns nothing. |
| `ui.py` | `draw_effects()` | 1110 | receives nothing; draws enemy attacks, hit flashes, floating numbers, the modifier card and the banner (each when its turn comes); returns nothing. |
| `ui.py` | `lerp()` | 1135 | receives two points and a fraction 0-1; returns the point that far along the line between them. |
| `ui.py` | `draw_slash()` | 1140 | receives a screen point and how far the slash has got (0-1); draws three crimson claw marks across it; returns nothing. |
| `ui.py` | `draw_strike()` | 1150 | receives one enemy attack and how far it has got (0-1); draws the lunge and slash, the flying stone, or the arcing bomb and its burst; returns nothing. |
| `ui.py` | `draw_puff()` | 1191 | receives a puff of smoke (left by a fallen enemy) and how many frames old it is; draws grey smoke rings drifting up; returns nothing. |
| `ui.py` | `draw_sparkle()` | 1203 | receives a sparkle (loot, heal, shield or dash) and how many frames old it is; draws little stars rising and a ring; returns nothing. |
| `ui.py` | `draw_feel()` | 1216 | receives nothing; draws the smoke puffs and sparkles that are playing; returns how many were drawn. |
| `ui.py` | `shake_offset()` | 1232 | receives nothing; returns how far [x, y] to jolt the screen this frame for the strongest shake playing ([0, 0] if none). |
| `ui.py` | `draw_strikes()` | 1243 | receives nothing; draws every enemy attack that is playing right now; returns how many were drawn. |
| `ui.py` | `caption()` | 1254 | receives the game, the enemy unit that is acting (None to clear) and what it is doing; shows it in a caption on the map ("Something in the dark" if the unit is hidden); returns nothing. |
| `ui.py` | `draw_caption()` | 1266 | receives nothing; draws the caption that says what the acting enemy is doing; returns True if one was drawn. |
| `ui.py` | `model_paths()` | 1285 | receives the game; turns the enemy moves the game logic made into walking paths (only for models the party can see); returns a list of [model, path]. |
| `ui.py` | `play_moves()` | 1302 | receives the game; shows the enemies that just moved walking along their paths tile by tile; returns how many models walked. |
| `ui.py` | `place_model()` | 1324 | receives a model, its walking path, the step it is on and how far along that step (0-1); sets where it is drawn this frame; returns nothing. |
| `ui.py` | `slide_hero()` | 1333 | receives the game, a walking hero and the tile they step from and to; slides the hero smoothly across that one step; returns nothing. |
| `ui.py` | `fly_card()` | 1343 | receives the game, the acting hero, the card being played and its target tile; shows the card flying from the hand to the target, shrinking as it goes; returns nothing. |
| `ui.py` | `draw_flying()` | 1365 | receives nothing; draws the card that is flying to its target, if any; returns True if one was drawn. |
| `ui.py` | `fast_forward()` | 1374 | receives nothing; returns True while the player holds Space to speed up the enemies' turns. |
| `ui.py` | `wait_effects()` | 1381 | receives the game; keeps drawing until every enemy attack on screen has landed; returns nothing. |
| `ui.py` | `draw_path()` | 1390 | receives the game, the dragged hero and the tile under the mouse; draws footsteps along the walking path; returns the path length. |
| `ui.py` | `preview_words()` | 1400 | receives the game, the acting hero, the card being dragged (None when walking) and the tile under the mouse; returns a short line saying what dropping there would do. |
| `ui.py` | `draw_preview()` | 1416 | receives the game, the acting hero and the card being dragged (None when walking); shows what a drop on the tile under the mouse would do; returns True if a preview was shown. |
| `ui.py` | `draw_drag()` | 1433 | receives the game; draws whatever is being dragged under the mouse (a card or the hero) and what dropping it would do; returns the kind of thing dragged ("" if nothing). |
| `ui.py` | `exit_open()` | 1454 | receives the game; returns True if the party's chamber is clear and has an unsealed EXIT door. |
| `ui.py` | `heal_tip()` | 1465 | receives the game and the acting hero; returns a tip if a hero is badly hurt and this hero holds a heal card ("" if not). |
| `ui.py` | `reach_tip()` | 1477 | receives the game and the acting hero; returns a tip if enemies are in sight but out of reach of every attack card ("" if not). |
| `ui.py` | `loot_tip()` | 1489 | receives the game and the acting hero; returns a tip if a chest or shrine can be reached this turn ("" if not). |
| `ui.py` | `situation_tip()` | 1497 | receives the game; returns the most useful tip for what is happening right now ("" if there is nothing to say). |
| `ui.py` | `draw_tip()` | 1517 | receives the game; draws the tip strip along the bottom of the map; returns True if a tip was shown. |
| `ui.py` | `hint_for()` | 1530 | receives the game and the acting hero; returns [words, rectangle to point at] for the next first-turn hint, or None when there is nothing left to teach. |
| `ui.py` | `draw_hint()` | 1551 | receives the game; on a hero's turn, shows a pointer bubble with the next thing to try, until the player has walked, played a card and ended a turn once; returns True if a hint was shown. |
| `ui.py` | `learn_hint()` | 1578 | receives the request the player just made; marks the matching first-turn hint as learned; returns the request type. |
| `ui.py` | `draw_game()` | 1586 | receives the game; draws the entire game screen once; returns nothing. |
| `ui.py` | `common_event()` | 1606 | receives the game (or None on menu screens) and one event; handles closing the window, full screen and log scrolling; returns nothing. |
| `ui.py` | `present()` | 1621 | receives the game (or None); shows the finished frame (jolted if a shake is playing), waits for 60 FPS and returns the list of new events (minus the ones the camera used up); holding Space speeds the effects up. |
| `ui.py` | `frame()` | 1643 | receives the game; draws one frame of the game screen and returns the new events. |
| `ui.py` | `pause()` | 1649 | receives the game and a time in milliseconds; keeps drawing for that long so the player can watch (much shorter while Space is held; nothing if no window is open, as in the tests); returns nothing. |
| `ui.py` | `move_cursor()` | 1660 | receives the game and an arrow key; moves the keyboard cursor one tile (staying on the map); returns the cursor tile. |
| `ui.py` | `clear_input()` | 1672 | receives nothing; forgets any drag, chosen card and glowing tiles; returns nothing. |
| `ui.py` | `dim_screen()` | 1681 | receives nothing; darkens the whole window behind a pop-up box; returns nothing. |
| `ui.py` | `check_number()` | 1688 | receives what the player typed and the allowed range; returns [number, ""] if it is good or [None, message] if it is not. |
| `ui.py` | `check_name()` | 1701 | receives what the player typed; returns [name, ""] if it is a good file name or [None, message] if it is not. |
| `ui.py` | `draw_text_box()` | 1711 | receives a question, the text typed so far and an error message; draws the typing box; returns nothing. |
| `ui.py` | `ask_text()` | 1728 | receives the game, a question, "number" or "name", and the number range; lets the player type until the answer is valid; returns the answer (None if cancelled). |
| `ui.py` | `type_loop()` | 1738 | receives the same things as ask_text(); runs the typing box until a valid answer or Esc; returns the answer (None if cancelled). |
| `ui.py` | `ask_yes_no()` | 1766 | receives the game and a yes/no question; waits for Y or N (or a click); returns True for yes. |
| `ui.py` | `ask_direction()` | 1789 | receives the game; waits for the player to press an arrow key; returns the step [dx, dy] (None if cancelled). |
| `ui.py` | `confirm_quit()` | 1803 | receives the game; asks the player if they really want to quit; returns True for yes. |
| `ui.py` | `turn_buttons()` | 1808 | receives nothing; puts the turn and menu buttons at the bottom right; returns the button list. |
| `ui.py` | `show_moves()` | 1814 | receives the game and the acting hero; lights up the tiles the hero can walk to, each with its step count; returns how many. |
| `ui.py` | `show_targets()` | 1823 | receives a list of tiles and a glow kind; lights them up (without step counts); returns how many. |
| `ui.py` | `refresh_glow()` | 1831 | receives the game and the acting hero; lights up what the player can do right now (the chosen card's targets, or walking tiles); returns how many tiles glow. |
| `ui.py` | `hand_card_at()` | 1839 | receives a hero and a mouse position; returns the number of the hand card there, or -1. |
| `ui.py` | `pick_card()` | 1848 | receives the acting hero and a hand card number; chooses that card so its targets glow; returns True if it could be chosen. |
| `ui.py` | `card_request()` | 1862 | receives the game, the acting hero and a tile; returns a request to play the chosen card there, or shows why not and returns None. |
| `ui.py` | `move_request()` | 1872 | receives the game, the acting hero and a tile; returns a request to walk there, or shows why not and returns None. |
| `ui.py` | `tile_request()` | 1880 | receives the game, the acting hero and a clicked or dropped-on tile; uses the chosen card there, or walks there; returns a request or None. |
| `ui.py` | `typed_move()` | 1894 | receives the game and the acting hero; asks "How many tiles to move?" in a typed box, then a direction; returns the walk request or None. |
| `ui.py` | `turn_button()` | 1910 | receives the game, the acting hero and the id of a button (or menu key); returns the request it makes, or None. |
| `ui.py` | `turn_mouse_down()` | 1923 | receives the game, the acting hero and a click position; starts dragging a card or the hero, or acts on a clicked tile; returns a request or None. |
| `ui.py` | `turn_mouse_up()` | 1941 | receives the game, the acting hero and where the mouse was let go; finishes a drag; returns a request, or None after a snap back. |
| `ui.py` | `turn_key()` | 1957 | receives the game, the acting hero and a key; returns the request it makes, or None. |
| `ui.py` | `turn_intro()` | 1977 | receives the acting hero; returns the sentence shown in the message bar that says what the player can do now. |
| `ui.py` | `get_hero_action()` | 1987 | receives the game and the hero whose turn it is; waits for the player to walk, play a card, use the menu or end the turn; returns that request. |
| `ui.py` | `draw_title()` | 2018 | receives the title buttons and a note (like a load error); draws the title screen with Frodo facing the Warlord; returns nothing. |
| `ui.py` | `title_screen()` | 2037 | receives a note to show (like a load error); shows the title screen and waits; returns "start", "continue", "rules" or "quit". |
| `ui.py` | `save_rect()` | 2056 | receives a row number on the Continue screen; returns that save's rectangle. |
| `ui.py` | `draw_load_screen()` | 2061 | receives the save names and their summaries; draws the Continue screen; returns nothing. |
| `ui.py` | `hover_border()` | 2082 | receives a rectangle; returns the border color for it (gold under the mouse, brass otherwise). |
| `ui.py` | `load_screen()` | 2089 | receives nothing; lists the saved games and waits for the player to pick one; returns its name, or "" to go back. |
| `ui.py` | `recruit_rect()` | 2109 | receives a recruit number; returns that recruit's card rectangle on the party screen. |
| `ui.py` | `draw_recruit()` | 2114 | receives the data, a hero name, a rectangle and whether the hero is chosen; draws the recruit card; returns nothing. |
| `ui.py` | `draw_party_screen()` | 2138 | receives the data, the recruit names, the chosen names, the buttons and a note; draws the party screen; returns nothing. |
| `ui.py` | `toggle_recruit()` | 2162 | receives the chosen names and one recruit name; adds or removes that recruit (3 at most); returns a note for the player. |
| `ui.py` | `level_rect()` | 2173 | receives a difficulty number (0-2); returns its button rectangle on the party screen. |
| `ui.py` | `draw_levels()` | 2178 | receives the data and the chosen difficulty number; draws the Easy / Normal / Hard buttons and what the chosen one means; returns nothing. |
| `ui.py` | `party_event()` | 2189 | receives one event, the recruit names and the buttons; returns "go", "back", a recruit name to toggle, or "". |
| `ui.py` | `change_level()` | 2213 | receives a party-screen choice like "level+1" or "level2", the current difficulty number and how many there are; returns the new difficulty number. |
| `ui.py` | `party_screen()` | 2222 | receives the loaded data; starts with only Frodo, lets the player add 2 or 3 companions and pick a difficulty; returns {"party": names, "difficulty": name}, or {} to go back. |
| `ui.py` | `title_flow()` | 2251 | receives the loaded data and a note for the title screen; runs the title, Continue, rules and party screens; returns {"party": names} for a new game, {"file": name} to load a save, or {} to quit. |
| `ui.py` | `draw_legend()` | 2350 | receives the y position to start at; draws the map legend with the real tile art; returns nothing. |
| `ui.py` | `quick_panel()` | 2360 | receives a rectangle, a heading and its lines; draws one step of the quick-start card; returns the rectangle. |
| `ui.py` | `quick_pictures()` | 2372 | receives the four quick-start panels; draws the little picture in each (the Warlord, a glowing tile, a card and an EXIT door); returns nothing. |
| `ui.py` | `draw_quickstart()` | 2388 | receives the rectangle to draw in; draws the one-page quick-start card (goal, walk, cards, doors, colours); returns nothing. |
| `ui.py` | `show_quickstart()` | 2414 | receives the game; shows the quick-start card over the map until the player clicks or presses a key; returns nothing. |
| `ui.py` | `draw_rules_page()` | 2429 | receives a rules page number; draws that page on a parchment sheet; returns nothing. |
| `ui.py` | `show_rules()` | 2455 | receives nothing; shows the rules pages until the player closes them; returns the last page number seen. |
| `ui.py` | `memory_line()` | 2476 | receives the game; returns a sentence listing what Spears has noticed about the party. |
| `ui.py` | `draw_status_box()` | 2484 | receives the status sentences; draws them in a pop-up parchment box; returns nothing. |
| `ui.py` | `show_status()` | 2499 | receives the game; shows the current status in a pop-up until a key or click; returns how many lines were shown. |
| `ui.py` | `draw_end()` | 2512 | receives "win" or "lose" and the summary sentences; draws the victory or defeat screen; returns nothing. |
| `ui.py` | `end_buttons()` | 2534 | receives nothing; returns the Play again and Quit buttons of the end screen. |
| `ui.py` | `end_screen()` | 2540 | receives "win" or "lose" and the summary sentences; shows the end screen until the player chooses; returns "again" or "quit". |
| `art.py` | `pick_font()` | 66 | receives a list of font names, a size and bold True/False; returns the first of those fonts found on this computer. |
| `art.py` | `make_fonts()` | 74 | receives nothing; builds every font the game uses and returns how many were made. |
| `art.py` | `setup()` | 89 | receives the game window; builds the fonts and textures once; returns how many pictures were built. |
| `art.py` | `build_overlays()` | 105 | receives the tile size; builds the see-through pictures stamped over tiles (darkness and wall shadows); returns nothing. |
| `art.py` | `stamp()` | 119 | receives an overlay name ("dark", "shadow_top" or "shadow_left") and a tile rectangle; stamps it over the tile; returns nothing. |
| `art.py` | `clamp()` | 124 | receives a number; returns it squeezed into the color range 0-255. |
| `art.py` | `tint()` | 129 | receives a color and an amount (+ lighter, - darker); returns the shifted color. |
| `art.py` | `pulse()` | 134 | receives nothing; returns a number that gently rises and falls between 0 and 1 for glowing effects. |
| `art.py` | `noise_tile()` | 141 | receives a size, a base color, how much it may vary and a seed; returns a speckled square picture. |
| `art.py` | `blotchy()` | 151 | receives a picture, a seed and a count; adds that many soft stains so it looks aged; returns the picture. |
| `art.py` | `crack()` | 165 | receives a tile picture, a random source and a color; scratches one wandering crack into it; returns nothing. |
| `art.py` | `floor_tile()` | 178 | receives a size and a seed; returns one worn stone flagstone picture. |
| `art.py` | `wall_tile()` | 196 | receives a size and a seed; returns one dungeon wall block picture (lighter top, bricks on the front). |
| `art.py` | `fill_texture()` | 215 | receives a rectangle and a texture name; covers that area of the screen with the texture; returns the rectangle. |
| `art.py` | `build_panel()` | 228 | receives a size and a texture name; returns a rounded panel picture with darker worn edges. |
| `art.py` | `panel()` | 247 | receives a rectangle, a texture name ("parchment", "leather" or "slate") and a border color; draws a framed panel; returns the rectangle. |
| `art.py` | `shade()` | 258 | receives a rectangle, a color and a see-through amount (0-255); tints that area; returns the rectangle. |
| `art.py` | `vignette()` | 266 | receives a rectangle; darkens its edges like torchlight fading; returns the rectangle. |
| `art.py` | `torch_glow()` | 279 | receives a center and a radius; adds a soft warm light there; returns nothing. |
| `art.py` | `draw_backdrop()` | 291 | receives nothing; fills the whole screen with a dark dungeon wall for the menu screens; returns nothing. |
| `art.py` | `text()` | 309 | receives words, a position, a font name, a color and "left", "center" or "right"; draws the words and returns their rectangle. |
| `art.py` | `text_outline()` | 323 | receives the same things as text(); draws the words with a dark outline so they read on any background; returns their rectangle. |
| `art.py` | `wrap_text()` | 330 | receives a sentence, a font name and a pixel width; returns the sentence split into lines that fit. |
| `art.py` | `ribbon()` | 346 | receives a center, a width, some words and a color; draws a heading ribbon with notched ends; returns nothing. |
| `art.py` | `divider()` | 356 | receives a center x, a y and a width; draws a brass line with a diamond in the middle; returns nothing. |
| `art.py` | `draw_plate()` | 366 | receives a rectangle, a label and "normal", "hot", "on" or "off"; draws a brass button plate; returns the rectangle. |
| `art.py` | `draw_button()` | 387 | receives a button dictionary; draws it (brighter under the mouse) and returns its rectangle. |
| `art.py` | `draw_bar()` | 395 | receives a rectangle, a value, its maximum and a color; draws a filled bar with a notch per point; returns nothing. |
| `art.py` | `draw_pips()` | 409 | receives a center x, a y, a count and a color; draws that many small wound drops; returns nothing. |
| `art.py` | `draw_skull()` | 417 | receives a center, a size and whether this Doom step is filled; draws one skull; returns nothing. |
| `art.py` | `medallion()` | 430 | receives a center, a radius, a fill color and a rim color; draws a round token; returns nothing. |
| `art.py` | `icon_attack()` | 440 | receives a center, a size and a color; draws a sword icon; returns nothing. |
| `art.py` | `icon_move()` | 448 | receives a center, a size and a color; draws a boot icon; returns nothing. |
| `art.py` | `icon_heal()` | 455 | receives a center, a size and a color; draws a heart icon; returns nothing. |
| `art.py` | `icon_shield()` | 463 | receives a center, a size and a color; draws a shield icon; returns nothing. |
| `art.py` | `icon_element()` | 471 | receives an element name, a center and a size; draws a flame, snowflake or sun; returns nothing. |
| `art.py` | `draw_icon()` | 493 | receives an icon name, a center, a size and a color; draws that icon; returns the name. |
| `art.py` | `mini_card()` | 508 | receives a position, a color and a number; draws a tiny card with the number beside it (for card piles); returns nothing. |
| `art.py` | `paint_frodo()` | 518 | receives a picture, a center and a size; paints Frodo the Maltese with cape and knight's helmet; returns nothing. |
| `art.py` | `paint_frodo_helmet()` | 537 | receives a picture and Frodo's center and size; paints the helmet brim, nose guard and crimson plume; returns nothing. |
| `art.py` | `paint_frodo_face()` | 548 | receives a picture and Frodo's center and size; paints his eyes, nose and tongue; returns nothing. |
| `art.py` | `paint_body()` | 558 | receives a picture, a center, a size, a body color and a head color; paints a simple person with a shaded side; returns nothing. |
| `art.py` | `paint_tank()` | 570 | receives a picture, a center and a size; paints Brother Biscuit with helmet, hammer and big shield; returns nothing. |
| `art.py` | `paint_archer()` | 584 | receives a picture, a center and a size; paints Pip the hooded archer with a bow; returns nothing. |
| `art.py` | `paint_mage()` | 598 | receives a picture, a center and a size; paints Mabel the mage with pointed hat and glowing staff; returns nothing. |
| `art.py` | `paint_rogue()` | 611 | receives a picture, a center and a size; paints Nettle the hooded rogue with a dagger; returns nothing. |
| `art.py` | `paint_orc()` | 624 | receives a picture, a center and a size; paints an Orc Brute with tusks and a club; returns nothing. |
| `art.py` | `paint_goblin()` | 637 | receives a picture, a center and a size; paints a small Goblin Slinger with pointy ears; returns nothing. |
| `art.py` | `paint_guard()` | 649 | receives a picture, a center and a size; paints an armored Iron Guard with tower shield and spear; returns nothing. |
| `art.py` | `paint_wolf()` | 664 | receives a picture, a center and a size; paints a Wolf Rider (a wolf with a small rider); returns nothing. |
| `art.py` | `paint_bomber()` | 681 | receives a picture, a center and a size; paints a Bomb Flinger (a goblin holding a lit bomb); returns nothing. |
| `art.py` | `paint_shade()` | 696 | receives a picture, a center and a size; paints a wispy Shade Stalker with glowing eyes; returns nothing. |
| `art.py` | `paint_warlord()` | 708 | receives a picture, a center and a size; paints Spears's Warlord with cape, crown and greatsword; returns nothing. |
| `art.py` | `paint_figure()` | 726 | receives a picture, a hero kind or enemy look, a center and a size; paints the matching figure; returns the name. |
| `art.py` | `outlined()` | 755 | receives a painted figure and an outline width; returns the figure with a dark outline all round, like a cut-out standee. |
| `art.py` | `sprite()` | 766 | receives a figure name and a size; returns its outlined picture (painted the first time, reused after that). |
| `art.py` | `draw_base()` | 777 | receives a center, a size and a color; draws the shadow and round coloured base a figure stands on; returns nothing. |
| `art.py` | `draw_hero()` | 789 | receives a hero kind, a center and a size; draws that hero standing on a base in the class color; returns the kind. |
| `art.py` | `draw_model()` | 797 | receives an enemy look, a center and a size; draws that enemy on a bone-white base (gold for the Warlord); returns the look. |
| `art.py` | `draw_floor()` | 810 | receives a tile rectangle and a variant number; draws a stone flagstone; returns nothing. |
| `art.py` | `draw_wall()` | 815 | receives a tile rectangle and a variant number; draws a wall block; returns nothing. |
| `art.py` | `draw_door()` | 820 | receives a tile rectangle and whether the door is unsealed; draws a sealed door or a glowing EXIT; returns nothing. |
| `art.py` | `draw_boss_mark()` | 844 | receives a door's tile rectangle; draws a crimson skull plaque over it to mark the way to the boss; returns nothing. |
| `art.py` | `draw_throne()` | 855 | receives the rectangle the throne covers (one or two tiles wide); draws the Warlord's iron throne on its stone dais; returns nothing. |
| `art.py` | `draw_brazier()` | 873 | receives a tile rectangle; draws an iron fire bowl on three legs (its flames are added with the lighting); returns nothing. |
| `art.py` | `draw_open_door()` | 886 | receives a tile rectangle; draws a doorway whose doors have been swung open for good; returns nothing. |
| `art.py` | `draw_chest()` | 897 | receives a tile rectangle; draws a banded treasure chest; returns nothing. |
| `art.py` | `draw_trap()` | 913 | receives a tile rectangle; draws a spike plate with crimson tips; returns nothing. |
| `art.py` | `draw_shrine()` | 927 | receives a tile rectangle; draws a stone shrine with a glowing rune (a point of interest); returns nothing. |
| `art.py` | `draw_cover()` | 942 | receives a tile rectangle; draws a wooden barricade crate that gives cover; returns nothing. |
| `art.py` | `draw_feature()` | 958 | receives a tile letter, its rectangle and an unused flag (kept so old calls still work); draws what stands on the tile; returns the letter. |
| `art.py` | `glow_rect()` | 981 | receives a rectangle, a color and a see-through amount; makes a tile glow with bright corner brackets; returns nothing. |
| `art.py` | `action_words()` | 994 | receives a card's action; returns [main words, small words] such as ["Attack 3", "range 4"]. |
| `art.py` | `draw_card()` | 1008 | receives a card, a rectangle, a border color and the owner's hero kind; draws the card (name, big action icon, action, range and element mark); returns the rectangle. |
| `art.py` | `draw_modifier()` | 1031 | receives a rectangle, the modifier text, "hero" or "enemy" and a flip amount 0-1; draws the attack modifier card that was just flipped; returns nothing. |
| `scenery.py` | `is_wall()` | 35 | receives the grid of letters the party sees and a col/row; returns True if that spot is wall (outside the room counts as wall). |
| `scenery.py` | `layer()` | 42 | receives a size; returns an empty see-through picture to paint soft things on. |
| `scenery.py` | `soft_blob()` | 47 | receives a picture, a position, a size, a color and a see-through amount; paints a soft oval stain there; returns nothing. |
| `scenery.py` | `grain()` | 54 | receives nothing; returns a picture of fine random speckles that makes flat color look like rough stone (built once). |
| `scenery.py` | `add_grain()` | 67 | receives a picture; covers it with the stone speckle; returns nothing. |
| `scenery.py` | `slab_fits()` | 77 | receives the grid of used half-tiles, a spot and a slab size; returns True if a slab that size fits there. |
| `scenery.py` | `pick_size()` | 86 | receives the used grid, a spot and a random source; returns a random slab size that fits (a small one if nothing else does). |
| `scenery.py` | `slab_plan()` | 95 | receives the room size in tiles and a random source; returns a list of [x, y, width, height] flagstones of mixed sizes that cover the floor. |
| `scenery.py` | `scratch()` | 113 | receives a picture, a start point, a random source and a color; scratches one wandering crack; returns nothing. |
| `scenery.py` | `paint_slab()` | 123 | receives a picture, one [x, y, width, height] flagstone and a random source; paints the worn stone with lit and shadowed edges; returns nothing. |
| `scenery.py` | `paint_puddle()` | 144 | receives a picture, a middle point and a random source; paints a dark puddle with a pale reflection; returns [x, y, width, height]. |
| `scenery.py` | `paint_debris()` | 159 | receives a picture, a middle point and a random source; scatters a few broken stones (and sometimes a bone) there; returns nothing. |
| `scenery.py` | `random_spot()` | 174 | receives the map size in tiles and a random source; returns a random pixel point [x, y] somewhere on the map. |
| `scenery.py` | `paint_floor()` | 179 | receives a picture, the map size in tiles and a random source; paints wet flagstone floor over the whole map (rock is painted over it later); returns the list of puddles. |
| `scenery.py` | `floor_base()` | 200 | receives the map size and the dungeon's seed; returns [floor picture, puddles], painted once per dungeon and then reused so the floor never changes under the party. |
| `scenery.py` | `paint_grid_hints()` | 210 | receives a picture and the letters grid; rules a clear grid over every floor tile (a dark line and a pale line, like a groove) so the party can count tiles; returns how many tiles were ruled. |
| `scenery.py` | `gradient()` | 231 | receives a size, which side is darkest ("top", "left", "right" or "bottom") and a strength; returns a shadow strip that fades away from that side. |
| `scenery.py` | `cached_gradient()` | 251 | receives the same things as gradient(); returns that shadow strip, built only once. |
| `scenery.py` | `paint_wall_shadows()` | 259 | receives a picture and the letters grid; darkens the floor along the foot of every wall, deepest under the tall north faces; returns nothing. |
| `scenery.py` | `paint_rock_top()` | 283 | receives a picture, the letters grid, a wall tile and a random source; paints the dark top of the wall with a pale rim where it meets the floor; returns nothing. |
| `scenery.py` | `brick_tint()` | 304 | receives a brick's place along the wall and its height; returns how much lighter or darker that brick is (always the same for the same brick). |
| `scenery.py` | `paint_course()` | 309 | receives a picture, the left and top of one row of bricks in a tile, its height and the row number; paints the bricks so they line up with the next tile; returns nothing. |
| `scenery.py` | `paint_damp()` | 321 | receives a picture, the left, top and bottom of a wall face and a random source; adds wet streaks running down and moss at the foot; returns nothing. |
| `scenery.py` | `paint_face()` | 333 | receives a picture, the letters grid, a wall tile with floor to its south and a random source; paints the tall brick face rising from the floor; returns the y of the face's top. |
| `scenery.py` | `has_torch()` | 355 | receives a wall face tile; returns True if a wall torch hangs on this face (about every fourth face). |
| `scenery.py` | `paint_sconce()` | 360 | receives a picture and a point on a wall face; paints the iron bracket and unlit torch that hangs there; returns nothing. |
| `scenery.py` | `near_floor()` | 367 | receives the letters grid and a wall tile; returns True if any of the eight tiles around it is floor (rock far from any room is left as black void). |
| `scenery.py` | `tile_dice()` | 376 | receives the dungeon's seed and a tile; returns a random source that is always the same for that tile, so walls look the same every time they are repainted. |
| `scenery.py` | `paint_walls()` | 381 | receives a picture, the letters grid and the dungeon's seed; paints every wall (dark tops first, then the tall faces over them); returns the list of torches [col, row, x, y]. |
| `scenery.py` | `build_room()` | 403 | receives the grid of letters the party sees and the dungeon's seed; paints the whole known dungeon (floor, shadows, walls); returns {"surface", "puddles", "torches"}. |
| `scenery.py` | `light_color()` | 415 | receives the vision grid, the light sources [col, row, strength], a col/row and the frame count; returns the color of the light on that tile (warm and flickering near light, cold and dark where unseen). |
| `scenery.py` | `light_grid()` | 427 | receives the vision grid, the light sources, the frame count and the visible tiles [left, top, right, bottom]; returns a tiny picture with one pixel of light per visible tile. |
| `scenery.py` | `draw_flame()` | 436 | receives a point on the screen, the frame count and the zoom; draws a flickering flame with a warm glow; returns nothing. |
| `scenery.py` | `draw_ripple()` | 449 | receives a point on the screen and how many frames the ripple has left (30 = new); draws a drip ring spreading on a puddle; returns nothing. |
