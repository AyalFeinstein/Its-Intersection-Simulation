from objects import GlobalObjectList
import logging

logging.getLogger('DetectorLogging')


class Detector:

    def __init__(self,
                 global_objects_list: GlobalObjectList):

        self._global_objects_list = global_objects_list

    def detect_crashes(self) -> list[int]:
        """ Return a list of crashed objects
        each crash is represented as a tuple of the object ids involved
        """
        crashes = set()
        for i in self._global_objects_list.values():
            for j in self._global_objects_list.values():
                if i is j:
                    continue
                i_rear_x, i_rear_y = i.my_vehicle.get_rear()
                j_rear_x, j_rear_y = j.my_vehicle.get_rear()

                if i.my_vehicle.angle == j.my_vehicle.angle:
                    if ((i.my_vehicle.x <= j.my_vehicle.x <= i_rear_x
                         and i.my_vehicle.y <= j.my_vehicle.y <= i_rear_y)
                            or (i.my_vehicle.x <= j_rear_x <= i_rear_x
                                and i.my_vehicle.y <= j_rear_y <= i_rear_y)
                            or (i_rear_x <= j.my_vehicle.x <= i.my_vehicle.x
                                and i_rear_y <= j.my_vehicle.y <= i.my_vehicle.y)
                            or (j_rear_x <= i.my_vehicle.x <= j.my_vehicle.x
                                and j_rear_y <= i.my_vehicle.y <= j.my_vehicle.y)
                            or (i.my_vehicle.x >= j.my_vehicle.x >= i_rear_x
                                and i.my_vehicle.y >= j.my_vehicle.y >= i_rear_y)
                            or (i.my_vehicle.x >= j_rear_x >= i_rear_x
                                and i.my_vehicle.y >= j_rear_y >= i_rear_y)
                            or (i_rear_x >= j.my_vehicle.x >= i.my_vehicle.x
                                and i_rear_y >= j.my_vehicle.y >= i.my_vehicle.y)
                            or (j_rear_x >= i.my_vehicle.x >= j.my_vehicle.x
                                and j_rear_y >= i.my_vehicle.y >= j.my_vehicle.y)):

                        crashes.add(i.object_id)
                        crashes.add(j.object_id)
                elif i.my_vehicle.angle % 180 == 0 and j.my_vehicle.angle % 180 == 90:
                    i_max_x = max(i.my_vehicle.x, i_rear_x)
                    i_min_x = min(i.my_vehicle.x, i_rear_x)
                    i_y = i.my_vehicle.y

                    j_max_y = max(j.my_vehicle.y, j_rear_y)
                    j_min_y = min(j.my_vehicle.y, j_rear_y)
                    j_x = j.my_vehicle.x
                    if (i_min_x <= j_x <= i_max_x
                    and j_min_y <= i_y <= j_max_y):
                        crashes.add(i.object_id)
                        crashes.add(j.object_id)
                        logging.info(f'crashed id loc 1={i.my_vehicle.x, i.my_vehicle.y}, loc 1 rear={i_rear_x, i_rear_y}, loc 2={j.my_vehicle.x, j.my_vehicle.y}, loc 2 rear={j_rear_x, j_rear_y}.')

        return list(crashes)

    def detect_end(self, road_length):
        cleared_objects = []
        for driver in self._global_objects_list.values():
            if driver.my_vehicle.x > road_length/2 or driver.my_vehicle.y > road_length/2:
                cleared_objects.append(driver.object_id)
        return cleared_objects

# print(Detector([Driver(0, Vehicle(2, 1, 1, 7), 2, (4, 4), None, 0), Driver(1, Vehicle(2, 1, 1, 1), 2, (4, 4), None, 0)]).act())
