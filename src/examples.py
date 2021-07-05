from abc import abstractmethod
from dataclasses import dataclass
import math


@dataclass
class Example:
    n: int
    start: float
    end: float

    @abstractmethod
    def f(self, x: float, y: float, z: float) -> float:
        pass

    @abstractmethod
    def L(self, delta: float):
        pass


class Example1(Example):
    start = -2
    end = 12

    def f(x: float, y: float, z: float) -> float:
        return -10 * math.exp(-math.sqrt(1 / 3 * (abs(x) + abs(y) + abs(z))))

    def L(delta: float):
        return 25 / (delta * math.sqrt(3))


class Example2(Example):
    start = -2
    end = 12

    def f(x: float, y: float, z: float) -> float:
        return -10 * math.exp(
            -math.sqrt(1 / 3 * (abs(x) + abs(y) + abs(z)))
        ) - math.exp(
            1
            / 3
            * (
                math.cos(2 * math.pi * x)
                + math.cos(2 * math.pi * y)
                + math.cos(2 * math.pi * z)
            )
        )

    def L(delta: float):
        return 25 / (delta * math.sqrt(3)) + 2 * math.pi * math.exp(1) / math.sqrt(3)


class Example3(Example):
    start = -10
    end = 10

    def f(x: float, y: float, z: float) -> float:
        return -abs(
            math.cos(x)
            * math.cos(y)
            * math.cos(z)
            * math.exp(1 / 3 * abs(1 - math.sqrt(abs(x) + abs(y) + abs(z))))
        )

    def L(delta: float):
        return 25 / (delta * math.sqrt(3)) + 2 * math.pi * math.exp(1) / math.sqrt(3)
