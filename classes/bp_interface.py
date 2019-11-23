from classes.bp_basics import *
from classes.Color_Scheme import *


class Text:
    def __init__(self, game, font_name='Arial', font_size=25, is_bold=True, is_italic=False, text='Text',
                 color=Color.WHITE, x=0, y=0):
        self.game = game
        self.font_name = font_name
        self.font_size = font_size
        self.is_bold = is_bold
        self.is_italic = is_italic
        self.color = color
        self.x, self.y = x, y
        self.text = ''
        self.text_surface = None
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.is_bold, self.is_italic)
        self.update_text(text)

    def update_text(self, text):
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.color)

    def update_position(self, x, y):
        self.x, self.y = x, y

    def draw(self):
        self.game.screen.blit(self.text_surface, [self.x, self.y])

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
        click = pygame.mouse.get_pressed()
        if self.position_x + self.width > mouse[0] > self.position_x and \
                self.position_y + self.height > mouse[1] > self.position_y:
            pygame.draw.rect(self.game_object.screen, self.active_color,
                             (self.position_x, self.position_y, self.width, self.height))
            if click[0] == 1 and self.on_click is not None:
                self.on_click.act()
        else:
            pygame.draw.rect(self.game_object.screen, self.inactive_color,
                             (self.position_x, self.position_y, self.width, self.height))
        self.text.draw()

    def step(self):
        pass

    def act(self, event):
        pass
