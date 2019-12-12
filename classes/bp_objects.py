from classes.bp_basics import *
from classes.Color_Scheme import *
from classes import bp_rooms as rooms
from random import randint


class Pacman(Creature):
    images = [pygame.image.load(e) for e in [
        "images/pacman.png",
        "images/pacman_closed1.png",
        "images/pacman_closed2.png",
    ]]
    images += reversed(images)
    image = images[0]

    def __init__(self, game: Game, x: int = 0, y: int = 0):
        super().__init__(game, x, y, (15, 15))
        self.move_cache = []
        self.speed = 0
        self.eating = False
        self.eat_animation_counter = 0
        self.passive = True
        self.look_forward = True
        self.look_vertical = False

    def interact(self, e: pygame.event):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_g:
                for g in self.game.current_room.ghosts:
                    g.die()
            if e.key == pygame.K_v:
                transit(self.game, rooms.Final(self.game, True))
            if e.key in (119, 97, 115, 100) and (self.move_cache == [] or self.move_cache[-1] != e.key) and len(
                    self.move_cache) < 5:
                self.move_cache.append(e.key)

    def step(self):
        # May move
        '''       [mmu]
                   ||
            [mml] <--> [mmr]
                   ||
                  [mmd]
        '''
        self.eating = False
        mmu = self.can_move(0, -self.speed)
        mmd = self.can_move(0, self.speed)
        mml = self.can_move(-self.speed, 0)
        mmr = self.can_move(self.speed, 0)

        if len(self.move_cache):
            self.passive = False
            mx_c, my_c = 0, 0
            look_forward = self.look_forward
            look_vertical = self.look_vertical
            if len(self.move_cache) > 1 and (\
               (self.move_cache[0] != 115 and self.move_cache[1] == 119 and mmu) or\
               (self.move_cache[0] != 119 and self.move_cache[1] == 115 and mmd) or\
               (self.move_cache[0] != 100 and self.move_cache[1] == 97 and mml) or\
               (self.move_cache[0] != 97 and self.move_cache[1] == 100 and mmr)):
                self.move_cache.pop(0)

            if self.move_cache[0] == 119:
                my_c = -1
                look_forward = look_vertical = True
            elif self.move_cache[0] == 97:
                mx_c = -1
                look_forward = look_vertical = False
            elif self.move_cache[0] == 115:
                my_c = 1
                look_forward = False
                look_vertical = True
            elif self.move_cache[0] == 100:
                mx_c = 1
                look_forward = True
                look_vertical = False
            if not self.move(self.speed * mx_c, self.speed * my_c):
                self.move_cache.pop(0)
                self.step()
            else:
                self.look_forward = look_forward
                self.look_vertical = look_vertical
        elif not self.passive:
            self.passive = True
            if mmr and mmd and not mml and not mmu:
                self.look_vertical = not self.look_vertical
            if mml and mmd and not mmr and not mmu:
                self.look_vertical = not self.look_vertical
                self.look_forward = not self.look_forward
            if mmr and mmu and not mml and not mmd:
                self.look_vertical = not self.look_vertical
                self.look_forward = not self.look_forward
            if mml and mmu and not mmr and not mmd:
                self.look_vertical = not self.look_vertical

    def collide(self, others, react: bool = True) -> bool:
        if not super().collide(others):
            return False
        for e in others:
            if isinstance(e, EctoWall):
                return False
            elif isinstance(e, Seed) and react:
                # Если съел энерджайзер, призраки становятся уязвимыми
                e.eat()
                self.eating = True

            elif isinstance(e, Ghost) and react:
                if e.is_alive:
                    if e.vulnerable:
                        e.die()
                        self.game.current_room.combos %= 4
                        self.game.current_room.combos += 1
                        self.game.current_room.change_score(self.game.current_room.combos*100)
                    else:
                        self.die()
            elif isinstance(e, Teleport) and react:
                if e.is_active():
                    e.apply(self)
                    self.move_cache = [self.move_cache[0]] + self.move_cache
                    return False  # Чтоб не возвращал в то же место по окончании
        return True

    def creation(self):
        self.move_cache = []
        self.speed = 2
        self.eating = False
        self.eat_animation_counter = 0
        self.look_forward = True
        self.dynamic_coll_check = self.game.current_room.ghosts
        self.look_vertical = False
        super().creation()

    def die(self):
        if not self.is_alive:
            return
        self.game.current_room.paclives.remove_life()
        self.game.current_room.toDraw.remove(self)
        self.game.current_room.eventListeners.remove(self)
        if len(self.game.current_room.paclives.lives):
            for e in self.game.current_room.ghosts:
                e.die()
                self.game.current_room.toDraw.remove(e)
                self.game.current_room.eventListeners.remove(e)
            self.spawner.spawn(120)
            for e in self.game.current_room.ghosts:
                e.spawner.spawn(120)
        else:
            transit(self.game, rooms.Final(self.game, False))
        super().die()

    def draw(self):
        if self.eating:
            self.image = self.images[self.eat_animation_counter//2 % len(self.images)]
            self.eat_animation_counter += 1
        im = self.image
        self.image = pygame.transform.flip(
            self.image,
            self.look_forward if self.look_vertical else
            not self.look_forward, False)
        self.image = pygame.transform.rotate(self.image, -90 if self.look_vertical else 0)
        Drawable.draw(self)
        self.image = im


class Ghost(Creature):
    vulnerable_steps = 720
    clyde = pygame.image.load("images/yellow.png")
    vuln = pygame.image.load("images/vuln.png")
    dead = pygame.image.load("images/eyes.png")
    eye_dist = 5  # Растояние от глаза до середины
    directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]

    def __init__(self, game: Game, x: int = 0, y: int = 0):
        super().__init__(game, x, y, (15, 15))
        self.vulnerable = False
        self.vulnerable_begin = 0
        self.direction = 0
        self.speed = 1
        self.target_pos = (self.x, self.y)
        self.type_image = self.image # Чтоб не None
        self.avaliable_places = []

    def step(self):
        if self.vulnerable and\
           self.vulnerable_begin+self.vulnerable_steps <= self.game.counter:
            self.image = self.type_image
            self.vulnerable = False
        ''' Directions is counter-clockwise
                 [up 0]
            [left 1] [right 3]
                 [down 2]
        '''
        if not self.x % 15 and not self.y % 15 and not randint(0, 2) or\
            self.x == self.game.current_room.pacman.x or\
            self.y == self.game.current_room.pacman.y:
            if self.x == self.game.current_room.pacman.x:
                tmpd = 0 if self.vulnerable^(self.game.current_room.pacman.y < self.y) else 2
            elif self.y == self.game.current_room.pacman.y:
                tmpd = 1 if self.vulnerable^(self.game.current_room.pacman.x < self.x) else 3
            else:
                tmpd = randint(0, 3)
            # Попытка сменить направление под прямым углом
            if tmpd % 2 == self.direction % 2:
                tmpd = (tmpd+1)%4
            mx_c, my_c = self.directions[tmpd]
            if self.can_move(self.speed * mx_c, self.speed * my_c):
                self.direction = tmpd
        mx_c, my_c = self.directions[self.direction]
        if not self.move(self.speed * mx_c, self.speed * my_c):
            if self.x == self.game.current_room.pacman.x:
                self.direction = 0 if self.vulnerable^(self.game.current_room.pacman.y < self.y) else 2
            elif self.y == self.game.current_room.pacman.y:
                self.direction = 1 if self.vulnerable^(self.game.current_room.pacman.x < self.x) else 3
            else:
                self.direction = randint(0, 3)
            self.step()
        self.target_pos = (self.game.current_room.pacman.x,
                           self.game.current_room.pacman.y)

    def collide(self, others, react: bool = True) -> bool:
        if not super().collide(others):
            return False
        if self.spawner in others and\
           not self.is_alive and\
           not self.spawner.can_spawn:
            self.spawner.spawn()
        return True

    def vulnerable_mode(self):
        if not self.vulnerable:
            self.game.current_room.combos = 0
            self.vulnerable = True
            self.image = self.vuln
        self.vulnerable_begin = self.game.counter

    def creation(self):
        super().creation()
        self.vulnerable = False
        self.speed = 1
        self.dynamic_coll_check = [self.game.current_room.pacman]
        self.target_pos = (self.x, self.y)
        self.image = self.type_image # Чтоб не None
        self.avaliable_places = []
        for i in range(len(self.game.current_room.map)):
            for j in range(len(self.game.current_room.map[i])):
                if None in self.game.current_room.map[i][j]:
                    self.avaliable_places += [(j * 30 + 15, i * 30 + 15)]
        self.direction = randint(0, 3)

    def die(self):
        if self.is_alive:
            self.image = self.dead
            super().die()

    def draw(self):
        if self.is_alive:
            super().draw()
            eyecolor = Color.WHITE
        else:
            eyecolor = Color.LIGHT_BLUE
        eye_xc, eye_yc = 0, 0
        if self.x > self.target_pos[0]:
            eye_xc = -1
        elif self.x < self.target_pos[0]:
            eye_xc = 1
        if self.y > self.target_pos[1]:
            eye_yc = -1
        elif self.y < self.target_pos[1]:
            eye_yc = 1
        pygame.draw.circle(self.game.screen, eyecolor, (self.x-self.eye_dist, self.y), 3)
        pygame.draw.circle(self.game.screen, eyecolor, (self.x+self.eye_dist, self.y), 3)
        pygame.draw.circle(self.game.screen, Color.DARK_RED, (self.x-self.eye_dist+eye_xc, self.y+eye_yc), 1)
        pygame.draw.circle(self.game.screen, Color.DARK_RED, (self.x+self.eye_dist+eye_xc, self.y+eye_yc), 1)


