#import the datetime library from the datetime module
from datetime import datetime

#conversion function for Fahrenheit to Celsius (takes a float and returns a float)
def fahrenheit_to_celsius(fahrenheit):
    celsius = (fahrenheit - 32) * 5 / 9
    return celsius

#conversion function for Celsius to Fahrenheit (takes a float and returns a float)
def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9 / 5) + 32
    return fahrenheit

#define a method that gets the appropriate weather emoji from a forecast's icon
def get_emoji(url):
    #parse the url parameter
    #The method will be passed a url. If there is no url, an empty string should be returned.
    if not url:
        return ""
    # Retrieve the base of the url by using the split operation
    url_base = url.split('?')[0]
    #split the base into parts, each of which will be separated by forward slash('/').
    base_parts = url_base.split('/')

    # Extract the weather condition from the parts. It will be the last element (hint: there's an easy way
    # to find this in Python). Make sure the condition is in lower case for consistent results.
    if not base_parts:
        return ""

    weather_condition = base_parts[-1].lower()

    #Check for multiple conditions
    # the condition may actually be a list of conditions separated by commas. If so, we will consider only
    # the first condition relevant. So it should be extracted.
    if ',' in weather_condition:
        weather_condition = weather_condition.split(',')[0]

    #Create a dictionary to map icons to emojis (provided below because I don't hate you)
    mapping = {
        "skc": "☀️",  # clear sky
        "few": "🌤️",  # few clouds
        "sct": "⛅",  # scattered clouds
        "bkn": "☁️",  # broken clouds
        "ovc": "☁️",  # overcast
        "sn": "❄️",  # snow
        "ra_sn": "🌨️",  # rain and snow mix
        "raip": "🌧️",  # rain with ice pellets
        "fzra": "🌧️",  # freezing rain
        "ra_fzra": "🌧️",  # rain/freezing rain mix
        "fzra_sn": "🌨️",  # freezing rain and snow
        "ip": "🧊",  # ice pellets
        "snip": "❄️",  # snow pellets
        "minus_ra": "🌦️",  # light rain
        "ra": "🌧️",  # rain
        "shra": "🌧️",  # showers
        "hi_shwrs": "🌧️",  # heavy showers
        "tsra": "⛈️",  # thunderstorms
        "scttsra": "⛈️",  # scattered thunderstorms
        "hi_tsra": "⛈️",  # heavy thunderstorms
        "fc": "🌪️",  # funnel cloud
        "tor": "🌪️",  # tornado
        "hur_warn": "🌀",  # hurricane warning
        "hur_watch": "🌀",  # hurricane watch
        "ts_warn": "⛈️",  # thunderstorm warning
        "ts_watch": "⛈️",  # thunderstorm watch
        "ts_nowarn": "⛈️",  # thunderstorm, no warning
        "wind_skc": "🌬️",  # clear with wind
        "wind_few": "🌬️",  # few clouds with wind
        "wind_sct": "🌬️",  # scattered clouds with wind
        "wind_bkn": "🌬️",  # broken clouds with wind
        "wind_ovc": "🌬️",  # overcast with wind
        "du": "🌫️",  # dust
        "fu": "🌫️",  # smoke/fugitive dust
        "hz": "🌫️",  # haze
        "hot": "🥵",  # hot
        "cold": "🥶",  # cold
        "blizzard": "🌨️",  # blizzard
        "fg": "🌫️",  # fog
    }

    #Find correct emoji for current condition
    # For each key/value pair in the dictionary, see if the key is in the condition.
    # If so, return that emoji; otherwise, return a question mark.
    for key, value in mapping.items():
        if key in weather_condition:
            return value

        return "?"


