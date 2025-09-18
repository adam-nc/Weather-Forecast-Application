import os
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import QFrame, QSizePolicy, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QScrollArea, QTextEdit, \
    QPushButton, QTabWidget, QLineEdit, QMessageBox
#from daily_forecast_manager_class import DailyForecastManager
from hourly_forecast_manager_class import HourlyForecastManager
from forecast_worker import ForecastWorker
from geolocator import GeolocatorService


class CurrentWeatherWidget(QFrame):
    """Displays the current temperature and short forecast using HourlyForecastManager."""

    def __init__(self, parent=None):
        """Initializes UI components."""
        super().__init__(parent)

        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background-color: white; border: none; padding: 7px;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Configure current temperature label
        current_temp_font = QFont()
        current_temp_font.setPixelSize(30)
        current_temp_font.setBold(True)

        self.currentTempLabel = QLabel("", self)
        self.currentTempLabel.setFont(current_temp_font)
        self.currentTempLabel.setStyleSheet("background-color: transparent;")
        self.currentTempLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Configure short forecast label
        short_forecast_font = QFont()
        short_forecast_font.setPixelSize(30)

        self.shortForecastLabel = QLabel("", self)
        self.shortForecastLabel.setFont(short_forecast_font)
        self.shortForecastLabel.setStyleSheet("background-color: transparent;")
        self.shortForecastLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Layout setup
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.currentTempLabel)
        layout.addWidget(self.shortForecastLabel, alignment=Qt.AlignRight)

    def update_data(self, temperature, short_forecast):
        """Fetches and updates weather data."""
        self.currentTempLabel.setText(f"{temperature}")
        self.shortForecastLabel.setText(f"{short_forecast}")

    def clear_data(self):
        """Handles cases where no forecast data is available."""
        self.currentTempLabel.setText("")
        self.shortForecastLabel.setText("")


class DailyForecastTab(QWidget):
    """A widget to display daily forecast information, including forecast cards and detailed forecast."""

    def __init__(self, parent=None):
        """Initializes the UI components and layout for displaying daily forecasts."""
        super().__init__(parent)

        # Initialize main layout
        self.daily_layout = QVBoxLayout(self)
        self.daily_layout.setContentsMargins(0, 0, 0, 0)
        self.daily_layout.setSpacing(5)

        # Create and configure the top section (scroll area for daily forecast cards)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget for the scroll area with a horizontal layout
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_layout.setSpacing(10)
        self.scroll_content.setLayout(self.scroll_layout)

        # Set the scroll content widget to the scroll area
        self.scroll_area.setWidget(self.scroll_content)

        # Create and configure the middle section (detailed forecast display area)
        self.detailed_forecast_label = QTextEdit()
        self.detailed_forecast_label.setReadOnly(True)
        self.detailed_forecast_label.setPlainText("")
        self.detailed_forecast_label.setFixedHeight(100)

        # Create and configure the bottom section (text area for generated time)
        self.daily_generated_time = QTextEdit()
        self.daily_generated_time.setReadOnly(True)
        self.daily_generated_time.setPlainText("")
        self.daily_generated_time.setFixedHeight(30)

        # Add all sections to the main layout
        self.daily_layout.addWidget(self.scroll_area)
        self.daily_layout.addWidget(self.detailed_forecast_label)
        self.daily_layout.addWidget(self.daily_generated_time)

    def update_data(self, daily_forecast_generated_time, daily_forecasts):
        """
        Loads and updates the daily forecast data.
        This will update the scroll area with new forecast cards and show the detailed forecast for the first item.
        """
        # Clear existing forecast cards in the scroll area
        self._clear_forecast_cards()

        # Add new forecast cards to the scroll layout
        for forecast in daily_forecasts:
            card = DailyForecastCard()
            card.update_data(forecast)
            # Connect signal to show detailed forecast
            card.showMoreClicked.connect(self.update_detailed_forecast_label)
            card.setFixedWidth(150)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()  # Stretch the layout to fill remaining space

        # Display the detailed forecast of the first forecast card
        self.update_detailed_forecast_label(daily_forecasts[0].period_name, daily_forecasts[0].detailed_forecast)

        # Update the generated time label
        self.daily_generated_time.setPlainText(f"Daily forecast generated at {daily_forecast_generated_time}")

    def _clear_forecast_cards(self):
        """Clears all the forecast cards currently in the scroll layout."""
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_detailed_forecast_label(self, period_name, detailed_forecast):
        """Updates the detailed forecast text area with the provided period name and detailed forecast."""
        text = f"{period_name}: {detailed_forecast}"
        self.detailed_forecast_label.setPlainText(text)

    def clear_data(self):
        """Clears the forecast cards, detailed forecast, and generated time."""
        self._clear_forecast_cards()
        self.detailed_forecast_label.setPlainText("")
        self.daily_generated_time.setPlainText("")


