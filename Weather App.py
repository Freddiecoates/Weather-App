from tkinter import *
import tkinter as tk
import requests
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz


def getweather():
    CITY = textfield.get()
    CITY.capitalize()

    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(CITY)
    obj = TimezoneFinder()
    result = obj.timezone_at(lng=location.longitude, lat=location.latitude)

    home = pytz.timezone(result)
    local_time = datetime.now(home)
    current_time = local_time.strftime("%I:%M %p")
    clock.config(text=current_time)
    name.config(text="CURRENT WEATHER")

    # weather API

    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
    API_KEY = "ecbfb347643dcca7705690ad75b98b40"

    url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY

    response = requests.get(url).json()

    temp_kelvin = response['main']['temp']
    feels_like_kelvin = response['main']['feels_like']
    humidity = response['main']['humidity']
    description = response['weather'][0]['description']
    wind_speed = response['wind']['speed']
    pressure = response['main']['pressure']
    description.capitalize()

    celsius = f"{temp_kelvin - 273.15:.1f}"
    feelsLike = f"{feels_like_kelvin - 273.15:.1f}"

    c.config(text=f"{celsius}°C", font=("Arial", 45, 'bold'))
    t.config(text=f"Feels Like {feelsLike}°C", font=("arial", 15, 'bold'))
    h.config(text=f"{humidity}%")
    d.config(text=description)
    p.config(text=pressure)
    w.config(text=f"{wind_speed}m/s")

    """if 'rain' in description:
        logo_image = PhotoImage(file="rain.png")
    elif 'clear' in description:
        logo_image = PhotoImage(file="sun.png")
    elif 'storm' in description:
        logo_image = PhotoImage(file="storm.png")
    elif 'wind' in description:
        logo_image = PhotoImage(file="wind.png")
    elif 'cloud' in description:
        logo_image = PhotoImage(file="cloudy.png")
    elif 'mist' in description:
        logo_image = PhotoImage(file="mist.png")
    else:
        logo_image = PhotoImage(file="logo.png")

    logo.config(image=logo_image)
    logo.image = logo_image"""


root = Tk()
root.title("Weather")
root.geometry("900x500+300+200")
root.resizable(False, False)

search_image = PhotoImage(file="search.png")
myimage = Label(image=search_image)
myimage.place(x=20, y=20)

textfield = tk.Entry(highlightthickness=4, highlightcolor="black", highlightbackground="black", justify="center",
                     width=17, font=("poppins", 25, "bold"), bg="#404040", border=0, fg="white", textvariable="City")
textfield.place(x=85, y=38)
textfield.focus()

# Search icon
search_image = PhotoImage(file="search_icon.png")
myimage_icon = Button(image=search_image, borderwidth=0, cursor="hand2", bg="#404040", command=getweather)
myimage_icon.place(x=400, y=34)

# Logo
logo_image = PhotoImage(file="logo.png")
logo = Label(image=logo_image)
logo.place(x=150, y=100)

# Bottom box
frame_image = PhotoImage(file="box.png")
frame_myimage = Label(master=root, image=frame_image)
frame_myimage.pack(padx=5, pady=5, side=BOTTOM)

# time
name = Label(root, font=("arial", 15, "bold"))
name.place(x=30, y=100)
clock = Label(master=root, font=("Helvetica", 20))
clock.place(x=30, y=130)

# Label
label1 = Label(root, text="WIND", font=("Helvetica", 15, 'bold'), fg='white', bg="#1ab5ef")
label1.place(x=120, y=400)

label2 = Label(root, text="HUMIDITY", font=("Helvetica", 15, 'bold'), fg='white', bg="#1ab5ef")
label2.place(x=250, y=400)

label3 = Label(root, text="DESCRIPTION", font=("Helvetica", 15, 'bold'), fg='white', bg="#1ab5ef")
label3.place(x=430, y=400)

label4 = Label(root, text="PRESSURE", font=("Helvetica", 15, 'bold'), fg='white', bg="#1ab5ef")
label4.place(x=650, y=400)

t = Label(font=("arial", 70, "bold"), fg="#ee666d")
t.place(x=400, y=150)
c = Label(font=("arial", 15, "bold"))
c.place(x=400, y=250)

w = Label(text="...", font=("arial", 20, 'bold'), bg="#1ab5ef")
w.place(x=110, y=430)
h = Label(text="...", font=("arial", 20, 'bold'), bg="#1ab5ef")
h.place(x=270, y=430)
d = Label(text="...", font=("arial", 20, 'bold'), bg="#1ab5ef")
d.place(x=445, y=430)
p = Label(text="...", font=("arial", 20, 'bold'), bg="#1ab5ef")
p.place(x=685, y=430)

root.mainloop()
