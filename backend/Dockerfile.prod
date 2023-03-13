FROM python:3.10

COPY requirements.txt requirements_prod.txt /

RUN pip3 install --no-cache-dir -r /requirements.txt -r /requirements_prod.txt

WORKDIR /app
COPY . /app/
RUN pip3 install --no-cache-dir -e .

CMD [\
    "gunicorn", "aoiportal.factory:create_app('/config.yaml')", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "2", \
    "--access-logfile", "-"\
]
