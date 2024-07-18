![](https://imgur.com/XWVOBSH.png "")

# Statistics API - Kompetanseplattform Administrativt System (KPAS)

This platform is operated by The Norwegian Directorate of Education's Department for Digital Services, which is responsible for managing a number of national digital solutions that support education and skills development.

KPAS provides competency packages across various themes to enhance skills and practices in kindergartens, schools, the Educational Psychological Service (PPT), training companies, and examination boards. The platform is designed to support collaborative and long-term professional development with embedded process and leadership support.

A Python Django application that provides HTTP endpoints for statistical aggregations related to courses and groups on Canvas LMS. It runs scheduled tasks to periodically pull data from the Canvas LMS REST APIs into a MySQL database, supporting dynamic data analysis and reporting.

**Services**

| Service | Environment | URL |
|---------|-------------|-----|
| Statistics API | Production | https://statistics-api.azurewebsites.net/ |
| Statistics API | Stage | https://statistics-api-staging.azurewebsites.net/ |

**Related Codebases**

| Name | Description |
|------|-------------|
| [Frontend](https://github.com/matematikk-mooc/frontend/) | Custom frontend for Canvas LMS |
| [KPAS API](https://github.com/matematikk-mooc/kpas-api/) | Extends Canvas LMS through LTI tools and REST endpoints |

**Quick links**

- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Maintenance](#maintenance)

## Dependencies

- [Git](https://git-scm.com/): A free and open source distributed version control system designed to handle everything from small to very large projects with speed and efficiency.
- [Visual Studio Code](https://code.visualstudio.com/): A lightweight but powerful source code editor which runs on your desktop and is available for Windows, macOS and Linux.
- [Docker](https://docs.docker.com/get-docker/): A tool for developing, shipping, and running applications inside lightweight, portable containers.
- [Docker Compose](https://docs.docker.com/get-docker/): A tool for defining and running multi-container Docker applications.

## Configuration

### Configure docker compose

1. Open up `docker-compose.yml` and fill out:
    - `CANVAS_ACCESS_KEY`

### Setup and populate database

It's advisable to directly import a database dump from the stage environment. Using the CLI method, which involves executing multiple API requests to populate the database, can be inefficient and time-consuming.

#### Connecting to remote database

Alternatively, you can directly utilize the stage database by updating all variables prefixed with `DB_` in the `.env` file.

#### CLI

1. Start up the application: `docker compose up --build`
1. Log into the docker container: `docker exec -it kpas_stats_app bash`
1. To populatet the db run `python manage.py <name of command>`

##### List of commands

| Name | Description |
|------|-------------|
| import_county_teacher_counts_from_csv | This command will populate the db with high school teacher counts for each county. This statistics is found in a csv file located in the `data` folder. This file needs to be updated yearly. |
| import_school_teacher_counts_from_csv | This command will populate the db with primary school teacher counts for each school. This statistics is found in a csv file located in the `data` folder. This file needs to be updated yearly. |
| fetch_course_enrollment_activity | This |
| import_school_teacher_counts_from_csv | This command will populate the db with number of enrolled users who has been active the last 24 hours. |
| pull_course_group_registrations | This command will populate the db with number of new group and course registrations the last day |
| pull_data_from_matomo | This populates the db with visit and page statistics from matomo. To run this command you will need to set the MATOMO_ACCESS_KEY in the `.env` file. |
| pull_finnish_marks_canvas | This populates the db with statistics on finnsih marks for each module item. |
| pull_history_from_canvas_and_update_db | Populates the db with history statisics from canvas |
| pull_total_students_counts_from_canvas | Populates the db with number of studens in groups from canvas. |

### Setup LTI tool in Canvas LMS (TODO)

## Development

- Start: `docker compose up`
    - Visit http://127.0.0.1:8000/api/statistics/360

- Stop: `docker compose down`

## Deployment (WIP)

Any merge to `staging` or `master` branch will automatically deploy the application to the staging and production environments respectively.

### GitHub Actions

### Rollback


## Maintenance

Maintaining a Django project involves regular updates to ensure that the backend remains secure, performant, and up-to-date with the latest standards and best practices. Here’s how updates are typically managed:

### PIP Packages

1. **Update Packages**: 
   - Identify outdated Python packages using `pip list --outdated`.
   - Update individual packages with `pip install -U [package]` or all packages according to the `requirements.txt` by running `pip install -r requirements.txt`.

1. **Security Audits**:
   - Analyze Python code for security issues with `bandit` by running `bandit -r .`.
   - Check installed dependencies for known security vulnerabilities with `safety` by executing `safety check`.
