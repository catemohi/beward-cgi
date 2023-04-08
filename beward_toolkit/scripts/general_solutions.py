#!/usr/bin/python
# coding=utf8
import os
from re import findall, match
from csv import DictReader
from platform import system
from subprocess import DEVNULL, call
from threading import Thread, active_count
from time import sleep, time
from pathlib import Path
from sys import path
from zipfile import ZipFile

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.settings import HOSTS


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
    seqens = list(seqens)

    @threading_decorator(thread_num)
    def _run_command():
        while len(seqens) > 0:
            args = seqens.pop(0)
            if not hasattr(args, "__iter__") or isinstance(args, str):
                args = (args,)
            input_args = dict(zip(iteration_kwargs_names, args))

            try:
                output = command(**input_args)
            except Exception as err:
                print("Error %s for input %s" % (str(err), input_args))
                output = {"Error": str(err)}
            general_output.append((input_args, output))

    _run_command()
    while active_count() > 1:
        sleep(1)
    return general_output


def ping(host):
    """
    Функция проверяет доступность удаленного устройства.

    Args:
        host: устройство для проверки.
    Returns True если устройство доступено, иначе False.
    """
    param = "-n" if system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    return call(command, stdout=DEVNULL) == 0


def get_reachable_hosts():
    """Получение списка доступных устройств."""
    reachable_hosts = []
    hosts = HOSTS[:]

    @threading_decorator(700)
    def _run_command():
        while len(hosts) > 0:
            ip = hosts.pop(0)
            ip = str(ip)
            if ping(ip):
                reachable_hosts.append(ip)

    _run_command()
    while active_count() > 1:
        sleep(1)
    return reachable_hosts


def get_cmd_window_size():
    """Функция для получения размера окна терминала windows.
    """
    from ctypes import windll, create_string_buffer
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = \
            struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
    else:
        sizex, sizey = 80, 25
    return int(sizex), int(sizey)


def get_tty_linux_size():
    """Функция для получения размера окна терминала linux.
    """
    sizex, sizey = os.popen('stty size', 'r').read().split()
    return int(sizex), int(sizey)


def get_terminal_size():
    """Получение размера окна терминала.
    """
    try:
        sizex, sizey = os.get_terminal_size()
    except:
        if system().lower() == "windows":
            sizex, sizey = get_cmd_window_size()
        elif system().lower() == "linux":
            sizex, sizey = get_tty_linux_size()
        else:
            # default
            sizex, sizey = 80, 25
    return sizex, sizey


def validate_csvfile(csv_file):
    """Валидация файла CSV.

    Args:
        csv_file (str): путь к файлу CSV.
    """
    valid_fieldnames = ['IP', 'Name']
    if not os.path.isfile(csv_file):
        raise FileNotFoundError("File not found: %s" % csv_file)
    with open(csv_file, "r", encoding="utf-8") as csv_file:
        csv_dict = DictReader(csv_file, delimiter=";")
        if csv_dict.fieldnames != valid_fieldnames:
            raise ValueError("CSV fieldnames must be {}".format(valid_fieldnames))
        return list(csv_dict)


def validate_string_line(string):
    """Валидация строки с адресами

    Args:
        string (str): строка с адресами
    """
    ip_regx = r"(?:(?:\d{1,3}\.){3}\d{1,3}){1,}"
    hosts = findall(ip_regx, string)
    if not hosts:
        raise ValueError("IP address not found in string: %s" % string)
    return hosts


def get_gmc_id(title):
    """Получение идентификатора GMC.

    Args:
        title (str): название RTSP потока
    """
    gmc_id_regx = r"(?:\w{2,}\d{2,}\-\d{4,})\s?"
    matched_str = match(gmc_id_regx, title)
    if matched_str is not None:
        return matched_str[0]
    return ""


def create_zip(name="", zip_path=".", files_path_collection=(), remove_files=False):
    """
    Функция создает архив .zip из набора файлов.

    Args:
        name (str): название архива. Если не указано, будет создано автоматически.
        zip_path (str): путь для сохранения архива. По умолчанию - текущая директория.
        files_path_collection (tuple): коллекция путей к файлам, которые нужно заархивировать.
        remove_files (bool): флаг, указывающий, нужно ли удалять исходные файлы после создания архива.

    Returns:
        tuple: кортеж из флага результата операции и пути к архиву типа Path.

    Raises:
        ValueError: если не передана коллекция файлов.
    """

    if not files_path_collection:
        raise ValueError("Необходимо передать коллекцию файлов.")

    format_name = "{epoch}-output-archive.zip"

    if not name:
        name = format_name.format(epoch=int(time()))
    else:
        name = name + ".zip"

    zip_path = Path(zip_path) / name

    with ZipFile(zip_path, "w") as zip_file:
        for file in files_path_collection:
            if not os.path.isfile(file):
                continue
            zip_file.write(file, arcname=os.path.basename(file))
            if remove_files:
                os.remove(file)

    return (True, zip_path)
