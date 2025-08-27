# Файл содержит класс-контекст управляющий отдельными состояниями
from PyQt5.QtCore import QObject, pyqtSlot, QSettings, pyqtSignal
from client.rabbitmq_client.states import (new_request_state, sending_request_state, waiting_response_state,
                                           response_received_state)


class BrokerWorker(QObject):
    ready_signal = pyqtSignal()  # сигнал брокера о готовности работы (если подключен)
    is_settings_editable_signal = pyqtSignal(bool)  # сигнал брокера о возможности редактирования настроек

    def __init__(self, logger, settings: QSettings):
        super().__init__()
        # Список-реестр всех состояний
        self.new_request_state = new_request_state.NewRequestState(self)
        self.sending_request_state = sending_request_state.SendingRequestState(self)
        self.waiting_response_state = waiting_response_state.WaitingResponseState(self)
        self.response_received_state = response_received_state.ResponseReceivedState(self)

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
