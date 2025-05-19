from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
import random

# Setup I2C and display
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
oled = SSD1306_I2C(128, 64, i2c)

# Keypad pins and keys
rows = [Pin(3, Pin.OUT), Pin(4, Pin.OUT), Pin(5, Pin.OUT), Pin(6, Pin.OUT)]
cols = [Pin(7, Pin.IN, Pin.PULL_DOWN), Pin(9, Pin.IN, Pin.PULL_DOWN), Pin(10, Pin.IN, Pin.PULL_DOWN), Pin(11, Pin.IN, Pin.PULL_DOWN)]

keys = [
    ["1", "2", "3", "÷"],
    ["4", "5", "6", "x"],
    ["7", "8", "9", "-"],
    [".", "0", "=", "+"]
]

def scan_keypad():
    for i, row in enumerate(rows):
        row.high()
        for j, col in enumerate(cols):
            if col.value():
                time.sleep(0.02)  # debounce
                while col.value():
                    pass
                row.low()
                return keys[i][j]
        row.low()
    return None

# Lane positions in pixels (x coordinates)
lanes = [28, 59, 90]  # left, center, right lanes

# Player car
car_lane = 1  # start in center lane
car_y = 50    # vertical fixed position near bottom
car_width = 20
car_height = 12

# Obstacles (other cars)
obstacle_width = 20
obstacle_height = 12
obstacles = []

# Speed controls
speed = 2      # pixels per frame
min_speed = 1
max_speed = 5

frame_count = 0
spawn_rate = 30  # frames between obstacles

score = 0
game_over = False

def draw_car(x, y):
    # Draw simple rectangle car + spoiler
    oled.fill_rect(x, y, car_width, car_height, 1)
    oled.fill_rect(x+5, y-4, car_width-10, 4, 1)

def draw_obstacle(x, y):
    # Draw simple rectangle obstacle car
    oled.fill_rect(x, y, obstacle_width, obstacle_height, 1)

def detect_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return not (x1+w1 < x2 or x1 > x2+w2 or y1+h1 < y2 or y1 > y2+h2)

def reset_game():
    global obstacles, score, game_over, car_lane, speed, frame_count
    obstacles = []
    score = 0
    game_over = False
    car_lane = 1
    speed = 2
    frame_count = 0

def draw_road():
    # Draw lane lines
    for x in [43, 74]:
        oled.vline(x, 0, 64, 1)
        # dotted lines
        for y in range(0, 64, 10):
            oled.pixel(x, y, 0)

def draw_score():
    oled.text(f"Score: {score}", 0, 0)
    oled.text(f"Speed: {speed}", 80, 0)

# Welcome screen
oled.fill(0)
oled.text("CAR RACE!", 30, 20)
oled.text("÷=Accel x=Decel", 0, 35)
oled.text("-=Right +=Left", 0, 45)
oled.text("Press any key", 0, 55)
oled.show()

while not scan_keypad():
    time.sleep(0.1)

reset_game()

while True:
    key = scan_keypad()

    if not game_over:
        # Controls
        if key == "÷":
            speed = min(speed + 1, max_speed)
        elif key == "x":
            speed = max(speed - 1, min_speed)
        elif key == "+":
            car_lane = max(0, car_lane - 1)  # move left lane
        elif key == "-":
            car_lane = min(2, car_lane + 1)  # move right lane

        # Spawn obstacles
        frame_count += 1
        if frame_count % spawn_rate == 0:
            lane = random.randint(0, 2)
            obstacles.append([lane, -obstacle_height])  # start just off-screen top

        # Move obstacles down
        for obs in obstacles:
            obs[1] += speed

        # Remove off screen obstacles & update score
        passed = [obs for obs in obstacles if obs[1] > 64]
        obstacles = [obs for obs in obstacles if obs[1] <= 64]
        score += len(passed)

        # Collision detection
        car_x = lanes[car_lane]
        for obs in obstacles:
            obs_x = lanes[obs[0]]
            obs_y = obs[1]
            if detect_collision(car_x, car_y, car_width, car_height,
                                obs_x, obs_y, obstacle_width, obstacle_height):
                game_over = True

        # Draw everything
        oled.fill(0)
        draw_road()
        draw_car(lanes[car_lane], car_y)
        for obs in obstacles:
            draw_obstacle(lanes[obs[0]], obs[1])
        draw_score()
        oled.show()

        time.sleep(0.03)

    else:
        # Game over screen
        oled.fill(0)
        oled.text("GAME OVER", 30, 20)
        oled.text(f"Score: {score}", 30, 40)
        oled.text("Press any key", 0, 55)
        oled.show()

        while not scan_keypad():
            time.sleep(0.1)

        reset_game()
