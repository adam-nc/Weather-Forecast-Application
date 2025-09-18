import csv
from datetime import datetime
from daily_forecast_class import DailyForecast


"""
The daily forecast manager class should load and store all daily forecast data from a csv file.
It should also store the forecast generation time and the forecast url.
It should contain: 
    - the name of the csv file
    - the time the forecast was generated at
    - the url of the forecast
    - a list of dictionaries containing the daily forecast for different persiods
"""
#implement the daily forecast manager class
class DailyForecastManager:
    #implement the constructor
    def __init__(self, file, generation_time):
        self._file = file
        self._generation_time = generation_time
        self._forecasts = []

    #a function to load forecasts
    def load_forecast(self):
        try:
            with open(self._file, newline='') as daily_file: # It should open the daily forecast file produced by the forecast worker
                reader = csv.DictReader(daily_file) # create a reader object similar to the writer object in ForecastWorker
                self._forecasts = [DailyForecast.entry_to_forecast_objects(row) for row in reader] # create a list of forecast objects for each forecast in the data file
            return True
        except Exception as e:  # If this is done successfully, return True; otherwise return False and print an error reading:
            print(f"Error loading daily forecasts: {e}")  # "Error loading daily forecasts: e" where e is the error raised during the run
            return False


    #write a getter for the forecasts
    def get_forecasts(self):
        return self._forecasts

    """
    TO STRING FUNCTION FORMAT:
        Daily forecast generated at: formatted_time
        Source URL: self.url
        forecast #1
        forecast #2
        ...
        forecast #n

    format the time with:
        datetime.fromisoformat()
    Use the return value to find the time zone like so:
        time zone = date/time return value.astimezone()
    Finalize the formatting with:
        formatted time = time zone.strftime('%I:%M %p')
    """

    #write a to string function that matches the format at the top of the file.
    def __str__(self):
        dt = datetime.fromisoformat(self._generation_time)
        time_zone = dt.astimezone()
        formatted_time = time_zone.strftime('%I:%M %p')

        #a very creative variable name
        function_output = [f"Daily forecast generated at: {formatted_time}"]

        for n, forecast in enumerate(self._forecasts, 1):
            function_output.append(f"\nforecast #{n}")
            function_output.append(str(forecast))

        #join then return as string
        return '\n'.join(function_output)