"""
A class representing a single hourly forecast period with formatted data.
The class should contain:
    - forecast period
    - start time
    - forecast date
    - the temperature in both Fahrenheit and Celsius
    - the chance of rain
    - the dewpoint in both Fahrenheit and Celsius
    - the relative humidity
    - the wind conditions
    - the weather icon url
    - a short forecast description
"""
#implement the Hourly Forecast Class
class HourlyForecast:
    def __init__(self, forecast_period, formatted_date, forecast_hour, temperature_fahrenheit, temperature_celsius,
                 chance_of_rain, dewpoint_fahrenheit, dewpoint_celsius, relative_humidity, wind, weather_icon, short_forecast):
        self._forecast_period = forecast_period
        self._formatted_date = formatted_date
        self._forecast_hour = forecast_hour
        self._temperature_fahrenheit = temperature_fahrenheit
        self._temperature_celsius = temperature_celsius
        self._chance_of_rain = chance_of_rain
        self._dewpoint_fahrenheit = dewpoint_fahrenheit
        self._dewpoint_celsius = dewpoint_celsius
        self._relative_humidity = relative_humidity
        self._wind = wind
        self._weather_icon = weather_icon
        self._short_forecast = short_forecast


    # TODO: create a method theat will convert data from a dictionary to an Hourly Forecast Object
    @staticmethod
    def data_to_objects(data):
        # extract each attribute from the dictionary parameter
        # the start time in the dictionary will initially contain both the time and the date. These
        # will need separated based on the value in the start time.
        start_time_raw = data.get('start_time')

        # format start time
        # if there is not start time, the formatted date and forecast hour should both be set to "N/A"
        # otherwise, try to use the following line to extract the start time properly formatted:
        #   date/time = datetime.fromisoformat(start time)
        # then use the following lines to extract the date and hour:
        #   formatted date = date/time.strftime("%A, %b %d")  # e.g., "Wednesday, Feb 26"
        #   forecast hour = date/time.strftime("%I:%M %p")
        # If that fails, expect a value error and set both date and hour to "N/A"
        if start_time_raw:
            try:
                date_time = datetime.fromisoformat(start_time_raw)
                formatted_date = date_time.strftime("%A, %b %d")
                forecast_hour = date_time.strftime("%I:%M %p")
            except ValueError:
                formatted_date = "N/A"
                forecast_hour = "N/A"



        # format temperature
        # For the temperature units, make sure to strip extra spaces and capitalize the letter (C or F)
        # If either the temperature value or unit is not populated, set the values to "N/A"
        # Otherwise, try converting the temperature from strings to floats
        # then convert to populate the other temperature unit (if it's F convert to C, and vice versa)
        # Here's the degree symbol for your convenience: °
        temperature_fahrenheit = "N/A"
        temperature_celsius = "N/A"
        temperature_str = data.get('temperature')
        temperature_unit_raw = data.get('temperature_unit')
        if temperature_str is not None and temperature_unit_raw:
            unit = temperature_unit_raw.strip().upper()
            try:
                temp_value = float(temperature_str)
                if unit == 'F':
                    temperature_fahrenheit = f"{temp_value}°F"
                    temperature_celsius = f"{fahrenheit_to_celsius(temp_value):.1f}°C"
                elif unit == 'C':
                    temperature_celsius = f"{temp_value}°C"
                    temperature_fahrenheit = f"{celsius_to_fahrenheit(temp_value):.1f}°F"
            except ValueError:
                pass

    
        # format precipitation
        # make sure to strip additional spaces, if it isn't populated, set to 0
        # then format in the following manner: "💧chance%" (copy and paste the icon)
        chance_of_rain = "💧0%"
        precip_prob_str = data.get('precipitation_probability_value')
        if precip_prob_str is not None:
            try:
                prob = int(precip_prob_str)
                chance_of_rain = f"💧{prob}%"
            except ValueError:
                pass

        # format dewpoint
        # Extract the dewpoint and unit making sure to strip spaces and capitolize.
        # If neither is populated set both F and C dewpoints to "N/A"
        # Otherwise, try to cast the dewpoint as a float.
        # Then convert to populate the other temperature unit (if it's F convert to C, and vice versa)
        # Expect the dewpoint using to be either "WMOUNIT:DEGC" or "WMOUNIT:DEGF"
        dewpoint_fahrenheit = "N/A"
        dewpoint_celsius = "N/A"
        detailed_forecast = data.get('detailed_forecast')
        if detailed_forecast:
            dew_f_val = None
            dew_c_val = None
            f_start = detailed_forecast.find("dewpoint around ")
            if f_start != -1:
                f_end = detailed_forecast.find(" F", f_start)
                if f_end != -1:
                    try:
                        dew_f_val = float(detailed_forecast[f_start + 16:f_end])
                        dewpoint_fahrenheit = f"{dew_f_val}°F"
                        dewpoint_celsius = f"{fahrenheit_to_celsius(dew_f_val):.1f}°C"
                    except ValueError:
                        pass

            c_start = detailed_forecast.find("dewpoint around ")
            if c_start != -1:
                c_end = detailed_forecast.find(" C", c_start)
                if c_end != -1:
                    try:
                        dew_c_val = float(detailed_forecast[c_start + 16:c_end])
                        dewpoint_celsius = f"{dew_c_val}°C"
                        dewpoint_fahrenheit = f"{celsius_to_fahrenheit(dew_c_val):.1f}°F"
                    except ValueError:
                        pass

        # TODO: format humitify
        # Extract the humitity probability percent. If populated, follow the value with a percent sign.
        # Otherwise, set to "N/A".
        relative_humidity = "N/A"
        if detailed_forecast:
            hum_start = detailed_forecast.find('humidity ')
            if hum_start != -1:
                hum_end = detailed_forecast.find("%", hum_start)
                if hum_end != -1:
                    try:
                        relative_humidity = detailed_forecast[hum_start:hum_end+1]
                    except ValueError:
                        pass

        # format wind conditions
        # Extract the wind speed and direction. If populated, string the direction and format "speed direction".
        # Otherwise, set to "N/A".
        wind = "N/A"
        wind_speed = data.get('wind_speed')
        wind_direction = data.get('wind_direction')
        if wind_speed and wind_direction:
            speed = wind_speed.strip()
            direction = wind_direction.strip().upper()
            wind = f"{speed} {direction}"

        # Get emoji to represent weather icon
        # Extract the url and icon
        weather_icon = get_emoji(data.get('weather_icon_url'))
        short_forecast = data.get('short_forecast')
        forecast_period = data.get('forecast_period')

        # return an Hourly Forecast Object with the values extracted above
        return HourlyForecast(
            forecast_period, formatted_date, forecast_hour, temperature_fahrenheit, temperature_celsius,
            chance_of_rain, dewpoint_fahrenheit, dewpoint_celsius, relative_humidity, wind, weather_icon, short_forecast
        )

