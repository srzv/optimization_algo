import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from main import Stats
import main


@dataclass
class Plots:
    stat = Stats()

    def Rk_plot(self, path="/", img_size=500):
        """график изменения радиуса шара"""
        n_parall = [x for x in range(len(self.stat.R))]
        fig, ax = plt.subplots()
        ax.plot(n_parall, self.stat.R)
        ax.set_xlabel("номер итерации")
        ax.set_ylabel("R_k")
        ax.set_title("Изменение радиуса шара B_k")
        if path == "/":
            plt.show()
        else:
            plt.ioff()
            plt.savefig(path + "/Rk.png", dpi=img_size)

    def N_plot(self, path="/", img_size=500):
        """график изменения количества делений текущего параллелепипеда на 2, 4, 6"""
        n_iter = [x for x in range(len(self.stat.div_2))]
        fig, ax = plt.subplots()
        ax.plot(n_iter, self.stat.div_2, label="деление на 2", color="#1f77b4")
        ax.plot(
            n_iter,
            self.stat.div_6,
            label="деление на 4, 6",
            linestyle="dashdot",
            color="#1f77b4",
        )
        ax.set_xlabel("номер итерации")
        ax.set_ylabel("n")
        ax.set_title("Изменение количества вариационных делений параллелепипеда")
        ax.legend()
        if path == "/":
            plt.show()
        else:
            plt.ioff()
            plt.savefig(path + "/n2_6.png", dpi=img_size)

    def gamma_plot(gamma, n, path="/", img_size=500):
        """графики зависимости количества итераций от гамма"""
        plt.style.use("style.mplstyle")
        fig, ax = plt.subplots()
        ax.plot(gamma, n)
        ax.set_xlabel(r"$\gamma$")
        ax.set_ylabel("N")
        ax.set_title("График зависимости количества итераций N от $\gamma$", pad=30)
        ax.set_xlim(0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        if path == "/":
            plt.show()
        else:
            plt.ioff()
            plt.savefig(path + "/gamma.png", dpi=img_size)
