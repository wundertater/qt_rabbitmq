from client.rabbitmq_client.states.base_state import BaseState


class RequestSendingErrorState(BaseState):
    def __init__(self, broker_client):
        super().__init__()
        self.broker_client = broker_client

    def connect(self):
        self.broker_client.state = self.broker_client.new_request_state
        self.broker_client.connect()

    def run(self):
        self.broker_client.server_state_response_signal.emit("Ошибка отправки запроса", "Неопределено")
        self.broker_client.request_sending_signal.emit(False)

    def send_request(self, request_num: int, delay: float = 0.0):
        self.broker_client.state = self.broker_client.sending_request_state
        self.broker_client.send_request(request_num, delay)

    def cancel_request(self):
        pass
