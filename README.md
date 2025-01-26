# get_enphase_hour_measure.py Documentation

This script retrieves hourly energy production data from an Enphase Envoy and inserts it into a MySQL database.

## Functionality

The script performs the following actions:

1. **Obtains an Enphase Web Token:** It retrieves an authentication token from Enphase's Enlighten platform.  The token is cached locally to avoid repeated authentication requests.  Credentials are loaded from a `.env` file.

2. **Retrieves Energy Data:** Uses the token to make an API request to the Enphase Envoy (at a specified IP address) to fetch current energy production data, including:
    * `wattHoursToday`: Total watt-hours produced today.
    * `wattHoursSevenDays`: Total watt-hours produced in the last seven days.
    * `wattHoursLifetime`: Total watt-hours produced since installation.
    * `wattsNow`: Current power production in watts.

3. **Inserts Data into MySQL:** Inserts the retrieved data along with the current timestamp into a MySQL database table named `enphase_production`.  The table structure is defined within the script.

## Dependencies

* `os`
* `sys`
* `mysql.connector`
* `datetime`
* `requests`
* `json`
* `log` (Assumed to be a custom logging module)
* `math`
* `dotenv`


## Configuration

The script relies on environment variables stored in a `.env` file:

* `ENVOY_USER`: Enphase Enlighten username.
* `ENVOY_PASSWORD`: Enphase Enlighten password.
* `ENVOY_SERIAL`: Enphase Envoy serial number.

These variables are loaded using the `load_dotenv()` function.  Ensure that the `.env` file is present in the same directory as the script.

## Database Configuration

The script connects to a MySQL database using the following hardcoded credentials:

* `user`: 'root'
* `database`: 'homepowerdb'

Modify these values if necessary to match your database setup.

## Usage

To run the script:

1.  Ensure all dependencies are installed (`pip install mysql-connector-python requests python-dotenv`).
2.  Create a `.env` file with the required environment variables.
3.  Run the script from the command line: `python get_enphase_hour_measure.py`


## Logging

The script uses a custom logging module (`log`) for debugging and informational messages. The specific implementation of this module is not included in this documentation.


## Potential Issues

* **Network Connectivity:** The script requires network access to both Enphase's servers and the local Enphase Envoy.
* **Authentication Errors:** Incorrect credentials will prevent the script from retrieving data.
* **API Changes:** Changes to the Enphase API might break the script.
* **Database Errors:** Problems connecting to or writing to the MySQL database will cause errors.


## Notes:

The script uses `requests.get(url, headers=headers,verify=False)` which disables SSL verification.  This should only be used in trusted environments and is generally **not recommended** for production systems.  Consider using appropriate SSL certificates for secure communication.  The IP address `192.168.2.1` needs to be replaced with your Envoy's actual IP address.

# history_collector.py Documentation

This script collects historical photovoltaic (PV) power generation data and meteorological data, then stores it in a MySQL database.  It uses data from Enphase Energy systems and a weather forecast API (presumably accessed through the `solar3p` module).


## File: history_collector.py

This script performs the following actions:

1. **Connects to a MySQL database:** Establishes a connection to the `homepowerdb` database using the `root` user.  Database credentials should be modified for production use.
2. **Retrieves historical PV generation data:** Queries the `enphase_production` table to get the total watt-hours generated for the past hour. Handles potential day-wrapping issues where `wattHoursToday` resets to 0 at midnight.
3. **Retrieves meteorological forecast data:**  Uses the `get_day_hour_forcast` function to obtain global horizontal irradiance (`gr_w`) and temperature (`tc`) from a forecast file (located at `/home/ec2-user/solar3p/data/data.rotterdam`). The forecast data is assumed to be in JSON format.
4. **Retrieves solar3p forecast data:** Uses the `solar3p` module to get a power forecast in kW for the past hour.  Defaults are set for prediction period, number of panels, panel wattage, orientation, granularity, and data file.
5. **Inserts data into the `pvhistory` table:**  Adds a new record to the `pvhistory` table containing the collected data (year, month, day, hour, `gr_w`, `tc`, PV generation in kWh, solar3p forecast in kWh, and power returned to the network (currently set to 0)).

## `pvhistory` Table Schema

The script interacts with a MySQL table named `pvhistory` with the following columns:

| Column Name    | Data Type     | Description                                      |
|----------------|----------------|--------------------------------------------------|
| `year`         | INT            | Year of the data                                |
| `month`        | INT            | Month of the data                               |
| `day`          | INT            | Day of the data                                 |
| `hour`         | DECIMAL(2,0)   | Hour of the data                                |
| `gr_w`         | DECIMAL(10,5)  | Global horizontal irradiance (W/m²)             |
| `tc`           | DECIMAL(10,5)  | Temperature (°C)                               |
| `kwh_pv`       | DECIMAL(10,5)  | PV power generated (kWh)                        |
| `kwh_s3p`      | DECIMAL(10,5)  | Solar3p forecasted power generation (kWh)       |
| `kwh_return`   | DECIMAL(10,5)  | Power returned to the network (kWh)             |


## Functions

* **`insert_hour_pvhistory(conn, now, gr_w, tc, kwh_pv, kwh_s3p, kwh_return)`:** Inserts a single row into the `pvhistory` table.
* **`get_meteo_data(hour)`:** (Currently unused)  Intended to retrieve meteorological data.
* **`load_meteo_forcast_data(g_file)`:** Loads meteorological forecast data from a JSON file.
* **`get_day_hour_forcast(location, now)`:** Retrieves the forecast for a specific date and time from the loaded forecast data.  Performs a linear search.
* **`get_pv_production(conn, now)`:** Retrieves PV production data from the `enphase_production` table for a given hour.
* **`get_solar3p_forcast(now)`:** Retrieves a solar3p power forecast for a given hour.
* **`main()`:** The main function that orchestrates the data collection and insertion process.


## Dependencies

* `os`
* `sys`
* `mysql.connector`
* `datetime`
* `json`
* `log` (custom logging module, assumed to be defined elsewhere)
* `solar3p` (custom module for accessing solar3p forecast data, assumed to be defined elsewhere)


## Notes

* The script uses hardcoded values for database credentials, file paths, and default parameters for solar3p forecasts. These should be configurable for production deployments.
* Error handling is minimal.  More robust error handling and logging should be implemented.
* The linear search in `get_day_hour_forcast` could be optimized for large datasets.


This documentation provides a basic overview. Further details may be found within the code itself and accompanying modules.

