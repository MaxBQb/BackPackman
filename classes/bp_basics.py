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
    7) Death (catches by die())
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
        self.pause_screen = pygame.Surface(self.size, pygame.SRCALPHA)
        self.pause_screen.fill((0, 0, 0, 200))

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
        quit()

    @staticmethod
    def quit():
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
    def __init__(self, game: Game, x: int = 0, y: int = 0, offset: (int, int) = (0, 0)):
        super().__init__(game, x, y, offset)
        self.spawner = None
        self.is_alive = True

    def get_pos(self):
        return self.x, self.y

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

    def can_set(self, x: int, y: int) -> bool:
        if not self.offset[0] <= x <= self.game.size[0] - self.offset[0]:
            return False
        if not self.offset[1] <= y <= self.game.size[1] - self.offset[1]:
            return False
        if True in self.may_collide_with(x, y):
            return False
        return True

    def set_pos(self, x, y) -> bool:
        if self.can_set(x, y):
            self.x, self.y = x, y
            return True
        return False

    def move(self, x: int, y: int) -> bool:
        return self.set_pos(self.x + x, self.y + y)

    def can_move(self, x: int, y: int) -> bool:
        return self.can_set(self.x + x, self.y + y)

    def creation(self):
        self.is_alive = True

    def die(self):
        self.is_alive = False


class Spawner(BasicObject):
    def __init__(self, game: Game, pos: (int, int), creature: Creature, delay: int = 0):
        super().__init__(game)
        self.delay = delay
        self.pos = pos
        self.spawn_request_time = self.game.counter
        self.can_spawn = True
        creature.spawner = self
        self.creature = creature

    def step(self):
        if self.can_spawn and \
                self.spawn_request_time + self.delay <= self.game.counter:
            self.can_spawn = False
            self.creature.creation()
            self.creature.set_pos(*self.pos)
            self.creature.spawner = self
            self.game.current_room.toDraw.append(self.creature)
            self.game.current_room.eventListeners.append(self.creature)

    def spawn(self, delay: int = 0):
        self.delay = delay
        self.spawn_request_time = self.game.counter
        self.can_spawn = True


class Wall(Drawable):
    line_width = 6
    background = Color.BLACK
    border_color = Color.BLUE
    '''
    Только отображение коридоров
    '''

    def __init__(self, game: Game, x: int = 0, y: int = 0):
        super().__init__(game, x, y)
        self.scr = pygame.Surface((30, 30), pygame.SRCALPHA)

    def reconnect(self, map: None):
        self.scr.fill(self.background)
        up, down, right, left = [True] * 4
        if not map:
            map = self.game.current_room.map
        ''' [ul] [uc] [ur]
            [ml] [<>] [mr]
            [dl] [dc] [dr]
        '''
        # up
        ul = True in map[self.y // 30 - 1][self.x // 30 - 1] if self.y > 0 and self.x > 0 else None
        uc = True in map[self.y // 30 - 1][self.x // 30] if self.y > 0 else None
        ur = True in map[self.y // 30 - 1][self.x // 30 + 1] if self.y > 0 and self.x // 30 < 27 else None
        # middle
        ml = True in map[self.y // 30][self.x // 30 - 1] if self.x > 0 else None
        mr = True in map[self.y // 30][self.x // 30 + 1] if self.x // 30 < 27 else None
        # down
        dl = True in map[self.y // 30 + 1][self.x // 30 - 1] if self.y // 30 < 23 and self.x > 0 else None
        dc = True in map[self.y // 30 + 1][self.x // 30] if self.y // 30 < 23 else None
        dr = True in map[self.y // 30 + 1][self.x // 30 + 1] if self.y // 30 < 23 and self.x // 30 < 27 else None
        v_start = self.line_width - 1
        v_end = 30 - v_start - 2
        h_start = self.line_width - 1
        h_end = 30 - h_start - 2
        if uc != False:
            h_start = 0
        if dc != False:
            h_end = 30 - 1
        if ml != False:
            v_start = 0
        if mr != False:
            v_end = 30 - 1
        '''
        Void: False
        Field end: None
        Wall: True
        '''
        # Borders
        if uc is False:
            pygame.draw.line(self.scr, self.border_color, (v_start, self.line_width // 2 - 1),
                             (v_end, self.line_width // 2 - 1), self.line_width)
        if ml is False:
            pygame.draw.line(self.scr, self.border_color, (self.line_width // 2 - 1, h_start),
                             (self.line_width // 2 - 1, h_end), self.line_width)
        if mr is False:
            pygame.draw.line(self.scr, self.border_color, (30 - self.line_width // 2 - 1, h_start),
                             (30 - self.line_width // 2 - 1, h_end), self.line_width)
        if dc is False:
            pygame.draw.line(self.scr, self.border_color, (v_start, 30 - self.line_width // 2 - 1),
                             (v_end, 30 - self.line_width // 2 - 1), self.line_width)
        # Inner rounds
        if ul is False and uc and ml:
            pygame.draw.circle(self.scr, self.border_color, (0, 0), self.line_width)
        if ur is False and uc and mr:
            pygame.draw.circle(self.scr, self.border_color, (30, 0), self.line_width)
        if dl is False and dc and ml:
            pygame.draw.circle(self.scr, self.border_color, (0, 30), self.line_width)
        if dr is False and dc and mr:
            pygame.draw.circle(self.scr, self.border_color, (30, 30), self.line_width)
        # Outer rounds
        if uc is False and ml is False:
            pygame.draw.circle(self.scr, self.border_color, (self.line_width, self.line_width), self.line_width)
        if uc is False and mr is False:
            pygame.draw.circle(self.scr, self.border_color, (30 - self.line_width, self.line_width), self.line_width)
        if dc is False and ml is False:
            pygame.draw.circle(self.scr, self.border_color, (self.line_width, 30 - self.line_width), self.line_width)
        if dc is False and mr is False:
            pygame.draw.circle(self.scr, self.border_color, (30 - self.line_width, 30 - self.line_width),
                               self.line_width)
        pygame.draw.rect(self.scr, self.background,
                         (self.line_width, self.line_width, 30 - self.line_width * 2, 30 - self.line_width * 2))

    def draw(self):
        self.game.screen.blit(self.scr, (self.x, self.y))
