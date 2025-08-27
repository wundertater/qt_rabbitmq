from PyQt5.QtWidgets import QDialog
from client.rabbitmq_client.client_gui.settings_dialog_ui import Ui_dialog


class SettingsDialog(QDialog, Ui_dialog):
    def __init__(self, settings):
        super().__init__()
        self.setupUi(self)
        self.settings = settings
        self.load_settings()

    def load_settings(self):
        self.hostLineEdit.setText(self.settings.value("broker/host", "localhost"))
        self.portSpinBox.setValue(int(self.settings.value("broker/port", 5672)))
        self.loginLineEdit.setText(self.settings.value("broker/login", "guest"))
        self.passwordLineEdit.setText(self.settings.value("broker/password", "guest"))
        self.exchangeLineEdit.setText(self.settings.value("broker/exchange"))
        self.queue_nameLineEdit.setText(self.settings.value("broker/queue_name"))
        self.routing_keyLineEdit.setText(self.settings.value("broker/routing_key"))
        self.uuidLineEdit.setText(self.settings.value("client/uuid"))
        self.timeoutDoubleSpinBox.setValue(float(self.settings.value("client/timeout", 5.0)))

    def setEditable(self, editable: bool):
        """
        Включает/выключает возможность редактирования полей
        """
        self.hostLineEdit.setReadOnly(not editable)
        self.portSpinBox.setReadOnly(not editable)
        self.loginLineEdit.setReadOnly(not editable)
        self.passwordLineEdit.setReadOnly(not editable)
        self.exchangeLineEdit.setReadOnly(not editable)
        self.queue_nameLineEdit.setReadOnly(not editable)
        self.routing_keyLineEdit.setReadOnly(not editable)
        self.uuidLineEdit.setReadOnly(not editable)
        self.timeoutDoubleSpinBox.setReadOnly(not editable)

        self.buttonBox.button(self.buttonBox.Ok).setEnabled(editable)

    def save_settings(self):
        self.settings.setValue("broker/host", self.hostLineEdit.text())
        self.settings.setValue("broker/port", self.portSpinBox.value())
        self.settings.setValue("broker/login", self.loginLineEdit.text())
        self.settings.setValue("broker/password", self.passwordLineEdit.text())
        self.settings.setValue("broker/exchange", self.exchangeLineEdit.text())
        self.settings.setValue("broker/queue_name", self.queue_nameLineEdit.text())
        self.settings.setValue("broker/routing_key", self.routing_keyLineEdit.text())
        self.settings.setValue("client/uuid", self.uuidLineEdit.text())
        self.settings.setValue("client/timeout", self.timeoutDoubleSpinBox.value())
        self.settings.sync()

    def accept(self):
        self.save_settings()
        super().accept()
