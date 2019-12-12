from classes.bp_interface import *
from classes.Color_Scheme import *
from classes.bp_objects import *


class Menu(Room):
    '''
    Здесь нужно реализовать комнату (сцену)
    сюда подключаются кнопки и прочее.
    У кнопок должны быть методы draw и act соответственно.
    '''

    def __init__(self, game: Game):
        super().__init__(game,
                         next_room=MainField(game, self),
                         pause_enabled=False)
        self.game.score = 0
        self.game.counter = 0
        title = Text(game=self.game, text='BACK_PAC_MAN')
        # START GAME <-> RESUME must keep in 'self'
        self.start_text = Text(self.game, text='START GAME', font_size=20, color=Color.DARK_GREEN,
                               pos=(self.game.size[0] // 2, self.game.size[1] // 3), centrate=(True, True))
        end_text = Text(self.game, text='EXIT GAME', font_size=20, color=Color.DARK_RED,
                        pos=(self.game.size[0] // 2, self.game.size[1] // 3 + 90), centrate=(True, True))
        start_btn = Button(self.game, self.start_text, Color.BLACK, Color.DARK_GREEN,
                           Action(transit, game=self.game, room=self.next_room))
        exit_btn = Button(self.game, end_text, Color.BLACK, Color.DARK_RED, Action(self.game.quit))

        records = Text(self.game, text='Show records', color=Color.YELLOW, font_size = 20,
                       pos=(self.game.size[0] // 2, self.game.size[1] // 3 + 45),
                       centrate=(True, True))
        records_btn = Button(self.game, records, Color.BLACK, Color.YELLOW, \
                             Action(transit, game=self.game, room=GameRecords(game, self)))
        self.toDraw += [title, start_btn, exit_btn, records, records_btn]
        self.eventListeners += [exit_btn, start_btn, records_btn]


class MainField(Room):
    def __init__(self, game, prev_room: Room = None):
        super().__init__(game, prev_room)
        # инициализация элементов поля
        self.lbl_score = Text(self.game, text="Score: {}".format(self.game.score),
                              pos=(self.game.size[0] // 2, self.game.size[1] - 30), centrate=(True, False))
        self.paclives = Paclives(game)
        self.ghosts = []  # для призраков
        self.pacman = None
        self.seeds_count = 0
        self.path = None
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
            "_____#*#####_##_#####*#_____",
            "_____#*###________###*#_____",
            "######*###_##--##_###*######",
            ">_____*____#BIPC#____*_____<",
            "######*###_######_###*######",
            "_____#*###___$____###*#_____",
            "_____#*###_######_###*#_____",
            "######*###_######_###*######",
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

        # инициализация элементов интерфейса взаимодействия с пользователем
        back_text = Text(self.game, text="Main Menu", pos=(30, self.game.size[1] - 30), color=Color.DARK_GREEN)
        back_btn = Button(self.game, back_text, Color.BLACK, Color.DARK_GREEN,
                          Action(transit, game=self.game, room=prev_room))
        self.toDraw += [back_btn, self.lbl_score, self.paclives]
        self.eventListeners += [back_btn]

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
        - = стена, только для пакмана
        """
        teleports = {}

        for l, line in enumerate(field):
            for c, char in enumerate(line):
                if char == '#':
                    fs = Wall(self.game, c * 30, l * 30)
                    self.map[l][c].append(True)
                    self.toDrawStatic.append(fs)
                else:
                    self.map[l][c].append(None)
                if char == '$':
                    spwn = Spawner(self.game, (c * 30 + 15, l * 30 + 15), Pacman(self.game))
                    self.pacman = spwn.creature
                    self.map[l][c].append(spwn)
                    self.eventListeners.append(spwn)
                elif char in '<>':
                    tp = Teleport(self.game, c * 30 + 15, l * 30 + 15)
                    self.map[l][c].append(tp)
                    if l in teleports:
                        teleports[l].append(tp)
                    else:
                        teleports[l] = [tp]
                elif char in '*+':
                    self.seeds_count += 1
                    if char == '*':
                        seed = Seed(self.game, c * 30 + 15, l * 30 + 15, 1, 4)
                    else:
                        seed = Energizer(self.game, c * 30 + 15, l * 30 + 15, 10, 8)
                    self.map[l][c].append(seed)
                    self.toDraw.append(seed)
                elif char in 'BIPC':
                    g = Ghost(self.game)
                    if char == 'B':
                        g.image = Ghost.blinky
                    elif char == 'I':
                        g.image = Ghost.inky
                    elif char == 'P':
                        g.image = Ghost.pinky
                    elif char == 'C':
                        g.image = Ghost.clyde
                    spwn = Spawner(self.game, (c * 30 + 15, l * 30 + 15), g)
                    self.map[l][c].append(spwn)
                    self.eventListeners.append(spwn)
                    self.ghosts.append(g)
                elif char == '-':
                    fs = EctoWall(self.game, c * 30, l * 30)
                    self.map[l][c].append(fs)
                    self.toDrawStatic.append(fs)

        for t in teleports.values():
            if len(t) == 2:
                t[0].connect(t[1])

    def change_score(self, x):
        self.game.score += x
        self.update_score()

    def update_score(self):
        self.lbl_score.update_text("Score: {}".format(self.game.score))

    def creation(self):
        self.game.score = 0
        self.game.counter = 0
        self.update_score()
        self.prev_room.start_text.update_text('RESUME')
        self.path = Path(self.map)
        super().creation()


class Final(Room):
    '''
    Конец игры,
    подведение итогов
    '''

    def __init__(self, game, is_victory: bool):
        super().__init__(game, pause_enabled=False, background= Color.BROWN if is_victory else Color.BLACK)
        title = Text(game=self.game, text='YOU WON!' if is_victory else'GAME OVER', font_size=48, color=Color.GREEN,
                     pos=(self.game.size[0] // 2, self.game.size[1] // 5), centrate=(True, False))
        self.game.records.add(self.game.score)
        self.next_room = GameRecords(game, self)

        record_text = Text(game=self.game, text='Your score is {}'.format(self.game.score),
                           pos=(self.game.size[0] // 2, self.game.size[1] / 2 - 50), centrate=(True, True))
        if self.game.score > max(self.game.records.stats):
            new_record = Text(game=self.game, text='This is a new record!', font_size=20,
                              pos=(self.game.size[0] // 2, self.game.size[1] / 2 - 30 + record_text.get_size()[1]),
                              color=Color.YELLOW, centrate=(True, True))
            self.toDraw.append(new_record)
        start_text = Text(self.game, text='MAIN MENU', color=Color.DARK_GREEN,
                          pos=(self.game.size[0] // 2, self.game.size[1] - self.game.size[1] // 3),
                          centrate=(True, True))
        replay_text = Text(self.game, text='PLAY AGAIN', color=Color.ORANGE,
                           pos=(self.game.size[0] // 2, self.game.size[1] - self.game.size[1] // 3 + 45),
                           centrate=(True, True))
        end_text = Text(self.game, text='EXIT GAME', color=Color.DARK_RED,
                        pos=(self.game.size[0] // 2, self.game.size[1] - self.game.size[1] // 3 + 135),
                        centrate=(True, True))
        records = Text(self.game, text='Show records', color=Color.YELLOW,
                       pos=(self.game.size[0] // 2, self.game.size[1] - self.game.size[1] // 3 + 90),
                       centrate=(True, True))
        menu = Menu(self.game)
        menu_btn = Button(self.game, start_text, Color.BLACK if not is_victory else Color.BROWN, Color.DARK_GREEN, \
                          Action(transit, game=self.game, room=menu))
        replay_btn = Button(self.game, replay_text, Color.BLACK if not is_victory else Color.BROWN, Color.ORANGE, \
                            Action(transit, game=self.game, room=menu.next_room))
        records_btn = Button(self.game, records, Color.BLACK if not is_victory else Color.BROWN, Color.YELLOW, \
                             Action(transit, game=self.game, room=self.next_room))
        exit_btn = Button(self.game, end_text, Color.BLACK if not is_victory else Color.BROWN, Color.DARK_RED, \
                          Action(self.game.quit))

        self.toDraw += [title, menu_btn, exit_btn, record_text, replay_text, replay_btn, records, records_btn]
        self.eventListeners += [exit_btn, menu_btn, replay_btn, records_btn]


class GameRecords(Room):

    def __init__(self, game, prev_room: Room = None):
        super().__init__(game)
        self.prev_room = prev_room
        shift = 0
        text = Text(self.game, text='highest scores:', font_size=25,
                    pos=(self.game.size[0] // 2, 50), centrate=(True, True))
        self.toDraw.append(text)

        if self.game.records.stats:
            for item in self.game.records.stats:
                text = Text(self.game, text=str(item), pos=(self.game.size[0] // 2, self.game.size[1] / 3 + shift),
                            centrate=(True, True))
                shift += text.get_size()[1] + 10
                self.toDraw.append(text)
        else:
            no = Text(self.game, text="There are no highest scores yet",
                      pos=(self.game.size[0] // 2, self.game.size[1] / 2),
                      centrate=(True, True))
            self.toDraw.append(no)

        back_text = Text(self.game, text='Back', color=Color.DARK_GREEN,
                         pos=(self.game.size[0] // 2, self.game.size[1] - self.game.size[1] // 4),
                         centrate=(True, True))
        back_btn = Button(self.game, back_text, Color.BLACK, Color.DARK_GREEN, \
                          Action(transit, game=self.game, room=self.prev_room))
        self.toDraw += [back_text, back_btn]
        self.eventListeners += [back_btn]
