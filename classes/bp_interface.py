from classes.bp_basics import *
from classes.Color_Scheme import *


class Text(Drawable):
    def __init__(self, game, font_name='fonts/Emulogic.ttf', font_size=15, is_bold=True, is_italic=False, text='Text',
                 color=Color.WHITE, x=0, y=0):
        super().__init__(game, x, y)
        self.font_name = font_name
        self.font_size = font_size
        self.is_bold = is_bold
        self.is_italic = is_italic
        self.color = color
        self.text = ''
        self.image = None
        self.font = pygame.font.Font(self.font_name, self.font_size)
        self.update_text(text)
        self.update_position(x, y)

    def update_text(self, text):
        self.text = text
        self.image = self.font.render(self.text, True, self.color)

    def update_position(self, x, y):
        self.x, self.y = x, y

    def draw(self):
        self.game.screen.fill(self.game.current_room.background, (self.game.size[0] // 2 - 30, self.game.size[1] - 30,
                                                                  self.get_size()[0], self.get_size()[1]))
        self.game.screen.blit(self.image, [self.x, self.y])

    def get_size(self):
        return self.font.size(self.text)


class Button(Drawable):
    def __init__(self, game_object: Game, text_object: Text, inactive_color, active_color, on_click: Action):
        super().__init__(game_object, 0, 0)
        self.game_object = game_object
        self.text = text_object
        self.position_x = text_object.x
        self.position_y = text_object.y
        self.width = text_object.get_size()[0]
        self.height = text_object.get_size()[1]
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.on_click = on_click

    def draw(self):
        mouse = pygame.mouse.get_pos()
        if self.position_x + self.width > mouse[0] > self.position_x and \
                self.position_y + self.height > mouse[1] > self.position_y:
            pygame.draw.rect(self.game_object.screen, self.active_color,
                             (self.position_x, self.position_y, self.width, self.height), 2)
        else:
            pygame.draw.rect(self.game_object.screen, self.inactive_color,
                             (self.position_x, self.position_y, self.width, self.height))
        self.text.draw()

    def step(self):
        pass

    def act(self, event):
        if event.type == pygame.MOUSEBUTTONUP\
           and event.button == 1\
           and self.position_x + self.width > event.pos[0] > self.position_x\
           and self.position_y + self.height > event.pos[1] > self.position_y\
           and self.on_click is not None:
            self.on_click.act()
