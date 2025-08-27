import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QThread, QSettings, pyqtSlot
from client_gui import main_window_ui
from settingsWindow import SettingsDialog
from logger import get_logger
from states.broker_client import BrokerWorker


class MainWindow(QtWidgets.QMainWindow):
    request_signal = pyqtSignal(int, float)  # Сигнал для отправки запроса
    cancel_signal = pyqtSignal()  # Сигнал для отмены запроса
    connect_signal = pyqtSignal()  # Сигнал о необходимости (пере)подключения к брокеру (запуск приложения/изменение настроек)

    def __init__(self):
        super().__init__()
        self.ui = main_window_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.logger = get_logger(self.ui)

        self.settings = QSettings("../client_config.ini", QSettings.IniFormat)
        self.is_settings_editable = True

        self.broker_worker = BrokerWorker(self.logger, self.settings)
        self.broker_thread = QThread()
        self.broker_worker.moveToThread(self.broker_thread)

        self.broker_worker.request_sending_signal.connect(self.on_sending_request)  # сигнал брокера об отправке запроса
        self.broker_worker.server_state_response_signal.connect(
            self.on_server_state_update)  # сигнал о состоянии сервера и ответе
        self.request_signal.connect(self.broker_worker.send_request)
        self.cancel_signal.connect(self.broker_worker.cancel_request)
        self.connect_signal.connect(self.broker_worker.connect)
        self.broker_thread.start()
        self.connect_signal.emit()  # сигнал брокеру о необходимости подключения

        self.ui.sendRequestButton.clicked.connect(self.on_send)
        self.ui.cancelButton.clicked.connect(self.on_cancel)
        self.ui.settingsButton.clicked.connect(self.on_settings)

    @pyqtSlot(str, str)
    def on_server_state_update(self, server_state: str, response: str):
        # Обновляет надпись состояния сервера и ответ
        self.ui.serverStateLabel.setText(server_state)
        self.ui.serverResponseLabel.setText(response)

    @pyqtSlot(bool)
    def on_sending_request(self, is_req_send: bool):
        # При сигнале отправка запроса от брокера блокирует кнопку отправить, разблокирует кнопку отмена, блокирует изменение настроек
        self.ui.sendRequestButton.setEnabled(not is_req_send)
        self.ui.cancelButton.setEnabled(is_req_send)
        self.is_settings_editable = not is_req_send

    @pyqtSlot()
    def on_send(self):
        value = self.ui.requestSpinBox.value()
        delay = self.ui.delaySpinBox.value() if self.ui.useDelayCheckBox.isChecked() else 0.0
        self.request_signal.emit(value, delay)

    @pyqtSlot()
    def on_cancel(self):
        self.cancel_signal.emit()

    @pyqtSlot()
    def on_settings(self):
        dialog = SettingsDialog(self.settings)
        dialog.setEditable(self.is_settings_editable)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.logger.info("Настройки сохранены")
            self.connect_signal.emit()  # сигнал брокеру о необходимости переподключения с новыми настройками

    def closeEvent(self, event):
        self.broker_thread.quit()
        self.broker_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