class Seed(Creature):
    def __init__(self, game: Game, x: int = 0, y: int = 0, score: int = 0, radius: int = 3):
        super().__init__(game, x, y, (radius, radius))
        self.radius, self.score = radius, score
        self.g = randint(10, 100)
        sc = randint(15, 40)
        delta = randint(1, 2) + randint(0, 1) * randint(0, 1) * randint(0, 1) * randint(0, 1) * randint(0, 1) * \
                randint(0, 1) * randint(0, 1)
        self.rad_frames = [i // sc for i in range(sc * (radius - delta), sc * (radius + delta))]
        self.rad_frames += reversed(self.rad_frames)

    def eat(self):
        if self.radius >= 1:
            self.radius -= 1
        elif self.is_alive:
            self.die()

    def die(self):
        self.game.current_room.toDraw.remove(self)
        self.game.current_room.change_score(self.score)
        self.game.current_room.map[self.y // 30][self.x // 30].remove(self)
        self.game.current_room.seeds_count -= 1
        if self.game.current_room.seeds_count < 1:
            transit(self.game, rooms.Final(self.game, True))
        super().die()

    def draw(self):
        r = int(self.rad_frames[(self.game.counter + self.g) % len(self.rad_frames)])
        pygame.draw.circle(self.game.screen, Color.GREEN, (self.x, self.y), r)


class Energizer(Seed):
    def die(self):
        for g in self.game.current_room.ghosts:
            g.vulnerable_mode()
        super().die()


class Teleport(BasicObject):
    cooldown = 400

    def __init__(self, game: Game, x, y):
        super().__init__(game)
        self.x, self.y = x, y
        self.last_active = 0
        self.out = None

    def connect(self, other) -> bool:
        self.out = other
        other.out = self

    def is_active(self) -> bool:
        return self.out and self.game.counter - self.last_active > self.cooldown

    def apply(self, entity: Creature):
        self.last_active = self.out.last_active = self.game.counter
        entity.set_pos(self.out.x, self.out.y)


class Spawner(BasicObject):
    def __init__(self, game: Game, pos: (int, int), creature: Creature, delay: int = 0):
        super().__init__(game)
        self.delay = delay
        self.pos = pos
        self.spawn_request_time = 0
        self.can_spawn = True
        creature.spawner = self
        self.creature = creature

    def creation(self):
        self.spawn_request_time = self.game.counter
        self.can_spawn = True

    def step(self):
        if self.can_spawn and \
                self.spawn_request_time + self.delay <= self.game.counter:
            self.can_spawn = False
            self.creature.creation()
            self.creature.set_pos(*self.pos)
            self.creature.spawner = self
            if not self.creature in self.game.current_room.toDraw:
                self.game.current_room.toDraw.append(self.creature)
            if not self.creature in self.game.current_room.eventListeners:
                self.game.current_room.eventListeners.append(self.creature)

    def spawn(self, delay: int = 0):
        self.delay = delay
        self.spawn_request_time = self.game.counter
        self.can_spawn = True


class Wall(Drawable):
    '''Самосоединяющаяся стена'''
    line_width = 6
    background = Color.BLACK
    border_color = Color.BLUE

    def __init__(self, game: Game, x: int = 0, y: int = 0):
        super().__init__(game, x, y)
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)

    def creation(self):
        self.image.fill(self.background)
        up, down, right, left = [True] * 4
        map = self.game.current_room.map
        ''' [ul] [uc] [ur]
            [ml] [<>] [mr]
            [dl] [dc] [dr]
        '''
        cy = self.y // 30
        cx = self.x // 30
        # up
        ul = True in map[cy-1][cx-1] if cy > 0 and cx > 0 else None
        uc = True in map[cy-1][cx] if cy > 0 else None
        ur = True in map[cy-1][cx+1] if cy > 0 and cx < 27 else None
        # middle
        ml = True in map[cy][cx-1] if cx > 0 else None
        mr = True in map[cy][cx+1] if cx < 27 else None
        # down
        dl = True in map[cy+1][cx-1] if cy < 23 and cx > 0 else None
        dc = True in map[cy+1][cx] if cy < 23 else None
        dr = True in map[cy+1][cx+1] if cy < 23 and cx < 27 else None
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
            pygame.draw.line(self.image, self.border_color, (v_start, self.line_width // 2 - 1),
                             (v_end, self.line_width // 2 - 1), self.line_width)
        if ml is False:
            pygame.draw.line(self.image, self.border_color, (self.line_width // 2 - 1, h_start),
                             (self.line_width // 2 - 1, h_end), self.line_width)
        if mr is False:
            pygame.draw.line(self.image, self.border_color, (30 - self.line_width // 2 - 1, h_start),
                             (30 - self.line_width // 2 - 1, h_end), self.line_width)
        if dc is False:
            pygame.draw.line(self.image, self.border_color, (v_start, 30 - self.line_width // 2 - 1),
                             (v_end, 30 - self.line_width // 2 - 1), self.line_width)
        # Inner rounds
        if ul is False and uc and ml:
            pygame.draw.circle(self.image, self.border_color, (0, 0), self.line_width)
        if ur is False and uc and mr:
            pygame.draw.circle(self.image, self.border_color, (30, 0), self.line_width)
        if dl is False and dc and ml:
            pygame.draw.circle(self.image, self.border_color, (0, 30), self.line_width)
        if dr is False and dc and mr:
            pygame.draw.circle(self.image, self.border_color, (30, 30), self.line_width)
        # Outer rounds
        if uc is False and ml is False:
            pygame.draw.circle(self.image, self.border_color, (self.line_width, self.line_width), self.line_width)
        if uc is False and mr is False:
            pygame.draw.circle(self.image, self.border_color, (30 - self.line_width, self.line_width), self.line_width)
        if dc is False and ml is False:
            pygame.draw.circle(self.image, self.border_color, (self.line_width, 30 - self.line_width), self.line_width)
        if dc is False and mr is False:
            pygame.draw.circle(self.image, self.border_color, (30 - self.line_width, 30 - self.line_width),
                               self.line_width)
        pygame.draw.rect(self.image, self.background,
                         (self.line_width, self.line_width, 30 - self.line_width * 2, 30 - self.line_width * 2))


class EctoWall(Drawable):
    '''Стена сквозная для призраков'''
    width = 8

    def __init__(self, game: Game, x: int = 0, y: int = 0):
        super().__init__(game, x, y)
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.line(self.image, Color.LIGHT_BLUE, (0, 15), (30, 15), self.width)


class Paclives(Drawable):
    def __init__(self, game: Game, x: int = 0, y: int = 0, offset: (int, int) = (0, 0)):
        super().__init__(game, x, y, offset)
        self.image = pygame.image.load("images/pacman_small.png")
        self.lives = []
        self.make_lives()

    def make_lives(self):
        shift = 35
        for i in range(3):
            life = Drawable(self.game, self.game.size[0] - shift, self.game.size[1] - 10, (15, 15))
            life.image = self.image
            shift += 35
            self.lives.append(life)

    def draw(self):
        for life in self.lives:
            life.draw()

    def remove_life(self):
        if len(self.lives):
            self.lives.pop()


# Ghosts
class Inky(Ghost):
    image = pygame.image.load("images/blue.png")


class Blinky(Ghost):
    image = pygame.image.load("images/red.png")


class Pinky(Ghost):
    image = pygame.image.load("images/blue.png")


class Clyde(Ghost):
    image = pygame.image.load("images/yellow.png")
