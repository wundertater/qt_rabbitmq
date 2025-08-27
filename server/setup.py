from setuptools import setup
from setuptools.command.build_py import build_py
from distutils.spawn import spawn, find_executable

class Build(build_py):
    def run(self):
        spawn([find_executable('protoc'), '--python_out=.', 'protobuf/message.proto'])
        build_py.run(self)


setup(
    name='rabbitmq_server',
    version='1.0.0',
    author='R&EC SPb ETU',
    author_email='info@nicetu.spb.ru',
    url='http://nicetu.spb.ru',
    description='Работа с брокером сообщений, серверная часть',
    long_description="",
    zip_safe=False,
    packages=['rabbitmq_server'],
)
