from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time

# I2C + OLED setup
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
oled = SSD1306_I2C(128, 64, i2c)

# Keypad setup
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
                time.sleep(0.02)
                while col.value():
                    pass
                row.low()
                return keys[i][j]
        row.low()
    return None

# Paddle and ball setup
paddle_height = 16
player_y = 24
ai_y = 24

ball_x = 64
ball_y = 32
ball_dx = 2
ball_dy = 1

# Scores
player_score = 0
ai_score = 0
winning_score = 5

def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val)

def draw():
    oled.fill(0)
    # Show scores top center
    oled.text(f"P: {player_score}  AI: {ai_score}", 20, 0)
    # Player paddle (left)
    oled.fill_rect(0, player_y, 3, paddle_height, 1)
    # AI paddle (right)
    oled.fill_rect(125, ai_y, 3, paddle_height, 1)
    # Ball
    oled.fill_rect(ball_x, ball_y, 3, 3, 1)
    oled.show()

def reset_positions():
    global player_y, ai_y, ball_x, ball_y, ball_dx, ball_dy
    player_y = 24
    ai_y = 24
    ball_x = 64
    ball_y = 32
    ball_dx = 2
    ball_dy = 1

# Intro screen
oled.fill(0)
oled.text("PONG: AI Edition", 10, 10)
oled.text("÷ = UP, x = DOWN", 0, 30)
oled.text("Press any key...", 0, 50)
oled.show()

while not scan_keypad():
    time.sleep(0.1)

reset_positions()

# Game loop
while True:
    key = scan_keypad()

    # Player movement
    if key == "÷":
        player_y -= 4
    elif key == "x":
        player_y += 4

    player_y = clamp(player_y, 0, 64 - paddle_height)

    # Simple AI movement
    if ball_y > ai_y + paddle_height // 2:
        ai_y += 2
    elif ball_y < ai_y + paddle_height // 2:
        ai_y -= 2

    ai_y = clamp(ai_y, 0, 64 - paddle_height)

    # Ball movement
    ball_x += ball_dx
    ball_y += ball_dy

    # Bounce off top/bottom
    if ball_y < 0:
        ball_y = 0
        ball_dy = -ball_dy
    elif ball_y > 61:
        ball_y = 61
        ball_dy = -ball_dy

    # Bounce off player paddle
    if ball_x <= 3 and player_y <= ball_y <= player_y + paddle_height:
        ball_x = 3
        ball_dx = -ball_dx

    # Bounce off AI paddle
    if ball_x >= 122 and ai_y <= ball_y <= ai_y + paddle_height:
        ball_x = 122
        ball_dx = -ball_dx

    # Scoring
    if ball_x < -3:
        ai_score += 1
        oled.fill(0)
        oled.text("You Lose!", 30, 20)
        oled.text(f"Score: P{player_score} - AI{ai_score}", 15, 40)
        oled.text("Press any key", 0, 55)
        oled.show()
        while not scan_keypad():
            time.sleep(0.1)
        reset_positions()
        continue

    if ball_x > 131:
        player_score += 1
        oled.fill(0)
        oled.text("You Win!", 30, 20)
        oled.text(f"Score: P{player_score} - AI{ai_score}", 15, 40)
        oled.text("Press any key", 0, 55)
        oled.show()
        while not scan_keypad():
            time.sleep(0.1)
        reset_positions()
        continue

    # Check if someone won
    if player_score >= winning_score:
        oled.fill(0)
        oled.text("GAME OVER", 30, 20)
        oled.text("You are the Champ!", 0, 40)
        oled.text("Reset device to play", 0, 55)
        oled.show()
        break

    if ai_score >= winning_score:
        oled.fill(0)
        oled.text("GAME OVER", 30, 20)
        oled.text("AI wins! Try again", 0, 40)
        oled.text("Reset device to play", 0, 55)
        oled.show()
        break

    draw()
    time.sleep(0.03)
