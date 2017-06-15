'''A GUI to display the status of downloaded images'''

import curses
import os
import re

import requests
import xmltodict

EMPTY_CHAR = "-"
TILE_CHAR = "X"

IMAGE_DIRECTORY = "images"

Y_OFFSET = 5
X_OFFSET = 1

session = requests.session()

def get_pyramid(key):
    '''Create the 'pyramid' of tiles for an image.'''

    # Request the pyramid and parse it the xml
    response = session.get(f"https://lh6.ggpht.com/{key}=g").text
    xml = xmltodict.parse(response)["TileInfo"]["pyramid_level"]

    # Add all the layers
    pyramid = []
    for level in xml:
        height = int(level["@num_tiles_y"])
        width = int(level["@num_tiles_x"])

        pyramid.append([[EMPTY_CHAR] * width for _ in range(height)])

    return pyramid

class UI:
    '''The UI class that holds infomation about screens'''

    pyramids = {}
    index = 0
    level = 0
    min_x = 0
    min_y = 0

    def __init__(self, screen):
        curses.use_default_colors()
        curses.init_pair(1, 8, -1)
        self.screen = screen
        self.keys = [key for key in os.listdir(IMAGE_DIRECTORY) if not key.startswith('.')]

        while True:
            key = self.key()

            if not key in self.pyramids:
                self.pyramids[key] = get_pyramid(key)

            self.add_new()
            self.draw()
            self.wait_for_key()

    def add_new(self):
        '''Add all the new tiles for the specific image 'pyramid'.'''

        # Get the pyramid to add to
        pyramid = self.pyramid()

        # Add all the new images
        for file in os.listdir(os.path.join(IMAGE_DIRECTORY, self.key())):
            try:
                z, x, y = re.findall("(\d+)-(\d+)-(\d+)", file)[0]
                z, x, y = int(z), int(x), int(y)
                if pyramid[z][y][x] == EMPTY_CHAR:
                    pyramid[z][y][x] = "new"
            except Exception as _:
                continue

    def commit_new(self):
        '''Change the 'new' tiles to the default tile character'''

        level = self.pyramid()[self.level]

        for y, row in enumerate(level):
            for x, tile in enumerate(row):
                if tile == "new":
                    level[y][x] = TILE_CHAR

    def key(self):
        '''Get the current key'''

        return self.keys[self.index]

    def pyramid(self):
        '''Get the pyramid for the current key'''

        return self.pyramids[self.key()]

    def levels(self):
        '''Get the number of levels in the current pyramid'''

        return len(self.pyramid())

    def width(self):
        '''Get the width of the current level in the pyramid'''

        return len(self.pyramid()[self.level][0])

    def height(self):
        '''Get the height of the current level in the pyramid'''

        return len(self.pyramid()[self.level])

    def draw(self):
        '''Draw the screen'''

        if self.level >= self.levels():
            self.level = self.levels() - 1

        max_y, max_x = self.screen.getmaxyx()
        visible_max_x = max_x + self.min_x - X_OFFSET
        visible_max_y = max_y + self.min_y - Y_OFFSET

        self.screen.erase()
        self.screen.addstr(1, X_OFFSET, f"{self.key()} {self.index + 1}/{len(self.keys)}")
        self.screen.addstr(2, X_OFFSET, f"Level {self.level}/{self.levels() - 1}")
        self.screen.addstr(3, X_OFFSET, f"x: showing {self.min_x}-{visible_max_x}/{self.width()}, y: showing {self.min_y}-{visible_max_y}/{self.height()}")

        for y, row in enumerate(self.pyramid()[self.level][self.min_y:]):
            for x, tile in enumerate(row[self.min_x:]):
                if Y_OFFSET + y >= max_y or X_OFFSET + x >= max_x:
                    continue

                if tile == "new":
                    self.screen.addstr(Y_OFFSET + y, X_OFFSET + x, TILE_CHAR)
                else:
                    self.screen.addstr(Y_OFFSET + y, X_OFFSET + x, tile, curses.color_pair(1))
        self.screen.refresh()

    def wait_for_key(self):
        '''wait for and handle key input. Any key other than these here will
        refresh the display (I like to use 'r' for this purpose)'''

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
            raise KeyboardInterrupt

# Break on a keyboard interrupt
try:
    curses.wrapper(UI)
except KeyboardInterrupt:
    pass
