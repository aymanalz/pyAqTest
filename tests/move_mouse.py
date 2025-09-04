import pyautogui
import time
import math


def move_mouse_in_circle():
    """Moves the mouse cursor in a circular pattern every second."""

    print("Starting circular mouse movement...")

    # Define the center of the circle and its radius
    center_x, center_y = (
        pyautogui.size().width // 2,
        pyautogui.size().height // 2,
    )  # Center of the screen
    radius = 100

    # Initial angle (in radians)
    angle = 0

    while True:  # Loop indefinitely for continuous circular movement
        # Calculate the new x and y coordinates on the circle's circumference
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))

        # Move the mouse to the calculated position
        pyautogui.moveTo(
            x, y, duration=0.2
        )  # Use moveTo for smoother movement to a specific point

        # Increment the angle for the next step (controls the speed and direction of rotation)
        angle += 0.1  # Adjust this value to change the speed of rotation

        # Wait for approximately one second before the next move
        time.sleep(1)


# Call the function to start the circular mouse movement
move_mouse_in_circle()
