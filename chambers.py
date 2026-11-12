"""chambers.py - plans the dungeon and carves its random chambers into the rock.

The dungeon is one big map that starts as solid rock ("#").
The map is split into a grid of CELLS (sizes come from the DUNGEON line in dungeon_data.txt).
plan_dungeon() picks, at random:
  - a 2 x 2 block of cells for the boss arena,
  - a MAIN path of chambers from a far start cell to the arena,
  - a few SIDE chambers branching off the main path (optional, extra loot).
Each chamber is only carved when its door is first opened, with a random shape
(rect, ell, round, cross or cave), a random size inside its cell, and maybe pillars.
A corridor is then dug through the rock from the door to the new chamber.
"""
import random

import movement


def blank_map(cols, rows):
    """AI-assisted: receives a width and height in tiles; returns a new map grid that is solid rock everywhere."""
    grid = []
    for row in range(rows):
        grid.append(["#"] * cols)
    return grid


def zone_box(grid, zone):
    """AI-assisted: receives the map grid and a zone [x, y, width, height]; returns [left, top, right, bottom], the tiles a chamber may use (always leaving a wall around it)."""
    left = max(1, zone[0] + 1)
    top = max(1, zone[1] + 1)
    right = min(len(grid[0]) - 2, zone[0] + zone[2] - 2)
    bottom = min(len(grid) - 2, zone[1] + zone[3] - 2)
    return [left, top, right, bottom]


