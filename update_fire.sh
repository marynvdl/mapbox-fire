
source venv/bin/activate

export MAPBOX_ACCESS_TOKEN=####


# Run python file
python3 update_fire.py

# Updating
tilesets upload-source africanswift fire-source data/fires.ldgeojson.ld --replace
tilesets publish africanswift.fire-tiles
