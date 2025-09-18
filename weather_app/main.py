import sys
from PyQt5.QtWidgets import QApplication
from ui import WeatherMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherMainWindow()
    window.setWindowTitle("Weather App")
    window.show()
    sys.exit(app.exec_())
