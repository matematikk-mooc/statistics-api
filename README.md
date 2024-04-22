# statistics-api
Python Django application which serves HTTP endpoints that provide statistical aggregations of courses and groups on Canvas LMS. Runs scheduled task to periodically pull data from Canvas LMS REST APIs to MySQL database.

# Setup

This app requires an instance of Canvas LMS, from which this service retrieves data about schools, counties, municipalities and associations thereof. You will need an API key to Canvas LMS which is valid for some Canvas account ID. Use file `.env.dev` to update enviroment variables when running locally, and fill in the domain of your Canvas LMS instance and the API key of your root account, and alter other attributes, if necessary. Adjust settings in `docker-compose.dev.yml` for your environment, if necessary.
To start the application locally do the following steps:

- Activate venv: `source ./venv/bin/activate`
- Run `run_development.sh` in venv.
- Access api at `http://localhost:8000/api`
- Available endpoints is specified in urls.py

Access application on e.g. `http://127.0.0.1:8000/api/statistics/:courseId`


# Testing

There are some unit tests located in the folder 'tests'. These will run when merging changes into the branches `staging` and `master`, as a part of the depoloyment. If any of the tests fails the deployment will stop.


# Deployment

Any merge to `staging` or `master` branch will automatically deploy the application to the staging and production environments respectively.

# Documentation

Swagger UI documentation is available at https://matematikk-mooc.github.io/statistics-api-documentation/, using GitHub pages. The source for the documentation is available at https://github.com/matematikk-mooc/statistics-api-documentation.
