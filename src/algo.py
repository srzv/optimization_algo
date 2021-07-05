import math
import bisect
from functools import cached_property
from dataclasses import dataclass, field
from collections.abc import Callable
from rich.console import Console


@dataclass
class BaseParall:
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float

    @cached_property
    def a(self) -> float:
        return self.side(self.x1, self.x2)

    @cached_property
    def b(self) -> float:
        return self.side(self.y1, self.y2)

    @cached_property
    def c(self) -> float:
        return self.side(self.z1, self.z2)

    def side(self, start, end):
        return abs(end - start)


@dataclass
class Parall(BaseParall):
    f: float

    def __init__(
        self,
        x1: float,
        y1: float,
        z1: float,
        x2: float,
        y2: float,
        z2: float,
        f: Callable,
    ):
        super().__init__(x1, y1, z1, x2, y2, z2)
        self.f = f(self.c_x, self.c_y, self.c_z)

    def center(self, start, end) -> float:
        return start + (end - start) / 2

    @cached_property
    def c_x(self) -> float:
        return self.center(self.x1, self.x2)

    @cached_property
    def c_y(self) -> float:
        return self.center(self.y1, self.y2)

    @cached_property
    def c_z(self) -> float:
        return self.center(self.z1, self.z2)

    def __lt__(self, p):
        return self.f < p.f


@dataclass
class Stats:
    n: int = -1
    fragm2: int = 0
    fragm4: int = 0
    fragm6: int = 0
    R: list = field(default_factory=list)
    min_n: int = -1
    min_f: float = -1
    min_x: list = field(default_factory=list)
    div_2: list = field(default_factory=list)
    div_6: list = field(default_factory=list)
    cov_center: list = field(default_factory=list)
    cov_size: list = field(default_factory=list)


