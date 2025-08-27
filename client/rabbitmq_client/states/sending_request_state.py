from client.rabbitmq_client.states.base_state import BaseState
from client.rabbitmq_client.protobuf.message_pb2 import Request
from uuid import uuid4
import pika


class SendingRequestState(BaseState):
    def __init__(self, broker_client):
        super().__init__()
        self.broker_client = broker_client

    def connect(self):
        # При изменении настроек при уже успешном подключении изменяем сосояние на новый запрос и выполняем переподключение
        self.broker_client.state = self.broker_client.new_request_state
        self.broker_client.connect()

    def send_request(self, request_num: int, delay: float = 0.0):
        try:
            self.broker_client.server_state_response_signal.emit("Отправка запроса", "Неопределено")
            self.broker_client.request_sending_signal.emit(True)

            request_id = str(uuid4())
            request = Request(
                return_address=self.broker_client.client_queue_name,
                request_id=request_id,
                process_time_in_seconds=delay,
                request=request_num,
            )

            self.broker_client.channel.basic_publish(
                exchange=self.broker_client.exchange,
                routing_key=self.broker_client.routing_key,
                body=request.SerializeToString(),
                properties=pika.BasicProperties(
                    correlation_id=request_id
                )
            )
            self.broker_client.logger.info(f"Отправлен запрос: {request_num}; delay: {delay}")
            self.broker_client.state = self.broker_client.waiting_response_state
            self.broker_client.state.request_id = request_id
            self.broker_client.run()
        except Exception as e:
            self.broker_client.logger.error(f"Ошибка отправки запроса: {e}")
            self.broker_client.state = self.broker_client.request_sending_error_state
            self.broker_client.run()

    def cancel_request(self):
        pass

    def run(self):
        pass
