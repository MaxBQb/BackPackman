from classes.bp_interface import *
from classes.Color_Scheme import *
from random import choice, randrange


class Menu(Room):
    '''
    Здесь нужно реализовать комнату (сцену)
    сюда подключаются кнопки и прочее.
    У кнопок должны быть методы draw и act соответственно.
    '''

    def __init__(self, game):
        super().__init__(game)
        self.game.score = 0
        self.game.counter = 0
        self.pause_enabled = False
        self.next_room = MainField(game, self)
        title = Text(game=self.game, text='BACK_PAC_MAN')
        # START GAME <-> RESUME must keep in 'self'
        self.start_text = Text(self.game, text='START GAME', font_size=20, color=Color.DARK_GREEN, pos=(self.game.size[0] // 2, self.game.size[1] // 3), centrate=(True, True))
        end_text = Text(self.game, text='EXIT GAME', font_size=20, color=Color.DARK_RED, pos=(self.game.size[0] // 2, self.game.size[1] // 3 + 45), centrate=(True, True))
        start_btn = Button(self.game, self.start_text, Color.BLACK, Color.DARK_GREEN,
                           Action(transit, game=self.game, room=self.next_room),
                           Action(self.start_text.update_text, text='RESUME'))
        exit_btn = Button(self.game, end_text, Color.BLACK, Color.DARK_RED, Action(quit))
        self.toDraw += [title, start_btn, exit_btn]
        self.eventListeners += [exit_btn, start_btn]


class MainField(Room):
    def __init__(self, game, prev_room: Room = None):
        super().__init__(game, prev_room)

        # инициализация элементов поля
        self.lbl_score = Text(self.game, text="Score: {}".format(self.game.score), pos=(self.game.size[0] // 2, self.game.size[1] - 30), centrate=(True, False))
        self.paclives = []  # для отрисовки жизней
        self.ghosts = [] # для призраков
        self.draw_lives()
        self.map = [[list() for j in range(28)] for i in range(24)]
        field = [
            "############################",
            "#************##************#",
            "#*####*#####*##*#####*####*#",
            "#+####*#####*##*#####*####+#",
            "#**************************#",
            "#*####*##*########*##*####*#",
            "#******##****##****##******#",
            "######*#####_##_#####*######",
            "_____#*##__________##*#_____",
            "_____#*##_###__###_##*#_____",
            "######*##_#_HIHH_#_##*######",
            ">_____*___#_HCBH_#___*_____<",
            "######*##_#_HHHH_#_##*######",
            "_____#*##_########_##*#_____",
            "_____#*##____$____P##*#_____",
            "######*##_########_##*######",
            "#************##************#",
            "#*####*#####*##*#####*####*#",
            "#+**##****************##**+#",
            "###*##*##*########*##*##*###",
            "#******##****##****##******#",
            "#*##########*##*##########*#",
            "#**************************#",
            "############################",
        ]
        self.parse_field(field)
        self.update_lives()

        # инициализация элементов интерфейса взаимодействия с пользователем
        back_text = Text(self.game, text="Main Menu", pos=(30, self.game.size[1] - 30), color=Color.DARK_GREEN)
        back_btn = Button(self.game, back_text, Color.BLACK, Color.DARK_GREEN,
                          Action(transit, game=self.game, room=prev_room))
        self.toDraw += [back_btn, self.lbl_score]
        self.eventListeners += [back_btn]

    def update_lives(self):
        self.toDraw.append(self.paclives)

    def parse_field(self, field: list):
        """
        _ = можно ходить
        + или * = зерно
        @ = энерджайзер
        I = Inky
        P = Pinky
        B = Blinky
        C = Clyde
        $ = Packman Spawner
        < или > = Teleport (стрелка - направление переноса)
        # = стена
        """
        teleports = {}
        for l, line in enumerate(field):
            for c, char in enumerate(line):
                if char == '#':
                    fs = Wall(self.game, c * 30, l * 30)
                    self.map[l][c] += [fs, True]
                    self.toDraw.append(fs)
                else:
                    self.map[l][c].append(None)
                if char == '$':
                    spwn = Spawner(self.game, (c * 30 + 15, l * 30 + 15), Pacman(self.game))
                    self.map[l][c].append(spwn)
                    self.eventListeners.append(spwn)
                elif char in '<>':
                    tp = Teleport(self.game, c * 30 + 15, l * 30 + 15)
                    self.map[l][c].append(tp)
                    if l in teleports:
                        teleports[l] += [tp]
                    else:
                        teleports[l] = [tp]
                elif char in '*+':
                    if char == '*':
                        seed = Seed(self.game, c * 30 + 15, l * 30 + 15, 1, 4)
                    else:
                        seed = Seed(self.game, c * 30 + 15, l * 30 + 15, 10, 8)
                    self.map[l][c].append(seed)
                    self.toDraw.append(seed)
                elif char == 'P':
                    spwn = Spawner(self.game, (c * 30 + 15, l * 30 + 15), Ghost(self.game))
                    spwn.creature.image = spwn.creature.pinky
                    self.map[l][c].append(spwn)
                    self.eventListeners.append(spwn)
                    self.ghosts.append(spwn)
                elif char == 'I':
                    spwn = Spawner(self.game, (c * 30 + 15, l * 30 + 15), Ghost(self.game))
                    spwn.creature.image = spwn.creature.inky
                    self.map[l][c].append(spwn)
                    self.eventListeners.append(spwn)
                    self.ghosts.append(spwn)
                elif char == 'B':
                    spwn = Spawner(self.game, (c * 30 + 15, l * 30 + 15), Ghost(self.game))
                    spwn.creature.image = spwn.creature.blinky
                    self.map[l][c].append(spwn)
                    self.eventListeners.append(spwn)
                    self.ghosts.append(spwn)
                elif char == 'C':
                    spwn = Spawner(self.game, (c * 30 + 15, l * 30 + 15), Ghost(self.game))
                    spwn.creature.image = spwn.creature.clyde
                    self.map[l][c].append(spwn)
                    self.eventListeners.append(spwn)
                    self.ghosts.append(spwn)
        for t in teleports.values():
            if len(t) == 2:
                t[0].connect(t[1])
        for line in self.map:
            for lis in line:
                for e in lis:
                    if isinstance(e, Wall):
                        e.reconnect(self.map)

    def change_score(self, x):
        self.game.score += x
        self.update_score()

    def update_score(self):
        self.lbl_score.update_text("Score: {}".format(self.game.score))

    def draw_lives(self):
        image = pygame.image.load("images/pacman_small.png")
        shift = 35
        for i in range(3):
            life = Drawable(self.game, self.game.size[0] - shift, self.game.size[1] - 10, (15, 15))
            life.image = image
            shift += 35
            self.paclives.append(life)

    def remove_life(self):
        if len(self.paclives):
            self.paclives.pop()


class DeathMessage(Room):
    '''
    Конец игры,
    подведение итогов
    '''

    def __init__(self, game):
        super().__init__(game)
        self.pause_enabled = False
        title = Text(game=self.game, text='GAME OVER', font_size=36, color=Color.GREEN, pos=(self.game.size[0] // 2, self.game.size[1] // 5), centrate=(True, False))
        record_text = Text(game=self.game, text='Your score is {}'.format(self.game.score), pos=(self.game.size[0] // 2, self.game.size[1] / 2), centrate=(True, True))
        start_text = Text(self.game, text='MAIN MENU', color=Color.DARK_GREEN, pos=(self.game.size[0] // 2, self.game.size[1] - self.game.size[1] // 3), centrate=(True, True))
        replay_text = Text(self.game, text='PLAY AGAIN', color=Color.ORANGE, pos=(self.game.size[0] // 2, self.game.size[1] - self.game.size[1] // 3 + 45), centrate=(True, True))
        end_text = Text(self.game, text='EXIT GAME', color=Color.DARK_RED, pos=(self.game.size[0] // 2, self.game.size[1] - self.game.size[1] // 3 + 90), centrate=(True, True))
        menu = Menu(self.game)
        menu_btn = Button(self.game, start_text, Color.BLACK, Color.DARK_GREEN,\
                          Action(transit, game=self.game, room=menu))
        replay_btn = Button(self.game, replay_text, Color.BLACK, Color.ORANGE,\
                            Action(transit, game=self.game, room=menu.next_room),
                            Action(menu.start_text.update_text, text='RESUME'))
        exit_btn = Button(self.game, end_text, Color.BLACK, Color.DARK_RED,\
                          Action(quit))

        self.toDraw += [title, menu_btn, exit_btn, record_text, replay_text, replay_btn]
        self.eventListeners += [exit_btn, menu_btn, replay_btn]


class Pacman(Creature):
    image = pygame.image.load("images/pacman.png")

    def __init__(self, game: Game, x: int = 0, y: int = 0):
        super().__init__(game, x, y, (15, 15))
        self.move_cache = []
        self.speed = 1
        self.steps_alive = 0
        self.look_forward = True
        self.look_vertical = False

    def act(self, e: pygame.event):
        if e.type == pygame.KEYDOWN:
            if e.key in (119, 97, 115, 100) and (self.move_cache == [] or self.move_cache[-1] != e.key) and len(
                    self.move_cache) < 5:
                self.move_cache.append(e.key)

    def step(self):
        self.steps_alive += 1
        for e in self.may_collide_with(self.x, self.y):
            if isinstance(e, Seed):
                '''
                Если съел энерджайзер, призраки становятся уязвимыми
                '''
                if e.score == 10:
                    for g in self.game.current_room.ghosts:
                        g.creature.vulnerable_mode()
                    e.eat()
                e.eat()

                '''
                Поединок с призраком
                '''
            elif isinstance(e, Spawner) and isinstance(e.creature, Ghost):
                if e.creature.vulnerable:
                    e.creature.die()
                else:
                    self.die()
                    return

            if isinstance(e, Teleport):
                e.apply(self)
        if len(self.move_cache):
            mx_c, my_c = 0, 0
            look_forward = self.look_forward
            look_vertical = self.look_vertical
            if len(self.move_cache) > 1:
                if self.move_cache[0] != 115 and self.move_cache[1] == 119:
                    my_c = -1
                elif self.move_cache[0] != 100 and self.move_cache[1] == 97:
                    mx_c = -1
                elif self.move_cache[0] != 119 and self.move_cache[1] == 115:
                    my_c = 1
                elif self.move_cache[0] != 97 and self.move_cache[1] == 100:
                    mx_c = 1
                if (mx_c or my_c) and self.can_move(self.speed * mx_c, self.speed * my_c):
                    self.move_cache.pop(0)
            mx_c, my_c = 0, 0
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

    def die(self):
        self.game.current_room.remove_life()
        self.game.current_room.toDraw.remove(self)
        self.game.current_room.eventListeners.remove(self)
        if len(self.game.current_room.paclives):
            self.spawner.spawn(120)
        else:
            transit(self.game, DeathMessage(self.game))
        super().die()

    def draw(self):
        im = self.image
        self.image = pygame.transform.flip(
            self.image,
            self.look_forward if self.look_vertical else
            not self.look_forward, False)
        self.image = pygame.transform.rotate(self.image, -90 if self.look_vertical else 0)
        Drawable.draw(self)
        self.image = im


class Ghost(Creature):
    pinky = pygame.image.load("images/pink.png")
    inky = pygame.image.load("images/blue.png")
    blinky = pygame.image.load("images/red.png")
    clyde = pygame.image.load("images/yellow.png")
    vuln = pygame.image.load("images/vuln.png")
    dead = pygame.image.load("images/eyes.png")

    def __init__(self, game: Game, x: int = 0, y: int = 0):
        super().__init__(game, x, y, (15, 15))
        self.vulnerable = False

    def step(self):
        pass

    def vulnerable_mode(self):
        image_cache = self.image
        self.vulnerable = True
        self.game.current_room.toDraw.remove(self)
        self.image = self.vuln
        self.game.current_room.toDraw.append(self)

    def die(self):
        image_cache = self.image
        self.game.current_room.toDraw.remove(self)
        self.image = self.dead
        self.game.current_room.toDraw.append(self)


class Seed(Creature):
    def __init__(self, game: Game, x: int = 0, y: int = 0, score: int = 0, radius: int = 3):
        super().__init__(game, x, y, (radius, radius))
        self.radius, self.score = radius, score
        from random import randint
        self.g = randint(10, 100)
        sc = randint(15, 40)
        delta = randint(1, 2) + randint(0, 1) * randint(0, 1) * randint(0, 1) * randint(0, 1) * randint(0, 1) * randint(
            0, 1) * randint(0, 1)
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
        super().die()

    def draw(self):
        r = int(self.rad_frames[(self.game.counter + self.g) % len(self.rad_frames)])
        pygame.draw.circle(self.game.screen, Color.GREEN, (self.x, self.y), r)


class Teleport(Interactable):
    def __init__(self, game: Game, x, y):
        super().__init__(game)
        self.x, self.y = x, y
        self.cooldown = 40
        self.last_active = 0
        self.out = None

    def connect(self, other) -> bool:
        self.out = other
        other.out = self

    def apply(self, entity: Creature):
        if self.out and self.game.counter - self.last_active > self.cooldown:
            entity.set_pos(self.out.x, self.out.y)
            self.last_active = self.out.last_active = self.game.counter
