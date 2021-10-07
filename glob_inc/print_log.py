import time
from .color import color

def find_color(color_):
    if color_ == "red":
        return color.RED
    elif color_ == "yellow":
        return color.YELLOW
    elif color_ == "green":
        return color.GREEN
    elif color_ == "cyan":
        return color.CYAN
    elif color_ == "purple":
        return color.PURPLE
    elif color_ == "blue":
        return color.BLUE
    else:
        return ""

def cur_time_str():
    cur_time = time.localtime()
    cur_time_string = "[" + time.strftime("%H:%M:%S", cur_time) + "]"
    return cur_time_string

def print_log(line, color_ = "", show_time = True):
    if type(line) == str:
        color_str = find_color(color_)
        if show_time == True:
            print(cur_time_str(), end=" ")
        else:
            line = "           " + line
        print(color_str + line + color.END)
    else:
        print(line)
