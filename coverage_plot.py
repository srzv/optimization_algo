from vpython import *
import time


class Cov_plot:
    def __init__(self, centers, sizes):
        self.centers = centers
        self.sizes = sizes

    def draw(self):
        for i in range(len(self.centers)):
            box(
                pos=vector(*self.centers[i]),
                length=self.sizes[i][0],
                height=self.sizes[i][1],
                width=self.sizes[i][2],
                color=color.red,
                opacity=1,
            )
            time.sleep(6 / len(self.mas1))

    def scene(self, start, end):
        side = end - start
        center = start + (end - start) / 2
        scene = canvas(
            width=1000,
            height=800,
            center=vector(center, center, center),
            background=color.white,
        )
        starting_cube = box(
            pos=vector(center, center, center),
            length=side,
            height=side,
            width=side,
            opacity=0.1,
        )
        self.draw()
        # scene.bind("keydown", self.draw)
