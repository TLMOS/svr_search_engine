from typing import Optional
from datetime import datetime

from PIL import Image, ImageDraw

import numpy as np


def float_to_color(value: float) -> tuple:
    """
    Convert float to color in RGB format.
    Color is picked from red to green through yellow gradient.

    Parameters:
    - value (float): value to convert to color

    Returns:
    - tuple[int, int, int]: color in RGB format
    """
    green = np.array([207, 246, 221])
    yellow = np.array([253, 245, 221])
    red = np.array([253, 221, 221])
    if value < 0.5:
        color = red + (yellow - red) * (value * 2)
    else:
        color = yellow + (green - yellow) * ((value - 0.5) * 2)
    return tuple(color.astype(int))


def draw_bounding_box(
    image: Image,
    box: list[int],
    color: tuple[int, int, int],
    width: int = 1,
):
    """
    Draw bounding box on image.

    Parameters:
    - image (Image): image to draw bounding box on
    - box (list[int]): bounding box coordinates (xyxy)
    - color (tuple[int, int, int]): bounding box color in RGB format
    - width (int): bounding box width
    """
    draw = ImageDraw.Draw(image)
    draw.rectangle(box, outline=color, width=width)


def date_time_form_to_timestamp(date: str, time: str) -> Optional[float]:
    """
    Convert date and time from web form to timestamp.

    Parameters:
    - date (str): date in format YYYY-MM-DD
    - time (str): time in format HH:MM

    Returns:
    - timestamp (float): timestamp
    """
    if date:
        date = datetime.strptime(date, '%Y-%m-%d')
    if time:
        time = datetime.strptime(time, '%H:%M')

    if time and date:
        time = datetime.combine(date, time.time()).timestamp()
    elif time:
        time = datetime.combine(datetime.today(), time.time()).timestamp()
    elif date:
        time = date.timestamp()
    else:
        time = None

    return time
