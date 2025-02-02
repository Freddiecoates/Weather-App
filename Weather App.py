import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                             QMessageBox)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
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
        self.ICON_MAP = {
            "01d": "sun.png",
            "01n": "moon.png",
            "02d": "partly-cloudy.png",
            "02n": "partly-cloudy-night.png",
            "03d": "cloud.png",
            "03n": "cloud.png",
            "04d": "cloud.png",
            "04n": "cloud.png",
            "09d": "rain.png",
            "09n": "rain.png",
            "10d": "rain.png",
            "10n": "rain.png",
            "11d": "storm.png",
            "11n": "storm.png",
            "13d": "snow.png",
            "13n": "snow.png",
            "50d": "mist.png",
            "50n": "mist.png"
        }
        self.ASSETS_DIR = "assets"
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Weather App")
        self.setFixedSize(900, 600)
        self.setStyleSheet("""
            background-color: #2c3e50;
            font-family: 'Arial';
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        #search Area
        search_container = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter City Name")
        self.city_input.setStyleSheet("""
            QLineEdit {
                background: #404040;
                border: 2px solid #34495e;
                border-radius: 15px;
                color: white;
                font-size: 18px;
                padding: 12px 20px;
                min-width: 300px;
            }
        """)

        search_btn = QPushButton()
        search_btn.setIcon(QIcon(self.asset_path("search_icon.png")))
        search_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                border: none;
                border-radius: 15px;
                padding: 12px;
                margin-left: 10px;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        search_btn.clicked.connect(self.fetch_weather)

        search_container.addWidget(self.city_input)
        search_container.addWidget(search_btn)
        layout.addLayout(search_container)

        #weather Icon
        self.weather_icon = QLabel()
        self.weather_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.weather_icon)

        #temperature Display
        self.temp_label = QLabel()
        self.temp_label.setStyleSheet("""
            color: #e74c3c;
            font-size: 72px;
            font-weight: bold;
            margin: 20px 0;
        """)
        layout.addWidget(self.temp_label, alignment=Qt.AlignCenter)

        #location and time
        self.location_label = QLabel()
        self.location_label.setStyleSheet("color: #ecf0f1; font-size: 20px;")
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #bdc3c7; font-size: 16px;")
        layout.addWidget(self.location_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.time_label, alignment=Qt.AlignCenter)

        #weather details
        details_layout = QHBoxLayout()
        self.create_detail_card(details_layout, "WIND", "wind.png")
        self.create_detail_card(details_layout, "HUMIDITY", "humidity.png")
        self.create_detail_card(details_layout, "PRESSURE", "pressure.png")
        self.create_detail_card(details_layout, "FEELS LIKE", "thermometer.png")
        layout.addLayout(details_layout)

    def asset_path(self, filename):
        return os.path.join(self.ASSETS_DIR, filename)

    def create_detail_card(self, layout, title, icon):
        card = QVBoxLayout()
        card.setSpacing(10)

        #icon
        icon_label = QLabel()
        pixmap = QPixmap(self.asset_path(icon))
        if pixmap.isNull():
            print(f"Missing icon: {icon}")
        icon_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignCenter)

        #title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #bdc3c7; font-size: 14px;")
        title_label.setAlignment(Qt.AlignCenter)

        #value
        value_label = QLabel("...")
        value_label.setObjectName(title.lower().replace(" ", "_"))
        value_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignCenter)

        card.addWidget(icon_label)
        card.addWidget(title_label)
        card.addWidget(value_label)
        layout.addLayout(card)

    def fetch_weather(self):
        try:
            city = self.city_input.text().strip()
            if not city:
                self.show_error("Please enter a city name")
                return

            geolocator = Nominatim(user_agent="WeatherApp/1.0")
            location = geolocator.geocode(city, exactly_one=True, timeout=10)
            if not location:
                self.show_error("City not found")
                return

            params = {
                "lat": location.latitude,
                "lon": location.longitude,
                "appid": self.API_KEY,
                "units": "metric"
            }

            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            self.update_display(data, location)

        except requests.exceptions.RequestException as e:
            self.show_error(f"API Error: {str(e)}")
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")

    def update_display(self, data, location):
        #weather icon
        icon_code = data["weather"][0]["icon"]
        self.set_weather_icon(icon_code)

        #temperature
        temp = data["main"]["temp"]
        self.temp_label.setText(f"{temp:.1f}°C")

        #location and time
        self.location_label.setText(location.address.split(',')[0])
        timezone_str = TimezoneFinder().timezone_at(lng=location.longitude, lat=location.latitude)
        current_time = datetime.now(pytz.timezone(timezone_str)).strftime("%I:%M %p, %A")
        self.time_label.setText(current_time)

        #weather details
        self.findChild(QLabel, "wind").setText(f"{data['wind']['speed']} m/s")
        self.findChild(QLabel, "humidity").setText(f"{data['main']['humidity']}%")
        self.findChild(QLabel, "pressure").setText(f"{data['main']['pressure']} hPa")
        self.findChild(QLabel, "feels_like").setText(f"{data['main']['feels_like']:.1f}°C")

    def set_weather_icon(self, icon_code):
        icon_file = self.ICON_MAP.get(icon_code, "logo.png")
        pixmap = QPixmap(self.asset_path(icon_file))

        if pixmap.isNull():
            print(f"Missing weather icon: {icon_file}")
            pixmap = QPixmap(self.asset_path("logo.png"))

        self.weather_icon.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
