from PyQt5.QtWidgets import QApplication
import sys
from clientMain import MainWindow


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
