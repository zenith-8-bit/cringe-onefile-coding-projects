import time
import numpy as np # For random functions
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1306, sh1106 # Or just ssd1306 if you know your chip
from PIL import ImageDraw

# --- Configuration for SPI ---
# SPI uses a bus (0 or 1) and device (0 or 1, for CS0 or CS1)
# Most common setup is bus 0, device 0 (CE0)
SPI_BUS = 0
SPI_DEVICE = 0 # Corresponds to CE0 (GPIO 8)

# GPIO pin numbers for DC and RESET (using BCM numbering)
# Ensure these match your wiring!
DC_PIN = 23   # Connected to GPIO 23 (Physical Pin 16)
RST_PIN = 24  # Connected to GPIO 24 (Physical Pin 18)

# Change this to match your display resolution and controller
# For 128x64: device = ssd1306(serial) or device = sh1106(serial)
# For 128x32: device = ssd1306(serial, width=128, height=32)
# The 'luma.oled' library will automatically try to autodetect the correct resolution
# if you don't specify width/height for common sizes.
serial = spi(port=SPI_BUS, device=SPI_DEVICE, gpio_DC=DC_PIN, gpio_RST=RST_PIN)
device = ssd1306(serial) # Try sh1106(serial) if ssd1306 doesn't work

# Calculate center for eye placement
center_x = device.width // 2
center_y = device.height // 2

# Define eye parameters (adjust these for your desired look)
EYE_RADIUS_X = 20
EYE_RADIUS_Y = 15
PUPIL_RADIUS = 5

# Eye positions (left and right eyes relative to the center)
LEFT_EYE_OFFSET_X = -25
RIGHT_EYE_OFFSET_X = 25
EYE_OFFSET_Y = 0 # Adjust vertical position if needed

def draw_eye(draw, center_x_eye, center_y_eye, pupil_x_offset=0, pupil_y_offset=0):
    """Draws a single open eye with a pupil."""
    # Draw eye ellipse
    draw.ellipse((center_x_eye - EYE_RADIUS_X, center_y_eye - EYE_RADIUS_Y,
                  center_x_eye + EYE_RADIUS_X, center_y_eye + EYE_RADIUS_Y),
                 outline="white", fill="black") # Outer eye shape

    # Draw pupil
    pupil_center_x = center_x_eye + pupil_x_offset
    pupil_center_y = center_y_eye + pupil_y_offset
    draw.ellipse((pupil_center_x - PUPIL_RADIUS, pupil_center_y - PUPIL_RADIUS,
                  pupil_center_x + PUPIL_RADIUS, pupil_center_y + PUPIL_RADIUS),
                 outline="white", fill="white") # Pupil

def draw_closed_eye(draw, center_x_eye, center_y_eye):
    """Draws a closed eye (a simple horizontal line)."""
    draw.line((center_x_eye - EYE_RADIUS_X, center_y_eye,
               center_x_eye + EYE_RADIUS_X, center_y_eye),
              fill="white", width=2) # Simple line for closed eye

def animate_eyes():
    while True:
        # --- Open Eyes, Looking Straight ---
        with canvas(device) as draw:
            draw_eye(draw, center_x + LEFT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
            draw_eye(draw, center_x + RIGHT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
        time.sleep(np.random.uniform(1.0, 3.0)) # Stay open for a random duration

        # --- Blink ---
        for _ in range(2): # Quick blink (open-closed-open sequence)
            with canvas(device) as draw:
                draw_closed_eye(draw, center_x + LEFT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
                draw_closed_eye(draw, center_x + RIGHT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
            time.sleep(0.1) # Short delay for closed state
            with canvas(device) as draw:
                draw_eye(draw, center_x + LEFT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
                draw_eye(draw, center_x + RIGHT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
            time.sleep(0.1) # Short delay after opening

        # --- Look Left (randomly) ---
        if np.random.rand() > 0.7: # 30% chance to look left
            with canvas(device) as draw:
                draw_eye(draw, center_x + LEFT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y, pupil_x_offset=-PUPIL_RADIUS)
                draw_eye(draw, center_x + RIGHT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y, pupil_x_offset=-PUPIL_RADIUS)
            time.sleep(0.5)
            # Look straight again
            with canvas(device) as draw:
                draw_eye(draw, center_x + LEFT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
                draw_eye(draw, center_x + RIGHT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
            time.sleep(0.3)

        # --- Look Right (randomly) ---
        if np.random.rand() > 0.7: # 30% chance to look right
            with canvas(device) as draw:
                draw_eye(draw, center_x + LEFT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y, pupil_x_offset=PUPIL_RADIUS)
                draw_eye(draw, center_x + RIGHT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y, pupil_x_offset=PUPIL_RADIUS)
            time.sleep(0.5)
            # Look straight again
            with canvas(device) as draw:
                draw_eye(draw, center_x + LEFT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
                draw_eye(draw, center_x + RIGHT_EYE_OFFSET_X, center_y + EYE_OFFSET_Y)
            time.sleep(0.3)

        # You can add more animations here: surprised eyes, winks, etc.

try:
    # Clear the display initially
    device.clear()
    animate_eyes()

except KeyboardInterrupt:
    print("\nExiting animation.")
finally:
    device.clear() # Clear display on exit
    print("Display cleared.")
