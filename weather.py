import requests, sys, time
import os.path
from collections import OrderedDict

"""
This project should:
Execute from commandline with two arguments: api key, and output csv filepath
The process called from commandline should:
    1) Get current weather for Boston, San Francisco, and London
    2) Append to existing CSV, or create new if one doesn't exist the following:
        1 Row per city
        Units should be in imperial (fahrenheit, feet etc)
        Columns should be: City Name | Date (human readable) | Temp | Weather Description (e.g. "Few clouds") | Pressure | Humidity
"""

CITY_GEO_COORDINATES = {
    'boston': (42.3, -71.1),
    'san francisco': (37.7, -122.4),
    'london': (51.5, -0.1)
}


class OpenWeatherApi(object):
    def __init__(self, api_key):
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        self.api_key = api_key

    def _get(self, endpoint, **arguments):
        """
        Calls api and returns response object

        :param endpoint:  string, e.g. '/puppies'
        :param arguments: N number of keyword arguments to be passed to rest call
        :return: requests response object
        """
        argument_string = self._format_arguments(**arguments)
        r = requests.get(f'{self.base_url}{endpoint}{argument_string}', verify=False)
        return r

    def _format_arguments(self, **arguments):
        """
        Formats input keyword arguments into REST arguments string, e.g.:
        Given input: name='joe', height='6ft', location='Boston'
        Returns: '?name=joe&height=6ft&location=Boston'

        :param arguments: keyword arguments
        :return: string
        """
        arguments_li = [f'{k}={v}' for k, v in arguments.items()]
        return '?' + '&'.join(arguments_li) + f'&appid={self.api_key}'

    def get_weather_for_city(self, city):
        """
        Gets weather for the given city and returns dictionary like:
        {
         'city': 'Boston',
         'date': '10/23/2022',
         'temperature': 50.1,
         'description': 'Partly Cloudy',
         'pressure': 1026,
         'humidity': 35
        }

        :param city: string, e.g. 'boston'
        :return: dictionary
        """
        latitude = CITY_GEO_COORDINATES[city.lower()][0]
        longitude = CITY_GEO_COORDINATES[city.lower()][1]
        response = self._get('/onecall', lat=latitude, lon=longitude, exclude='hourly,daily,minutely', units='imperial')
        response_di = response.json()['current']

        return OrderedDict({
            'city': city,
            'date': time.strftime('%m/%d/%Y', time.localtime(response_di['dt'])),
            'temperature': response_di['temp'],
            'description': response_di['weather'][0]['description'],
            'pressure': response_di['pressure'],
            'humidity': response_di['humidity']
        })


def di_to_csv(input_li_of_di, filepath):
    """
    Given an input list of dictionaries, will create a csv file at the given filepath (if not exist),
    and add rows to that csv where each dictionary in the input list represents a single row.

    Note:
    If the csv file does not yet exist, then the header row will be created from the keys of the first
    input dictionary

    :param input_li_of_di: list of dictionaries, where each dictionary is one row
    :param filepath: e.g. './csv/weather.csv'
    :return:
    """
    csv_exists = os.path.isfile(filepath)

    # Format input data into lists of just the values
    list_of_value_li = list()
    for di in input_li_of_di:
        list_of_value_li.append([str(v) for k, v in di.items()])

    # Create header row if CSV doesn't exist yet
    if not csv_exists:
        list_of_value_li.insert(0, list(input_li_of_di[0].keys()))

    # Format entire list into a list of CSV format strings
    csv_rows_li = [','.join(li) for li in list_of_value_li]

    with open(filepath, 'a') as f:
        for line in csv_rows_li:
            f.write(line + '\n')


if __name__ == '__main__':
    api_key = sys.argv[1]
    outputfilepath = sys.argv[2]
    if not outputfilepath.endswith('.csv'):
        outputfilepath += '.csv'

    api_object = OpenWeatherApi(api_key)

    # Get weather for all cities
    cities = ['boston', 'san francisco', 'london']
    weather_li = list()
    for city in cities:
        weather_li.append(api_object.get_weather_for_city(city))

    # Output to CSV
    di_to_csv(weather_li, outputfilepath)
