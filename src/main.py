import time
import sys
from random import randint
from neopixel import Neopixel
from machine import Pin, ADC

# LED strip settings
num_leds = 64  # Number of LED lights
state_machine = 0  # ID of the PIO state machine
pin_led = 0  # Pin controlling the LED strip
mode = "GRB"  # LED color mode
delay = 0.0001  # LED update delay
led_strip = Neopixel(num_leds, state_machine, pin_led, mode, delay)

# Joystick initialization
xAxis = ADC(Pin(27))  # Reading X-axis value from the joystick
yAxis = ADC(Pin(26))  # Reading Y-axis value from the joystick

# RGB color definitions
white = (245, 245, 220)
green = (102, 204, 0)
dark_green = (0, 153, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
black = (32, 32, 32)
dark_blue = (0, 76, 153)
magenta = (255, 0, 27)

class Field:
    def __init__(self, size):
        self.size = size  # Game field size
        self.icons = {
            0: (245, 245, 220),  # Empty field
            1: (102, 204, 0),  # Snake body
            2: (0, 153, 0),  # Snake head
            3: (255, 0, 0),  # Food
        }
        self.snake_coords = []  # Snake coordinates
        self._generate_field()
        self.add_entity()  # Add initial food

    def add_entity(self):
        """Adds food at a random position on the field."""
        while True:
            i = randint(0, self.size - 1)
            j = randint(0, self.size - 1)
            entity = [i, j]
            if entity not in self.snake_coords:
                self.field[i][j] = 3  # Set food
                break

    def _generate_field(self):
        """Creates an empty field of the given size."""
        self.field = [[0 for j in range(self.size)] for i in range(self.size)]

    def _clear_field(self):
        """Clears the field, removing snake traces."""
        self.field = [[j if j != 1 and j != 2 else 0 for j in i] for i in self.field]

    def get_entity_pos(self):
        """Returns the coordinates of the food on the field."""
        for i in range(self.size):
            for j in range(self.size):
                if self.field[i][j] == 3:
                    return [i, j]
        return [-1, -1]

    def is_snake_eat_entity(self):
        """Checks if the snake has eaten the food."""
        entity = self.get_entity_pos()
        head = self.snake_coords[-1]
        return entity == head

class Snake:
    def __init__(self, name):
        self.name = name  # Player name
        self.direction = 'up'  # Initial movement direction
        self.coords = [[0, 1], [0, 2], [0, 3]]  # Initial snake coordinates

    def level_up(self):
        """Adds a new segment to the snake's body."""
        a = self.coords[0]
        b = self.coords[1]
        tail = a[:]

        if a[0] < b[0]:
            tail[0] -= 1
        elif a[1] < b[1]:
            tail[1] -= 1
        elif a[0] > b[0]:
            tail[0] += 1
        elif a[1] > b[1]:
            tail[1] += 1

        tail = self._check_limit(tail)
        self.coords.insert(0, tail)

    def is_alive(self):
        """Checks if the snake has not collided with itself."""
        head = self.coords[-1]
        snake_body = self.coords[:-1]
        return head not in snake_body

    def _check_limit(self, point):
        """Ensures the snake does not go out of bounds (wraps around)."""
        if point[0] > self.field.size - 1:
            point[0] = 0
        elif point[0] < 0:
            point[0] = self.field.size - 1
        elif point[1] < 0:
            point[1] = self.field.size - 1
        elif point[1] > self.field.size - 1:
            point[1] = 0
        return point

    def move(self):
        """Moves the snake in the current direction."""
        head = self.coords[-1][:]

        if self.direction == 'up':
            head[0] -= 1
        elif self.direction == 'down':
            head[0] += 1
        elif self.direction == 'right':
            head[1] += 1
        elif self.direction == 'left':
            head[1] -= 1

        head = self._check_limit(head)
        del self.coords[0]
        self.coords.append(head)
        self.field.snake_coords = self.coords

        if not self.is_alive():
            sys.exit()

        if self.field.is_snake_eat_entity():
            self.level_up()
            self.field.add_entity()

    def set_field(self, field):
        """Assigns the field to the snake."""
        self.field = field

if __name__ == '__main__':
    field = Field(8)  # Creating the game field
    snake = Snake("Joe")  # Creating the snake
    snake.set_field(field)
    size = field.size

    while True:
        xValue = xAxis.read_u16()
        yValue = yAxis.read_u16()

        # Change direction based on joystick values
        if xValue <= 10000 and snake.direction != 'left':
            snake.direction = 'right'
        if xValue >= 56000 and snake.direction != 'right':
            snake.direction = 'left'
        if yValue <= 10000 and snake.direction != 'up':
            snake.direction = 'down'
        if yValue >= 56000 and snake.direction != 'down':
            snake.direction = 'up'

        # Move the snake
        snake.move()
        field._clear_field()

        for i, j in field.snake_coords:
            field.field[i][j] = 1
        head = field.snake_coords[-1]
        field.field[head[0]][head[1]] = 2

        for i in range(size):
            for j in range(size):
                led_strip.set_pixel(i * 8 + j, field.icons[field.field[i][j]])

        led_strip.show()
        time.sleep(0.25)
