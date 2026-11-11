"""scenery.py - paints a dungeon room so it looks like a real place, not a board of tiles.

The view is "three-quarter": we look down into the room from the south. That means:
  - walls on the far (north) side of a floor show their tall brick FACE,
  - every other wall shows only its dark rock TOP, with a pale rim where it meets the floor,
  - floors are irregular flagstones of many sizes, with wet grout, puddles, moss and rubble,
  - shadows gather along the foot of every wall,
  - light is real: the room is multiplied by a light map, bright and warm near the heroes
    and cold and nearly black where nobody can see.

build_room() paints the room once into one big picture. ui.py reuses that picture every
frame and only repaints it when the walls the party knows about change.
"""
import math
import random

import pygame

import art

TILE = 48
RISE = 30            # how many pixels a wall face rises above its own tile
COURSE = 14          # height of one row of bricks
FLOOR_STONE = (88, 86, 86)
GROUT = (14, 15, 20)
FACE_STONE = (112, 108, 118)
ROCK = (27, 26, 33)
RIM = (136, 132, 146)
MOSS = (58, 92, 52)
WATER = (8, 14, 26)
DARK_LIGHT = (46, 54, 84)      # the cold light in places no hero can see
SIZES = [[2, 2], [2, 2], [4, 2], [2, 4], [3, 2], [2, 3], [2, 1], [1, 2], [1, 1]]


def is_wall(letters, col, row):
    """receives the grid of letters the party sees and a col/row; returns True if that spot is wall (outside the room counts as wall)."""
    if row < 0 or row >= len(letters) or col < 0 or col >= len(letters[0]):
        return True
    return letters[row][col] == "#"


def layer(width, height):
    """receives a size; returns an empty see-through picture to paint soft things on."""
    return pygame.Surface((max(1, int(width)), max(1, int(height))), pygame.SRCALPHA)


def soft_blob(surface, x, y, width, height, color, alpha):
    """receives a picture, a position, a size, a color and a see-through amount; paints a soft oval stain there; returns nothing."""
    patch = layer(width, height)
    pygame.draw.ellipse(patch, (color[0], color[1], color[2], alpha), patch.get_rect())
    surface.blit(patch, (int(x), int(y)))


def grain():
    """receives nothing; returns a picture of fine random speckles that makes flat color look like rough stone (built once)."""
    if "grain" not in art.ART["cache"]:
        dice = random.Random(99)
        picture = layer(128, 128)
        for x in range(128):
            for y in range(128):
                value = dice.choice([0, 0, 255])
                picture.set_at((x, y), (value, value, value, dice.randint(0, 20)))
        art.ART["cache"]["grain"] = picture
    return art.ART["cache"]["grain"]


def add_grain(surface):
    """receives a picture; covers it with the stone speckle; returns nothing."""
    speckle = grain()
    for x in range(0, surface.get_width(), 128):
        for y in range(0, surface.get_height(), 128):
            surface.blit(speckle, (x, y))


# ================================================================ the floor

def slab_fits(used, ux, uy, size):
    """receives the grid of used half-tiles, a spot and a slab size; returns True if a slab that size fits there."""
    for row in range(uy, uy + size[1]):
        for col in range(ux, ux + size[0]):
            if row >= len(used) or col >= len(used[0]) or used[row][col]:
                return False
    return True


def pick_size(used, ux, uy, dice):
    """receives the used grid, a spot and a random source; returns a random slab size that fits (a small one if nothing else does)."""
    for attempt in range(4):
        size = dice.choice(SIZES)
        if slab_fits(used, ux, uy, size):
            return size
    return [1, 1]


def slab_plan(cols, rows, dice):
    """receives the room size in tiles and a random source; returns a list of [x, y, width, height] flagstones of mixed sizes that cover the floor."""
    used = []
    for row in range(rows * 2):
        used.append([False] * (cols * 2))
    slabs = []
    for uy in range(rows * 2):
        for ux in range(cols * 2):
            if used[uy][ux]:
                continue
            size = pick_size(used, ux, uy, dice)
            for row in range(uy, uy + size[1]):
                for col in range(ux, ux + size[0]):
                    used[row][col] = True
            slabs.append([ux * 24, uy * 24, size[0] * 24, size[1] * 24])
    return slabs


