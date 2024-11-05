"""
The Snake.
A game where you play as a snake eating apples and growing.
Eat an apple, get an extra cell to the body.
Hit your own body, the game starts from scratch.
"""

from random import randint, choice

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
GRID_WIDTH_CENTER = SCREEN_WIDTH // 2
GRID_HEIGHT_CENTER = SCREEN_HEIGHT // 2

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 6

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Common root for game classes."""

    def __init__(self, position=None, body_color=(0, 0, 255)):
        """Create object GameObject using input parameters."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Draw the game object, must be implemented in child classes."""
        raise NotImplementedError('Method has to be implemented in sub-class')

    def reset(self):
        """Delete the existing object and create a new one."""
        raise NotImplementedError('Method has to be implemented in sub-class')


class Apple(GameObject):
    """Game class Apple."""

    def __init__(self, body_color=APPLE_COLOR, forbidden_cells=None):
        """Create Apple object using input parameters."""
        super().__init__(None, body_color)
        self.randomize_position(forbidden_cells)

    def randomize_position(self, forbidden_cells):
        """Return random position on the field for apple."""
        _forbidden_cells = forbidden_cells if forbidden_cells else []
        cell_candidate = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        while cell_candidate in _forbidden_cells:
            cell_candidate = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
        self.position = cell_candidate

    def draw(self):
        """Draw apple on the field."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def reset(self, forbidden_cells=None):
        """Delete the apple and create another."""
        self.randomize_position(forbidden_cells=forbidden_cells)


class Snake(GameObject):
    """Game class Snake."""

    def __init__(self,
                 direction=RIGHT,
                 body_color=SNAKE_COLOR):
        """Create Snake object using input parameters."""
        super().__init__((GRID_WIDTH_CENTER, GRID_HEIGHT_CENTER), body_color)
        self.positions = [(GRID_WIDTH_CENTER, GRID_HEIGHT_CENTER)]
        self.direction = direction
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Get head position."""
        return self.positions[0]

    def get_field_ahead(self):
        """Get position to be stepped into."""
        head_x, head_y = self.get_head_position()
        if self.direction == RIGHT:
            return (head_x + GRID_SIZE) % SCREEN_WIDTH, head_y
        if self.direction == DOWN:
            return head_x, (head_y + GRID_SIZE) % SCREEN_HEIGHT,
        if self.direction == LEFT:
            return (head_x - GRID_SIZE) % SCREEN_WIDTH, head_y
        if self.direction == UP:
            return head_x, (head_y - GRID_SIZE) % SCREEN_HEIGHT

    def update_direction(self):
        """Update direction."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Update structure accordingly to the one cell move."""
        new_head = self.get_field_ahead()
        self.positions.insert(0, new_head)
        self.last = self.positions.pop()

    def draw(self):
        """Draw he snake."""
        for position in self.positions[:-1]:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pg.Rect(
            self.positions[0], (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Kill the snake and create another."""
        self.positions = [(GRID_WIDTH_CENTER, GRID_HEIGHT_CENTER)]
        self.direction = choice([RIGHT, DOWN, LEFT, UP])
        self.next_direction = None
        self.last = None
        self.draw_reset()

    def draw_reset(self):
        """Fill entire filed with background color."""
        field = pg.Rect((0, 0), (SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, field)


def handle_keys(game_object):
    """Handle keys."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Main method of the program."""
    pg.init()

    apple = Apple()
    snake = Snake()
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake_tail = snake.positions[-1]
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.positions.append(snake_tail)
            apple.reset(forbidden_cells=snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
