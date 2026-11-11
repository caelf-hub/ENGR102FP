"""art.py - the look of the game: palette, fonts, textures, standees, tiles, icons, cards.

Everything here is drawn in code with pygame.draw. No image files are loaded.
The style is inspired by dungeon-crawl board games: aged parchment, dark slate cards
with the initiative in a centre medallion, stone flagstone tiles, and figures that
stand on coloured bases like cardboard standees.

ui.py decides WHERE things go and handles the mouse and keyboard.
art.py only knows HOW each thing looks.
"""
import math
import random

import pygame

# ---------------------------------------------------------------- palette (one place)
NIGHT = (14, 12, 16)
STONE_DARK = (24, 21, 24)
FLOOR = (104, 96, 88)
WALL = (50, 45, 47)
WALL_CAP = (84, 76, 74)
DARKNESS = (6, 7, 14)
PARCHMENT = (226, 208, 170)
PARCHMENT_DARK = (186, 164, 122)
LEATHER = (40, 33, 30)
SLATE = (44, 42, 52)
INK = (44, 32, 22)
BRASS = (186, 146, 62)
BRASS_DARK = (112, 84, 34)
GOLD = (246, 210, 96)
CRIMSON = (190, 40, 48)
BLOOD = (112, 20, 28)
STEEL = (160, 168, 180)
STEEL_DARK = (92, 98, 112)
WHITE = (247, 245, 238)
FUR_SHADE = (214, 210, 200)
BONE = (224, 218, 200)
GREEN = (86, 164, 96)
BLUE = (74, 116, 196)
PURPLE = (140, 88, 178)
TEAL = (50, 116, 118)
SKIN = (228, 186, 152)
WOOD = (116, 80, 48)
WOOD_DARK = (70, 46, 28)
ORC = (104, 150, 76)
GOBLIN = (170, 182, 78)
SHADOW = (54, 42, 82)
BLACK = (12, 10, 14)
CYAN = (112, 214, 230)
ORANGE = (240, 142, 50)
PINK = (236, 120, 140)

COLOR_NAMES = {"crimson": CRIMSON, "white": WHITE, "gold": GOLD, "green": GREEN}
ELEMENT_COLORS = {"fire": ORANGE, "frost": CYAN, "light": GOLD}
ACTION_COLORS = {"attack": (240, 104, 92), "move": (134, 184, 244), "heal": (124, 214, 136),
                 "shield": (206, 212, 222)}
GLOW_COLORS = {"attack": CRIMSON, "move": (96, 160, 240), "heal": GREEN, "shield": STEEL, "gold": GOLD}
CLASS_COLORS = {"leader": (168, 44, 52), "tank": BLUE, "archer": GREEN, "mage": PURPLE, "rogue": TEAL}

# Everything art.py needs to remember (the screen, fonts and pictures built once).
ART = {"screen": None, "fonts": {}, "tick": 0, "cache": {}}


# ================================================================ setup

def pick_font(names, size, bold):
    """AI-assisted: receives a list of font names, a size and bold True/False; returns the first of those fonts found on this computer."""
    for name in names:
        if pygame.font.match_font(name) is not None:
            return pygame.font.SysFont(name, size, bold)
    return pygame.font.SysFont("georgia", size, bold)


def make_fonts():
    """AI-assisted: receives nothing; builds every font the game uses and returns how many were made."""
    book = ["palatinolinotype", "bookantiqua", "georgia"]
    gothic = ["oldenglishtext", "oldenglishtextmt", "blackadderitc"] + book
    sizes = {"tiny": 12, "small": 14, "body": 17}
    for name in sizes:
        ART["fonts"][name] = pick_font(book, sizes[name], False)
    bold_sizes = {"bold": 14, "head": 21, "big": 34}
    for name in bold_sizes:
        ART["fonts"][name] = pick_font(book, bold_sizes[name], True)
    ART["fonts"]["huge"] = pick_font(gothic, 84, False)
    ART["fonts"]["title"] = pick_font(gothic, 40, False)
    return len(ART["fonts"])


def setup(screen):
    """AI-assisted: receives the game window; builds the fonts and textures once; returns how many pictures were built."""
    ART["screen"] = screen
    make_fonts()
    cache = ART["cache"]
    cache["parchment"] = blotchy(noise_tile(256, PARCHMENT, 6, 1), 2, 90)
    cache["leather"] = blotchy(noise_tile(192, LEATHER, 5, 3), 4, 40)
    cache["slate"] = blotchy(noise_tile(192, SLATE, 5, 5), 6, 40)
    cache["brass"] = noise_tile(64, BRASS, 8, 7)
    for number in range(8):
        cache["floor" + str(number)] = floor_tile(48, 20 + number)
        cache["wall" + str(number)] = wall_tile(48, 40 + number)
    build_overlays(48)
    return len(cache)


def build_overlays(size):
    """AI-assisted: receives the tile size; builds the see-through pictures stamped over tiles (darkness and wall shadows); returns nothing."""
    dark = pygame.Surface((size, size), pygame.SRCALPHA)
    dark.fill((DARKNESS[0], DARKNESS[1], DARKNESS[2], 176))
    top = pygame.Surface((size, 14), pygame.SRCALPHA)
    left = pygame.Surface((14, size), pygame.SRCALPHA)
    for depth in range(14):
        pygame.draw.line(top, (0, 0, 0, 120 - depth * 8), (0, depth), (size, depth), 1)
        pygame.draw.line(left, (0, 0, 0, 90 - depth * 6), (depth, 0), (depth, size), 1)
    ART["cache"]["dark"] = dark
    ART["cache"]["shadow_top"] = top
    ART["cache"]["shadow_left"] = left


def stamp(name, rect):
    """AI-assisted: receives an overlay name ("dark", "shadow_top" or "shadow_left") and a tile rectangle; stamps it over the tile; returns nothing."""
    ART["screen"].blit(ART["cache"][name], rect)


def clamp(value):
    """AI-assisted: receives a number; returns it squeezed into the color range 0-255."""
    return max(0, min(255, int(value)))


def tint(color, amount):
    """AI-assisted: receives a color and an amount (+ lighter, - darker); returns the shifted color."""
    return (clamp(color[0] + amount), clamp(color[1] + amount), clamp(color[2] + amount))


def pulse():
    """AI-assisted: receives nothing; returns a number that gently rises and falls between 0 and 1 for glowing effects."""
    return 0.5 + 0.5 * math.sin(ART["tick"] / 9.0)


# ================================================================ textures (built once)

def noise_tile(size, base, spread, seed):
    """AI-assisted: receives a size, a base color, how much it may vary and a seed; returns a speckled square picture."""
    dice = random.Random(seed)
    surface = pygame.Surface((size, size))
    for x in range(size):
        for y in range(size):
            surface.set_at((x, y), tint(base, dice.randint(-spread, spread)))
    return surface


def blotchy(surface, seed, count):
    """AI-assisted: receives a picture, a seed and a count; adds that many soft stains so it looks aged; returns the picture."""
    dice = random.Random(seed)
    size = surface.get_width()
    for number in range(count):
        radius = dice.randint(4, 16)
        stain = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        shade_value = dice.choice([0, 0, 255])
        pygame.draw.circle(stain, (shade_value, shade_value, shade_value, dice.randint(3, 8)),
                           (radius, radius), radius)
        surface.blit(stain, (dice.randint(-8, size - 8), dice.randint(-8, size - 8)))
    return surface


def crack(surface, dice, color):
    """AI-assisted: receives a tile picture, a random source and a color; scratches one wandering crack into it; returns nothing."""
    size = surface.get_width()
    x = dice.randint(6, size - 6)
    y = dice.randint(6, size - 6)
    for step in range(dice.randint(2, 4)):
        next_x = x + dice.randint(-9, 9)
        next_y = y + dice.randint(-9, 9)
        pygame.draw.line(surface, color, (x, y), (next_x, next_y), 1)
        x = next_x
        y = next_y


