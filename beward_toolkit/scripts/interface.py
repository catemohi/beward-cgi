#!/usr/bin/python
# coding=utf8
from general_solutions import get_terminal_size
from argparse import ArgumentParser


def get_divider():
    """Получить разделитель"""
    return get_terminal_size()[0] * "=" + "\n"


def get_epiloge_message(version, created_by, last_updated):
    """Получить конечное сообщение
    """
    divider = get_divider()
    return u"{divider}NAME: %(prog)s\nVERSION: {version}\nCREATED BY: {created_by}\nLAST UPDATED: {last_updated}\n{divider}".format(
        divider=divider,
        version=version,
        created_by=created_by,
        last_updated=last_updated,
    )


def init_default_parser():
    credentials_parser = ArgumentParser(add_help=False)
    credentials_parser.add_argument("-u", "--username", metavar="x", default=None, help="Имя пользователя зарегистрированного на панели Beward")
    credentials_parser.add_argument("-p", "--password", metavar="x", default=None, help="Пароль пользователя зарегистрированного на панели Beward")

    host_parser = ArgumentParser(add_help=False)
    host_parser.add_argument("ip", help="IP адрес панели Beward")

    list_parser = ArgumentParser(add_help=False)
    list_parser.add_argument("csvpath", help="Путь к csv файлу. Требования в csv файле. Столбцы: IP, Name; Делиметр: <;>. Кодировка: UTF-8")

    string_parser = ArgumentParser(add_help=False)
    string_parser.add_argument("string", help="Список адресов. Требования строке. Адреса разделены <;>")
    return credentials_parser, host_parser, list_parser, string_parser


CREDENTIALS_PARSER, HOST_PARSER, LIST_PARSER, STRING_PARSER = init_default_parser()
