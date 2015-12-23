
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


    def on_event(self, event_name, callback):
        self.game.eventbus.register(event_name, callback)

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
                self.game.add_display_part(CellDisplay(self.game, r, c, 100*r, 100*c))

class Button(GameElement):
    def __init__(self, game, rect, on_click):
        super(Button, self).__init__(game)
        self.rect = rect
        self.on_click = on_click

        self.on_event("input.mouse.click", self.handle_click)

    def handle_click(self, event_name, button, position):
        if self.rect.collidepoint(position):
            self.on_click.__call__(button)

    
class CellDisplay(GameElement):
    def __init__(self, game, row, col, x, y):
        super(CellDisplay, self).__init__(game)

        self.row = row
        self.col = col

        self.x = x
        self.y = y

        self.button = Button(game, pygame.Rect(self.x+5, self.y+5, 90, 90), self.clicked)

    def clicked(self, button):
        self.game.eventbus.fire("tile_clicked", self.row, self.col)

    def create_grid(self, event_name, grid):
        self.grid = grid

    def draw(self, screen):
        rect = pygame.Rect(self.x+5, self.y+5, 90, 90)
        screen.fill((0, 255, 0), rect)
        
class Grid(GameElement):
    def __init__(self, game):
        super(Grid, self).__init__(game)

        self.width = 5
        self.height = 5
        self.grid = collections.defaultdict(None)

        self.on_event("boot", self.create_grid)

    def create_grid(self, event_name):
        self.game.eventbus.fire("grid.created", self)

    def __repr__(self):
        return "Grid(width=%d,height=%d,grid=%s)" % (self.width, self.height, self.grid)

def run():
    game = GameContainer()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    running = True

    game.eventbus.register("", EventPrinter(ignore=["draw"]))

    Grid(game)
    GridDisplay(game)


    game.eventbus.fire("boot")
    while running:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.locals.MOUSEBUTTONUP:
            game.eventbus.fire("input.mouse.click", event.button, event.pos)
        screen.fill((0, 0, 0))
        game.draw_all(screen)
        pygame.display.flip()

if __name__ == "__main__":
    run()
