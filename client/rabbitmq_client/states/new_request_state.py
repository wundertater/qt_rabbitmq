from client.rabbitmq_client.states.base_state import BaseState
import pika
from uuid import uuid4


class NewRequestState(BaseState):
    def __init__(self, broker_client):
        super().__init__()
        self.broker_client = broker_client

    def connect(self):
        try:
            self.broker_client.server_state_response_signal.emit("Подключение к брокеру", "Неопределено")
            self.broker_client.settings.sync()
            settings = self.broker_client.settings

            # Получаем логин и пароль из настроек
            username = settings.value("broker/login")
            password = settings.value("broker/password")
            # Создаем параметры подключения
            broker_conn_params = pika.ConnectionParameters(
                host=settings.value("broker/host", defaultValue="localhost"),
                port=settings.value("broker/port", defaultValue=5672),
                socket_timeout=float(settings.value("client/timeout", defaultValue=5.0))
            )
            # Добавляем credentials только если они указаны в настройках
            if username and password:
                credentials = pika.PlainCredentials(username=username, password=password)
                broker_conn_params.credentials = credentials

            # Для предотвращения создания множества подключений одним пользователем закрываем предыдущее соединение
            if getattr(self.broker_client, "connection", None):
                try:
                    self.broker_client.connection.close()
                except Exception as e:
                    self.broker_client.logger.warning(f"Ошибка при закрытии старого соединения: {e}")

            # Обновление полей класса-контекста broker_client
            self.broker_client.exchange = settings.value("broker/exchange")
            self.broker_client.queue_name = settings.value("broker/queue_name")
            self.broker_client.routing_key = settings.value("broker/routing_key")
            self.broker_client.client_queue_name = settings.value("client/uuid")
            if not self.broker_client.client_queue_name:  # если UUID данного клиента не задано вручную генерируем
                self.broker_client.client_queue_name = f"client-{uuid4()}"

            # Подключение к брокеру, объявление очереди клиента
            self.broker_client.connection = pika.BlockingConnection(broker_conn_params)
            self.broker_client.channel = self.broker_client.connection.channel()
            self.broker_client.channel.queue_declare(self.broker_client.client_queue_name, exclusive=True)

            self.broker_client.logger.debug("Подключено к брокеру")
            self.broker_client.logger.info("Для отправки запроса нажмите кнопку отправить")
            self.broker_client.server_state_response_signal.emit("Подключено", "Неопределено")
            # Меняем состояние брокера
            self.broker_client.state = self.broker_client.sending_request_state
            self.broker_client.request_sending_signal.emit(False)

        except pika.exceptions.AMQPConnectionError as e:
            self.broker_client.logger.error(
                f"Не удалось подключиться к брокеру, попробуйте изменить настройки подключения: {e}")

    def send_request(self, request_num: int, delay: float = 0.0):
        pass

    def cancel_request(self):
        pass

    def run(self):
        pass
