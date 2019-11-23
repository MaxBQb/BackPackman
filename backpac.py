'''
BackPackMan v0.0.1 initial
'''

import pygame, sys
from bp_basics import *
from bp_interface import *


class Menu(Room):
    '''
    Здесь нужно реализовать комнату (сцену)
    сюда подключаются кнопки и прочее.
    У конопок должны быть методы draw и act соответственно.
    '''

    def __init__(self, game):
        super().__init__(game)
        self.game = game

    def draw(self):
        title = Text(game=self.game, text='BACK_PAC_MAN')

        start_text = Text(self.game, text='START GAME')
        start_text_w = start_text.get_size()[0]
        start_text_h = start_text.get_size()[1]
        start_text.update_position(x=self.game.size[0] / 2 - start_text_w / 2, y=self.game.size[1] / 3)

        end_text = Text(self.game, text='EXIT GAME')
        end_text_w = end_text.get_size()[0]
        end_text.update_position(x=self.game.size[0] / 2 - end_text_w / 2, y=self.game.size[1] / 3 + start_text_h + 10)

        start_btn = Button(self.game, start_text, Color.GREEN, Color.DARK_GREEN, Action(transit, game=self.game, room=MainField(self.game)))
        exit_btn = Button(self.game, end_text, Color.RED, Color.DARK_RED, Action(quit))

        self.toDraw.append(title)
        self.toDraw.append(start_btn)
        self.toDraw.append(exit_btn)
        self.eventListeners.append(start_btn)
        self.eventListeners.append(exit_btn)

        super().draw()
        self.game.clock.tick(15)


class MainField(Room):
    def __init__(self, game):
        super().__init__(game)

    def draw(self):
        text = Text(self.game, text="This is a main field", x=100, y=100)

        back_text = Text(self.game, text="MAIN MENU", x=self.game.size[0] // 2, y=self.game.size[1] // 2)

        back_btn = Button(self.game, back_text, Color.GREEN, Color.DARK_GREEN, Action(transit, game=self.game, room=Menu(self.game)))

        self.toDraw.append(text)
        self.toDraw.append(back_text)
        self.toDraw.append(back_btn)

        super().draw()

    def step(self):
        pass


class Pacman(Creature):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(game, x, y, (64, 64))
        self.move_cache = []
        self.speed = 4

    def act(self, e: pygame.event):
        if e.type == pygame.KEYDOWN:
            if e.key in (119, 97, 115, 100) and (not len(self.move_cache) or self.move_cache[-1] != e.key) and len(
                    self.move_cache) < 5:
                self.move_cache.append(e.key)

    def step(self):
        if len(self.move_cache):
            mx_c, my_c = 0, 0
            if self.move_cache[0] == 119:
                my_c = -1
            elif self.move_cache[0] == 97:
                mx_c = -1
            elif self.move_cache[0] == 115:
                my_c = 1
            elif self.move_cache[0] == 100:
                mx_c = 1
            if not self.move(self.speed * mx_c, self.speed * my_c):
                self.move_cache.pop(0)
                self.step()


if __name__ == '__main__':
    g = Game(600, 600)
    g.start(Menu(g))
