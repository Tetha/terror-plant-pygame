
import collections
import pygame

import plant.main

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
    def __init__(self, eventbus):
        self.eventbus = eventbus

        self.eventbus.register("grid.created", self.create_grid_display)

    def create_grid_display(self, event_name, grid):
        for r in xrange(0, grid.height):
            for c in xrange(0, grid.width):
                CellDisplay(self.eventbus, r, c, 100*r, 100*c)

class CellDisplay(object):
    def __init__(self, eventbus, row, col, x, y):
        self.row = row
        self.col = col

        self.x = x
        self.y = y

        self.eventbus = eventbus
        self.eventbus.register("draw", self.draw)
        self.eventbus.register("grid.created", self.create_grid)

    def create_grid(self, event_name, grid):
        self.grid = grid

    def draw(self, event_name, screen):
        rect = pygame.Rect(self.x+5, self.y+5, 90, 90)
        screen.fill((0, 255, 0), rect)
        
class Grid(object):
    def __init__(self, eventbus):
        self.eventbus = eventbus
        self.width = 5
        self.height = 5
        self.grid = collections.defaultdict(None)

        self.eventbus.register("boot", self.create_grid)

    def create_grid(self, event_name, event_data):
        self.eventbus.fire("grid.created", self)

    def __repr__(self):
        return "Grid(width=%d,height=%d,grid=%s)" % (self.width, self.height, self.grid)

def run():
    eventbus = EventBus()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    running = True

    eventbus.register("", EventPrinter(ignore=["draw"]))

    Grid(eventbus)
    GridDisplay(eventbus)


    eventbus.fire("boot")
    while running:
        clock.tick(60)
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False
        screen.fill((0, 0, 0))
        eventbus.fire("draw", screen)
        pygame.display.flip()

if __name__ == "__main__":
    run()
