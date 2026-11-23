"""movement.py - tiles, distances, reachable tiles and pathing around walls.

A tile is a small list [col, row]. The room is a list of lists of letters,
so the letter at a tile is grid[row][col].
"""

STEPS = [[1, 0], [-1, 0], [0, 1], [0, -1]]
SIGHT = 5


def tile_distance(first, second):
    """Team-written. [Owner: Yassin] receives two tiles; returns how many up/down/left/right steps apart they are.

    Called by: frodo_game.count_clumping, spears_ai.furnish, spears_ai.nearest_tile, spears_ai.pick_target,
        spears_ai.coherency_ok, spears_ai.goal_tile, spears_ai.choose_victim, spears_ai.splash,
        spears_ai.touching_hero, spears_ai.nearest_gap, spears_ai.safest_tile, spears_ai.apply_preparations,
        enemy_targets, friend_targets, drop_message, chambers.far_cell, chambers.pick_door,
        chambers.far_cluster, chambers.far_tiles, ui.nearest_first
    """
    return abs(first[0] - second[0]) + abs(first[1] - second[1])


def in_bounds(grid, col, row):
    """Team-written. [Owner: Yassin] receives the grid and a col/row; returns True if that spot is inside the room.

    Called by: is_floor, lower_neighbor, wall_in_view, chambers.carve_arena, chambers.open_sides,
        ui.tile_letter, ui.move_cursor
    """
    return row >= 0 and row < len(grid) and col >= 0 and col < len(grid[0])


def is_floor(grid, col, row, door_open):
    """Team-written. [Owner: Yassin] receives the grid, a col/row and whether sealed doors count as open; returns True if someone can stand there.

    Called by: can_enter, refresh_vision
    Uses: in_bounds
    Decides: if not in_bounds(grid, col, row); if spot == "#" or spot == "Y" or spot == "B"; if spot == "D"
    Why: #, Y (throne) and B (brazier) block; D (sealed door) is walkable only when door_open is True;
        everything else is floor.
    """
    if not in_bounds(grid, col, row):
        return False
    spot = grid[row][col]
    if spot == "#" or spot == "Y" or spot == "B":
        return False
    elif spot == "D":
        return door_open
    else:
        return True


def blank_grid(grid, value):
    """Team-written. [Owner: Yassin] receives the grid and a value; returns a new grid of the same size filled with that value.

    Called by: spears_ai.build_dungeon, step_map, lit_floor, chambers.owner_grid, chambers.find_corridor,
        savegame.build_game
    Loops: for row in grid; for spot in row
    """
    new_grid = []
    for row in grid:
        line = []
        for spot in row:
            line.append(value)
        new_grid.append(line)
    return new_grid


def can_enter(grid, steps, tile, blocked, door_open):
    """Team-written. [Owner: Yassin] receives the grid, the step counts so far, a tile and the blocked tiles; returns True if the search may step onto it.

    Called by: step_map
    Uses: is_floor
    Decides: if not is_floor(grid, tile[0], tile[1], door_open); if steps[tile[1]][tile[0]] != -1
    """
    if not is_floor(grid, tile[0], tile[1], door_open):
        return False
    if steps[tile[1]][tile[0]] != -1:
        return False
    return tile not in blocked


def step_map(grid, start, blocked, door_open):
    """Team-written. [Owner: Yassin] receives the grid, a start tile and blocked tiles; returns a grid of step counts from the start (-1 = cannot be reached).

    Called by: spears_ai.move_unit, reachable_tiles, find_path, lit_floor, move_targets
    Uses: blank_grid, can_enter
    Decides: if can_enter(grid, steps, next_tile, blocked, door_open)
    Loops: while len(queue) > 0; for step in STEPS
    Why: A breadth-first search: the start tile is 0, each neighbour gets +1, and -1 means it cannot be
        reached. Used for walking ranges, paths, sight and enemy goals.
    """
    steps = blank_grid(grid, -1)
    steps[start[1]][start[0]] = 0
    queue = [start]
    while len(queue) > 0:
        tile = queue.pop(0)
        for step in STEPS:
            next_tile = [tile[0] + step[0], tile[1] + step[1]]
            if can_enter(grid, steps, next_tile, blocked, door_open):
                steps[next_tile[1]][next_tile[0]] = steps[tile[1]][tile[0]] + 1
                queue.append(next_tile)
    return steps


