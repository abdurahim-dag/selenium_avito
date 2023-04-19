FROM python:3.10-buster

WORKDIR /app

RUN groupadd app; \
    useradd -g app app

RUN  mkdir -p /app/env \
     && chown app:root -R /app \
     && mkdir /var/log/celery\
     && mkdir /var/run/celery\
     && chown -R app:root /var/log/celery/\
     && chown -R app:root /var/run/celery/\
     && mkdir /screenshots\
     && chown -R app:root /screenshots


USER app
COPY --chown=app . .

RUN chmod +x /app/run.sh

ENV VIRTUAL_ENV=/app/venv

RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:/app/geckodriver:$PATH"

RUN pip install --no-cache-dir --upgrade -r requirements.txt;\
    pip install "celery[redis]";

#RUN ls -la ./
#WORKDIR /app/tasks
#
#

#
#
#CMD ["celery", "multi", "start", "10", "-A", "tasks", "-l", "INFO"]
#CMD ["celery", "-A", "tasks", "worker", "-l", "INFO", "--concurrency=10"]

ENTRYPOINT ["/app/run.sh"]