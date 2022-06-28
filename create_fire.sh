export MAPBOX_ACCESS_TOKEN=####

# Create a tileset source
tilesets upload-source africanswift fire-source data/fires.ldgeojson.ld

# Write a recipe - .json file

# Create new tileset
tilesets create africanswift.fire-tiles --recipe fire_recipe.json --name "Fire"

# Publish tileset
tilesets publish africanswift.fire-tiles

# Check status
tilesets status africanswift.fire-tiles
tilesets jobs africanswift.fire-tiles


# Update recipe
tilesets update-recipe africanswift.fire-tiles fire_recipe.json
tilesets publish africanswift.fire-tiles
