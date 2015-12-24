
import collections

import pygame
import pygame.locals

import plant.main

class GameContainer(object):
    def __init__(self):
        self.entities = EntitySet()

    def all_with(self, *tags):
        return self.entities.all_with(*tags)

    def add_entity(self, entity):
        self.entities.add(entity)

    def draw_all(self, screen):
        for entity in self.all_with('draw'):
            entity.draw(screen)

    def act_all(self, delta):
        for entity in self.all_with('act_per_frame'):
            actor.act(delta)

class EntitySet(object):
    def __init__(self, entities=None):
        if entities is None:
            entities = []
        self.entities = entities

    def add(self, entity):
        self.entities.append(entity)

    def all_with(self, *tags):
        return EntitySet([e for e in self.entities if all(tag in e.tags for tag in tags)])

    def call(self, callback):
        for e in self.entities:
            callback(e)

    def __getitem__(self, idx):
        return self.entities[idx]

    def __len__(self):
        return len(self.entities)

class GameElement(object):
    def __init__(self, game):
        self.game = game
        self.tags = []
        self.display_part = None

        self.game.add_entity(self)

    def add_tag(self, tag):
        self.tags.append(tag)

    def draw(self, screen):
        self.display_part.draw(screen)

    def enable_clicks(self):
        self.button = Button(self.game, self.clicked)

    def clicked(self, button):
        self.on_click.__call__(button)

    def add_placeholder_sprite(self):
        self.add_tag('draw')
        self.display_part = PlaceHolderSprite(self.game)
        

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

        grid = game.all_with('grid')[0]

        for r in xrange(0, grid.height):
            for c in xrange(0, grid.width):
                CellDisplay(self.game, r, c, 100*r, 100*c)

class Button(GameElement):
    def __init__(self, game, on_click):
        super(Button, self).__init__(game)

        self.x = 0
        self.y = 0

        self.width = 100
        self.height = 100

        self.on_click = on_click
        self.add_tag('click_observer')

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def mouse_click(self, button, position):
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

        self.enable_clicks()
        self.button.x = x
        self.button.y = y
        self.button.width = 100
        self.button.height = 100
        self.button.on_click = self.clicked

        self.add_tag('tile_observer')

    def clicked(self, button):
        self.game.all_with('grid').call(lambda e: e.change_tile(self.row, self.col))

    def tile_updated(self, row, col, new_field_type):
        if row != self.row or col != self.col:
            return

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

        self.add_tag('grid')

    def field_type(self, row, column):
        return self.grid.get((row, column), None)

    def change_tile(self, row, column):
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

        self.game.all_with('tile_observer').call(lambda e: e.tile_updated(row, col, new_type))

    def __repr__(self):
        return "Grid(width=%d,height=%d,grid=%s)" % (self.width, self.height, self.grid)

def run():
    pygame.init()

    game = GameContainer()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    running = True

    Grid(game)
    GridDisplay(game)
    BuyLeafButton(game)

    while running:
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.locals.MOUSEBUTTONUP:
                game.all_with('click_observer').call(lambda e: e.mouse_click(event.button, event.pos))
        screen.fill((0, 0, 0))
        game.draw_all(screen)
        pygame.display.flip()

if __name__ == "__main__":
    run()
