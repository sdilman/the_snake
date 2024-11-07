"""The Snake Game.

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
DEFAULT_GAME_OBJECT_COLOR = (0, 0, 255)

SPEED = 6

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Common root for game classes."""

    def __init__(self, position=None, body_color=DEFAULT_GAME_OBJECT_COLOR):
        """Create object GameObject using input parameters."""
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position=None, body_color=None):
        """Draw one cell."""
        _position = position or self.position
        _body_color = body_color or self.body_color
        rect = pg.Rect(_position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, _body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

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
        super().__init__(position=None, body_color=body_color)
        self.randomize_position(forbidden_cells)

    def randomize_position(self, forbidden_cells):
        """Return random position on the field for apple."""
        _forbidden_cells = forbidden_cells or []
        while True:
            cell_candidate = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if cell_candidate not in _forbidden_cells:
                break
        self.position = cell_candidate

    def draw(self):
        """Draw apple on the field."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def reset(self, forbidden_cells=None):
        """Recreate the structure of the apple."""
        self.randomize_position(forbidden_cells=forbidden_cells)


class Snake(GameObject):
    """Game class Snake."""

    def __init__(self,
                 direction=RIGHT,
                 body_color=SNAKE_COLOR):
        """Create Snake object using input parameters."""
        super().__init__(
            position=(GRID_WIDTH_CENTER, GRID_HEIGHT_CENTER),
            body_color=body_color
        )
        self.reset(direction=direction)

    def get_head_position(self):
        """Get head position."""
        return self.positions[0]

    def get_field_ahead(self):
        """Get position to be stepped into."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        return (
            (
                abs(dir_x) * ((head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH)
                + abs(dir_y) * head_x
            ),
            (
                abs(dir_x) * head_y
                + abs(dir_y) * ((head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT)
            )
        )

    def update_direction(self):
        """Update direction."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Update structure accordingly to the one cell move."""
        # К замечанию об обязательной правке:
        #
        # В данном методе змейка движется строго на одну клетку,
        # поэтому удаление последнего элемента производится всегда.
        # Если она съедает яблоко, то эта ситуация обрабатывается
        # в основном цикле и хвост увеличивается. В основном цикле
        # сделана правка относительно обнуления поля last.
        new_head = self.get_field_ahead()
        self.positions.insert(0, new_head)
        self.last = self.positions.pop()

    def draw(self):
        """Draw he snake."""
        # К замечанию об НЕобязательной правке:
        #
        # Отрисовываем всю змейку так как в основном цикле
        # происходит сброс всего экрана...
        for position in self.positions:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)
        # К замечанию об обязательной правке:
        #
        # Отрисовка головы удалена в пользу отрисовки всей змеи
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self, direction=None):
        """Recreate the structure of the snake."""
        self.positions = [(GRID_WIDTH_CENTER, GRID_HEIGHT_CENTER)]
        self.direction = direction or choice((RIGHT, DOWN, LEFT, UP))
        self.next_direction = None
        self.last = None

    def restore_tail(self):
        """Cancel removal of the last cell."""
        if self.last:
            self.positions.append(self.last)
            self.last = None


def refresh_field():
    """Fill entire filed with background color."""
    screen.fill(BOARD_BACKGROUND_COLOR)


snake_directions = {
    (pg.K_UP, RIGHT): UP,
    (pg.K_UP, LEFT): UP,
    (pg.K_DOWN, RIGHT): DOWN,
    (pg.K_DOWN, LEFT): DOWN,
    (pg.K_RIGHT, DOWN): RIGHT,
    (pg.K_RIGHT, UP): RIGHT,
    (pg.K_LEFT, DOWN): LEFT,
    (pg.K_LEFT, UP): LEFT
}


def handle_keys(game_object):
    """Handle keys."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit("The game is over by user's request!")
        if event.type == pg.KEYDOWN:
            game_object.next_direction = snake_directions.get(
                (event.key, game_object.direction), game_object.direction
            )


def main():
    """Main method of the program."""
    pg.init()

    refresh_field()
    apple = Apple()
    snake = Snake()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.restore_tail()
            apple.reset(forbidden_cells=snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.reset(forbidden_cells=snake.positions)
            refresh_field()
        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
