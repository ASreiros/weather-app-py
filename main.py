import requests
import smtplib
import os
from email.message import EmailMessage

# TODO 6 Temperatura vodi

OWM_ENDPOINT = "https://api.openweathermap.org/data/3.0/onecall"
MY_LAT = 55.66
MY_LNG = 21.18

params = {
	"appid": os.environ.get("OMW_API_KEY"),
	"lat": MY_LAT,
	"lon": MY_LNG,
	"units": "metric",
	"exclude": "minutely,daily"
}


def wind_name(wind_speed):
	if wind_speed < 3:
		w_name = "Почти нет ветра/штиль"
	elif wind_speed < 5:
		w_name = "Слабый ветер"
	elif wind_speed < 10:
		w_name = "Ветер средней силы"
	elif wind_speed < 15:
		w_name = "Сильный ветер"
	else:
		w_name = "Ураганный ветер"
	return w_name


def define_weather(t, f, w, g):
	text = f"Температура воздуха: {int(round(t))} градусов\nОщущается как: {int(round(f))} градусов\n"
	text += f"{wind_name(w)}\n"
	text += f'Скорость ветра: {int(round(w))} м/с\n'
	if g > w + 2:
		text += f'Порывы ветра: {int(round(g))} м/с\n'
	return text


def define_rain_text(rain, hr=8):
	rain_text = ""
	if len(rain) > 0:
		rain_text += "Дождь будет в: "
		for n in rain:
			rain_text += str(n + hr) + "  "
		rain_text += "часов"
	else:
		rain_text += "Дождя не будет"
	return rain_text


try:
	response = requests.get(url=OWM_ENDPOINT, params=params)
	response.raise_for_status()
	data = response.json()
	current = data["current"]
except Exception as e:
	print(e)
else:
	list_hourly = data["hourly"]
	temp_sum_list = [0, 0, 0, 0]
	temp_feel_list = [0, 0, 0, 0]
	wind_speed_list = [0, 0, 0, 0]
	wind_gust_list = [0, 0, 0, 0]
	rain_list = [[], [], [], []]
	for n in range(22):
		hour = list_hourly[n]
		weather = hour["weather"][0]

		weather_desc = weather["description"]
		weather_id = weather["id"]
		if n < 4:
			m = 0
		elif n < 10:
			m = 1
		elif n < 16:
			m = 2
		else:
			m = 3
		temp_sum_list[m] += float(hour["temp"])
		temp_feel_list[m] += float(hour["feels_like"])
		wind_speed_list[m] += float(hour["wind_speed"])
		wind_gust_list[m] += float(hour["wind_gust"])
		if int(weather_id) < 600:
			rain_list[m].append(n)
	temp_sum = int(round((sum(temp_sum_list)-temp_sum_list[3])/16))
	feel_sum = int(round((sum(temp_feel_list)-temp_feel_list[3])/16))
	wind_sum = int(round((sum(wind_speed_list)-wind_speed_list[3])/16))
	gust_sum = int(round((sum(wind_gust_list)-wind_gust_list[3])/16))

	weather_forecast_main= define_weather(temp_sum, feel_sum, wind_sum, gust_sum)
	rain_full_list = rain_list[0] + rain_list[1] + rain_list[2]
	weather_forecast_main += define_rain_text(rain_full_list)

	weather_forecast_ru = "Погода подробнее:"
	weather_forecast_ru += "\n--------------------------------------\n"
	weather_forecast_ru += "Погода утром(8-12):\n"
	weather_forecast_ru += define_weather(temp_sum_list[0]/4, temp_feel_list[0]/4, wind_speed_list[0]/4, wind_gust_list[0]/4)
	weather_forecast_ru += define_rain_text(rain_list[0])

	weather_forecast_ru += "\n--------------------------------------\n"
	weather_forecast_ru += "Погода днем(12-18):\n"
	weather_forecast_ru += define_weather(temp_sum_list[1]/6, temp_feel_list[1]/6, wind_speed_list[1]/6, wind_gust_list[1]/6)
	weather_forecast_ru += define_rain_text(rain_list[1])

	weather_forecast_ru += "\n--------------------------------------\n"
	weather_forecast_ru += "Погода вечером(18-24):\n"
	weather_forecast_ru += define_weather(temp_sum_list[2]/6, temp_feel_list[2]/6, wind_speed_list[2]/6, wind_gust_list[2]/6)
	weather_forecast_ru += define_rain_text(rain_list[2])

	weather_forecast_ru += "\n--------------------------------------\n"
	weather_forecast_ru += "Погода завтра ночью(0-6):\n"
	weather_forecast_ru += define_weather(temp_sum_list[3]/6, temp_feel_list[3]/6, wind_speed_list[3]/6, wind_gust_list[3]/6)
	weather_forecast_ru += define_rain_text(rain_list[3], -16)

	weather_forecast_ru += "\n\nЖелаю хорошего дня!!!\nАнтон"


	addresses = ["elenasokolkina@gmail.com", "gutoreva@gmail.com"]
	connection = smtplib.SMTP(os.environ.get("EMAIL_TEST_SMTP"), int(os.environ.get("EMAIL_TEST_PORT")))
	connection.starttls()
	connection.login(user=os.environ.get("EMAIL_TEST_NAME"), password=os.environ.get("EMAIL_TEST_PASSWORD"))

	msg = EmailMessage()
	msg['Subject'] = 'Прогноз погоды'
	msg['From'] = os.environ.get("EMAIL_TEST_NAME")
	msg['To'] = addresses
	msg.set_content(weather_forecast_main + "\n\n\n\n" + weather_forecast_ru)
	connection.send_message(msg)
	connection.close()

	BOT_TOKEN = os.environ.get("BOT_TOKEN")
	chat = "-903822745"
	# chat_test = "-972102355"
	url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat}&text={weather_forecast_main}"
	requests.get(url).json()

	url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat}&text={weather_forecast_ru}"
	requests.get(url).json()

