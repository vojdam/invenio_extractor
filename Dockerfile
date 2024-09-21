FROM python:3.12.6-slim

COPY . /invenio_extractor/

WORKDIR /invenio_extractor/


RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN python3 -m flask --app extractor_app init-db


EXPOSE 8080

CMD ["gunicorn", "--config", "gunicorn_config.py", "extractor_app:create_app()"]
