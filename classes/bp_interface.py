from classes.bp_basics import *
from classes.Color_Scheme import *


class Text(Drawable):
    def __init__(self, game, font_name='fonts/Emulogic.ttf', font_size=15, is_bold=True, is_italic=False, text='Text',
                 color=Color.WHITE, pos=(0, 0), centrate: (bool, bool) = (False, False)):
        super().__init__(game, *pos)
        self.container = None
        self.font_name = font_name
        self.font_size = font_size
        self.is_bold = is_bold
        self.centrate = centrate
        self.is_italic = is_italic
        self.color = color
        self.text = ''
        self.image = None
        self.font = pygame.font.Font(self.font_name, self.font_size)
        self.update_text(text)

    def update_text(self, text):
        self.text = text
        self.image = self.font.render(self.text, True, self.color)
        if self.centrate[0] or self.centrate[1]:
            sz = self.get_size()
            self.offset = (sz[0]//2, sz[1]//2)
            if not self.centrate[0]:
                self.offset = (0, sz[1]//2)
            if not self.centrate[1]:
                self.offset = (sz[0]//2, 0)
        if self.container:
            self.container.update()

    def update_position(self, x, y):
        self.x, self.y = x, y
        if self.container:
            self.container.update()

    def get_size(self):
        return self.font.size(self.text)


class Button(Drawable):
    def __init__(self, game_object: Game, text_object: Text, inactive_color, active_color, *on_click: Action, padding: int = 6):
        super().__init__(game_object, text_object.x-padding, text_object.y-padding)
        self.padding = padding
        self.text = text_object
        self.text.container = self
        self.width, self.height = (0, 0)
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.on_click = on_click
        self.prepare_position()

    def draw(self):
        mouse = pygame.mouse.get_pos()
        if self.x + self.width > mouse[0] > self.x and \
                self.y + self.height > mouse[1] > self.y:
            pygame.draw.rect(self.game.screen, self.active_color,
                             (self.x, self.y, self.width, self.height), 2)
        else:
            pygame.draw.rect(self.game.screen, self.inactive_color,
                             (self.x, self.y, self.width, self.height))
        self.text.draw()

    def update(self):
        self.prepare_position()

    def prepare_position(self):
        self.width, self.height = self.text.get_size()
        self.width += 2*self.padding
        self.height += 2*self.padding
        self.x = self.text.x - self.padding - self.text.offset[0]
        self.y = self.text.y - self.padding - self.text.offset[1]

    def interact(self, event):
        if event.type == pygame.MOUSEBUTTONUP\
           and event.button == 1\
           and self.x + self.width > event.pos[0] > self.x\
           and self.y + self.height > event.pos[1] > self.y\
           and self.on_click is not None:
            for e in self.on_click:
                e.act()



