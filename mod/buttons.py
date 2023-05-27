"""Button object"""

from __future__ import annotations

import pygame
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..game import Minesweeper

# this uses an entirely different font obj because the other
# one adjusts for screensize *according to the size of a tile*
# which won't do for buttons
secfont = pygame.font.SysFont("Corbel", 30)

class Button:
    text: str
    txtsurf: pygame.surface.Surface
    rectsurf: pygame.Rect

    def __init__(
        self,
        gameobj,
        text,
        # size = None,
        textclr = None,
        btnclr = None,
        btnhoverclr = None,
        # btnclickclr = None,
    ):
        self._game: Minesweeper = gameobj
        self.pos: Tuple[int, int] = (0, 0)
        # self.size = size

        self.textclr = textclr or "#000000"
        self.btnclr = btnclr or "#81d6e3"
        self.btnhoverclr = btnhoverclr or "#4cb5ae"
        # self.btnclickclr = btnclickclr or self.btnhoverclr

        self.updateobjs(text)

    def position(self, pos):
        """Set the position"""
        # This is its own function because screen resizing
        self.pos = pos
        self.rectsurf.center = self.pos

    def updateobjs(
        self,
        newtxt,
        btnclr = None,
        btnhoverclr = None
    ):
        """This function takes the new text of the button and
        updates all the objects (txt, rect) that depend on it.
        """
        self.text = newtxt
        self.txtsurf = secfont.render(newtxt, True, pygame.Color(self.textclr))
        self.rectsurf = self.txtsurf.get_rect()
        if self.pos:
            self.rectsurf.center = self.pos

        if btnclr is not None:
            self.btnclr = btnclr

        if btnhoverclr is not None:
            self.btnhoverclr = btnhoverclr

    def render(self):
        """Render the button"""
        if self.ishovering():
            print(self.btnhoverclr)
            color = self.btnhoverclr
        else:
            color = self.btnclr

        self._renderrect(margin=5, color=pygame.Color(color))
        self._game.screen.blit(self.txtsurf, self.rectsurf)

    def ishovering(self):
        """Check if mouse if hovering over this button"""
        if self._game.mousepos is None:
            return False

        print(self.rectsurf.left, self.rectsurf.right, self.rectsurf.top, self.rectsurf.bottom, self._game.mousepos, self._game.inrect(self._game.mousepos, self.rectsurf))

        return self._game.inrect(self._game.mousepos, self.rectsurf)

    def _renderrect(self, margin, color):
        """Draw the rectangle part of the button"""
        pygame.draw.rect(
            self._game.screen,
            pygame.Color(color),
            (
                self.rectsurf.left - margin,
                self.rectsurf.top - margin,
                self.rectsurf.width + (2 * margin),
                self.rectsurf.height + (2 * margin)
            )
        )
