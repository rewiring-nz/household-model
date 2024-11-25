# Methodology and assumptions

## 1.1 Summary of modelling approach

Our modelling uses household and vehicle energy use data at a per machine level (e.g. energy use per gas water heater, or per petrol car), primarily from government sources, combined with up-to-date (2024) energy pricing and product pricing, to understand the economics of electrifying each type of individual machine occurring in New Zealand’s housing stock. This includes the operating costs (the gas, electricity, or petrol bills paid to operate that machine), the product replacement costs (the costs to replace like for like, or to replace a fossil fuel option with an electrified option including installation costs). Road user charges (RUCs) are included in the model for electric vehicles and diesel vehicles. Fixed connection costs are included for gas, LPG, and electricity.

## 1.2 Assumptions used in the model

#### Energy Use by Appliance

We derive average household energy use across different appliances through the Australian and New Zealand Residential Baseline Study 2021, published November 2022.[^1]  

#### Occupancy and Energy Use

Household energy needs scale non-linearly based on occupancy. For example, a 1-bedroom apartment with two people living in it does not have twice the energy consumption as one person living in it. The ratio is likely to be lower, as some of the energy needs are shared (e.g. heating the living room, cooking 1 meal that is shared). We have used ratios from the [Australian Energy Regulator Electricity and Gas consumption benchmarks for residential customers 2020 study](https://www.aer.gov.au/industry/registers/resources/guidelines/electricity-and-gas-consumption-benchmarks-residential-customers-2020) to scale the energy consumption of a household based on its occupancy, from the NZ averages.

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

#### Energy Use by Vehicles

We derive average vehicle energy use through the EECA energy end use database for 2019.[^2] We use data from 2019 for vehicles as this is before COVID lockdowns and the database for vehicles had not been updated for 2022 onwards when our analysis was completed. The assumption made here is that New Zealanders drive similar amounts per year today as they did in 2019\. The amount of vehicles per home is sourced from the Census 2018\. The number of vehicle types (light passenger and light commercial) is sourced from the Motor Vehicle Association historic sales data.[^3]

#### Energy Efficiency of appliances

We use energy factors / coefficient of performance across each appliance type to calculate the base energy requirements needed by a household depending on what appliances it uses. Heat pump space heating Coefficient Of Performance (COP) is sourced from EECA and a COP of 4.08 is used for the average heat pump.[^4] Space heating energy factors for other appliances are sourced from the Warm Homes Technical Report published by the Ministry for the Environment in November 2005.[^5] 

Water heating efficiencies are sourced from the US Department of Energy \- Energy Star ratings scheme.[^6] Electric Resistive Tank water heating is assumed at 90%, and Heat Pump water heaters are assumed at 367%, which is based upon the 10% tank losses combined with the EECA 408% heat pump efficiency for space heating. 

Cooktop efficiency is sourced from the Frontier Energy Residential Cooktop Performance and Energy Comparison Study Report \# 501318071-R0, published in July 2019.[^7] Electric oven efficiency is assumed at 95%, and gas/LPG oven at 90%. 

#### Energy Efficiency of Vehicles

We use miles per gallon (MPG) vehicle driving data from the US Department of Energy fuel economy database to calculate the different energy requirements across vehicle types popular in New Zealand.[^8] For electric vehicles, this includes charging losses. To calculate the average efficiency difference between an electric and internal combustion engine (ICE) vehicle, we use a comparison of popular New Zealand vehicles both ICE and electric and their fueleconomy.gov MPG combined rating from the website administered by Oak Ridge National Laboratory for the U.S. Department of Energy and the U.S. Environmental Protection Agency. Where fueleconomy.gov data is not available for some electric vehicles in New Zealand (e.g. BYD), we use the Electric Vehicle Database real range energy consumption estimate.[^9] Where the energy consumption is not available for any remaining vehicles through either of these methods, we use manufacturer estimates provided in technical vehicle documentation or a comparative vehicle model. The average MPG for an ICE vehicle used is 30.24, the average MPG for an electric vehicle used is 117.13.

#### Energy Prices

Energy prices for petrol, diesel, and natural gas, come from the average of the most recent four quarters of the MBIE Energy Prices data.[^10] These prices are reconciled with a comparison of prices available to consumers from PowerSwitch provided by ConsumerNZ for May 2024\. Where data is not provided (e.g. wood), an online comparison of prices is used. While MBIE provides combined residential gas fixed and volume costs in a combined rate, this is split into a lower cost volume rate, and a fixed yearly raterom natural gas offers available on PowerSwitch.The following fuel prices are used:

* Gas fixed costs are estimated at $689 (ConsumerNZ). LPG fixed costs are estimated at $69 (Genesis LPG pricing).   
* Gas volume cost per kWh is 11.8 cents.   
* LPG volume cost per kWh is 25.5 cents.   
* Petrol is $2.74 per litre or 28.9 cents per kWh.   
* Diesel is $2.11 per litre or 19.7 cents per kWh.   
* Wood is 11.3 cents per kWh, or $4.4 per Kg, or $150 per cubic metre.   
* Coal price is 7 cents per kWh for consumption and 4.2 cents per kWh for electricity generation. The generation price was taken from MBIE’s  EDGS 2024 historic coal import price assumptions.[^11] 

Household electricity price is calculated using data from MBIE Energy Prices and Quarterly Survey of Domestic Electricity Prices (QSDEP) 2024\. We split electricity pricing into a volume cost per kWh and a fixed cost per kWh. Electricity fixed costs vary by energy use in the home. We use a ConsumerNZ average estimate for May 2024 of $2.10 per day, or $767.76 per year.  Electricity volume cost (excluding fixed costs) per kWh is 26.2 cents. Ripple control off peak is 24.2 cents per kWh. Nightly electricity is 17.3 cents per kWh, and feed in tariff for solar is 13 cents per kWh.

Costs in forward years are calculated using the consumer price index for each fuel, and the national numbers shown in this paper are Real 2024 dollars. Energy costs for product comparisons use the average energy price over 15 years from the date of purchase. 

#### Solar and Battery Cost, Specification, and Utilisation

Solar prices are estimated at $2,000/kW using a combination of 2023 data from the Sustainable Energy Association of New Zealand (SEANZ) and direct surveys from installers. For full household calculations, we use an example 7kW installation. Assuming 0.5% degradation per year over a 30-year lifetime. Inverter replacement costs are assumed at $2,500. The solar capacity factor assumption is 15%. 

We assume 50% of appliance energy needs and 50% of vehicle energy needs can be met during the solar window. Water heating, which is near a third of average household loads, can be moved almost entirely into the solar window in what is described as a “thermal battery”. This is similar to existing “ripple control” used in New Zealand electric water heaters to avoid peak electricity times. Other appliances, such as  space heaters, can only be moved a small amount, with significant energy needs being met outside the solar window. We consider this to be a conservative estimate of the load shifting possible by households. For example, with new electric vehicles having more range than a week or even two weeks of driving, households could choose to charge near 100% from solar on weekends or, if they are at home during sunlight hours, any time during the week. The other electricity consumption is assumed at full grid electricity costs, which we also consider to be conservative as households often have access to low cost electric vehicle charging rates during off peak periods. 

All households remain connected to the grid, consume grid electricity, and pay for grid fixed costs and volume costs for the amount of electricity used. The solar export feed-in-tariff is assumed at 13 cents per kWh based on an online comparison of feed-in tariffs. We note that the primary electrified comparison home in the model also has a battery. However, the battery export feed-in-tariff is assumed to be the same as the solar feed-in-tariff. This is considered conservative, as the battery can feed in at peak times when electricity prices are significantly higher, and where some EDBs and retailers provide higher reward for peak feed-in. 

For individual appliance comparisons we calculate a cost/kWh for solar based on the above example installation. This is then applied for the portion of the appliance energy use that could be feasibly powered during the solar window and the rest of the energy comes from the grid. 

Battery costs are assumed at $1000/kWh, from multiple surveys of 2023 installation costs in New Zealand direct from battery installers, in addition to comparison of available online prices for batteries in New Zealand. Battery cycle costs are calculated over a 15 year, 5475 cycle life. Degradation is assumed at 60% after the 15th year with an accelerating degradation curve from the first year of use. We assume a round trip efficiency of 95%. 

#### Solar by region

Assumes a static capacity factor per region, although this is likely to increase over the next 30 years as it has historically:

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

#### Appliance Prices 

Appliance prices come from a comparison of over 100 different quotes for appliance costs, sourced both online and direct from installers. An average capital cost and average install cost is used for each individual appliance. The scope of the appliance cost comparison aims to compare products that are not the cheapest possible product, nor the most expensive, as appliance costs can vary significantly. The aim of the comparison was to create an assumed common cost for each option, in the middle of the cost spectrum. 

Appliance installation specific costing is scarce, and we acknowledge the need for detailed work in the area of obtaining these “soft costs” or installation costs of devices. Installation costs also vary significantly between installers, creating further complexity. This paper uses installation costs that are the result of real quotes from both online and direct installer but A detailed analysis of the impact of different household conditions and installation costs across different appliances would be valuable for emissions reduction and energy system planning in New Zealand.  
   
The following appliance price and installation cost are assumed:

* Heat pump costs are $3,800 per device, including $1,050 per device installation.   
* Gas flued heater costs are $3,200 per device, including $1,250 per device installation.   
* LPG flued heater costs are $3,300 per device, including $1,250 per device installation.   
* Resistance bar heater costs are $300 per device and $0 for installation as they plug in at the wall.   
* Wood fire costs are $2,900 for the fire, $1,000 for the flue, and $1,000 for installation.   
* Gas instant water heaters are $1,400, and $2,180 for installation.   
* LPG instant water heaters are $1,400, and $2,180 for installation.   
* Heat pump water heaters are $4,700, and $2,320 for installation.   
* Resistance water heaters are $2,000, and $2,000 for installation.   
* Gas and LPG cooktops are $1,000, and $700 for installation.   
* Induction cooktops are $1,400, and $1,300 for installation.   
* Resistance cooktops are $900, and $300 for installation. 

#### Vehicle Prices

Vehicle prices are based on a comparison of popular New Zealand petrol vehicles and their prices, compared to a similar EV option and its price, using pricing data from vehicle manufacturer websites accessed in August 2024\. Clean car rebate is not included as it was phased out in 2024\. The average new price used for ICE vehicles is $41,175 and the average new price used for EV’s is $55,176. One $2,000 EV charger per home is also added onto the costs of a new EV. RUCs are included on electric vehicles at 11,000km per year, $76 per 1000km. 

#### Finance Rates, Terms, and Lifetimes 

The primary finance rate used to compare homes is 5.5%. The term used for the finance is 15 years, with acknowledgement that some homes may pay this off faster and reduce total interest spending on finance. The lifetime for appliances, vehicles, and batteries is assumed at 15 years, with solar panels at 30 years with one replacement inverter required. Solar panels often have 25–30-year performance warranties, some up to 40 years, and the assumption is that products will not die the moment the warranty ends. Batteries often have 10-year warranties for capacity, e.g. the Tesla Powerwall 2 has a 70% capacity warranty of 10 years, and some have 15 year warranties. The assumption is that capacity will continue to degrade increasingly, and the battery will still remain functional (at lower capacity) for 15 years. Electric vehicles often come with 8-year warranties (and/or around 160,000km) for the battery and drivetrain, and it is assumed the vehicles will last longer than their warranties as most cars significantly outlast their warranty (e.g. a 15 year old car did not have a 15 year warranty). Heat pumps, water heaters, and stovetops are assumed to last 15 years, noting that the quality of device impacts this lifetime, and this study has purposely avoided choosing only the cheapest options, instead aiming for common expected pricing in the middle of the cost spectrum for appliance choices.

#### Price History and Forecasts 

Historic prices for electricity, gas, LPG, petrol, diesel, and wood are modelled using the quarterly consumer price index for the associated type of fuel for the past 24 years \- indexed to 2000 \- with today’s pricing as the basis.[^12] Future prices for each of these energy types is based on the Real price increase seen historically. Calculated as the average nominal price increase minus the average All groups CPI increase. 

Solar price history is based on international solar price trends adjusted to current New Zealand solar prices. Nemet (2009); Farmer & Lafond (2016); International Renewable Energy Agency (IRENA).[^13] Future solar price forecasts are based on the National Renewable Energy Laboratory Residential PV Advanced cost forecast,[^14] adjusted to New Zealand solar prices. With acknowledgement that forecasts have historically underestimated the speed at which renewable energy technology drops in price.[^15] 

Battery price history is based on the paper by Ziegler from 2021,[^16] adjusted to New Zealand battery prices. Forecast battery prices are based on the National Renewable Energy Laboratory Residential Battery Storage Advanced cost forecast,[^17] which is adjusted to New Zealand battery prices and has the cost decline offset (delayed) by one year to represent delays in supply chain cost reductions reaching New Zealand consumers. 

Electric vehicle price forecasts are based on an index derived from the Climate Change Commission (CCC) EV price parity forecast Scenario B,[^18] reconciled with market EV and ICE pricing data comparisons done by Rewiring Aotearoa. We found that both EV and ICE vehicle prices on market were lower than the average price used in the CCC forecast, and that the CCC forecast delayed by 1 year represented a more reflective mix of the higher cost of EVs today (about 130% of ICE vehicle costs).

#### Emissions factors

These figures are taken from the Ministry for the Environment's [Measuring emissions: A guide for organisations (2023)](https://environment.govt.nz/assets/publications/Measuring-Emissions-Guidance_EmissionFactors_Summary_2023_ME1781.pdf).

| Energy Type   | Emissions Factor (kgCO₂e/kWh) |
|---------------|-------------------------------|
| Electricity   | 0.074                         |
| Natural Gas   | 0.201                         |
| LPG           | 0.219                         |
| Wood          | 0.016                         |
| Petrol        | 0.258                         |
| Diesel        | 0.253                         |

#### Inflation Rates

We base the rate of inflation of product prices on the New Zealand CPI history from 2000 to 2024 at 2.56%. Energy inflation rates are determined by the respective category rate of inflation in the New Zealand CPI history, with gas at 4.55%, electricity at 3.69%, petrol and diesel at 5.29%, and solid fuels at 3.86%. We set future product price base inflation at 2%. The real inflation rates used for energy are the nominal value minus the All CPI groups rate over the same period of 2.55% pa (All Groups CPI). Specifically, 1.14% for electricity, 2.00% for gas and LPG, 2.73% for petrol and diesel, and solid fuels at 1.30%. The primary numbers presented are based on 2024 dollars and use these real inflation rates.

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
