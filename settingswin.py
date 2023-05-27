"""Code for the settings window"""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from game import Minesweeper

class SettingsWin:
    def __init__(self):
        # TODO: type this better
        self._game: Optional[Minesweeper] = None
        self.active = False

        self._win = tk.Tk()
        # TODO: how to place window in center of screen? idk
        # self._win.eval('tk::PlaceWindow . center')

        self._win.protocol("WM_DELETE_WINDOW", self._close)

        self._minesno: tk.IntVar = self._option("Number of Mines:")
        self._height: tk.IntVar = self._option("Minefield Height:")
        self._width: tk.IntVar = self._option("Minefield Width:")

        # submit button
        tk.Button(self._win, text="Submit", command=self._submit).pack()

        # hide the window
        self._win.withdraw()

    def _option(self, text):
        """Common code for all option creation"""
        opt = tk.IntVar(self._win)
        tk.Label(self._win, text=text).pack()
        mentry = tk.Entry(self._win, textvariable=opt)
        mentry.pack()
        return opt

    def _close(self):
        """Tell the game obj that the user closed the win."""
        self._game.tksubmit(1)  # type: ignore

    def _submit(self):
        """Call the game obj to manage the inputs"""
        self._game.tksubmit(0)  # type: ignore

    def update(self):
        """Update per tick, is called by the main game obj"""
        return self._win.update()

    def activate(self):
        """De-minimize (?) and appear"""
        self.active = True
        self._minesno.set(self._game.minesno)
        self._height.set(self._game.height)
        self._width.set(self._game.width)
        self._win.deiconify()

    def done(self):
        """Minimize the window and deactivate for now"""
        self._win.withdraw()
        self.active = False

    def minesno(self):
        """Retrieve input for mine no."""
        return int(self._minesno.get())

    def height(self):
        """Retrieve input for height of field"""
        return int(self._height.get())

    def width(self):
        """Retrieve input for width of field"""
        return int(self._width.get())
