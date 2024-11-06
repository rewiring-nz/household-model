# Methodology

## Energy prices

We use average pricing over the next 15 years (real pricing, as opposed to nominal pricing). This is the average of the next 15 years of energy prices, projected out from today's prices at current real inflation rates. This is calculated using the average inflation from 2000 onwards for each energy type, using Stats NZ Quarterly Consumer Price Index History.

Table 1: Energy prices ($/kWh)

| Energy Type                                | Rate of Inflation (Real) | 2024 Prices | Average Pricing Over Next 15 Years (Real) |
|--------------------------------------------|--------------------------|-------------|-------------------------------------------|
| Natural Gas                                | 2.55%                    | $0.118    | $0.14161                                  |
| Natural Gas (Fixed Supply Charge - yearly) | 2.55%                    | $689.22675  | $827.10354                                |
| LPG                                        | 2.55%                    | $0.25452    | $0.30544                                  |
| LPG (Fixed Supply Charge - yearly)         | 2.55%                    | $69.00   | $82.80315                                 |
| Wood                                       | 1.86%                    | $0.11250    | $0.12837                                  |
| Electricity (volume rate)                  | 1.69%                    | $0.26175    | $0.29515                                  |
| Electricity (Fixed Supply Charge - yearly) | 1.69%                    | $767.7555  | $865.70526                                |
| Electricity (controlled)                   | 1.69%                    | $0.242    | $0.27287                                  |
| Electricity (night-rate)                   | 1.69%                    | $0.173    | $0.19507                                  |
| Electricity (solar feed-back tariff)        | 1.69%                    | $0.135    | $0.15222                                  |
| Petrol                                     | 3.29%                    | $0.28884    | $0.36584                                  |
| Diesel                                     | 3.29%                    | $0.19679    | $0.24925                                  |

## Emissions factors

These figures are taken from the Ministry for the Environment's [Measuring emissions: A guide for organisations (2023)](https://environment.govt.nz/assets/publications/Measuring-Emissions-Guidance_EmissionFactors_Summary_2023_ME1781.pdf).

| Energy Type   | Emissions Factor (kgCO₂e/kWh) |
|---------------|-------------------------------|
| Electricity   | 0.074                         |
| Natural Gas   | 0.201                         |
| LPG           | 0.219                         |
| Wood          | 0.016                         |
| Petrol        | 0.258                         |
| Diesel        | 0.253                         |

## Solar

- Assumes 0.5% degradation per year, which averages out to 6.92% degradation over 30 years, or 93.08% performance of nameplate capacity over 30 years.

## Battery

- Assumes 1% degradation per year, which averages out to 85.22% performance of nameplate capacity over 15 years.
- Assumes 5% losses in battery to the electronics & wiring within the battery itself
- Assumes that having a battery results in a 20% discount on the price of grid electricity, as it allows you to buy power at off-peak prices and 

## Vehicles

- Assumes average distance driven per vehicle per year is 10,950 km, rounded to 210 km per week. This is taken from 2019 stats on light passenger and light commercial vehicles from the [Ministry of Transport's Annual Fleet Statistics](https://www.transport.govt.nz/statistics-and-insights/fleet-statistics/annual-fleet-statistics/) for the year 2019, to avoid the anomalies from COVID-19.