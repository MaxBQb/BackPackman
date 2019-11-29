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
        title = Text(game=self.game, text='BACK_PAC_MAN')
        start_text = Text(self.game, text='START GAME')
        start_text_w, start_text_h = start_text.get_size()
        start_text.update_position(x=self.game.size[0] / 2 - start_text_w / 2, y=self.game.size[1] / 3)

        end_text = Text(self.game, text='EXIT GAME')
        end_text_w = end_text.get_size()[0]
        end_text.update_position(x=self.game.size[0] / 2 - end_text_w / 2, y=self.game.size[1] / 3 + start_text_h + 10)

        start_btn = Button(self.game, start_text, Color.GREEN, Color.DARK_GREEN,
                           Action(transit, game=self.game, room=MainField(self.game)))
        exit_btn = Button(self.game, end_text, Color.RED, Color.DARK_RED, Action(quit))

        self.toDraw += [title, start_btn, exit_btn]
        self.eventListeners += [exit_btn, start_btn]


class MainField(Room):
    def __init__(self, game):
        super().__init__(game)
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
            "______*___#_HCBH_#___*______",
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
            "############################"
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
        T или < или > = Teleport
        # = стена (подразумевается)
        '''
        for l, line in enumerate(field):
            for c, char in enumerate(line):
                if char in ' _+IPBCHP$@*':
                    fs = FreeSpace(self.game, c * 30, l * 30)
                    self.map[l][c].append(fs)
                    self.toDraw.append(fs)
                else:
                    self.map[l][c].append(None)
                if char is '$':
                    spwn = Spawner(self.game, Pacman(self.game, c * 30 + 15, l * 30 + 15))
                    self.map[l][c].append(spwn)
                    self.eventListeners.append(spwn)
                if char in '*+':
                    if char == '*':
                        seed = Seed(self.game, c * 30 + 15, l * 30 + 15, 1, 3)
                    else:
                        seed = Seed(self.game, c * 30 + 15, l * 30 + 15, 10, 6)
                    self.map[l][c].append(seed)
                    self.toDraw.append(seed)

    def update_score(self):
        score_text = Text(self.game, text="Score: {}".format(self.game.score), x=self.game.size[0] // 2 - 30, y=self.game.size[1] - 30)
        self.toDraw.append(score_text)

    def draw(self):
        back_text = Text(self.game, text="MAIN MENU", x=30, y=self.game.size[1] - 30)
        back_btn = Button(self.game, back_text, Color.GREEN, Color.DARK_GREEN,
                          Action(transit, game=self.game, room=Menu(self.game)))
        self.toDraw += [back_text, back_btn]
        self.update_score()
        super().draw()


class Pacman(Creature):
    image = pygame.image.load("images/pacman.png")

    def __init__(self, game: Game, x: int, y: int):
        super().__init__(game, x, y, (15, 15))
        self.move_cache = []
        self.pressed_key = None
        self.speed = 10
        self.score = 0
        self.look_forward = True
        self.look_vertical = False

    def act(self, e: pygame.event):
        if e.type == pygame.KEYDOWN:
            if e.key in (119, 97, 115, 100) and self.pressed_key is None:
                self.pressed_key = e.key
                self.step()
        if e.type == pygame.KEYUP:
            if e.key in (119, 97, 115, 100) and self.pressed_key == e.key:
                self.pressed_key = None

    def step(self):
        for e in self.may_collide_with(self.x, self.y):
            if isinstance(e, Seed):
                self.score += e.score
                e.eat()
        if self.pressed_key is not None:
            mx_c, my_c = 0, 0
            if self.pressed_key == 119:
                my_c = -1
                self.look_forward = self.look_vertical = True
            elif self.pressed_key == 97:
                mx_c = -1
                self.look_forward = self.look_vertical = False
            elif self.pressed_key == 115:
                my_c = 1
                self.look_forward = False
                self.look_vertical = True
            elif self.pressed_key == 100:
                mx_c = 1
                self.look_forward = True
                self.look_vertical = False
            if not self.move(self.speed * mx_c, self.speed * my_c):
                self.pressed_key = None
                self.step()

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
        self.game.score += self.score
        super().die()

    def draw(self):
        pygame.draw.circle(self.game.screen, Color.GREEN, (self.x, self.y), self.radius)


class FreeSpace(Drawable):
    '''
    Только отображение коридоров
    '''

    def draw(self):
        pygame.draw.rect(self.game.screen, Color.BLACK, (self.x, self.y, 30, 30))
