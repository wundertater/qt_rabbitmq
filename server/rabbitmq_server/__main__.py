"""Точка запуска для сервера"""
import configparser
from model import RabbitMQServer

config = configparser.ConfigParser()
config.read('../server_config.ini')

server = RabbitMQServer(config)
server.start()
