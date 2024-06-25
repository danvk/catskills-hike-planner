# Catskills Hike Planner

This is the serverless backend part of the [Catskills Hike Planner][planner].

Deploy:

    sls deploy --param=git_sha=$(git rev-parse HEAD)

(The git SHA is used as a cache key.)

Local development:

    DEV=1 poetry run python devserver.py
    curl \
      --request POST \
      'http://127.0.0.1:5000/find-hikes' \
      --header 'Content-Type: application/json' \
      --data-raw '{"area": "catskills", "peaks": ["H", "BD", "TC", "C", "Pl", "Su"]}'

## Updating from computing-in-the-catskills repo

See computing-in-the-catskills/README.md.

[planner]: https://danvk.org/catskills/map/planner
