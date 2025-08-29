from setuptools import setup, find_packages

setup(
    name='rabbitmq_client',
    version='1.0.0',
    author='R&EC SPb ETU',
    author_email='info@nicetu.spb.ru',
    url='http://nicetu.spb.ru',
    description='Работа с брокером сообщений, клиентская часть',
    long_description="",
    zip_safe=False,
    packages=find_packages(where="."),  # ищем пакеты внутри client/
    package_dir={"": "."},              # корень пакетов = текущая папка
)
