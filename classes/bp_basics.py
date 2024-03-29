from collections import deque

import pygame
from sys import exit
from classes.Color_Scheme import *

'''
Events scheme
Firstly:
    1) Room creation event (once)
    2) Generate room cached (static) background (once)
    3) Already exist in room objects creation event (once)

Loop:
    1) User interaction event for each in eventListeners (catches by act())
    2) Step event for each in eventListeners (catches by step())
    3) Draw event for each in toDraw (catches by draw())

Possible events:
    1) Creation (by Spawner or script)
    2) Collision for Creature every step (catches by collide())
    3) Death (catches by die())
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
        self.records = Records("high_scores.txt")
        self.records.read()
        self.pause_screen = pygame.Surface(self.size, pygame.SRCALPHA)
        self.pause_screen.fill((0, 0, 0, 160))
        pygame.draw.circle(self.pause_screen, (*Color.DARK_RED, 200), (w//2, h//2), 75)
        pygame.draw.rect(self.pause_screen, Color.LIGHT_BLUE, (w//2-30, h//2-45, 20, 90))
        pygame.draw.rect(self.pause_screen, Color.LIGHT_BLUE, (w//2+10, h//2-45, 20, 90))

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.GameOver = True
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_ESCAPE and\
                        self.current_room.prev_room:
                    transit(self, self.current_room.prev_room)
                elif e.key == pygame.K_RETURN and\
                        self.current_room.next_room:
                    transit(self, self.current_room.next_room)
                elif e.key in [pygame.K_SPACE, pygame.K_p] and \
                        self.current_room.pause_enabled:
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
                self.screen.blit(self.current_room.static_back, (0, 0))
                self.current_room.draw()
                pygame.display.flip()
                self.counter += 1
                pygame.time.delay(8)
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
        self.created = False
        self.static_back = pygame.Surface(game.size, pygame.SRCALPHA)
        self.pause_enabled = pause_enabled
        self.static_back.fill(background)
        # Сюда классы наследники добавляют объекты для отрисовки
        self.toDraw = []
        # Сюда объекты для отрисовки в фон
        self.toDrawStatic = []
        # Cюда для взаимодействия
        self.eventListeners = []

    def interact(self, event: pygame.event):
        for obj in self.eventListeners:
            obj.interact(event)

    def creation(self):
        if self.created:
            return
        self.created = True
        all_o = self.eventListeners+self.toDraw+self.toDrawStatic
        unic_o = []
        for e in all_o:
            if not e in unic_o:
                unic_o.append(e)
        for o in unic_o:
            if not isinstance(o, list):
                o.creation()
        for e in self.toDrawStatic:
            e.draw(self.static_back)

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
    game.preload_room = room


class Drawable(BasicObject):
    image = pygame.image.load("images/null.png")

    def __init__(self, game: Game, x: int = 0, y: int = 0, offset: (int, int) = (0, 0)):
        super().__init__(game)
        self.x, self.y = x, y
        self.offset = offset

    def draw(self, surf=None):
        if not surf:
            surf = self.game.screen
        surf.blit(self.image, (self.x - self.offset[0], self.y - self.offset[1]))


class Creature(Drawable):
    dynamic_coll_check = []

    def __init__(self, game: Game, x: int = 0, y: int = 0, offset: (int, int) = (0, 0)):
        super().__init__(game, x, y, offset)
        self.spawner = None
        self.is_alive = True

    def get_pos(self):
        return self.x, self.y

    def dynamic_collision_test(self, x: int, y: int, others: list) -> list:
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
                    c.collide([self])
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
        self.save()


class Node:
    def __init__(self, pos):
        self.pos = pos
        self.x, self.y = pos
        self.neighbors = []
        self.reserv = []

    def occupy(self):
        self.reserv = self.neighbors[::]
        for e in self.reserv:
            self.disconnect(e)

    def unoccupy(self):
        for e in self.reserv:
            self.connect(e)
        self.reserv = []

    def connect(self, other):
        self.neighbors.append(other)
        other.neighbors.append(self)

    def disconnect(self, other):
        self.neighbors.remove(other)
        other.neighbors.remove(self)


class Path(BasicObject):
    def __init__(self, game: Game, maze):
        super().__init__(game)
        self.graph = [[Node((j * 30 + 15, i * 30 + 15))
                      for j in range(len(maze[i]))]
                      for i in range(len(maze))]
        graph = self.graph
        for i in range(len(maze) - 1):
            for j in range(len(maze[i]) - 1):
                if not True in [*maze[i][j], *maze[i + 1][j]]:
                    graph[i][j].connect(graph[i + 1][j])
                if not True in [*maze[i][j], *maze[i][j + 1]]:
                    graph[i][j].connect(graph[i][j + 1])
        self.occupied = []

    def occupy(self, node: Node):
        self.occupied.append(node)
        node.occupy()

    def occupy_pos(self, x: int, y:int):
        x //= 30
        y //= 30
        self.occupy(self.graph[y][x])

    def step(self):
        if not self.occupied:
            return
        for e in self.occupied:
            e.unoccupy()
        self.occupied = []

    def find(self, start, goal):
        graph = self.graph
        start = graph[start[1]//30][start[0]//30]
        goal = graph[goal[1]//30][goal[0]//30]
        if start == goal:
            return [start]
        visited = {start}
        queue = deque([(start, [])])

        while queue:
            current, path = queue.popleft()
            visited.add(current)
            for neighbor in current.neighbors:
                if neighbor == goal:
                    return path + [current, neighbor]
                if neighbor in visited:
                    continue
                queue.append((neighbor, path + [current]))
                visited.add(neighbor)
        return []
