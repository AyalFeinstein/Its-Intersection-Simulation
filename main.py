import time
from signal import TrafficLight, TrafficLightColor, TrafficHead
from collision_detector import Detector
from lane import Lane
from generator import Generator
from objects import GlobalObjectList
from settings import Settings
import sys
import logging
from math import floor
from road import Road
from visuals import Window
from constants import ROUNDING
import pygame
pygame.init()


def main():
    """ To run: main settings_file """
    throughput = 0
    throughput_out = 0
    final_crashed = []
    final_crashed_ids = []
    average_speed = 0

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

    # init the traffic light
    if "traffic_light" in my_settings.get('intersection', {}):
        light_settings = my_settings['intersection']['traffic_light']
        roads = global_objects_list.get_roads()
        colors = [TrafficLightColor.GREEN, TrafficLightColor.RED]
        initial_colors = {
            rd: colors[i]
            for i, rd in enumerate(roads)
        }
        heads = []
        for lane in global_objects_list.get_lanes():
            other_road = [rd for rd in roads if rd is not lane.road]
            position = other_road[0].get_width(global_objects_list)/2 if other_road else 0
            heads.append(TrafficHead(position, lane, initial_colors[lane.road]))
        light = TrafficLight(light_settings['cycle_time'], light_settings['yellow_time'], heads)
        global_objects_list.add_light(light)
    # run the time loop
    total_timesteps = my_settings["simulation_timesteps"]
    timestep_length = my_settings["timestep"]

    detector = Detector(global_objects_list)
    lanes: list[Lane] = global_objects_list.get_lanes()
    debug = my_settings['loglevel']
    logging.getLogger().setLevel(debug)
    window = Window(global_objects_list)
    break_length = my_settings['simulation_speed']

    for loop in range(total_timesteps):
        time.sleep(break_length)
        all_visuals = global_objects_list.draw()
        for visual in all_visuals:
            pygame.draw.polygon(window.screen, visual.color, visual.locations)
        the_time = loop * timestep_length
        window.update(the_time)
        logging.info(f"Starting loop={loop}/{total_timesteps} time={the_time}s")

        # generate objects
        for this_lane in lanes:
            road_speed_limit = this_lane.get_speed_limit()
            x0, y0 = this_lane.get_position(0)
            # this_lane.update(the_time)
            should_generate = this_lane.generator.should_generate(the_time, this_lane)
            if should_generate:
                endx, endy = this_lane.get_position(1)
                new_driver = this_lane.generator.generate(x0, y0, my_settings['visibility'], endx, endy, road_speed_limit, my_settings)
                global_objects_list[new_driver.object_id] = new_driver
                this_lane.add(new_driver.object_id)
                logging.info(f"Generating a vehicle={new_driver.object_id} in lane={this_lane} position=({x0}, {y0}), destination=({endx}, {endy}) of type {new_driver.my_vehicle}")
                throughput += 1

        # plan next steps
        for this_driver in global_objects_list.values():
            for lane in lanes:
                if this_driver in lane.get_objects():
                    road_speed_limit = lane.get_speed_limit()
                    if this_driver.should_plan():
                        visible_objects = this_driver.look(global_objects_list)
                        accel_change = this_driver.plan(visible_objects, road_speed_limit, timestep_length, lane, traffic_light=global_objects_list.get_light())
                        this_driver.accelerate(accel_change)
                        logging.debug(f"{this_driver.object_id=} acceleration ={this_driver.my_vehicle.acceleration}")

        # updating the map
        global_objects_list.get_light().update(the_time)

        for this_driver in global_objects_list.values():
            this_driver.my_vehicle.update(timestep_length)
            logging.info(f"Updating {this_driver}")

        # detect crashes
        crashed_ids = detector.detect_crashes()
        crashes += floor(len(crashed_ids)/2)
        if crashed_ids:
            logging.info(f'Objects {crashed_ids} crashed.\n {[global_objects_list[crashed_id] for crashed_id in crashed_ids]}')
        logging.info(f'crashed_ids={crashed_ids}')

        final_crashed_ids += crashed_ids
        final_crashed.extend(global_objects_list[crashed_id] for crashed_id in crashed_ids)

        finished_ids = crashed_ids.copy()
        # remove objects that crashed or move off the board
        for lane in lanes:
            finished_ids += lane.detect_end()
        logging.info(f'finished_ids={finished_ids}')
        # remove objects that move off the board
        for finished_object in finished_ids:
            if finished_object in global_objects_list:
                the_object = global_objects_list[finished_object]

                logging.info(f"Object {finished_object} being removed with a length of {the_object.my_vehicle.length} with location ({the_object.my_vehicle.x, the_object.my_vehicle.y}).")
                for lane in global_objects_list.get_lanes():
                    lane.remove(finished_object)
                average_speed += the_object.my_vehicle.average_speed()
                del global_objects_list[finished_object]
                throughput_out += 1
            else:
                logging.warning(f'Sim is trying to delete an object id={finished_object} that it already deleted. Ignoring it.')
        throughput_out += len(finished_ids)-len(crashed_ids)
    for obj in global_objects_list.values():
        average_speed += obj.my_vehicle.average_speed()
    average_speed = round(average_speed / throughput, ROUNDING)
    crashed_drivers_string = "\n".join(str(f) for f in final_crashed)
    print(f'There were {crashes} crashes.')
    print(f'The following objects crashed:\n{crashed_drivers_string}')
    print(f'{round(throughput/(total_timesteps*timestep_length), ROUNDING)} cars per second \n{round(throughput_out/(total_timesteps*timestep_length), ROUNDING)} cars out per second \n{average_speed=} meters per second')


if __name__ == "__main__":
    main()
