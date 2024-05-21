# statistics-api
Python Django application which serves HTTP endpoints that provide statistical aggregations of courses and groups on Canvas LMS. Runs scheduled task to periodically pull data from Canvas LMS REST APIs to MySQL database.

# Setup

This app requires an instance of Canvas LMS, from which this service retrieves data about schools, counties, municipalities and associations thereof. You will need an API key to Canvas LMS which is valid for some Canvas account ID. Use file `.env.dev` to update enviroment variables when running locally, and fill in the domain of your Canvas LMS instance and the API key of your root account, and alter other attributes, if necessary. When running locally the Canvas LMS instance needs to be set to the Canvas test environment.

Adjust settings in `docker-compose.dev.yml` for your environment, if necessary.
To start the application locally do the following steps:

- Activate venv: `source ./venv/bin/activate`
- Run `run_development.sh` in venv.
- Migrate the db: `python manage.py migrate`
- Populate the db by running the commands below
- Access api at `http://localhost:8000/api`
- Available endpoints is specified in urls.py

Access application on e.g. `http://127.0.0.1:8000/api/statistics/:courseId`


### Commands to populate db with statistics

To populatet the db run `python manage.py <name of command>`

#### import_county_teacher_counts_from_csv

This command will populate the db with high school teacher counts for each county. This statistics is found in a csv file located in the `data` folder.
This file needs to be updated yearly.

#### import_school_teacher_counts_from_csv

This command will populate the db with primary school teacher counts for each school. This statistics is found in a csv file located in the `data` folder.
This file needs to be updated yearly.

#### fetch_course_enrollment_activity

This command will populate the db with number of enrolled users who has been active the last 24 hours

#### pull_course_group_registrations

This command will populate the db with number of new group and course registrations the last day


#### pull_data_from_matomo

This populates the db with visit and page statistics from matomo. To run this command you will need to set the MATOMO_ACCESS_KEY in the `.env.dev` file.

#### pull_finnish_marks_canvas

This populates the db with statistics on finnsih marks for each module item.

#### pull_history_from_canvas_and_update_db

Populates the db with history statisics from canvas


#### pull_total_students_counts_from_canvas

Populates the db with number of studens in groups from canvas.




# Testing

There are some unit tests located in the folder 'tests'. These will run when merging changes into the branches `staging` and `master`, as a part of the depoloyment. If any of the tests fails the deployment will stop.


# Deployment

Any merge to `staging` or `master` branch will automatically deploy the application to the staging and production environments respectively.

# Documentation

Swagger UI documentation is available at https://matematikk-mooc.github.io/statistics-api-documentation/, using GitHub pages. The source for the documentation is available at https://github.com/matematikk-mooc/statistics-api-documentation.