def floor_tile(size, seed):
    """AI-assisted: receives a size and a seed; returns one worn stone flagstone picture."""
    dice = random.Random(seed)
    surface = noise_tile(size, tint(FLOOR, dice.randint(-6, 6)), 6, seed)
    blotchy(surface, seed, 5)
    for number in range(dice.randint(0, 1)):
        crack(surface, dice, tint(FLOOR, -26))
    for number in range(dice.randint(1, 4)):
        spot = (dice.randint(4, size - 5), dice.randint(4, size - 5))
        pygame.draw.circle(surface, tint(FLOOR, dice.choice([-26, 16])), spot, dice.randint(1, 2))
    pygame.draw.line(surface, tint(FLOOR, 24), (1, 1), (size - 2, 1), 1)
    pygame.draw.line(surface, tint(FLOOR, 24), (1, 1), (1, size - 2), 1)
    pygame.draw.line(surface, tint(FLOOR, -34), (1, size - 2), (size - 2, size - 2), 1)
    pygame.draw.line(surface, tint(FLOOR, -34), (size - 2, 1), (size - 2, size - 2), 1)
    pygame.draw.rect(surface, tint(FLOOR, -62), pygame.Rect(0, 0, size, size), 1)
    return surface


def wall_tile(size, seed):
    """AI-assisted: receives a size and a seed; returns one dungeon wall block picture (lighter top, bricks on the front)."""
    dice = random.Random(seed)
    surface = noise_tile(size, WALL, 5, seed)
    pygame.draw.rect(surface, WALL_CAP, pygame.Rect(0, 0, size, 13))
    for number in range(40):
        spot = (dice.randint(0, size - 1), dice.randint(0, 12))
        surface.set_at(spot, tint(WALL_CAP, dice.randint(-12, 12)))
    pygame.draw.line(surface, tint(WALL_CAP, 26), (0, 0), (size, 0), 1)
    pygame.draw.line(surface, BLACK, (0, 13), (size, 13), 1)
    pygame.draw.line(surface, tint(WALL, -22), (0, 30), (size, 30), 1)
    split = dice.randint(14, 34)
    pygame.draw.line(surface, tint(WALL, -22), (split, 14), (split, 30), 1)
    pygame.draw.line(surface, tint(WALL, -22), (size - split, 30), (size - split, size), 1)
    pygame.draw.line(surface, tint(WALL, 14), (0, 15), (size, 15), 1)
    pygame.draw.rect(surface, BLACK, pygame.Rect(0, 0, size, size), 1)
    return surface


def fill_texture(rect, name):
    """AI-assisted: receives a rectangle and a texture name; covers that area of the screen with the texture; returns the rectangle."""
    screen = ART["screen"]
    texture = ART["cache"][name]
    step = texture.get_width()
    screen.set_clip(rect)
    for x in range(rect.x - rect.x % step, rect.right, step):
        for y in range(rect.y - rect.y % step, rect.bottom, step):
            screen.blit(texture, (x, y))
    screen.set_clip(None)
    return rect


