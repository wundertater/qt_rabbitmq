# Файл содержит класс-контекст управляющий отдельными состояниями
from PyQt5.QtCore import QObject, pyqtSlot, QSettings, pyqtSignal
from client.rabbitmq_client.states import (new_request_state, sending_request_state, waiting_response_state,
                                           response_received_state, waiting_cancelled_state,
                                           response_receiving_error_state, request_sending_error_state)


class BrokerWorker(QObject):
    # Сигнал брокера об отправке запроса: блокирует кнопку отправить, брокирует изменение настроек, разблокирует кнопку отмены
    request_sending_signal = pyqtSignal(bool)
    server_state_response_signal = pyqtSignal(str, str)  # сигнал о состоянии сервера и ответе

    def __init__(self, logger, settings: QSettings):
        super().__init__()
        # Список-реестр всех состояний
        self.new_request_state = new_request_state.NewRequestState(self)
        self.sending_request_state = sending_request_state.SendingRequestState(self)
        self.waiting_response_state = waiting_response_state.WaitingResponseState(self)
        self.response_received_state = response_received_state.ResponseReceivedState(self)
        self.waiting_cancelled_state = waiting_cancelled_state.WaitingCancelledState(self)
        self.response_receiving_error_state = response_receiving_error_state.ResponseReceivingErrorState(self)
        self.request_sending_error_state = request_sending_error_state.RequestSendingErrorState(self)

        self.state = self.new_request_state  # self.state хранит текущее состояние, первоначальное состояние - новый запрос
        self.logger = logger
        self.settings = settings
        # Атрибуты для работы с брокером
        self.exchange = None
        self.queue_name = None
        self.routing_key = None
        self.connection = None
        self.channel = None
        self.client_queue_name = None

    @pyqtSlot(int, float)
    def send_request(self, request_num: int, delay: float = 0.0):
        self.state.send_request(request_num, delay)

    @pyqtSlot()
    def connect(self):
        self.state.connect()

    @pyqtSlot()
    def cancel_request(self):
        self.state.cancel_request()

    def run(self):
        self.state.run()
