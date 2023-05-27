"""Base game object"""

import os

if os.name == 'nt':
    os.environ['SDL_VIDEODRIVER'] = 'windib'

import pygame
from pygame.locals import RESIZABLE, QUIT

class BasicGame:
    def __init__(self, size=(500, 500), fill=(255, 255, 255)):
        self.screen = pygame.display.set_mode(size, RESIZABLE)
        self.screen.fill(fill)

        self.running = False
        self.clock = pygame.time.Clock() #to track FPS
        self.size = size
        self.fps = 0

    @property
    def w(self):
        return self.size[0]

    @property
    def h(self):
        return self.size[1]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            self.key_poll(event)
            self.meta_event_poll(event)

    def mainloop(self, fps=0):
        self.running = True
        self.fps = fps

        while self.running:
            try:
                pygame.display.set_caption(f"FPS: {round(self.clock.get_fps())}")
                self.update()
                self.clock.tick(self.fps)
            except KeyboardInterrupt:
                self.running = False

        pygame.quit()

    def update(self):
        self.handle_events()
        self.draw()

    def draw(self):
        pass

    def key_poll(self, event: pygame.event.Event):
        pass

    def meta_event_poll(self, event: pygame.event.Event):
        pass
