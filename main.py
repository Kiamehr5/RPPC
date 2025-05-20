from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time

# ───── OLED SETUP ─────
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
time.sleep(0.1) #delay for it to initialize
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
        for j, col in enumerate(cols):
            if col.value():
                time.sleep(0.02)  # debounce delay
                while col.value():
                    pass  # wait until key is released
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
oled.text("Enter a key to", 0, 0)
oled.text("continue...", 0, 10)
oled.show()

while not scan_keypad():
    time.sleep(0.1)

# ───── MAIN LOOP ─────
while True:
    values = ""
    last_key = ""

    # Collect input
    while True:
        key = scan_keypad()
        if key:
            if key == "=":
                break
            if key == "x":
                key = "*"
            elif key == "÷":
                key = "/"
            if not is_valid_input(values, key):
                continue
            values += key
            last_key = key
            display_text(values)

    # Evaluate expression
    try:
        result = eval(values)
        display_text(f"= {result}")
    except Exception:
        display_text("Error")

    # Wait for next key to restart
    while not scan_keypad():
        time.sleep(0.1)
    time.sleep(0.3)
