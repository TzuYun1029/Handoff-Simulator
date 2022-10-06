import random
import math
import numpy as np
from tkinter import *
import UI

class Car:
    def __init__(self, start_x, start_y, way):
        
        self.x = start_x  
        self.y = start_y 
        self.way = way  # 0123 上右下左

        self.calling = True
        self.m_call = round(np.random.normal(300, 5), 0) # avg call time = 300sec
        self.m_release = 0
        self.current_call_time = 0
        self.current_release_time = 0
        self.current_bs_pmin = self.get_max_db_bs()
        self.current_bs_best_effort = self.get_max_db_bs()
        self.current_bs_entropy = self.get_max_db_bs()
        self.current_bs_algo4 = self.get_max_db_bs()
        self.dot = UI.draw_car_itself(w, self.x, self.y)

    def drive(self):
        if self.x % 2500 == 0 and self.y % 2500 == 0: # intersection
            r = random.randint(0,31)
            # 0123 上右下左
            if r < 2: # back
                self.way = (self.way + 2) % 4
            elif r < 9: # turn left
                self.way = (self.way + 3) % 4
            elif r < 16: # turn right
                self.way = (self.way + 1) % 4


        if self.way == 0: # go up
            self.y = self.y - 20
        elif self.way == 1: # go right
            self.x = self.x + 20
        elif self.way == 2: # go down
            self.y = self.y + 20
        elif self.way == 3: # go left
            self.x = self.x - 20

        if self.x < 0 or self.x > 25000 or self.y < 0 or self.y > 25000:
            w.delete(self.dot)
            return False # not in map
        else:
            if self.x % 100 == 0 and self.y % 100 == 0:
                if self.way == 0: # go up
                    w.move(self.dot, 0, -2)
                elif self.way == 1: # go right
                    w.move(self.dot, 2, 0)
                elif self.way == 2: # go down
                    w.move(self.dot, 0, 2)
                elif self.way == 3: # go left
                    w.move(self.dot, -2, 0)
            return True


    def call_release(self):
        if self.calling == True: # calling
            self.current_call_time = self.current_call_time + 1
            handoff = self.test_handoff(0) # calling
            if self.current_call_time == self.m_call:
                self.calling = False
                self.current_call_time = 0
                # mean release time = 1500 sec
                self.m_release = round(np.random.normal(1500, 5), 0)
            return handoff
        else: # releasing
            self.current_release_time = self.current_release_time + 1
            handoff = self.test_handoff(1) # releasing
            if self.current_release_time == self.m_release:
                self.calling = True
                self.current_release_time = 0
                # mean call time = 300 sec
                self.m_call = round(np.random.normal(300, 5), 0)
            return handoff


    def test_handoff(self, behavior):
        bs_db_list = self.get_db_list()
        max_db = max(bs_db_list)
        max_db_bs = bs_db_list.index(max_db)
        handoff = [0, 0, 0, 0, 0]
        # Pmin
        pmin = 20
        if bs_db_list[self.current_bs_pmin] < pmin and self.current_bs_pmin != max_db_bs:
            self.current_bs_pmin = max_db_bs
            handoff[0] = 1

        # best_effort
        if self.current_bs_best_effort != max_db_bs:
            self.current_bs_best_effort = max_db_bs
            handoff[1] = 1
            
        # Entropy
        entropy = 25
        diff = bs_db_list[max_db_bs] - bs_db_list[self.current_bs_entropy]
        if diff > entropy and self.current_bs_entropy != max_db_bs:
            self.current_bs_entropy = max_db_bs
            handoff[2] = 1

        # self-algorithm
        mymin = 15
        if bs_db_list[self.current_bs_algo4] < mymin and self.current_bs_algo4 != max_db_bs:
            self.current_bs_algo4 = max_db_bs
            handoff[3] = 1

        handoff[4] = behavior # 0 is calling / 1 is releasing

        return handoff
        

    def get_max_db_bs(self):
        bs_db_list = self.get_db_list()
        max_db = max(bs_db_list)
        best_bs = bs_db_list.index(max_db)
        return best_bs

    def get_db_list(self):
        if self.y % 2500 == 0: # horizontal road
            road_index = self.y // 2500
            point = self.x // 20
        else: # vertical road
            road_index = self.x // 2500 + 11
            point = self.y // 20
        return list(road_db[road_index][point])

###################################################################

# set UI canvas
canvas_width = 530
canvas_height = 700
master = Tk()
master.title("Network Simulator")
w = Canvas(master,width=canvas_width,height=canvas_height)

