import csv
from datetime import datetime
from hourly_forecast_class import HourlyForecast

"""
The hourly forecast manager class should load and store all houly forecast data from a csv file.
It should also store the forecast generation time.
It should contain: 
    - the name of the csv file
    - the time the forecast was generated at
    - a list of dictionaries containing the daily forecast for different periods
"""
#Create an Hourly Forecast Manager Class
class HourlyForecastManager:
    def __init__(self, csv_file_name):
        self._csv_file_name = csv_file_name
        self._forecasts = []
        self._forecast_generation_time = None

    # Create a method to read forecasts from the csv file and create hourly forecast objects from the data
    # If this is done successfully, return True; otherwise return False and print an error reading:
    #    "Error loading daily forecasts: e" where e is the erorr raised during the run
    def read_forecasts_from_csv(self):
        try:
            with open(self._csv_file_name, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                header = reader.fieldnames
                if not reader.fieldnames:
                    raise ValueError("CSV file is empty or has no headers.")
                for row in reader:
                    # check for missing values
                    for key, value in row.items():
                        if value == '':
                            row[key] = None
                    forecast_object = HourlyForecast.data_to_objects(row)  # Use the class method
                    self._forecasts.append(forecast_object)

                # Get forecast generation time from the first row, if available
                if self._forecasts:
                    first_forecast = self._forecasts[0]
                    if first_forecast.start_time_raw:  # check if start_time_raw exists
                        try:
                            # parse the time.
                            forecast_gen_time = datetime.fromisoformat(first_forecast.start_time_raw)
                            self._forecast_generation_time = forecast_gen_time
                        except ValueError:
                            self._forecast_generation_time = None
                    else:
                        self._forecast_generation_time = None
                else:
                    self._forecast_generation_time = None

            return True
        except Exception as e:
            print(f"Error loading daily forecasts: {e}")
            return False

    # write a getter for the forecasts
    def get_forecasts(self):
        return self._forecasts

    def get_forecast_generation_time(self):
        return self._forecast_generation_time

    def __str__(self):
        return f"HourlyForecastManager(csv_file_name='{self._csv_file_name}', num_forecasts={len(self._forecasts)}, generation_time={self._forecast_generation_time})"


if __name__ == "__main__":
    csv_file = "daily_forecast_data.csv"
    forecast_manager = HourlyForecastManager(csv_file)
    if forecast_manager.read_forecasts_from_csv():
        forecasts = forecast_manager.get_forecasts()
        generation_time = forecast_manager.get_forecast_generation_time()

        print(f"Forecast Generation Time: {generation_time}")
        print(f"Number of forecasts loaded: {len(forecasts)}")
        if forecasts:
            print("First forecast:")
            print(forecasts[0])
        else:
            print("No forecasts loaded.")
    else:
        print("Failed to load forecasts.")
