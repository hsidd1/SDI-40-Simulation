import random
import matplotlib.pyplot as plt


#Constants
#   Event types:
ARRIVAL = "Arrival"
STOP = "Stop"
CLEAR = "Clear"

#   Directions:
N = "North"
E = "East"
S = "South"
W = "West"


#Controls
TIME_STEP = 0.5
ARRIVAL_TIME = 10
HUMAN_CLEAR_TIME = 3
SDC_CLEAR_TIME = 2
HUMAN_TURNING_TIME = 5
SDC_TURNING_TIME = 4
HUMAN_MIN_STOP_TIME = 2
SDC_MIN_STOP_TIME = 1


NORTH_CAR_PROBABILITY = 0.05
EAST_CAR_PROBABILITY = 0.05
SOUTH_CAR_PROBABILITY = 0.05
WEST_CAR_PROBABILITY = 0.05


TURN_PROBABILITY = 0.33
LEFT_TURN_PROBABILITY = 0.5
HUMAN_PROBABILITY = 0

FENDERBENDER_PROBABILITY_HUMAN = 0.02
FENDERBENDER_PROBABILITY_SDC = 0.01
FATAL_PROBABILITY_HUMAN = 0.002
FATAL_PROBABILITY_SDC = 0.001

FENDERBENDER_TIME = 20
FATAL_TIME = 120


#Classes

class Driver:

    def __init__(self, name, time, arrival_time, direction_from, direction_to, is_human):
        self.name = name
        self.is_human = is_human
        self.event = ARRIVAL
        self.start_time = time
        self.direction_from = direction_from
        self.direction_to = direction_to
        self.elapsed_time = 0
        self.busy_time = arrival_time
        self.crashed = False

    def get_from_to(self):
        return [self.direction_from, self.direction_to]

class DriverQueue:

    def __init__(self):
        self.north, self.east, self.south, self.west = [], [], [], []
        self.north_stop, self.east_stop, self.south_stop, self.west_stop = [], [], [], []
        self.intersection = []

    def add_driver_arrivals(self, driver):
        if driver.direction_from == N:
            self.north.append(driver)
        elif driver.direction_from == E:
            self.east.append(driver)
        elif driver.direction_from == S:
            self.south.append(driver)
        elif driver.direction_from == W:
            self.west.append(driver)

    def add_driver_stop(self, driver):
        if driver.direction_from == N:
            self.north_stop.append(driver)
        elif driver.direction_from == E:
            self.east_stop.append(driver)
        elif driver.direction_from == S:
            self.south_stop.append(driver)
        elif driver.direction_from == W:
            self.west_stop.append(driver)

    def add_driver_intersection(self, driver):
        self.intersection.append(driver)

    def elapse_driver_time(self):
        for driver in self.north:
            driver.busy_time -= TIME_STEP
        for driver in self.east:
            driver.busy_time -= TIME_STEP
        for driver in self.south:
            driver.busy_time -= TIME_STEP
        for driver in self.west:
            driver.busy_time -= TIME_STEP
        for driver in self.north_stop:
            driver.busy_time -= TIME_STEP
        for driver in self.west_stop:
            driver.busy_time -= TIME_STEP
        for driver in self.south_stop:
            driver.busy_time -= TIME_STEP
        for driver in self.east_stop:
            driver.busy_time -= TIME_STEP
        for driver in self.intersection:
            driver.busy_time -= TIME_STEP

    def get_next_driver(self):
        min_busy_time = 0
        driver = None
        if len(self.north_stop) != 0 and self.north_stop[0].busy_time < min_busy_time:
            min_busy_time = self.north_stop[0].busy_time
            driver = self.north_stop[0]
        if len(self.east_stop) != 0 and self.east_stop[0].busy_time < min_busy_time:
            min_busy_time = self.east_stop[0].busy_time
            driver = self.east_stop[0]
        if len(self.south_stop) != 0 and self.south_stop[0].busy_time < min_busy_time:
            min_busy_time = self.south_stop[0].busy_time
            driver = self.south_stop[0]
        if len(self.west_stop) != 0 and self.west_stop[0].busy_time < min_busy_time:
            min_busy_time = self.west_stop[0].busy_time
            driver = self.west_stop[0]
        return driver

    def reset_busy_time(self, direction):
        if direction == N:
            for driver in self.north_stop:
                if driver.busy_time < 0:
                    driver.busy_time = 0
        elif direction == E:
            for driver in self.east_stop:
                if driver.busy_time < 0:
                    driver.busy_time = 0
        elif direction == S:
            for driver in self.south_stop:
                if driver.busy_time < 0:
                    driver.busy_time = 0
        elif direction == W:
            for driver in self.west_stop:
                if driver.busy_time < 0:
                    driver.busy_time = 0
        


