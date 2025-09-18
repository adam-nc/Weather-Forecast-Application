import csv
import requests
from datetime import datetime
from geopy.location import Location
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication

"""
A worker that fetches weather data in the background.
"""
class ForecastWorker(QThread):
    """
    This line creates a signal object using the pyqtSignal function from the PyQt library.
    A signal lets different parts of your program communicate safely.
    Later, the program can use this signal object to send three pieces of information (strings)
    from the ForecastWorker thread (doing background tasks) back to your main program.
    Signal emits three strings: result message, generated_at_hourly, and hourly_forecast_url"
    It will tell the main program when we're done.
    """
    worker_finished = pyqtSignal(bool, str, str, str)

    """
    Initialize the ForecastWorker object by giving it the location from the user
    and set up this worker as a QThread.
    This is required so ForecastWorker can run its tasks in the background without freezing your program.
    """
    def __init__(self, location: Location) -> None:
        super().__init__()
        self.location = location

    
    def run(self) -> None:
        """
        This method starts running when the thread is activated.
        It fetches weather forecast data, saves it to CSV files, and signals the result.
        """
        try:
            # Step 1: Get location info from the API
            # Round latitude and longitude to 4 decimal places for consistency
            # Then use them to build the URL to retrieve local forecast endpoints
            latitude = round(self.location.latitude, 4)
            longitude = round(self.location.longitude, 4)
            location_url = f"https://api.weather.gov/points/{latitude},{longitude}"
            location_data = self._get_api_data(location_url)

            # Step 2: Get daily forecast
            # Use the forecast URL to request daily forecast data
            # Save the time it was generated (or current time if not provided)
            daily_forecast_url = location_data["properties"]["forecast"]
            daily_forecast_data = self._get_api_data(daily_forecast_url)
            daily_forecast_generated_time = (
                daily_forecast_data["properties"].get("generatedAt", datetime.now().isoformat())
            )
            # Write daily forecast data into a CSV file
            self._save_daily_forecast(daily_forecast_data)

            # Step 3: Get hourly forecast
            # Use the forecastHourly URL to request hourly forecast data
            # Save the time it was generated (or current time if not provided)
            hourly_forecast_url = location_data["properties"]["forecastHourly"]
            hourly_forecast_data = self._get_api_data(hourly_forecast_url)
            hourly_forecast_generated_time = (
                hourly_forecast_data["properties"].get("generatedAt", datetime.now().isoformat())
            )
            # Write hourly forecast data into a CSV file
            self._save_hourly_forecast(hourly_forecast_data)

            # Step 4: Signal that the operation succeeded
            # Send a success message, plus the times when each forecast was generated
            self.worker_finished.emit(
                True, "Forecast CSV files written", daily_forecast_generated_time, hourly_forecast_generated_time
            )
        # Handle network-related issues, like connection timeouts
        except requests.exceptions.RequestException as e:
            self.worker_finished.emit(False, f"Forecast fetch failed: {str(e)}", "", "")
        # Handle problems with unexpected or missing data in the API response
        except (KeyError, TypeError) as e:
            self.worker_finished.emit(False, f"Invalid API response format: {str(e)}", "", "")
        # Handle file writing errors, like permission issues or missing directories
        except (IOError, OSError) as e:
            self.worker_finished.emit(False, f"File save failed: {str(e)}", "", "")

    def _get_api_data(self, url: str) -> dict:
        """
        This helper method sends a GET request to the given API URL 
        and returns the response as a dictionary (parsed JSON).
    
        It includes headers to make sure we don’t get old, cached data.
        If the request fails (e.g., bad URL or network issue), it raises an error.
        """
        response = requests.get(url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"}, timeout=10)
        response.raise_for_status()  # Raises an error if request failed
        return response.json()

    def _save_daily_forecast(self, daily_forecast_data: dict) -> None:
        """Save daily forecast data to CSV"""
        daily_periods = daily_forecast_data["properties"]["periods"]

        #opens a csv file named 'daily_forecast_data.csv' in write mode
        with open("daily_forecast_data.csv", "w", newline ='') as daily_file:
            #creates a list of headers
            headers = ["forecast_period", "name", "start_time", "end_time", "isDaytime","temperature",
                   "temperature_unit", "temperature_trend","precipitation_probability_unit",
                   "precipitation_probability_value", "wind_speed", "wind_direction", "weather_icon_url",
                   "short_forecast", "detailed_forecast"]
            #creates a csv dictionary writer object using the file and fieldnames above
            writer = csv.DictWriter(daily_file, fieldnames=headers)
            #writes headers to file
            writer.writeheader()
            #loops through each item in daily_periods and writes it to the csv
            for period in daily_periods:
                writer.writerow({
                   "forecast_period": period.get("number", ""),
                   "name": period.get("name", ""),
                   "start_time": period.get("startTime", ""),
                   "end_time": period.get("endTime", ""),
                   "isDaytime": period.get("isDaytime", ""),
                   "temperature": period.get("temperature", ""),
                   "temperature_unit": period.get("temperatureUnit", ""),
                   "temperature_trend": period.get("temperatureTrend", ""),
                   "precipitation_probability_unit": period.get("probabilityOfPrecipitation", {}).get("unitCode", ""),
                   "precipitation_probability_value": period.get("probabilityOfPrecipitation", {}).get("value", ""),
                   "wind_speed": period.get("windSpeed", ""),
                  "wind_direction": period.get("windDirection", ""),
                 "weather_icon_url": period.get("icon", ""),
                 "short_forecast": period.get("shortForecast", ""),
                  "detailed_forecast": period.get("detailedForecast", "")})

    def _save_hourly_forecast(self, hourly_forecast_data: dict) -> None:
        """Save hourly forecast data to CSV"""
        hourly_periods = hourly_forecast_data["properties"]["periods"]

        #Opens a CSV file named 'hourly_forecast_data.csv' in write mode.
        with open("hourly_forecast_data.csv", "w", newline='') as hourly_file:
            #creates a list of headers
            headers = ["forecast_period", "start_time", "temperature", "temperature_unit",
               "precipitation_probability_unit", "precipitation_probability_value",
               "dewpoint_unit", "dewpoint_value", "relative_humidity_unit", "relative_humidity_value",
              "wind_speed", "wind_direction", "weather_icon_url", "short_forecast"]
            #creates a csv dictionary writer object using the file and fieldnames above
            writer = csv.DictWriter(hourly_file, fieldnames=headers)
            #writes headers to file
            writer.writeheader()
            #loops through each item in hourly_periods and writes it to the csv
            for period in hourly_periods:
                writer.writerow({
                   "forecast_period": period.get("number", ""),
                   "start_time": period.get("startTime", ""),
                   "temperature": period.get("temperature", ""),
                   "temperature_unit": period.get("temperatureUnit", ""),
                   "precipitation_probability_unit": period.get("probabilityOfPrecipitation", {}).get("unitCode", ""),
                   "precipitation_probability_value": period.get("probabilityOfPrecipitation", {}).get("value", ""),
                   "dewpoint_unit": period.get("dewpoint", {}).get("unitCode", ""),
                   "dewpoint_value": period.get("dewpoint", {}).get("value", ""),
                   "relative_humidity_unit": period.get("relativeHumidity", {}).get("unitCode", ""),
                   "relative_humidity_value": period.get("relativeHumidity", {}).get("value", ""),
                   "wind_speed": period.get("windSpeed", ""),
                   "wind_direction": period.get("windDirection", ""),
                   "weather_icon_url": period.get("icon", ""),
                   "short_forecast": period.get("shortForecast", "")})


def main():
    app = QCoreApplication([])

    # Create a dummy location (using coordinates for New York)
    location = Location("New York", (40.71282, -74.00603), {})

    worker = ForecastWorker(location)
    worker.worker_finished.connect(
        lambda success, message, daily_time, hourly_time: (
            print("Success:", success),
            print("Message:", message),
            print("Daily time:", daily_time),
            print("Hourly time:", hourly_time),
            app.quit()
        )
    )

    worker.start()
    app.exec_()


if __name__ == "__main__":
    main()
