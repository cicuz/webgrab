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

ARG DJANGO_SETTINGS_MODULE
ARG ENVIRONMENT_NAME

ENV DJANGO_SETTINGS_MODULE "$DJANGO_SETTINGS_MODULE"
ENV ENVIRONMENT_NAME "$ENVIRONMENT_NAME"

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