def build_panel(width, height, name):
    """AI-assisted: receives a size and a texture name; returns a rounded panel picture with darker worn edges."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    texture = ART["cache"][name]
    step = texture.get_width()
    for x in range(0, width, step):
        for y in range(0, height, step):
            surface.blit(texture, (x, y))
    for inset in range(5):
        edge = pygame.Rect(inset, inset, width - inset * 2, height - inset * 2)
        layer = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(layer, (30, 16, 6, 46 - inset * 9), edge, 1, 7)
        surface.blit(layer, (0, 0))
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), pygame.Rect(0, 0, width, height), 0, 7)
    surface.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MIN)
    return surface


def panel(rect, name, border):
    """AI-assisted: receives a rectangle, a texture name ("parchment", "leather" or "slate") and a border color; draws a framed panel; returns the rectangle."""
    key = name + str(rect.width) + "x" + str(rect.height)
    if key not in ART["cache"]:
        ART["cache"][key] = build_panel(rect.width, rect.height, name)
    ART["screen"].blit(ART["cache"][key], rect)
    pygame.draw.rect(ART["screen"], BLACK, rect, 1, 7)
    pygame.draw.rect(ART["screen"], border, rect.inflate(-2, -2), 2, 6)
    return rect


def shade(rect, color, alpha):
    """AI-assisted: receives a rectangle, a color and a see-through amount (0-255); tints that area; returns the rectangle."""
    layer = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    layer.fill((color[0], color[1], color[2], clamp(alpha)))
    ART["screen"].blit(layer, rect)
    return rect


def vignette(rect):
    """AI-assisted: receives a rectangle; darkens its edges like torchlight fading; returns the rectangle."""
    key = "vignette" + str(rect.width) + "x" + str(rect.height)
    if key not in ART["cache"]:
        layer = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for ring in range(22):
            edge = pygame.Rect(ring * 4, ring * 4, rect.width - ring * 8, rect.height - ring * 8)
            pygame.draw.rect(layer, (0, 0, 0, max(0, 120 - ring * 6)), edge, 4)
        ART["cache"][key] = layer
    ART["screen"].blit(ART["cache"][key], rect)
    return rect


def torch_glow(cx, cy, radius):
    """AI-assisted: receives a center and a radius; adds a soft warm light there; returns nothing."""
    key = "glow" + str(radius)
    if key not in ART["cache"]:
        layer = pygame.Surface((radius * 2, radius * 2))
        for ring in range(radius, 0, -6):
            warmth = int(34 * (1 - ring / radius))
            pygame.draw.circle(layer, (warmth, int(warmth * 0.8), int(warmth * 0.45)), (radius, radius), ring)
        ART["cache"][key] = layer
    ART["screen"].blit(ART["cache"][key], (cx - radius, cy - radius), None, pygame.BLEND_RGB_ADD)


def draw_backdrop():
    """AI-assisted: receives nothing; fills the whole screen with a dark dungeon wall for the menu screens; returns nothing."""
    screen = ART["screen"]
    if "backdrop" not in ART["cache"]:
        picture = pygame.Surface(screen.get_size())
        for x in range(0, picture.get_width(), 48):
            for y in range(0, picture.get_height(), 48):
                picture.blit(ART["cache"]["wall" + str((x // 48 * 3 + y // 48 * 5) % 8)], (x, y))
        dark = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        dark.fill((8, 6, 10, 150))
        picture.blit(dark, (0, 0))
        ART["cache"]["backdrop"] = picture
    screen.blit(ART["cache"]["backdrop"], (0, 0))
    vignette(screen.get_rect())


# ================================================================ text

def text(words, x, y, size, color, anchor):
    """AI-assisted: receives words, a position, a font name, a color and "left", "center" or "right"; draws the words and returns their rectangle."""
    image = ART["fonts"][size].render(str(words), True, color)
    rect = image.get_rect()
    if anchor == "center":
        rect.center = (int(x), int(y))
    elif anchor == "right":
        rect.topright = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    ART["screen"].blit(image, rect)
    return rect


def text_outline(words, x, y, size, color, anchor):
    """AI-assisted: receives the same things as text(); draws the words with a dark outline so they read on any background; returns their rectangle."""
    for step in [[-2, 0], [2, 0], [0, -2], [0, 2], [-1, -1], [1, 1], [-1, 1], [1, -1]]:
        text(words, x + step[0], y + step[1], size, BLACK, anchor)
    return text(words, x, y, size, color, anchor)


def wrap_text(words, size, width):
    """AI-assisted: receives a sentence, a font name and a pixel width; returns the sentence split into lines that fit."""
    font = ART["fonts"][size]
    lines = []
    line = ""
    for word in str(words).split(" "):
        trial = (line + " " + word).strip()
        if font.size(trial)[0] <= width or line == "":
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def ribbon(cx, cy, width, words, color):
    """AI-assisted: receives a center, a width, some words and a color; draws a heading ribbon with notched ends; returns nothing."""
    half = width // 2
    points = [(cx - half, cy - 15), (cx + half, cy - 15), (cx + half - 12, cy), (cx + half, cy + 15),
              (cx - half, cy + 15), (cx - half + 12, cy)]
    pygame.draw.polygon(ART["screen"], color, points)
    pygame.draw.polygon(ART["screen"], GOLD, points, 2)
    text(words, cx, cy, "head", GOLD, "center")


def divider(cx, y, width):
    """AI-assisted: receives a center x, a y and a width; draws a brass line with a diamond in the middle; returns nothing."""
    screen = ART["screen"]
    pygame.draw.line(screen, BRASS, (cx - width // 2, y), (cx + width // 2, y), 2)
    pygame.draw.polygon(screen, GOLD, [(cx, y - 7), (cx + 7, y), (cx, y + 7), (cx - 7, y)])
    pygame.draw.polygon(screen, BRASS_DARK, [(cx, y - 7), (cx + 7, y), (cx, y + 7), (cx - 7, y)], 1)


# ================================================================ buttons and bars

def draw_plate(rect, label, state):
    """AI-assisted: receives a rectangle, a label and "normal", "hot", "on" or "off"; draws a brass button plate; returns the rectangle."""
    screen = ART["screen"]
    fill = BRASS
    if state == "hot":
        fill = tint(BRASS, 34)
    elif state == "on":
        fill = GOLD
    elif state == "off":
        fill = (112, 100, 82)
    pygame.draw.rect(screen, fill, rect, 0, 6)
    pygame.draw.rect(screen, tint(fill, 30), pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 2 - 2), 0, 5)
    pygame.draw.rect(screen, BLACK, rect, 1, 6)
    pygame.draw.rect(screen, tint(fill, -60), rect.inflate(-2, -2), 1, 5)
    size = "bold"
    if ART["fonts"]["bold"].size(label)[0] > rect.width - 6:
        size = "tiny"
    text(label, rect.centerx, rect.centery, size, INK, "center")
    return rect


def draw_button(button):
    """AI-assisted: receives a button dictionary; draws it (brighter under the mouse) and returns its rectangle."""
    state = "normal"
    if button["rect"].collidepoint(pygame.mouse.get_pos()):
        state = "hot"
    return draw_plate(button["rect"], button["label"], state)


def draw_bar(rect, value, top, color):
    """AI-assisted: receives a rectangle, a value, its maximum and a color; draws a filled bar with a notch per point; returns nothing."""
    screen = ART["screen"]
    pygame.draw.rect(screen, (30, 22, 18), rect, 0, 4)
    if top > 0 and value > 0:
        fill = pygame.Rect(rect.x + 1, rect.y + 1, int((rect.width - 2) * value / top), rect.height - 2)
        pygame.draw.rect(screen, color, fill, 0, 3)
        pygame.draw.line(screen, tint(color, 50), (fill.x + 2, fill.y + 1), (fill.right - 3, fill.y + 1), 1)
    for notch in range(1, top):
        x = rect.x + int(rect.width * notch / top)
        pygame.draw.line(screen, (30, 22, 18), (x, rect.y + 1), (x, rect.bottom - 2), 1)
    pygame.draw.rect(screen, BLACK, rect, 1, 4)


def draw_pips(cx, y, count, color):
    """AI-assisted: receives a center x, a y, a count and a color; draws that many small wound drops; returns nothing."""
    start = cx - (count * 7) // 2 + 3
    for index in range(count):
        pygame.draw.circle(ART["screen"], BLACK, (start + index * 7, y), 3)
        pygame.draw.circle(ART["screen"], color, (start + index * 7, y), 2)


def draw_skull(cx, cy, size, filled):
    """AI-assisted: receives a center, a size and whether this Doom step is filled; draws one skull; returns nothing."""
    screen = ART["screen"]
    color = (124, 116, 122)
    if filled:
        color = CRIMSON
        pygame.draw.circle(screen, BLOOD, (cx, cy), size + 2)
    pygame.draw.circle(screen, color, (cx, cy), size)
    pygame.draw.rect(screen, color, pygame.Rect(cx - size // 2, cy + size // 2, size, size - 1))
    pygame.draw.circle(screen, BLACK, (cx - size // 2, cy), max(1, size // 3))
    pygame.draw.circle(screen, BLACK, (cx + size // 2, cy), max(1, size // 3))


def medallion(cx, cy, radius, fill, rim):
    """AI-assisted: receives a center, a radius, a fill color and a rim color; draws a round token; returns nothing."""
    screen = ART["screen"]
    pygame.draw.circle(screen, BLACK, (cx, cy), radius + 1)
    pygame.draw.circle(screen, rim, (cx, cy), radius)
    pygame.draw.circle(screen, fill, (cx, cy), radius - 2)


# ================================================================ icons

def icon_attack(cx, cy, s, color):
    """AI-assisted: receives a center, a size and a color; draws a sword icon; returns nothing."""
    screen = ART["screen"]
    pygame.draw.line(screen, color, (cx - 0.5 * s, cy + 0.5 * s), (cx + 0.6 * s, cy - 0.6 * s), max(2, int(s * 0.28)))
    pygame.draw.line(screen, color, (cx - 0.55 * s, cy - 0.05 * s), (cx + 0.05 * s, cy + 0.55 * s), max(2, int(s * 0.2)))
    pygame.draw.circle(screen, color, (cx - 0.62 * s, cy + 0.62 * s), max(1, s * 0.16))


def icon_move(cx, cy, s, color):
    """AI-assisted: receives a center, a size and a color; draws a boot icon; returns nothing."""
    boot = [(cx - 0.35 * s, cy - 0.7 * s), (cx + 0.1 * s, cy - 0.7 * s), (cx + 0.12 * s, cy + 0.1 * s),
            (cx + 0.7 * s, cy + 0.3 * s), (cx + 0.7 * s, cy + 0.65 * s), (cx - 0.4 * s, cy + 0.65 * s)]
    pygame.draw.polygon(ART["screen"], color, boot)


def icon_heal(cx, cy, s, color):
    """AI-assisted: receives a center, a size and a color; draws a heart icon; returns nothing."""
    screen = ART["screen"]
    pygame.draw.circle(screen, color, (cx - 0.3 * s, cy - 0.2 * s), 0.36 * s)
    pygame.draw.circle(screen, color, (cx + 0.3 * s, cy - 0.2 * s), 0.36 * s)
    pygame.draw.polygon(screen, color, [(cx - 0.64 * s, cy - 0.05 * s), (cx + 0.64 * s, cy - 0.05 * s), (cx, cy + 0.7 * s)])


def icon_shield(cx, cy, s, color):
    """AI-assisted: receives a center, a size and a color; draws a shield icon; returns nothing."""
    shape = [(cx - 0.55 * s, cy - 0.65 * s), (cx + 0.55 * s, cy - 0.65 * s), (cx + 0.55 * s, cy + 0.1 * s),
             (cx, cy + 0.72 * s), (cx - 0.55 * s, cy + 0.1 * s)]
    pygame.draw.polygon(ART["screen"], color, shape)
    pygame.draw.line(ART["screen"], BLACK, (cx, cy - 0.5 * s), (cx, cy + 0.45 * s), 1)


def icon_element(name, cx, cy, s):
    """AI-assisted: receives an element name, a center and a size; draws a flame, snowflake or sun; returns nothing."""
    screen = ART["screen"]
    color = ELEMENT_COLORS[name]
    if name == "fire":
        flame = [(cx, cy - 0.8 * s), (cx + 0.5 * s, cy + 0.1 * s), (cx + 0.3 * s, cy + 0.7 * s),
                 (cx - 0.3 * s, cy + 0.7 * s), (cx - 0.5 * s, cy + 0.1 * s), (cx - 0.15 * s, cy - 0.1 * s)]
        pygame.draw.polygon(screen, color, flame)
    elif name == "frost":
        for turn in range(3):
            angle = turn * math.pi / 3
            reach_x = math.cos(angle) * 0.75 * s
            reach_y = math.sin(angle) * 0.75 * s
            pygame.draw.line(screen, color, (cx - reach_x, cy - reach_y), (cx + reach_x, cy + reach_y), 2)
    else:
        pygame.draw.circle(screen, color, (cx, cy), 0.4 * s)
        for turn in range(8):
            angle = turn * math.pi / 4
            pygame.draw.line(screen, color, (cx + math.cos(angle) * 0.55 * s, cy + math.sin(angle) * 0.55 * s),
                             (cx + math.cos(angle) * 0.85 * s, cy + math.sin(angle) * 0.85 * s), 1)


def draw_icon(name, cx, cy, s, color):
    """AI-assisted: receives an icon name, a center, a size and a color; draws that icon; returns the name."""
    if name == "attack":
        icon_attack(cx, cy, s, color)
    elif name == "move":
        icon_move(cx, cy, s, color)
    elif name == "heal":
        icon_heal(cx, cy, s, color)
    elif name == "shield":
        icon_shield(cx, cy, s, color)
    else:
        icon_element(name, cx, cy, s)
    return name


def mini_card(x, y, color, count):
    """AI-assisted: receives a position, a color and a number; draws a tiny card with the number beside it (for card piles); returns nothing."""
    card = pygame.Rect(x, y, 9, 13)
    pygame.draw.rect(ART["screen"], color, card, 0, 2)
    pygame.draw.rect(ART["screen"], BLACK, card, 1, 2)
    text(count, x + 13, y - 1, "bold", INK, "left")


# ================================================================ figures (painted once, then reused)

def paint_frodo(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints Frodo the Maltese with cape and knight's helmet; returns nothing."""
    cape = [(cx - 0.5 * s, cy + 0.1 * s), (cx + 0.5 * s, cy + 0.1 * s), (cx + 0.8 * s, cy + 0.95 * s),
            (cx - 0.8 * s, cy + 0.95 * s)]
    pygame.draw.polygon(surface, BLOOD, cape)
    pygame.draw.circle(surface, FUR_SHADE, (cx, cy + 0.55 * s), 0.6 * s)
    pygame.draw.circle(surface, WHITE, (cx - 0.04 * s, cy + 0.5 * s), 0.54 * s)
    pygame.draw.circle(surface, WHITE, (cx + 0.6 * s, cy + 0.34 * s), 0.2 * s)
    for side in [-1, 1]:
        pygame.draw.circle(surface, WHITE, (cx + side * 0.28 * s, cy + 0.98 * s), 0.17 * s)
        pygame.draw.circle(surface, FUR_SHADE, (cx + side * 0.52 * s, cy + 0.04 * s), 0.3 * s)
        pygame.draw.circle(surface, FUR_SHADE, (cx + side * 0.5 * s, cy + 0.3 * s), 0.2 * s)
    pygame.draw.circle(surface, STEEL, (cx, cy - 0.3 * s), 0.54 * s)
    pygame.draw.circle(surface, tint(STEEL, 40), (cx - 0.16 * s, cy - 0.5 * s), 0.14 * s)
    pygame.draw.circle(surface, WHITE, (cx, cy - 0.02 * s), 0.5 * s)
    paint_frodo_helmet(surface, cx, cy, s)
    paint_frodo_face(surface, cx, cy, s)


