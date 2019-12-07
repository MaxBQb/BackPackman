import pygame
from sys import exit
from classes.Color_Scheme import *

'''
Events scheme
Firstly:
    1) Room creation event (once)
    2) Already exist in room objects creation event (once)

Loop:
    3) User interaction event for each in eventListeners (catches by act())
    4) Step event for each in eventListeners (catches by step())
    5) Draw event for each in toDraw (catches by draw())

Possible events:
    6) Creation (by Spawner or script)
    7) Collision for Creature every step (catches by collide())
    8) Death (catches by die())
'''


class Game:
    def __init__(self, w: int, h: int):
        pygame.init()
        self.size = (w, h)
        self.screen = pygame.display.set_mode(self.size)
        self.GameOver = False
        self.Paused = False
        self.preload_room = self.current_room = None
        self.counter = 0
        self.score = 0
        self.records = Records("hight_scores.txt")
        self.records.read()
        self.pause_screen = pygame.Surface(self.size, pygame.SRCALPHA)
        self.pause_screen.fill((0, 0, 0, 160))

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.GameOver = True
            if e.type == pygame.KEYUP and e.key == pygame.K_SPACE \
                    and self.current_room.pause_enabled:
                if not self.Paused:
                    self.pause()
                self.Paused = not self.Paused
            if not self.Paused:
                self.current_room.interact(e)

    def pause(self):
        self.screen.blit(self.pause_screen, (0, 0))
        pygame.display.flip()

    def start(self, s_room):
        self.current_room = s_room
        self.current_room.creation()
        self.preload_room = s_room
        while not self.GameOver:
            self.process_events()
            if not self.Paused:
                # if not self.counter % 3:
                self.current_room.step()
                self.screen.fill(self.current_room.background)
                self.current_room.draw()
                pygame.display.flip()
                self.counter += 1
            if not self.current_room is self.preload_room:
                self.current_room = self.preload_room
                self.current_room.creation()
        self.quit()

    def quit(self):
        self.records.save()
        pygame.quit()
        exit(0)


class BasicObject:
    def __init__(self, game: Game):
        self.game = game

    def creation(self):
        pass

    def interact(self, event: pygame.event):
        pass

    def step(self):
        pass

    def draw(self):
        pass

    def die(self):
        pass


class Room(BasicObject):
    '''
    Базовый объект комнта (сцена),
    содержит все действующие лица.
    Отвечает за их отрисовку и интерактивность.
    '''

    def __init__(self, game: Game, prev_room=None, next_room=None, pause_enabled: bool = True, background=Color.BLACK):
        super().__init__(game)
        self.prev_room = prev_room
        self.next_room = next_room
        self.pause_enabled = pause_enabled
        self.background = background
        # Сюда классы наследники добавляют объекты для отрисовки
        self.toDraw = []
        # Cюда для взаимодействия
        self.eventListeners = []

    def interact(self, event: pygame.event):
        for obj in self.eventListeners:
            obj.interact(event)

    def creation(self):
        all_o = []
        for e in self.eventListeners:
            if not e in all_o:
                all_o.append(e)
        for e in self.toDraw:
            if not e in all_o:
                all_o.append(e)
        for o in all_o:
            if not isinstance(o, list):
                o.creation()

    def step(self):
        for obj in self.eventListeners:
            obj.step()

    def draw(self):
        for obj in self.toDraw:
            # Это условие добавлено для обработки массива жизней пакмана paclives, остальные элементы обрабатываются напрямую
            if isinstance(obj, list):
                for item in obj:
                    item.draw()
            else:
                obj.draw()


class Action:
    def __init__(self, action, **params):
        self.action = action
        self.params = params

    def act(self):
        self.action(**self.params)


def transit(game: Game, room: Room):
    game.preload_room = room


class Drawable(BasicObject):
    image = pygame.image.load("images/null.png")

    def __init__(self, game: Game, x: int = 0, y: int = 0, offset: (int, int) = (0, 0)):
        super().__init__(game)
        self.x, self.y = x, y
        self.offset = offset

    def draw(self):
        self.game.screen.blit(self.image, (self.x - self.offset[0], self.y - self.offset[1]))


