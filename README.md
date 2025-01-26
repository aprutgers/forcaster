= Solar Panel Power Forcaster

Project to collect and record data to train a model that can forcast solar panel output

== Input training data (each hour)
* Meteo watt/m3 `gr_w` and total cloud coverage `tc`
* Solar3P predicted solar panel power for home installation
* Actual produced solar panel power from home installation
* Actual power returned to the network from smartmeter

== Training and Models

TODO

== Inference

TODO


# get_enphase_hour_measure.py Documentation

This script retrieves hourly energy production data from an Enphase Envoy and inserts it into a MySQL database.  It uses the Enphase Enlighten API and handles authentication securely.

## Functionality

The script performs the following actions:

1. **Authentication:**
   - It retrieves an Enphase web token, either from a cached file or by authenticating with the Enphase Enlighten API using credentials stored in a `.env` file (ENVOY_USER, ENVOY_PASSWORD, ENVOY_SERIAL).  The token is cached for subsequent runs to avoid repeated logins.

2. **Data Retrieval:**
   - It uses the retrieved token to make an API request to the Enphase Envoy (local IP address assumed) to fetch current energy production data, including:
     - `wattHoursToday`: Total watt-hours produced today.
     - `wattHoursSevenDays`: Total watt-hours produced in the last seven days.
     - `wattHoursLifetime`: Total watt-hours produced since installation.
     - `wattsNow`: Current power production in watts.

3. **Database Insertion:**
   - It inserts the retrieved data into the `enphase_production` table in a MySQL database (`homepowerdb`). The table structure is defined within the script.  The data includes the current year, month, day, hour, and minute.

## Dependencies

- `os`
- `sys`
- `mysql.connector`
- `datetime`
- `requests`
- `json`
- `log` (Assumed to be a custom logging module)
- `math` (Not explicitly used in the provided code, but may be used in other parts of the `log` module)
- `dotenv`


## Configuration

- A `.env` file in the same directory as the script must contain the following environment variables:
    - `ENVOY_USER`: Enphase Enlighten username.
    - `ENVOY_PASSWORD`: Enphase Enlighten password.
    - `ENVOY_SERIAL`: Enphase Envoy serial number.

- MySQL connection details are hardcoded within the `insert_enphase_production` function (user='root', database='homepowerdb').  These should be modified to match your MySQL server configuration.

- The script assumes the Enphase Envoy is accessible at `https://192.168.2.1/ivp/pdm/energy`.  Adjust this URL if necessary.

- The script caches the Enphase web token in `/home/ec2-user/forcaster/.cached_enphase_web_token`. Adjust the path if needed.


## Usage

Run the script from the command line:

```bash
python get_enphase_hour_measure.py
```

## Error Handling

The script includes basic logging using a custom `log` module.  More robust error handling (e.g., exception handling for API requests, database connections) could be added for improved reliability.  The script also disables SSL verification (`requests.packages.urllib3.disable_warnings()` and `verify=False`), which is a security risk and should be avoided unless absolutely necessary and the implications are fully understood.

## Notes

- The script assumes a specific table structure in the MySQL database.  Adapt the SQL statement if your table schema differs.
- The script currently runs only once. Consider adding scheduling capabilities using cron or a similar task scheduler for regular execution.
- Consider using a more secure method for storing credentials than a `.env` file, particularly in production environments.  Secrets management tools are recommended.

# history_collector.py Documentation

This script collects and stores photovoltaic (PV) system data into a MySQL database. It retrieves data from various sources, including Enphase energy production data, meteorological forecasts, and Solar3P predictions.

## File: `history_collector.py`

This script performs the following functions:

1. **Connects to a MySQL database:** Establishes a connection to the `homepowerdb` database using the root user.  Ensure appropriate database credentials are set.

2. **Retrieves data:** Collects data from different sources:
    * **Enphase Production:**  Extracts hourly energy production (`wattHoursToday`) from the `enphase_production` table.  Handles day wrapping where `wattHoursToday` resets to 0 at midnight.
    * **Meteorological Forecast:** Loads weather forecast data (global radiation `gr_w` and temperature `tc`) from a JSON file located at `/home/ec2-user/solar3p/data/data.<location>`, where `<location>` is a parameter (e.g., 'rotterdam').  It performs a linear search for the matching timestamp.
    * **Solar3P Forecast:** Retrieves a PV power forecast in kW from the `solar3p` module.  Uses default parameters unless otherwise specified.
    * **Power Returned to Grid:** Gets the amount of power returned to the grid (`kwh_prod`) from the `hour_usage_prices` table.

3. **Calculates Key Metrics:** Computes the difference in energy production between consecutive hours (`delta_wattHoursToday`).

4. **Inserts Data into Database:** Stores the collected and calculated data into the `pvhistory` table.

## Database Table: `pvhistory`

The script interacts with the `pvhistory` table, which has the following columns:

| Column Name    | Data Type    | Description                                      |
|----------------|---------------|--------------------------------------------------|
| `year`         | INT           | Year of the recorded data                       |
| `month`        | INT           | Month of the recorded data                      |
| `day`          | INT           | Day of the recorded data                        |
| `hour`         | INT           | Hour of the recorded data                       |
| `gr_w`         | DECIMAL(10,5) | Global radiation (W/m²) from meteorological forecast |
| `tc`           | DECIMAL(10,5) | Temperature (°C) from meteorological forecast     |
| `kwh_pv`       | DECIMAL(10,5) | PV energy generated (kWh) during the hour       |
| `kwh_s3p`      | DECIMAL(10,5) | Predicted PV energy generation (kWh) from Solar3P |
| `kwh_return`   | DECIMAL(10,5) | Energy returned to the grid (kWh)               |


## Functions:

* **`insert_hour_pvhistory(conn, now, gr_w, tc, kwh_pv, kwh_s3p, kwh_return)`:** Inserts a single row into the `pvhistory` table.
* **`load_meteo_forcast_data(g_file)`:** Loads meteorological forecast data from a JSON file.
* **`get_day_hour_forcast(location, now)`:** Retrieves the meteorological forecast for a specific location and timestamp.
* **`get_pv_production(conn, now)`:** Retrieves PV energy production data from the database.
* **`get_solar3p_forcast(now)`:** Retrieves PV power forecast from the `solar3p` module.
* **`get_pv_watt_returned(conn, now)`:** Retrieves the power returned to the grid from the database.
* **`main()`:** The main function that orchestrates the data collection and insertion process.


## Dependencies:

* `os`
* `sys`
* `mysql.connector`
* `datetime`
* `json`
* `log` (custom logging module - assumed to be defined elsewhere)
* `math`
* `solar3p` (custom module for Solar3P predictions - assumed to be defined elsewhere)


## Error Handling:

The script includes basic error handling, primarily logging errors using the `log` module.  More robust error handling might be beneficial in a production environment.

## Configuration:

The script uses hardcoded values for database credentials and file paths. Consider using configuration files for better maintainability and flexibility.  The location of the meteo forecast data is hardcoded.

