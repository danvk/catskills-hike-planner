# Catskills Hike Planner

This is the serverless backend part of the [Catskills Hike Planner][planner].

Deploy:

    sls deploy --param=git_sha=$(git rev-parse HEAD)

(The git SHA is used as a cache key.)

Local development:

    poetry run python devserver.py
    curl \
      --request POST \
      'http://127.0.0.1:5000/find-hikes' \
      --header 'Content-Type: application/json' \
      --data-raw '{"peaks": ["H", "BD", "TC", "C", "Pl", "Su"]}'

## Updating from computing-in-the-catskills repo

The shared files are:

- `graph.py`: no changes
- `subset_cover.py`:
  - [x] Orient the GeoJSON feature: back-port
  - [x] Add `{'hike_index': i}` property: back-port
  - [x] Drops `__main__` section: factor this out into a separate script
- `peak_planner.py`: mostly independent, adds hard-coded code -> OSM ID table
  - [ ] Derive this mapping from the data

The shared data files are:

- `data/hikes.json`
- `data/network.geojson`

The HTML parts of this repo are in catskills/map-src/
The list of peaks and codes is hard-coded in `HikePlanner.tsx`.


[planner]: https://danvk.org/catskills/map/planner
