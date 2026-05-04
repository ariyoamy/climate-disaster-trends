# Data

## Source

The dataset comes from **EM-DAT** (The International Disasters Database), maintained by the Centre for Research on the Epidemiology of Disasters (CRED) at UCLouvain, Brussels. It was downloaded through [Our World in Data](https://ourworldindata.org/natural-disasters), which provides cleaned, pre-aggregated versions of the EM-DAT data under a Creative Commons BY licence.

Direct download link:  
https://ourworldindata.org/grapher/number-of-natural-disaster-events

## File

`disaster_events_owid.csv` — number of reported disaster events per year, broken down by hazard type.

Columns:
- **Entity** — disaster type (e.g. Flood, Drought, Extreme weather)
- **Year** — calendar year
- **Disasters** — number of events recorded that year

## What counts as a disaster in EM-DAT

EM-DAT includes an event if it meets at least one of these thresholds:
- 10 or more people reported killed
- 100 or more people reported affected
- A declaration of a state of emergency
- A call for international assistance

This means smaller events don't appear. The bar for inclusion has also been applied more consistently in recent decades, which is one reason the counts rise over time.

## Important caveats

- **Reporting bias**: disaster recording has improved dramatically since the 1960s. More events being recorded does not necessarily mean more events are happening.
- **Definitional changes**: what counts as a "flood" vs. a "storm" can vary across time and between countries.
- **No severity weighting**: a single flash flood and a catastrophic multi-country flood both count as one event.
- **Incomplete 2020s**: the latest data covers 2020–2024, so decade totals for the 2020s are not directly comparable to full decades.

## Citation

EM-DAT, CRED / UCLouvain — with processing by Our World in Data.  
"Number of reported natural disaster events" [dataset].  
Retrieved May 2025.
