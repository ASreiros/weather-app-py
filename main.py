from hidden_info import *
import requests
import smtplib

OWM_ENDPOINT = "https://api.openweathermap.org/data/3.0/onecall"
params = {
	"appid": api_key,
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
except:
	pass
else:

	weather_forecast = f"Temperatura: {current['temp']}\nOsiusiajetsia kak: {current['feels_like']}\n"
	list_hourly = data["hourly"]
	print(list_hourly)

	rain_list = []
	for n in range(16):
		weather = list_hourly[n]["weather"][0]["main"]
		weather_desc = list_hourly[n]["weather"][0]["description"]
		weather_id = list_hourly[n]["weather"][0]["id"]
		if int(weather_id) < 600:
			rain_list.append(n)
		print(weather)
		print(weather_desc)
		print(weather_id)
		print(n)
		print("-----")

	if len(rain_list) > 0:
		weather_forecast +="Dozd budet v: "
		for n in rain_list:
			weather_forecast += str(n+9) + " "
		weather_forecast += "casov"
	else:
		weather_forecast += "Dozdia ne budet"

	addresses = ["elenasokolkina@gmail.com", "ansokolkin@gmail.com" ]
	connection = smtplib.SMTP(smtp_info, port)
	connection.starttls()
	connection.login(user=email, password=password)
	connection.sendmail(
		from_addr=email,
		to_addrs=addresses,
		msg=f"Subject:Prognoz pogodi ot Antona\n\n {weather_forecast}")
	connection.close()
