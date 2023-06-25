# Catskills Hike Planner

This is the serverless backend part of the [Catskills Hike Planner][planner].

Deploy:

    sls deploy

Local development:

    poetry run python devserver.py
    curl \
      --request POST \
      'http://127.0.0.1:5000/find-hikes' \
      --header 'Content-Type: application/json' \
      --data-raw '{"peaks": ["H", "BD", "TC", "C", "Pl", "Su"]}'

[planner]: https://danvk.org/catskills/map/planner
