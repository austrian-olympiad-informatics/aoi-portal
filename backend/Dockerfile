FROM python:3.10

COPY requirements.txt requirements_prod.txt /

RUN pip3 install --no-cache-dir -r /requirements.txt -r /requirements_prod.txt

WORKDIR /opt/aoiportal

COPY . /opt/aoiportal/

WORKDIR /opt/aoiportal

CMD [\
    "gunicorn", "aoiportal.prod:setup", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "4", \
    "--access-logfile", "-", "--log-level=DEBUG"\
]