def scratch(surface, x, y, dice, color):
    """receives a picture, a start point, a random source and a color; scratches one wandering crack; returns nothing."""
    for step in range(dice.randint(2, 5)):
        next_x = x + dice.randint(-10, 10)
        next_y = y + dice.randint(-8, 8)
        pygame.draw.line(surface, color, (x, y), (next_x, next_y), 1)
        x = next_x
        y = next_y


def paint_slab(surface, slab, dice):
    """receives a picture, one [x, y, width, height] flagstone and a random source; paints the worn stone with lit and shadowed edges; returns nothing."""
    color = art.tint(FLOOR_STONE, dice.randint(-18, 8))
    if dice.randint(1, 5) == 1:
        color = (art.clamp(color[0] - 8), color[1], art.clamp(color[2] + 8))
    left = slab[0] + 1 + dice.randint(0, 2)
    top = slab[1] + 1 + dice.randint(0, 2)
    right = slab[0] + slab[2] - 2 - dice.randint(0, 2)
    bottom = slab[1] + slab[3] - 2 - dice.randint(0, 2)
    points = [(left, top + dice.randint(0, 2)), (right, top), (right - dice.randint(0, 2), bottom), (left, bottom)]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.line(surface, art.tint(color, 26), points[0], points[1], 1)
    pygame.draw.line(surface, art.tint(color, 14), points[0], points[3], 1)
    pygame.draw.line(surface, art.tint(color, -30), points[3], points[2], 2)
    pygame.draw.line(surface, art.tint(color, -24), points[1], points[2], 1)
    if dice.randint(1, 3) == 1:
        scratch(surface, dice.randint(left, right), dice.randint(top, bottom), dice, art.tint(color, -34))
    if dice.randint(1, 4) == 1:
        soft_blob(surface, left, top, slab[2] - 4, slab[3] - 4, (0, 0, 0), dice.randint(18, 46))