def paint_frodo_helmet(surface, cx, cy, s):
    """AI-assisted: receives a picture and Frodo's center and size; paints the helmet brim, nose guard and crimson plume; returns nothing."""
    brim = pygame.Rect(cx - 0.6 * s, cy - 0.46 * s, 1.2 * s, 0.16 * s)
    pygame.draw.rect(surface, STEEL_DARK, brim, 0, 3)
    pygame.draw.rect(surface, STEEL, pygame.Rect(cx - 0.06 * s, cy - 0.46 * s, 0.12 * s, 0.36 * s))
    pygame.draw.circle(surface, GOLD, (cx, cy - 0.38 * s), max(1, 0.07 * s))
    plume = [(cx - 0.08 * s, cy - 0.8 * s), (cx + 0.08 * s, cy - 0.8 * s),
             (cx + 0.4 * s, cy - 1.2 * s), (cx + 0.02 * s, cy - 1.06 * s)]
    pygame.draw.polygon(surface, CRIMSON, plume)


def paint_frodo_face(surface, cx, cy, s):
    """AI-assisted: receives a picture and Frodo's center and size; paints his eyes, nose and tongue; returns nothing."""
    for side in [-1, 1]:
        pygame.draw.circle(surface, BLACK, (cx + side * 0.2 * s, cy - 0.04 * s), max(1.5, 0.08 * s))
        pygame.draw.circle(surface, WHITE, (cx + side * 0.2 * s + 0.025 * s, cy - 0.065 * s), 0.028 * s)
    pygame.draw.circle(surface, FUR_SHADE, (cx, cy + 0.2 * s), 0.2 * s)
    pygame.draw.ellipse(surface, PINK, pygame.Rect(cx - 0.07 * s, cy + 0.2 * s, 0.14 * s, 0.2 * s))
    pygame.draw.circle(surface, BLACK, (cx, cy + 0.14 * s), max(1.5, 0.09 * s))


def paint_body(surface, cx, cy, s, color, skin):
    """AI-assisted: receives a picture, a center, a size, a body color and a head color; paints a simple person with a shaded side; returns nothing."""
    body = [(cx - 0.5 * s, cy + 0.9 * s), (cx + 0.5 * s, cy + 0.9 * s),
            (cx + 0.3 * s, cy - 0.05 * s), (cx - 0.3 * s, cy - 0.05 * s)]
    pygame.draw.polygon(surface, color, body)
    side = [(cx + 0.14 * s, cy - 0.05 * s), (cx + 0.3 * s, cy - 0.05 * s), (cx + 0.5 * s, cy + 0.9 * s),
            (cx + 0.24 * s, cy + 0.9 * s)]
    pygame.draw.polygon(surface, tint(color, -34), side)
    pygame.draw.line(surface, tint(color, -60), (cx - 0.36 * s, cy + 0.42 * s), (cx + 0.38 * s, cy + 0.42 * s), max(1, int(s * 0.09)))
    pygame.draw.circle(surface, skin, (cx, cy - 0.35 * s), 0.3 * s)


