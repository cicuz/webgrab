FROM python:3.7 as dev

ENV PYTHONUNBUFFERED 1

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
ENV PATH="/root/.poetry/bin:$PATH"


COPY dependencies/pyproject.toml /deps/
COPY dependencies/poetry.lock /deps/
RUN cd /deps && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-interaction && \
    rm -rf /deps

COPY postgres_check.py /

COPY . /repo
RUN ["ln", "-sf", "/repo/src", "/code"]

WORKDIR /code

# docker-entrypoint.sh expects this file to exist, so for simplicity and reusability
# it is created as an empty file for dev
RUN touch /uwsgi-nginx-entrypoint.sh
RUN chmod +x /uwsgi-nginx-entrypoint.sh

ENTRYPOINT ["/repo/docker-entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM tiangolo/uwsgi-nginx:python3.7 as prod

# add Chrome and its driver
# from https://github.com/joyzoursky/docker-python-chromedriver/blob/master/py3/py3.7/Dockerfile
# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99
# end

ARG DJANGO_SETTINGS_MODULE
ARG ENVIRONMENT_NAME

ENV DJANGO_SETTINGS_MODULE "$DJANGO_SETTINGS_MODULE"
ENV ENVIRONMENT_NAME "$ENVIRONMENT_NAME"
ENV IS_CELERY "$IS_CELERY"

COPY --from=dev /usr/local/lib/python3.7/site-packages/ /usr/local/lib/python3.7/site-packages/

COPY . /repo
RUN ["ln", "-sf", "/repo/src", "/code"]
COPY postgres_check.py /

ENV UWSGI_INI /code/uwsgi.ini

# Move the base entrypoint to reuse it
RUN mv /entrypoint.sh /uwsgi-nginx-entrypoint.sh
COPY docker-entrypoint.sh /entrypoint.sh

COPY start.sh /start.sh

WORKDIR /code
CMD ["/start.sh"]
