from abc import abstractmethod, ABC


class BaseState(ABC):
    @abstractmethod
    def send_request(self, request_num: int, delay: float = 0.0):
        # Метод для отправки запроса
        pass

    @abstractmethod
    def run(self):
        # Метод для запуска функционала состояния
        pass

    @abstractmethod
    def cancel_request(self):
        # Метод вызываемый при нажатии отмены
        pass

    @abstractmethod
    def connect(self):
        # Метод вызываемый при изменении настроек или первичном подключении к брокеру
        pass
