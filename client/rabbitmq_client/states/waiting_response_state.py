from PyQt5.QtCore import QTimer
from client.rabbitmq_client.states.base_state import BaseState


class WaitingResponseState(BaseState):
    def __init__(self, broker_client, request_id=None):
        super().__init__()
        self.broker_client = broker_client
        self.request_id = request_id
        self.consumer_tag = None
        self.timer = None

    def connect(self):
        pass

    def run(self):
        def on_response(ch, method, properties, body):
            if properties.correlation_id == self.request_id:
                # отменяем подписку
                ch.basic_cancel(self.consumer_tag)
                # останавливаем таймер
                if self.timer:
                    self.timer.stop()
                self.broker_client.state = self.broker_client.response_received_state
                self.broker_client.state.body = body  # передаем в состояние ответ
                self.broker_client.state.run()

        self.consumer_tag = self.broker_client.channel.basic_consume(
            queue=self.broker_client.client_queue_name,
            on_message_callback=on_response,
            auto_ack=True
        )

        # запускаем QTimer для регулярного polling
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(lambda: self.broker_client.channel.connection.process_data_events(time_limit=0))
        self.timer.start()

        self.broker_client.logger.info("Ожидание ответа...")

    def send_request(self, request_num: int, delay: float = 0.0):
        pass

    def cancel_request(self):
        if self.consumer_tag:
            self.broker_client.channel.basic_cancel(self.consumer_tag)
            self.consumer_tag = None

        if self.timer:
            self.timer.stop()

        self.broker_client.logger.info("Ожидание ответа отменено пользователем")
