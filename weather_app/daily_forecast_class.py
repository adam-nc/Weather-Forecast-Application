#function for converting Fahrenheit to Celsius(takes a float and returns a float)
def fahrenheit_to_celsius(fahrenheit):
    celsius = (fahrenheit - 32) * 5 / 9
    return celsius


#function for converting Celsius to Fahrenheit (takes a float and returns a float)
def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9 / 5) + 32
    return fahrenheit

"""
The daily forecast class for a single period of the day (e.g., Monday Night, Tuesday Afternoon, etc.).
The class should contain:
    - the period name
    - the temperature in both Fahrenheit and Celsius
    - the chance of rain
    - an icon URL
    - a detailed forecast string
"""
#define a daily forecast class
class DailyForecast:
    #define the constructor
    def __init__(self, period_name, temperature_fahrenheit, temperature_celsius, chance_of_rain, icon_url, detailed_forecast):
        self._period_name = period_name
        self._temperature_fahrenheit = temperature_fahrenheit
        self._temperature_celsius = temperature_celsius
        self._chance_of_rain = chance_of_rain
        self._icon_url = icon_url
        self._detailed_forecast = detailed_forecast


    #creates a function that is passed a dictionary and turns the entries into daily forecast objects
    @staticmethod
    def entry_to_forecast_objects(data: dict):
        temp_str = str(data.get("temperature", "")).strip() if data.get("temperature") else "" #formats temperature
        unit = data.get("temperature_unit", "").strip().upper() #For the temperature units, make sure to string extra spaces and capitalize the letter (C or F)

        #If either the temperature value or unit is empty, set the values to "N/A"
        temperature_display = "N/A"
        temperature_fahrenheit = "N/A"
        temperature_celsius = "N/A"

        if temp_str and unit in ("C", "F"):
            try:
                temp = float(temp_str)
                if unit == "F":
                    temperature_fahrenheit = temp
                    temperature_celsius = fahrenheit_to_celsius(temp)
                    temperature_display = f"{temperature_fahrenheit:.1f}°F ({temperature_celsius:.1f}°C)"
                else:
                    temperature_celsius = temp
                    temperature_fahrenheit = celsius_to_fahrenheit(temp)
                    temperature_display = f"{temperature_celsius:.1f}°C ({temperature_fahrenheit:.1f}°F)"
            except ValueError:
                print(f"Invalid value: {temp_str}")

        #formats precipitation
        precip_str = str(data.get("precipitation_probability_value", "")).strip()

        # make sure to strip additional spaces, if it isn't populated, set to 0
        # then format in the following manner: "💧chance%" (copy and paste the icon)
        try:
            chance_of_rain = f"💧{precip_str}%" if precip_str.isdigit() else "💧 0%"
        except ValueError:
                chance_of_rain = "💧 0%"

        #Extract rest of data
        period_name = data.get("name", "N/A")
        icon_url = data.get("weather_icon_url", "N/A")
        detailed_forecast = data.get("detailed_forecast", "N/A")

        #return a daily forecast object with the data pulled from the dictionary
        return DailyForecast(
            period_name = period_name,
            temperature_fahrenheit = temperature_display,
            temperature_celsius = "N/A",
            chance_of_rain = chance_of_rain,
            icon_url = icon_url,
            detailed_forecast = detailed_forecast
        )
