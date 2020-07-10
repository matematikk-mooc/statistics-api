# statistics-api
Python Django application which serves HTTP endpoints that provide statistical aggregations of courses and groups on Canvas LMS. Runs scheduled task to periodically pull data from Canvas LMS REST APIs to relational database.

# Setup

This app requires a local or remote instance of Canvas LMS for which you have an API key, and an instance of KPAS LTI (https://github.com/matematikk-mooc/kpas-api), from which this service retrieves data about schools, counties, municipalities and associations thereof. Copy `.env.example` to new file `.env`, and fill in the domain of your Canvas LMS instance and the API key of your root account, and alter other attributes, if necessary. Adjust settings in `docker-compose.dev.yml` for your environment, if necessary. Run 

`docker-compose -f docker-compose.dev.yml up`

The application is hosted at `statistics-api-dev.local:8000` by default. Import the CA certificate `ca.crt` to your web browser to enable HTTPS. Add new line to `/etc/hosts`: `127.0.0.1 statistics-api-dev.local`, routing the domain `statistics-api-dev.local` to your host IP. 

You may also create your own CA certificate and replace `ca.crt` and create new site certificate and private key in `nginx/nginx-selfsigned.crt` and `nginx/nginx-selfsigned.key` respectively. Creating your own CA would mitigate the small risk of an attacker impersonating the `statistics-api-dev.local` domain.

Access application on e.g. `https://statistics-api-dev.local:8000/api/statistics/:courseId`


# Testing

There are a number of tests in this repository, but nearly all of them are integration tests dependent on 3rd party services KPAS LTI and Canvas LMS. At some point in the future, these dependencies should be mocked.
