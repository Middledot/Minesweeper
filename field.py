"""The code that handles the properties and behaviour of the minefield"""

from __future__ import annotations

import pygame
from math import floor, ceil
from random import randrange
from typing import TYPE_CHECKING

from consts import (
    numtocol,
    xico,
    flagico,
    mineico,
    State,
    Coords
)
from mod.grid import Grid

if TYPE_CHECKING:
    from game import Minesweeper

class Field:
    box: pygame.Surface
    flagico: pygame.Surface
    mineico: pygame.Surface
    xico: pygame.Surface

    top: int
    bottom: int
    left: int
    right: int

    def __init__(self, game: Minesweeper, mines: int = 20):
        self._game = game

        # TUPLE STRUCT:
        #  (0, 0, 0, 0)
        #            - Is this square flagged?
        #         - How many mines are around it? [TODO: do on the fly?]
        #      - Is this square uncovered?
        #   - Does this square have a mine?
        self._grid = Grid(game.width, game.height, (0, 0, 0, 0))

        # Minimum size of a square. Maybe move to consts.py?
        self.minsqrsize = 15

        # These are set in the next function
        self.sqrsize = 0  # size of a square (will adjust)
        self.margins = (0, 0)  # margins for (leftright, updown)
        self.mainfont: pygame.font.Font  # the font for the mine numbers

        self.adjust()

        # All mineless squares uncovered add to the counter
        # All mined squares flagged add to the counter
        # Other states do not
        self.correctsquares = 0
        self.flagged = mines  # for the mine counter, is subtrated from over time
        self.minesno = mines  # num o' mines

        self.target = None  # the mine they clicked and lost
        # the field isn't initialized until the user clicks to guarantee
        # they don't immediately click on a mine
        self.initialized = False

    # these 3 are shortcuts

    @property
    def w(self) -> int:
        return self._game.w

    @property
    def h(self) -> int:
        return self._game.h

    @property
    def state(self):
        return self._game.state

    @state.setter
    def state(self, val):
        self._game.state = val

    @property
    def minmargin(self):
        # I don't exactly remember why I made this, but
        # it works so I'm leaving it (this is to calculate
        # the minimum margin that all the adjustment code is based on)
        return ((0.1*self.h)+(0.1*self.w))/2

    def adjust(self):
        """Function to manage adjustent of field size on screen (super high tech!!)."""
        # If only I was using html
        # TODO: clicking in small dimensions doesn't work

        # FIRST PART: adjust grid
        if (self._grid.rows() > self._grid.cols()) or (self.h < self.w):
            #   The field height is bigger
            #               OR
            #   the pixel height is smaller
            #   so the minmargin will be the topbottom
            #   and the calculated margin will be leftright
            check = True
        elif (self._grid.rows() < self._grid.cols()) or (self.h > self.w):
            # This is the opposite
            check = False
        else:
            check = None

        # For the suffixes: 
        #   p = pixels dimensions
        #   f = field dimensions
        if check:
            biggerp = self.h
            smallerp = self.w
            biggerf = self._grid.rows()
        else:
            biggerp = self.w
            smallerp = self.h
            biggerf = self._grid.cols()

        # The size of all squares
        self.sqrsize = (biggerp - (2 * self.minmargin))/biggerf
        # self.sqrsize += self.sqrsize * 0.05
        if self.sqrsize < self.minsqrsize:
            self.sqrsize = self.minsqrsize

        # compensate for decimal rounding
        # TODO:
        #   Compensation still doesn't work sometimes probably because of the
        #   prioritization of one axis over the other on even-sided grids
        compensation = 0
        if (compen := self.sqrsize % 1) != 0:
            # split amongst each margin
            compensation = (compen * biggerf)/2
            self.sqrsize = floor(self.sqrsize)

        if check:
            self.margins = (ceil(compensation + (smallerp - (self._grid.cols() * self.sqrsize)) / 2), compensation + self.minmargin)
        else:
            self.margins = (compensation + self.minmargin, ceil(compensation + (smallerp - self._grid.rows() * self.sqrsize) / 2))

        self.top = round(self.minmargin)
        self.bottom = round(biggerp - self.minmargin)
        self.left = round(self.margins[1])
        self.right = round(smallerp - self.minmargin)

        self.box = pygame.Surface((self.sqrsize, self.sqrsize))

        # SECOND PART: adjust icons and fonts
        biggersize = self.sqrsize * 1.3  # make it fill the square better
        self.flagico = pygame.transform.scale(
            flagico,
            (self.sqrsize, self.sqrsize)
        )
        self.mineico = pygame.transform.scale(
            mineico,
            (self.sqrsize, self.sqrsize)
        )
        self.xico = pygame.transform.scale(
            xico,
            (self.sqrsize, self.sqrsize)
        )
        self.mainfont = pygame.font.SysFont("Corbel", round(biggersize))
        self._game.verycoolfont = pygame.font.Font("assets/minesweeper.ttf", round(biggersize/3))

    def __iter__(self):
        """Shortcut for iterating the grid"""
        yield from self._grid

    def initialize(self, theexempt):
        """Setup all the mines in the field."""
        for _ in range(self.minesno):
            while True:
                x = randrange(self._grid.cols())
                y = randrange(self._grid.rows())
                if (x, y) in theexempt:
                    continue
                if self._grid.get((x, y))[0] == 0:
                    break

            # TODO: ik about this fix it
            # to clarify: the fact I have to set every single data even
            # if I'm only changing one
            self._grid.set((x, y), (1, 0, 0, 0))
        for tile in self:
            data = self._grid.get(tile)
            if data[0] == 1:
                continue

            count = 0
            for nb in self._grid.iterneighbours(tile):
                ctile = self._grid.get(nb)
                if ctile[0] == 1:
                    count += 1

            self._grid.set(tile, (data[0], data[1], count, 0))

    def forestfires(self, pos, _from: list = []):
        """This is a recursive function that clears all neighbouring empty squares
        if empty square was clicked. Thus, a forest fire.
        """
        for tile in self._grid.iterneighbours(pos):
            # Remove all their flags
            mined, uncovered, mines, _ = self._grid.get(tile)
            if uncovered:
                continue
            if tile in _from:
                continue
            
            self._grid.set(tile, (mined, 1, mines, 0))
            if mines == 0:
                _from.append(pos)
                self.forestfires(tile, _from)

    def click(self, pos, flagging):
        """Handle clicking on the minefield"""
        cell = self.pixel2grid(pos)
        x, y = cell
        if x < 0 or x > self._grid.rows() or y < 0 or y > self._grid.cols():
            return  # outtabounds

        # decides the positions of all the mines on the first click
        if self.initialized == False:
            listt = [cell]
            ncells = list(self._grid.iterneighbours(cell))
            listt += ncells
            for i in ncells:
                listt += list(self._grid.iterneighbours(i))

            listt = list(set(listt))
            self.initialize(listt)
            self.initialized = True

        data = self._grid.get(cell)
        if data is None:
            return

        mined, uncovered, mines, flagged = data
        # ignore already uncovered mines
        if uncovered:
            return

        if flagging:
            # if right clicking
            if not flagged:
                flagged = 1
                self.flagged -= 1
                if mined:
                    self.correctsquares += 1
            else:
                flagged = 0
                self.flagged += 1
                if mined:
                    self.correctsquares -= 1
            self._grid.set(cell, (mined, uncovered, mines, flagged))
        else:
            # if left clicking
            if flagged:
                return
            if mined:
                self.target = cell
                self._game.lost()
                return

            self._grid.set(cell, (mined, 1, mines, 0))
            if mines == 0:
                # empty square, so clear neighbours
                self.forestfires(cell, _from=[])

        if self.correctsquares == self.minesno:
            self._game.won()

    def grid2pixel(self, pos: Coords) -> Coords:
        # given a position where pos = (x, y) is in grid coordinates
        # return the pixel coordinates of the northwest corner of pos

        x, y = pos
        return (self.sqrsize * x, self.sqrsize * y)
    
    def pixel2grid(self, pos: Coords) -> Coords:
        # given a position where pos = (x, y) is in pixel coordinates
        # return the grid coordinates of the northwest corner of pos
        x, y = pos
        x, y = x-self.margins[0], y-self.margins[1]
        res = (int(x // self.sqrsize), int(y // self.sqrsize))
        return res
    
    def draw(self, image: pygame.Surface):
        """Draw the grid."""
        for x, y in self:
            self.draw_cell(image, (x, y))

    def draw_cell(self, image: pygame.Surface, pos):
        """Draw a single cell."""
        mined, uncovered, mines, flagged = self._grid.get(pos)

        if pos == self.target:
            color = pygame.Color("red")
        elif (
            uncovered
            or (self.state is State.lost and (bool(mined) ^ bool(flagged)))  # XOR operation
            or (self.state is State.won and (not uncovered ^ bool(flagged)))
        ):
            color = pygame.Color("white")
        else:
            color = pygame.Color("grey")

        self.box.fill(color)
        pygame.draw.rect(
            self.box,
            (0, 0, 0),
            rect=pygame.Rect(0, 0, self.sqrsize, self.sqrsize), #self.box.get_width(), self.box.get_height()),
            width=1
        )
        if mines > 0 and (uncovered or (self.state is State.won and (not uncovered ^ bool(flagged)))):
            self.writeonmine(self.box, mines)
        drawx, drawy = self.grid2pixel(pos)
        drawx, drawy = drawx + self.margins[0], drawy + self.margins[1]

        if self.state is State.lost:
            # TODO: cleanup
            if mined and not flagged:
                self.box.blit(self.mineico, (0, 0))
            elif not mined and flagged:
                self.box.blit(self.mineico, (0, 0))
                self.box.blit(self.xico, (0, 0))
            elif mined and flagged:
                self.box.blit(self.flagico, (0, 0))
        elif flagged:
            self.box.blit(self.flagico, (0, 0))

        image.blit(self.box, (drawx-1, drawy-1))

    def writeonmine(self, image: pygame.Surface, number):
        """Used for showing the number of neighbours with mines."""
        textimg = self.mainfont.render(str(number), True, numtocol[number])
        w = (image.get_width() - textimg.get_width()) / 2
        h = (image.get_height() - textimg.get_height()) / 2
        image.blit(textimg, (w, h))
