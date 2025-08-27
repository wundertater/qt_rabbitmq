from client.rabbitmq_client.states.base_state import BaseState
from client.rabbitmq_client.states.new_request_state import NewRequestState


class ResponseReceivedState(BaseState):
    def __init__(self, broker_client):
        super().__init__()
        self.broker_client = broker_client

    def connect(self):
        pass

    def send_request(self, request_num: int, delay: float = 0.0):
        pass

    def cancel_request(self):
        pass

    def run(self):
        self.broker_client.state = NewRequestState(self.broker_client)
