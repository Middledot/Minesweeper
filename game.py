"""The Game"""

import pygame
from pygame.locals import VIDEORESIZE, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from tkinter import messagebox
from typing import Union, Tuple

from field import Field
from consts import segfont, tkwin, State, Coords
from mod.buttons import Button
from mod.game import BasicGame

class Minesweeper(BasicGame):
    def __init__(self):
        self.bg_color = (255, 255, 255)
        super().__init__(size=(500, 500))

        self.minesno = 30
        self.height = 10
        self.width = 10

        # restart button
        self.resbtn = Button(self, "Restart")
        # settings button
        self.settbtn = Button(self, "Settings")

        # current mouse position
        self.mousepos: Coords = (0, 0)
        # font obj for the title (to be set)
        self.verycoolfont: pygame.font.Font
        self.gamesetup()

        tkwin._game = self

    def gamesetup(self):
        """Setup/reset the game variables"""
        # mouse down state
        self.mdstate = False

        # confirming a restart variable
        self.rconfirm = False

        # uses enum, the current state
        self.state = State.playing

        # the actual field
        self.field = Field(
            game=self,
            mines=self.minesno
        )

        self.adjust()

    def update(self):
        """Frame update callback"""
        self.mousepos = pygame.mouse.get_pos()
        if tkwin.active:
            tkwin.update()
        else:
            pygame.display.flip()
            super().update()

    def key_poll(self, event: pygame.event.Event):
        """Callback for clicking events"""
        if event.type == MOUSEBUTTONDOWN:
            if self.mdstate == False:
                self.mdstate = True
                # TODO: debug this
                print(event.dict)
                self.mousedown(pygame.mouse.get_pressed(), self.mousepos)
                return True
        elif event.type == MOUSEBUTTONUP:
            self.mdstate = False

    def adjust(self):
        """Adjust buttons for screen resize (& other game related things)"""
        self.resbtn.position(((self.w/2-self.resbtn.rectsurf.width), (self.field.minmargin/2)))
        self.settbtn.position(((self.w/2+self.settbtn.rectsurf.width), (self.field.minmargin/2)))

    def meta_event_poll(self, event: pygame.event.Event):
        """Event handler for non-clicking (i.e. screen resize)"""
        if event.type == VIDEORESIZE:
            self.size = event.dict["size"]
            # different adjust functions because buttons
            # have nothing to do with fields
            print(self.size)
            self.adjust()
            self.field.adjust()

    def _inborder(self, pos: Coords, left, right, top, bott) -> bool:
        """Check if a position is inside the pixel boundaries"""
        x, y = pos
        if left < x < right and top < y < bott:
            return True
        return False

    def inrect(self, pos, rect: Union[pygame.Rect, Field]):
        """A shortcut _inborder function for the Field and pygame.Surface"""
        # The reason the 'inrect' function can accept the field is
        # because of the new left/right/top/bottom attributes that are
        # compatible with this function, so I'm just reusing code
        pygame.Surface
        return self._inborder(pos, rect.left, rect.right, rect.top, rect.bottom)

    def mousedown(
            self,
            button: Tuple[int, int, int],
            pos: Coords
        ):
        """Handle ALL clicking"""
        # opening = left click
        # flagging = right click
        # middle button is not important
        opening, _, flagging = button
        if self.inrect(pos, self.field) and self.state not in (State.lost, State.won):
            # click handling is delegated to the Field obj (unless the game is over)
            if opening or flagging:
                # NOTE: this is a bug w/ pygame or smth idk what it is
                if opening and flagging:
                    flagging = False

                self.field.click(pos, flagging)
        elif self.resbtn.ishovering():
            # runs if the mouse is down AND it's hovering over the restart button
            if self.rconfirm == False:
                self.rconfirm = True
            else:
                self.restart()
        elif self.settbtn.ishovering():
            # same thing but for the settings button ^^^
            self.screen.fill((232, 232, 232))
            # TODO: do another font because wow I do not like this
            notice: pygame.Surface = self.verycoolfont.render("Refer to settings window", True, pygame.Color("black"))
            rect = notice.get_rect()
            rect.center = ((self.w/2), (self.h/2))

            self.screen.blit(notice, rect)
            pygame.display.flip()
    
            tkwin.activate()

    def tksubmit(self, code: int):
        """Callback for the tkwin (SettingsWin) object"""
        # code = 1 means the user exited the window via x button
        if code == 1:
            tkwin.done()

        mines = tkwin.minesno()
        height = tkwin.height()
        width = tkwin.width()

        # for more checks and errors, this code's extendable
        checks = [
            mines != self.minesno,
            height != self.height,
            width != self.width
        ]
        if not any(checks):
            tkwin.done()
            return

        errmsg = []

        if mines >= self.field._grid.cellno:
            errmsg.append(f"Too many mines for the field! (max: {int(self.field._grid.cellno-1)})")

        if errmsg:
            finalmsg = "We have a few problems:\n - " + "\n - ".join(errmsg)
            messagebox.showerror("Few problems", finalmsg)
        elif messagebox.askokcancel("Restarting Game...", "We are going to restart the game with the new settings. Proceed?"):
            tkwin.done()
            self.minesno = mines
            self.height = height
            self.width = width
            self.restart()

    # TODO:
    #   For these 2 functions, find a way to edit the buttons to clarify that
    #   if you don't restart now you can restart later. E.g. "Do you wanna
    #   restart now?", buttons: "yes", "not now"

    def lost(self):
        """Player has lost :("""
        self.state = State.lost
        self.draw()
        pygame.display.flip()
        restart = messagebox.askyesno("R.I.P.", "Shame, it's ok though. Do you want to restart *now*?")
        if restart:
            self.restart()

    def won(self):
        """Player has won!!!!!"""
        self.state = State.won
        # TODO: Do something like google (maybe?) if you do that, uncomment the code under
        # self.draw()
        # pygame.display.flip()
        restart = messagebox.askyesno("Literally Me", "Wow, you're a literally god(dess) literally the best wow, congrats!!!!! Do you wanna restart?")
        if restart:
            self.restart()

    def restart(self):
        # it's a new function because better naming
        self.gamesetup()

    def drawmeta(self):
        """Draw meta stuff like the restart and settings button, and the mine counter"""
        # You need to click the restart button twice for it to actually restart [I mean it's intentional]
        if self.rconfirm and self.resbtn.text == "Restart":
            self.resbtn.updateobjs("Restart?", btnhoverclr="#b2ddf7")
        elif (self.rconfirm and not self.resbtn.ishovering()) or (not self.rconfirm and self.resbtn.text == "Restart?"):  # TODO: refactor maybe
            self.resbtn.updateobjs("Restart", btnhoverclr="#4cb5ae")
            self.rconfirm = False

        self.resbtn.render()
        self.settbtn.render()

        # Mine Counter
        # TODO: find better font, this one's blurry
        textimg = segfont.render(str(self.field.flagged), True, (50, 50, 50))
        x = (self.field.minmargin)
        h = (self.field.minmargin/2 - textimg.get_height()/2)
        self.screen.blit(textimg, (x, h))

    def draw(self):
        """The general draw function"""
        self.screen.fill(self.bg_color)  # clear screen
        self.field.draw(self.screen)
        self.drawmeta()
