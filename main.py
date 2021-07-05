"""Модуль взимодействия с пользователем"""
import os
import math
import time
import click
from rich.console import Console
from src.coverage_plot import Cov_plot
from src.plots import Plots
import src.examples as examples
from src.algo import Parall_processing

TIME = time.strftime("%d.%m.%y_%H:%M:%S")
# расположение сохраненных графиков
PARENT_DIR = "plots/"
console = Console()


@click.command()
@click.option("--n", default=1, help="Номер примера")
@click.option("--eps", default=0.1, help="Точность вычислений")
@click.option("--plot", is_flag=True, help="Построить графики")
@click.option("--vis3d", is_flag=True, help="Трехмерная визуализация покрытия")
@click.option("--half", is_flag=True, help="Использование метода половинного деления")
@click.option("--gamma", default=0.01, help="Изменить гамму")
def user_input(n, eps, plot, vis3d, half, gamma):
    """обработка аргументов передаваемых программе"""
    st_time = time.perf_counter()
    if half:
        gamma = math.inf
    if n == 1:
        stats = Parall_processing(
            examples.Example1.f,
            examples.Example1.L,
            eps,
            examples.Example1.start,
            examples.Example1.end,
            gamma,
        ).covering_loop()
        start = examples.Example1.start
        end = examples.Example1.end
    if n == 2:
        stats = Parall_processing(
            examples.Example2.f,
            examples.Example2.L,
            eps,
            examples.Example2.start,
            examples.Example2.end,
            gamma,
        ).covering_loop()
        start = examples.Example2.start
        end = examples.Example2.end
    if n == 3:
        stats = Parall_processing(
            examples.Example3.f,
            examples.Example3.L,
            eps,
            examples.Example3.start,
            examples.Example3.end,
            gamma,
        ).covering_loop()
        start = examples.Example3.start
        end = examples.Example3.end
    end_time = time.perf_counter()
    console.rule("")
    console.print(f"Функции номер {n}", style="bold red")
    console.print(f"Минимальное значение функции {stats.min_f}", style="bold red")
    console.print(f"Точность ", eps, style="bold red")
    console.print(f"Коэффициент дробления {gamma}", style="bold red")
    console.print(f"Значение x в этой точке {stats.min_x[0]}", style="bold red")
    console.print(f"Значение y в этой точке {stats.min_x[1]}", style="bold red")
    console.print(f"Значение z в этой точке {stats.min_x[2]}", style="bold red")
    console.print(f"Найдено на итерации {stats.min_n} из {stats.n}", style="bold red")
    console.print(f"Количество делений на 2 {stats.fragm2}", style="bold red")
    console.print(f"Количество делений на 4 {stats.fragm4}", style="bold red")
    console.print(f"Количество делений на 6 {stats.fragm6}", style="bold red")
    console.print(f"Затраченное время {end_time - st_time}", style="bold red")
    if plot:
        path = PARENT_DIR + "function_" + str(n) + "_" + TIME
        try:
            os.mkdir(path)
        except OSError as error:
            print(error)
        plots = Plots(stats)
        plots.Rk_plot()
        plots.N_plot()
    if vis3d:
        coverage = Cov_plot(stats.cov_center, stats.cov_size)
        coverage.scene(start, end)


if __name__ == "__main__":
    user_input()
