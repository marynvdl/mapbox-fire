## Technical details

Set up a cronjob running the bash script `run_update_fire.sh` in this repo, something like this:

```
* * * * /home/mapbox-fire/run_update_fire.sh >> /home/mapbox-fire/logs/run_update_fire.log 2>&1
```

This script runs `update_fire.py`, replaces a *Mapbox TileSet Source*, and publishes the tiles on *Mapbox* account name africanswift (you'll have to replace your account name and Mapbox token).

These tile layer contains FIRMS Data with all of these parameters:
- regions = ['northern_and_central_africa', 'southern_africa']
- date_span= ['72h']
- sensors = ['c6.1', 'suomi-npp-viirs-c2', 'noaa-20-viirs-c2']

Firms has a rather messy API, only providing kml as output format. Thus, we `BeautifulSoup` to scrape the html tags of each feature in the kml for attribute data.

## Adding the fire layer to EarthRanger
1. Going to yoursite.pamdas.org/admin click Maplayers >  Basemaps > Add Basemap
2. Copy the following details:
	- Name: `Fire`
    - Map Layer service Type:: `Tile Server`
    - Title: `Fire`
    - URL: `https://api.mapbox.com/styles/v1/africanswift/ckxsnt3rg1ga714nuco9pt31y/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYWZyaWNhbnN3aWZ0IiwiYSI6ImNrNzJ5MjIwZjA2cW8zZ3FvZDZ6OGppenIifQ.YIHEN9bzJCReMX2kI9cwTg&fresh=true&dt=${Date.now()}&update=1`
    - Icon URL: `https://img.icons8.com/color/50/000000/fire-element.png`
    - Service Configuration: `null`
