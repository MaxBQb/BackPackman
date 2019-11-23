import pygame
from sys import exit
from math import ceil
from .Color_Scheme import *


class Game:
    def __init__(self, w: int, h: int):
        pygame.init()
        self.background = Color.BLACK
        self.screen = None
        self.size = (w, h)
        self.GameOver = False
        self.Paused = False
        self.current_room = None
        self.counter = 0

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.GameOver = True
            if e.type == pygame.KEYUP and e.key == pygame.K_SPACE:
                if not self.Paused:
                    self.pause()
                self.Paused = not self.Paused
            if not self.Paused:
                self.current_room.process_event(e)

    def pause(self):
        pass

    def start(self, s_room):
        self.current_room = s_room
        self.screen = pygame.display.set_mode(self.size)
        while not self.GameOver:
            self.process_events()
            if not self.Paused:
                self.current_room.step()
                self.screen.fill(self.background)
                self.current_room.draw()
                pygame.display.flip()
        quit()

    @staticmethod
    def quit():
        pygame.quit()
        exit(0)


class Room:
    '''
    Базовый объект комнта (сцена),
    содержит все действующие лица.
    Отвечает за их отрисовку и интерактивность.
    '''

    def __init__(self, game: Game):
        self.game = game
        # Сюда классы наследники добавляют объекты для отрисовки
        self.toDraw = []
        # А сюда для взаимодействия
        self.eventListeners = []

    def process_event(self, event: pygame.event):
        for obj in self.eventListeners:
            obj.act(event)

    def step(self):
        for obj in self.eventListeners:
            obj.step()

    def draw(self):
        for obj in self.toDraw:
            obj.draw()


class Action:
    def __init__(self, action, **params):
        self.action = action
        self.params = params

    def act(self):
        self.action(**self.params)


def transit(game: Game, room: Room):
    game.current_room = room


class Drawable:
    image = pygame.image.load("images/null.png")

    def __init__(self, game: Game, x: int = 0, y: int = 0, offset: (int, int) = (0, 0)):
        self.x, self.y, self.game, self.offset = x, y, game, offset

    def draw(self):
        self.game.screen.blit(self.image, (self.x - self.offset[0], self.y - self.offset[1]))


class Interactable:
    def __init__(self, game: Game):
        self.game = game

    def act(self, event: pygame.event):
        pass

    def step(self):
        pass


class Creature(Interactable, Drawable):
    def __init__(self, game: Game, x: int = 0, y: int = 0, offset: (int, int) = (0, 0)):
        Drawable.__init__(self, game, x, y, offset)
        Interactable.__init__(self, game)
        self.game = game
        self.x, self.y = x, y
        self.is_alive = True

    def get_pos(self):
        return self.x, self.y

    def may_collide_with(self, x, y):
        return self.game.current_room.map[ceil((y - self.offset[1]) / 30)][ceil((x - self.offset[0]) / 30)] + self.game.current_room.map[(y - self.offset[1]) // 30][(x - self.offset[0]) // 30]

    def set_pos(self, x, y) -> bool:
        # Нужно добавить проверку на возможность перемещения
        if not self.offset[0] <= x <= self.game.size[0] - self.offset[0]:
            return False
        if not self.offset[1] <= y <= self.game.size[1] - self.offset[1]:
            return False
        if None in self.may_collide_with(x, y):
            return False
        self.x, self.y = x, y
        return True

    def move(self, x: int, y: int) -> bool:
        return self.set_pos(self.x + x, self.y + y)

    def die(self):
        self.is_alive = False


class Spawner(Interactable):
    def __init__(self, game: Game, creature: Creature):
        super().__init__(game)
        self.can_spawn = True
        self.creature = creature

    def step(self):
        if self.can_spawn:
            self.can_spawn = False
            self.creature.is_alive = True
            self.game.current_room.toDraw.append(self.creature)
            self.game.current_room.eventListeners.append(self.creature)

    def spawn(self):
        self.can_spawn = True