def reachable_tiles(grid, start, limit, blocked, occupied, door_open):
    """Team-written. [Owner: Yassin] receives the grid, a start tile, a step limit, tiles that block the way and tiles nobody may stop on; returns the list of tiles that can be reached.

    Called by: spears_ai.place_models, spears_ai.best_tile, spears_ai.safest_tile, move_targets
    Uses: step_map
    Decides: if count > 0 and count <= limit and [col, row] not in occupied
    Loops: for row in range(len(grid)); for col in range(len(grid[0]))
    Why: Keeps tiles whose step count is between 1 and the limit, minus tiles someone is standing on. These
        are the blue glowing tiles.
    """
    steps = step_map(grid, start, blocked, door_open)
    tiles = []
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            count = steps[row][col]
            if count > 0 and count <= limit and [col, row] not in occupied:
                tiles.append([col, row])
    return tiles


def lower_neighbor(steps, tile):
    """Team-written. [Owner: Yassin] receives the step counts and a tile; returns the neighbor tile that is one step closer to the start.

    Called by: find_path, chambers.find_corridor
    Uses: in_bounds
    Decides: if in_bounds(steps, col, row) and steps[row][col] == wanted
    Loops: for step in STEPS
    """
    wanted = steps[tile[1]][tile[0]] - 1
    for step in STEPS:
        col = tile[0] + step[0]
        row = tile[1] + step[1]
        if in_bounds(steps, col, row) and steps[row][col] == wanted:
            return [col, row]
    return tile


def find_path(grid, start, goal, blocked, door_open):
    """Team-written. [Owner: Yassin] receives the grid, a start tile and a goal tile; returns the list of tiles to walk (start first), or [] if there is no way.

    Called by: frodo_game.hero_move, ui.model_paths, ui.draw_path
    Uses: step_map, lower_neighbor
    Decides: if steps[goal[1]][goal[0]] < 0
    Loops: while steps[tile[1]][tile[0]] > 0
    Why: Walks backwards from the goal on the step map, always to a neighbour one step closer, inserting
        each tile at the front of the path.
    """
    steps = step_map(grid, start, blocked, door_open)
    if steps[goal[1]][goal[0]] < 0:
        return []
    path = [goal]
    tile = goal
    while steps[tile[1]][tile[0]] > 0:
        tile = lower_neighbor(steps, tile)
        path.insert(0, tile)
    return path


def hero_tiles(heroes):
    """Team-written. [Owner: Yassin] receives the hero list; returns the tiles of every hero still standing.

    Called by: frodo_game.count_clumping, frodo_game.open_game, spears_ai.deploy_room,
        spears_ai.deploy_boss, spears_ai.best_tile, spears_ai.touching_hero, spears_ai.safest_tile,
        spears_ai.apply_preparations, spears_ai.summon_guards, lit_floor, friend_targets, move_targets,
        ui.show_chamber, ui.light_sources
    Decides: if not hero["exhausted"]
    Loops: for hero in heroes
    """
    tiles = []
    for hero in heroes:
        if not hero["exhausted"]:
            tiles.append(hero["pos"])
    return tiles


def model_tiles(units):
    """Team-written. [Owner: Yassin] receives the enemy unit list; returns the tile of every enemy model.

    Called by: frodo_game.hero_move, spears_ai.deploy_room, spears_ai.deploy_boss, spears_ai.best_tile,
        spears_ai.safest_tile, spears_ai.apply_preparations, spears_ai.summon_guards, enemy_targets,
        move_targets, ui.draw_path
    Loops: for unit in units; for model in unit["models"]
    """
    tiles = []
    for unit in units:
        for model in unit["models"]:
            tiles.append(model["pos"])
    return tiles


def hero_at(heroes, tile):
    """Team-written. [Owner: Yassin] receives the hero list and a tile; returns the standing hero on that tile, or None.

    Called by: frodo_game.hero_heal, ui.hero_at_pixel, ui.tooltip_lines, ui.preview_words, ui.tile_request
    Decides: if not hero["exhausted"] and hero["pos"] == tile
    Loops: for hero in heroes
    """
    for hero in heroes:
        if not hero["exhausted"] and hero["pos"] == tile:
            return hero
    return None


