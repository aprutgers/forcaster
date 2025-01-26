# Solar Panel Power Forcaster

APR Digital Studios Project to collect and record data to train a model that can forcast solar panel output.

## Input training data (each hour)

* Meteo watt/m3 `gr_w` and total cloud coverage `tc`
* Solar3P predicted solar panel power for home installation
* Actual produced solar panel power from home installation
* Actual power returned to the network from smartmeter

Actual produced solar panel power is retrieved trough the local Enphase gateway in the lan network trough a documented API:
* Manual: https://enphase.com/download/accessing-iq-gateway-local-apis-or-local-ui-token-based-authentication
* Locatie-id: 3220284
* Gateway SN: 122151028718
* Gateway IP: 192.168.2.1

## Training and Models

TODO

## Inference

TODO

# Generated Code Documentation (per file)


# get_enphase_hour_measure.py Documentation

This script retrieves hourly energy production data from an Enphase Envoy system and inserts it into a MySQL database.

## Functionality

The script performs the following actions:

1. **Retrieves an Enphase web token:**  It attempts to retrieve a valid web token from a cached file. If the token is not found or invalid, it obtains one from the Enphase Enlighten platform using provided credentials stored in a `.env` file.  The token is then cached for subsequent use.

2. **Retrieves Enphase energy data:** Using the obtained web token, it makes an API call to the Enphase Envoy (at a specified IP address) to fetch current energy production data, including:
    * `wattHoursToday`: Total watt-hours produced today.
    * `wattHoursSevenDays`: Total watt-hours produced in the last seven days.
    * `wattHoursLifetime`: Total watt-hours produced since installation.
    * `wattsNow`: Current power production in watts.

3. **Inserts data into MySQL database:** The retrieved data, along with the current timestamp (year, month, day, hour, minute), is inserted into the `enphase_production` table of a MySQL database.

## Dependencies

* `os`
* `sys`
* `mysql.connector`
* `datetime`
* `requests`
* `json`
* `log` (custom logging module - assumed to be defined elsewhere)
* `math`
* `dotenv`


## Configuration

The script requires a `.env` file in the same directory containing the following environment variables:

* `ENVOY_USER`: Enphase Enlighten username.
* `ENVOY_PASSWORD`: Enphase Enlighten password.
* `ENVOY_SERIAL`: Enphase Envoy serial number.

The script also connects to a MySQL database.  The database credentials are hardcoded within the `insert_enphase_production` function (currently using `user='root', database='homepowerdb'`).  It's highly recommended to move these credentials to an `.env` file for security reasons.


##  Error Handling

The script includes basic error handling by checking for the existence of a cached token and using `requests.packages.urllib3.disable_warnings()` to suppress warnings related to SSL verification.  More robust error handling (e.g., handling API request failures, database connection errors) should be added for production use.


## Usage

Run the script from the command line:  `python get_enphase_hour_measure.py`

##  Database Table Structure

The `enphase_production` table should have the following columns:

```sql
`year` DECIMAL(4,0) NOT NULL,
`month` DECIMAL(2,0) NOT NULL,
`day` DECIMAL(2,0) NOT NULL,
`hour` DECIMAL(2,0) NOT NULL,
`minute` DECIMAL(2,0) NOT NULL,
`wattHoursToday` DECIMAL(10,5) NOT NULL,
`wattHoursSevenDays` DECIMAL(10,5) NOT NULL,
`wattHoursLifetime` DECIMAL(10,5) NOT NULL,
`wattsNow` DECIMAL(10,5) NOT NULL,
`created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
```

##  Note:

The script directly accesses the Enphase Envoy using its IP address (`https://192.168.2.1/ivp/pdm/energy`). This approach bypasses the Enphase Enlighten API and may not be suitable for all setups.  Consider using the official Enphase Enlighten API for a more robust and supported method.  Also, disabling SSL verification (`verify=False`) is generally discouraged in production environments.

# history_collector.py Documentation

This script collects historical photovoltaic (PV) system data and stores it in a MySQL database. It retrieves data from various sources, including Enphase energy production data, weather forecasts, and Solar3P predictions.


## File: `history_collector.py`

This script performs the following actions:

1. **Connects to a MySQL database:** Establishes a connection to a MySQL database (`homepowerdb`) using the root user.  Ensure the database and user exist before running the script.

2. **Retrieves data:** Collects data from multiple sources:
    * **Enphase Production:** Extracts hourly PV energy production (`wattHoursToday`) from the `enphase_production` table. It handles day wrapping where `wattHoursToday` resets to 0 at midnight.
    * **Meteo Forecast:** Loads weather forecast data (global horizontal irradiance `gr_w` and temperature `tc`) from a JSON file located at `/home/ec2-user/solar3p/data/data.rotterdam`.  The filename (`rotterdam`) is configurable.
    * **Solar3P Forecast:** Retrieves PV power production forecast from a `solar3p` module (assumed to be a custom module).
    * **Power Returned to Grid:**  Retrieves the amount of power returned to the grid (`kwh_prod`) from the `hour_usage_prices` table.


3. **Calculates Delta:** Determines the change in energy production between consecutive hours (`delta_wattHoursToday`).

4. **Inserts data into database:** Stores the collected and calculated data into the `pvhistory` table.

## Database Table: `pvhistory`

The script interacts with the `pvhistory` table in the `homepowerdb` database. The table structure is as follows:

| Column Name     | Data Type    | Description                                      |
|-----------------|---------------|--------------------------------------------------|
| `year`          | INT           | Year of the data                                 |
| `month`         | INT           | Month of the data                                |
| `day`           | INT           | Day of the data                                  |
| `hour`          | INT           | Hour of the data                                 |
| `gr_w`          | DECIMAL(10,5) | Global horizontal irradiance (W/m²)              |
| `tc`            | DECIMAL(10,5) | Temperature (°C)                                 |
| `kwh_pv`        | DECIMAL(10,5) | PV energy production in kWh (delta between hours) |
| `kwh_s3p`       | DECIMAL(10,5) | Solar3P forecast in kWh                           |
| `kwh_return`    | DECIMAL(10,5) | Power returned to the grid in kWh                 |


## Functions:

* **`insert_hour_pvhistory(conn, now, gr_w, tc, kwh_pv, kwh_s3p, kwh_return)`:** Inserts a new row into the `pvhistory` table.
* **`load_meteo_forcast_data(g_file)`:** Loads meteo forecast data from a JSON file.
* **`get_day_hour_forcast(location, now)`:** Retrieves the meteo forecast for a specific day and hour.
* **`get_pv_production(conn, now)`:** Retrieves PV production data from the database.
* **`get_solar3p_forcast(now)`:** Retrieves Solar3P forecast data.
* **`get_pv_watt_returned(conn, now)`:** Retrieves power returned to the grid data.
* **`main()`:** The main function that orchestrates the data collection and insertion process.


## Dependencies:

* `mysql.connector`
* `datetime`
* `json`
* `log` (assumed to be a custom logging module)
* `solar3p` (assumed to be a custom module for Solar3P interaction)


## Configuration:

* Database connection details (currently hardcoded in `main()`).
* Meteo forecast data file path (hardcoded in `load_meteo_forcast_data()`).
* Solar3P parameters (hardcoded in `get_solar3p_forcast()`).  These parameters should be moved to a configuration file for better maintainability.

Remember to install the necessary dependencies before running the script.  Adjust database credentials and file paths to match your environment.

