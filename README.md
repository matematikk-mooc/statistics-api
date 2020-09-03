# statistics-api
Python Django application which serves HTTP endpoints that provide statistical aggregations of courses and groups on Canvas LMS. Runs scheduled task to periodically pull data from Canvas LMS REST APIs to MySQL database.

# Setup

This app requires a local or remote instance of Canvas LMS and an instance of KPAS LTI (https://github.com/matematikk-mooc/kpas-api), from which this service retrieves data about schools, counties, municipalities and associations thereof. You will need an API key to Canvas LMS which is valid for some Canvas account ID, and a valid access token to KPAS LTI. Copy `.env.example` to new file `.env`, and fill in the domain of your Canvas LMS instance and the API key of your root account, and alter other attributes, if necessary. Adjust settings in `docker-compose.dev.yml` for your environment, if necessary. Run 

`docker-compose -f docker-compose.dev.yml up`

The application is hosted at `statistics-api-dev.local:8000` by default. Import the CA certificate `ca.crt` to your web browser to enable HTTPS. Add new line to `/etc/hosts`: `127.0.0.1 statistics-api-dev.local`, routing the domain `statistics-api-dev.local` to your host IP. If you're not running a Linux OS, the procedure to add new domain route will be somewhat different.

You may also create your own CA certificate and replace `ca.crt` and create new site certificate and private key in `nginx/nginx-selfsigned.crt` and `nginx/nginx-selfsigned.key` respectively. Creating your own CA would mitigate the small risk of an attacker impersonating the `statistics-api-dev.local` domain.

Access application on e.g. `https://statistics-api-dev.local:8000/api/statistics/:courseId`


# Testing

There are a number of tests in this repository, but nearly all of them are integration tests dependent on 3rd party services KPAS LTI and Canvas LMS. The tests require the database to be populated with data from Skoleporten about (1) number of primary teachers at schools, (2) number of high school teachers at counties and (3) Canvas enrollment data. Before you can execute any tests locally, the following management commands need to run successfully:

`python manage.py import_school_teacher_counts_from_csv`

`python manage.py import_county_teacher_counts_from_csv`

`python manage.py do_all_scheduled_maintenance_jobs`

However, a working test environment is automatically built in GitHub actions pipelines. Any time you push to the `test` branch, all unit tests will be run.


# Deployment

Any merge to `staging` or `master` branch will automatically deploy the application to the staging and production environments respectively. Unit tests will also be run, and deployment will stop if any test fails.

# Documentation

Swagger UI documentation is available at https://matematikk-mooc.github.io/statistics-api-documentation/, using GitHub pages. The source for the documentation is available at https://github.com/matematikk-mooc/statistics-api-documentation.
