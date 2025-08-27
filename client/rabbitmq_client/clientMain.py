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
        self.is_settings_editable = True  # управляется сигналом is_settings_editable_signal с брокера

        self.broker_worker = BrokerWorker(self.logger, self.settings)
        self.broker_thread = QThread()
        self.broker_worker.moveToThread(self.broker_thread)
        self.broker_worker.ready_signal.connect(self.on_ready)  # сигнал брокера о готовности работы (если подключен)
        self.broker_worker.is_settings_editable_signal.connect(  # сигнал брокера о возможности редактировать настройки
            lambda editable: setattr(self, "is_settings_editable", editable)
        )
        self.request_signal.connect(self.broker_worker.send_request)
        self.cancel_signal.connect(self.broker_worker.cancel_request)
        self.connect_signal.connect(self.broker_worker.connect)
        self.broker_thread.start()
        self.connect_signal.emit()  # сигнал брокеру о необходимости подключения

        self.ui.sendRequestButton.clicked.connect(self.on_send)
        self.ui.cancelButton.clicked.connect(self.on_cancel)
        self.ui.settingsButton.clicked.connect(self.on_settings)

    @pyqtSlot()
    def on_ready(self):
        # Функция срабатывает при успешном подключении к брокеру
        self.ui.sendRequestButton.setEnabled(True)
        self.logger.info("Для отправки запроса нажмите кнопку отправить")

    @pyqtSlot()
    def on_send(self):
        value = self.ui.requestSpinBox.value()
        delay = self.ui.delaySpinBox.value() if self.ui.useDelayCheckBox.isChecked() else 0.0
        self.request_signal.emit(value, delay)
        self.ui.cancelButton.setEnabled(True)
        self.logger.info(f"Отправка запроса: {value}, delay={delay}")

    @pyqtSlot()
    def on_cancel(self):
        self.ui.cancelButton.setEnabled(False)
        self.cancel_signal.emit()
        self.logger.info("Отмена запроса")

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
