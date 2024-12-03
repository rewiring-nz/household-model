# Methodology and assumptions

## Summary of modelling approach

Our modelling uses household and vehicle energy use data at a per machine level (e.g. energy use per gas water heater, or per petrol car), primarily from government sources, combined with up-to-date (2024) energy pricing and product pricing, to understand the economics of electrifying each type of individual machine occurring in New Zealand’s housing stock. This includes:

- operating costs
    - the gas, electricity, or petrol bills paid to operate that machine
    - fixed connection costs for gas, LPG, and electricity.
    - road user charges (RUCs) for electric vehicles, plug-in hybrids, and diesel vehicles
- emissions: the amount of emissions saved based on energy consumption and emissions factor of the fuel type
- product replacement costs: the costs to replace like for like, or to replace a fossil fuel option with an electrified option including installation costs

## Energy Use

### Energy Use of Appliances

We use energy factors / coefficient of performance across each appliance type to calculate the base energy requirements needed by a household depending on what appliances it uses. Heat pump space heating Coefficient Of Performance (COP) is sourced from EECA and a COP of 4.08 is used for the average heat pump.[^4] Space heating energy factors for other appliances are sourced from the Warm Homes Technical Report published by the Ministry for the Environment in November 2005.[^5] 

Water heating efficiencies are sourced from the US Department of Energy \- Energy Star ratings scheme.[^6] Electric Resistive Tank water heating is assumed at 90%, and Heat Pump water heaters are assumed at 367%, which is based upon the 10% tank losses combined with the EECA 408% heat pump efficiency for space heating. 

Cooktop efficiency is sourced from the Frontier Energy Residential Cooktop Performance and Energy Comparison Study Report \# 501318071-R0, published in July 2019.[^7] Electric oven efficiency is assumed at 95%, and gas/LPG oven at 90%. 

### Energy Use by Vehicles

We derive average vehicle energy use through the EECA energy end use database for 2019.[^2] We use data from 2019 for vehicles as this is before COVID lockdowns and the database for vehicles had not been updated for 2022 onwards when our analysis was completed. The assumption made here is that New Zealanders drive similar amounts per year today as they did in 2019\.

| Vehicle type | Energy use (kWh/day) |
|--------------|----------------------|
| Petrol       | 31.4                |
| Diesel       | 22.8                |
| Electric     | 7.324               |

Plug-in hybrids are assumed to be 60% petrol and 40% electric, while hybrids are considered to be 70% petrol and 30% electric.

