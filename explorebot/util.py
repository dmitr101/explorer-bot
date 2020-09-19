from telegram import ReplyKeyboardMarkup, KeyboardButton
from math import sqrt, floor, ceil


def to_reply_keyboard(arr, request_location=False):
    grid_side = sqrt(len(arr))
    grid_width = floor(grid_side)
    grid_height = ceil(grid_side)
    keys = []
    for i in range(grid_height):
        row = []
        for j in range(grid_width):
            lin_index = i * grid_width + j
            row.append(KeyboardButton(
                arr[lin_index], request_location=request_location))
        keys.append(row)
    return ReplyKeyboardMarkup(keys, one_time_keyboard=True)