class DailyForecastCard(QFrame):
    """A widget to display daily forecast information, including weather icon, temperature, and rain chances."""

    # Signal to emit period name and detailed forecast when the "Show More" button is clicked.
    showMoreClicked = pyqtSignal(str, str)

    def __init__(self, parent=None):
        """Initializes the UI components and layout for displaying forecast details."""
        super().__init__(parent)

        # Initialize the UI components and set up the layout
        self.setStyleSheet("background-color: white;")
        self.uniform_font = QFont()
        self.uniform_font.setPixelSize(24)

        # Create and configure labels with common style
        self.period_label = QLabel("", self)
        self.period_label.setFont(self.uniform_font)
        self.period_label.setAlignment(Qt.AlignCenter)
        self.period_label.setWordWrap(True)

        self.temp_label = QLabel("", self)
        self.temp_label.setFont(self.uniform_font)
        self.temp_label.setAlignment(Qt.AlignCenter)

        self.rain_label = QLabel("", self)
        self.rain_label.setFont(self.uniform_font)
        self.rain_label.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel("", self)
        self.icon_label.setFont(self.uniform_font)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Create "Show More" button and connect it to the handler
        self.show_more_button = QPushButton("Show More", self)
        self.show_more_button.setFont(self.uniform_font)
        self.show_more_button.clicked.connect(self.on_show_more_clicked)

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Add widgets to layout
        self.layout.addWidget(self.period_label)
        self.layout.addWidget(self.temp_label)
        self.layout.addWidget(self.rain_label)
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.show_more_button, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        # Set up the network manager for fetching weather icon images
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.on_image_loaded)

        # Initialize period_name and detailed_forecast to None (to prevent crashes before it's set)
        self.period_name = None
        self.detailed_forecast = None

    def update_data(self, forecast):
        """Populate the card with forecast data and trigger the image fetch."""
        self.period_label.setText(forecast.period_name)
        self.temp_label.setText(forecast.temperature_fahrenheit)
        self.rain_label.setText(forecast.chance_of_rain)
        self.icon_label.setText(f"Icon: {forecast.icon_url}")
        self.period_name = forecast.period_name
        self.detailed_forecast = forecast.detailed_forecast

        # Request the weather icon image using the URL from forecast data
        request = QNetworkRequest(QUrl(forecast.icon_url))
        self.manager.get(request)

    def on_image_loaded(self, reply):
        """Handles the completion of the image fetch and sets it on the icon label."""
        if reply.error():
            self.icon_label.setText("Failed to load image")
        else:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.icon_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))

        reply.deleteLater()

    def on_show_more_clicked(self):
        """Emits a signal with period name and detailed forecast when the button is clicked."""
        if self.period_name and self.detailed_forecast:
            self.showMoreClicked.emit(self.period_name, self.detailed_forecast)


class ForecastHeadingWidget(QLabel):
    """Widget displaying the forecast heading with location."""

    def __init__(self, parent=None):
        """Initializes UI components."""
        super().__init__(parent)

        self.setText("Forecast for...")
        self.setWordWrap(True)

        font = QFont()
        font.setPixelSize(30)
        self.setFont(font)

    def update_data(self, address):
        """Updates the heading with the given address."""
        self.setText(f"Forecast for {address}")

    def clear_data(self):
        self.setText("Forecast for...")


class ForecastTabsWidget(QTabWidget):
    """A tab widget containing a 'Daily Forecast' tab and an 'Hourly Forecast' tab."""

    def __init__(self, parent=None):
        """Initializes the UI components and layout for displaying the tabs."""
        super().__init__(parent)

        # Create and initialize the forecast tabs
        self.daily_tab = DailyForecastTab()
        self.hourly_tab = HourlyForecastTab()

        # Add tabs to the widget
        self.addTab(self.daily_tab, "Daily")
        self.addTab(self.hourly_tab, "Hourly")

    def update_data(self, daily_generated_time, hourly_generated_time, daily_forecasts, hourly_forecasts):
        """Updates both the Daily and Hourly forecast tabs with new forecast data."""
        self.daily_tab.update_data(daily_generated_time, daily_forecasts)
        self.hourly_tab.update_data(hourly_generated_time, hourly_forecasts)

    def clear_data(self):
        """Clears all forecast data from both tabs."""
        self.daily_tab.clear_data()
        self.hourly_tab.clear_data()


