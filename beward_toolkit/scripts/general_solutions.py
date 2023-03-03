#!/usr/bin/python
# coding=utf8
from threading import Thread, active_count
from time import sleep


def threading_decorator(thread_num):
    def actual_decorator(func):
        """"""

        def wrapper(*args, **kwargs):

            for _ in range(thread_num):
                t = Thread(target=func, args=args, kwargs=kwargs)
                t = t.start()
            return t

        return wrapper

    return actual_decorator


def run_command_to_seqens(
    command,
    seqens,
    iteration_kwargs_names=(),
    thread_num=1,
):
    """Запускает команду для последовательности аргументов.
    Присутвует возможность запускать команду в несколько потоков.

    Args:
        command (Callable): комманда которую нужно запустить
        seqens (tuple): последовательность аргументов
        iteration_kwargs_names (tuple, optional): аргументы функции.
        thread_num (int, optional): количество потоков. По умолчанию 1.

    """
    general_output = []

    @threading_decorator(thread_num)
    def _run_command():
        while len(seqens) > 0:
            args = seqens.pop(0)
            if not hasattr(args, "__iter__") or isinstance(args, str):
                args = (args,)
            input = dict(zip(iteration_kwargs_names, args))
            try:
                output = command(**input)
            except Exception as err:
                output = (err, str(err))
            general_output.append((input, output))

    _run_command()
    while active_count() > 1:
        sleep(1)
    return general_output