class Creature(Drawable):
    dynamic_coll_check = []

    def __init__(self, game: Game, x: int = 0, y: int = 0, offset: (int, int) = (0, 0)):
        super().__init__(game, x, y, offset)
        self.spawner = None
        self.is_alive = True

    def get_pos(self):
        return self.x, self.y

    def dynamic_collision_test(self, x:int, y:int, others: list) -> list:
        return [e for e in others if (x-e.x)**2+(y-e.y)**2 <= 30**2]

    def may_collide_with(self, x: int, y: int) -> list:
        '''
        Получить все вероятно пересекаемые объекты
        :return: Список касаний
        '''
        '''
        ### Расчитываем,
        #o# в которую из сторон смещён,
        ### проверяем столкновения с этой областью.
        '''
        pos_x, pos_y = x // 30, y // 30
        lower_bound_x, upper_bound_x = x % 30 < self.offset[0], x % 30 > self.offset[0],
        lower_bound_y, upper_bound_y = y % 30 < self.offset[1], y % 30 > self.offset[1]
        collisions = self.game.current_room.map[pos_y][pos_x][::]
        if lower_bound_x:
            collisions += self.game.current_room.map[pos_y][pos_x - 1]
        if upper_bound_x:
            collisions += self.game.current_room.map[pos_y][pos_x + 1]
        if lower_bound_y:
            collisions += self.game.current_room.map[pos_y - 1][pos_x]
        if upper_bound_y:
            collisions += self.game.current_room.map[pos_y + 1][pos_x]
        if lower_bound_x and lower_bound_y:
            collisions += self.game.current_room.map[pos_y - 1][pos_x - 1]
        if lower_bound_x and upper_bound_y:
            collisions += self.game.current_room.map[pos_y + 1][pos_x - 1]
        if upper_bound_x and lower_bound_y:
            collisions += self.game.current_room.map[pos_y - 1][pos_x + 1]
        if upper_bound_x and upper_bound_y:
            collisions += self.game.current_room.map[pos_y + 1][pos_x + 1]
        return collisions

    def can_set(self, x: int, y: int, avalanche: bool = False) -> bool:
        if not self.offset[0] <= x <= self.game.size[0] - self.offset[0]:
            return False
        if not self.offset[1] <= y <= self.game.size[1] - self.offset[1]:
            return False
        collisions = self.may_collide_with(x, y) + \
                     self.dynamic_collision_test(x, y, self.dynamic_coll_check)
        if avalanche:
            for c in collisions:
                if isinstance(c, Creature):
                    c.collide(collisions+[self])
        return self.collide(collisions, avalanche)

    def set_pos(self, x, y) -> bool:
        if self.can_set(x, y, True):
            self.x, self.y = x, y
            return True
        return False

    def collide(self, others, react: bool = True) -> bool:
        if True in others:
            return False
        return True

    def move(self, x: int, y: int) -> bool:
        return self.set_pos(self.x + x, self.y + y)

    def can_move(self, x: int, y: int, avalanche: bool = False) -> bool:
        return self.can_set(self.x + x, self.y + y, avalanche)

    def creation(self):
        self.is_alive = True

    def die(self):
        self.is_alive = False


class Records:
    def __init__(self, fname: str):
        self.fname = fname
        self.stats = []

    def read(self) -> list:
        try:
            with open(self.fname, 'r') as f:
                self.stats = [int(e) for e in f.readlines() if e][:10]
        except:
            with open(self.fname, 'w') as f:
                f.writelines([])
            self.stats = []
        return self.stats

    def save(self):
        with open(self.fname, 'w') as f:
            f.writelines('\n'.join([str(e) for e in self.stats[:10] if e]))

    def add(self, score: int):
        self.stats.append(score)
        self.stats = sorted(self.stats, reverse=True)[:10]


class Graph:
    def __init__(self):
        self.neighbors = []

    def connect(self, other, both: bool = True):
        if not isinstance(other, Graph):
            raise TypeError(f"Cannot connect {self.__class__} and {other.__class__}")
        self.neighbors.append(other)
        if both:
            other.neighbors.append(self)


class Path:
    def __init__(self, mmap: list):
        n = len(mmap)
        m = len(mmap[0])
        # Void graph

        self.map = [[Graph() for _ in range(m)] for i in range(n)]
        for i in range(n):
            for j in range(m):
                if None in mmap[i][j]:
                    if i > 0 and None in mmap[i-1][j]:
                        self.map[i][j].connect(self.map[i-1][j])
                    if j > 0 and None in mmap[i][j-1]:
                        self.map[i][j].connect(self.map[i][j-1])
                    if i < n-1 and None in mmap[i+1][j]:
                        self.map[i][j].connect(self.map[i+1][j])
                    if j > m-1 and None in mmap[i][j+1]:
                        self.map[i][j].connect(self.map[i][j+1])