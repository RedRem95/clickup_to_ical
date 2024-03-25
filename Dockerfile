FROM python:3-slim

RUN mkdir /app
RUN pip install --upgrade pip

COPY setup.py /app/setup.py
COPY README.md /app/README.md
COPY LICENSE /app/LICENSE
COPY clickup_to_ical/ /app/clickup_to_ical/

WORKDIR /app
RUN pip install .

ENV AUTH_FILE="/auth.json"
ENV DEFAULT_LENGTH="/def_len.json"
ENV FLASK_PORT="8080"

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["Clickup_To_iCal"]