# draw roads
UI.draw_roads(w)
# set up bs
bs_pos_and_freq = []
for x in range(10):
    for y in range(10):
        r = random.randint(0,9)
        if r == 0:
            center_x = 1250 + 2500*x # meter
            center_y = 1250 + 2500*y
            
            r = random.randint(0,3)
            if r == 0:
                center_x = center_x + 100
            elif r == 1:
                center_x = center_x - 100
            elif r == 2:
                center_y = center_y + 100
            else: # 3
                center_y = center_y - 100

            f = random.randint(1,10) * 100
            pos_and_freq = (center_x, center_y,f)
            bs_pos_and_freq.append(pos_and_freq)

UI.draw_bs(w, bs_pos_and_freq)

road_db = [] # every point on the road has a list of receving dB from every bs
for road_index in range(22): # total 22 roads (0-10 horizontal 11-21 vertical)
    road = []
    for point in range(1251): # total 1251 points on each road (speed of car = 2m/s)
        point_db = []
        for bs in bs_pos_and_freq:
            if road_index < 11: # horizontal road
                # y^2 + x^2
                distance_square = pow((2500 * road_index - int(bs[1])),2) + pow((20 * point - int(bs[0])),2)
            else:
                # x^2 + y^2
                distance_square = pow((2500 * (road_index-11) - int(bs[0])),2) + pow((20 * point - int(bs[1])),2)
            distance = pow(distance_square, 0.5)/1000 # km
            Lp_db = round(32.45 + 20*(math.log(int(bs[2]),10) + math.log(distance,10)), 2)
            recv_db = round(120 - Lp_db, 2)
            point_db.append(recv_db)
        road.append(tuple(point_db))
    road_db.append(road)


cars_list = []
handoff_times_pmin = 0
handoff_times_best_effort = 0
handoff_times_entropy = 0
handoff_times_algo4 = 0
handoff_times_pmin_calling = 0
handoff_times_best_effort_calling = 0
handoff_times_entropy_calling = 0
handoff_times_algo4_calling = 0
time = 0
exact_time_label = w.create_text(20, 550, text='', anchor='nw')
num_of_car_label = w.create_text(20, 570, text='', anchor='nw')
q1_handoff_times = w.create_text(20, 590, text='', anchor='nw')
q2_handoff_times = w.create_text(20, 610, text='', anchor='nw')

while True:
    time = time + 1
    for i in range(36):
        # p = (math.exp(-1/12))*(1/12)
        #   = 0.07667
        r = random.randint(1,100000)
        if r <= 766:
            # 0123 上右下左
            if i < 9: # enter from top
                car = Car((i + 1) * 2500, 0, 2) # go dowon
            elif i < 18: # # enter from downward
                car = Car((i - 9 + 1) * 2500, 25000, 0) # go up
            elif i < 27: # enter from left
                car = Car(0, (i - 18 + 1) * 2500, 1) # go right
            else: # enter from right
                car = Car(25000, (i - 27 + 1) * 2500, 3) # go left

            cars_list.append(car)

    for car in cars_list: 
        if car.drive() == False: # not in map
            cars_list.remove(car)  
        else:
            handoff = car.call_release()
            if handoff[0] == 1:
                handoff_times_pmin += 1
            if handoff[1] == 1:
                handoff_times_best_effort += 1
            if handoff[2] == 1:
                handoff_times_entropy += 1
            if handoff[3] == 1:
                handoff_times_algo4 += 1

            if handoff[4] == 0: # calling
                if handoff[0] == 1:
                    handoff_times_pmin_calling += 1
                if handoff[1] == 1:
                    handoff_times_best_effort_calling += 1
                if handoff[2] == 1:
                    handoff_times_entropy_calling += 1
                if handoff[3] == 1:
                    handoff_times_algo4_calling += 1

    exact_time = str(time//3600) + "hr" + str((time//60)%60) + "min"
    num_of_cars = len(cars_list)
    w.itemconfig(exact_time_label, text=str(exact_time))
    w.itemconfig(num_of_car_label, text='number of cars: '+str(num_of_cars))
    w.itemconfig(q1_handoff_times, text='Q1 handoff times: Pmin: '+str(handoff_times_pmin)+' / best effort: '+str(handoff_times_best_effort)+' / entropy: '+str(handoff_times_entropy)+' / my algorithm: '+str(handoff_times_algo4))
    w.itemconfig(q2_handoff_times, text='Q2 handoff times: Pmin: '+str(handoff_times_pmin_calling)+' / best effort: '+str(handoff_times_best_effort_calling)+' / entropy: '+str(handoff_times_entropy_calling)+' / my algorithm: '+str(handoff_times_algo4_calling))

    w.update_idletasks()
    
            