def model_at(units, tile):
    """Team-written. [Owner: Yassin] receives the unit list and a tile; returns [unit, model] for the enemy on that tile, or None.

    Called by: frodo_game.hero_attack, spears_ai.is_flank, drop_message, ui.tooltip_lines, ui.preview_words
    Decides: if model["pos"] == tile
    Loops: for unit in units; for model in unit["models"]
    """
    for unit in units:
        for model in unit["models"]:
            if model["pos"] == tile:
                return [unit, model]
    return None


def learn_outline(game):
    """Team-written. [Owner: Yassin] receives the game; adds every floor tile, door, throne and brazier of the chambers the party has opened to what it knows (the shape of the rooms, not their contents); returns how many tiles were learned.

    Called by: frodo_game.install_room
    Decides: if spot == "#" or game["known"][row][col] != "#"; if owner >= 0 and not
        game["plan"][owner]["carved"]; if spot in "DdEYB"
    Loops: for row in range(len(game["grid"])); for col in range(len(game["grid"][0]))
    """
    learned = 0
    for row in range(len(game["grid"])):
        for col in range(len(game["grid"][0])):
            spot = game["grid"][row][col]
            owner = game["owners"][row][col]
            if spot == "#" or game["known"][row][col] != "#":
                continue
            elif owner >= 0 and not game["plan"][owner]["carved"]:
                continue
            elif spot in "DdEYB":
                game["known"][row][col] = spot
            else:
                game["known"][row][col] = "."
            learned += 1
    return learned


def shown_letter(spot):
    """Team-written. [Owner: Yassin] receives a tile letter; returns the letter the party sees there (hidden pits look like floor, trapped chests like chests).

    Called by: refresh_vision, ui.tile_letter
    Decides: if spot == "H"; if spot == "X"
    """
    if spot == "H":
        return "."
    elif spot == "X":
        return "C"
    return spot


def lit_floor(game):
    """Team-written. [Owner: Yassin] receives the game; returns a grid marking every tile a standing hero can see: within SIGHT steps on foot, so walls block the view.

    Called by: refresh_vision
    Uses: blank_grid, hero_tiles, step_map
    Decides: if steps[row][col] >= 0 and steps[row][col] <= SIGHT
    Loops: for tile in hero_tiles(game["heroes"]); for row in range(len(lit)); for col in range(len(lit[0]))
    """
    lit = blank_grid(game["grid"], False)
    for tile in hero_tiles(game["heroes"]):
        steps = step_map(game["grid"], tile, [], True)
        for row in range(len(lit)):
            for col in range(len(lit[0])):
                if steps[row][col] >= 0 and steps[row][col] <= SIGHT:
                    lit[row][col] = True
    return lit


def wall_in_view(game, lit, col, row):
    """Team-written. [Owner: Yassin] receives the game, the lit-floor grid and a wall tile; returns True if a lit floor tile touches that wall (so the wall is lit too).

    Called by: refresh_vision
    Uses: in_bounds
    Decides: if in_bounds(lit, near_col, near_row) and lit[near_row][near...
    Loops: for near_row in range(row - 1, row + 2); for near_col in range(col - 1, col + 2)
    """
    for near_row in range(row - 1, row + 2):
        for near_col in range(col - 1, col + 2):
            if in_bounds(lit, near_col, near_row) and lit[near_row][near_col]:
                return True
    return False


def refresh_vision(game):
    """Team-written. [Owner: Yassin] receives the game; works out which tiles the heroes can see right now and remembers what is on them; returns how many tiles are visible.

    Called by: frodo_game.install_room, frodo_game.hero_move, frodo_game.take_turn, savegame.build_game
    Uses: lit_floor, is_floor, wall_in_view, shown_letter
    Decides: if not is_floor(game["grid"], col, row, True); if visible
    Loops: for row in range(len(game["grid"])); for col in range(len(game["grid"][0]))
    Why: A tile is seen if a standing hero can walk to it within SIGHT (5) steps, so walls block sight.
        Walls count as seen when they touch seen floor. Seen tiles are remembered in game['known'].
    """
    lit = lit_floor(game)
    count = 0
    for row in range(len(game["grid"])):
        for col in range(len(game["grid"][0])):
            visible = lit[row][col]
            if not is_floor(game["grid"], col, row, True):
                visible = wall_in_view(game, lit, col, row)
            game["seen"][row][col] = visible
            if visible:
                game["known"][row][col] = shown_letter(game["grid"][row][col])
                count += 1
    return count


