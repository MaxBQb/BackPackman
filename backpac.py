'''
BackPackMan v0.0.1 initial
'''

import pygame, sys


class Game:
    def __init__(self, w: int, h: int):
        self.background = (0, 0, 0)
        self.screen = None
        self.size = (w, h)
        self.GameOver = False
        self.Paused = False
        self.current_room = Menu(self)
        self.clock = pygame.time.Clock()

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.GameOver = True
            if not self.Paused:
                self.current_room.process_event(e)

    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        while not self.GameOver:
            self.process_events()
            self.current_room.step()
            self.screen.fill(self.background)
            self.current_room.draw()
            pygame.display.flip()
            pygame.time.wait(60)

    def gamequit(self):
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


class Menu(Room):
    '''
    Здесь нужно реализовать комнату (сцену)
    сюда подключаются кнопки и прочее.
    У конопок должны быть методы draw и act соответственно.
    '''

    def __init__(self, game):
        super().__init__(game)
        self.game = game

    def draw(self):
        title = Text(game=self.game, text='BACK_PAC_MAN')

        start_text = Text(self.game, text='START GAME')
        start_text_w = start_text.get_size()[0]
        start_text_h = start_text.get_size()[1]
        start_text.update_position(x=self.game.size[0] / 2 - start_text_w / 2, y=self.game.size[1] / 3)

        end_text = Text(self.game, text='EXIT GAME')
        end_text_w = end_text.get_size()[0]
        end_text.update_position(x=self.game.size[0] / 2 - end_text_w / 2, y=self.game.size[1] / 3 + start_text_h + 10)

        start_btn = Button(self.game, start_text, Color.GREEN, Color.DARK_GREEN, MainField(self.game))
        exit_btn = Button(self.game, end_text, Color.RED, Color.DARK_RED, self.game.gamequit)

        self.toDraw.append(title)
        self.toDraw.append(start_btn)
        self.toDraw.append(exit_btn)
        self.eventListeners.append(start_btn)
        self.eventListeners.append(exit_btn)

        super().draw()
        self.game.clock.tick(15)


class MainField(Room):
    def __init__(self, game):
        super().__init__(game)

    def draw(self):
        text = Text(self.game, text="This is a main field", x=100, y=100)

        back_text = Text(self.game, text="MAIN MENU", x=self.game.size[0] / 2, y=self.game.size[1] / 2)

        back_btn = Button(self.game, back_text, Color.GREEN, Color.DARK_GREEN, Menu(self.game))

        self.toDraw.append(text)
        self.toDraw.append(back_text)
        self.toDraw.append(back_btn)

        super().draw()

    def step(self):
        pass


class Drawable:
    image = pygame.image.load("null.png")

    def __init__(self, game: Game, x: int, y: int):
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


class Pacman(Creature):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(game, x, y, (64, 64))
        self.move_cache = []
        self.speed = 4

    def act(self, e: pygame.event):
        if e.type == pygame.KEYDOWN:
            if e.key in (119, 97, 115, 100) and (not len(self.move_cache) or self.move_cache[-1] != e.key) and len(
                    self.move_cache) < 5:
                self.move_cache.append(e.key)

    def step(self):
        if len(self.move_cache):
            mx_c, my_c = 0, 0
            if self.move_cache[0] == 119:
                my_c = -1
            elif self.move_cache[0] == 97:
                mx_c = -1
            elif self.move_cache[0] == 115:
                my_c = 1
            elif self.move_cache[0] == 100:
                mx_c = 1
            if not self.move(self.speed * mx_c, self.speed * my_c):
                self.move_cache.pop(0)
                self.step()


class FreeSpace(Interactable, Drawable):
    # Пути, по которым Creature ходит
    def __init__(self, game: Game, x: int, y: int):
        super(FreeSpace, self).__init__(game, x, y)


class Text:
    def __init__(self, game, font_name='Arial', font_size=25, is_bold=True, is_italic=False, text='Text',
                 color=(255, 255, 255), x=0, y=0):
        self.game = game
        self.font_name = font_name
        self.font_size = font_size
        self.is_bold = is_bold
        self.is_italic = is_italic
        self.color = color
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.is_bold, self.is_italic)
        self.update_text(text)

    def update_text(self, text):
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.color)

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        self.game.screen.blit(self.text_surface, [self.x, self.y])

    def get_size(self):
        return self.font.size(self.text)


class Button(Drawable):
    def __init__(self, game_object, text_object, inactive_color, active_color, room=None):
        super().__init__(game_object, 0, 0)
        self.game_object = game_object
        self.text = text_object
        self.position_x = text_object.x
        self.position_y = text_object.y
        self.width = text_object.get_size()[0]
        self.height = text_object.get_size()[1]
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.room = room

    def draw(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.position_x + self.width > mouse[0] > self.position_x and \
                self.position_y + self.height > mouse[1] > self.position_y:
            pygame.draw.rect(self.game_object.screen, self.active_color,
                             (self.position_x, self.position_y, self.width, self.height))
            if click[0] == 1 and self.room is not None:
                self.game_object.current_room = self.room
        else:
            pygame.draw.rect(self.game_object.screen, self.inactive_color,
                             (self.position_x, self.position_y, self.width, self.height))
        self.text.draw()

    def step(self):
        pass

    def act(self, event):
        pass


class Color:
    RED = (200, 0, 0)
    DARK_RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 200, 0)
    DARK_GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    ORANGE = (255, 180, 0)


if __name__ == '__main__':
    g = Game(600, 600)
    g.start()
