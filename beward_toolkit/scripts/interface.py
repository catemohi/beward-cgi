#!/usr/bin/python
# coding=utf8
import gettext
from general_solutions import get_terminal_size


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


def convertArgparseMessages(s):
    subDict = {
        'ambiguous option: %s could match %s':
        'ambiguous option: %s could match %s',
        'argument "-" with mode %r': 'argument "-" with mode %r',
        'cannot merge actions - two groups are named %r':
        'cannot merge actions - two groups are named %r',
        "can't open '%s': %s": "can't open '%s': %s",
        'dest= is required for options like %r':
        'dest= is required for options like %r',
        'expected at least one argument': 'expected at least one argument',
        'expected at most one argument': 'expected at most one argument',
        'expected one argument': 'expected one argument',
        'ignored explicit argument %r': 'ignored explicit argument %r',
        'invalid choice: %r (choose from %s)':
        'invalid choice: %r (choose from %s)',
        'invalid conflict_resolution value: %r':
        'invalid conflict_resolution value: %r',
        'invalid option string %r: must start with a character %r':
        'invalid option string %r: must start with a character %r',
        'invalid %s value: %r': 'invalid %s value: %r',
        'mutually exclusive arguments must be optional':
        'mutually exclusive arguments must be optional',
        'not allowed with argument %s': 'not allowed with argument %',
        'one of the arguments %s is required':
        'one of the arguments %s is required',
        'optional arguments': u'{}именнованные аргументы'.format(get_divider()),
        'options': u'{}именнованные аргументы'.format(get_divider()),
        'positional arguments': u'{}позиционнные аргументы'.format(get_divider()),
        "'required' is an invalid argument for positionals":
        "'required' is an invalid argument for positionals",
        'show this help message and exit': u'показать справку и выйти.',
        'unrecognized arguments: %s': 'unrecognized arguments: %s',
        'unknown parser %r (choices: %s)': 'unknown parser %r (choices: %s)',
        'usage: ': u'используйте: ',
        '%s: error: %s\n': '%s: error: %s\n',
        '%r is not callable': '%r is not callable',
    }
    if s in subDict:
        s = subDict[s]
    return s


gettext.gettext = convertArgparseMessages
from argparse import ArgumentParser


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