def paint_tank(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints Brother Biscuit with helmet, hammer and big shield; returns nothing."""
    paint_body(surface, cx, cy, s, BLUE, STEEL)
    pygame.draw.circle(surface, tint(STEEL, 40), (cx - 0.1 * s, cy - 0.46 * s), 0.08 * s)
    pygame.draw.line(surface, BLACK, (cx - 0.18 * s, cy - 0.34 * s), (cx + 0.18 * s, cy - 0.34 * s), max(1, int(s * 0.1)))
    pygame.draw.line(surface, WOOD, (cx + 0.6 * s, cy + 0.8 * s), (cx + 0.6 * s, cy - 0.5 * s), max(2, int(s * 0.12)))
    pygame.draw.rect(surface, STEEL_DARK, pygame.Rect(cx + 0.38 * s, cy - 0.74 * s, 0.46 * s, 0.3 * s), 0, 2)
    shield = [(cx - 0.82 * s, cy - 0.02 * s), (cx - 0.1 * s, cy - 0.02 * s), (cx - 0.1 * s, cy + 0.5 * s),
              (cx - 0.46 * s, cy + 0.88 * s), (cx - 0.82 * s, cy + 0.5 * s)]
    pygame.draw.polygon(surface, BRASS, shield)
    pygame.draw.polygon(surface, BRASS_DARK, shield, max(1, int(s * 0.07)))
    pygame.draw.circle(surface, BLUE, (cx - 0.46 * s, cy + 0.34 * s), 0.17 * s)


def paint_archer(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints Pip the hooded archer with a bow; returns nothing."""
    paint_body(surface, cx, cy, s, GREEN, SKIN)
    hood = [(cx - 0.42 * s, cy - 0.18 * s), (cx + 0.42 * s, cy - 0.18 * s), (cx + 0.04 * s, cy - 1.02 * s)]
    pygame.draw.polygon(surface, (44, 98, 56), hood)
    pygame.draw.circle(surface, SKIN, (cx, cy - 0.32 * s), 0.21 * s)
    for side in [-1, 1]:
        pygame.draw.circle(surface, BLACK, (cx + side * 0.08 * s, cy - 0.34 * s), max(1, 0.035 * s))
    bow = pygame.Rect(cx + 0.2 * s, cy - 0.62 * s, 0.72 * s, 1.44 * s)
    pygame.draw.arc(surface, WOOD, bow, -1.4, 1.4, max(2, int(s * 0.12)))
    pygame.draw.line(surface, WHITE, (cx + 0.62 * s, cy - 0.58 * s), (cx + 0.62 * s, cy + 0.78 * s), 1)
    pygame.draw.rect(surface, WOOD_DARK, pygame.Rect(cx - 0.56 * s, cy - 0.1 * s, 0.2 * s, 0.6 * s), 0, 2)


def paint_mage(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints Mabel the mage with pointed hat and glowing staff; returns nothing."""
    paint_body(surface, cx, cy, s, PURPLE, SKIN)
    for side in [-1, 1]:
        pygame.draw.circle(surface, BLACK, (cx + side * 0.1 * s, cy - 0.34 * s), max(1, 0.035 * s))
    hat = [(cx - 0.52 * s, cy - 0.5 * s), (cx + 0.52 * s, cy - 0.5 * s), (cx + 0.12 * s, cy - 1.24 * s)]
    pygame.draw.polygon(surface, (92, 54, 126), hat)
    pygame.draw.line(surface, GOLD, (cx - 0.52 * s, cy - 0.5 * s), (cx + 0.52 * s, cy - 0.5 * s), max(2, int(s * 0.09)))
    pygame.draw.line(surface, WOOD, (cx + 0.7 * s, cy + 0.9 * s), (cx + 0.7 * s, cy - 0.5 * s), max(2, int(s * 0.1)))
    pygame.draw.circle(surface, ORANGE, (cx + 0.7 * s, cy - 0.64 * s), 0.21 * s)
    pygame.draw.circle(surface, GOLD, (cx + 0.7 * s, cy - 0.64 * s), 0.1 * s)


def paint_rogue(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints Nettle the hooded rogue with a dagger; returns nothing."""
    dark = (28, 42, 46)
    paint_body(surface, cx, cy, s, TEAL, dark)
    pygame.draw.circle(surface, dark, (cx, cy - 0.35 * s), 0.39 * s)
    pygame.draw.circle(surface, SKIN, (cx, cy - 0.3 * s), 0.21 * s)
    pygame.draw.rect(surface, dark, pygame.Rect(cx - 0.23 * s, cy - 0.25 * s, 0.46 * s, 0.16 * s))
    for side in [-1, 1]:
        pygame.draw.circle(surface, BLACK, (cx + side * 0.09 * s, cy - 0.34 * s), max(1, 0.035 * s))
    pygame.draw.line(surface, STEEL, (cx + 0.42 * s, cy + 0.4 * s), (cx + 0.88 * s, cy - 0.18 * s), max(2, int(s * 0.12)))
    pygame.draw.line(surface, GOLD, (cx + 0.36 * s, cy + 0.26 * s), (cx + 0.58 * s, cy + 0.44 * s), max(2, int(s * 0.12)))


def paint_orc(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints an Orc Brute with tusks and a club; returns nothing."""
    paint_body(surface, cx, cy, s * 1.08, (92, 66, 46), ORC)
    pygame.draw.line(surface, BLACK, (cx - 0.24 * s, cy - 0.5 * s), (cx + 0.24 * s, cy - 0.5 * s), max(2, int(s * 0.1)))
    for side in [-1, 1]:
        pygame.draw.circle(surface, GOLD, (cx + side * 0.12 * s, cy - 0.4 * s), max(1, 0.045 * s))
        tusk = [(cx + side * 0.22 * s, cy - 0.16 * s), (cx + side * 0.1 * s, cy - 0.16 * s),
                (cx + side * 0.19 * s, cy - 0.42 * s)]
        pygame.draw.polygon(surface, WHITE, tusk)
    pygame.draw.line(surface, WOOD, (cx + 0.52 * s, cy + 0.6 * s), (cx + 0.78 * s, cy - 0.62 * s), max(3, int(s * 0.26)))
    pygame.draw.circle(surface, STEEL_DARK, (cx + 0.78 * s, cy - 0.62 * s), 0.12 * s)


def paint_goblin(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints a small Goblin Slinger with pointy ears; returns nothing."""
    paint_body(surface, cx, cy + 0.15 * s, s * 0.8, (108, 96, 54), GOBLIN)
    for side in [-1, 1]:
        ear = [(cx + side * 0.2 * s, cy - 0.22 * s), (cx + side * 0.2 * s, cy - 0.02 * s),
               (cx + side * 0.64 * s, cy - 0.32 * s)]
        pygame.draw.polygon(surface, GOBLIN, ear)
        pygame.draw.circle(surface, CRIMSON, (cx + side * 0.1 * s, cy - 0.16 * s), max(1, 0.05 * s))
    pygame.draw.line(surface, WOOD, (cx + 0.3 * s, cy + 0.3 * s), (cx + 0.7 * s, cy - 0.3 * s), max(1, int(s * 0.08)))
    pygame.draw.circle(surface, STEEL, (cx + 0.72 * s, cy - 0.36 * s), 0.11 * s)


def paint_guard(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints an armored Iron Guard with tower shield and spear; returns nothing."""
    pygame.draw.rect(surface, STEEL_DARK, pygame.Rect(cx - 0.45 * s, cy - 0.1 * s, 0.9 * s, 1.0 * s), 0, 3)
    pygame.draw.rect(surface, tint(STEEL_DARK, -26), pygame.Rect(cx + 0.14 * s, cy - 0.1 * s, 0.31 * s, 1.0 * s), 0, 3)
    pygame.draw.rect(surface, STEEL, pygame.Rect(cx - 0.3 * s, cy - 0.74 * s, 0.6 * s, 0.64 * s), 0, 3)
    pygame.draw.rect(surface, BLACK, pygame.Rect(cx - 0.2 * s, cy - 0.5 * s, 0.4 * s, 0.1 * s))
    pygame.draw.polygon(surface, CRIMSON, [(cx - 0.06 * s, cy - 0.74 * s), (cx + 0.06 * s, cy - 0.74 * s), (cx, cy - 1.02 * s)])
    pygame.draw.line(surface, WOOD, (cx + 0.64 * s, cy + 0.9 * s), (cx + 0.64 * s, cy - 0.8 * s), max(2, int(s * 0.09)))
    spear = [(cx + 0.52 * s, cy - 0.8 * s), (cx + 0.76 * s, cy - 0.8 * s), (cx + 0.64 * s, cy - 1.14 * s)]
    pygame.draw.polygon(surface, STEEL, spear)
    shield = pygame.Rect(cx - 0.82 * s, cy - 0.16 * s, 0.56 * s, 0.98 * s)
    pygame.draw.rect(surface, BLOOD, shield, 0, 3)
    pygame.draw.rect(surface, BRASS, shield, max(1, int(s * 0.07)), 3)


def paint_wolf(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints a Wolf Rider (a wolf with a small rider); returns nothing."""
    fur = (118, 110, 106)
    for leg in [-0.35, 0.0, 0.35, 0.6]:
        pygame.draw.line(surface, tint(fur, -24), (cx + leg * s, cy + 0.5 * s), (cx + leg * s, cy + 0.92 * s), max(2, int(s * 0.14)))
    pygame.draw.line(surface, fur, (cx + 0.7 * s, cy + 0.2 * s), (cx + 1.0 * s, cy - 0.12 * s), max(2, int(s * 0.16)))
    pygame.draw.ellipse(surface, fur, pygame.Rect(cx - 0.55 * s, cy + 0.05 * s, 1.3 * s, 0.6 * s))
    head = [(cx - 0.98 * s, cy + 0.22 * s), (cx - 0.4 * s, cy - 0.22 * s), (cx - 0.28 * s, cy + 0.46 * s)]
    pygame.draw.polygon(surface, fur, head)
    ear = [(cx - 0.52 * s, cy - 0.12 * s), (cx - 0.3 * s, cy - 0.1 * s), (cx - 0.36 * s, cy - 0.48 * s)]
    pygame.draw.polygon(surface, fur, ear)
    pygame.draw.circle(surface, CRIMSON, (cx - 0.56 * s, cy + 0.1 * s), max(1, 0.07 * s))
    pygame.draw.rect(surface, (92, 66, 46), pygame.Rect(cx - 0.1 * s, cy - 0.14 * s, 0.42 * s, 0.34 * s), 0, 2)
    pygame.draw.circle(surface, ORC, (cx + 0.1 * s, cy - 0.34 * s), 0.25 * s)
    pygame.draw.line(surface, STEEL, (cx + 0.36 * s, cy), (cx + 0.56 * s, cy - 0.8 * s), max(1, int(s * 0.08)))


def paint_bomber(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints a Bomb Flinger (a goblin holding a lit bomb); returns nothing."""
    paint_body(surface, cx, cy + 0.15 * s, s * 0.8, (128, 62, 42), GOBLIN)
    for side in [-1, 1]:
        ear = [(cx + side * 0.2 * s, cy - 0.22 * s), (cx + side * 0.2 * s, cy - 0.02 * s),
               (cx + side * 0.58 * s, cy - 0.32 * s)]
        pygame.draw.polygon(surface, GOBLIN, ear)
        pygame.draw.circle(surface, BLACK, (cx + side * 0.1 * s, cy - 0.16 * s), max(1, 0.05 * s))
    pygame.draw.circle(surface, BLACK, (cx + 0.62 * s, cy - 0.5 * s), 0.3 * s)
    pygame.draw.circle(surface, STEEL_DARK, (cx + 0.54 * s, cy - 0.6 * s), 0.08 * s)
    pygame.draw.line(surface, WOOD, (cx + 0.62 * s, cy - 0.8 * s), (cx + 0.78 * s, cy - 1.0 * s), max(1, int(s * 0.08)))
    pygame.draw.circle(surface, ORANGE, (cx + 0.8 * s, cy - 1.04 * s), 0.13 * s)
    pygame.draw.circle(surface, GOLD, (cx + 0.8 * s, cy - 1.04 * s), 0.06 * s)


def paint_shade(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints a wispy Shade Stalker with glowing eyes; returns nothing."""
    wisp = [(cx, cy - 0.98 * s), (cx + 0.5 * s, cy - 0.3 * s), (cx + 0.62 * s, cy + 0.92 * s),
            (cx + 0.2 * s, cy + 0.6 * s), (cx, cy + 0.96 * s), (cx - 0.2 * s, cy + 0.6 * s),
            (cx - 0.62 * s, cy + 0.92 * s), (cx - 0.5 * s, cy - 0.3 * s)]
    pygame.draw.polygon(surface, SHADOW, wisp)
    pygame.draw.polygon(surface, PURPLE, wisp, max(1, int(s * 0.07)))
    for side in [-1, 1]:
        pygame.draw.circle(surface, CYAN, (cx + side * 0.18 * s, cy - 0.3 * s), max(1.5, 0.09 * s))
        pygame.draw.line(surface, tint(SHADOW, -20), (cx + side * 0.5 * s, cy), (cx + side * 0.85 * s, cy + 0.4 * s), max(1, int(s * 0.1)))


def paint_warlord(surface, cx, cy, s):
    """AI-assisted: receives a picture, a center and a size; paints Spears's Warlord with cape, crown and greatsword; returns nothing."""
    cape = [(cx - 0.78 * s, cy + 1.0 * s), (cx + 0.78 * s, cy + 1.0 * s), (cx + 0.42 * s, cy - 0.3 * s),
            (cx - 0.42 * s, cy - 0.3 * s)]
    pygame.draw.polygon(surface, CRIMSON, cape)
    paint_body(surface, cx, cy, s, (30, 26, 34), (198, 192, 182))
    pygame.draw.polygon(surface, STEEL_DARK, [(cx - 0.5 * s, cy - 0.08 * s), (cx - 0.2 * s, cy - 0.16 * s), (cx - 0.3 * s, cy + 0.2 * s)])
    pygame.draw.polygon(surface, STEEL_DARK, [(cx + 0.5 * s, cy - 0.08 * s), (cx + 0.2 * s, cy - 0.16 * s), (cx + 0.3 * s, cy + 0.2 * s)])
    crown = [(cx - 0.32 * s, cy - 0.55 * s), (cx - 0.32 * s, cy - 0.98 * s), (cx - 0.16 * s, cy - 0.72 * s),
             (cx, cy - 1.04 * s), (cx + 0.16 * s, cy - 0.72 * s), (cx + 0.32 * s, cy - 0.98 * s),
             (cx + 0.32 * s, cy - 0.55 * s)]
    pygame.draw.polygon(surface, GOLD, crown)
    for side in [-1, 1]:
        pygame.draw.circle(surface, CRIMSON, (cx + side * 0.12 * s, cy - 0.36 * s), max(1.5, 0.065 * s))
    pygame.draw.line(surface, STEEL, (cx + 0.72 * s, cy + 0.7 * s), (cx + 0.72 * s, cy - 0.95 * s), max(3, int(s * 0.16)))
    pygame.draw.line(surface, GOLD, (cx + 0.5 * s, cy + 0.32 * s), (cx + 0.94 * s, cy + 0.32 * s), max(2, int(s * 0.12)))


def paint_figure(surface, name, cx, cy, s):
    """AI-assisted: receives a picture, a hero kind or enemy look, a center and a size; paints the matching figure; returns the name."""
    if name == "leader":
        paint_frodo(surface, cx, cy, s)
    elif name == "tank":
        paint_tank(surface, cx, cy, s)
    elif name == "archer":
        paint_archer(surface, cx, cy, s)
    elif name == "mage":
        paint_mage(surface, cx, cy, s)
    elif name == "rogue":
        paint_rogue(surface, cx, cy, s)
    elif name == "orc":
        paint_orc(surface, cx, cy, s)
    elif name == "goblin":
        paint_goblin(surface, cx, cy, s)
    elif name == "guard":
        paint_guard(surface, cx, cy, s)
    elif name == "wolf":
        paint_wolf(surface, cx, cy, s)
    elif name == "bomber":
        paint_bomber(surface, cx, cy, s)
    elif name == "shade":
        paint_shade(surface, cx, cy, s)
    else:
        paint_warlord(surface, cx, cy, s * 1.12)
    return name


def outlined(raw, width):
    """AI-assisted: receives a painted figure and an outline width; returns the figure with a dark outline all round, like a cut-out standee."""
    mask = pygame.mask.from_surface(raw)
    dark = mask.to_surface(None, None, None, (20, 14, 16, 255), (0, 0, 0, 0))
    result = pygame.Surface(raw.get_size(), pygame.SRCALPHA)
    for step in [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]:
        result.blit(dark, (step[0] * width, step[1] * width))
    result.blit(raw, (0, 0))
    return result


def sprite(name, s):
    """AI-assisted: receives a figure name and a size; returns its outlined picture (painted the first time, reused after that)."""
    key = name + "@" + str(int(s))
    if key not in ART["cache"]:
        size = int(s * 3.6)
        raw = pygame.Surface((size, size), pygame.SRCALPHA)
        paint_figure(raw, name, size / 2, size / 2 + 0.12 * s, s)
        ART["cache"][key] = outlined(raw, max(1, min(3, int(s / 14))))
    return ART["cache"][key]


def draw_base(cx, cy, s, color):
    """AI-assisted: receives a center, a size and a color; draws the shadow and round coloured base a figure stands on; returns nothing."""
    screen = ART["screen"]
    base = pygame.Rect(cx - 0.86 * s, cy + 0.6 * s, 1.72 * s, 0.62 * s)
    shadow = pygame.Surface((int(2.6 * s), int(0.9 * s)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 120), shadow.get_rect())
    screen.blit(shadow, (cx - 0.9 * s, cy + 0.62 * s))
    pygame.draw.ellipse(screen, BLACK, base.inflate(4, 4))
    pygame.draw.ellipse(screen, color, base)
    pygame.draw.ellipse(screen, tint(color, -70), base.inflate(-int(0.36 * s), -int(0.2 * s)))


def draw_hero(kind, cx, cy, s):
    """AI-assisted: receives a hero kind, a center and a size; draws that hero standing on a base in the class color; returns the kind."""
    draw_base(cx, cy, s, CLASS_COLORS[kind])
    picture = sprite(kind, s)
    ART["screen"].blit(picture, (cx - picture.get_width() / 2, cy - picture.get_height() / 2 - 0.12 * s))
    return kind


def draw_model(look, cx, cy, s):
    """AI-assisted: receives an enemy look, a center and a size; draws that enemy on a bone-white base (gold for the Warlord); returns the look."""
    color = BONE
    if look == "warlord":
        color = GOLD
    draw_base(cx, cy, s, color)
    picture = sprite(look, s)
    ART["screen"].blit(picture, (cx - picture.get_width() / 2, cy - picture.get_height() / 2 - 0.12 * s))
    return look


# ================================================================ map tiles and features

def draw_floor(rect, variant):
    """AI-assisted: receives a tile rectangle and a variant number; draws a stone flagstone; returns nothing."""
    ART["screen"].blit(ART["cache"]["floor" + str(variant % 8)], rect)


def draw_wall(rect, variant):
    """AI-assisted: receives a tile rectangle and a variant number; draws a wall block; returns nothing."""
    ART["screen"].blit(ART["cache"]["wall" + str(variant % 8)], rect)


def draw_door(rect, is_open):
    """AI-assisted: receives a tile rectangle and whether the door is unsealed; draws a sealed door or a glowing EXIT; returns nothing."""
    screen = ART["screen"]
    pygame.draw.rect(screen, (58, 56, 64), rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    for stone in range(4):
        pygame.draw.line(screen, (28, 27, 32), (rect.x, rect.y + stone * 12), (rect.right, rect.y + stone * 12), 1)
    arch = rect.inflate(-10, -4)
    pygame.draw.rect(screen, BLACK, arch, 0, 12)
    door = arch.inflate(-6, -6)
    if is_open:
        glow = int(150 + 100 * pulse())
        pygame.draw.rect(screen, (glow, int(glow * 0.78), 60), door, 0, 9)
        pygame.draw.rect(screen, WHITE, door.inflate(-10, -10), 0, 6)
        text("EXIT", rect.centerx, rect.centery, "tiny", INK, "center")
    else:
        pygame.draw.rect(screen, WOOD_DARK, door, 0, 9)
        pygame.draw.line(screen, BLACK, (door.centerx, door.y + 2), (door.centerx, door.bottom - 2), 1)
        pygame.draw.line(screen, STEEL_DARK, (door.x, door.y + 9), (door.right - 1, door.y + 9), 3)
        pygame.draw.line(screen, STEEL_DARK, (door.x, door.bottom - 10), (door.right - 1, door.bottom - 10), 3)
        pygame.draw.circle(screen, CRIMSON, door.center, 6)
        pygame.draw.circle(screen, BLOOD, door.center, 6, 2)


def draw_boss_mark(rect):
    """AI-assisted: receives a door's tile rectangle; draws a crimson skull plaque over it to mark the way to the boss; returns nothing."""
    screen = ART["screen"]
    cx = rect.centerx
    cy = rect.y + 10
    pygame.draw.circle(screen, BLACK, (cx, cy), 10)
    pygame.draw.circle(screen, BLOOD, (cx, cy), 9)
    draw_skull(cx, cy, 5, False)
    pygame.draw.circle(screen, GOLD, (cx, cy), 10, 1)


def draw_throne(rect):
    """AI-assisted: receives the rectangle the throne covers (one or two tiles wide); draws the Warlord's iron throne on its stone dais; returns nothing."""
    screen = ART["screen"]
    dais = rect.inflate(-2, -6).move(0, 4)
    pygame.draw.rect(screen, (70, 66, 74), dais, 0, 3)
    pygame.draw.rect(screen, BLACK, dais, 1, 3)
    back = pygame.Rect(rect.x + 8, rect.y - 14, rect.width - 16, 34)
    pygame.draw.rect(screen, (40, 36, 44), back, 0, 3)
    pygame.draw.rect(screen, GOLD, back, 2, 3)
    spikes = max(3, back.width // 14)
    for spike in range(spikes):
        left = back.x + 2 + spike * (back.width - 4) // spikes
        pygame.draw.polygon(screen, GOLD, [(left, back.y), (left + 8, back.y), (left + 4, back.y - 10)])
    seat = pygame.Rect(rect.x + 6, rect.y + 18, rect.width - 12, 16)
    pygame.draw.rect(screen, CRIMSON, seat, 0, 4)
    pygame.draw.rect(screen, BLOOD, seat, 2, 4)


def draw_brazier(rect):
    """AI-assisted: receives a tile rectangle; draws an iron fire bowl on three legs (its flames are added with the lighting); returns nothing."""
    screen = ART["screen"]
    cx = rect.centerx
    for leg in [-10, 0, 10]:
        pygame.draw.line(screen, (30, 28, 32), (cx + leg * 0.6, rect.y + 24), (cx + leg, rect.y + 42), 3)
    bowl = pygame.Rect(cx - 15, rect.y + 14, 30, 14)
    pygame.draw.ellipse(screen, (46, 42, 48), bowl)
    pygame.draw.ellipse(screen, BLACK, bowl, 2)
    pygame.draw.ellipse(screen, ORANGE, pygame.Rect(cx - 11, rect.y + 15, 22, 7))
    pygame.draw.ellipse(screen, GOLD, pygame.Rect(cx - 6, rect.y + 16, 12, 4))


def draw_open_door(rect):
    """AI-assisted: receives a tile rectangle; draws a doorway whose doors have been swung open for good; returns nothing."""
    screen = ART["screen"]
    for x in [rect.x, rect.right - 7]:
        leaf = pygame.Rect(x, rect.y + 4, 7, rect.height - 8)
        pygame.draw.rect(screen, WOOD_DARK, leaf, 0, 2)
        pygame.draw.rect(screen, BLACK, leaf, 1, 2)
        pygame.draw.circle(screen, BRASS, leaf.center, 2)
    pygame.draw.line(screen, STEEL_DARK, (rect.x + 7, rect.bottom - 3), (rect.right - 8, rect.bottom - 3), 2)


def draw_chest(rect):
    """AI-assisted: receives a tile rectangle; draws a banded treasure chest; returns nothing."""
    screen = ART["screen"]
    pygame.draw.ellipse(screen, tint(FLOOR, -50), pygame.Rect(rect.x + 6, rect.y + 32, 36, 10))
    box = pygame.Rect(rect.x + 8, rect.y + 20, 32, 18)
    lid = pygame.Rect(rect.x + 8, rect.y + 11, 32, 12)
    pygame.draw.rect(screen, WOOD, box, 0, 2)
    pygame.draw.rect(screen, tint(WOOD, 22), lid, 0, 6)
    for band in [box.x + 5, box.right - 9]:
        pygame.draw.rect(screen, BRASS, pygame.Rect(band, lid.y, 4, 27))
    pygame.draw.rect(screen, BLACK, box, 1, 2)
    pygame.draw.rect(screen, BLACK, lid, 1, 6)
    pygame.draw.rect(screen, GOLD, pygame.Rect(box.centerx - 3, box.y - 2, 6, 8), 0, 2)
    pygame.draw.circle(screen, BLACK, (box.centerx, box.y + 2), 1)


def draw_trap(rect):
    """AI-assisted: receives a tile rectangle; draws a spike plate with crimson tips; returns nothing."""
    screen = ART["screen"]
    plate = rect.inflate(-12, -12)
    pygame.draw.rect(screen, (44, 40, 44), plate, 0, 3)
    pygame.draw.rect(screen, BLACK, plate, 1, 3)
    for index in range(3):
        left = plate.x + 3 + index * 11
        spike = [(left, plate.bottom - 4), (left + 9, plate.bottom - 4), (left + 4.5, plate.y + 2)]
        pygame.draw.polygon(screen, STEEL, spike)
        pygame.draw.polygon(screen, CRIMSON, [(left + 2.5, plate.y + 10), (left + 6.5, plate.y + 10), (left + 4.5, plate.y + 2)])
        pygame.draw.polygon(screen, BLACK, spike, 1)


def draw_shrine(rect):
    """AI-assisted: receives a tile rectangle; draws a stone shrine with a glowing rune (a point of interest); returns nothing."""
    screen = ART["screen"]
    cx = rect.centerx
    cy = rect.centery
    pygame.draw.ellipse(screen, tint(FLOOR, -50), pygame.Rect(cx - 16, cy + 8, 32, 10))
    pygame.draw.rect(screen, STEEL_DARK, pygame.Rect(cx - 12, cy - 4, 24, 18), 0, 3)
    pygame.draw.rect(screen, BLACK, pygame.Rect(cx - 12, cy - 4, 24, 18), 1, 3)
    size = 9 + 2 * pulse()
    diamond = [(cx, cy - 8 - size), (cx + size, cy - 8), (cx, cy - 8 + size), (cx - size, cy - 8)]
    pygame.draw.polygon(screen, (40, 96, 110), diamond)
    pygame.draw.polygon(screen, CYAN, diamond, 2)
    pygame.draw.circle(screen, WHITE, (cx, cy - 8), 2)


def draw_cover(rect):
    """AI-assisted: receives a tile rectangle; draws a wooden barricade crate that gives cover; returns nothing."""
    screen = ART["screen"]
    box = rect.inflate(-14, -14)
    pygame.draw.rect(screen, tint(FLOOR, -50), box.move(3, 4), 0, 2)
    pygame.draw.rect(screen, WOOD, box, 0, 2)
    for plank in range(1, 3):
        y = box.y + plank * box.height // 3
        pygame.draw.line(screen, WOOD_DARK, (box.x, y), (box.right - 1, y), 1)
    pygame.draw.rect(screen, WOOD_DARK, box, 3, 2)
    pygame.draw.line(screen, WOOD_DARK, box.topleft, box.bottomright, 3)
    pygame.draw.rect(screen, BLACK, box, 1, 2)
    for corner in [box.topleft, box.topright, box.bottomleft, box.bottomright]:
        pygame.draw.circle(screen, STEEL, corner, 2)


def draw_feature(spot, rect, is_open):
    """AI-assisted: receives a tile letter, its rectangle and an unused flag (kept so old calls still work); draws what stands on the tile; returns the letter."""
    if spot == "D":
        draw_door(rect, False)
    elif spot == "E":
        draw_door(rect, True)
    elif spot == "d":
        draw_open_door(rect)
    elif spot == "Y":
        draw_throne(rect)
    elif spot == "B":
        draw_brazier(rect)
    elif spot == "C" or spot == "X":
        draw_chest(rect)
    elif spot == "T":
        draw_trap(rect)
    elif spot == "P":
        draw_shrine(rect)
    elif spot == "~":
        draw_cover(rect)
    return spot


def glow_rect(rect, color, alpha):
    """AI-assisted: receives a rectangle, a color and a see-through amount; makes a tile glow with bright corner brackets; returns nothing."""
    screen = ART["screen"]
    shade(rect, color, alpha)
    reach = 9
    for corner in [[rect.x + 1, rect.y + 1, 1, 1], [rect.right - 2, rect.y + 1, -1, 1],
                   [rect.x + 1, rect.bottom - 2, 1, -1], [rect.right - 2, rect.bottom - 2, -1, -1]]:
        pygame.draw.line(screen, tint(color, 60), (corner[0], corner[1]), (corner[0] + reach * corner[2], corner[1]), 2)
        pygame.draw.line(screen, tint(color, 60), (corner[0], corner[1]), (corner[0], corner[1] + reach * corner[3]), 2)


# ================================================================ cards

def action_words(action):
    """AI-assisted: receives a card's action; returns [main words, small words] such as ["Attack 3", "range 4"]."""
    amount = str(action["amount"])
    if action["kind"] == "move":
        return ["Dash +" + amount, "extra moves"]
    elif action["kind"] == "shield":
        return ["Shield " + amount, "self, this round"]
    elif action["kind"] == "heal":
        return ["Heal " + amount, "range " + str(action["range"])]
    elif action["range"] <= 1:
        return ["Attack " + amount, "melee"]
    return ["Attack " + amount, "range " + str(action["range"])]


def draw_card(card, rect, border, kind):
    """AI-assisted: receives a card, a rectangle, a border color and the owner's hero kind; draws the card (name, big action icon, action, range and element mark); returns the rectangle."""
    screen = ART["screen"]
    action = card["action"]
    tone = ACTION_COLORS[action["kind"]]
    panel(rect, "slate", border)
    bar = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, 18)
    pygame.draw.rect(screen, tint(CLASS_COLORS[kind], -30), bar, 0, 4)
    pygame.draw.rect(screen, BLACK, bar, 1, 4)
    screen.set_clip(bar.inflate(-4, 0))
    text(card["name"], rect.centerx, bar.centery, "tiny", WHITE, "center")
    screen.set_clip(None)
    medallion(rect.centerx, rect.y + 52, 22, (30, 28, 36), tone)
    draw_icon(action["kind"], rect.centerx, rect.y + 52, 12, tone)
    words = action_words(action)
    text(words[0], rect.centerx, rect.y + 89, "bold", tone, "center")
    text(words[1], rect.centerx, rect.y + 107, "tiny", PARCHMENT_DARK, "center")
    if card["element"] in ELEMENT_COLORS:
        medallion(rect.x + 14, rect.y + 34, 8, SLATE, ELEMENT_COLORS[card["element"]])
        draw_icon(card["element"], rect.x + 14, rect.y + 34, 6, WHITE)
    return rect


def draw_modifier(rect, words, side, squeeze):
    """AI-assisted: receives a rectangle, the modifier text, "hero" or "enemy" and a flip amount 0-1; draws the attack modifier card that was just flipped; returns nothing."""
    width = max(6, int(rect.width * squeeze))
    card = pygame.Rect(rect.centerx - width // 2, rect.y, width, rect.height)
    border = BRASS
    label = "Hero draw"
    if side == "enemy":
        border = CRIMSON
        label = "Spears draw"
    panel(card, "slate", border)
    if squeeze < 0.9:
        return
    color = WHITE
    if words == "null":
        words = "MISS"
        color = CRIMSON
    elif words == "x2":
        color = GOLD
    medallion(card.centerx, card.centery - 8, 24, (30, 28, 36), border)
    size = "head"
    if len(words) > 2:
        size = "bold"
    text(words, card.centerx, card.centery - 8, size, color, "center")
    text(label, card.centerx, card.bottom - 13, "tiny", PARCHMENT, "center")
