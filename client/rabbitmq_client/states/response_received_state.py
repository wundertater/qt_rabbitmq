from client.rabbitmq_client.states.base_state import BaseState
from client.rabbitmq_client.protobuf.message_pb2 import Response


class ResponseReceivedState(BaseState):
    def __init__(self, broker_client, body=None):
        super().__init__()
        self.body = body  # тело ответа
        self.broker_client = broker_client

    def connect(self):
        # Если изменены параметры запроса (настройки) то переподключаемся, state - новый запрос
        self.broker_client.state = self.broker_client.new_request_state
        self.broker_client.connect()

    def send_request(self, request_num: int, delay: float = 0.0):
        self.broker_client.state = self.broker_client.sending_request_state
        self.broker_client.send_request(request_num, delay)

    def cancel_request(self):
        pass

    def run(self):
        response = Response()
        response.ParseFromString(self.body)
        self.broker_client.server_state_response_signal.emit("Ответ получен", str(response.response))
        self.broker_client.logger.info(f"Ответ от сервера: {response.response}")
        self.broker_client.request_sending_signal.emit(False)
