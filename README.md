# ﻿Weather Forecast Application

### How the System Works
This system is made up of several key components that work together to retrieve, store, and display weather forecast data.

#### 1. Retrieving Weather Data
- The system connects to an **external weather service** using an API.
- The API provides weather data for a specific location, including temperature, chance of rain, wind speed, and other relevant conditions.
- The system requests **two types of forecasts**: a **daily forecast** (covering multiple days) and an **hourly forecast** (covering a more detailed breakdown).
- This data is retrieved by a **ForecastWorker**, a background process that ensures the system remains responsive while waiting for data from the online service.

#### 2. Storing and Organizing Data
- The retrieved forecast data is **saved in CSV files** for easier access and processing.
- The system has two main classes for storing forecasts:
  - **DailyForecast**: Stores forecast details for a given day.
  - **HourlyForecast**: Stores forecast details for a specific hour.
- Each forecast object stores **temperature values in both Fahrenheit and Celsius**, converting between the two when necessary.
- Forecast objects also include details like weather condition icons (e.g., ☀️ for sunny, 🌧️ for rain), precipitation probability, and wind information.

#### 3. Managing Forecast Data
- The system uses two management classes:
  - **DailyForecastManager**: Loads and organizes daily forecast data.
  - **HourlyForecastManager**: Loads and organizes hourly forecast data.
- These managers read data from the CSV files and transform it into structured objects that can be used by the rest of the system.
- The system ensures data is formatted in a user-friendly way, including converting temperature units and formatting times.
