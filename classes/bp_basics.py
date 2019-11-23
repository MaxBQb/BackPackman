import pygame
import sys


class Game:
    def __init__(self, w: int, h: int):
        self.background = (0, 0, 0)
        self.screen = None
        self.size = (w, h)
        self.GameOver = False
        self.Paused = False
        self.current_room = None
        self.clock = pygame.time.Clock()

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.GameOver = True
            if not self.Paused:
                self.current_room.process_event(e)

    def start(self, s_room):
        pygame.init()
        self.current_room = s_room
        self.screen = pygame.display.set_mode(self.size)
        while not self.GameOver:
            self.process_events()
            self.current_room.step()
            self.screen.fill(self.background)
            self.current_room.draw()
            pygame.display.flip()
            pygame.time.wait(60)
        quit()

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit(0)


class Room:
    '''
    Базовый объект комнта (сцена),
    содержит все действующие лица.
    Отвечает за их отрисовку и интерактивность.
    '''

    def __init__(self, game: Game):
        self.game = game
        # Сюда классы наследники добавляют объекты для отрисовки
        self.toDraw = [Level(game)]
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

    def __init__(self, game: Game, x=0, y=0):
        self.x, self.y, self.game = x, y, game

    def draw(self):
        self.game.screen.blit(self.image, (self.x, self.y))


class Interactable:
    def __init__(self, game: Game):
        self.game = game

    def act(self, event: pygame.event):
        pass

    def step(self):
        pass


class Level(Drawable):
    def __init__(self, game):
        super(Level, self).__init__(game)
        self.map = matrix = [[0] * 5 for i in range(5)]
        self.map[0][0] = 1
        self.map[1][1] = 1
        self.map[2][2] = 1

    def draw(self):
        for j in range(len(self.map)):
            for i in range(len(self.map[j])):

                if self.map[i][j] == 1:
                    pygame.draw.rect(self.game.screen, (255, 0, 0), (i * 30 + self.x, j * 30 + self.y, 30, 30))
                if self.map[i][j] == 0:
                    pygame.draw.rect(self.game.screen, (0, 255, 0), (i * 30 + self.x, j * 30 + self.y, 30, 30))


class Creature(Interactable, Drawable):
    def __init__(self, game: Game, x: int, y: int, offset: (int, int) = (0, 0)):
        super(Creature, self).__init__(game)
        self.game = game
        self.x, self.y = x, y
        self.offset = offset
        self.is_alive = True

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, x, y) -> bool:
        # Нужно добавить проверку на возможность перемещения
        if self.game.size[0] - self.offset[0] < x or x < 0 or self.game.size[1] - self.offset[1] < y or y < 0:
            return False
        self.x, self.y = x, y
        return True

    def move(self, x: int, y: int) -> bool:
        return self.set_pos(self.x + x, self.y + y)

    def die(self):
        self.is_alive = False


class FreeSpace(Interactable, Drawable):
    # Пути, по которым Creature ходит
    def __init__(self, game: Game, x: int, y: int):
        super(FreeSpace, self).__init__(game, x, y)
