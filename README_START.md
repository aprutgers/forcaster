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


