import datetime
import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, send_file
import urllib.parse
from geopy.geocoders import Nominatim
from countryinfo import CountryInfo
import boto3
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter
import logging
#from elasticsearch import Elasticsearch
#from logging.handlers import RotatingFileHandler


#es = Elasticsearch(['http://54.160.199.184:9200'])
app = Flask(__name__)
app.config['BG_COLOR'] = os.environ.get('BG_COLOR')
geolocator = Nominatim(user_agent="server")
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')
city_search_count = Counter('city_search_count', 'Number of times a city has been searched', ['city'])
#handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
#handler.setLevel(logging.INFO)
#app.logger.addHandler(handler)

logging.info('Application Running!')
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename="/logs/app.log")

"""
def log_to_elasticsearch(record):
    es.index(index='flask_logs', body={
        'timestamp': datetime.now(),
        'level': record.levelname,
        'message': record.getMessage()
    })

handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
handler.setFormatter(log_to_elasticsearch)
"""


@app.route('/', methods=['GET'])
def index():
    """
    :return: Landing page
    """
    bg_color = os.environ.get('BG_COLOR')
    #print(bg_color)
    app.logger.warning("user asks for home page")
    return render_template('index.html', bg_color=bg_color)


metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

@app.route('/error', methods=['GET'])
def err():
    """
    :return A rendered template of an error page
    """
    app.logger.error("user entered invalid input")
    return render_template('err.html')


def getcountry(cityname):
    """
    Returns the country name from a name of a city (reversed_geocoding)
    Meteo-API returns country name in different languages, so we use this function
    to retreive country name by reverse geocoding and represent it with the corresponding city
    """
    loc = geolocator.geocode(cityname)
    country = geolocator.reverse(f"{loc.latitude},{loc.longitude}", language='en').raw['address'].get('country', '')
    return country


def change_date(var):
    """
    Function that receives a list of formatted data and replaces the Date and Time data with the current day of the week
    and a Symbol of sunshine and moon for the current time
    """
    days = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    for i in var:
        # print([i['date'][11:13]])
        i['date'] = days[datetime.datetime.strptime(i['date'], '%Y-%m-%d %H:%M').weekday()] + " " + (
            "☼" if int(i['date'][11:13]) < 12 else "☽")
    return var


def getweather(lat, lon):
    """
    Gets Latitude and Longitude as an arguments and returns the weather forecast for those coordinates
    Also filtering methods used here to filter the data we need for which we extract from API
    """
    new_url = 'https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&hourly=temperature_2m,' \
              'relativehumidity_2m'.format(lat, lon)
    new_response = requests.get(new_url).json()
    forecast = []
    # filter the data and append it to empty forecast list
    for hour in new_response['hourly']['time']:
        if hour.endswith('09:00') or hour.endswith('21:00'):
            index = new_response['hourly']['time'].index(hour)
            forecast.append(
                {
                    'date': hour,
                    'temperature': new_response['hourly']['temperature_2m'][index],
                    'humidity': new_response['hourly']['relativehumidity_2m'][index]}
            )
    # modification of data
    # Remove T in date to format the data with strptime function
    for item in forecast:
        item['date'] = item['date'].replace('T', " ")
    change_date(forecast)
   # dynamodb = boto3.resource('dynamodb')
   # table = dynamodb.Table('webapplication')
   # response = table.put_item(Item={"weather": city+" "+country+"_"+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
   # "forecast": str(forecast)})
    return forecast

def save_search_data(data):
    filename = "{}_{}.json".format(data["name"], data["date"])
    with open(filename, "w") as f:
        json.dump(data, f)

@app.route('/weather', methods=['POST'])
def weather():
    """
    Gets the input from the user (city name), uses functions and returns render template of html file with forecast
    """
    city = request.form['city']
    city_search_count.labels(city).inc()
    if str.isnumeric(city):
        return redirect(url_for('err'))
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(city) + '?format=json'
    response = requests.get(url).json()
    if response:
        save_path = './data'
        os.makedirs(save_path, exist_ok=True)
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        file_name = f'{current_time}_{city}.json'
        file_path = os.path.join(save_path, file_name)
        lat, lon = response[0]['lat'], response[0]['lon']
        country = getcountry(city)
        # get information about capital city of country
        capital_info = CountryInfo(country)
        # capital_city holds the name of the capital city of {country}
        capital_city = capital_info.capital()
        if country in city:
            new_forecast = capital_info.capital_latlng()
            forecast = getweather(new_forecast[0], new_forecast[1])
            app.logger.warning("User typed a country" +country)
            with open(file_path, 'w') as f:
                json.dump(forecast, f)
            return render_template('weather.html', forecast=forecast, country=country, capital=capital_city)

        forecast = getweather(lat, lon)
        app.logger.warning("user typed a city" +city)
        with open(file_path, 'w') as f:
            json.dump(forecast, f)
        return render_template('weather.html', forecast=forecast, city=city, country=country)
    else:
        app.logger.error("User entered invalid input")
        return redirect(url_for('err'))


@app.post('/dynamo')
def data():
	if request.method == 'POST':
		city = request.form.get("city")
		country=request.form.get("country")
		url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(city) + '?format=json'
		response = requests.get(url).json()
		lat, lon = response[0]['lat'], response[0]['lon']
		country = getcountry(city)
		forecast = getweather(lat, lon)
		print(forecast)
		print(type(forecast))
		dynamodb = boto3.resource('dynamodb')
		table = dynamodb.Table('webapplication')
		print(table.creation_date_time)
		table.put_item(
		Item={
		'weather': city+" "+country+"_"+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'forecast' : str(forecast)})
	return redirect(url_for('index'))

@app.route('/history')
def history():
    """
    Displays a list of links to the saved weather data files.
    """
    save_path = './data'
    files = [f for f in os.listdir(save_path) if os.path.isfile(os.path.join(save_path, f))]
    file_links = []
    for file in files:
        file_path = os.path.join(save_path, file)
        file_links.append(f'<a href="{file_path}" download>{file}</a>')
    return '<br>'.join(file_links)


@app.route('/data/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    """
    Downloads a saved weather data file.
    """
    save_path = f'data/{filename}'
    return send_file(save_path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

