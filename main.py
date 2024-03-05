import time

from collision_detector import Detector
from lane import Lane
from generator import Generator
from objects import GlobalObjectList
from settings import Settings
import sys
import logging
from math import floor
from road import Road
from visuals import Window, Visual
from constants import Ratio
import pygame
pygame.init()


def main():
    """ To run: main settings_file """
    final_crashed_ids = []

    crashes = 0
    my_settings = Settings(sys.argv[1])

    # initialize all objects based on settings

    # init your global objects list
    global_objects_list = GlobalObjectList()
    road_list = my_settings['roads']
    window = Window(global_objects_list)

    # init all Roads
    print(road_list)
    for road_settings in road_list:
        road_length = road_settings['length']
        current_road = Road(road_length, road_settings['direction'], road_settings['speed_limit'])
        global_objects_list.add_road(current_road)

        # init this road's lanes
        for lane_num, lane_settings in enumerate(road_settings['lanes']):
            my_generator = Generator(global_objects_list, lane_settings["generator"], lane_settings['flow_direction'], current_road.get_direction())
            my_lane = Lane(lane_num, current_road, lane_settings['width'],
                           global_objects_list, my_generator, lane_settings['flow_direction'])
            global_objects_list.add_lane(my_lane)

    # run the time loop
    total_timesteps = my_settings["simulation_timesteps"]
    timestep_length = my_settings["timestep"]

    detector = Detector(global_objects_list)
    lanes: list[Lane] = global_objects_list.get_lanes()
    debug = my_settings['loglevel']
    logging.getLogger().setLevel(debug)
    window = Window(global_objects_list)

    for loop in range(total_timesteps):
        time.sleep(0)
        all_visuals = global_objects_list.draw()
        for visual in all_visuals:
            pygame.draw.polygon(window.screen, visual.color, visual.locations)
        the_time = loop * timestep_length
        window.update(the_time)
        logging.info(f"Starting loop={loop}/{total_timesteps} time={the_time}s")

        # generate objects
        for this_lane in lanes:
            road_speed_limit = this_lane.get_speed_limit()
            if this_lane.generator.should_generate(the_time, this_lane.road.get_length(), global_objects_list):
                x0, y0 = this_lane.get_position(0)
                endx, endy = this_lane.get_position(1)
                new_driver = this_lane.generator.generate(x0, y0, my_settings['visibility'], endx, endy, road_speed_limit, my_settings)
                global_objects_list[new_driver.object_id] = new_driver
                this_lane.add(new_driver.object_id)
                logging.info(f"Generating a vehicle={new_driver.object_id} in lane={this_lane} position=({x0}, {y0}), destination=({endx}, {endy}) of type {new_driver.my_vehicle}")

        # plan next steps
        for this_driver in global_objects_list.values():
            for lane in lanes:
                if this_driver in lane.get_objects():
                    road_speed_limit = lane.get_speed_limit()
                    if this_driver.should_plan():
                        visible_objects = this_driver.look(global_objects_list)
                        accel_change = this_driver.plan(visible_objects, road_speed_limit, timestep_length)
                        assert accel_change <= this_driver.my_vehicle.max_acceleration
                        this_driver.accelerate(accel_change)

        # updating the map
        for this_driver in global_objects_list.values():
            this_driver.my_vehicle.update(timestep_length)
            logging.info(f"Updating {this_driver.object_id} to ({this_driver.my_vehicle.x}, {this_driver.my_vehicle.y})")

        # detect crashes
        crashed_ids = detector.detect_crashes()
        final_crashed_ids += crashed_ids
        crashes += len(crashed_ids)/2
        if crashed_ids:
            logging.info(f'Objects {crashed_ids} crashed.\n {[global_objects_list[crashed_id] for crashed_id in crashed_ids]}')
        crashes = floor(crashes)
        print(f'crashed_ids={crashed_ids}')

        finished_ids = crashed_ids
        # remove objects that crashed or move off the board
        for lane in lanes:
            finished_ids += lane.detect_end()

        print(f'finished_ids={finished_ids}')
        final_crashed = []
        # remove objects that move off the board
        for finished_object in finished_ids:
            if finished_object in global_objects_list:
                the_object = global_objects_list[finished_object]
                final_crashed.append(the_object)

                logging.info(f"Object {finished_object} being removed with a length of {the_object.my_vehicle.length} with location ({the_object.my_vehicle.x, the_object.my_vehicle.y}).")
                for lane in global_objects_list.get_lanes():
                    lane.remove(finished_object)

                del global_objects_list[finished_object]
            else:
                logging.warning(f'Sim is trying to delete an object id={finished_object} that it already deleted. Ignoring it.')
    print(f'There were {crashes} crashes.')
    print(f'The following objects crashed:\n{[obj.__str__() for obj in final_crashed]}')



if __name__ == "__main__":
    main()
