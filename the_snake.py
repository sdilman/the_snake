from random import randint

import pygame

# Константы для размеров поля и сетки:
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

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 6

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Common root for game classes"""

    def __init__(self, position=None, body_color=(0, 0, 255)):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Draw the game object (must be implemented in child classes)"""
        raise NotImplementedError


class Apple(GameObject):
    """Apple"""

    def __init__(self, body_color=(255, 0, 0)):
        _position = self.randomize_position()
        super().__init__(_position, body_color)

    def randomize_position(self):
        """Returns random position on the field for apple"""
        return (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self):
        """Draws apple on the field"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Snake"""

    def __init__(self,
                 length=1,
                 positions=[(GRID_WIDTH_CENTER, GRID_HEIGHT_CENTER)],
                 direction=RIGHT,
                 next_direction=None,
                 last=None,
                 dead_snake=None,
                 body_color=(0, 255, 0)):
        super().__init__(positions[0], body_color)
        self.length = length
        self.positions = positions
        self.direction = direction
        self.next_direction = next_direction
        self.last = last
        self.dead_snake = dead_snake

    def get_head_position(self):
        """Get head position"""
        return self.positions[0]

    def get_field_ahead(self):
        """Get position to be stepped into"""
        if self.direction == RIGHT:
            return (
                (self.positions[0][0] + GRID_SIZE) % SCREEN_WIDTH,
                self.positions[0][1],
            )
        elif self.direction == DOWN:
            return (
                self.positions[0][0],
                (self.positions[0][1] + GRID_SIZE) % SCREEN_HEIGHT,
            )
        elif self.direction == LEFT:
            return (
                (self.positions[0][0] - GRID_SIZE) % SCREEN_WIDTH,
                self.positions[0][1],
            )
        elif self.direction == UP:
            return (
                self.positions[0][0],
                (self.positions[0][1] - GRID_SIZE) % SCREEN_HEIGHT,
            )

    def update_direction(self):
        """Update direction"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, length_increase=False):
        """Update structure accordingly to the one cell move"""
        new_head = self.get_field_ahead()
        new_positions = [new_head]
        new_positions.extend(self.positions)
        self.positions = new_positions
        if not length_increase:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Draw he snake"""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(
            self.positions[0], (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(
                screen, BOARD_BACKGROUND_COLOR, last_rect)

        # Затирание умершей змеи
        if self.dead_snake:
            for cell in self.dead_snake:
                cell_rect = pygame.Rect(cell, (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, cell_rect)

    def reset(self):
        """Kill the snake and create another"""
        self.length = 1
        self.dead_snake = self.positions
        self.positions = [(GRID_WIDTH_CENTER, GRID_HEIGHT_CENTER)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Handle keys"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Main method of the program"""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    apple = Apple()
    snake = Snake()
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        eat_apple = (snake.get_field_ahead() == apple.position)
        self_crash = (snake.get_field_ahead() in snake.positions)
        if eat_apple:
            snake.move(length_increase=True)
            apple = Apple()
        elif self_crash:
            snake.reset()
        else:
            snake.move(length_increase=False)

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