The average New Zealand car drives 10,950 km, rounded to 210 km per week. This is taken from 2019 stats on light passenger and light commercial vehicles from the [Ministry of Transport's Annual Fleet Statistics](https://www.transport.govt.nz/statistics-and-insights/fleet-statistics/annual-fleet-statistics/) for the year 2019, to avoid the anomalies from COVID-19. We use this to scale the energy usage per vehicle. For example, if a petrol vehicle's mileage is 300 kms/week, then its energy usage would be:

$31.4 \space\text{kWh/day} \times \frac{300\space\text{km/week}}{210\space\text{km/week}} \times 24\space\text{hours/day} \times 7\space\text{days/week}$.

The dropdown options for vehicle usage in our [household calculator frontend app](https://github.com/rewiring-nz/household-calculator-app/) are `Low (<100 km/wk)`, `Medium (100-300 km/wk)`, and `High (300+ km/wk)`. They are fed into the calculation as 50 km/wk, 210 km/wk (the national average), and 400 km/wk respectively.

### Scaling energy use by occupancy

We derive average household energy use across different appliances through the Australian and New Zealand Residential Baseline Study 2021, published November 2022.[^1] However, household energy consumption does not scale linearly with the number of occupants. Shared resources and economies of scale mean that additional occupants do not proportionally increase energy usage. For example, a 1-bedroom apartment with two people living in it does not have twice the energy consumption as one person living in it. The ratio is likely to be lower, as some of the energy needs are shared (e.g. heating the living room, cooking 1 meal that is shared). 

Given that much of our energy consumption rates for each household appliances was based on averages from the Australian and New Zealand Residential Baseline Study 2021 (published November 2022), and given that the average New Zealand household has 2.7 occupants according to 2018 Census data ([Household size in New Zealand, Figure.NZ](https://figure.nz/chart/vdTbdOaKUE9zTKo3)), we needed to calculate a multiplier for the occupancy options given in the calculator.

#### Data collection

We used electricity consumption numbers from data collected by the Australian Energy Regulator in their [Electricity and Gas consumption benchmarks for residential customers 2020 study](https://www.aer.gov.au/industry/registers/resources/guidelines/electricity-and-gas-consumption-benchmarks-residential-customers-2020). From the [Frontier Economics - Simple electricity and gas benchmarks - From June 2021](https://www.aer.gov.au/documents/frontier-economics-simple-electricity-and-gas-benchmarks-june-2021) data sheet, on the "Climate zone 6" sheet (Mild temperate, such as urban Melbourne, Adelaide Hills, Ulladulla, similar to NZ average; [see Table 1 on page 15](https://www.aer.gov.au/system/files/Residential%20energy%20consumption%20benchmarks%20-%209%20December%202020_0.pdf)), we averaged across all states and seasons, and we found the following electricity consumption and ratios.

_Table 1: Energy consumption by household size ([Source](https://www.aer.gov.au/documents/frontier-economics-simple-electricity-and-gas-benchmarks-june-2021))_
| Household Size | Average Electricity Use per Season (kWh) | Ratio |
|----------------|-----------------------------------------|-------|
| 1              | 803                                     | 1.00   |
| 2              | 1,328                                   | 1.65   |
| 3              | 1,410                                   | 1.75   |
| 4              | 1,583                                   | 1.97   |
| 5+             | 2,018                                   | 2.51   |


We did not use the separate gas energy consumption numbers to scale gas energy use as the ratios turned out to be very similar to the electricity consumption ratios for household size, and the immaterial difference was not worth the extra complexity.

#### Nonlinear interpolation

In order to calculate the multiplier of the average energy consumption values, we first needed to find the ratio value for our reference occupancy of 2.7. To do this, we fitted an exponential model to the data in Table 1, using the first four data points and excluding `5+` as this is not actually a discrete data point, but a range. Please refer to `notebooks/occupancy.ipynb` for the working on model fitting.

$f(x) = a \cdot (1 - e^{-b \cdot (x-1)}) + c$

Where:

- $x$ is the number of occupants
- $a$, $b$, and $c$ are fitted parameters

We selected this nonlinear exponential model because the relationship should:

- be nonlinear
- start close to 1 when x = 1
- have a sharp initial increase in consumption (from 1 to 2 occupants)
- show diminishing returns as occupancy increases (plateau)

There are limitations to this modelling approach given that it is based on very few data points, and certainly does not account for specific household characteristics (e.g. a 2-person apartment that luxuriates in fresh hot baths every day).

The interpolated value of the fitted exponential model at 2.7 occupants was 1.79.

#### Scaling multiplier

To find the multiplier that we can use to scale our reference energy values, we then use the following formula:

$E_{new} = E_{ref} \cdot \frac{f(x)}{f(x_{ref})}$

Where:

- $E_{new}$ is the estimated energy consumption for the new  given household size
- $E_{ref}$ is the reference energy consumption from our existing data about the average household
- $f(x)$ is the exponential scaling function
- $x$ is the number of occupants
- $x_{ref}$ is the reference occupancy (2.7)

Since this formula was fitted to only the first four values of household size, and is not intended to work with a range like `5+ occupants`, it will not work for the `5+` category. The jump from 4 to 5+ occupants in the original data (Table 1) is actually quite high. The jump from 3 to 4 occupants is 0.2, but 4 to 5+ is 0.5. This makes sense because 5+ includes households larger than 5, so extrapolating for $x = 5$ would not give an accurate figure.

Instead, we've instead taken the relative increase in energy consumption between `4` and `5+` occupants from Table 1 (27.5% increase from 1,583 kWh to 2,018 kWh) and applied this to the energy consumption scaling factor $f(4)$.

$f(5+) = f(4) \cdot (1+\frac{2,018 - 1,583}{1,583}) \approx 1.37$

This rounds out our table of scaling factors for all the occupancy options that we have available:

Table 2: Scaling factors for energy consumption based on occupancy

| Occupants | Energy Consumption scaling factor |
|-----------|--------------------------|
| 1 | 0.56 |
| 2 | 0.90 |
| 2.7 (reference) | 1.00 |
| 3 | 1.03 |
| 4 | 1.07 |
| 5+ | 1.09 |

### Solar

The formula for calculating electricity generation from solar is as follows:

$E = S \cdot C_{loc} \cdot D$

Where:

- $E$ is the energy generated per hour
- $S$ is the solar panel size in kW
- $C_{loc}$ is the solar capacity factor for a given location
- $D$ is the degradation over the 30 year lifespan of the panels

We assume the following static capacity factors per region. However, this is a conservative estimate as capacity factor likely to increase over the next 30 years, as it has historically.

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

We also assume:

- 0.5% degradation per year over a 30-year lifetime, which averages out to 6.92% degradation over 30 years, or 93.08% performance of nameplate capacity over 30 years.
- 50% self-consumption, i.e. 50% of appliance energy needs and 50% of vehicle energy needs can be met during the solar window.
    - Water heating, which is near a third of average household loads, can be moved almost entirely into the solar window in what is described as a “thermal battery”. This is similar to existing “ripple control” used in New Zealand electric water heaters to avoid peak electricity times.
    - Other appliances, such as space heaters, can only be moved a small amount, with significant energy needs being met outside the solar window.
    - We consider this to be a conservative estimate of the load shifting possible by households. For example, with new electric vehicles having more range than a week or even two weeks of driving, households could choose to charge near 100% from solar on weekends or, if they are at home during sunlight hours, any time during the week.
    - The other electricity consumption is assumed at full grid electricity costs, which we also consider to be conservative as households often have access to low cost electric vehicle charging rates during off peak periods.

### Battery

We assume:

- Average degradation of 85.22% over a 15 year product lifetime
- 1 battery cycle per day (it is filled up and depleted once per day)
- 5% of electricity stored is lost to electronics & wiring to keep the battery running
- All the electricity stored in the battery is from solar. The model does not handle the scenario where there are batteries but no solar (we don't model arbitrage). The API does not accept households with a battery but no solar.

## Emissions

To calculate emissions, we take the energy consumption from the various machines, and multiply these by the emissions factors. We use these emissions factors are taken from the Ministry for the Environment's [Measuring emissions: A guide for organisations (2023)](https://environment.govt.nz/assets/publications/Measuring-Emissions-Guidance_EmissionFactors_Summary_2023_ME1781.pdf).

| Energy Type   | Emissions Factor (kgCO₂e/kWh) |
|---------------|-------------------------------|
| Electricity   | 0.074                         |
| Natural Gas   | 0.201                         |
| LPG           | 0.219                         |
| Wood          | 0.016                         |
| Petrol        | 0.258                         |
| Diesel        | 0.253                         |

## Operating Costs

### Energy

Energy prices for petrol, diesel, and natural gas, come from the average of the most recent four quarters of the MBIE Energy Prices data, based on 2024 New Zealand dollars.[^10] These prices are reconciled with a comparison of prices available to consumers from PowerSwitch provided by ConsumerNZ for May 2024. Where data is not provided (e.g. wood), an online comparison of prices is used. While MBIE provides combined residential gas fixed and volume costs in a combined rate, this is split into a lower cost volume rate, and a fixed yearly rate from natural gas offers available on PowerSwitch.

We base the rate of inflation on the New Zealand CPI history from 2000 to 2024 at 2.56%. We set future product price base inflation at 2%. The real inflation rates used for energy are the nominal value minus the All CPI groups rate over the same period of 2.55% pa (All Groups CPI). The specific rate of inflation for each fuel type, alongside today's fixed & volume costs versus the average over the next 15 years, can be found in the table below. Our cost savings calculations for weekly & yearly savings use 2024 prices, while our lifetime savings use the average prices over 15 years.

Table 1: Energy prices

| Fuel type                | Fixed costs in 2024 ($/yr) | Volume costs in 2024 ($/kWh) | Rate of Inflation (Real) | Average fixed costs over next 15 years ($/yr) | Average volume cost over next 15 years ($/kWh) |
|--------------------------|---------------------------|------------------------------|---------------------------|-----------------------------------------------|-----------------------------------------------|
| Gas                     | 689.22675                | 0.118                      | 2.00%                     | 794.48                                     | 0.13602                                       |
| LPG                     | 69.00                    | 0.25452                      | 2.00%                     | 79.537                                      | 0.29339                                       |
| Petrol                  | -                        | 0.28884                      | 2.73%                     | -                                             | 0.35125                                       |
| Diesel                  | -                        | 0.19679                      | 2.73%                     | -                                             | 0.23931                                       |
| Wood                    | -                        | 0.11250                      | 2.00%                     | -                                             | 0.12968                                       |
| Electricity (standard)  | 767.7555                 | 0.26175                      | 1.14%                     | 831.99                                     | 0.28365                                       |
| Electricity (off-peak)  | -                        | 0.17300                      | 1.14%                     | -                                             | 0.18747                                       |
| Electricity (solar feed-back tariff) | -         | 0.135                        | 1.14%                     | -                                             | 0.14632                                       |

### Solar

Solar prices are estimated at $2277.78/kW using a combination of 2023 data from the Sustainable Energy Association of New Zealand (SEANZ) and direct surveys from installers. This is essentially $2000/kW plus the cost of an inverter which lasts 15 years.  Inverter replacement costs are assumed at $2,500. The solar capacity factor assumption is 15%. 

All households remain connected to the grid, consume grid electricity, and pay for grid fixed costs and volume costs for the amount of electricity used. The solar export feed-in-tariff is assumed at 13.5 cents per kWh based on an online comparison of feed-in tariffs. 

### Batteries

Battery costs are assumed at $1000/kWh, from multiple surveys of 2023 installation costs in New Zealand direct from battery installers, in addition to comparison of available online prices for batteries in New Zealand. Battery cycle costs are calculated over a 15 year, 5475 cycle life. Degradation is assumed at 60% after the 15th year with an accelerating degradation curve from the first year of use. We assume a round trip efficiency of 95%. 

The battery export feed-in-tariff is assumed to be the same as the solar feed-in-tariff. This is considered conservative, as the battery can feed in at peak times when electricity prices are significantly higher, and where some EDBs and retailers provide higher reward for peak feed-in. 

### Appliances

Appliance replacement costs come from a comparison of over 100 different quotes for appliance costs, sourced both online and direct from installers. An average capital cost and average install cost is used for each individual appliance. The scope of the appliance cost comparison aims to compare products that are not the cheapest possible product, nor the most expensive, as appliance costs can vary significantly. The aim of the comparison was to create an assumed common cost for each option, in the middle of the cost spectrum. 

Appliance installation specific costing is scarce, and we acknowledge the need for detailed work in the area of obtaining these “soft costs” or installation costs of devices. Installation costs also vary significantly between installers, creating further complexity. This paper uses installation costs that are the result of real quotes from both online and direct installer but A detailed analysis of the impact of different household conditions and installation costs across different appliances would be valuable for emissions reduction and energy system planning in New Zealand.  
   
The following appliance price and installation cost are assumed:

| Appliance     | Fuel type                   | Item price ($) | Install cost ($) |
|---------------|-----------------------------|----------------|------------------|
| Space heater  | Electricity (heat pump)     | 2728           | 1050             |
| Space heater  | Electricity (resistive)     | 300            | 0                |
| Space heater  | Gas                         | 3876.085       | 1250             |
| Space heater  | LPG                         | 3876.085       | 1250             |
| Space heater  | Wood                        | 4913           | 0                |
| Water heater  | Electricity (heat pump)     | 4678           | 2321             |
| Water heater  | Electricity (resistive)     | 1975           | 1995             |
| Water heater  | Gas                         | 1418           | 2175             |
| Water heater  | LPG                         | 1419           | 2175             |
| Cooktop       | Electricity (induction)     | 1430           | 1265             |
| Cooktop       | Electricity (resistive)     | 879            | 288              |
| Cooktop       | Gas                         | 1022           | 630              |
| Cooktop       | LPG                         | 1022           | 630              |

### Vehicles

We use current Road User Charges (RUCs) without taking inflation into account:

- Electric: $76 per year per 1000km
- Plug-in hybrid: $38 per year per 1000km
- Hybrid: $0 per year per 1000km
- Petrol: $0 per year per 1000km
- Diesel: $76 per year per 1000km

The model does not provide upfront costs for vehicles, although the calculator app provides a general range to give an indication of replacing fossil fuel vehicles with EVs. The range is based on a comparison of popular New Zealand petrol vehicles and their prices, compared to a similar EV option and its price, using pricing data from vehicle manufacturer websites accessed in August 2024. Clean car rebate is not included as it was phased out in 2024. 

## Recommendations

TODO: about how the next steps algo works



[^1]:  [https://www.energyrating.gov.au/industry-information/publications/report-2021-residential-baseline-studyaustralia-](https://www.energyrating.gov.au/industry-information/publications/report-2021-residential-baseline-studyaustralia-and-new-zealand-2000-2040)

[^2]:  https://www.[eeca.govt.nz/insights/data-tools/energy-end-use-database/](http://eeca.govt.nz/insights/data-tools/energy-end-use-database/)

[^3]:  [https://www.mia.org.nz/Sales-Data/Vehicle-Sales\#oss](https://www.mia.org.nz/Sales-Data/Vehicle-Sales#oss)

[^4]:  [https://www.eeca.govt.nz/insights/eeca-insights/e3-programme-sales-and-efficiency-data/](https://www.eeca.govt.nz/insights/eeca-insights/e3-programme-sales-and-efficiency-data/)

[^5]:  [environment.govt.nz/assets/Publications/Files/warm-homes-heating-optionsphase1.pdf](http://environment.govt.nz/assets/Publications/Files/warm-homes-heating-optionsphase1.pdf) 

[^6]:  [https://www.energystar.gov/products/water\_heaters/residential\_water\_heaters\_key\_ product\_criteria](https://www.energystar.gov/products/water_heaters/residential_water_heaters_key_)

[^7]:  [https://cao-94612.s3.amazonaws.com/documents/Induction-Range-Final-Report-July-2019.pdf](https://cao-94612.s3.amazonaws.com/documents/Induction-Range-Final-Report-July-2019.pdf) 

[^8]:  [www.fueleconomy.gov](http://www.fueleconomy.gov) 

[^9]:  [https://ev-database.org/ car/1782/BYD-ATTO-3](https://ev-database.org/) 

[^10]:  [https://www.mbie.govt.nz/building-and-energy/energy-and-natural-resources/energystatistics-and-modelling/](https://www.mbie.govt.nz/building-and-energy/energy-and-natural-resources/energystatistics-and-modelling/energy-statistics/energy-prices/)

[^11]:  [https://www.mbie.govt.nz/building-and-energy/energy-and-natural-resources/energy-statistics-and-modelling/](https://www.mbie.govt.nz/building-and-energy/energy-and-natural-resources/energy-statistics-and-modelling/energy-modelling/electricity-demand-and-generation-scenarios)

[^12]:  [https://www.stats.govt.nz/indicators/consumers-price-index-cpi/](https://www.stats.govt.nz/indicators/consumers-price-index-cpi/)

[^13]:  [https://ourworldindata.org/grapher/solar-pv-prices](https://ourworldindata.org/grapher/solar-pv-prices) 

[^14]:  [https://atb.nrel.gov/electricity/2023/residential\_pv\#capital\_expenditures\_(capex)](https://atb.nrel.gov/electricity/2023/residential_pv#capital_expenditures_\(capex\)) 

[^15]:  [https://www.cell.com/joule/fulltext/ S2542-4351(22)00410-X](https://www.cell.com/joule/fulltext/) 

[^16]:  Ziegler M. S.; Trancik, J. E. Re-Examining Rates of Lithium-Ion Battery Technology Improvement and Cost Decline. Energy Environ. Sci. 2021, 14, 1635–1651. DOI: 10.1039/D0EE02681F, [https://pubs.rsc.org/en/content/articlelanding/2021/ee/d0ee02681f](https://pubs.rsc.org/en/content/articlelanding/2021/ee/d0ee02681f) [https://doi.org/10.7910/DVN/9FEJ7C](https://doi.org/10.7910/DVN/9FEJ7C)

[^17]:  [https://atb.nrel.gov/electricity/2023/residential\_battery\_storage](https://atb.nrel.gov/electricity/2023/residential_battery_storage)

[^18]:  [https://www.climatecommission.govt.nz/our-work/advice-to-government-topic/preparing-advice-on-emissions](https://www.climatecommission.govt.nz/our-work/advice-to-government-topic/preparing-advice-on-emissions-budgets/advice-on-the-fourth-emissions-budget/modelling-and-data-consultation-on-emissions-reduction-target-and-emissions-budgets/)

[^19]:  [https://www.stats.govt.nz/information-releases/dwelling-and-household-estimates-june-2024-quarter](https://www.stats.govt.nz/information-releases/dwelling-and-household-estimates-june-2024-quarter)

[^20]:  [https://www.energyrating.gov.au/industry-information/publications/report-2021-residential-baseline-study](https://www.energyrating.gov.au/industry-information/publications/report-2021-residential-baseline-studyaustralia-and-new-zealand-2000-2040)

[^21]:  [https://www.emi.ea.govt.nz/Retail/Reports/GUEHMT?DateFrom=20130901\&DateTo=20240331\&RegionType](https://www.emi.ea.govt.nz/Retail/Reports/GUEHMT?DateFrom=20130901&DateTo=20240331&RegionType=NZ&MarketSegment=Res&Capacity=All_Total&FuelType=solar_all&Show=ICP_Count&seriesFilter=NZ&_rsdr=ALL&_si=_db_Capacity%7CAll_Total,_db_MarketSegment%7CRes,_db_RegionCode%7CNZ,_db_RegionType%7CNZ,db%7C5YPBXT,dri%7C3745,s%7Cdmt,v%7C3)