def paint_puddle(surface, spot, dice):
    """receives a picture, a middle point and a random source; paints a dark puddle with a pale reflection; returns [x, y, width, height]."""
    width = dice.randint(44, 104)
    height = dice.randint(20, 42)
    patch = layer(width, height)
    box = patch.get_rect()
    pygame.draw.ellipse(patch, (0, 0, 0, 110), box)
    pygame.draw.ellipse(patch, (WATER[0], WATER[1], WATER[2], 190), box.inflate(-4, -4))
    pygame.draw.ellipse(patch, (52, 68, 96, 90), pygame.Rect(width * 0.18, height * 0.2, width * 0.5, height * 0.4))
    pygame.draw.arc(patch, (176, 196, 222, 170), box.inflate(-10, -8), 1.7, 2.9, 2)
    pygame.draw.line(patch, (220, 232, 246, 200), (width * 0.6, height * 0.34), (width * 0.72, height * 0.3), 1)
    surface.blit(patch, (spot[0] - width // 2, spot[1] - height // 2))
    return [spot[0] - width // 2, spot[1] - height // 2, width, height]


def paint_debris(surface, spot, dice):
    """receives a picture, a middle point and a random source; scatters a few broken stones (and sometimes a bone) there; returns nothing."""
    for number in range(dice.randint(2, 5)):
        x = spot[0] + dice.randint(-18, 18)
        y = spot[1] + dice.randint(-18, 18)
        size = dice.randint(2, 4)
        stone = [(x, y - size), (x + size, y), (x, y + size), (x - size, y + 1)]
        pygame.draw.polygon(surface, art.tint(FLOOR_STONE, dice.randint(-40, 20)), stone)
        pygame.draw.line(surface, GROUT, (x - size, y + size + 1), (x + size, y + size + 1), 1)
    if dice.randint(1, 3) == 1:
        pygame.draw.line(surface, art.BONE, (spot[0] - 7, spot[1] + 4), (spot[0] + 7, spot[1] - 3), 2)
        pygame.draw.circle(surface, art.BONE, (spot[0] - 7, spot[1] + 4), 2)
        pygame.draw.circle(surface, art.BONE, (spot[0] + 7, spot[1] - 3), 2)


def random_spot(cols, rows, dice):
    """AI-assisted: receives the map size in tiles and a random source; returns a random pixel point [x, y] somewhere on the map."""
    return [dice.randint(TILE, (cols - 1) * TILE), dice.randint(TILE, (rows - 1) * TILE)]


def paint_floor(surface, cols, rows, dice):
    """AI-assisted: receives a picture, the map size in tiles and a random source; paints wet flagstone floor over the whole map (rock is painted over it later); returns the list of puddles."""
    surface.fill(GROUT)
    for slab in slab_plan(cols, rows, dice):
        paint_slab(surface, slab, dice)
    area = cols * rows
    for number in range(area // 13):
        spot = random_spot(cols, rows, dice)
        soft_blob(surface, spot[0] - 40, spot[1] - 26, 80, 52, (0, 0, 0), dice.randint(24, 54))
    for number in range(area // 18):
        spot = random_spot(cols, rows, dice)
        soft_blob(surface, spot[0] - 22, spot[1] - 14, dice.randint(24, 50), dice.randint(14, 30), MOSS, dice.randint(30, 64))
    for number in range(area // 23):
        paint_debris(surface, random_spot(cols, rows, dice), dice)
    puddles = []
    for number in range(area // 22):
        puddles.append(paint_puddle(surface, random_spot(cols, rows, dice), dice))
    add_grain(surface)
    return puddles


def floor_base(cols, rows, seed):
    """AI-assisted: receives the map size and the dungeon's seed; returns [floor picture, puddles], painted once per dungeon and then reused so the floor never changes under the party."""
    key = "floor" + str(seed) + "x" + str(cols) + "x" + str(rows)
    if key not in art.ART["cache"]:
        surface = pygame.Surface((cols * TILE, rows * TILE))
        puddles = paint_floor(surface, cols, rows, random.Random(seed))
        art.ART["cache"][key] = [surface, puddles]
    return art.ART["cache"][key]


def paint_grid_hints(surface, letters):
    """receives a picture and the letters grid; rules a clear grid over every floor tile (a dark line and a pale line, like a groove) so the party can count tiles; returns how many tiles were ruled."""
    marks = layer(surface.get_width(), surface.get_height())
    count = 0
    for row in range(len(letters)):
        for col in range(len(letters[0])):
            if is_wall(letters, col, row):
                continue
            x = col * TILE
            y = row * TILE
            pygame.draw.line(marks, (0, 0, 0, 120), (x, y + TILE - 1), (x + TILE - 1, y + TILE - 1), 1)
            pygame.draw.line(marks, (0, 0, 0, 120), (x + TILE - 1, y), (x + TILE - 1, y + TILE - 1), 1)
            pygame.draw.line(marks, (210, 214, 226, 46), (x, y), (x + TILE - 2, y), 1)
            pygame.draw.line(marks, (210, 214, 226, 46), (x, y), (x, y + TILE - 2), 1)
            count += 1
    surface.blit(marks, (0, 0))
    return count


# ================================================================ shadows at the foot of walls

def gradient(width, height, side, strength):
    """receives a size, which side is darkest ("top", "left", "right" or "bottom") and a strength; returns a shadow strip that fades away from that side."""
    strip = layer(width, height)
    if side == "top" or side == "bottom":
        depth = height
    else:
        depth = width
    for step in range(depth):
        alpha = int(strength * (1 - step / depth) ** 1.6)
        if side == "top":
            pygame.draw.line(strip, (0, 0, 0, alpha), (0, step), (width, step), 1)
        elif side == "bottom":
            pygame.draw.line(strip, (0, 0, 0, alpha), (0, height - 1 - step), (width, height - 1 - step), 1)
        elif side == "left":
            pygame.draw.line(strip, (0, 0, 0, alpha), (step, 0), (step, height), 1)
        else:
            pygame.draw.line(strip, (0, 0, 0, alpha), (width - 1 - step, 0), (width - 1 - step, height), 1)
    return strip


def cached_gradient(width, height, side, strength):
    """AI-assisted: receives the same things as gradient(); returns that shadow strip, built only once."""
    key = "gradient" + str(width) + side + str(height) + "x" + str(strength)
    if key not in art.ART["cache"]:
        art.ART["cache"][key] = gradient(width, height, side, strength)
    return art.ART["cache"][key]


def paint_wall_shadows(surface, letters):
    """receives a picture and the letters grid; darkens the floor along the foot of every wall, deepest under the tall north faces; returns nothing."""
    top = gradient(TILE, 30, "top", 210)
    left = gradient(20, TILE, "left", 150)
    right = gradient(14, TILE, "right", 110)
    bottom = gradient(TILE, 12, "bottom", 130)
    for row in range(len(letters)):
        for col in range(len(letters[0])):
            if is_wall(letters, col, row):
                continue
            x = col * TILE
            y = row * TILE
            if is_wall(letters, col, row - 1):
                surface.blit(top, (x, y))
            if is_wall(letters, col - 1, row):
                surface.blit(left, (x, y))
            if is_wall(letters, col + 1, row):
                surface.blit(right, (x + TILE - 14, y))
            if is_wall(letters, col, row + 1):
                surface.blit(bottom, (x, y + TILE - 12))


# ================================================================ walls

def paint_rock_top(surface, letters, col, row, dice):
    """receives a picture, the letters grid, a wall tile and a random source; paints the dark top of the wall with a pale rim where it meets the floor; returns nothing."""
    x = col * TILE
    y = row * TILE
    pygame.draw.rect(surface, ROCK, pygame.Rect(x, y, TILE, TILE))
    for number in range(10):
        spot = (x + dice.randint(2, TILE - 3), y + dice.randint(2, TILE - 3))
        pygame.draw.circle(surface, art.tint(ROCK, dice.randint(4, 16)), spot, dice.randint(1, 3))
    split = dice.randint(14, 34)
    pygame.draw.line(surface, art.tint(ROCK, -12), (x, y + split), (x + TILE, y + split), 2)
    pygame.draw.line(surface, art.tint(ROCK, 12), (x, y + split + 2), (x + TILE, y + split + 2), 1)
    pygame.draw.line(surface, art.tint(ROCK, -12), (x + split, y), (x + split, y + split), 2)
    if not is_wall(letters, col, row - 1):
        pygame.draw.line(surface, RIM, (x, y + 1), (x + TILE - 1, y + 1), 3)
        pygame.draw.line(surface, art.tint(ROCK, 20), (x, y + 5), (x + TILE - 1, y + 5), 3)
    if not is_wall(letters, col - 1, row):
        pygame.draw.line(surface, art.tint(RIM, -20), (x + 1, y), (x + 1, y + TILE - 1), 3)
    if not is_wall(letters, col + 1, row):
        pygame.draw.line(surface, art.tint(RIM, -30), (x + TILE - 2, y), (x + TILE - 2, y + TILE - 1), 3)


def brick_tint(brick_x, brick_y):
    """receives a brick's place along the wall and its height; returns how much lighter or darker that brick is (always the same for the same brick)."""
    return (brick_x * 37 + brick_y * 91) % 23 - 13


def paint_course(surface, x, y, height, number):
    """receives a picture, the left and top of one row of bricks in a tile, its height and the row number; paints the bricks so they line up with the next tile; returns nothing."""
    pygame.draw.rect(surface, GROUT, pygame.Rect(x, y, TILE, height))
    start = x - 24 * (number % 2) - (x % 48)
    for left in range(start, x + TILE, 48):
        color = art.tint(FACE_STONE, brick_tint(left // 24, y))
        brick = pygame.Rect(left + 1, y + 1, 46, height - 2)
        pygame.draw.rect(surface, color, brick, 0, 2)
        pygame.draw.line(surface, art.tint(color, 24), (brick.x + 1, brick.y), (brick.right - 2, brick.y), 1)
        pygame.draw.line(surface, art.tint(color, -26), (brick.x + 1, brick.bottom - 1), (brick.right - 2, brick.bottom - 1), 1)


def paint_damp(surface, x, top, bottom, dice):
    """receives a picture, the left, top and bottom of a wall face and a random source; adds wet streaks running down and moss at the foot; returns nothing."""
    for number in range(dice.randint(1, 3)):
        streak_x = x + dice.randint(4, TILE - 5)
        length = dice.randint(14, bottom - top - 6)
        soft_blob(surface, streak_x - 3, top, 7, length, (4, 8, 18), dice.randint(70, 130))
        pygame.draw.line(surface, (130, 144, 168), (streak_x + 2, top + 3), (streak_x + 2, top + length // 2), 1)
    for number in range(dice.randint(0, 3)):
        soft_blob(surface, x + dice.randint(0, TILE - 16), bottom - dice.randint(8, 14), dice.randint(12, 22),
                  dice.randint(8, 14), MOSS, dice.randint(90, 150))


def paint_face(surface, letters, col, row, dice):
    """receives a picture, the letters grid, a wall tile with floor to its south and a random source; paints the tall brick face rising from the floor; returns the y of the face's top."""
    x = col * TILE
    bottom = row * TILE + TILE
    top = row * TILE
    if row > 0 and is_wall(letters, col, row - 1):
        top = top - RISE
    surface.set_clip(pygame.Rect(x, top, TILE, bottom - top))
    pygame.draw.rect(surface, ROCK, pygame.Rect(x, top, TILE, 9))
    y = top + 9
    number = 0
    while y < bottom:
        paint_course(surface, x, y, min(COURSE, bottom - y), number)
        y += COURSE
        number += 1
    paint_damp(surface, x, top + 9, bottom, dice)
    surface.blit(cached_gradient(TILE, 20, "bottom", 105), (x, bottom - 20))
    pygame.draw.line(surface, RIM, (x, top + 8), (x + TILE - 1, top + 8), 2)
    surface.set_clip(None)
    return top


def has_torch(col, row):
    """receives a wall face tile; returns True if a wall torch hangs on this face (about every fourth face)."""
    return (col * 3 + row) % 4 == 1


def paint_sconce(surface, x, y):
    """receives a picture and a point on a wall face; paints the iron bracket and unlit torch that hangs there; returns nothing."""
    pygame.draw.rect(surface, (30, 28, 32), pygame.Rect(x - 5, y + 8, 10, 4))
    pygame.draw.rect(surface, art.WOOD_DARK, pygame.Rect(x - 2, y - 4, 4, 14))
    pygame.draw.rect(surface, (30, 28, 32), pygame.Rect(x - 3, y - 6, 6, 4))


def near_floor(letters, col, row):
    """AI-assisted: receives the letters grid and a wall tile; returns True if any of the eight tiles around it is floor (rock far from any room is left as black void)."""
    for near_row in range(row - 1, row + 2):
        for near_col in range(col - 1, col + 2):
            if not is_wall(letters, near_col, near_row):
                return True
    return False


def tile_dice(seed, col, row):
    """AI-assisted: receives the dungeon's seed and a tile; returns a random source that is always the same for that tile, so walls look the same every time they are repainted."""
    return random.Random(seed * 7919 + col * 131 + row * 17)


def paint_walls(surface, letters, seed):
    """AI-assisted: receives a picture, the letters grid and the dungeon's seed; paints every wall (dark tops first, then the tall faces over them); returns the list of torches [col, row, x, y]."""
    faces = []
    for row in range(len(letters)):
        for col in range(len(letters[0])):
            if not is_wall(letters, col, row):
                continue
            elif not near_floor(letters, col, row):
                pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(col * TILE, row * TILE, TILE, TILE))
            elif is_wall(letters, col, row + 1):
                paint_rock_top(surface, letters, col, row, tile_dice(seed, col, row))
            else:
                faces.append([col, row])
    torches = []
    for face in faces:
        top = paint_face(surface, letters, face[0], face[1], tile_dice(seed, face[0], face[1]))
        if has_torch(face[0], face[1]):
            torches.append([face[0], face[1], face[0] * TILE + TILE // 2, top + 30])
            paint_sconce(surface, face[0] * TILE + TILE // 2, top + 30)
    return torches


def build_room(letters, seed):
    """AI-assisted: receives the grid of letters the party sees and the dungeon's seed; paints the whole known dungeon (floor, shadows, walls); returns {"surface", "puddles", "torches"}."""
    base = floor_base(len(letters[0]), len(letters), seed)
    surface = base[0].copy()
    paint_grid_hints(surface, letters)
    paint_wall_shadows(surface, letters)
    torches = paint_walls(surface, letters, seed)
    return {"surface": surface, "puddles": base[1], "torches": torches}


# ================================================================ light

def light_color(seen, lights, col, row, tick):
    """AI-assisted: receives the vision grid, the light sources [col, row, strength], a col/row and the frame count; returns the color of the light on that tile (warm and flickering near light, cold and dark where unseen)."""
    if not seen[row][col]:
        return DARK_LIGHT
    level = 70
    for light in lights:
        near = max(abs(col - light[0]), abs(row - light[1]))
        level = max(level, light[2] - near * 20)
    level = level + int(7 * math.sin(tick / 6.0 + col * 1.7 + row * 0.9))
    return (art.clamp(level), art.clamp(level * 0.9), art.clamp(level * 0.74))


def light_grid(seen, lights, tick, box):
    """AI-assisted: receives the vision grid, the light sources, the frame count and the visible tiles [left, top, right, bottom]; returns a tiny picture with one pixel of light per visible tile."""
    small = pygame.Surface((box[2] - box[0] + 1, box[3] - box[1] + 1))
    for row in range(box[1], box[3] + 1):
        for col in range(box[0], box[2] + 1):
            small.set_at((col - box[0], row - box[1]), light_color(seen, lights, col, row, tick))
    return small


def draw_flame(x, y, tick, scale):
    """AI-assisted: receives a point on the screen, the frame count and the zoom; draws a flickering flame with a warm glow; returns nothing."""
    screen = art.ART["screen"]
    sway = math.sin(tick / 4.0 + x) * 2 * scale
    tall = (11 + math.sin(tick / 3.0 + x * 0.5) * 2) * scale
    width = 4 * scale
    rise = 5 * scale
    art.torch_glow(x, y - rise, max(12, int(54 * scale / 6) * 6))
    pygame.draw.polygon(screen, art.ORANGE, [(x - width, y - rise), (x + width, y - rise), (x + sway, y - rise - tall)])
    pygame.draw.polygon(screen, art.GOLD, [(x - width / 2, y - rise), (x + width / 2, y - rise),
                                           (x + sway * 0.6, y - rise - tall * 0.6)])


def draw_ripple(x, y, life):
    """receives a point on the screen and how many frames the ripple has left (30 = new); draws a drip ring spreading on a puddle; returns nothing."""
    grow = 30 - life
    shade_value = 60 + life * 4
    ring = pygame.Rect(0, 0, 4 + grow * 1.1, 2 + grow * 0.55)
    ring.center = (int(x), int(y))
    pygame.draw.ellipse(art.ART["screen"], (shade_value, shade_value + 12, shade_value + 30), ring, 1)