class Simulation:

    def __init__(self, total_cars):
        self.num_cars = 0
        self.total_cars = total_cars
        self.clock = 0

        self.intersection_free = True
        self.driver_queue = DriverQueue()
        self.generate_arrivals()
        self.completed_cars = []
        self.crashed_cars = []

    def run(self):
        while len(self.completed_cars) + len(self.crashed_cars) < self.total_cars:
            #print("The current time is ", self.clock)
            self.execute_events()
            self.driver_queue.elapse_driver_time()
            self.clock += TIME_STEP
            
    def execute_events(self):
        for driver in self.driver_queue.intersection:
            if driver.busy_time <= 0:
                self.execute_clear(driver)
        for driver in self.driver_queue.north:
            if driver.busy_time <= 0:
                self.execute_arrival(driver)
        for driver in self.driver_queue.west:
            if driver.busy_time <= 0:
                self.execute_arrival(driver)
        for driver in self.driver_queue.south:
            if driver.busy_time <= 0:
                self.execute_arrival(driver)
        for driver in self.driver_queue.east:
            if driver.busy_time <= 0:
                self.execute_arrival(driver)

        driver = self.driver_queue.get_next_driver()
        if driver != None:
            self.execute_stop(driver)
            
        if self.num_cars < self.total_cars:
            self.generate_arrivals()

    def execute_arrival(self, driver):
        desire = driver.get_from_to()

        if desire[0] == N:
            driver.event = STOP
            if driver.is_human:
                driver.busy_time = HUMAN_MIN_STOP_TIME
            else:
                driver.busy_time = SDC_MIN_STOP_TIME
            self.driver_queue.north.pop(0)
            self.driver_queue.add_driver_stop(driver)
        elif desire[0] == S:
            driver.event = STOP
            if driver.is_human:
                driver.busy_time = HUMAN_MIN_STOP_TIME
            else:
                driver.busy_time = SDC_MIN_STOP_TIME
            self.driver_queue.south.pop(0)
            self.driver_queue.add_driver_stop(driver)
        elif desire[0] == E:
            driver.event = STOP
            if driver.is_human:
                driver.busy_time = HUMAN_MIN_STOP_TIME
            else:
                driver.busy_time = SDC_MIN_STOP_TIME
            self.driver_queue.east.pop(0)
            self.driver_queue.add_driver_stop(driver)
        elif desire[0] == W:
            driver.event = STOP
            if driver.is_human:
                driver.busy_time = HUMAN_MIN_STOP_TIME
            else:
                driver.busy_time = SDC_MIN_STOP_TIME
            self.driver_queue.west.pop(0)
            self.driver_queue.add_driver_stop(driver)

          
    def generate_arrivals(self):
        time = self.clock
        
        r = random.random()
        car_id = self.num_cars
        if r < NORTH_CAR_PROBABILITY and len(self.driver_queue.north) == 0: #From North
            r = random.random()
            if r < TURN_PROBABILITY:
                r = random.random()
                if r < LEFT_TURN_PROBABILITY:
                    direction_to = E
                else:
                    direction_to = W
            else:
                direction_to = S
            r = random.random()
            if r < HUMAN_PROBABILITY:
                is_human = True
            else:
                is_human = False
            #print("Driver ", car_id, " from the North is going to the ", direction_to)
            self.driver_queue.add_driver_arrivals(Driver(car_id, time, ARRIVAL_TIME, N, direction_to, is_human))
            self.num_cars += 1

        r = random.random()
        car_id = self.num_cars
        if r < EAST_CAR_PROBABILITY and len(self.driver_queue.east) == 0: #From East
            r = random.random()
            if r < TURN_PROBABILITY:
                r = random.random()
                if r < LEFT_TURN_PROBABILITY:
                    direction_to = S
                else:
                    direction_to = N
            else:
                direction_to = W
            r = random.random()
            if r < HUMAN_PROBABILITY:
                is_human = True
            else:
                is_human = False
            #print("Driver ", car_id, " from the East is going to the ", direction_to)
            self.driver_queue.add_driver_arrivals(Driver(car_id, time, ARRIVAL_TIME, E, direction_to, is_human))
            self.num_cars += 1

        r = random.random()
        car_id = self.num_cars
        if r < SOUTH_CAR_PROBABILITY and len(self.driver_queue.south) == 0: #From South
            r = random.random()
            if r < TURN_PROBABILITY:
                r = random.random()
                if r < LEFT_TURN_PROBABILITY:
                    direction_to = W
                else:
                    direction_to = E
            else:
                direction_to = N
            r = random.random()
            if r < HUMAN_PROBABILITY:
                is_human = True
            else:
                is_human = False
            #print("Driver ", car_id, " from the South is going to the ", direction_to)
            self.driver_queue.add_driver_arrivals(Driver(car_id, time, ARRIVAL_TIME, S, direction_to, is_human))
            self.num_cars += 1

        r = random.random()
        car_id = self.num_cars
        if r < WEST_CAR_PROBABILITY and len(self.driver_queue.west) == 0: #From West
            r = random.random()
            if r < TURN_PROBABILITY:
                r = random.random()
                if r < LEFT_TURN_PROBABILITY:
                    direction_to = N
                else:
                    direction_to = S
            else:
                direction_to = E
            r = random.random()
            if r < HUMAN_PROBABILITY:
                is_human = True
            else:
                is_human = False
            #print("Driver ", car_id, "from the West is going to the ", direction_to)
            self.driver_queue.add_driver_arrivals(Driver(car_id, time, ARRIVAL_TIME, W, direction_to, is_human))
            self.num_cars += 1

    def execute_clear(self, driver):
        possible_crash_time = self.execute_crash(driver)
        self.clock += possible_crash_time
        driver.elapsed_time = self.clock - driver.start_time
        if possible_crash_time > 0:
            driver.crashed = True
            self.crashed_cars.append(driver)
        else:
            self.completed_cars.append(driver)
        self.driver_queue.intersection.pop(0)
        #print("Driver ", driver.name, " just left the intersection after ", driver.elapsed_time, "seconds")
        if len(self.driver_queue.intersection) == 0:
            self.intersection_free = True

    def execute_crash(self, driver):
        r = random.random()
        if r < FATAL_PROBABILITY_SDC and not driver.is_human:
            return FATAL_TIME
        elif r < FATAL_PROBABILITY_HUMAN and driver.is_human:
            return FATAL_TIME
        elif r < FENDERBENDER_PROBABILITY_SDC and not driver.is_human:
            return FENDERBENDER_TIME
        elif r < FENDERBENDER_PROBABILITY_HUMAN and driver.is_human:
            return FENDERBENDER_TIME
        else:
            return 0


    def execute_stop(self, driver):
        desire = driver.get_from_to()
        if not self.intersection_free:
            return


        if desire[0] == N and self.intersection_free:
            if desire[1] == S:
                driver.event = CLEAR
                if driver.is_human:
                    driver.busy_time = HUMAN_CLEAR_TIME
                else:
                    driver.busy_time = SDC_CLEAR_TIME
                self.driver_queue.north_stop.pop(0)
                self.driver_queue.reset_busy_time(N)
                self.driver_queue.add_driver_intersection(driver)
                self.intersection_free = False
            else:
                driver.event = CLEAR
                if driver.is_human:
                    driver.busy_time = HUMAN_TURNING_TIME
                else:
                    driver.busy_time = SDC_TURNING_TIME
                self.driver_queue.north_stop.pop(0)
                self.driver_queue.reset_busy_time(N)
                self.driver_queue.add_driver_intersection(driver)
                self.intersection_free = False
        elif desire[0] == S and self.intersection_free:
            if desire[1] == N:
                driver.event = CLEAR
                if driver.is_human:
                    driver.busy_time = HUMAN_CLEAR_TIME
                else:
                    driver.busy_time = SDC_CLEAR_TIME
                self.driver_queue.south_stop.pop(0)
                self.driver_queue.reset_busy_time(S)
                self.driver_queue.add_driver_intersection(driver)
                self.intersection_free = False
            else:
                driver.event = CLEAR
                if driver.is_human:
                    driver.busy_time = HUMAN_TURNING_TIME
                else:
                    driver.busy_time = SDC_TURNING_TIME
                self.driver_queue.south_stop.pop(0)
                self.driver_queue.reset_busy_time(S)
                self.driver_queue.add_driver_intersection(driver)
                self.intersection_free = False
        elif desire[0] == E and self.intersection_free:
            if desire[1] == W:
                driver.event = CLEAR
                if driver.is_human:
                    driver.busy_time = HUMAN_CLEAR_TIME
                else:
                    driver.busy_time = SDC_CLEAR_TIME
                self.driver_queue.east_stop.pop(0)
                self.driver_queue.reset_busy_time(E)
                self.driver_queue.add_driver_intersection(driver)
                self.intersection_free = False
            else:
                driver.event = CLEAR
                if driver.is_human:
                    driver.busy_time = HUMAN_TURNING_TIME
                else:
                    driver.busy_time = SDC_TURNING_TIME
                self.driver_queue.east_stop.pop(0)
                self.driver_queue.reset_busy_time(E)
                self.driver_queue.add_driver_intersection(driver)
                self.intersection_free = False
        elif desire[0] == W and self.intersection_free:
            if desire[1] == E:
                driver.event = CLEAR
                if driver.is_human:
                    driver.busy_time = HUMAN_CLEAR_TIME
                else:
                    driver.busy_time = SDC_CLEAR_TIME
                self.driver_queue.west_stop.pop(0)
                self.driver_queue.reset_busy_time(W)
                self.driver_queue.add_driver_intersection(driver)
                self.intersection_free = False
            else:
                driver.event = CLEAR
                if driver.is_human:
                    driver.busy_time = HUMAN_TURNING_TIME
                else:
                    driver.busy_time = SDC_TURNING_TIME
                self.driver_queue.west_stop.pop(0)
                self.driver_queue.reset_busy_time(W)
                self.driver_queue.add_driver_intersection(driver)
                self.intersection_free = False

    def output_times(self):
        times = []
        for car in self.completed_cars:
            times.append(car.elapsed_time)
        print(times)

    def output_to_CSV(self):
        f = open("output_SDtest.csv", 'w')
        f.write("Name,Type,Start Time,Elapsed Time,Start Direction,End Direction,Crashed\n")
        for car in self.completed_cars:
            f.write(str(car.name) + "," + str(car.is_human) + "," + str(car.start_time) + "," + str(car.elapsed_time) + "," + str(car.direction_from) + "," + str(car.direction_to) + str(car.crashed) + "\n")
        f.close()
        


def main():
    sim = Simulation(100000)
    sim.run()
    sim.output_times()
    sim.output_to_CSV()
