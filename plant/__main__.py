
import collections
import pygame

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

    def fire(self, event_name, event_data=None):
        current_subs = dict(self.subscribers)
        for k, v in current_subs.iteritems():
            if event_name.startswith(k):
                for sub in v:
                    sub.__call__(event_name, event_data)

class EventPrinter(object):
    def __init__(self, ignore=None):
        self.ignored = []
        if ignore:
            self.ignored.extend(ignore)

    def __call__(self, name, data):
        if name not in self.ignored:
            print "Event %s -> %s" % (name, data)

class GridDisplay(object):
    def __init__(self, game):
        self.game = game

        self.game.eventbus.register("grid.created", self.create_grid_display)

    def create_grid_display(self, event_name, grid):
        for r in xrange(0, grid.height):
            for c in xrange(0, grid.width):
                self.game.add_display_part(CellDisplay(r, c, 100*r, 100*c))

class CellDisplay(object):
    def __init__(self, row, col, x, y):
        self.row = row
        self.col = col

        self.x = x
        self.y = y

    def create_grid(self, event_name, grid):
        self.grid = grid

    def draw(self, screen):
        rect = pygame.Rect(self.x+5, self.y+5, 90, 90)
        screen.fill((0, 255, 0), rect)
        
class Grid(object):
    def __init__(self, game):
        self.game = game

        self.width = 5
        self.height = 5
        self.grid = collections.defaultdict(None)

        self.game.eventbus.register("boot", self.create_grid)

    def create_grid(self, event_name, event_data):
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
        clock.tick(60)
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False
        screen.fill((0, 0, 0))
        game.draw_all(screen)
        pygame.display.flip()

if __name__ == "__main__":
    run()