class HourlyForecastTab(QWidget):
    """A widget to display hourly forecast information."""

    def __init__(self, parent=None):
        """Initializes the UI components and layout for displaying hourly forecasts."""
        super().__init__(parent)

        # Initialize main layout
        self.hourly_layout = QVBoxLayout(self)
        self.hourly_layout.setContentsMargins(0, 0, 0, 0)
        self.hourly_layout.setSpacing(5)

        # Create and configure the top section (scroll area for hourly forecast rows)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget for the scroll area with a vertical layout
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_layout.setSpacing(5)
        self.scroll_content.setLayout(self.scroll_layout)

        # Set the scroll content widget to the scroll area
        self.scroll_area.setWidget(self.scroll_content)

        # Create and configure the bottom section (text area for generated time)
        self.hourly_generated_time = QTextEdit()
        self.hourly_generated_time.setReadOnly(True)
        self.hourly_generated_time.setPlainText("")
        self.hourly_generated_time.setFixedHeight(30)

        # Add all sections to the main layout
        self.hourly_layout.addWidget(self.scroll_area)
        self.hourly_layout.addWidget(self.hourly_generated_time)

    def update_data(self, hourly_forecast_generated_time, hourly_forecasts):
        # Clear existing rows in the scroll area
        self._clear_forecast_rows()

        forecast_date = ""

        # Add new forecast row to the scroll layout
        for forecast in hourly_forecasts:
            row = HourlyForecastRow()
            row.update_data(forecast)

            if forecast.formatted_date != forecast_date:
                forecast_date = forecast.formatted_date
                header_row = HourlyForecastHeaderRow()
                header_row.update_data(forecast_date)
                self.scroll_layout.addWidget(header_row)
            # Connect signal to show extra details
            # row.showMoreClicked.connect(self.update_detailed_forecast_label)
            self.scroll_layout.addWidget(row)

        # Update the generated time label
        self.hourly_generated_time.setPlainText(f"Hourly forecast generated at {hourly_forecast_generated_time}")

    def clear_data(self):
        self._clear_forecast_rows()
        self.hourly_generated_time.setPlainText("")

    def _clear_forecast_rows(self):
        """Clears all the rows currently in the scroll layout."""
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class HourlyForecastHeaderRow(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        heading_font = QFont()
        heading_font.setPixelSize(20)

        self.setFont(heading_font)
        self.setText("")
        self.setContentsMargins(5, 5, 5, 5)

    def update_data(self, date):
        self.setText(date)


class HourlyForecastRow(QFrame):
    """A row widget to display hourly forecast data."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize the UI components and set up the layout
        self.setStyleSheet("""
            HourlyForecastRow {
                background-color: white;
                border-radius: 4px;
            }
            QLabel {
                padding: 4px;
            }
        """)

        self.uniform_font = QFont()
        self.uniform_font.setPixelSize(20)

        self.icon_font = QFont('Segoe UI Emoji')
        self.icon_font.setPixelSize(20)

        self.is_expanded = False

        # Main row widgets
        self.hour_label = QLabel("", self)
        self.icon_label = QLabel("", self)
        self.rain_label = QLabel("", self)
        self.temp_label = QLabel("", self)
        self.wind_label = QLabel("", self)
        self.show_more_button = QPushButton("+", self)

        # Set fixed widths for consistent spacing
        self.hour_label.setFixedWidth(110)
        self.icon_label.setFixedWidth(45)
        self.rain_label.setFixedWidth(100)
        self.temp_label.setFixedWidth(70)
        self.show_more_button.setFixedWidth(30)

        # Details section (initially hidden)
        self.details_widget = QWidget()
        self.details_widget.setVisible(False)
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setSpacing(2)  # Reduced from default
        self.details_layout.setContentsMargins(0, 0, 0, 0)

        # Detail labels
        self.detail_short_forecast = QLabel("", self.details_widget)
        self.detail_short_forecast.setWordWrap(True)
        self.detail_dewpoint = QLabel("", self.details_widget)
        self.detail_humidity = QLabel("", self.details_widget)

        # Set fonts
        for widget in [self.hour_label, self.rain_label, self.temp_label, self.wind_label, self.detail_short_forecast,
                       self.detail_dewpoint, self.detail_humidity]:
            widget.setFont(self.uniform_font)

        self.icon_label.setFont(self.icon_font)

        # Main layout setup
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(0)

        # Top row layout
        self.top_row = QHBoxLayout()
        self.top_row.setContentsMargins(0, 0, 5, 0)

        # Add widgets
        for widget in [self.hour_label, self.icon_label, self.rain_label, self.temp_label, self.wind_label,
                       self.show_more_button]:
            self.top_row.addWidget(widget)

        for widget in [self.detail_short_forecast, self.detail_dewpoint, self.detail_humidity]:
            self.details_layout.addWidget(widget)

        # Add to main layout
        self.main_layout.addLayout(self.top_row)
        self.main_layout.addWidget(self.details_widget)

        # Connect button
        self.show_more_button.clicked.connect(self.toggle_details)

    def toggle_details(self):
        """Toggle the visibility of the details section."""
        self.is_expanded = not self.is_expanded
        self.details_widget.setVisible(self.is_expanded)
        self.show_more_button.setText("-" if self.is_expanded else "+")

    def update_data(self, forecast):
        """Populate the row with forecast data"""
        self.hour_label.setText(forecast.forecast_hour)
        self.icon_label.setText(forecast.weather_icon)
        self.rain_label.setText(forecast.chance_of_rain)
        self.temp_label.setText(forecast.temperature_fahrenheit)
        self.wind_label.setText(forecast.wind)

        self.detail_short_forecast.setText(f"Short Forecast: {forecast.short_forecast}")
        self.detail_dewpoint.setText(f"Dewpoint: {forecast.dewpoint_fahrenheit}")
        self.detail_humidity.setText(f"Relative Humidity: {forecast.relative_humidity}")


class LocationSearchWidget(QWidget):
    locationConfirmed = pyqtSignal(object)

    def __init__(self, parent=None):
        """Set up the UI components."""
        super().__init__(parent)
        self.geo_service = GeolocatorService()

        # Configure Font
        font = QFont()
        font.setPixelSize(16)

        # Create and Configure Search Bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Enter location")
        self.search_bar.setFont(font)
        self.search_bar.setFixedHeight(40)
        self.search_bar.setStyleSheet("padding-left: 5px; padding-right: 5px")
        self.search_bar.returnPressed.connect(self.search_location)

        # Create and Configure Search Button
        self.search_button = QPushButton("Search", self)
        self.search_button.setFont(font)
        self.search_button.setFixedSize(80, 40)
        self.search_button.clicked.connect(self.search_location)

        # Layout Setup
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.search_button)

        self.setLayout(layout)

    def search_location(self):
        """Handles location search and emits a signal if confirmed."""
        location_text = self.search_bar.text().strip()
        if not location_text:
            QMessageBox.warning(self, "Input Error", "Please enter a location.")
            return

        location = self.geo_service.get_location(location_text)
        if location:
            if self._confirm_location(location.address):
                self._clear_previous_forecast()
                self.locationConfirmed.emit(location)
                self.search_bar.clear()
        else:
            QMessageBox.warning(self, "Location Not Found",
                                "Could not find the location. Please try a different query.")

    def _confirm_location(self, address):
        """Prompt the user to confirm the found location."""
        return QMessageBox.question(self, "Confirm Location", f"Is this the correct location?\n\n{address}",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes

    def _clear_previous_forecast(self):
        """Remove old forecast data files if they exist."""
        for filename in ['daily_forecast_data.csv', 'hourly_forecast_data.csv']:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except OSError:
                pass


class WeatherMainWindow(QWidget):
    def __init__(self, parent=None):
        """Sets up the UI layout and widgets."""
        super().__init__(parent)

        self.setFixedSize(600, 800)

        self.search_widget = LocationSearchWidget(self)
        self.search_widget.locationConfirmed.connect(self.handle_location_confirmed)
        self.heading_widget = ForecastHeadingWidget(self)
        self.current_weather_widget = CurrentWeatherWidget(self)
        self.forecast_tabs_widget = ForecastTabsWidget(self)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.search_widget)
        layout.addWidget(self.heading_widget)
        layout.addWidget(self.current_weather_widget)
        layout.addWidget(self.forecast_tabs_widget)

        self.setLayout(layout)

    def handle_location_confirmed(self, location):
        """Handles the location confirmation event."""
        self.heading_widget.update_data(location.address)

        # Start forecast worker thread
        self.worker = ForecastWorker(location)
        self.worker.worker_finished.connect(self.handle_forecast_result)
        self.worker.start()

    def handle_forecast_result(self, success, message, daily_generated_time, hourly_generated_time):
        """Handles the forecast result update."""
        print(message)
        if success:
            daily_manager = DailyForecastManager("daily_forecast_data.csv", daily_generated_time)
            hourly_manager = HourlyForecastManager("hourly_forecast_data.csv", hourly_generated_time)

            if daily_manager.load_forecasts() and hourly_manager.load_forecasts():
                daily_forecasts = daily_manager.get_forecasts()
                hourly_forecasts = hourly_manager.get_forecasts()
                self.current_weather_widget.update_data(hourly_forecasts[0].temperature_fahrenheit,
                                                        hourly_forecasts[0].short_forecast)
                self.forecast_tabs_widget.update_data(daily_generated_time, hourly_generated_time, daily_forecasts,
                                                      hourly_forecasts)
            else:
                self.heading_widget.clear_data()
                self.current_weather_widget.clear_data()
                self.forecast_tabs_widget.clear_data()
        else:
            # Data retrieval failed, update UI to show no data
            self.heading_widget.clear_data()
            self.current_weather_widget.clear_data()
            self.forecast_tabs_widget.clear_data()
