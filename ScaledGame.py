import pygame
import os
from pygame.locals import *

class ScaledGame(pygame.Surface):
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center window position
    title = None
    FPS = None
    clock = None
    game_gap = None
    game_size = None
    game_scaled = None
    screen_info = None
    screen = None
    resize = True
    set_zoom = False
    set_fullscreen = False
    factor_w = 1
    factor_h = 1

    def __init__(self, title, game_size, FPS, first_screen=False):
        # Title
        self.title = title
        pygame.display.set_caption(self.title)

        # Game Settings
        self.FPS = FPS
        self.clock = pygame.time.Clock()

        # Window Settings
        self.game_gap = (0, 0)
        self.game_size = game_size

        # Required to set a good resolution for the game screen
        self.screen_info = pygame.display.Info()

        if not first_screen:
            self.screen = pygame.display.set_mode(game_size, RESIZABLE)
        else:
            # Take 120 pixels from the height because of the menu bar, window bar and dock takes space
            self.screen = pygame.display.set_mode((self.screen_info.current_w, self.screen_info.current_h - 120), RESIZABLE)

        # Sets up the Surface for the game.
        pygame.Surface.__init__(self, self.game_size)

    def get_resolution(self, ss, gs):
        gap = float(gs[0]) / float(gs[1])  # Game aspect ratio
        sap = float(ss[0]) / float(ss[1])  # Scaled aspect ratio
        if gap > sap:
            # Divides the height by the factor which the width changes so the aspect ratio remains the same.
            factor = float(gs[0]) / float(ss[0])
            new_h = gs[1] / factor
            game_scaled = (ss[0], new_h)
        elif gap < sap:
            # Divides the width by the factor which the height changes so the aspect ratio remains the same.
            factor = float(gs[1]) / float(ss[1])
            new_w = gs[0] / factor
            game_scaled = (new_w, ss[1])
        else:
            game_scaled = self.screen.get_size()
        game_scaled = int(game_scaled[0]), int(game_scaled[1])
        return game_scaled

    def fullscreen(self):
        if not self.set_fullscreen:
            self.game_gap = 0, 0
            self.game_scaled = self.game_size
            self.set_zoom = False
            self.screen = pygame.display.set_mode(self.game_size, FULLSCREEN)
            self.factor_w = 1
            self.factor_h = 1
            self.set_fullscreen = True
        else:
            self.resize = True
            self.set_fullscreen = False

    def update(self, events):
        # Display FPS in window title
        pygame.display.set_caption(self.title + " (" + str(int(self.clock.get_fps())) + "FPS)")

        # Updates screen properly
        ss = [self.screen.get_width(), self.screen.get_height()]
        for event in events:
            if event.type == VIDEORESIZE:
                ss = [event.w, event.h]
                self.resize = not (self.set_zoom and (ss[0] == self.screen_info.current_w or ss[0] == self.game_scaled[0]))

        # Fullscreen
        if self.set_fullscreen:
            self.screen.blit(self, self.game_gap)

        # Resize
        elif self.resize:
            self.game_scaled = self.get_resolution(ss, self.game_size)

            # Zoom
            if ss[0] + self.game_gap[0] == self.screen_info.current_w:
                self.game_gap = int((self.screen_info.current_w - self.game_scaled[0]) / 2), self.game_gap[1]
                self.set_zoom = True
            elif self.set_zoom:
                self.game_gap = 0, 0
                self.game_scaled = self.game_size
                self.set_zoom = False

            # Scale game to screen resolution, keeping aspect ratio
            screen_w = self.game_scaled[0] + self.game_gap[0] * 2
            screen_h = self.game_scaled[1] + self.game_gap[1] * 2
            self.screen = pygame.display.set_mode((screen_w, screen_h), RESIZABLE)
            self.resize = False

            # Variables that can be used to resize the position on the aspect ratio
            self.factor_w = self.game_scaled[0] / self.get_width()
            self.factor_h = self.game_scaled[1] / self.get_height()

    def draw(self):
        # Add game to screen with the scaled size and gap required.
        self.screen.blit(pygame.transform.scale(self, self.game_scaled), self.game_gap)
        pygame.display.flip()
