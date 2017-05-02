import curses
import requests
import xmltodict
import re
import os

empty_char = "-"
tile_char = "X"

session = requests.session()

def get_pyramid(key):
    response = session.get(f"https://lh6.ggpht.com/{key}=g").text
    xml = xmltodict.parse(response)["TileInfo"]["pyramid_level"]
    pyramid = []

    for level in range(len(xml)):
        y = int(xml[level]["@num_tiles_y"])
        x = int(xml[level]["@num_tiles_x"])
        
        pyramid.append([[empty_char] * x for _ in range(y)])

    return pyramid

class UI:
    pyramids = {}
    index = 0
    level = 0
    min_x = 0
    min_y = 0
    
    def __init__(self, screen):
        curses.use_default_colors()
        curses.init_pair(1, 8, -1)
        self.screen = screen
        self.keys = keys = [key for key in os.listdir("images") if not key.startswith('.')]

        while True:
            self.loop()

    def loop(self):
        key = self.key()

        if not key in self.pyramids:
            self.pyramids[key] = get_pyramid(key)

        self.add_new()
        self.draw()
        self.wait_for_key()

    def add_new(self):
        pyramid = self.pyramid()

        for file in os.listdir(os.path.join("images", self.key())):
            try:
                z, x, y = re.findall("(\d+)-(\d+)-(\d+)", file)[0]
                z, x, y = int(z), int(x), int(y)
                if pyramid[z][y][x] == empty_char:
                    pyramid[z][y][x] = "new"
            except:
                continue

    def commit_new(self):
        level = self.pyramid()[self.level]

        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == "new":
                    level[y][x] = tile_char

    def key(self):
        return self.keys[self.index]

    def pyramid(self):
        return self.pyramids[self.key()]

    def levels(self):
        return len(self.pyramid())

    def width(self):
        return len(self.pyramid()[self.level][0])

    def height(self):
        return len(self.pyramid()[self.level])

    def draw(self):
        if self.level >= self.levels():
            self.level = self.levels() - 1

        y_offset, x_offset = 5, 1
        max_y, max_x = self.screen.getmaxyx()
        visible_max_x = max_x + self.min_x - x_offset
        visible_max_y = max_y + self.min_y - y_offset

        self.screen.erase()
        self.screen.addstr(1, x_offset, f"{self.key()} {self.index + 1}/{len(self.keys)}")
        self.screen.addstr(2, x_offset, f"Level {self.level}/{self.levels() - 1}")
        self.screen.addstr(3, x_offset, f"x: showing {self.min_x}-{visible_max_x}/{self.width()}, y: showing {self.min_y}-{visible_max_y}/{self.height()}")

        for y, row in enumerate(self.pyramid()[self.level][self.min_y:]):
            for x, tile in enumerate(row[self.min_x:]):
                if y_offset + y >= max_y or x_offset + x >= max_x:
                    continue
                
                if tile == "new":
                    self.screen.addstr(y_offset + y, x_offset + x, tile_char)
                else:
                    self.screen.addstr(y_offset + y, x_offset + x, tile, curses.color_pair(1))
        self.screen.refresh()

    def wait_for_key(self):
        keypress = self.screen.getkey()

        if keypress == 'KEY_UP':
            self.level = (self.level + 1) % self.levels()
        elif keypress == 'KEY_DOWN':
            self.level = (self.level - 1) % self.levels()
        elif keypress == 'KEY_LEFT':
            self.index = (self.index - 1) % len(self.keys)
        elif keypress == 'KEY_RIGHT':
            self.index = (self.index + 1) % len(self.keys)
        elif keypress == 'w':
            self.min_y = max(0, self.min_y - 1)
        elif keypress == 'a':
            self.min_x = max(0, self.min_x - 1)
        elif keypress == 's':
            self.min_y += 1
        elif keypress == 'd':
            self.min_x += 1
        elif keypress == 'c':
            self.commit_new()
        elif keypress == 'q':
            raise(KeyboardInterrupt)

try:
    curses.wrapper(UI)
except KeyboardInterrupt:
    exit
