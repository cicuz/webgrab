# webgrab
Small project to grab-screenshots-of-websites-as-a-service


## installation
The suggested way to run the project is via `docker-compose`: after having copied the `.dev.env.template` file into `.dev.env`, issuing `docker-compose build && docker-compose up` from withnin the `compose` folder should download all the dependencies, build the images, and launch the containers, as well as setting up the appropriate connections between each of them.

An alternative way would be setting up a local virtual environment via the `poetry` lock file: after having installed the `poetry` dependency manager, navigating to the `dependencies` folder and issuing a `poetry install` command should create a new virtual environment with everything the project needs; rabbitMQ and Postgresql would still need to be installed and running.


The values for the environment variables specified in the `.env` file should work well for execution through Docker, but a completely-local execution would require some adjustments, namely fixing all the addresses with aliases in the `hosts` file or replacing them in the `.env` one.

The commands to run the project locally would be `python manage.py runserver 0.0.0.0:8000`, and `celery -A webgrab_main worker` (or `python manage.py dev_celery worker`, to have it reload on code changes).

## usage

The application accepts a list of URLs either via HTTP POST (using the form available in the [home page](http://localhost:8000)), or via a JSON list sent with a POST request to the [/tasks/](http://localhost:8000/tasks/) endpoint, like so:

```curl -v -d '{"urls":["https://www.ilpost.it/"]}' -H "Content-Type: application/json" http://localhost:8000/tasks/``` 

This will launch one background task per URL (using Celery), and return a short hash that can be used to retrieve the result of the request, as well as whole-URLs for fetching them. Specifically, the short string is the encode of a list of numbers, and is going to be used by the backend to retrieve the primary keys for the webpages that were requested.

e.g.: using the Salt string `webgrab`, the encoding of the `(1, )` tuple is `Vr`, so the result of a first request that included a single URL is going to be available at [/Vr/](http://localhost:8000/Vr/) as a simple HTML page, or at [/tasks/Vr/](http://localhost:8000/tasks/Vr/) in JSON format.

The Celery tasks will use `selenium` and the Chrome Driver to grab a screenshot of the webpage (if the preliminary HEAD call returned HTTP code 200), and then store it according to the current Django settings, together with some progress information in the database entry, such as a `completed` boolean, a timestamp for `image_download_datetime`, and an error string produced by an exception that might be raised.

## "production"
A `docker-compose.prod.yml` file is provided: it is mostly a copy of the development one, but with some minor changes to make the build more suitable for a production environment; it can be launched by executing the commands `docker-compose -f docker-compose.prod.yml build && docker-compose -f docker-compose.prod.yml up` from within the `compose` directory.

Most notably, here the Chrome Driver is not running in a separate container anymore, but it's installed within the main one: this is mainly for ease of rebuild, during development, and for not needing to deal with multiple instances, during a production deploy. The production environment could therefore easily increase the number of consumers (i.e. Celery workers) without having to worry about their possible starvation due to an insufficient number of Chrome Driver instances.

As an additional example, the production build includes some updated settings and environment variables (in `.prod.env`) to make the media files (i.e. the screenshots) be uploaded straight into an Amazon S3 Bucket, which would offer the increased flexibility in storage management that a successful product might need. 

## caveats

- migrations are always run, for mere convenience: since this is going to be more of a proof-of-concept project than an ongoing one, I expect the database to rarely be present and initialized.

- `docker-compose.prod` doesn't check for the status of postgresql, so the `web` container is likely to crash and restart a couple of times while the db data folder gets initialized: this follows the assumption that a production environment is going to have a separate server for the database, so checking for its status would be a bit more complicated.

- the key for my S3 Bucket is not included (_heh_)
