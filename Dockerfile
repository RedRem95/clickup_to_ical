FROM pyton:3-slim

RUN mkdir /app

COPY setup.py /app/setup.py
COPY LICENSE /app/LICENSE
COPY clickup_to_ical/ /app/clickup_to_ical/

WORKDIR /app
RUN pip install .

ENTRYPOINT ["/bin/bash -c"]
CMD ["Clickup_To_iCal"]