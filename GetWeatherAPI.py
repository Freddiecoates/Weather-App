import requests
import datetime as dt

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = "7f60b92f2d07989763505b34b9a84347"
CITY = input("Input a city: ")

url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY

response = requests.get(url).json()


def kelvinconversion(kelvin):
    celcius = kelvin - 273.15
    fahrenheit = celcius * (9/5) + 32
    return celcius, fahrenheit

temp_kelvin = response['main']['temp']
temp_celcius, temp_fahrenheit = kelvinconversion(temp_kelvin)
feels_like_kelvin = response['main']['feels_like']
feels_like_celcius, feels_like_fahrenheit = kelvinconversion(feels_like_kelvin)
humidity = response['main']['humidity']
description =  response['weather'][0]['description']
sunrise_time = dt.datetime.fromtimestamp(response['sys']['sunrise'] + response['timezone'])
sunset_time = dt.datetime.fromtimestamp(response['sys']['sunset'] + response['timezone'])
wind_speed = response['wind']['speed']

print(f"Temperature in {CITY}: {temp_celcius:.2f}°C or {temp_fahrenheit:.2f}°F")
print(f"Temperature in {CITY} Feels like: {feels_like_celcius:.2f}°C or Feels like: {feels_like_fahrenheit:.2f}°F")
print(f"Humidity in {CITY}: {humidity}%")
print(f"Wind Speed in {CITY}: {wind_speed}m/s")
print(f"General weather in {CITY}: {description}")
print(f"Sun rises in {CITY} at {sunrise_time} local time.")
print(f"Sun sets in {CITY} at {sunset_time} local time.")