def box_center(box):
    """AI-assisted: receives a box [left, top, right, bottom]; returns the tile in its middle."""
    return [(box[0] + box[2]) // 2, (box[1] + box[3]) // 2]


def shrink_box(box):
    """AI-assisted: receives a box [left, top, right, bottom]; returns a randomly smaller box inside it, so chambers differ in size and position."""
    width = box[2] - box[0] + 1
    height = box[3] - box[1] + 1
    new_width = random.randint(max(3, width - 2), width)
    new_height = random.randint(max(3, height - 1), height)
    left = box[0] + random.randint(0, width - new_width)
    top = box[1] + random.randint(0, height - new_height)
    return [left, top, left + new_width - 1, top + new_height - 1]


def box_tiles(box):
    """AI-assisted: receives a box [left, top, right, bottom]; returns the list of every tile inside it."""
    tiles = []
    for row in range(box[1], box[3] + 1):
        for col in range(box[0], box[2] + 1):
            tiles.append([col, row])
    return tiles


# ================================================================ planning the dungeon

def cell_zone(dungeon, cells):
    """AI-assisted: receives the DUNGEON settings and a list of cells [cx, cy]; returns the zone [x, y, width, height] that covers all of them."""
    left = 999
    top = 999
    right = -1
    bottom = -1
    for cell in cells:
        left = min(left, cell[0])
        top = min(top, cell[1])
        right = max(right, cell[0])
        bottom = max(bottom, cell[1])
    width = dungeon["cell_width"]
    height = dungeon["cell_height"]
    return [left * width, top * height, (right - left + 1) * width, (bottom - top + 1) * height]


def cell_neighbors(dungeon, cell):
    """AI-assisted: receives the DUNGEON settings and a cell; returns the cells next to it (up, down, left, right) that are on the map."""
    near = []
    for step in movement.STEPS:
        col = cell[0] + step[0]
        row = cell[1] + step[1]
        if col >= 0 and col < dungeon["cell_cols"] and row >= 0 and row < dungeon["cell_rows"]:
            near.append([col, row])
    return near


def touches(dungeon, cell, cells):
    """AI-assisted: receives the DUNGEON settings, a cell and a list of cells; returns True if the cell is next to any of them."""
    for near in cell_neighbors(dungeon, cell):
        if near in cells:
            return True
    return False


def boss_block(dungeon):
    """AI-assisted: receives the DUNGEON settings; returns the 4 cells of a random 2 x 2 block for the boss arena."""
    left = random.randint(0, dungeon["cell_cols"] - 2)
    top = random.randint(0, dungeon["cell_rows"] - 2)
    return [[left, top], [left + 1, top], [left, top + 1], [left + 1, top + 1]]


def far_cell(dungeon, boss):
    """AI-assisted: receives the DUNGEON settings and the boss cells; returns a random cell among those farthest from the boss (where the party starts)."""
    best = []
    best_gap = -1
    for row in range(dungeon["cell_rows"]):
        for col in range(dungeon["cell_cols"]):
            if [col, row] in boss:
                continue
            gap = 99
            for cell in boss:
                gap = min(gap, movement.tile_distance([col, row], cell))
            if gap > best_gap:
                best = [[col, row]]
                best_gap = gap
            elif gap == best_gap:
                best.append([col, row])
    return random.choice(best)


def random_walk(dungeon, start, boss, length):
    """AI-assisted: receives the DUNGEON settings, the start cell, the boss cells and a wanted length; walks at random from the start and returns the path if it ends next to the boss at that length, else []."""
    path = [start]
    while len(path) < length:
        options = []
        for near in cell_neighbors(dungeon, path[len(path) - 1]):
            if near not in path and near not in boss:
                options.append(near)
        if len(options) == 0:
            return []
        path.append(random.choice(options))
    if touches(dungeon, path[len(path) - 1], boss):
        return path
    return []


def main_path(dungeon, boss, start):
    """AI-assisted: receives the DUNGEON settings, the boss cells and the start cell; returns a random main path of cells (as close to the wanted length as possible), or [] if none was found."""
    for spread in [0, 1, 2, 3]:
        for attempt in range(250):
            length = dungeon["main"] + random.randint(-spread, spread)
            path = random_walk(dungeon, start, boss, max(2, length))
            if len(path) > 0:
                return path
    return []


def make_chamber(number, kind, cells, parent, dungeon):
    """AI-assisted: receives a chamber number, its kind ("start", "main", "side" or "boss"), its cells, its parent's number and the DUNGEON settings; returns a new, not yet carved chamber dictionary."""
    return {"id": number, "kind": kind, "cells": cells, "zone": cell_zone(dungeon, cells), "parent": parent,
            "carved": False, "cleared": False, "tiles": [], "name": "", "step": 0,
            "markers": {}, "prepared": []}


def add_sides(dungeon, plan, path, boss):
    """AI-assisted: receives the DUNGEON settings, the plan so far, the main path and the boss cells; adds side chambers in free cells next to the main path; returns how many were added."""
    used = list(path) + list(boss)
    added = 0
    order = list(range(len(path)))
    random.shuffle(order)
    for index in order:
        if added == dungeon["sides"]:
            break
        options = []
        for near in cell_neighbors(dungeon, path[index]):
            if near not in used:
                options.append(near)
        if len(options) > 0:
            cell = random.choice(options)
            used.append(cell)
            side = make_chamber(len(plan), "side", [cell], index, dungeon)
            side["step"] = index + 1
            plan.append(side)
            added += 1
    return added


def plan_dungeon(dungeon):
    """AI-assisted: receives the DUNGEON settings; plans the whole dungeon at random (main path, side chambers and boss arena); returns the list of chambers (number 0 is where the party starts)."""
    path = []
    while len(path) == 0:
        boss = boss_block(dungeon)
        path = main_path(dungeon, boss, far_cell(dungeon, boss))
    plan = []
    for index in range(len(path)):
        kind = "main"
        parent = index - 1
        if index == 0:
            kind = "start"
            parent = None
        chamber = make_chamber(index, kind, [path[index]], parent, dungeon)
        chamber["step"] = index + 1
        plan.append(chamber)
    arena = make_chamber(len(plan), "boss", boss, len(path) - 1, dungeon)
    arena["step"] = len(path) + 1
    plan.append(arena)
    add_sides(dungeon, plan, path, boss)
    return plan


def children(plan, number):
    """AI-assisted: receives the plan and a chamber number; returns the chambers whose door is in that chamber's wall."""
    result = []
    for chamber in plan:
        if chamber["parent"] == number:
            result.append(chamber)
    return result


def owner_grid(grid, plan):
    """AI-assisted: receives the map grid and the plan; returns a grid saying which chamber's zone each tile is in (-1 = no chamber)."""
    owners = movement.blank_grid(grid, -1)
    for chamber in plan:
        zone = chamber["zone"]
        for row in range(zone[1], min(len(grid), zone[1] + zone[3])):
            for col in range(zone[0], min(len(grid[0]), zone[0] + zone[2])):
                owners[row][col] = chamber["id"]
    return owners


# ================================================================ chamber shapes

def shape_ell(box):
    """AI-assisted: receives a box; returns its tiles with one random corner block cut away (an L-shaped room)."""
    cut_width = max(1, (box[2] - box[0] + 1) // 2)
    cut_height = max(1, (box[3] - box[1] + 1) // 2)
    cut_left = random.choice([box[0], box[2] - cut_width + 1])
    cut_top = random.choice([box[1], box[3] - cut_height + 1])
    tiles = []
    for tile in box_tiles(box):
        in_cut_cols = tile[0] >= cut_left and tile[0] < cut_left + cut_width
        in_cut_rows = tile[1] >= cut_top and tile[1] < cut_top + cut_height
        if not (in_cut_cols and in_cut_rows):
            tiles.append(tile)
    return tiles


def shape_round(box):
    """AI-assisted: receives a box; returns its tiles with the corners clipped off (a rounded room)."""
    clip = 1
    if box[2] - box[0] >= 5 and box[3] - box[1] >= 5:
        clip = 2
    tiles = []
    for tile in box_tiles(box):
        from_side = min(tile[0] - box[0], box[2] - tile[0])
        from_end = min(tile[1] - box[1], box[3] - tile[1])
        if from_side + from_end >= clip:
            tiles.append(tile)
    return tiles


def shape_cross(box):
    """AI-assisted: receives a box; returns the tiles of a plus-shaped room (a wide bar across and a wide bar down)."""
    width = box[2] - box[0] + 1
    height = box[3] - box[1] + 1
    band_cols = max(2, width // 2)
    band_rows = max(2, height // 2)
    first_col = box[0] + (width - band_cols) // 2
    first_row = box[1] + (height - band_rows) // 2
    tiles = []
    for tile in box_tiles(box):
        in_cols = tile[0] >= first_col and tile[0] < first_col + band_cols
        in_rows = tile[1] >= first_row and tile[1] < first_row + band_rows
        if in_cols or in_rows:
            tiles.append(tile)
    return tiles


def shape_cave(box):
    """AI-assisted: receives a box; returns its tiles with random bites taken out of the edge (a rough cave)."""
    tiles = []
    for tile in box_tiles(box):
        on_edge = tile[0] == box[0] or tile[0] == box[2] or tile[1] == box[1] or tile[1] == box[3]
        if not on_edge or random.randint(1, 100) <= 60:
            tiles.append(tile)
    return tiles


def connected(tiles):
    """AI-assisted: receives a list of floor tiles; returns only the tiles that can be walked to from the first one."""
    if len(tiles) == 0:
        return []
    reached = [tiles[0]]
    queue = [tiles[0]]
    while len(queue) > 0:
        tile = queue.pop(0)
        for step in movement.STEPS:
            next_tile = [tile[0] + step[0], tile[1] + step[1]]
            if next_tile in tiles and next_tile not in reached:
                reached.append(next_tile)
                queue.append(next_tile)
    return reached


def shape_tiles(shape, box):
    """AI-assisted: receives a shape name and a box; returns the floor tiles of a chamber of that shape (a plain rectangle if the shape came out too small)."""
    if shape == "ell":
        tiles = shape_ell(box)
    elif shape == "round":
        tiles = shape_round(box)
    elif shape == "cross":
        tiles = shape_cross(box)
    elif shape == "cave":
        tiles = shape_cave(box)
    else:
        tiles = box_tiles(box)
    tiles = connected(tiles)
    if len(tiles) < 12:
        tiles = box_tiles(box)
    return tiles


def is_open_floor(tiles, tile):
    """AI-assisted: receives the floor tiles and one tile; returns True if all eight tiles around it are floor too (a safe spot for a pillar)."""
    for row in range(tile[1] - 1, tile[1] + 2):
        for col in range(tile[0] - 1, tile[0] + 2):
            if [col, row] not in tiles:
                return False
    return True


def add_pillars(tiles, count):
    """AI-assisted: receives the floor tiles and how many pillars to try for; turns that many open floor tiles back into rock without cutting the room in two; returns how many were placed."""
    placed = 0
    for attempt in range(count * 8):
        if placed == count or len(tiles) < 26:
            break
        tile = random.choice(tiles)
        if not is_open_floor(tiles, tile):
            continue
        tiles.remove(tile)
        if len(connected(tiles)) == len(tiles):
            placed += 1
        else:
            tiles.append(tile)
    return placed


def carve_chamber(grid, zone, style):
    """AI-assisted: receives the map grid, a zone and a room style; carves a random chamber of that style into the rock; returns its floor tiles."""
    box = shrink_box(zone_box(grid, zone))
    tiles = shape_tiles(style["shape"], box)
    add_pillars(tiles, style["pillars"])
    for tile in tiles:
        grid[tile[1]][tile[0]] = "."
    return tiles


def carve_arena(grid, zone, rows):
    """AI-assisted: receives the map grid, the boss zone and the arena drawing from dungeon_data.txt; carves the throne hall into the middle of the zone; returns [floor tiles, markers] (markers: "W" warlord, "G" guard spawn spots)."""
    box = zone_box(grid, zone)
    left = box[0] + max(0, (box[2] - box[0] + 1 - len(rows[0])) // 2)
    top = box[1] + max(0, (box[3] - box[1] + 1 - len(rows)) // 2)
    tiles = []
    markers = {"W": [], "G": []}
    for row in range(len(rows)):
        for col in range(len(rows[row])):
            spot = rows[row][col]
            tile = [left + col, top + row]
            if spot == "#" or not movement.in_bounds(grid, tile[0], tile[1]):
                continue
            if spot in markers:
                markers[spot].append(tile)
                spot = "."
            grid[tile[1]][tile[0]] = spot
            if spot != "Y" and spot != "B":
                tiles.append(tile)
    return [tiles, markers]


# ================================================================ doors and corridors

def inside(grid, col, row):
    """AI-assisted: receives the map grid and a col/row; returns True if a door or corridor may be there (not on the map's outer edge)."""
    return col >= 1 and col <= len(grid[0]) - 2 and row >= 1 and row <= len(grid) - 2


def open_sides(grid, tile):
    """AI-assisted: receives the map grid and a tile; returns how many of the four tiles next to it are not rock."""
    count = 0
    for step in movement.STEPS:
        col = tile[0] + step[0]
        row = tile[1] + step[1]
        if movement.in_bounds(grid, col, row) and grid[row][col] != "#":
            count += 1
    return count


def pick_door(grid, tiles, aim):
    """AI-assisted: receives the map grid, a chamber's floor tiles and a point to aim at; returns the wall tile for a door (closest to the aim), or None."""
    best = None
    best_gap = 999
    shuffled = list(tiles)
    random.shuffle(shuffled)
    for tile in shuffled:
        for step in movement.STEPS:
            spot = [tile[0] + step[0], tile[1] + step[1]]
            if not inside(grid, spot[0], spot[1]) or grid[spot[1]][spot[0]] != "#":
                continue
            gap = movement.tile_distance(spot, aim)
            if open_sides(grid, spot) == 1 and gap < best_gap:
                best = spot
                best_gap = gap
    return best


def can_dig(grid, steps, tile, rules):
    """AI-assisted: receives the map grid, the dig search so far, a tile and the dig rules (door, goal tiles, owner grid, allowed chambers, strict); returns True if the corridor may pass through this rock tile."""
    if not inside(grid, tile[0], tile[1]) or grid[tile[1]][tile[0]] != "#":
        return False
    if steps[tile[1]][tile[0]] != -1:
        return False
    if rules["owners"][tile[1]][tile[0]] not in rules["allowed"]:
        return False
    for step in movement.STEPS:
        near = [tile[0] + step[0], tile[1] + step[1]]
        old_floor = grid[near[1]][near[0]] != "#" and near not in rules["goal"] and near != rules["door"]
        if rules["strict"] and old_floor:
            return False
    return True


def find_corridor(grid, rules):
    """AI-assisted: receives the map grid and the dig rules; returns the list of rock tiles to dig from the door to the new chamber ([] if there is no way)."""
    door = rules["door"]
    steps = movement.blank_grid(grid, -1)
    steps[door[1]][door[0]] = 0
    queue = [door]
    while len(queue) > 0:
        tile = queue.pop(0)
        for step in movement.STEPS:
            next_tile = [tile[0] + step[0], tile[1] + step[1]]
            if next_tile in rules["goal"]:
                path = [tile]
                while steps[tile[1]][tile[0]] > 0:
                    tile = movement.lower_neighbor(steps, tile)
                    path.insert(0, tile)
                return path
            if can_dig(grid, steps, next_tile, rules):
                steps[next_tile[1]][next_tile[0]] = steps[tile[1]][tile[0]] + 1
                queue.append(next_tile)
    return []


def dig_corridor(grid, door, goal, owners, allowed):
    """AI-assisted: receives the map grid, the door, the new chamber's tiles, the owner grid and the chamber numbers the corridor may cross; digs the corridor and returns its tiles."""
    rules = {"door": door, "goal": goal, "owners": owners, "allowed": allowed, "strict": True}
    path = find_corridor(grid, rules)
    if len(path) == 0:
        rules["strict"] = False
        path = find_corridor(grid, rules)
    if len(path) == 0:
        rules["allowed"] = list(range(-1, 100))
        path = find_corridor(grid, rules)
    for tile in path:
        if tile != door:
            grid[tile[1]][tile[0]] = "."
    return path


def far_cluster(tiles, origin, count):
    """AI-assisted: receives floor tiles, a point and a count; returns that many tiles huddled together as far from the point as possible (where the party starts)."""
    far = tiles[0]
    for tile in tiles:
        if movement.tile_distance(tile, origin) > movement.tile_distance(far, origin):
            far = tile
    pool = list(tiles)
    cluster = []
    while len(cluster) < count and len(pool) > 0:
        best = pool[0]
        for tile in pool:
            if movement.tile_distance(tile, far) < movement.tile_distance(best, far):
                best = tile
        pool.remove(best)
        cluster.append(best)
    return cluster


def far_tiles(tiles, origin):
    """AI-assisted: receives floor tiles and a point; returns the tiles in the far half of the chamber from that point (where Spears deploys)."""
    longest = 1
    for tile in tiles:
        longest = max(longest, movement.tile_distance(tile, origin))
    result = []
    for tile in tiles:
        if movement.tile_distance(tile, origin) * 2 >= longest:
            result.append(tile)
    return result
