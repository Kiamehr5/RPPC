from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
import random

# ───── OLED SETUP ─────
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
time.sleep(0.1)
oled = SSD1306_I2C(128, 64, i2c)

def display_text(text, y=0):
    oled.fill(0)
    oled.text(text, 0, y)
    oled.show()

# ───── KEYPAD SETUP ─────
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
        print(f"Row {i} set HIGH")
        for j, col in enumerate(cols):
            print(f"  Col {j} = {col.value()}")
            time.sleep(0.01)
            if col.value():
                print(f"Key press detected at {i},{j}")
                time.sleep(0.01)
                while col.value():
                    pass
                row.low()
                return keys[i][j]
        row.low()
    return None


# ───── INPUT VALIDATION ─────
def is_operator(char):
    return char in "+-*/"

def is_valid_input(values, key):
    if not values:
        return key not in "+*/."
    last_char = values[-1]
    if is_operator(last_char) and is_operator(key):
        return False
    if last_char == "." and key == ".":
        return False
    if key == ".":
        parts = split_expression(values)
        if "." in parts[-1]:
            return False
    return True

def split_expression(expr):
    part = ""
    parts = []
    for ch in expr:
        if is_operator(ch):
            if part:
                parts.append(part)
                part = ""
        else:
            part += ch
    if part:
        parts.append(part)
    return parts

# ───── STARTUP SCREEN ─────
oled.fill(0)
oled.text("Welcome!", 0, 0)
oled.show()
time.sleep(2)

oled.fill(0)
oled.text("This Project is", 0, 0)
oled.text("Created by", 0, 10)
oled.text("Kiamehr", 0, 20)
oled.show()
time.sleep(2)

oled.fill(0)
oled.text("Enter / to", 0, 0)
oled.text("Calculator Mode", 0, 10)
oled.text("x = Pong", 0, 20)
oled.text("- = Car Game", 0, 30)
oled.show()

# ───── WAIT FOR SELECTION ─────
selected = None
while selected is None:
    key = scan_keypad()
    if key in ["÷", "x", "-"]:
        selected = key
    time.sleep(0.1)

# ───── PONG GAME ─────
class Pong:
    def __init__(self):
        self.paddle_height = 16
        self.player_y = 24
        self.ai_y = 24
        self.ball_x = 64
        self.ball_y = 32
        self.ball_dx = 2
        self.ball_dy = 1
        self.player_score = 0
        self.ai_score = 0
        self.winning_score = 5

    def clamp(self, val, min_val, max_val):
        return max(min(val, max_val), min_val)

    def reset_positions(self):
        self.player_y = 24
        self.ai_y = 24
        self.ball_x = 64
        self.ball_y = 32
        self.ball_dx = 2
        self.ball_dy = 1

    def draw(self):
        oled.fill(0)
        oled.text(f"P:{self.player_score} AI:{self.ai_score}", 10, 0)
        oled.fill_rect(0, self.player_y, 3, self.paddle_height, 1)
        oled.fill_rect(125, self.ai_y, 3, self.paddle_height, 1)
        oled.fill_rect(self.ball_x, self.ball_y, 3, 3, 1)
        oled.show()

    def run(self):
        oled.fill(0)
        oled.text("PONG: AI Edition", 10, 10)
        oled.text("÷ = UP, x = DOWN", 0, 30)
        oled.text("Press any key...", 0, 50)
        oled.show()
        while not scan_keypad():
            time.sleep(0.1)

        self.reset_positions()

        while True:
            key = scan_keypad()
            if key == "÷":
                self.player_y -= 4
            elif key == "x":
                self.player_y += 4

            self.player_y = self.clamp(self.player_y, 0, 64 - self.paddle_height)

            # AI movement
            if self.ball_y > self.ai_y + self.paddle_height // 2:
                self.ai_y += 2
            elif self.ball_y < self.ai_y + self.paddle_height // 2:
                self.ai_y -= 2

            self.ai_y = self.clamp(self.ai_y, 0, 64 - self.paddle_height)

            # Ball movement
            self.ball_x += self.ball_dx
            self.ball_y += self.ball_dy

            if self.ball_y < 0 or self.ball_y > 61:
                self.ball_dy = -self.ball_dy

            if self.ball_x <= 3 and self.player_y <= self.ball_y <= self.player_y + self.paddle_height:
                self.ball_dx = -self.ball_dx

            if self.ball_x >= 122 and self.ai_y <= self.ball_y <= self.ai_y + self.paddle_height:
                self.ball_dx = -self.ball_dx

            if self.ball_x < -3:
                self.ai_score += 1
                self.reset_positions()
            elif self.ball_x > 131:
                self.player_score += 1
                self.reset_positions()

            if self.player_score >= self.winning_score or self.ai_score >= self.winning_score:
                oled.fill(0)
                oled.text("GAME OVER", 20, 20)
                oled.text("Reset to play", 10, 40)
                oled.show()
                break

            self.draw()
            time.sleep(0.03)

