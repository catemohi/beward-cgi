#!/usr/bin/python
# coding=utf8

from beward_cgi.upgrade import UpgradeModule

with open('text.txt', 'rb') as file:
    client = UpgradeModule(ip='10.80.1.213',login='admin',password='admin')
    client.upgrade(file)
