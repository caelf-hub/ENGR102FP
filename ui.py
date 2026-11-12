"""ui.py - the game window: layout, panels, drag and drop, buttons, text fields, screens.

ui.py decides WHERE things go and what the mouse and keyboard do.
art.py knows HOW each thing looks (palette, textures, figures, cards, icons).
The game logic never draws; it only asks this file to show things and wait for the player.

The file is in this order:
  1. layout numbers and the UI dictionary      5. effects (floaters, banner, modifier card)
  2. positions (which tile / card is where)    6. the frame loop and typed input boxes
  3. the camera and the map                     7. the hero's turn (walk, card, orders)   
  4. the panels (top bar, party, log, cards)   8. full screens: title, party, rules, end
"""
import random

import pygame

import art
import cards
import logbook
import movement
import savegame
import scenery

# ---------------------------------------------------------------- layout
W = 1280
H = 720
TILE = 48
GRID_X = 236
GRID_Y = 64
GRID_W = 768
GRID_H = 480

ARROWS = {pygame.K_LEFT: [-1, 0], pygame.K_RIGHT: [1, 0], pygame.K_UP: [0, -1], pygame.K_DOWN: [0, 1]}
MENU_KEYS = {pygame.K_F1: "rules", pygame.K_F2: "status", pygame.K_F3: "save", pygame.K_F9: "quit"}
FEATURE_NOTES = {"C": "Chest: move a hero here for loot.", "P": "Shrine: move a hero here for a small gift.",
                 "T": "Trap: 2 damage and Doom +1 if a hero stops here.",
                 "~": "Cover: blocks 1 damage from enemy shots.",
                 "D": "Door: opens when every enemy unit here is destroyed.",
                 "E": "Unsealed door: walk a hero onto it to open the chamber behind.",
                 "d": "Open doorway.", "Y": "The Warlord's iron throne.",
                 "B": "Brazier: its fire lights the arena."}
MIN_ZOOM_LIMIT = 0.25
MAX_ZOOM = 1.6
PAN_KEYS = {pygame.K_w: [0, -1], pygame.K_a: [-1, 0], pygame.K_s: [0, 1], pygame.K_d: [1, 0]}

# Everything the window needs to remember between frames lives in this one dictionary.
UI = {"screen": None, "clock": None, "closed": False,
      "phase": "menu", "buttons": [], "message": "", "selected": 0, "turn_hero": None,
      "drag": None, "card": None, "highlights": [], "glows": [], "steps": [],
      "cursor": [1, 1], "cursor_on": False, "log_scroll": 0,
      "hints": {"walk": False, "card": False, "end": False},
      "strikes": [], "busy_until": 0, "caption": None,
      "floaters": [], "flashes": [], "mod": None, "banner": None,
      "room": None, "room_key": "", "ripples": [],
      "cam": [384.0, 240.0], "zoom": 1.0, "cam_goal": None, "zoom_goal": None, "pan": None,
      "mode": "screen", "view": pygame.Rect(0, 0, 768, 480), "map_size": [16, 10], "typing": False,
      "canvas": None}


# ================================================================ setup and positions

def init():
    """AI-assisted: receives nothing; opens the 1280x720 window (scaled to fit the screen), builds the art and returns the screen surface."""
    pygame.init()
    try:
        UI["screen"] = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
    except pygame.error:
        UI["screen"] = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Frodo and the Dungeon Lord")
    UI["clock"] = pygame.time.Clock()
    art.setup(UI["screen"])
    return UI["screen"]


def set_message(words):
    """AI-assisted: receives a sentence; shows it in the message bar under the map and returns it."""
    UI["message"] = words
    return words


def tile_rect(tile):
    """AI-assisted: receives a tile [col, row]; returns its rectangle - on the map picture while the map is being painted, otherwise on the screen (zoomed and panned)."""
    view = UI["view"]
    if UI["mode"] == "world":
        return pygame.Rect(tile[0] * TILE - view.x, tile[1] * TILE - view.y, TILE, TILE)
    zoom = UI["zoom"]
    left = int(GRID_X + (tile[0] * TILE - view.x) * zoom)
    top = int(GRID_Y + (tile[1] * TILE - view.y) * zoom)
    right = int(GRID_X + ((tile[0] + 1) * TILE - view.x) * zoom)
    bottom = int(GRID_Y + ((tile[1] + 1) * TILE - view.y) * zoom)
    return pygame.Rect(left, top, right - left, bottom - top)


def tile_center(tile):
    """AI-assisted: receives a tile [col, row]; returns the [x, y] pixel at its middle."""
    rect = tile_rect(tile)
    return [rect.centerx, rect.centery]


