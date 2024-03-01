import time
import pygame
import constants

pygame.init()
import dataclasses


@dataclasses.dataclass
class Visual:
    color: tuple
    locations: list[tuple]


class Window:
    def __init__(self, global_objects_list):
        self.global_objects_list = global_objects_list
        self.screen = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

    def update(self, the_time):
        obj_visuals = self.global_objects_list.draw()
        self.screen.fill(constants.BACKGROUND)
        for obj in obj_visuals:
            pygame.draw.polygon(self.screen, obj.color,
                                obj.locations)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        pygame.display.flip()
        self.clock.tick(60)
        return True


'''if __name__ == "__main__":
    w = Window()
    running = True
    while running:
        time.sleep(0.02)
        running = w.update(0)
    pygame.quit()'''
