"""
Модуль для обработки аргументов командной строки и предоставления вспомогательных функций.

Этот модуль содержит функции и аргумент-парсеры, которые используются для обработки
и анализа аргументов командной строки программы. Включает также функции для форматирования
конечного сообщения и получения разделителя.

Модуль также предоставляет функцию инициализации стандартных аргумент-парсеров для разбора
определенных входных аргументов программы, таких как учетные данные, IP-адрес, пути к файлам и
другие параметры.

Функции:
- get_divider(): Возвращает разделитель, состоящий из символов `=`.
- get_epiloge_message(version, created_by, last_updated): Получает конечное сообщение с информацией о версии,
  создателе и дате последнего обновления.
- init_default_parser(): Инициализирует стандартные аргумент-парсеры.

Аргумент-парсеры:
- CREDENTIALS_PARSER: Парсер для аргументов, связанных с учетными данными.
- HOST_PARSER: Парсер для аргументов, связанных с IP-адресом.
- LIST_PARSER: Парсер для аргументов, связанных с путем к CSV файлу и количеством потоков.
- STRING_PARSER: Парсер для аргументов, связанных со списком адресов и количеством потоков.
- ZIP_PARSER: Парсер для аргументов, связанных с запаковкой файлов в zip архив.

"""
#!/usr/bin/python
# coding=utf8
from general_solutions import get_terminal_size
from argparse import ArgumentParser
from general_solutions import validate_string_line, validate_csvfile


def get_divider():
    """
    Возвращает разделитель, состоящий из символов `=`.

    Args:
        None

    Note:
        Использует функцию get_terminal_size() для определения ширины окна терминала.

    Returns:
        divider (str): Символ `=`, повторенный количество раз, равное ширине окна терминала.
    """
    return get_terminal_size()[0] * "=" + "\n"


def get_epiloge_message(version, created_by, last_updated):
    """
    Получить конечное сообщение с информацией о версии, создателе и дате последнего обновления.

    Args:
        version (str): Версия программы.
        created_by (str): Создатель программы.
        last_updated (str): Дата последнего обновления программы.

    Returns:
        str: Сформированное конечное сообщение.

    Note:
        Эта функция форматирует конечное сообщение, которое содержит информацию о версии программы,
        создателе и дате последнего обновления. Она использует функцию `get_divider()` для получения
        разделителя между сообщением и секциями информации. Возвращаемое конечное сообщение будет 
        иметь следующий формат:
        ```
        -----------------------------
        NAME: %(prog)s
        VERSION: <version>
        CREATED BY: <created_by>
        LAST UPDATED: <last_updated>
        -----------------------------
        ```
        Где `<version>`, `<created_by>` и `<last_updated>` заменяются соответствующими значениями.
    """
    divider = get_divider()
    return u"{divider}NAME: %(prog)s\nVERSION: {version}\nCREATED BY: {created_by}\nLAST UPDATED: {last_updated}\n{divider}".format(
        divider=divider,
        version=version,
        created_by=created_by,
        last_updated=last_updated,
    )


def init_default_parser():
    """
    Инициализирует стандартные аргумент-парсеры.

    Returns:
        (ArgumentParser, ArgumentParser, ArgumentParser, ArgumentParser, ArgumentParser):
        Пары аргумент-парсеров, каждый из которых содержит определенные аргументы и опции.

    Note:
        Данная функция создает различные аргумент-парсеры, каждый из которых используется
        для разбора и обработки определенных входных аргументов программы. Пользователь
        может использовать эти парсеры по своему усмотрению, чтобы обрабатывать разные виды
        аргументов, такие как учетные данные, IP-адрес, пути к файлам и другие параметры.
    """
    credentials_parser = ArgumentParser(add_help=False)
    credentials_parser.add_argument("-u", "--username", metavar="x", default=None, help="Имя пользователя, зарегистрированного на панели Beward")
    credentials_parser.add_argument("-p", "--password", metavar="x", default=None, help="Пароль пользователя, зарегистрированного на панели Beward")

    host_parser = ArgumentParser(add_help=False)
    host_parser.add_argument("ip", help="IP-адрес панели Beward")

    list_parser = ArgumentParser(add_help=False)
    list_parser.add_argument("csvpath", help="Путь к CSV файлу. Требования: Столбцы: IP, Name; Разделитель: <;>. Кодировка: UTF-8",
                             type=validate_csvfile)
    list_parser.add_argument("--thread", help="Количество потоков для запуска скрипта.", type=int, default=1)

    string_parser = ArgumentParser(add_help=False)
    string_parser.add_argument("string", help="Список адресов. Требования: Адреса разделены запятой (,)",
                               type=validate_string_line)
    string_parser.add_argument("--thread", help="Количество потоков для запуска скрипта.", type=int, default=1)

    zip_parser = ArgumentParser(add_help=False)
    zip_parser.add_argument("-r", "--archiveted", help="Запаковать файлы в zip архив", action="store_true")

    return credentials_parser, host_parser, list_parser, string_parser, zip_parser


# Создаем аргумент-парсеры, используя функцию init_default_parser
CREDENTIALS_PARSER, HOST_PARSER, LIST_PARSER, STRING_PARSER, ZIP_PARSER = init_default_parser()