def enemy_targets(game, origin, reach):
    """Team-written. [Owner: Yassin] receives the game, a tile and a range; returns the tiles of visible enemy models within range.

    Called by: action_targets, ui.reach_tip
    Uses: model_tiles, tile_distance
    Decides: if game["seen"][tile[1]][tile[0]] and tile_distance(origin, ...
    Loops: for tile in model_tiles(game["units"])
    """
    tiles = []
    for tile in model_tiles(game["units"]):
        if game["seen"][tile[1]][tile[0]] and tile_distance(origin, tile) <= reach:
            tiles.append(tile)
    return tiles


def friend_targets(game, origin, reach):
    """Team-written. [Owner: Yassin] receives the game, a tile and a range; returns the tiles of standing heroes within range.

    Called by: action_targets
    Uses: hero_tiles, tile_distance
    Decides: if tile_distance(origin, tile) <= reach
    Loops: for tile in hero_tiles(game["heroes"])
    """
    tiles = []
    for tile in hero_tiles(game["heroes"]):
        if tile_distance(origin, tile) <= reach:
            tiles.append(tile)
    return tiles


def move_targets(game, hero):
    """Team-written. [Owner: Yassin] receives the game and a hero; returns [tiles the hero can walk to with the moves left this turn, steps to each].

    Called by: ui.loot_tip, ui.show_moves, ui.move_request
    Uses: model_tiles, hero_tiles, step_map, reachable_tiles
    Loops: for tile in tiles
    """
    blocked = model_tiles(game["units"])
    occupied = hero_tiles(game["heroes"])
    steps = step_map(game["grid"], hero["pos"], blocked, False)
    tiles = reachable_tiles(game["grid"], hero["pos"], hero["moves_left"], blocked, occupied, False)
    counts = []
    for tile in tiles:
        counts.append(steps[tile[1]][tile[0]])
    return [tiles, counts]


def action_targets(game, hero, action):
    """Team-written. [Owner: Yassin] receives the game, a hero and a card's action; returns the list of tiles that card can be dropped on.

    Called by: ui.reach_tip, ui.hint_for, ui.refresh_glow, ui.card_request
    Uses: enemy_targets, friend_targets
    Decides: if action["kind"] == "attack"; if action["kind"] == "heal"
    """
    if action["kind"] == "attack":
        return enemy_targets(game, hero["pos"], action["range"])
    elif action["kind"] == "heal":
        return friend_targets(game, hero["pos"], action["range"])
    else:
        return [hero["pos"]]


def is_valid_drop(tile, targets):
    """Team-written. [Owner: Yassin] receives the tile under the mouse and the allowed tiles; returns True if the drop is allowed.

    Called by: ui.draw_preview, ui.draw_drag, ui.card_request, ui.move_request
    """
    return tile is not None and tile in targets


def drop_message(game, hero, action, tile):
    """Team-written. [Owner: Yassin] receives the game, a hero, the card's action (None for walking) and the bad drop tile; returns a friendly message saying why it did not work.

    Called by: ui.card_request, ui.move_request
    Uses: tile_distance, model_at
    Decides: if action is None; if hero["moves_left"] == 0; if tile is not None and
        tile_distance(hero["pos"], tile) > h...; if action["kind"] == "attack"; if tile is None or
        model_at(game["units"], tile) is None; if action["kind"] == "heal"
    """
    name = hero["name"]
    if action is None:
        if hero["moves_left"] == 0:
            return name + " has no moves left this turn."
        if tile is not None and tile_distance(hero["pos"], tile) > hero["moves_left"]:
            return "Too far - " + name + " has " + str(hero["moves_left"]) + " moves left."
        return name + " can't get there. Pick a glowing blue tile."
    elif action["kind"] == "attack":
        if tile is None or model_at(game["units"], tile) is None:
            return "No enemy there. Drop the attack on a glowing red enemy."
        return "Out of range - this attack reaches " + str(action["range"]) + " tiles."
    elif action["kind"] == "heal":
        return "Drop the heal on a glowing hero within " + str(action["range"]) + " tiles."
    else:
        return "Drop this card on " + name + " (the glowing tile)."
