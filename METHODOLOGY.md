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
- Assumes a static capacity factor per region, although this is likely to change over the next 30 years:

| Region                 | Solar capacity factor (%) |
|------------------------|---------------------------|
| Northland             | 15.5%                     |
| Auckland North        | 15.5%                     |
| Auckland Central      | 15.5%                     |
| Auckland East         | 15.5%                     |
| Auckland West         | 15.5%                     |
| Auckland South        | 15.5%                     |
| Waikato               | 15.5%                     |
| Bay of Plenty         | 15.5%                     |
| Gisborne              | 15.0%                     |
| Hawkes Bay            | 15.0%                     |
| Taranaki              | 15.0%                     |
| Manawatu Wanganui     | 15.0%                     |
| Wellington            | 14.9%                     |
| Tasman                | 15.0%                     |
| Nelson                | 15.5%                     |
| Marlborough           | 15.0%                     |
| West Coast            | 15.0%                     |
| Canterbury            | 14.3%                     |
| Otago                 | 12.5%                     |
| Southland             | 12.5%                     |
| Stewart Island        | 12.5%                     |
| Chatham Islands       | 12.5%                     |
| Great Barrier Island  | 15.0%                     |
| Overseas              | 15.0%                     |
| Other                 | 15.0%                     |


## Battery

- Assumes 1% degradation per year, which averages out to 85.22% performance of nameplate capacity over 15 years.
- Assumes 5% losses in battery to the electronics & wiring within the battery itself
- Assumes that having a battery results in a 20% discount on the price of grid electricity, as it allows you to buy power at off-peak prices and 

## Vehicles

- Assumes average distance driven per vehicle per year is 10,950 km, rounded to 210 km per week. This is taken from 2019 stats on light passenger and light commercial vehicles from the [Ministry of Transport's Annual Fleet Statistics](https://www.transport.govt.nz/statistics-and-insights/fleet-statistics/annual-fleet-statistics/) for the year 2019, to avoid the anomalies from COVID-19.
- Assumes current Road User Charges (RUCs) without taking inflation or policy changes into account.
    - Electric: $76 per year per 1000km
    - Plug-in hybrid: $38 per year per 1000km
    - Hybrid: $0 per year per 1000km
    - Petrol: $0 per year per 1000km
    - Diesel: $76 per year per 1000km

## Occupancy

The energy needs of the household have been scaled from the NZ averages based on occupancy ratios from the [Australian Energy Regulator Electricity and Gas consumption benchmarks for residential customers 2020 study](https://www.aer.gov.au/industry/registers/resources/guidelines/electricity-and-gas-consumption-benchmarks-residential-customers-2020).

We used the numbers for climate zone 6 (Mild temperate, such as urban Melbourne, Adelaide Hills, Ulladulla; [see Table 1 on page 15](https://www.aer.gov.au/system/files/Residential%20energy%20consumption%20benchmarks%20-%209%20December%202020_0.pdf)). Using the spreadsheet of [Frontier Economics - Simple electricity and gas benchmarks - From June 2021](https://www.aer.gov.au/documents/frontier-economics-simple-electricity-and-gas-benchmarks-june-2021) and taking an average across all states and seasons, we found the following electricity consumption and ratios.

We did not use the separate gas energy consumption numbers as we were only requiring an idea of a ratio, and when we calculated the ratios, where wasn't a material difference with the electricity consumption ratios.

| Household Size | Average Electricity Use per Season (kWh) | Ratio |
|----------------|-----------------------------------------|-------|
| 1              | 803                                     | 1.0   |
| 2              | 1,328                                   | 1.7   |
| 3              | 1,410                                   | 1.8   |
| 4              | 1,583                                   | 2.0   |
| 5+             | 2,018                                   | 2.5   |

We used this ratio to scale up the energy consumption rates for the average NZ household, which assumes 2.7 people per home according to 2018 Census data ([Household size in New Zealand, Figure.NZ](https://figure.nz/chart/vdTbdOaKUE9zTKo3)), and average energy consumption values from the Residential Baseline Study (total energy use by machine types such as heat pumps, gas heaters, etc.).