class Parall_processing:
    def __init__(self, f, L, eps, start=-2, end=12, gamma=0.03):
        self.f = f
        self.L = L
        self.eps = eps
        self.r = 0
        self.F = []
        self.p_list = []
        self.f_k = 0
        self.F_k = 0
        self.limit = 100000
        self.start = start
        self.end = end
        self.gamma = gamma
        self.stat = Stats()

    @cached_property
    def A(self):
        return math.sqrt(2) / 2 * (self.end - self.start) * self.gamma

    def find_one_side(self, r, a, b):
        return math.sqrt(r ** 2 - (a / 2) ** 2 - (b / 2) ** 2)

    def find_two_sides(self, r, a):
        return math.sqrt(2) / 2 * math.sqrt(r ** 2 - (a / 2) ** 2)

    def old_R_k(self):
        delta = 0
        final_delta = 0
        result = 0
        final_result = -math.inf
        delta_max = self.f_k - self.F_k + self.eps
        h = delta_max / 5
        delta += h
        while delta <= delta_max:
            prev_result = result
            result = self.R2(delta)
            if result > final_result:
                final_result = result
                final_delta = delta
            delta = delta + h
        return final_result

    def R1(self, delta):
        return -(self.f_k - self.F_k + self.eps - delta) / self.L(delta)

    def R2(self, delta):
        return (self.f_k - self.F_k + self.eps - delta) / self.L(delta)

    def inscribed_parall(self, p: Parall):
        # добавляем текущее значение функции в список значений функций
        bisect.insort(self.F, p.f)
        # радиус шара
        self.f_k = p.f
        self.F_k = self.F[0]
        # итерация, на которой найдено минимальное значение функции
        if self.F_k == self.f_k:
            self.stat.min_f = self.f_k
            self.stat.min_n = self.stat.n
            self.stat.min_x = [p.c_x, p.c_y, p.c_z]
        self.r = self.old_R_k()
        self.stat.R.append(self.r)
        self.stat.n += 1
        # вписанный параллелепипед
        b = BaseParall(0, 0, 0, 0, 0, 0)
        # неизвестная сторона
        side = 0
        # сторона куба
        cube = 2 * self.r / math.sqrt(3)
        # определяем полностью ли находится текущий паралелеппепед внутри шара
        if (
            p.c_x + self.r / math.sqrt(3) >= p.x2
            and p.c_y + self.r / math.sqrt(3) >= p.y2
            and p.c_z + self.r / math.sqrt(3) >= p.z2
        ):
            self.stat.cov_size.append([p.a, p.b, p.c])
            self.stat.cov_center.append([p.c_x, p.c_y, p.c_z])
            return 0
        # учитывается вариант, когда текущий параллелепипед вытянутой формы
        elif (
            (pow(self.r, 2) >= pow(p.a / 2, 2) + pow(p.b / 2, 2) + pow(p.c / 2, 2))
            and p.x2 < p.c_x + self.r
            and p.y2 < p.c_y + self.r
            and p.z2 < p.c_z + self.r
        ):
            self.stat.cov_size.append([p.a, p.b, p.c])
            self.stat.cov_center.append([p.c_x, p.c_y, p.c_z])
            return 0
        # имеется ли воможность вписать куб в шар
        elif (
            p.c_x + self.r / math.sqrt(3) < p.x2
            and p.c_y + self.r / math.sqrt(3) < p.y2
            and p.c_z + self.r / math.sqrt(3) < p.z2
        ):
            # нижняя левая вершина
            b.x1 = p.c_x - self.r / math.sqrt(3)
            b.y1 = p.c_y - self.r / math.sqrt(3)
            b.z1 = p.c_z - self.r / math.sqrt(3)
            # верхняя правая вершина
            b.x2 = p.c_x + self.r / math.sqrt(3)
            b.y2 = p.c_y + self.r / math.sqrt(3)
            b.z2 = p.c_z + self.r / math.sqrt(3)
        # определяем пары сторон, не позовляющих вписать куб
        elif p.a < cube and p.b < cube:
            side = self.find_one_side(self.r, p.a, p.b)
            # нижняя левая вершина
            b.x1 = p.x1
            b.y1 = p.y1
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.c < 2 * side:
                b.z1 = p.z1
            else:
                b.z1 = p.c_z - side
            # верхняя правая вершина
            b.x2 = p.x2
            b.y2 = p.y2
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.c < 2 * side:
                b.z2 = p.z2
            else:
                b.z2 = p.c_z + side
        elif p.a < cube and p.c < cube:
            side = self.find_one_side(self.r, p.a, p.c)
            # нижняя левая вершина
            b.x1 = p.x1
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.b < 2 * side:
                b.y1 = p.y1
            else:
                b.y1 = p.c_y - side
            b.z1 = p.z1
            # верхняя правая вершина
            b.x2 = p.x2
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.b < 2 * side:
                b.y2 = p.y2
            else:
                b.y2 = p.c_y + side
            b.z2 = p.z2

        elif p.b < cube and p.c < cube:
            side = self.find_one_side(self.r, p.b, p.c)
            # нижняя левая вершина
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.a < 2 * side:
                b.x1 = p.x1
            else:
                b.x1 = p.c_x - side
            b.y1 = p.y1
            b.z1 = p.z1
            # верхняя правая вершина
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.a < 2 * side:
                b.x2 = p.x2
            else:
                b.x2 = p.c_x + side
            b.y2 = p.y2
            b.z2 = p.z2

        # определяем сторону, не позовляющую вписать куб
        elif p.a < cube:
            side = self.find_two_sides(self.r, p.a)
            # нижняя левая вершина
            b.x1 = p.x1
            # верхняя правая вершина
            b.x2 = p.x2
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.b < 2 * side or p.c < 2 * side:
                if p.b < p.c:
                    b.y1 = p.y1
                    b.z1 = p.c_z - p.b / 2
                    b.y2 = p.y2
                    b.z2 = p.c_z + p.b / 2
                else:
                    b.y1 = p.c_y - p.c / 2
                    b.z1 = p.z1
                    b.y2 = p.c_y + p.c / 2
                    b.z2 = p.z2
            else:
                b.y1 = p.c_y - side
                b.z1 = p.c_z - side
                b.y2 = p.c_y + side
                b.z2 = p.c_z + side

        elif p.b < cube:
            side = self.find_two_sides(self.r, p.b)
            # нижняя левая вершина
            b.y1 = p.y1
            # верхняя правая вершина
            b.y2 = p.y2
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.a < 2 * side or p.c < 2 * side:
                if p.a < p.c:
                    b.x1 = p.x1
                    b.z1 = p.c_z - p.a / 2
                    b.x2 = p.x2
                    b.z2 = p.c_z + p.a / 2
                else:
                    b.x1 = p.c_x - p.c / 2
                    b.z1 = p.z1
                    b.x2 = p.c_x + p.c / 2
                    b.z2 = p.z2
            else:
                b.x1 = p.c_x - side
                b.z1 = p.c_z - side
                b.x2 = p.c_x + side
                b.z2 = p.c_z + side

        elif p.c < cube:
            side = self.find_two_sides(self.r, p.c)
            # нижняя левая вершина
            b.z1 = p.z1
            # верхняя правая вершина
            b.z2 = p.z2
            # если полученное ребро оказалось больше соответствующего ребра текущего параллелепипеда
            if p.a < 2 * side or p.b < 2 * side:
                if p.a < p.b:
                    b.x1 = p.x1
                    b.y1 = p.c_y - p.a / 2
                    b.x2 = p.x2
                    b.y2 = p.c_y + p.a / 2
                else:
                    b.x1 = p.c_x - p.b / 2
                    b.y1 = p.y1
                    b.x2 = p.c_x + p.b / 2
                    b.y2 = p.y2
            else:
                b.x1 = p.c_x - side
                b.y1 = p.c_y - side
                b.x2 = p.c_x + side
                b.y2 = p.c_y + side
        self.stat.cov_size.append([b.a, b.b, b.c])
        self.stat.cov_center.append(
            [
                b.x1 + (b.x2 - b.x1) / 2,
                b.y1 + (b.y2 - b.y1) / 2,
                b.z1 + (b.z2 - b.z1) / 2,
            ]
        )
        self.fragmentation(p, b)

    def fragmentation(self, p, b):
        if self.r <= self.A:
            self.stat.fragm2 += 1
            # если наибольшие грани параллельны оси Ox
            if p.a >= p.b and p.a >= p.c:
                # спереди
                bisect.insort(
                    self.p_list, Parall(p.c_x, p.y1, p.z1, p.x2, p.y2, p.z2, self.f)
                )
                # сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, p.c_x, p.y2, p.z2, self.f)
                )
            # если наибольшие грани параллельны оси Oy
            elif p.b >= p.a and p.b >= p.c:
                # слева
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, p.c_y, p.z2, self.f)
                )
                # справа
                bisect.insort(
                    self.p_list, Parall(p.x1, p.c_y, p.z1, p.x2, p.y2, p.z2, self.f)
                )
            # если наибольшие грани параллельны оси Oz
            else:
                # сверху
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.c_z, p.x2, p.y2, p.z2, self.f)
                )
                # снизу
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, p.y2, p.c_z, self.f)
                )
        # если совпали два ребра
        elif p.x2 == b.x2 and p.y2 == b.y2:
            self.stat.fragm2 += 1
            # снизу
            bisect.insort(
                self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, p.y2, b.z1, self.f)
            )
            # сверху
            bisect.insort(
                self.p_list, Parall(p.x1, p.y1, b.z2, p.x2, p.y2, p.z2, self.f)
            )
        elif p.x2 == b.x2 and p.z2 == b.z2:
            self.stat.fragm2 += 1
            # слева
            bisect.insort(
                self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, b.y1, p.z2, self.f)
            )
            # справа
            bisect.insort(
                self.p_list, Parall(p.x1, b.y2, p.z1, p.x2, p.y2, p.z2, self.f)
            )
        elif p.y2 == b.y2 and p.z2 == b.z2:
            self.stat.fragm2 += 1
            # спереди
            bisect.insort(
                self.p_list, Parall(b.x2, p.y1, p.z1, p.x2, p.y2, p.z2, self.f)
            )
            # сзади
            bisect.insort(
                self.p_list, Parall(p.x1, p.y1, p.z1, b.x1, p.y2, p.z2, self.f)
            )
        # если совпало одно ребро
        elif p.x2 == b.x2:
            self.stat.fragm4 += 1
            # определяем наибольшее ребро
            if p.b >= p.c:
                # слева
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, b.y1, p.z2, self.f)
                )
                # справа
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y2, p.z1, p.x2, p.y2, p.z2, self.f)
                )
                # сверху
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y1, b.z2, p.x2, b.y2, p.z2, self.f)
                )
                # снизу
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y1, p.z1, p.x2, b.y2, b.z1, self.f)
                )
            else:
                # сверху
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, b.z2, p.x2, p.y2, p.z2, self.f)
                )
                # снизу
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, p.y2, b.z1, self.f)
                )
                # слева
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, b.z1, p.x2, b.y1, b.z2, self.f)
                )
                # справа
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y2, b.z1, p.x2, p.y2, b.z2, self.f)
                )
        elif p.y2 == b.y2:
            self.stat.fragm4 += 1
            if p.a >= p.c:
                # сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, b.x1, p.y2, p.z2, self.f)
                )
                # спереди
                bisect.insort(
                    self.p_list, Parall(b.x2, p.y1, p.z1, p.x2, p.y2, p.z2, self.f)
                )
                # по центру сверху
                bisect.insort(
                    self.p_list, Parall(b.x1, p.y1, b.z2, b.x2, p.y2, p.z2, self.f)
                )
                # по центру снизу
                bisect.insort(
                    self.p_list, Parall(b.x1, p.y1, p.z1, b.x2, p.y2, b.z1, self.f)
                )
            else:
                # сверху
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, b.z2, p.x2, p.y2, p.z2, self.f)
                )
                # снизу
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, p.y2, b.z1, self.f)
                )
                # сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, b.z1, b.x1, p.y2, b.z2, self.f)
                )
                # спереди
                bisect.insort(
                    self.p_list, Parall(b.x2, p.y1, b.z1, p.x2, p.y2, b.z2, self.f)
                )
        elif p.z2 == b.z2:
            self.stat.fragm4 += 1
            if p.a >= p.b:
                # сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, b.x1, p.y2, p.z2, self.f)
                )
                # спереди
                bisect.insort(
                    self.p_list, Parall(b.x2, p.y1, p.z1, p.x2, p.y2, p.z2, self.f)
                )
                # по центру слева
                bisect.insort(
                    self.p_list, Parall(b.x1, p.y1, p.z1, b.x2, b.y1, p.z2, self.f)
                )
                # по центру справа
                bisect.insort(
                    self.p_list, Parall(b.x1, b.y2, p.z1, b.x2, p.y2, p.z2, self.f)
                )
            else:
                # слева
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, b.y1, p.z2, self.f)
                )
                # справа
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y2, p.z1, p.x2, p.y2, p.z2, self.f)
                )
                # по центру спереди
                bisect.insort(
                    self.p_list, Parall(b.x2, b.y1, p.z1, p.x2, b.y2, p.z2, self.f)
                )
                # по центру сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y1, p.z1, b.x1, b.y2, p.z2, self.f)
                )
        # если не совпало ни одно ребро
        # определяем наибольшее и следующее за наибольшим
        elif p.a >= p.b and p.a >= p.c:
            self.stat.fragm6 += 1
            # спереди
            bisect.insort(
                self.p_list, Parall(b.x2, p.y1, p.z1, p.x2, p.y2, p.z2, self.f)
            )
            # сзади
            bisect.insort(
                self.p_list, Parall(p.x1, p.y1, p.z1, b.x1, p.y2, p.z2, self.f)
            )
            if p.b >= p.c:
                # по центру слева
                bisect.insort(
                    self.p_list, Parall(b.x1, p.y1, p.z1, b.x2, b.y1, p.z2, self.f)
                )
                # по центру справа
                bisect.insort(
                    self.p_list, Parall(b.x1, b.y2, p.z1, b.x2, p.y2, p.z2, self.f)
                )
                # по центру снизу
                bisect.insort(
                    self.p_list, Parall(b.x1, b.y1, p.z1, b.x2, b.y2, b.z1, self.f)
                )
                # по центру сверху
                bisect.insort(
                    self.p_list, Parall(b.x1, b.y1, b.z2, b.x2, b.y2, p.z2, self.f)
                )
            else:
                # по центру снизу
                bisect.insort(
                    self.p_list, Parall(b.x1, p.y1, p.z1, b.x2, p.y2, b.z1, self.f)
                )
                # по центру сверху
                bisect.insort(
                    self.p_list, Parall(b.x1, p.y1, b.z2, b.x2, p.y2, p.z2, self.f)
                )
                # по центру слева
                bisect.insort(
                    self.p_list, Parall(b.x1, p.y1, b.z1, b.x2, b.y1, b.z2, self.f)
                )
                # по центру справа
                bisect.insort(
                    self.p_list, Parall(b.x1, b.y2, b.z1, b.x2, p.y2, b.z2, self.f)
                )
        elif p.b > p.a and p.b >= p.c:
            self.stat.fragm6 += 1
            # слева
            bisect.insort(
                self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, b.y1, p.z2, self.f)
            )
            # справа
            bisect.insort(
                self.p_list, Parall(p.x1, b.y2, p.z1, p.x2, p.y2, p.z2, self.f)
            )
            if p.a >= p.c:
                # по центру спереди
                bisect.insort(
                    self.p_list, Parall(b.x2, b.y1, p.z1, p.x2, b.y2, p.z2, self.f)
                )
                # по центру сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y1, p.z1, b.x1, b.y2, p.z2, self.f)
                )
                # по центру сверху
                bisect.insort(
                    self.p_list, Parall(b.x1, b.y1, b.z2, b.x2, b.y2, p.z2, self.f)
                )
                # по центру снизу
                bisect.insort(
                    self.p_list, Parall(b.x1, b.y1, p.z1, b.x2, b.y2, b.z1, self.f)
                )
            else:
                # по центру сверху
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y1, b.z2, p.x2, b.y2, p.z2, self.f)
                )
                # по центру снизу
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y1, p.z1, p.x2, b.y2, b.z1, self.f)
                )
                # по центру спереди
                bisect.insort(
                    self.p_list, Parall(b.x2, b.y1, b.z1, p.x2, b.y2, b.z2, self.f)
                )
                # по центру сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y1, b.z1, b.x1, b.y2, b.z2, self.f)
                )
        elif p.c > p.a and p.c > p.b:
            self.stat.fragm6 += 1
            # снизу
            bisect.insort(
                self.p_list, Parall(p.x1, p.y1, p.z1, p.x2, p.y2, b.z1, self.f)
            )
            # сверху
            bisect.insort(
                self.p_list, Parall(p.x1, p.y1, b.z2, p.x2, p.y2, p.z2, self.f)
            )
            if p.a >= p.b:
                # по центру спереди
                bisect.insort(
                    self.p_list, Parall(b.x2, p.y1, b.z1, p.x2, p.y2, b.z2, self.f)
                )
                # по центру сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, b.z1, b.x1, p.y2, b.z2, self.f)
                )
                # по центру слева
                bisect.insort(
                    self.p_list, Parall(b.x1, p.y1, b.z1, b.x2, b.y1, b.z2, self.f)
                )
                # по центру справа
                bisect.insort(
                    self.p_list, Parall(b.x1, b.y2, b.z1, b.x2, p.y2, b.z2, self.f)
                )
            else:
                # слева
                bisect.insort(
                    self.p_list, Parall(p.x1, p.y1, b.z1, p.x2, b.y1, b.z2, self.f)
                )
                # справа
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y2, b.z1, p.x2, p.y2, b.z2, self.f)
                )
                # по центру спереди
                bisect.insort(
                    self.p_list, Parall(b.x2, b.y1, b.z1, p.x2, b.y2, b.z2, self.f)
                )
                # по центру сзади
                bisect.insort(
                    self.p_list, Parall(p.x1, b.y1, b.z1, b.x1, b.y2, b.z2, self.f)
                )

    def covering_loop(self):
        self.inscribed_parall(
            Parall(
                self.start, self.start, self.start, self.end, self.end, self.end, self.f
            )
        )
        for i in range(self.limit):
            try:
                self.inscribed_parall(self.p_list.pop(0))
            except IndexError as error:
                # Исходный параллелепипед покрыт
                return self.stat