# ───── CAR GAME ─────
class CarGame:
    def __init__(self):
        self.lanes = [28, 59, 90]
        self.car_lane = 1
        self.car_y = 50
        self.car_width = 20
        self.car_height = 12
        self.obstacles = []
        self.speed = 2
        self.min_speed = 1
        self.max_speed = 5
        self.frame_count = 0
        self.spawn_rate = 30
        self.score = 0
        self.game_over = False

    def draw_car(self, x, y):
        oled.fill_rect(x, y, self.car_width, self.car_height, 1)
        oled.fill_rect(x+5, y-4, self.car_width-10, 4, 1)

    def draw_obstacle(self, x, y):
        oled.fill_rect(x, y, self.car_width, self.car_height, 1)

    def detect_collision(self, x1, y1, x2, y2):
        return abs(x1 - x2) < self.car_width and abs(y1 - y2) < self.car_height

    def draw_road(self):
        for x in [43, 74]:
            for y in range(0, 64, 4):
                oled.pixel(x, y, 1)

    def draw_score(self):
        oled.text(f"Score:{self.score}", 0, 0)
        oled.text(f"Spd:{self.speed}", 80, 0)

    def run(self):
        oled.fill(0)
        oled.text("CAR RACE!", 30, 20)
        oled.text("÷=Accel x=Decel", 0, 35)
        oled.text("-=Right +=Left", 0, 45)
        oled.text("Press any key", 0, 55)
        oled.show()
        while not scan_keypad():
            time.sleep(0.1)

        while True:
            key = scan_keypad()
            if not self.game_over:
                if key == "÷":
                    self.speed = min(self.speed + 1, self.max_speed)
                elif key == "x":
                    self.speed = max(self.speed - 1, self.min_speed)
                elif key == "+":
                    self.car_lane = max(0, self.car_lane - 1)
                elif key == "-":
                    self.car_lane = min(2, self.car_lane + 1)

                self.frame_count += 1
                if self.frame_count % self.spawn_rate == 0:
                    lane = random.randint(0, 2)
                    self.obstacles.append([lane, -self.car_height])

                for obs in self.obstacles:
                    obs[1] += self.speed

                self.obstacles = [obs for obs in self.obstacles if obs[1] < 64]
                self.score += 1

                car_x = self.lanes[self.car_lane]
                for obs in self.obstacles:
                    obs_x = self.lanes[obs[0]]
                    if self.detect_collision(car_x, self.car_y, obs_x, obs[1]):
                        self.game_over = True

                oled.fill(0)
                self.draw_road()
                self.draw_car(car_x, self.car_y)
                for obs in self.obstacles:
                    self.draw_obstacle(self.lanes[obs[0]], obs[1])
                self.draw_score()
                oled.show()
                time.sleep(0.03)
            else:
                oled.fill(0)
                oled.text("GAME OVER", 30, 20)
                oled.text(f"Score: {self.score}", 30, 40)
                oled.text("Press any key", 0, 55)
                oled.show()
                while not scan_keypad():
                    time.sleep(0.1)
                return
                

# ───── CALCULATOR ─────
def run_calculator():
    display_text("Press a button...", 0)
    while True:
        values = ""
        while True:
            key = scan_keypad()
            time.sleep(0.2) #debounce
            if key:
                if key == "x":
                    key = "*"
                elif key == "÷":
                    key = "/"
                if key == "=":
                    break
                if not is_valid_input(values, key):
                    continue
                values += key
                display_text(values)
        try:
            result = eval(values)
            display_text(f"= {result}")
        except Exception:
            display_text("Error")
        time.sleep(1)

# ───── RUN MODE ─────
if selected == "x":
    while True:
        Pong().run()
elif selected == "-":
    while True:
        CarGame().run()
else:
    while True:
        run_calculator()

