from classes.bp_interface import *
from classes.Color_Scheme import *
from random import choice, randrange


class Menu(Room):
    '''
    Здесь нужно реализовать комнату (сцену)
    сюда подключаются кнопки и прочее.
    У конопок должны быть методы draw и act соответственно.
    '''

    def __init__(self, game):
        super().__init__(game)
        self.next_room = MainField(game, self)
        title = Text(game=self.game, text='BACK_PAC_MAN')
        start_text = Text(self.game, text='START GAME')
        start_text_w, start_text_h = start_text.get_size()
        start_text.update_position(x=self.game.size[0] / 2 - start_text_w / 2, y=self.game.size[1] / 3)
        end_text = Text(self.game, text='EXIT GAME')
        end_text_w = end_text.get_size()[0]
        end_text.update_position(x=self.game.size[0] / 2 - end_text_w / 2, y=self.game.size[1] / 3 + start_text_h + 10)

        start_btn = Button(self.game, start_text, Color.GREEN, Color.DARK_GREEN,
                           Action(transit, game=self.game, room=self.next_room))
        exit_btn = Button(self.game, end_text, Color.RED, Color.DARK_RED, Action(quit))
        self.toDraw += [title, start_btn, exit_btn]
        self.eventListeners += [exit_btn, start_btn]


class MainField(Room):
    def __init__(self, game, prev_room: Room = None):
        super().__init__(game, prev_room)
        self.lbl_score = Text(self.game, text="Score: {}".format(self.game.score), x=self.game.size[0] // 2 - 30, y=self.game.size[1] - 30)
        back_text = Text(self.game, text="MAIN MENU", x=30, y=self.game.size[1] - 30)
        back_btn = Button(self.game, back_text, Color.GREEN, Color.DARK_GREEN, Action(transit, game=self.game, room=prev_room))
        self.toDraw += [back_text, back_btn, self.lbl_score]
        game.background = Color.BLUE
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
            "######*##_#_HIPH_#_##*######",
            ">_____*___#_HCBH_#___*_____<",
            "######*##_#_HHHH_#_##*######",
            "_____#*##_########_##*#_____",
            "_____#*##____$_____##*#_____",
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

    def parse_field(self, field: list):
        '''
        _ = можно ходить
        + или * = зерно
        @ = энерджайзер
        I = Inky
        P = Pinky
        B = Blinky
        C = Clyde
        $ = Packman Spawner
        < или > = Teleport (стрелка - направление переноса)
        # = стена (подразумевается)
        '''
        teleports = {}
        for l, line in enumerate(field):
            for c, char in enumerate(line):
                if char in ' _+IPBCHP<>$@*':
                    fs = FreeSpace(self.game, c * 30, l * 30)
                    self.map[l][c].append(fs)
                    self.toDraw.append(fs)
                else:
                    self.map[l][c].append(None)
                if char == '$':
                    spwn = Spawner(self.game, Pacman(self.game, c * 30 + 15, l * 30 + 15))
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
                        seed = Seed(self.game, c * 30 + 15, l * 30 + 15, 1, 3)
                    else:
                        seed = Seed(self.game, c * 30 + 15, l * 30 + 15, 10, 6)
                    self.map[l][c].append(seed)
                    self.toDraw.append(seed)
        for t in teleports.values():
            if len(t) == 2:
                t[0].connect(t[1])

    def change_score(self, x):
        self.game.score += x
        self.update_score()

    def update_score(self):
        self.lbl_score.update_text("Score: {}".format(self.game.score))


class Pacman(Creature):
    image = pygame.image.load("images/pacman.png")

    def __init__(self, game: Game, x: int, y: int):
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
                e.eat()
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

    def draw(self):
        im = self.image
        self.image = pygame.transform.flip(self.image,
                                           self.look_forward if self.look_vertical else not self.look_forward, False)
        self.image = pygame.transform.rotate(self.image, -90 if self.look_vertical else 0)
        Drawable.draw(self)
        self.image = im


class Seed(Creature):
    def __init__(self, game: Game, x: int = 0, y: int = 0, score: int = 0, radius: int = 3):
        super().__init__(game, x, y, (radius, radius))
        self.radius, self.score = radius, score

    def eat(self):
        if self.radius >= 1:
            self.radius -= 1
        elif self.is_alive:
            self.die()

    def die(self):
        self.game.current_room.toDraw.remove(self)
        self.game.current_room.change_score(self.score)
        super().die()

    def draw(self):
        pygame.draw.circle(self.game.screen, Color.GREEN, (self.x, self.y), self.radius)


class FreeSpace(Drawable):
    '''
    Только отображение коридоров
    '''

    def draw(self):
        pygame.draw.rect(self.game.screen, Color.BLACK, (self.x, self.y, 30, 30))
        if None in self.game.current_room.map[self.y//30-1][self.x//30]:
            pygame.draw.line(self.game.screen, Color.ORANGE, (self.x, self.y), (self.x+30, self.y), 4)
        if None in self.game.current_room.map[self.y//30][self.x//30-1]:
            pygame.draw.line(self.game.screen, Color.ORANGE, (self.x, self.y), (self.x, self.y+30), 4)
        if self.y//30 < 23 and None in self.game.current_room.map[self.y//30+1][self.x//30]:
            pygame.draw.line(self.game.screen, Color.ORANGE, (self.x, self.y+30), (self.x+30, self.y+30), 4)
        if self.y//30 < 23 and self.x//30 < 27 and None in self.game.current_room.map[self.y//30][self.x//30+1]:
            pygame.draw.line(self.game.screen, Color.ORANGE, (self.x+30, self.y), (self.x+30, self.y+30), 4)


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
