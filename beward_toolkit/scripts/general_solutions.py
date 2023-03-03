#!/usr/bin/python
# coding=utf8


def run_command_to_seqens(command, seqens, iteration_kwargs_names=()):
    """Запускает команду для последовательности аргументов

    Args:
        command (Callable): комманда которую нужно запустить
        seqens (tuple): последовательность аргументов
        iteration_kwargs_names (tuple, optional): . Defaults to ().
    """
    general_output = []
    for args in seqens:
        if not hasattr(args, "__iter__") or isinstance(args, str):
            args = (args,)
        input = dict(zip(iteration_kwargs_names, args))
        output = command(**input)
        general_output.append((input, output))
    return general_output
