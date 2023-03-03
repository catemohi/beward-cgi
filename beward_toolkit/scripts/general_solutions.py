#!/usr/bin/python
# coding=utf8


def run_command_to_seqens(command, seqens, iteration_kwargs_names=()):
    """Запускает команду для последовательности аргументов

    Args:
        command (Callable): комманда которую нужно запустить
        seqens (tuple): последовательность аргументов
        iteration_kwargs_names (tuple, optional): . Defaults to ().
    """
    print(iteration_kwargs_names)
    print(seqens)
    for args in seqens:
        kwargs = dict(zip(iteration_kwargs_names, args))
        print(kwargs)
        command(**kwargs)