def tile_at(pos):
    """AI-assisted: receives a mouse position; returns the dungeon tile under it (taking zoom and panning into account), or None if it is off the map."""
    if not pygame.Rect(GRID_X, GRID_Y, GRID_W, GRID_H).collidepoint(pos):
        return None
    view = UI["view"]
    col = int((view.x + (pos[0] - GRID_X) / UI["zoom"]) // TILE)
    row = int((view.y + (pos[1] - GRID_Y) / UI["zoom"]) // TILE)
    if col < 0 or row < 0 or col >= UI["map_size"][0] or row >= UI["map_size"][1]:
        return None
    return [col, row]


def hero_block_rect(index):
    """AI-assisted: receives a hero's place in the party (0 = Frodo); returns that hero's panel rectangle on the left."""
    return pygame.Rect(8, 62 + index * 118, 204, 110)


def card_rect(index):
    """AI-assisted: receives a hand card number (0-2); returns its rectangle in the bottom strip."""
    return pygame.Rect(252 + index * 176, 584, 160, 132)


def hero_at_pixel(game, pos):
    """AI-assisted: receives the game and a mouse position; returns the hero whose portrait or token is there, or None."""
    for index in range(len(game["heroes"])):
        if hero_block_rect(index).collidepoint(pos):
            return game["heroes"][index]
    tile = tile_at(pos)
    if tile is None:
        return None
    return movement.hero_at(game["heroes"], tile)


def moved_far(start, pos):
    """AI-assisted: receives where a drag started and where it ended; returns True if the mouse really moved (a drag, not a click)."""
    return abs(start[0] - pos[0]) + abs(start[1] - pos[1]) > 10


def selected_hero(game):
    """AI-assisted: receives the game; returns the hero whose turn it is (whose cards are shown at the bottom), or None."""
    if UI["phase"] == "turn":
        return UI["turn_hero"]
    return None


def find_by_name(things, name):
    """AI-assisted: receives a list of heroes or units and a name; returns the one with that name, or None."""
    for thing in things:
        if thing["name"] == name:
            return thing
    return None


# ================================================================ buttons

def make_button(name, label, rect):
    """AI-assisted: receives an id, a label and a rectangle; returns a button dictionary."""
    return {"id": name, "label": label, "rect": rect}


def set_buttons(specs):
    """AI-assisted: receives a list of [id, label]; lays them out at the foot of the right panel (the first one wide on top, the rest two per row) and returns the button list."""
    UI["buttons"] = []
    for index in range(len(specs)):
        if index == 0:
            rect = pygame.Rect(1030, 534, 238, 34)
        else:
            rect = pygame.Rect(1030 + ((index - 1) % 2) * 122, 574 + ((index - 1) // 2) * 36, 116, 30)
        UI["buttons"].append(make_button(specs[index][0], specs[index][1], rect))
    return UI["buttons"]


def button_at(buttons, pos):
    """AI-assisted: receives a list of buttons and a mouse position; returns the id of the button there, or ""."""
    for button in buttons:
        if button["rect"].collidepoint(pos):
            return button["id"]
    return ""


# ================================================================ the map and fog of war

def tile_letter(game, col, row):
    """AI-assisted: receives the game and a col/row; returns the letter the party SEES there: the real tile if a hero can see it, otherwise what they remember."""
    if not movement.in_bounds(game["grid"], col, row):
        return "#"
    if game["seen"][row][col]:
        return movement.shown_letter(game["grid"][row][col])
    return game["known"][row][col]


def min_zoom():
    """AI-assisted: receives nothing; returns the smallest zoom, where the whole dungeon fits in the map window."""
    width = UI["map_size"][0] * TILE
    height = UI["map_size"][1] * TILE
    return max(MIN_ZOOM_LIMIT, min(1.0, GRID_W / width, GRID_H / height))


def clamp_camera():
    """AI-assisted: receives nothing; keeps the zoom in range and the camera over the dungeon; returns the zoom."""
    UI["zoom"] = max(min_zoom(), min(MAX_ZOOM, UI["zoom"]))
    sizes = [UI["map_size"][0] * TILE, UI["map_size"][1] * TILE]
    halves = [GRID_W / UI["zoom"] / 2, GRID_H / UI["zoom"] / 2]
    for axis in range(2):
        if sizes[axis] <= halves[axis] * 2:
            UI["cam"][axis] = sizes[axis] / 2
        else:
            UI["cam"][axis] = max(halves[axis], min(sizes[axis] - halves[axis], UI["cam"][axis]))
    return UI["zoom"]


def view_rect():
    """AI-assisted: receives nothing; returns the part of the dungeon picture (in map pixels) that the map window shows."""
    width = GRID_W / UI["zoom"]
    height = GRID_H / UI["zoom"]
    return pygame.Rect(int(UI["cam"][0] - width / 2), int(UI["cam"][1] - height / 2), int(width) + 1, int(height) + 1)


def visible_box():
    """AI-assisted: receives nothing; returns [left, top, right, bottom], the tiles that are (at least partly) in the map window."""
    view = UI["view"]
    left = max(0, view.x // TILE)
    top = max(0, view.y // TILE)
    right = min(UI["map_size"][0] - 1, view.right // TILE)
    bottom = min(UI["map_size"][1] - 1, view.bottom // TILE)
    return [left, top, right, bottom]


def tile_middle(tile):
    """AI-assisted: receives a tile; returns the map-pixel point at its middle."""
    return [tile[0] * TILE + TILE / 2, tile[1] * TILE + TILE / 2]


def follow(tile):
    """AI-assisted: receives a tile; glides the camera there if that tile is near the edge of the map window or off it; returns True if the camera moves."""
    point = tile_middle(tile)
    view = UI["view"]
    inner = view.inflate(-view.width // 3, -view.height // 3)
    if inner.collidepoint(point):
        return False
    UI["cam_goal"] = point
    return True


def frame_tiles(tiles, largest):
    """AI-assisted: receives a list of tiles and the biggest zoom allowed; glides the camera (and zoom) to show all of them; returns the new zoom goal."""
    if len(tiles) == 0:
        return UI["zoom"]
    left = 9999
    top = 9999
    right = -1
    bottom = -1
    for tile in tiles:
        left = min(left, tile[0])
        top = min(top, tile[1])
        right = max(right, tile[0])
        bottom = max(bottom, tile[1])
    width = (right - left + 3) * TILE
    height = (bottom - top + 3) * TILE
    UI["cam_goal"] = [(left + right + 1) * TILE / 2, (top + bottom + 1) * TILE / 2]
    UI["zoom_goal"] = max(min_zoom(), min(largest, GRID_W / width, GRID_H / height))
    return UI["zoom_goal"]


def show_chamber(game, tiles):
    """AI-assisted: receives the game and a newly opened chamber's tiles; glides the camera to show the chamber and the party; returns the zoom goal."""
    UI["map_size"] = [len(game["grid"][0]), len(game["grid"])]
    return frame_tiles(list(tiles) + movement.hero_tiles(game["heroes"]), 1.1)


def fit_view(game):
    """AI-assisted: receives the game; glides the camera out to show every part of the dungeon the party knows about; returns the zoom goal."""
    tiles = []
    for row in range(len(game["known"])):
        for col in range(len(game["known"][0])):
            if game["known"][row][col] != "#":
                tiles.append([col, row])
    return frame_tiles(tiles, 1.0)


def zoom_by(factor, pos):
    """AI-assisted: receives a zoom factor and a screen point; zooms in or out keeping the dungeon point under that screen point still; returns the new zoom."""
    before = [UI["view"].x + (pos[0] - GRID_X) / UI["zoom"], UI["view"].y + (pos[1] - GRID_Y) / UI["zoom"]]
    UI["zoom"] = max(min_zoom(), min(MAX_ZOOM, UI["zoom"] * factor))
    UI["cam"][0] = before[0] - (pos[0] - GRID_X - GRID_W / 2) / UI["zoom"]
    UI["cam"][1] = before[1] - (pos[1] - GRID_Y - GRID_H / 2) / UI["zoom"]
    UI["cam_goal"] = None
    UI["zoom_goal"] = None
    clamp_camera()
    UI["view"] = view_rect()
    return UI["zoom"]


def glide_camera():
    """AI-assisted: receives nothing; moves the camera a little toward its goal each frame and pans with WASD; returns nothing."""
    goal = UI["cam_goal"]
    if goal is not None:
        UI["cam"][0] += (goal[0] - UI["cam"][0]) * 0.16
        UI["cam"][1] += (goal[1] - UI["cam"][1]) * 0.16
        if abs(goal[0] - UI["cam"][0]) + abs(goal[1] - UI["cam"][1]) < 2:
            UI["cam_goal"] = None
    if UI["zoom_goal"] is not None:
        UI["zoom"] += (UI["zoom_goal"] - UI["zoom"]) * 0.16
        if abs(UI["zoom_goal"] - UI["zoom"]) < 0.005:
            UI["zoom_goal"] = None
    if not UI["typing"]:
        pressed = pygame.key.get_pressed()
        for key in PAN_KEYS:
            if pressed[key]:
                UI["cam"][0] += PAN_KEYS[key][0] * 12 / UI["zoom"]
                UI["cam"][1] += PAN_KEYS[key][1] * 12 / UI["zoom"]
                UI["cam_goal"] = None
    clamp_camera()
    UI["view"] = view_rect()


def camera_event(game, event):
    """AI-assisted: receives the game and one event; handles mouse-wheel zoom, right-drag panning and the Home / + / - keys; returns True if the event was used up by the camera."""
    over_map = pygame.Rect(GRID_X, GRID_Y, GRID_W, GRID_H).collidepoint(pygame.mouse.get_pos())
    if event.type == pygame.MOUSEWHEEL and over_map:
        zoom_by(1.15 ** event.y, pygame.mouse.get_pos())
        return True
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and over_map:
        UI["pan"] = {"start": event.pos, "cam": list(UI["cam"])}
        UI["cam_goal"] = None
        return True
    elif event.type == pygame.MOUSEMOTION and UI["pan"] is not None:
        UI["cam"][0] = UI["pan"]["cam"][0] - (event.pos[0] - UI["pan"]["start"][0]) / UI["zoom"]
        UI["cam"][1] = UI["pan"]["cam"][1] - (event.pos[1] - UI["pan"]["start"][1]) / UI["zoom"]
        return False
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
        UI["pan"] = None
        return True
    elif event.type == pygame.KEYDOWN and not UI["typing"]:
        return camera_key(game, event.key)
    return False


def camera_key(game, key):
    """AI-assisted: receives the game and a key; Home fits the whole known dungeon, + and - zoom; returns True if the key was a camera key."""
    middle = (GRID_X + GRID_W // 2, GRID_Y + GRID_H // 2)
    if key == pygame.K_HOME:
        fit_view(game)
    elif key == pygame.K_EQUALS or key == pygame.K_KP_PLUS or key == pygame.K_PAGEUP:
        zoom_by(1.2, middle)
    elif key == pygame.K_MINUS or key == pygame.K_KP_MINUS or key == pygame.K_PAGEDOWN:
        zoom_by(1 / 1.2, middle)
    else:
        return False
    return True


def seen_letters(game):
    """AI-assisted: receives the game; returns a grid of the letters the party sees on every tile (real where lit, remembered where dark)."""
    letters = []
    for row in range(len(game["grid"])):
        line = []
        for col in range(len(game["grid"][0])):
            line.append(tile_letter(game, col, row))
        letters.append(line)
    return letters


def room_art(game, letters):
    """AI-assisted: receives the game and the letters the party sees; returns the painted dungeon picture, repainting it only when the known walls change."""
    rock = 0
    for line in letters:
        for spot in line:
            if spot == "#":
                rock += 1
    key = str(game["seed"]) + ":" + str(rock)
    if UI["room_key"] != key:
        UI["room"] = scenery.build_room(letters, game["seed"])
        UI["room_key"] = key
        UI["ripples"] = []
    return UI["room"]


def draw_features(game, letters):
    """AI-assisted: receives the game and the letters the party sees; draws the chests, traps, shrines, cover, doors, throne and braziers in the map window; returns how many were drawn."""
    count = 0
    box = visible_box()
    for row in range(box[1], box[3] + 1):
        for col in range(box[0], box[2] + 1):
            spot = letters[row][col]
            if spot == "Y" and col > 0 and letters[row][col - 1] == "Y":
                continue
            elif spot == "Y" and col + 1 < len(letters[0]) and letters[row][col + 1] == "Y":
                art.draw_throne(tile_rect([col, row]).union(tile_rect([col + 1, row])))
                count += 1
            elif spot != "#" and spot != ".":
                art.draw_feature(spot, tile_rect([col, row]), False)
                count += 1
            if game["boss_door"] == [col, row] and spot != "#":
                art.draw_boss_mark(tile_rect([col, row]))
    return count


def draw_ripples(game, room):
    """AI-assisted: receives the game and the room picture; now and then starts a drip ring on a puddle the heroes can see, and draws the rings; returns how many rings are alive."""
    if art.ART["tick"] % 16 == 0 and len(room["puddles"]) > 0:
        puddle = random.choice(room["puddles"])
        x = puddle[0] + random.randint(8, puddle[2] - 8)
        y = puddle[1] + random.randint(5, puddle[3] - 5)
        if game["seen"][min(y // TILE, len(game["seen"]) - 1)][min(x // TILE, len(game["seen"][0]) - 1)]:
            UI["ripples"].append({"x": x, "y": y, "life": 30, "start": art.ART["tick"]})
    for ripple in UI["ripples"]:
        scenery.draw_ripple(ripple["x"] - UI["view"].x, ripple["y"] - UI["view"].y, ripple["life"])
    return fade_list(UI["ripples"])


def draw_highlights():
    """AI-assisted: receives nothing; makes every tile you can use glow in the color of what would happen there (blue walk, red attack, green heal), with the step count on walking tiles; returns how many there are."""
    alpha = int(46 + 50 * art.pulse())
    for index in range(len(UI["highlights"])):
        kind = "gold"
        if index < len(UI["glows"]):
            kind = UI["glows"][index]
        rect = tile_rect(UI["highlights"][index])
        art.glow_rect(rect, art.GLOW_COLORS[kind], alpha)
        if index < len(UI["steps"]) and rect.width >= 20:
            art.text_outline(UI["steps"][index], rect.right - 9, rect.bottom - 11, "tiny", art.WHITE, "center")
    return len(UI["highlights"])


def light_sources(game):
    """AI-assisted: receives the game; returns the light sources [col, row, strength]: every standing hero's torch, and every brazier the party can see."""
    lights = []
    for tile in movement.hero_tiles(game["heroes"]):
        lights.append([tile[0], tile[1], 276])
    box = visible_box()
    for row in range(box[1], box[3] + 1):
        for col in range(box[0], box[2] + 1):
            if game["grid"][row][col] == "B" and game["seen"][row][col]:
                lights.append([col, row, 250])
    return lights


def draw_flames(game, room, lights):
    """AI-assisted: receives the game, the dungeon picture and the light sources; draws the flames of the wall torches and braziers the heroes can see; returns how many burn."""
    burning = 0
    view = UI["view"]
    for torch in room["torches"]:
        if game["seen"][torch[1]][torch[0]]:
            scenery.draw_flame(GRID_X + (torch[2] - view.x) * UI["zoom"], GRID_Y + (torch[3] - view.y) * UI["zoom"],
                               art.ART["tick"], UI["zoom"])
            burning += 1
    for light in lights:
        if game["grid"][light[1]][light[0]] == "B":
            middle = tile_rect([light[0], light[1]])
            scenery.draw_flame(middle.centerx, middle.y + middle.height * 0.36, art.ART["tick"], UI["zoom"] * 1.6)
            burning += 1
    return burning


def draw_lighting(game, room):
    """AI-assisted: receives the game and the dungeon picture; multiplies the map window by the light (warm near heroes and braziers, cold dark elsewhere) and lights the flames; returns how many flames burn."""
    box = visible_box()
    lights = light_sources(game)
    small = scenery.light_grid(game["seen"], lights, art.ART["tick"], box)
    area = tile_rect([box[0], box[1]]).union(tile_rect([box[2], box[3]]))
    light = pygame.transform.smoothscale(small, (max(1, area.width), max(1, area.height)))
    UI["screen"].blit(light, area.topleft, None, pygame.BLEND_RGB_MULT)
    return draw_flames(game, room, lights)


def visible_models(game, unit):
    """AI-assisted: receives the game and a unit; returns the unit's models that a hero can see right now."""
    shown = []
    for model in unit["models"]:
        if game["seen"][model["pos"][1]][model["pos"][0]]:
            shown.append(model)
    return shown


def draw_coherency(models):
    """AI-assisted: receives the visible models of one unit; draws a faint outline around them to show they are one unit; returns nothing."""
    if len(models) < 2:
        return
    box = tile_rect(models[0]["pos"])
    for model in models:
        box = box.union(tile_rect(model["pos"]))
    pygame.draw.rect(UI["screen"], art.BLOOD, box.inflate(-4, -4), 2, 14)
    pygame.draw.rect(UI["screen"], art.BLACK, box.inflate(-2, -2), 1, 14)


def draw_model_token(unit, model):
    """AI-assisted: receives an enemy unit and one of its models; draws the model with its wounds; returns nothing."""
    center = tile_center(model["pos"])
    if "draw" in model:
        center = [model["draw"][0] - UI["view"].x, model["draw"][1] - UI["view"].y]
    art.draw_model(unit["look"], center[0], center[1] - 5, 15)
    art.draw_pips(center[0], center[1] + 20, min(model["hp"], 6), art.CRIMSON)
    if model["hp"] > 6:
        art.text_outline(model["hp"], center[0] + 16, center[1] + 12, "tiny", art.WHITE, "center")


def draw_figures(game):
    """AI-assisted: receives the game; draws every visible enemy and hero in the map window, row by row from the back of the room to the front, so nearer figures overlap farther ones; returns how many were drawn."""
    count = 0
    box = visible_box()
    for unit in game["units"]:
        draw_coherency(visible_models(game, unit))
    for row in range(max(0, box[1] - 1), box[3] + 2):
        for unit in game["units"]:
            for model in visible_models(game, unit):
                if model["pos"][1] == row:
                    draw_model_token(unit, model)
                    count += 1
        for hero in game["heroes"]:
            if hero["pos"][1] == row:
                draw_hero_token(game, hero)
                count += 1
    return count


def draw_hero_token(game, hero):
    """AI-assisted: receives the game and a hero; draws the hero on the map with a pulsing ring if it is their turn; returns nothing."""
    if hero["exhausted"]:
        return
    center = tile_center(hero["pos"])
    if hero["name"] == game["turn_name"] or hero is selected_hero(game):
        pygame.draw.circle(UI["screen"], art.GOLD, center, int(22 + 2 * art.pulse()), 2)
    art.draw_hero(hero["kind"], center[0], center[1] - 5, 15)
    if hero["shield"] + hero["armor"] > 0:
        art.draw_icon("shield", center[0] + 16, center[1] - 14, 9, art.STEEL)
        art.text(hero["shield"] + hero["armor"], center[0] + 16, center[1] - 15, "tiny", art.BLACK, "center")


def draw_cursor():
    """AI-assisted: receives nothing; draws the keyboard cursor on the map when the arrow keys are in use; returns nothing."""
    if UI["cursor_on"]:
        rect = tile_rect(UI["cursor"]).inflate(-4, -4)
        pygame.draw.rect(UI["screen"], art.BLACK, rect.inflate(2, 2), 4, 5)
        pygame.draw.rect(UI["screen"], art.WHITE, rect, 2, 4)


def paint_world(game, letters, room):
    """AI-assisted: receives the game, the letters the party sees and the dungeon picture; paints the part of the dungeon in view (floor, walls, objects, figures) at full size onto a scratch picture; returns that picture."""
    view = UI["view"]
    canvas = UI["canvas"]
    if canvas is None or canvas.get_size() != view.size:
        canvas = pygame.Surface(view.size)
        UI["canvas"] = canvas
    canvas.fill(art.BLACK)
    canvas.blit(room["surface"], (-view.x, -view.y))
    screen = UI["screen"]
    UI["screen"] = canvas
    art.ART["screen"] = canvas
    UI["mode"] = "world"
    draw_features(game, letters)
    draw_ripples(game, room)
    draw_figures(game)
    UI["mode"] = "screen"
    UI["screen"] = screen
    art.ART["screen"] = screen
    return canvas


def show_map(game):
    """AI-assisted: receives the game; draws the dungeon in the map window: the painted rooms zoomed and panned, then real light and darkness, then glows and markers; returns how many tiles are in view."""
    UI["map_size"] = [len(game["grid"][0]), len(game["grid"])]
    glide_camera()
    area = pygame.Rect(GRID_X, GRID_Y, GRID_W, GRID_H)
    letters = seen_letters(game)
    room = room_art(game, letters)
    canvas = paint_world(game, letters, room)
    if UI["zoom"] < 0.999:
        picture = pygame.transform.smoothscale(canvas, (GRID_W, GRID_H))
    elif UI["zoom"] > 1.001:
        picture = pygame.transform.scale(canvas, (GRID_W, GRID_H))
    else:
        picture = canvas
    UI["screen"].set_clip(area)
    UI["screen"].blit(picture, (GRID_X, GRID_Y))
    draw_lighting(game, room)
    draw_highlights()
    draw_cursor()
    draw_boss_bar(game)
    UI["screen"].set_clip(None)
    art.vignette(area)
    frame_rect = pygame.Rect(GRID_X - 4, GRID_Y - 4, GRID_W + 8, GRID_H + 8)
    pygame.draw.rect(UI["screen"], art.BLACK, frame_rect, 5, 5)
    pygame.draw.rect(UI["screen"], art.BRASS, frame_rect, 3, 5)
    draw_zoom_hint()
    box = visible_box()
    return (box[2] - box[0] + 1) * (box[3] - box[1] + 1)


def draw_zoom_hint():
    """AI-assisted: receives nothing; writes the camera controls and the zoom level in the map window's corner; returns nothing."""
    words = "Wheel zoom  |  Right-drag / WASD pan  |  Home whole map  |  " + str(int(UI["zoom"] * 100)) + "%"
    width = art.ART["fonts"]["tiny"].size(words)[0] + 14
    box = pygame.Rect(GRID_X + GRID_W - width - 6, GRID_Y + 6, width, 18)
    art.shade(box, art.BLACK, 150)
    art.text(words, box.x + 7, box.y + 2, "tiny", art.PARCHMENT_DARK, "left")


def draw_boss_bar(game):
    """AI-assisted: receives the game; once the Warlord is in sight, shows his name, health and phase at the top of the map window; returns True if it was shown."""
    unit = None
    for each in game["units"]:
        if each["type"] == "Warlord" and len(visible_models(game, each)) > 0:
            unit = each
    if unit is None:
        return False
    plate = pygame.Rect(GRID_X + GRID_W // 2 - 200, GRID_Y + GRID_H - 72, 400, 40)
    art.panel(plate, "slate", art.CRIMSON)
    phases = ["", " - his guard is summoned", " - ENRAGED"]
    art.text("Spears's Warlord" + phases[game["boss_phase"]], plate.centerx, plate.y + 11, "bold", art.GOLD, "center")
    bar = pygame.Rect(plate.x + 14, plate.y + 23, plate.width - 28, 11)
    art.draw_bar(bar, unit["models"][0]["hp"], unit["wounds"], art.CRIMSON)
    return True


def tooltip_lines(game, tile):
    """AI-assisted: receives the game and the tile under the mouse; returns the lines of help to show about what is there ([] if nothing)."""
    hero = movement.hero_at(game["heroes"], tile)
    found = movement.model_at(game["units"], tile)
    spot = tile_letter(game, tile[0], tile[1])
    if hero is not None:
        return [hero["name"] + " - " + hero["title"], "HP " + str(hero["hp"]) + "/" + str(hero["max_hp"])
                + "   Shield " + str(hero["shield"] + hero["armor"])]
    elif found is not None and game["seen"][tile[1]][tile[0]]:
        unit = found[0]
        return [unit["name"] + " (" + unit["role"] + ")",
                "Wounds " + str(found[1]["hp"]) + "/" + str(unit["wounds"]) + "   Attack " + str(unit["attack"])
                + "   Toughness " + str(unit["toughness"]),
                "Move " + str(unit["move"]) + "   Range " + str(unit["range"]) + "   Leadership " + str(unit["leadership"])]
    elif spot in FEATURE_NOTES:
        return [FEATURE_NOTES[spot]]
    return []


def draw_tooltip(game):
    """AI-assisted: receives the game; shows a small note about the hero, enemy or feature under the mouse; returns how many lines were shown."""
    mouse = pygame.mouse.get_pos()
    tile = tile_at(mouse)
    if tile is None or UI["drag"] is not None:
        return 0
    lines = tooltip_lines(game, tile)
    if len(lines) == 0:
        return 0
    width = 20
    for line in lines:
        width = max(width, art.ART["fonts"]["small"].size(line)[0] + 20)
    box = pygame.Rect(min(mouse[0] + 14, W - width - 4), max(60, mouse[1] - 20 - len(lines) * 18), width, 12 + len(lines) * 18)
    art.panel(box, "parchment", art.BRASS)
    for number in range(len(lines)):
        art.text(lines[number], box.x + 10, box.y + 6 + number * 18, "small", art.INK, "left")
    return len(lines)


# ================================================================ panels: top bar

def draw_doom(game):
    """AI-assisted: receives the game; draws the Doom Track as a crimson bar with a skull every 10 steps; returns the Doom value."""
    plate = pygame.Rect(736, 5, 538, 46)
    art.panel(plate, "slate", art.BLOOD)
    art.text("DOOM", 746, 9, "bold", art.CRIMSON, "left")
    art.text(str(game["doom"]) + " / " + str(game["doom_max"]), 746, 28, "small", art.PARCHMENT, "left")
    bar = pygame.Rect(812, 20, 448, 14)
    art.draw_bar(bar, game["doom"], game["doom_max"], art.CRIMSON)
    for step in range(10, game["doom_max"] + 1, 10):
        x = bar.x + int(bar.width * step / game["doom_max"])
        art.draw_skull(min(x, bar.right - 6), bar.centery, 6, step <= game["doom"])
    return game["doom"]


def draw_elements(game):
    """AI-assisted: receives the game; draws the fire, frost and light medallions (bright = strong, dim ring = waning, dark = gone); returns nothing."""
    x = 640
    for name in ["fire", "frost", "light"]:
        color = art.ELEMENT_COLORS[name]
        strength = game["elements"][name]
        if strength >= 2:
            art.medallion(x, 20, 11, color, art.GOLD)
            art.draw_icon(name, x, 20, 7, art.WHITE)
        elif strength == 1:
            art.medallion(x, 20, 11, art.tint(color, -90), color)
            art.draw_icon(name, x, 20, 7, color)
        else:
            art.medallion(x, 20, 11, art.SLATE, art.STEEL_DARK)
            art.draw_icon(name, x, 20, 7, art.STEEL_DARK)
        art.text(name, x, 35, "tiny", art.PARCHMENT_DARK, "center")
        x += 32


def draw_tracker_entry(game, entry, cx):
    """AI-assisted: receives the game, one [initiative, tie, kind, name] entry and an x position; draws its medallion and initiative number; returns nothing."""
    rim = art.BRASS_DARK
    if entry[3] == game["turn_name"]:
        rim = art.GOLD
        pygame.draw.circle(UI["screen"], art.GOLD, (cx, 21), int(19 + art.pulse() * 2), 2)
    art.medallion(cx, 21, 16, art.SLATE, rim)
    name = "?"
    if entry[2] == "hero":
        name = find_by_name(game["heroes"], entry[3])["kind"]
    else:
        unit = find_by_name(game["units"], entry[3])
        if unit is not None and len(visible_models(game, unit)) > 0:
            name = unit["look"]
        elif unit is None:
            name = "x"
    if len(name) == 1:
        art.text(name, cx, 21, "bold", art.STEEL, "center")
    else:
        picture = art.sprite(name, 8)
        UI["screen"].blit(picture, (cx - picture.get_width() // 2, 21 - picture.get_height() // 2))
    plate = pygame.Rect(cx - 12, 39, 24, 14)
    pygame.draw.rect(UI["screen"], art.BLACK, plate, 0, 4)
    art.text(entry[0], cx, 46, "tiny", art.PARCHMENT, "center")


def draw_top_bar(game):
    """AI-assisted: receives the game; draws the round, room, initiative tracker, elements and Doom Track; returns nothing."""
    art.fill_texture(pygame.Rect(0, 0, W, 57), "leather")
    pygame.draw.line(UI["screen"], art.BLACK, (0, 57), (W, 57), 3)
    pygame.draw.line(UI["screen"], art.BRASS, (0, 56), (W, 56), 1)
    art.text("Round " + str(game["round"]), 12, 6, "head", art.GOLD, "left")
    art.text(game["room_name"] + "  -  " + str(game["depth"]) + " of " + str(len(game["plan"])) + " chambers",
             12, 34, "tiny", art.PARCHMENT, "left")
    if len(game["order"]) == 0:
        art.text("The initiative order appears here once cards are picked.", 196, 20, "small", art.PARCHMENT_DARK, "left")
    for index in range(min(len(game["order"]), 10)):
        draw_tracker_entry(game, game["order"][index], 214 + index * 41)
    draw_elements(game)
    draw_doom(game)


# ================================================================ panels: party, log, message

def hero_status(game, hero):
    """AI-assisted: receives the game and a hero; returns the short status words shown on the hero's panel."""
    if hero["exhausted"]:
        return "EXHAUSTED"
    elif UI["phase"] == "turn" and hero is UI["turn_hero"]:
        card = "card ready"
        if hero["acted"]:
            card = "card played"
        return "moves " + str(hero["moves_left"]) + "  -  " + card
    return "acts at " + str(hero["init"])


def draw_portrait(hero, rect):
    """AI-assisted: receives a hero and the hero's panel rectangle; draws the framed portrait; returns nothing."""
    frame_rect = pygame.Rect(rect.x + 6, rect.y + 6, 60, 68)
    art.panel(frame_rect, "slate", art.CLASS_COLORS[hero["kind"]])
    art.draw_hero(hero["kind"], frame_rect.centerx, frame_rect.centery - 2, 20)


def draw_hero_block(game, index):
    """AI-assisted: receives the game and a hero's place in the party; draws the hero's panel (portrait, hp bar, deck and discard, status); returns nothing."""
    hero = game["heroes"][index]
    rect = hero_block_rect(index)
    border = art.BRASS_DARK
    if hero is selected_hero(game) or hero["name"] == game["turn_name"]:
        border = art.GOLD
    art.panel(rect, "parchment", border)
    draw_portrait(hero, rect)
    art.text(hero["name"], rect.x + 72, rect.y + 4, "bold", art.INK, "left")
    art.draw_bar(pygame.Rect(rect.x + 72, rect.y + 24, 124, 15), hero["hp"], hero["max_hp"], art.CRIMSON)
    art.text_outline(str(hero["hp"]) + " / " + str(hero["max_hp"]), rect.x + 134, rect.y + 31, "tiny", art.WHITE, "center")
    art.text("Move " + str(hero["move"]) + "   Speed " + str(hero["speed"]), rect.x + 72, rect.y + 45, "tiny",
             art.INK, "left")
    art.text(hero_status(game, hero), rect.x + 72, rect.y + 62, "tiny", art.BLOOD, "left")
    art.text(hero["title"], rect.x + 8, rect.y + 86, "tiny", art.INK, "left")
    if hero["exhausted"]:
        art.shade(rect, art.BLACK, 150)


def draw_party_panel(game):
    """AI-assisted: receives the game; draws the whole left panel (one block per hero); returns nothing."""
    art.fill_texture(pygame.Rect(0, 58, 222, H - 58), "leather")
    for index in range(len(game["heroes"])):
        draw_hero_block(game, index)


def log_color(sentence):
    """AI-assisted: receives a log sentence; returns the ink color for it (red for Spears and danger, plain otherwise)."""
    for word in ["Spears", "exhausted", "trap", "dark", "Doom"]:
        if word in sentence:
            return art.BLOOD
    return art.INK


def draw_log(game):
    """AI-assisted: receives the game; draws the scrolling combat log on the right; returns how many lines were drawn."""
    area = pygame.Rect(1024, 62, 250, 462)
    art.fill_texture(pygame.Rect(1018, 58, 262, H - 58), "leather")
    art.panel(area, "parchment", art.BRASS_DARK)
    art.ribbon(area.centerx, area.y + 20, 190, "Combat Log", art.BLOOD)
    y = area.bottom - 10
    drawn = 0
    last = len(game["log"]) - 1 - UI["log_scroll"]
    for index in range(last, max(-1, last - 40), -1):
        lines = art.wrap_text(game["log"][index], "tiny", area.width - 22)
        y -= len(lines) * 14 + 5
        if y < area.y + 40:
            break
        pygame.draw.circle(UI["screen"], art.BRASS_DARK, (area.x + 9, y + 7), 2)
        for number in range(len(lines)):
            art.text(lines[number], area.x + 15, y + number * 14, "tiny", log_color(game["log"][index]), "left")
            drawn += 1
    return drawn


def draw_message():
    """AI-assisted: receives nothing; draws the message bar under the map, with Frodo doing the talking; returns nothing."""
    rect = pygame.Rect(GRID_X - 4, 550, GRID_W + 8, 26)
    art.panel(rect, "slate", art.BRASS_DARK)
    picture = art.sprite("leader", 7)
    UI["screen"].blit(picture, (rect.x + 4, rect.centery - picture.get_height() // 2))
    art.text(UI["message"], rect.x + 32, rect.y + 4, "small", art.GOLD, "left")


# ================================================================ panels: cards at the bottom

def dragging_card(index):
    """AI-assisted: receives a hand card number; returns True if that card is being dragged right now."""
    drag = UI["drag"]
    return drag is not None and drag["kind"] == "card" and drag["index"] == index


def draw_pile(hero):
    """AI-assisted: receives the acting hero; draws their deck as a small stack of card backs with the deck and discard counts; returns nothing."""
    for layer in range(min(3, len(hero["deck"]))):
        back = pygame.Rect(800 + layer * 3, 600 - layer * 3, 78, 104)
        art.panel(back, "slate", art.BRASS_DARK)
    art.text("Deck " + str(len(hero["deck"])), 842, 642, "bold", art.PARCHMENT, "center")
    art.text("Discard " + str(len(hero["discard"])), 842, 662, "tiny", art.PARCHMENT_DARK, "center")
    art.text("Play 1 card a turn.", 950, 600, "tiny", art.PARCHMENT, "center")
    art.text("A new card is", 950, 620, "tiny", art.PARCHMENT_DARK, "center")
    art.text("drawn at once.", 950, 636, "tiny", art.PARCHMENT_DARK, "center")
    art.text("Moves left: " + str(hero["moves_left"]), 950, 664, "bold", art.GOLD, "center")


def draw_hand(hero):
    """AI-assisted: receives the hero whose turn it is; draws their 3 cards (the chosen one lifted in gold, all dimmed once a card is played) and their deck; returns how many cards were drawn."""
    mouse = pygame.mouse.get_pos()
    for index in range(len(hero["hand"])):
        card = hero["hand"][index]
        rect = card_rect(index)
        if dragging_card(index):
            pygame.draw.rect(UI["screen"], art.BRASS_DARK, rect, 2, 7)
        elif UI["card"] == index:
            art.draw_card(card, rect.move(0, -14), art.GOLD, hero["kind"])
        elif rect.collidepoint(mouse) and not hero["acted"]:
            art.draw_card(card, rect.move(0, -8), art.BRASS, hero["kind"])
        else:
            art.draw_card(card, rect, art.BRASS_DARK, hero["kind"])
        art.text(index + 1, rect.x + 6, rect.bottom - 15, "tiny", art.STEEL_DARK, "left")
    draw_pile(hero)
    if hero["acted"]:
        art.shade(pygame.Rect(240, 578, 540, 140), art.BLACK, 160)
        art.text_outline("Card played - walk with any moves left, then End turn", 510, 640, "bold", art.GOLD,
                         "center")
    return len(hero["hand"])


def phase_hint():
    """AI-assisted: receives nothing; returns the lines of help shown in the bottom strip while no hero is taking a turn."""
    return ["Spears's armies are on the move...", "Hold SPACE to speed up the enemies' turns.",
            "Enemies in the dark stay hidden until a hero can see them."]


def draw_bottom(game):
    """AI-assisted: receives the game; draws the bottom strip (the acting hero's hand, or hints while enemies act); returns the phase."""
    art.fill_texture(pygame.Rect(222, 578, 796, 142), "leather")
    hero = selected_hero(game)
    if hero is not None:
        draw_hand(hero)
    else:
        lines = phase_hint()
        for number in range(len(lines)):
            art.text(lines[number], 250, 600 + number * 30, "body", art.PARCHMENT, "left")
    return UI["phase"]


# ================================================================ effects

def effect_start():
    """AI-assisted: receives nothing; returns the frame an effect should start on: now, or when the attacks already on screen have landed."""
    return max(art.ART["tick"], UI["busy_until"])


def add_floater(tile, words, color):
    """AI-assisted: receives a tile, some words and a color; starts floating text over the tile (after any attack still flying); returns how many floaters exist."""
    UI["floaters"].append({"text": words, "tile": [tile[0], tile[1]], "rise": 10 + 14 * len(UI["floaters"]),
                           "color": color, "life": 75, "start": effect_start()})
    return len(UI["floaters"])


def add_strike(fx):
    """AI-assisted: receives a strike effect from the game (an enemy attack); queues its animation after the ones already playing; returns the frame it ends on."""
    length = 16
    if fx["style"] == "bomb":
        length = 26
    elif fx["style"] == "ranged":
        length = 20
    start = effect_start()
    UI["strikes"].append({"from": fx["from"], "to": fx["to"], "style": fx["style"], "start": start,
                          "life": length + 10, "length": length})
    UI["busy_until"] = start + length
    return UI["busy_until"]


def consume_fx(game):
    """AI-assisted: receives the game; turns the effects the game logic asked for into things on screen, in order; returns how many were handled."""
    handled = 0
    while len(game["fx"]) > 0:
        fx = game["fx"].pop(0)
        handled += 1
        if fx["kind"] == "float":
            add_floater(fx["tile"], fx["text"], art.COLOR_NAMES[fx["color"]])
            UI["flashes"].append({"tile": fx["tile"], "life": 14, "color": art.COLOR_NAMES[fx["color"]],
                                  "start": effect_start()})
        elif fx["kind"] == "strike":
            add_strike(fx)
        elif fx["kind"] == "mod":
            UI["mod"] = {"text": fx["text"], "side": fx["side"], "life": 64, "start": effect_start()}
        elif fx["kind"] == "banner":
            UI["banner"] = {"text": fx["text"], "life": 280}
        else:
            add_floater(fx["tile"], "MORALE BROKEN!", art.GOLD)
            UI["flashes"].append({"tile": fx["tile"], "life": 40, "color": art.GOLD, "start": effect_start()})
    return handled


def fade_list(items):
    """AI-assisted: receives a list of effects with "start" and "life"; ages the ones that have started and removes the finished ones; returns how many are left."""
    for index in range(len(items) - 1, -1, -1):
        if art.ART["tick"] >= items[index]["start"]:
            items[index]["life"] -= 1
        if items[index]["life"] <= 0:
            items.pop(index)
    return len(items)


def draw_mod_card():
    """AI-assisted: receives nothing; flips over and briefly shows the attack modifier card that was just drawn; returns nothing."""
    mod = UI["mod"]
    if mod is None or art.ART["tick"] < mod["start"]:
        return
    rect = pygame.Rect(GRID_X + GRID_W - 86, GRID_Y + 84, 74, 100)
    art.draw_modifier(rect, mod["text"], mod["side"], min(1.0, (65 - mod["life"]) / 8.0))
    mod["life"] -= 1
    if mod["life"] <= 0:
        UI["mod"] = None


def draw_banner():
    """AI-assisted: receives nothing; shows the Spears banner (a crimson ribbon) while it lasts; returns nothing."""
    banner = UI["banner"]
    if banner is None:
        return
    rect = pygame.Rect(GRID_X + 20, GRID_Y + 30, GRID_W - 40, 44)
    points = [(rect.x, rect.y), (rect.right, rect.y), (rect.right - 14, rect.centery), (rect.right, rect.bottom),
              (rect.x, rect.bottom), (rect.x + 14, rect.centery)]
    pygame.draw.polygon(UI["screen"], art.BLOOD, points)
    pygame.draw.polygon(UI["screen"], art.BLACK, points, 4)
    pygame.draw.polygon(UI["screen"], art.GOLD, points, 2)
    picture = art.sprite("warlord", 10)
    UI["screen"].blit(picture, (rect.x + 26, rect.centery - picture.get_height() // 2))
    art.text(banner["text"], rect.centerx + 18, rect.centery, "bold", art.GOLD, "center")
    banner["life"] -= 1
    if banner["life"] <= 0:
        UI["banner"] = None


def draw_effects():
    """AI-assisted: receives nothing; draws enemy attacks, hit flashes, floating numbers, the modifier card and the banner (each when its turn comes); returns nothing."""
    UI["screen"].set_clip(pygame.Rect(GRID_X, GRID_Y, GRID_W, GRID_H))
    draw_strikes()
    for flash in UI["flashes"]:
        if art.ART["tick"] >= flash["start"]:
            art.shade(tile_rect(flash["tile"]), flash["color"], min(190, flash["life"] * 14))
    for floater in UI["floaters"]:
        if art.ART["tick"] >= floater["start"]:
            floater["rise"] += 0.6
            middle = tile_center(floater["tile"])
            art.text_outline(floater["text"], middle[0], middle[1] - floater["rise"], "head", floater["color"], "center")
    UI["screen"].set_clip(None)
    fade_list(UI["flashes"])
    fade_list(UI["floaters"])
    fade_list(UI["strikes"])
    draw_mod_card()
    draw_banner()
    draw_caption()


def lerp(first, second, part):
    """AI-assisted: receives two points and a fraction 0-1; returns the point that far along the line between them."""
    return [first[0] + (second[0] - first[0]) * part, first[1] + (second[1] - first[1]) * part]


def draw_slash(point, part):
    """AI-assisted: receives a screen point and how far the slash has got (0-1); draws three crimson claw marks across it; returns nothing."""
    size = 14 * UI["zoom"] + 6
    for offset in [-1, 0, 1]:
        top = [point[0] - size + offset * 7, point[1] - size]
        bottom = [point[0] + size + offset * 7, point[1] + size]
        pygame.draw.line(UI["screen"], art.WHITE, top, lerp(top, bottom, part), 4)
        pygame.draw.line(UI["screen"], art.CRIMSON, top, lerp(top, bottom, part), 2)


def draw_strike(strike, part):
    """AI-assisted: receives one enemy attack and how far it has got (0-1); draws the lunge and slash, the flying stone, or the arcing bomb and its burst; returns nothing."""
    start = tile_center(strike["from"])
    end = tile_center(strike["to"])
    screen = UI["screen"]
    if strike["style"] == "melee":
        reach = lerp(start, end, min(1.0, part * 1.6) * 0.8)
        pygame.draw.line(screen, art.BLOOD, start, reach, 6)
        pygame.draw.line(screen, art.CRIMSON, start, reach, 2)
        if part > 0.5:
            draw_slash(end, (part - 0.5) * 2)
    elif strike["style"] == "ranged":
        spot = lerp(start, end, part)
        tail = lerp(start, end, max(0.0, part - 0.15))
        pygame.draw.line(screen, art.PARCHMENT_DARK, tail, spot, 2)
        pygame.draw.circle(screen, art.BLACK, spot, 5)
        pygame.draw.circle(screen, art.STEEL, spot, 4)
    elif part < 0.8:
        spot = lerp(start, end, part / 0.8)
        spot[1] -= 70 * UI["zoom"] * (1 - ((part / 0.8) * 2 - 1) ** 2)
        pygame.draw.circle(screen, art.BLACK, spot, 7)
        pygame.draw.circle(screen, art.ORANGE, (spot[0] + 4, spot[1] - 6), 3)
    else:
        burst = int((part - 0.8) * 5 * 40 * UI["zoom"]) + 6
        pygame.draw.circle(screen, art.ORANGE, end, burst, 5)
        pygame.draw.circle(screen, art.GOLD, end, max(2, burst // 2))


def draw_strikes():
    """AI-assisted: receives nothing; draws every enemy attack that is playing right now; returns how many were drawn."""
    drawn = 0
    for strike in UI["strikes"]:
        part = (art.ART["tick"] - strike["start"]) / strike["length"]
        if 0 <= part <= 1:
            draw_strike(strike, part)
            drawn += 1
    return drawn


def caption(game, unit, words):
    """AI-assisted: receives the game, the enemy unit that is acting (None to clear) and what it is doing; shows it in a caption on the map ("Something in the dark" if the unit is hidden); returns nothing."""
    if unit is None or UI["screen"] is None:
        UI["caption"] = None
        return
    visible = len(visible_models(game, unit)) > 0
    if visible:
        UI["caption"] = {"look": unit["look"], "name": unit["name"], "words": words}
    else:
        UI["caption"] = {"look": "", "name": "Something in the dark", "words": "moves where you cannot see..."}


def draw_caption():
    """AI-assisted: receives nothing; draws the caption that says what the acting enemy is doing; returns True if one was drawn."""
    shown = UI["caption"]
    if shown is None:
        return False
    top = GRID_Y + 30
    if UI["banner"] is not None:
        top = GRID_Y + 80
    width = max(art.ART["fonts"]["bold"].size(shown["name"])[0], art.ART["fonts"]["body"].size(shown["words"])[0]) + 90
    box = pygame.Rect(GRID_X + 10, top, width, 54)
    art.panel(box, "slate", art.CRIMSON)
    if shown["look"] != "":
        picture = art.sprite(shown["look"], 12)
        UI["screen"].blit(picture, (box.x + 30 - picture.get_width() // 2, box.centery - picture.get_height() // 2))
    art.text(shown["name"], box.x + 62, box.y + 7, "bold", art.GOLD, "left")
    art.text(shown["words"], box.x + 62, box.y + 27, "body", art.PARCHMENT, "left")
    return True


def model_paths(game):
    """AI-assisted: receives the game; turns the enemy moves the game logic made into walking paths (only for models the party can see); returns a list of [model, path]."""
    paths = []
    for move in game["moves"]:
        model = move["model"]
        start = move["from"]
        seen = game["seen"][start[1]][start[0]] or game["seen"][model["pos"][1]][model["pos"][0]]
        if not seen:
            continue
        path = movement.find_path(game["grid"], start, model["pos"], [], True)
        if len(path) < 2:
            path = [start, model["pos"]]
        paths.append([model, path])
    game["moves"] = []
    return paths


def play_moves(game):
    """AI-assisted: receives the game; shows the enemies that just moved walking along their paths tile by tile; returns how many models walked."""
    if UI["screen"] is None:
        game["moves"] = []
        return 0
    paths = model_paths(game)
    longest = 0
    for item in paths:
        longest = max(longest, len(item[1]) - 1)
    for step in range(longest):
        for part in range(1, 6):
            for item in paths:
                place_model(item[0], item[1], step, part / 5)
            frame(game)
            if fast_forward():
                break
    for item in paths:
        if "draw" in item[0]:
            del item[0]["draw"]
    return len(paths)


def place_model(model, path, step, part):
    """AI-assisted: receives a model, its walking path, the step it is on and how far along that step (0-1); sets where it is drawn this frame; returns nothing."""
    last = len(path) - 1
    first = path[min(step, last)]
    second = path[min(step + 1, last)]
    point = lerp(tile_middle(first), tile_middle(second), part)
    model["draw"] = point


def fast_forward():
    """AI-assisted: receives nothing; returns True while the player holds Space to speed up the enemies' turns."""
    if UI["screen"] is None or UI["typing"]:
        return False
    return pygame.key.get_pressed()[pygame.K_SPACE]


def wait_effects(game):
    """AI-assisted: receives the game; keeps drawing until every enemy attack on screen has landed; returns nothing."""
    if UI["screen"] is None:
        return
    consume_fx(game)
    while game["running"] and art.ART["tick"] < UI["busy_until"]:
        frame(game)


def draw_path(game, hero, tile):
    """AI-assisted: receives the game, the dragged hero and the tile under the mouse; draws footsteps along the walking path; returns the path length."""
    blocked = movement.model_tiles(game["units"])
    path = movement.find_path(game["grid"], hero["pos"], tile, blocked, False)
    for step in path:
        pygame.draw.circle(UI["screen"], art.BLACK, tile_center(step), 6)
        pygame.draw.circle(UI["screen"], art.WHITE, tile_center(step), 4)
    return len(path)


def preview_words(game, hero, card, tile):
    """AI-assisted: receives the game, the acting hero, the card being dragged (None when walking) and the tile under the mouse; returns a short line saying what dropping there would do."""
    if card is None:
        index = UI["highlights"].index(tile)
        return "Walk here (" + str(UI["steps"][index]) + " of " + str(hero["moves_left"]) + " moves)"
    action = card["action"]
    found = movement.model_at(game["units"], tile)
    if action["kind"] == "attack" and found is not None:
        base = action["amount"] + hero["attack_bonus"] - found[0]["toughness"]
        return "Attack " + found[0]["name"] + ": about " + str(max(0, base)) + " damage"
    friend = movement.hero_at(game["heroes"], tile)
    if action["kind"] == "heal" and friend is not None:
        return "Heal " + friend["name"] + " +" + str(action["amount"])
    return art.action_words(action)[0]


def draw_preview(game, hero, card):
    """AI-assisted: receives the game, the acting hero and the card being dragged (None when walking); shows what a drop on the tile under the mouse would do; returns True if a preview was shown."""
    mouse = pygame.mouse.get_pos()
    tile = tile_at(mouse)
    if not movement.is_valid_drop(tile, UI["highlights"]):
        return False
    words = preview_words(game, hero, card, tile)
    kind = "move"
    if card is not None:
        kind = card["action"]["kind"]
    width = art.ART["fonts"]["bold"].size(words)[0] + 24
    box = pygame.Rect(min(mouse[0] - width // 2, W - width - 4), mouse[1] - 104, width, 26)
    art.panel(box, "slate", art.GLOW_COLORS[kind])
    art.text(words, box.centerx, box.centery, "bold", art.ACTION_COLORS[kind], "center")
    return True


def draw_drag(game):
    """AI-assisted: receives the game; draws whatever is being dragged under the mouse (a card or the hero) and what dropping it would do; returns the kind of thing dragged ("" if nothing)."""
    drag = UI["drag"]
    hero = selected_hero(game)
    if drag is None or hero is None:
        return ""
    mouse = pygame.mouse.get_pos()
    if drag["kind"] == "card":
        card = hero["hand"][drag["index"]]
        art.draw_card(card, pygame.Rect(mouse[0] - 46, mouse[1] - 65, 92, 130), art.GOLD, hero["kind"])
        draw_preview(game, hero, card)
    elif drag["kind"] == "hero":
        if movement.is_valid_drop(tile_at(mouse), UI["highlights"]):
            draw_path(game, hero, tile_at(mouse))
        art.draw_hero(hero["kind"], mouse[0], mouse[1] - 6, max(8, int(17 * UI["zoom"])))
        draw_preview(game, hero, None)
    return drag["kind"]


# ================================================================ the frame

def exit_open(game):
    """AI-assisted: receives the game; returns True if the party's chamber is clear and has an unsealed EXIT door."""
    if not game["plan"][game["chamber"]]["cleared"]:
        return False
    for door in game["doors"]:
        tile = door["tile"]
        if game["grid"][tile[1]][tile[0]] == "E":
            return True
    return False


def heal_tip(game, hero):
    """AI-assisted: receives the game and the acting hero; returns a tip if a hero is badly hurt and this hero holds a heal card ("" if not)."""
    for friend in game["heroes"]:
        if friend["exhausted"] or friend["hp"] * 3 > friend["max_hp"]:
            continue
        for card in hero["hand"]:
            if card["action"]["kind"] == "heal":
                return (friend["name"] + " is badly hurt - drag " + card["name"] + " onto them"
                        + " (walk closer first if they do not glow).")
    return ""


def reach_tip(game, hero):
    """AI-assisted: receives the game and the acting hero; returns a tip if enemies are in sight but out of reach of every attack card ("" if not)."""
    seen = movement.enemy_targets(game, hero["pos"], 999)
    if len(seen) == 0:
        return ""
    for card in hero["hand"]:
        action = card["action"]
        if action["kind"] == "attack" and len(movement.action_targets(game, hero, action)) > 0:
            return ""
    return "No enemy is in range of " + hero["name"] + "'s attack cards - walk closer first, then play one."


def loot_tip(game, hero):
    """AI-assisted: receives the game and the acting hero; returns a tip if a chest or shrine can be reached this turn ("" if not)."""
    for tile in movement.move_targets(game, hero)[0]:
        if game["known"][tile[1]][tile[0]] in "CP":
            return "Loot in reach - walk onto the chest or shrine to grab it."
    return ""


def situation_tip(game):
    """AI-assisted: receives the game; returns the most useful tip for what is happening right now ("" if there is nothing to say)."""
    hero = selected_hero(game)
    if hero is None:
        return "Enemies are acting - hold SPACE to speed them up."
    if exit_open(game):
        return "This chamber is clear - walk a hero onto a glowing EXIT door. Side doors lead to extra loot."
    tips = [heal_tip(game, hero), reach_tip(game, hero)]
    if hero["moves_left"] > 0:
        tips.append(loot_tip(game, hero))
    if hero["acted"] and hero["moves_left"] == 0:
        tips.append("Nothing left to do this turn - click End turn (E).")
    if game["doom"] * 4 >= game["doom_max"] * 3:
        tips.append("The Doom bar is nearly full - hurry to the red-skull door!")
    for tip in tips:
        if tip != "":
            return tip
    return ""


def draw_tip(game):
    """AI-assisted: receives the game; draws the tip strip along the bottom of the map; returns True if a tip was shown."""
    words = situation_tip(game)
    if words == "" or UI["phase"] == "menu":
        return False
    band = pygame.Rect(GRID_X, GRID_Y + GRID_H - 26, GRID_W, 26)
    art.shade(band, art.BLACK, 175)
    pygame.draw.line(UI["screen"], art.BRASS_DARK, band.topleft, band.topright, 1)
    art.draw_icon("light", band.x + 16, band.centery, 7, art.GOLD)
    art.text("TIP:  " + words, band.x + 30, band.y + 4, "small", art.GOLD, "left")
    return True


def hint_for(game, hero):
    """AI-assisted: receives the game and the acting hero; returns [words, rectangle to point at] for the next first-turn hint, or None when there is nothing left to teach."""
    hints = UI["hints"]
    if not hints["walk"] and hero["moves_left"] > 0 and not hero["acted"] and UI["drag"] is None:
        for index in range(len(UI["glows"])):
            if UI["glows"][index] == "move":
                return ["Click a blue tile to walk there", tile_rect(UI["highlights"][index])]
    if not hints["card"] and not hero["acted"]:
        for index in range(len(hero["hand"])):
            action = hero["hand"][index]["action"]
            if action["kind"] == "attack" and len(movement.action_targets(game, hero, action)) > 0:
                return ["Drag this card onto the glowing enemy", card_rect(index)]
        if hints["walk"]:
            return ["Drag a card onto a glowing target", card_rect(0)]
    if not hints["end"] and (hero["acted"] or hints["walk"]):
        for button in UI["buttons"]:
            if button["id"] == "end":
                return ["Click End turn when you are done", button["rect"]]
    return None


def draw_hint(game):
    """AI-assisted: receives the game; on a hero's turn, shows a pointer bubble with the next thing to try, until the player has walked, played a card and ended a turn once; returns True if a hint was shown."""
    if UI["phase"] != "turn" or UI["turn_hero"] is None:
        return False
    hint = hint_for(game, UI["turn_hero"])
    if hint is None:
        return False
    target = hint[1]
    pygame.draw.rect(UI["screen"], art.GOLD, target.inflate(6, 6), 3, 6)
    width = art.ART["fonts"]["bold"].size(hint[0])[0] + 28
    box = pygame.Rect(0, 0, width, 34)
    box.centerx = max(width // 2 + 4, min(W - width // 2 - 4, target.centerx))
    if target.y > 560:
        box.bottom = 542 - int(4 * art.pulse())
        tip = [(box.centerx - 8, box.bottom), (box.centerx + 8, box.bottom), (target.centerx, target.y - 6)]
    elif target.y > 300:
        box.bottom = target.y - 22 - int(4 * art.pulse())
        tip = [(target.centerx - 8, box.bottom), (target.centerx + 8, box.bottom), (target.centerx, target.y - 6)]
    else:
        box.y = target.bottom + 22 + int(4 * art.pulse())
        tip = [(target.centerx - 8, box.y), (target.centerx + 8, box.y), (target.centerx, target.bottom + 6)]
    pygame.draw.polygon(UI["screen"], art.GOLD, tip)
    art.panel(box, "parchment", art.GOLD)
    art.text(hint[0], box.centerx, box.centery, "bold", art.INK, "center")
    return True


def learn_hint(request):
    """AI-assisted: receives the request the player just made; marks the matching first-turn hint as learned; returns the request type."""
    names = {"move": "walk", "card": "card", "end": "end"}
    if request["type"] in names:
        UI["hints"][names[request["type"]]] = True
    return request["type"]


def draw_game(game):
    """AI-assisted: receives the game; draws the entire game screen once; returns nothing."""
    UI["screen"].fill(art.NIGHT)
    consume_fx(game)
    draw_top_bar(game)
    draw_party_panel(game)
    draw_log(game)
    draw_bottom(game)
    show_map(game)
    draw_message()
    for button in UI["buttons"]:
        art.draw_button(button)
    draw_tip(game)
    draw_effects()
    draw_hint(game)
    draw_tooltip(game)
    draw_drag(game)


def common_event(game, event):
    """AI-assisted: receives the game (or None on menu screens) and one event; handles closing the window, full screen and log scrolling; returns nothing."""
    if event.type == pygame.QUIT:
        UI["closed"] = True
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            set_message("Full screen is not available here.")
    elif game is None:
        return
    elif event.type == pygame.MOUSEWHEEL and pygame.Rect(1018, 58, 262, H - 58).collidepoint(pygame.mouse.get_pos()):
        UI["log_scroll"] = max(0, min(len(game["log"]) - 1, UI["log_scroll"] + event.y))


def present(game):
    """AI-assisted: receives the game (or None); shows the finished frame, waits for 60 FPS and returns the list of new events (minus the ones the camera used up); holding Space speeds the effects up."""
    pygame.display.flip()
    UI["clock"].tick(60)
    art.ART["tick"] += 1
    if game is not None and UI["phase"] == "watch" and fast_forward():
        art.ART["tick"] += 3
    events = []
    for event in pygame.event.get():
        common_event(game, event)
        if game is None or not camera_event(game, event):
            events.append(event)
    if UI["closed"] and game is not None:
        game["running"] = False
    return events


def frame(game):
    """AI-assisted: receives the game; draws one frame of the game screen and returns the new events."""
    draw_game(game)
    return present(game)


def pause(game, milliseconds):
    """AI-assisted: receives the game and a time in milliseconds; keeps drawing for that long so the player can watch (much shorter while Space is held; nothing if no window is open, as in the tests); returns nothing."""
    if UI["screen"] is None:
        return
    end = pygame.time.get_ticks() + milliseconds
    while game["running"] and pygame.time.get_ticks() < end:
        frame(game)
        if fast_forward():
            end -= 50


def move_cursor(game, key):
    """AI-assisted: receives the game and an arrow key; moves the keyboard cursor one tile (staying on the map); returns the cursor tile."""
    step = ARROWS[key]
    col = UI["cursor"][0] + step[0]
    row = UI["cursor"][1] + step[1]
    if movement.in_bounds(game["grid"], col, row):
        UI["cursor"] = [col, row]
    UI["cursor_on"] = True
    follow(UI["cursor"])
    return UI["cursor"]


def clear_input():
    """AI-assisted: receives nothing; forgets any drag, chosen card and glowing tiles; returns nothing."""
    UI["drag"] = None
    UI["card"] = None
    UI["highlights"] = []
    UI["glows"] = []
    UI["steps"] = []


def dim_screen():
    """AI-assisted: receives nothing; darkens the whole window behind a pop-up box; returns nothing."""
    art.shade(pygame.Rect(0, 0, W, H), art.BLACK, 160)


# ================================================================ typed input boxes

def check_number(typed, low, high):
    """AI-assisted: receives what the player typed and the allowed range; returns [number, ""] if it is good or [None, message] if it is not."""
    if typed.strip() == "":
        return [None, "Nothing typed yet - please type a number."]
    try:
        value = int(typed)
    except ValueError:
        return [None, "'" + typed + "' is not a whole number. Try again."]
    if value < low or value > high:
        return [None, "Please pick a number from " + str(low) + " to " + str(high) + "."]
    return [value, ""]


def check_name(typed):
    """AI-assisted: receives what the player typed; returns [name, ""] if it is a good file name or [None, message] if it is not."""
    if typed.strip() == "":
        return [None, "Nothing typed yet - please type a name."]
    for letter in typed:
        if not (letter.isalnum() or letter == "_"):
            return [None, "Use only letters, numbers and _ (no spaces or dots)."]
    return [typed, ""]


def draw_text_box(prompt, typed, error):
    """AI-assisted: receives a question, the text typed so far and an error message; draws the typing box; returns nothing."""
    dim_screen()
    box = pygame.Rect(W // 2 - 290, H // 2 - 100, 580, 200)
    art.panel(box, "parchment", art.BRASS)
    art.text(prompt, box.centerx, box.y + 32, "head", art.INK, "center")
    field = pygame.Rect(box.x + 70, box.y + 62, box.width - 140, 42)
    pygame.draw.rect(UI["screen"], art.WHITE, field, 0, 6)
    pygame.draw.rect(UI["screen"], art.INK, field, 2, 6)
    shown = typed
    if art.ART["tick"] % 60 < 30:
        shown = typed + "|"
    art.text(shown, field.x + 12, field.y + 9, "body", art.INK, "left")
    art.text(error, box.centerx, box.y + 128, "bold", art.CRIMSON, "center")
    art.text("Type, then press Enter.   Esc = cancel", box.centerx, box.y + 168, "small", art.INK, "center")


def ask_text(game, prompt, kind, low, high):
    """AI-assisted: receives the game, a question, "number" or "name", and the number range; lets the player type until the answer is valid; returns the answer (None if cancelled)."""
    typed = ""
    error = ""
    UI["typing"] = True
    answer = type_loop(game, prompt, kind, low, high)
    UI["typing"] = False
    return answer


def type_loop(game, prompt, kind, low, high):
    """AI-assisted: receives the same things as ask_text(); runs the typing box until a valid answer or Esc; returns the answer (None if cancelled)."""
    typed = ""
    error = ""
    while game["running"]:
        draw_game(game)
        draw_text_box(prompt, typed, error)
        for event in present(game):
            if event.type != pygame.KEYDOWN:
                continue
            elif event.key == pygame.K_ESCAPE:
                return None
            elif event.key == pygame.K_BACKSPACE:
                typed = typed[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if kind == "number":
                    result = check_number(typed, low, high)
                else:
                    result = check_name(typed)
                if result[0] is not None:
                    return result[0]
                error = result[1]
                typed = ""
            elif event.unicode.isprintable() and event.unicode != "" and len(typed) < 20:
                typed += event.unicode
    return None


def ask_yes_no(game, question):
    """AI-assisted: receives the game and a yes/no question; waits for Y or N (or a click); returns True for yes."""
    yes = make_button("yes", "Yes (Y)", pygame.Rect(W // 2 - 130, H // 2 + 14, 110, 34))
    no = make_button("no", "No (N)", pygame.Rect(W // 2 + 20, H // 2 + 14, 110, 34))
    while game["running"]:
        draw_game(game)
        dim_screen()
        art.panel(pygame.Rect(W // 2 - 340, H // 2 - 74, 680, 148), "parchment", art.BRASS)
        art.text(question, W // 2, H // 2 - 36, "body", art.INK, "center")
        art.draw_button(yes)
        art.draw_button(no)
        for event in present(game):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                choice = button_at([yes, no], event.pos)
                if choice != "":
                    return choice == "yes"
    return False


def ask_direction(game):
    """AI-assisted: receives the game; waits for the player to press an arrow key; returns the step [dx, dy] (None if cancelled)."""
    set_message("Now press an arrow key for the direction (Esc = cancel).")
    while game["running"]:
        for event in frame(game):
            if event.type == pygame.KEYDOWN and event.key in ARROWS:
                return ARROWS[event.key]
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
    return None


# ================================================================ the hero's turn

def confirm_quit(game):
    """AI-assisted: receives the game; asks the player if they really want to quit; returns True for yes."""
    return ask_yes_no(game, "Quit the game? The adventure log so far is kept in frodo_log.txt.")


def turn_buttons():
    """AI-assisted: receives nothing; puts the turn and menu buttons at the bottom right; returns the button list."""
    return set_buttons([["end", "End turn (E)"], ["typed", "Type move (M)"], ["rules", "Rules (F1)"],
                        ["status", "Status (F2)"], ["save", "Save (F3)"], ["quit", "Quit (F9)"]])


def show_moves(game, hero):
    """AI-assisted: receives the game and the acting hero; lights up the tiles the hero can walk to, each with its step count; returns how many."""
    result = movement.move_targets(game, hero)
    UI["highlights"] = result[0]
    UI["steps"] = result[1]
    UI["glows"] = ["move"] * len(result[0])
    return len(result[0])


def show_targets(tiles, kind):
    """AI-assisted: receives a list of tiles and a glow kind; lights them up (without step counts); returns how many."""
    UI["highlights"] = tiles
    UI["steps"] = []
    UI["glows"] = [kind] * len(tiles)
    return len(tiles)


def refresh_glow(game, hero):
    """AI-assisted: receives the game and the acting hero; lights up what the player can do right now (the chosen card's targets, or walking tiles); returns how many tiles glow."""
    if UI["card"] is not None and UI["card"] < len(hero["hand"]):
        action = hero["hand"][UI["card"]]["action"]
        return show_targets(movement.action_targets(game, hero, action), action["kind"])
    return show_moves(game, hero)


def hand_card_at(hero, pos):
    """AI-assisted: receives a hero and a mouse position; returns the number of the hand card there, or -1."""
    for index in range(len(hero["hand"])):
        rect = card_rect(index)
        if rect.union(rect.move(0, -14)).collidepoint(pos):
            return index
    return -1


def pick_card(hero, index):
    """AI-assisted: receives the acting hero and a hand card number; chooses that card so its targets glow; returns True if it could be chosen."""
    if hero["acted"]:
        set_message(hero["name"] + " has already played a card this turn.")
        return False
    if index < 0 or index >= len(hero["hand"]):
        set_message("There is no card " + str(index + 1) + " in " + hero["name"] + "'s hand.")
        return False
    UI["card"] = index
    card = hero["hand"][index]
    set_message(card["name"] + ": drop it on a glowing target (or click one). Esc puts it back.")
    return True


def card_request(game, hero, tile):
    """AI-assisted: receives the game, the acting hero and a tile; returns a request to play the chosen card there, or shows why not and returns None."""
    card = hero["hand"][UI["card"]]
    if movement.is_valid_drop(tile, movement.action_targets(game, hero, card["action"])):
        UI["card"] = None
        return {"type": "card", "card": card["name"], "tile": [tile[0], tile[1]]}
    set_message(movement.drop_message(game, hero, card["action"], tile))
    return None


def move_request(game, hero, tile):
    """AI-assisted: receives the game, the acting hero and a tile; returns a request to walk there, or shows why not and returns None."""
    if movement.is_valid_drop(tile, movement.move_targets(game, hero)[0]):
        return {"type": "move", "tile": [tile[0], tile[1]]}
    set_message(movement.drop_message(game, hero, None, tile))
    return None


def tile_request(game, hero, tile):
    """AI-assisted: receives the game, the acting hero and a clicked or dropped-on tile; uses the chosen card there, or walks there; returns a request or None."""
    if UI["card"] is not None:
        return card_request(game, hero, tile)
    other = movement.hero_at(game["heroes"], tile)
    if other is not None and other is not hero:
        set_message("It is " + hero["name"] + "'s turn. " + other["name"] + " acts on their own turn.")
        return None
    elif tile == hero["pos"]:
        set_message("Click a glowing blue tile to walk there, or drag a card from the bottom onto a target.")
        return None
    return move_request(game, hero, tile)


def typed_move(game, hero):
    """AI-assisted: receives the game and the acting hero; asks "How many tiles to move?" in a typed box, then a direction; returns the walk request or None."""
    if hero["moves_left"] == 0:
        set_message(hero["name"] + " has no moves left this turn.")
        return None
    limit = hero["moves_left"]
    count = ask_text(game, "How many tiles to move? (1 to " + str(limit) + ")", "number", 1, limit)
    if count is None:
        return None
    step = ask_direction(game)
    if step is None:
        return None
    tile = [hero["pos"][0] + step[0] * count, hero["pos"][1] + step[1] * count]
    return move_request(game, hero, tile)


def turn_button(game, hero, choice):
    """AI-assisted: receives the game, the acting hero and the id of a button (or menu key); returns the request it makes, or None."""
    if choice == "end":
        return {"type": "end"}
    elif choice == "typed":
        return typed_move(game, hero)
    elif choice == "quit":
        if confirm_quit(game):
            return {"type": "menu", "choice": "quit"}
        return None
    return {"type": "menu", "choice": choice}


def turn_mouse_down(game, hero, pos):
    """AI-assisted: receives the game, the acting hero and a click position; starts dragging a card or the hero, or acts on a clicked tile; returns a request or None."""
    UI["cursor_on"] = False
    choice = button_at(UI["buttons"], pos)
    index = hand_card_at(hero, pos)
    tile = tile_at(pos)
    if choice != "":
        return turn_button(game, hero, choice)
    elif index >= 0:
        if pick_card(hero, index):
            UI["drag"] = {"kind": "card", "index": index, "start": pos}
    elif tile is not None and tile == hero["pos"] and UI["card"] is None:
        UI["drag"] = {"kind": "hero", "start": pos}
    elif tile is not None:
        return tile_request(game, hero, tile)
    return None


def turn_mouse_up(game, hero, pos):
    """AI-assisted: receives the game, the acting hero and where the mouse was let go; finishes a drag; returns a request, or None after a snap back."""
    drag = UI["drag"]
    UI["drag"] = None
    if drag is None or not moved_far(drag["start"], pos):
        return None
    tile = tile_at(pos)
    if tile is None:
        UI["card"] = None
        set_message("Dropped off the map - nothing happened. Drop onto a glowing tile.")
        return None
    elif drag["kind"] == "hero":
        return move_request(game, hero, tile)
    return tile_request(game, hero, tile)


def turn_key(game, hero, key):
    """AI-assisted: receives the game, the acting hero and a key; returns the request it makes, or None."""
    if pygame.K_1 <= key <= pygame.K_9:
        pick_card(hero, key - pygame.K_1)
    elif key in ARROWS:
        move_cursor(game, key)
    elif key == pygame.K_ESCAPE:
        UI["card"] = None
        set_message("Cancelled.")
    elif key == pygame.K_e:
        return {"type": "end"}
    elif key == pygame.K_m:
        return typed_move(game, hero)
    elif key in MENU_KEYS:
        return turn_button(game, hero, MENU_KEYS[key])
    elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
        return tile_request(game, hero, UI["cursor"])
    return None


def turn_intro(hero):
    """AI-assisted: receives the acting hero; returns the sentence shown in the message bar that says what the player can do now."""
    if hero["acted"] and hero["moves_left"] == 0:
        return hero["name"] + " is done - click End turn (E)."
    elif hero["acted"]:
        return hero["name"] + ": click a glowing tile to walk (" + str(hero["moves_left"]) + " moves left), or End turn."
    return (hero["name"] + "'s turn: click a glowing tile to walk (" + str(hero["moves_left"])
            + " moves), and drag one card onto a target.")


def get_hero_action(game, hero):
    """AI-assisted: receives the game and the hero whose turn it is; waits for the player to walk, play a card, use the menu or end the turn; returns that request."""
    UI["phase"] = "turn"
    UI["turn_hero"] = hero
    clear_input()
    UI["cursor"] = list(hero["pos"])
    turn_buttons()
    set_message(turn_intro(hero))
    request = None
    while game["running"] and request is None:
        refresh_glow(game, hero)
        for event in frame(game):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                request = turn_mouse_down(game, hero, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                request = turn_mouse_up(game, hero, event.pos)
            elif event.type == pygame.KEYDOWN:
                request = turn_key(game, hero, event.key)
            if request is not None:
                break
    clear_input()
    UI["phase"] = "watch"
    set_buttons([])
    if request is None:
        return {"type": "end"}
    learn_hint(request)
    return request


# ================================================================ full screens: title and party

def draw_title(buttons, note):
    """AI-assisted: receives the title buttons and a note (like a load error); draws the title screen with Frodo facing the Warlord; returns nothing."""
    art.draw_backdrop()
    art.torch_glow(360, 430, 260)
    art.torch_glow(920, 420, 260)
    art.text_outline("Frodo", W // 2, 104, "huge", art.GOLD, "center")
    art.text_outline("and the Dungeon Lord", W // 2, 176, "title", art.PARCHMENT, "center")
    art.divider(W // 2, 214, 460)
    art.text("A tactical dungeon crawl. Lead the party. Outsmart Spears.", W // 2, 240, "body", art.PARCHMENT_DARK, "center")
    art.draw_hero("leader", 360, 430, 100)
    art.draw_model("warlord", 920, 420, 84)
    art.ribbon(360, 610, 260, "Frodo, Party Leader", art.BLOOD)
    art.ribbon(920, 610, 260, "Spears's Warlord", art.BLOOD)
    for button in buttons:
        art.draw_button(button)
    art.text(note, W // 2, 660, "body", art.CRIMSON, "center")
    art.text("F11 = full screen", W // 2, 690, "small", art.PARCHMENT_DARK, "center")


def title_screen(note):
    """AI-assisted: receives a note to show (like a load error); shows the title screen and waits; returns "start", "continue", "rules" or "quit"."""
    names = ["start", "continue", "rules", "quit"]
    labels = ["1  New Game", "2  Continue", "3  Rules", "4  Quit"]
    buttons = []
    for index in range(4):
        buttons.append(make_button(names[index], labels[index], pygame.Rect(W // 2 - 90, 300 + index * 56, 180, 44)))
    while not UI["closed"]:
        draw_title(buttons, note)
        for event in present(None):
            if event.type == pygame.MOUSEBUTTONDOWN and button_at(buttons, event.pos) != "":
                return button_at(buttons, event.pos)
            elif event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_4:
                return names[event.key - pygame.K_1]
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return "start"
    return "quit"


def save_rect(index):
    """AI-assisted: receives a row number on the Continue screen; returns that save's rectangle."""
    return pygame.Rect(W // 2 - 360, 150 + index * 58, 720, 50)


def draw_load_screen(saves, summaries):
    """AI-assisted: receives the save names and their summaries; draws the Continue screen; returns nothing."""
    art.draw_backdrop()
    art.text_outline("Continue a Saved Game", W // 2, 70, "title", art.GOLD, "center")
    art.divider(W // 2, 104, 420)
    if len(saves) == 0:
        art.text("No saved games yet. The game saves itself every time a door opens, and F3 saves by name.",
                 W // 2, 200, "body", art.PARCHMENT, "center")
    for index in range(len(saves)):
        rect = save_rect(index)
        state = hover_border(rect)
        art.panel(rect, "parchment", state)
        title = saves[index]
        if title == "autosave":
            title = "Autosave (last door opened)"
        art.text(str(index + 1) + ".  " + title, rect.x + 16, rect.y + 6, "bold", art.INK, "left")
        art.text(summaries[index], rect.x + 40, rect.y + 27, "small", art.BLOOD, "left")
    art.text("Click a save (or press its number) to load it.   Esc = back", W // 2, 650, "body", art.PARCHMENT_DARK,
             "center")


def hover_border(rect):
    """AI-assisted: receives a rectangle; returns the border color for it (gold under the mouse, brass otherwise)."""
    if rect.collidepoint(pygame.mouse.get_pos()):
        return art.GOLD
    return art.BRASS_DARK


def load_screen():
    """AI-assisted: receives nothing; lists the saved games and waits for the player to pick one; returns its name, or "" to go back."""
    saves = savegame.list_saves()[:8]
    summaries = []
    for name in saves:
        summaries.append(savegame.save_summary(name))
    while not UI["closed"]:
        draw_load_screen(saves, summaries)
        for event in present(None):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return ""
            elif event.type == pygame.KEYDOWN and pygame.K_1 <= event.key < pygame.K_1 + len(saves):
                return saves[event.key - pygame.K_1]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for index in range(len(saves)):
                    if save_rect(index).collidepoint(event.pos):
                        return saves[index]
    return ""


def recruit_rect(index):
    """AI-assisted: receives a recruit number; returns that recruit's card rectangle on the party screen."""
    return pygame.Rect(330 + index * 232, 170, 216, 380)


def draw_recruit(data, name, rect, chosen):
    """AI-assisted: receives the data, a hero name, a rectangle and whether the hero is chosen; draws the recruit card; returns nothing."""
    info = data["heroes"][name]
    color = art.CLASS_COLORS[info["kind"]]
    border = art.BRASS_DARK
    if chosen:
        border = art.GOLD
        pygame.draw.rect(UI["screen"], art.GOLD, rect.inflate(8, 8), 3, 10)
    art.panel(rect, "parchment", border)
    art.panel(pygame.Rect(rect.x + 28, rect.y + 16, 160, 160), "slate", color)
    art.draw_hero(info["kind"], rect.centerx, rect.y + 92, 52)
    art.text(name, rect.centerx, rect.y + 200, "head", art.INK, "center")
    art.text(info["title"], rect.centerx, rect.y + 224, "small", art.BLOOD, "center")
    art.draw_icon("heal", rect.centerx - 22, rect.y + 256, 8, art.CRIMSON)
    art.text(str(info["hp"]) + " HP", rect.centerx + 8, rect.y + 256, "bold", art.INK, "center")
    lines = art.wrap_text(info["blurb"], "small", rect.width - 24)
    for number in range(len(lines)):
        art.text(lines[number], rect.centerx, rect.y + 286 + number * 18, "small", art.INK, "center")
    if chosen:
        art.draw_plate(pygame.Rect(rect.centerx - 70, rect.bottom - 38, 140, 26), "In the party", "on")
    else:
        art.draw_plate(pygame.Rect(rect.centerx - 70, rect.bottom - 38, 140, 26), "Click to add", "off")


def draw_party_screen(data, recruits, chosen, buttons, note):
    """AI-assisted: receives the data, the recruit names, the chosen names, the buttons and a note; draws the party screen; returns nothing."""
    art.draw_backdrop()
    art.text_outline("Choose Your Party", W // 2, 62, "title", art.GOLD, "center")
    art.divider(W // 2, 96, 420)
    art.text("Frodo always leads. Add at least 2 companions (up to 3) by clicking them, or press 1-"
             + str(len(recruits)) + ".", W // 2, 126, "body", art.PARCHMENT, "center")
    count = "Companions chosen: " + str(len(chosen)) + " of 3"
    if len(chosen) < 2:
        count += "  -  choose " + str(2 - len(chosen)) + " more to begin"
    art.text(count, W // 2, 152, "bold", art.GOLD, "center")
    draw_recruit(data, "Frodo", pygame.Rect(98, 170, 216, 380), True)
    for index in range(len(recruits)):
        draw_recruit(data, recruits[index], recruit_rect(index), recruits[index] in chosen)
        art.medallion(recruit_rect(index).x + 18, recruit_rect(index).y + 18, 13, art.PARCHMENT, art.BRASS)
        art.text(str(index + 1), recruit_rect(index).x + 18, recruit_rect(index).y + 18, "bold", art.INK, "center")
    art.text(note, W // 2, 582, "body", art.GOLD, "center")
    for button in buttons:
        if button["id"] == "go" and len(chosen) < 2:
            art.draw_plate(button["rect"], button["label"], "off")
        else:
            art.draw_button(button)


def toggle_recruit(chosen, name):
    """AI-assisted: receives the chosen names and one recruit name; adds or removes that recruit (3 at most); returns a note for the player."""
    if name in chosen:
        chosen.remove(name)
        return name + " stays behind."
    elif len(chosen) >= 3:
        return "The party is full (Frodo + 3). Click a chosen hero to swap them out."
    chosen.append(name)
    return name + " joins the party!"


def party_event(event, recruits, buttons):
    """AI-assisted: receives one event, the recruit names and the buttons; returns "go", "back", a recruit name to toggle, or ""."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            return "go"
        elif event.key == pygame.K_ESCAPE:
            return "back"
        elif pygame.K_1 <= event.key < pygame.K_1 + len(recruits):
            return recruits[event.key - pygame.K_1]
    elif event.type == pygame.MOUSEBUTTONDOWN:
        for index in range(len(recruits)):
            if recruit_rect(index).collidepoint(event.pos):
                return recruits[index]
        return button_at(buttons, event.pos)
    return ""


def party_screen(data):
    """AI-assisted: receives the loaded data; starts with only Frodo and lets the player add 2 or 3 companions; returns the party name list (Frodo first), or [] to go back."""
    recruits = []
    for name in data["heroes"]:
        if name != "Frodo":
            recruits.append(name)
    chosen = []
    note = ""
    buttons = [make_button("go", "Begin (Enter)", pygame.Rect(W // 2 - 190, 622, 180, 44)),
               make_button("back", "Back (Esc)", pygame.Rect(W // 2 + 10, 622, 180, 44))]
    while not UI["closed"]:
        draw_party_screen(data, recruits, chosen, buttons, note)
        for event in present(None):
            choice = party_event(event, recruits, buttons)
            if choice == "go" and len(chosen) >= 2:
                return ["Frodo"] + chosen
            elif choice == "go":
                note = "Choose at least 2 companions to join Frodo first."
            elif choice == "back":
                return []
            elif choice != "":
                note = toggle_recruit(chosen, choice)
    return []


def title_flow(data, note):
    """AI-assisted: receives the loaded data and a note for the title screen; runs the title, Continue, rules and party screens; returns {"party": names} for a new game, {"file": name} to load a save, or {} to quit."""
    while not UI["closed"]:
        choice = title_screen(note)
        note = ""
        if choice == "rules":
            show_rules()
        elif choice == "continue":
            name = load_screen()
            if name != "":
                return {"file": name}
        elif choice == "start":
            party = party_screen(data)
            if len(party) > 0:
                return {"party": party}
        else:
            break
    return {}


# ================================================================ full screens: rules, status, end

RULES = [
    ["Quick Start", []],
    ["The Quest", [
        "You are Frodo, a small white dog in a knight's helmet, and you lead the party.",
        "Spears, the Dungeon Lord, has dug a dungeon of about 12 chambers. It is different every game.",
        "WIN: reach the Throne of Spears and destroy his Warlord. LOSE: every hero is exhausted, or the Doom Track",
        "    (the crimson bar, top right) fills up. Doom rises every round, and faster when you spring traps.",
        "Every chamber's doors stay sealed until all enemies in that chamber are destroyed. Then they glow as EXITs:",
        "    walk a hero onto one and the chamber behind it is dug out and filled - Spears shapes it to counter you.",
        "MAIN PATH or SIDE CHAMBER? Most chambers have one door onward. Some also have a side door to an optional",
        "    chamber with extra chests and rarer loot - but it costs rounds, and every round costs Doom.",
        "THE BOSS: the door to the Throne of Spears wears a red skull.",
        "    At half health the Warlord summons his Iron Guard. Near death he becomes ENRAGED (+2 attack, +1 move)."]],
    ["A Hero's Turn", [
        "Heroes and enemy units take turns in order: the row of portraits at the top left (left goes first).",
        "Each hero has a SPEED (lower acts earlier) and a MOVE (how many tiles they walk each turn).",
        "On a hero's turn you may do these in any order:",
        "WALK: the tiles you can reach glow blue, each with its step count. Click one (or drag the hero onto it)",
        "    and the hero walks there tile by tile. You can walk again with any moves left over.",
        "PLAY ONE CARD: the hero holds 3 cards (bottom of the screen). Drag one onto a glowing target:",
        "    an enemy to attack it, a hero to heal them, or the hero itself for a shield or a dash.",
        "    (Or click the card, then click the target.) A new card is drawn straight away.",
        "Then click End turn (E). Things you cannot use look dark; a bad drop snaps back and says why.",
        "Stand on a chest or shrine to loot it. Walk onto a glowing EXIT door to open the next chamber."]],
    ["Fog of War", [
        "You only see chambers you have opened. Everything else is black - even the boss's throne room.",
        "In opened chambers you can always see the SHAPE of the room: walls, floor, doors and the grid.",
        "You only see what is IN a chamber near your heroes: about 5 steps on foot. Walls block the view.",
        "Darkened places show what you remember. Chests and shrines you have seen stay on the map.",
        "Enemies in the dark are hidden. They still move and may shoot from the dark.",
        "Spears never changes the chamber you are in. But after a round he may secretly prepare a chamber you",
        "    have not opened yet: an extra trap, a trapped chest or an extra guard. You only see a warning.",
        "Hover the mouse over a hero, an enemy or an object on the map to read its details.",
        "CAMERA: mouse wheel zooms in and out. Hold the RIGHT mouse button and drag (or use W A S D) to pan.",
        "    Home shows the whole dungeon you know. The camera follows whoever is acting."]],
    ["Keyboard Controls", [
        "Everything can also be done without the mouse.",
        "MENU (always at the bottom right on a hero's turn): F1 Rules, F2 Status, F3 Save, F9 Quit.",
        "SAVING: F3 saves the whole game under a name you type. The game also saves itself every time a door",
        "    opens. Choose Continue on the title screen to load a save.   Hold SPACE to speed up enemy turns.",
        "WALK: arrows move the white cursor, Enter walks to the cursor tile.",
        "    Or press M, type how many tiles, then press an arrow key for the direction.",
        "CARDS: 1, 2 or 3 chooses a card, arrows move the cursor to a target, Enter plays it. Esc puts it back.",
        "E = end the turn.",
        "TYPED BOXES: type, Enter to confirm, Esc to cancel. A wrong entry shows a message and asks again.",
        "CAMERA: W A S D pan, + and - zoom, Home = whole map.   Mouse wheel over the log scrolls it.",
        "POP-UP QUESTIONS: Y = yes, N = no.   F11 = full screen."]],
    ["Cards and Combat", [
        "Every hero has a deck of 8 cards and holds 3 of them. Each card is ONE action, shown by its big icon:",
        "    ATTACK 3, range 4 = 3 damage to an enemy up to 4 tiles away (melee = the tile right next to you).",
        "    HEAL 2 = heal a hero in range.   SHIELD 2 = block 2 damage from every hit this round.",
        "    DASH +4 = 4 extra tiles of walking this turn.",
        "Play one card a turn. It goes to the discard pile and a new card is drawn from the deck at once.",
        "    When the deck runs out, the discard pile is shuffled into a new deck. You never run out of cards.",
        "Every attack flips a modifier card: +0, +1, -1, +2, -2, x2 (double damage) or MISS.",
        "ELEMENTS: a card with a fire, frost or light icon makes that medallion glow (top of the screen).",
        "    The next card with the same icon uses up the glow for +1.",
        "A hero with 0 HP is EXHAUSTED and leaves the fight. If Frodo falls, the party fights on without him.",
        "EVERY TIME A DOOR OPENS the party catches its breath and heals."]],
    ["Spears and his Armies", [
        "Enemies fight in UNITS of several models that stay within 2 tiles of each other (dark red outline).",
        "The red drops under a model are its wounds (hit points). Toughness blocks damage from each hit.",
        "Each unit acts in phases: MOVE, then SHOOT (ranged units) or CHARGE (a dice roll for distance) and FIGHT.",
        "MORALE: a unit below half strength rolls 2 dice. If the roll is over its leadership it loses a model or runs.",
        "Spears goes for weak heroes, flanks them, and his Iron Guard hold the door until you come close.",
        "HE ADAPTS: lots of melee brings armored guards and slingers. Lots of ranged brings fast Wolf Riders and cover.",
        "    Looting brings trapped chests and Shade Stalkers. Huddling together brings Bomb Flingers and hidden pits.",
        "After a round he may secretly prepare a chamber ahead: an extra trap, trapped chest or guard.",
        "Enemies walk, strike and shoot on screen, and a caption says what each unit is doing. Hold SPACE to speed up."]],
]

LEGEND = [["C", "Chest - move onto it for loot"], ["P", "Shrine - a small gift"],
          ["T", "Trap - 2 damage and Doom +1"], ["~", "Cover - blocks 1 damage from shots"],
          ["D", "Door - sealed until the room is clear"]]


def draw_legend(top):
    """AI-assisted: receives the y position to start at; draws the map legend with the real tile art; returns nothing."""
    for index in range(len(LEGEND)):
        rect = pygame.Rect(150 + (index % 3) * 350, top + (index // 3) * 62, TILE, TILE)
        art.draw_floor(rect, index)
        art.draw_feature(LEGEND[index][0], rect, False)
        pygame.draw.rect(UI["screen"], art.INK, rect, 2)
        art.text(LEGEND[index][1], rect.right + 8, rect.y + 15, "small", art.INK, "left")


def quick_panel(rect, title, lines):
    """AI-assisted: receives a rectangle, a heading and its lines; draws one step of the quick-start card; returns the rectangle."""
    art.panel(rect, "parchment", art.BRASS)
    art.ribbon(rect.centerx, rect.y + 20, rect.width - 30, title, art.BLOOD)
    y = rect.y + 196
    for sentence in lines:
        for line in art.wrap_text(sentence, "small", rect.width - 24):
            art.text(line, rect.centerx, y, "small", art.INK, "center")
            y += 18
    return rect


def quick_pictures(boxes):
    """AI-assisted: receives the four quick-start panels; draws the little picture in each (the Warlord, a glowing tile, a card and an EXIT door); returns nothing."""
    art.draw_model("warlord", boxes[0].centerx, boxes[0].y + 110, 36)
    tile = pygame.Rect(boxes[1].centerx - 20, boxes[1].y + 80, 70, 70)
    art.draw_floor(tile, 1)
    art.glow_rect(tile, art.GLOW_COLORS["move"], 90)
    art.text_outline("2", tile.right - 10, tile.bottom - 12, "bold", art.WHITE, "center")
    art.draw_hero("archer", tile.x - 30, tile.y + 26, 15)
    card = {"name": "Quick Shot", "action": {"kind": "attack", "amount": 2, "range": 4}, "element": "none"}
    art.draw_card(card, pygame.Rect(boxes[2].x + 12, boxes[2].y + 50, 110, 132), art.GOLD, "archer")
    art.draw_model("orc", boxes[2].right - 38, boxes[2].y + 110, 17)
    pygame.draw.line(UI["screen"], art.GOLD, (boxes[2].x + 126, boxes[2].y + 116), (boxes[2].right - 62, boxes[2].y + 116), 3)
    door = pygame.Rect(boxes[3].centerx - 35, boxes[3].y + 80, 70, 70)
    art.draw_door(door, True)


def draw_quickstart(sheet):
    """AI-assisted: receives the rectangle to draw in; draws the one-page quick-start card (goal, walk, cards, doors, colours); returns nothing."""
    art.panel(sheet, "leather", art.GOLD)
    art.text_outline("Quick Start", sheet.centerx, sheet.y + 34, "title", art.GOLD, "center")
    width = (sheet.width - 50) // 4
    boxes = []
    steps = [["Your Goal", ["Reach the boss behind the RED-SKULL door and defeat him.",
                            "Don't let the Doom bar (top right) fill up."]],
             ["1. Walk", ["On a hero's turn, click a BLUE tile to walk there.", "The number is how many steps."]],
             ["2. Play a Card", ["Drag ONE card from the bottom onto a glowing target.",
                                 "Red = enemy, green = friend. A new card is drawn."]],
             ["3. Open Doors", ["Beat every enemy in a room, then walk onto the glowing EXIT door.",
                                "Click End turn when you are done."]]]
    for index in range(4):
        box = pygame.Rect(sheet.x + 10 + index * (width + 10), sheet.y + 66, width, 292)
        boxes.append(quick_panel(box, steps[index][0], steps[index][1]))
    quick_pictures(boxes)
    legend = [["move", "Blue: walk"], ["attack", "Red: attack"], ["heal", "Green: heal"], ["gold", "Gold: your hero"]]
    for index in range(4):
        spot = pygame.Rect(sheet.x + 60 + index * 210, sheet.y + 372, 26, 26)
        art.glow_rect(spot, art.GLOW_COLORS[legend[index][0]], 120)
        art.text(legend[index][1], spot.right + 10, spot.y + 4, "body", art.PARCHMENT, "left")
    art.text("Hover over anything on the map to learn about it.   F1 = rules (this card is page 1).",
             sheet.centerx, sheet.bottom - 30, "small", art.PARCHMENT_DARK, "center")


def show_quickstart(game):
    """AI-assisted: receives the game; shows the quick-start card over the map until the player clicks or presses a key; returns nothing."""
    if UI["screen"] is None:
        return
    waiting = True
    while game["running"] and waiting:
        draw_game(game)
        dim_screen()
        draw_quickstart(pygame.Rect(120, 90, W - 240, 470))
        art.text_outline("Click or press any key to begin", W // 2, 600, "head", art.GOLD, "center")
        for event in present(game):
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False


def draw_rules_page(number):
    """AI-assisted: receives a rules page number; draws that page on a parchment sheet; returns nothing."""
    art.draw_backdrop()
    sheet = pygame.Rect(60, 36, W - 120, H - 72)
    art.panel(sheet, "parchment", art.BRASS)
    page = RULES[number]
    if len(page[1]) == 0:
        draw_quickstart(sheet.inflate(-40, -110).move(0, -10))
        art.text("Page " + str(number + 1) + " of " + str(len(RULES)) + "     Right arrow or click = next     Esc = close",
                 W // 2, sheet.bottom - 28, "small", art.BLOOD, "center")
        return
    art.text(page[0], W // 2, 76, "title", art.BLOOD, "center")
    art.divider(W // 2, 106, 520)
    y = 128
    for sentence in page[1]:
        for line in art.wrap_text(sentence, "body", sheet.width - 110):
            art.text(line, 112, y, "body", art.INK, "left")
            y += 23
        y += 9
    if number == 1:
        draw_legend(y + 14)
    art.text("Page " + str(number + 1) + " of " + str(len(RULES))
             + "     Right arrow or click = next     Left arrow = back     Esc or Enter = close",
             W // 2, sheet.bottom - 28, "small", art.BLOOD, "center")


def show_rules():
    """AI-assisted: receives nothing; shows the rules pages until the player closes them; returns the last page number seen."""
    number = 0
    while not UI["closed"]:
        draw_rules_page(number)
        for event in present(None):
            if event.type == pygame.MOUSEBUTTONDOWN:
                number += 1
            elif event.type != pygame.KEYDOWN:
                continue
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                number += 1
            elif event.key == pygame.K_LEFT:
                number = max(0, number - 1)
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return number
        if number >= len(RULES):
            return len(RULES) - 1
    return number


def memory_line(game):
    """AI-assisted: receives the game; returns a sentence listing what Spears has noticed about the party."""
    memory = game["memory"]
    return ("Spears has noticed: " + str(memory["melee_hits"]) + " melee hits, "
            + str(memory["ranged_hits"]) + " ranged hits, " + str(memory["chests_opened"]) + " chests, "
            + str(memory["clumped"]) + " huddles, " + str(memory["tiles_moved"]) + " tiles moved.")


def draw_status_box(lines):
    """AI-assisted: receives the status sentences; draws them in a pop-up parchment box; returns nothing."""
    dim_screen()
    box = pygame.Rect(140, 110, 1000, 130 + len(lines) * 40)
    art.panel(box, "parchment", art.BRASS)
    art.text("Current Status", box.centerx, box.y + 34, "title", art.BLOOD, "center")
    art.divider(box.centerx, box.y + 62, 420)
    y = box.y + 82
    for sentence in lines:
        for line in art.wrap_text(sentence, "body", box.width - 60):
            art.text(line, box.x + 30, y, "body", art.INK, "left")
            y += 22
        y += 6


def show_status(game):
    """AI-assisted: receives the game; shows the current status in a pop-up until a key or click; returns how many lines were shown."""
    lines = logbook.status_lines(game) + [memory_line(game), "", "Press any key or click to close."]
    waiting = True
    while game["running"] and waiting:
        draw_game(game)
        draw_status_box(lines)
        for event in present(game):
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
    return len(lines)


def draw_end(result, lines):
    """AI-assisted: receives "win" or "lose" and the summary sentences; draws the victory or defeat screen; returns nothing."""
    art.draw_backdrop()
    art.torch_glow(300, 420, 280)
    if result == "win":
        art.text_outline("Victory!", W // 2, 92, "huge", art.GOLD, "center")
        art.text("The Warlord falls. Frodo demands a treat.", W // 2, 160, "head", art.PARCHMENT, "center")
        art.draw_hero("leader", 300, 410, 110)
    else:
        art.text_outline("Defeat", W // 2, 92, "huge", art.CRIMSON, "center")
        art.text("Spears laughs in the dark. The dungeon wins... this time.", W // 2, 160, "head", art.PARCHMENT, "center")
        art.draw_model("warlord", 300, 400, 96)
    sheet = pygame.Rect(560, 204, 560, 76 + len(lines) * 34)
    art.panel(sheet, "parchment", art.BRASS)
    art.ribbon(sheet.centerx, sheet.y + 26, 300, "Adventure Summary", art.BLOOD)
    for number in range(len(lines)):
        art.text(lines[number], sheet.x + 40, sheet.y + 60 + number * 34, "body", art.INK, "left")
    art.text("The full story is saved in frodo_log.txt.     Press Enter or click to close.",
             W // 2, 684, "body", art.PARCHMENT_DARK, "center")


def end_screen(result, lines):
    """AI-assisted: receives "win" or "lose" and the summary sentences; shows the end screen until the player closes it; returns the result."""
    while not UI["closed"]:
        draw_end(result, lines)
        for event in present(None):
            if event.type == pygame.MOUSEBUTTONDOWN:
                return result
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                return result
    return result
