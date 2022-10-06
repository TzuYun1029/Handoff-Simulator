from tkinter import *
    
boundary_x = 15
boundary_y = 15
width = 50

def draw_roads(w):
    line_num = 11
    line_len = width*(line_num-1)

    for i in range(line_num):
        x1 = boundary_x + i*width
        x2 = boundary_x + i*width
        y1 = boundary_y
        y2 = boundary_y + line_len
        w.create_line(x1, y1, x2, y2)
    for i in range(line_num):
        x1 = boundary_x
        x2 = boundary_x + line_len
        y1 = boundary_y + i*width
        y2 = boundary_y+ i*width
        w.create_line(x1, y1, x2, y2)


def draw_bs(w, bs_pos_and_freq):
    radius = 4
    for bs in bs_pos_and_freq:
        x_in_canvas = bs[0]/(2500/width) + boundary_x
        y_in_canvas = bs[1]/(2500/width) + boundary_y
        w.create_oval(x_in_canvas - radius, y_in_canvas - radius, x_in_canvas + radius, y_in_canvas + radius, fill="red")


def draw_car_itself(w, x, y):
    radius = 4
    x_in_canvas = x/(2500/width) + boundary_x
    y_in_canvas = y/(2500/width) + boundary_y
    dot = w.create_oval(x_in_canvas - radius, y_in_canvas - radius, x_in_canvas + radius, y_in_canvas + radius, fill="green")
    w.update_idletasks()
    w.pack()
    return dot
        







    