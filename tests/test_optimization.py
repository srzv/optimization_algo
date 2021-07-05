from ..src import examples
from ..src.algo import Parall_processing
import pytest


def pytest_generate_tests(metafunc):
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )


class Test_for_algo:
    params = {
        "test_for_f1": [{"eps": 0.1}, {"eps": 0.5}],
        "test_for_f2": [{"eps": 0.1}, {"eps": 0.5}],
    }

    def test_for_f1(self, eps):
        gamma = 0.1
        answer1 = -10
        answer2 = Parall_processing(
            examples.Example1.f,
            examples.Example1.L,
            eps,
            examples.Example1.start,
            examples.Example1.end,
            gamma,
        ).covering_loop()
        assert answer1 - eps <= answer2.min_f <= answer1 + eps

    def test_for_f2(self, eps):
        gamma = 0.1
        answer1 = -12.71828
        answer2 = Parall_processing(
            examples.Example2.f,
            examples.Example2.L,
            eps,
            examples.Example2.start,
            examples.Example2.end,
            gamma,
        ).covering_loop()
        assert answer1 - eps <= answer2.min_f <= answer1 + eps
