import sys
import os
# Update the PyQt5 imports at the top
from PyQt5.QtGui import (
    QPixmap, QIcon, QFont, QLinearGradient,
    QBrush, QPalette, QColor  # Added QColor here
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QSizePolicy
)
import requests
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz


class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.API_KEY = "ecbfb347643dcca7705690ad75b98b40"
        self.BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
        self.GEOCODING_TIMEOUT = 10
        self.ASSETS_DIR = self.resolve_assets_path()
        self.ICON_MAP = self.create_icon_mapping()
        self.init_ui()
        self.last_update = None

    def resolve_assets_path(self):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, "assets")

    def create_icon_mapping(self):
        return {
            "01d": "sun.png", "01n": "moon.png",
            "02d": "partly-cloudy.png", "02n": "partly-cloudy-night.png",
            "03d": "cloud.png", "03n": "cloud.png",
            "04d": "cloud.png", "04n": "cloud.png",
            "09d": "rain.png", "09n": "rain.png",
            "10d": "rain.png", "10n": "rain.png",
            "11d": "storm.png", "11n": "storm.png",
            "13d": "snow.png", "13n": "snow.png",
            "50d": "mist.png", "50n": "mist.png"
        }

    def init_ui(self):
        self.setWindowTitle("WeatherSphere")
        self.setMinimumSize(900, 600)
        self.setWindowIcon(QIcon(self.asset_path("app_icon.png")))
        self.setup_styles()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.create_search_bar(layout)
        self.create_weather_display(layout)
        self.create_footer(layout)

        QTimer.singleShot(0, self.load_default_location)

    def setup_styles(self):
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0, QColor(44, 62, 80))
        gradient.setColorAt(1, QColor(52, 73, 94))

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    def create_search_bar(self, parent_layout):
        search_container = QHBoxLayout()
        search_container.setContentsMargins(20, 20, 20, 30)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name...")
        self.city_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                color: white;
                font-size: 18px;
                padding: 12px 20px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.city_input.returnPressed.connect(self.fetch_weather)

        search_btn = QPushButton()
        search_btn.setIcon(QIcon(self.asset_path("search_icon.png")))
        search_btn.setIconSize(QSize(24, 24))
        search_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                border: none;
                border-radius: 15px;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:hover { background: #2980b9; }
            QPushButton:pressed { background: #1a5276; }
        """)
        search_btn.clicked.connect(self.fetch_weather)

        search_container.addWidget(self.city_input, 4)
        search_container.addWidget(search_btn, 1)
        parent_layout.addLayout(search_container)

    def create_weather_display(self, parent_layout):
        self.weather_container = QVBoxLayout()
        self.weather_container.setAlignment(Qt.AlignCenter)

        # Current weather
        self.weather_icon = QLabel()
        self.weather_icon.setAlignment(Qt.AlignCenter)
        self.weather_icon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.temp_label = QLabel()
        self.temp_label.setStyleSheet("""
            color: #ecf0f1;
            font-size: 72px;
            font-weight: 500;
            margin: 10px 0;
        """)

        self.condition_label = QLabel()
        self.condition_label.setStyleSheet("""
            color: #bdc3c7;
            font-size: 24px;
            text-transform: capitalize;
        """)

        # Details grid
        details_grid = QHBoxLayout()
        self.create_detail_card(details_grid, "Feels Like", "thermometer.png", "feels_like")
        self.create_detail_card(details_grid, "Humidity", "humidity.png", "humidity")
        self.create_detail_card(details_grid, "Wind", "wind.png", "wind")
        self.create_detail_card(details_grid, "Pressure", "pressure.png", "pressure")

        self.weather_container.addWidget(self.weather_icon)
        self.weather_container.addWidget(self.temp_label)
        self.weather_container.addWidget(self.condition_label)
        self.weather_container.addLayout(details_grid)
        parent_layout.addLayout(self.weather_container)

    def create_detail_card(self, layout, title, icon, key):
        card = QVBoxLayout()
        card.setSpacing(8)

        icon_label = QLabel()
        pixmap = QPixmap(self.asset_path(icon))
        icon_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 14px;
            font-weight: 500;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        self.value_label = QLabel("--")
        self.value_label.setObjectName(key)
        self.value_label.setStyleSheet("""
            color: #ecf0f1;
            font-size: 18px;
            font-weight: 600;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)

        card.addWidget(icon_label)
        card.addWidget(title_label)
        card.addWidget(self.value_label)
        layout.addLayout(card)

    def create_footer(self, parent_layout):
        footer = QHBoxLayout()
        footer.setContentsMargins(20, 20, 20, 10)

        self.location_label = QLabel()
        self.location_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")

        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")

        self.update_label = QLabel()
        self.update_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")

        footer.addWidget(self.location_label)
        footer.addStretch()
        footer.addWidget(self.time_label)
        footer.addStretch()
        footer.addWidget(self.update_label)
        parent_layout.addLayout(footer)

    def asset_path(self, filename):
        path = os.path.join(self.ASSETS_DIR, filename)
        if not os.path.exists(path):
            print(f"Missing asset: {path}")
        return path

    def load_default_location(self):
        self.city_input.setText("London")
        self.fetch_weather()

    def fetch_weather(self):
        city = self.city_input.text().strip()
        if not city:
            self.show_error("Please enter a city name")
            return

        try:
            # Get coordinates
            geolocator = Nominatim(user_agent="WeatherSphere/1.0", timeout=self.GEOCODING_TIMEOUT)
            location = geolocator.geocode(city, exactly_one=True, language='en')
            if not location:
                raise ValueError("Location not found")

            # Get weather data
            params = {
                'lat': location.latitude,
                'lon': location.longitude,
                'appid': self.API_KEY,
                'units': 'metric'
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Update display
            self.update_display(data, location)
            self.last_update = datetime.now()
            self.update_status()

        except requests.exceptions.RequestException as e:
            self.show_error(f"Network Error: {str(e)}")
        except Exception as e:
            self.show_error(str(e))

    def update_display(self, data, location):
        # Main weather
        self.set_weather_icon(data['weather'][0]['icon'])
        self.temp_label.setText(f"{data['main']['temp']:.1f}°C")
        self.condition_label.setText(data['weather'][0]['description'].capitalize())

        # Details
        self.update_detail('feels_like', f"{data['main']['feels_like']:.1f}°C")
        self.update_detail('humidity', f"{data['main']['humidity']}%")
        self.update_detail('wind', f"{data['wind']['speed']} m/s")
        self.update_detail('pressure', f"{data['main']['pressure']} hPa")

        # Location info
        self.location_label.setText(location.address.split(',')[0])
        timezone = self.get_timezone(location)
        self.time_label.setText(datetime.now(timezone).strftime("%I:%M %p"))

    def update_detail(self, key, value):
        if label := self.findChild(QLabel, key):
            label.setText(value)

    def set_weather_icon(self, icon_code):
        icon_file = self.ICON_MAP.get(icon_code, "logo.png")
        pixmap = QPixmap(self.asset_path(icon_file))

        if pixmap.isNull():
            pixmap = QPixmap(self.asset_path("logo.png"))

        pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.weather_icon.setPixmap(pixmap)

    def get_timezone(self, location):
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        return pytz.timezone(timezone_str)

    def update_status(self):
        if self.last_update:
            timestamp = self.last_update.strftime("%H:%M:%S")
            self.update_label.setText(f"Last update: {timestamp}")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.reset_display()

    def reset_display(self):
        self.temp_label.setText("--°C")
        self.condition_label.setText("")
        for field in ['feels_like', 'humidity', 'wind', 'pressure']:
            self.update_detail(field, "--")
        self.location_label.setText("")
        self.time_label.setText("")
        self.update_label.setText("")
        self.weather_icon.setPixmap(QPixmap(self.asset_path("logo.png")))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
