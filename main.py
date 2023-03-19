import requests
import smtplib
import os

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
try:
	response = requests.get(url=OWM_ENDPOINT, params=params)
	response.raise_for_status()
	data = response.json()
	current = data["current"]
except Exception as e:
	print(e)
else:
	wind_name = ""
	wind_name_ru = ""
	if int(data["current"]["wind_speed"])< 3:
		wind_name = "Net vetra"
		wind_name_ru = "Почти нет ветра"
	elif int(data["current"]["wind_speed"])< 5:
		wind_name = "Slabij veter"
		wind_name_ru = "Слабый ветер"
	elif int(data["current"]["wind_speed"]) < 10:
		wind_name = "Srednij veter"
		wind_name_ru = "Ветер средней силы"
	elif int(data["current"]["wind_speed"]) < 15:
		wind_name = "Silnij veter"
		wind_name_ru = "Сильный ветер"
	else:
		wind_name = "Uraganij veter"
		wind_name_ru = "Ураганный ветер"

	weather_forecast = f"Temperatura: {round(int(current['temp']))}\nOsiusiajetsia kak: {round(int(current['feels_like']))}\n"
	weather_forecast_ru = f"Температура воздуха: {round(int(current['temp']))} градусов\nОщущается как: {round(int(current['feels_like']))} градусов\n"
	weather_forecast += f"{wind_name}\n"
	weather_forecast_ru += f"{wind_name_ru}\n"
	weather_forecast +=f'Skorost vetra: {round(int(data["current"]["wind_speed"]))} m/s\nPorivi vetra: {round(int(data["current"]["wind_gust"]))} m/s\n'
	weather_forecast_ru += f'Скорость ветра: {round(int(data["current"]["wind_speed"]))} м/с\nПорывы ветра: {round(int(data["current"]["wind_gust"]))} м/с\n'
	list_hourly = data["hourly"]

	rain_list = []
	for n in range(16):
		weather = list_hourly[n]["weather"][0]["main"]
		weather_desc = list_hourly[n]["weather"][0]["description"]
		weather_id = list_hourly[n]["weather"][0]["id"]
		if int(weather_id) < 600:
			rain_list.append(n)

	if len(rain_list) > 0:
		weather_forecast +="Dozd budet v: "
		weather_forecast_ru += "Дождь будет в: "
		for n in rain_list:
			weather_forecast += str(n+9) + " "
		weather_forecast += "casov"
		weather_forecast_ru += "часов"
	else:
		weather_forecast += "Dozdia ne budet"
		weather_forecast_ru += "Дождя не будет"

	addresses = ["elenasokolkina@gmail.com", "ansokolkin@gmail.com", "ira-s@bk.ru", "gutoreva@gmail.com"]
	connection = smtplib.SMTP(os.environ.get("EMAIL_TEST_SMTP"), int(os.environ.get("EMAIL_TEST_PORT")))
	connection.starttls()
	connection.login(user=os.environ.get("EMAIL_TEST_NAME"), password=os.environ.get("EMAIL_TEST_PASSWORD"))
	connection.sendmail(
		from_addr=os.environ.get("EMAIL_TEST_NAME"),
		to_addrs=addresses,
		msg=f"Subject:Prognoz pogodi ot Antona\n\n {weather_forecast}")
	connection.close()

	BOT_TOKEN = os.environ.get("BOT_TOKEN")
	chat = "-903822745"
	url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat}&text={weather_forecast_ru}"
	requests.get(url).json()

