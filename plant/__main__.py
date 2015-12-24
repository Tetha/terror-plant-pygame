
import collections

import pygame
import pygame.locals

import plant.main

class GameContainer(object):
    def __init__(self):
        self.eventbus = EventBus()
        self.display_parts = []
        self.actors = []

    def draw_all(self, screen):
        for display_part in self.display_parts:
            display_part.draw(screen)

    def add_display_part(self, display_part):
        self.display_parts.append(display_part)

    def act_all(self, delta):
        for actor in self.actors:
            actor.act(delta)

class EventBus(object):
    def __init__(self):
        self.subscribers = collections.defaultdict(list)

    def register(self, event_name, listener):
        self.subscribers[event_name].append(listener)

    def fire(self, event_name, *args, **kwargs):
        current_subs = dict(self.subscribers)
        for k, v in current_subs.iteritems():
            if event_name.startswith(k):
                for sub in v:
                    sub.__call__(event_name, *args, **kwargs)

class GameElement(object):
    def __init__(self, game):
        self.game = game
        self.display_part = None

    def on_event(self, event_name, callback):
        self.game.eventbus.register(event_name, callback)

    def fire_event(self, event_name, *args, **kwargs):
        self.game.eventbus.fire(event_name, *args, **kwargs)

    def add_placeholder_sprite(self):
        self.display_part = PlaceHolderSprite(self.game)
        self.game.add_display_part(self.display_part)
        

class PlaceHolderSprite(object):
    def __init__(self, game):
        self.game = game

        self.x = 0
        self.y = 0

        self.width = 100
        self.height = 100

        self.margin = 5

        self.marker = None

        self.red = 0
        self.green = 255 
        self.blue = 0


    @property
    def rect(self):
        return pygame.Rect(self.x+self.margin/2, self.y+self.margin/2, self.width-self.margin/2, self.height-self.margin/2)
    
    def enable_clicks(self):
        self.button = Button(self.game, self.rect, self.clicked)

    def clicked(self, button):
        self.on_click.__call__(button)

    def draw(self, screen):
        screen.fill((self.red, self.green, self.blue), self.rect)

        if self.marker is not None:
            font = pygame.font.SysFont('Arial', 12)
            textsur = font.render(self.marker, False, (0, 0, 0))
            screen.blit(textsur, self.rect)
        
class EventPrinter(object):
    def __init__(self, ignore=None):
        self.ignored = []
        if ignore:
            self.ignored.extend(ignore)

    def __call__(self, name, *args, **kwargs):
        if name not in self.ignored:
            print "Event %s -> %s / %s" % (name, args, kwargs)

class GridDisplay(GameElement):
    def __init__(self, game):
        super(GridDisplay, self).__init__(game)

        self.on_event("grid.created", self.create_grid_display)

    def create_grid_display(self, event_name, grid):
        for r in xrange(0, grid.height):
            for c in xrange(0, grid.width):
                CellDisplay(self.game, r, c, 100*r, 100*c)

class Button(GameElement):
    def __init__(self, game, rect, on_click):
        super(Button, self).__init__(game)
        self.rect = rect
        self.on_click = on_click

        self.on_event("input.mouse.click", self.handle_click)

    def handle_click(self, event_name, button, position):
        if self.rect.collidepoint(position):
            self.on_click.__call__(button)

    
class BuyLeafButton(GameElement):
    def __init__(self, game):
        super(BuyLeafButton, self).__init__(game)

        self.add_placeholder_sprite()
        self.display_part.x = 550
        self.display_part.y = 100

        self.display_part.red = 0
        self.display_part.green = 0
        self.display_part.blue = 255

        self.display_part.marker = "GROW LEAF"

class CellDisplay(GameElement):
    def __init__(self, game, row, col, x, y):
        super(CellDisplay, self).__init__(game)

        self.row = row
        self.col = col

        self.x = x
        self.y = y

        self.add_placeholder_sprite()
        self.display_part.x = x
        self.display_part.y = y
        self.display_part.width = 100
        self.display_part.height = 100
        self.display_part.margin = 10
        self.display_part.marker = "PLAINS"

        self.display_part.enable_clicks()
        self.display_part.on_click = self.clicked

        self.on_event("grid.tile.%d.%d.updated" % (self.row, self.col), self.tile_updated)

    def clicked(self, button):
        self.fire_event("tile_clicked", self.row, self.col)

    def tile_updated(self, event_name, new_field_type):
        if new_field_type is None:
            self.display_part.marker = "PLAINS"
        else:
            self.display_part.marker = new_field_type

class Grid(GameElement):
    def __init__(self, game):
        super(Grid, self).__init__(game)

        self.width = 5
        self.height = 5
        self.grid = {} 

        self.on_event("boot", self.create_grid)
        self.on_event("tile_clicked", self.change_tile)

    def field_type(self, row, column):
        return self.grid.get((row, column), None)

    def change_tile(self, event_name, row, column):
        if self.field_type(row, column) is None:
            new_type = "TOWN"
        else:
            new_type = None

        self.set_field_type(row, column, new_type)

    def set_field_type(self, row, col, new_type):
        if new_type is None:
            del self.grid[(row, col)]
        else:
            self.grid[(row, col)] = new_type
        self.fire_event("grid.tile.%d.%d.updated" % (row, col), new_type)        

    def create_grid(self, event_name):
        self.fire_event("grid.created", self)

    def __repr__(self):
        return "Grid(width=%d,height=%d,grid=%s)" % (self.width, self.height, self.grid)

def run():
    pygame.init()

    game = GameContainer()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    running = True

    game.eventbus.register("", EventPrinter(ignore=["draw"]))

    Grid(game)
    GridDisplay(game)
    BuyLeafButton(game)

    game.eventbus.fire("boot")
    while running:
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.locals.MOUSEBUTTONUP:
                game.eventbus.fire("input.mouse.click", event.button, event.pos)
        screen.fill((0, 0, 0))
        game.draw_all(screen)
        pygame.display.flip()

if __name__ == "__main__":
    run()
