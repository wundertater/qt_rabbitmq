import logging
from PyQt5.QtCore import pyqtSignal, QObject


class QtLogHandler(QObject, logging.Handler):
    emitter = pyqtSignal(str)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.emitter.emit(msg)
        except Exception:
            self.handleError(record)


def get_logger(ui):
    logger = logging.getLogger("client")
    logger.setLevel(logging.DEBUG)
    logger_format = "%(asctime)s [%(levelname)s] %(message)s"

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(logger_format))
    logger.addHandler(console_handler)

    widget_handler = QtLogHandler()
    widget_handler.setLevel(logging.INFO)
    widget_handler.setFormatter(logging.Formatter(logger_format))
    widget_handler.emitter.connect(ui.loggingText.appendPlainText)
    logger.addHandler(widget_handler)
    return logger
