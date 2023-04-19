import os
import sys
import logging
from celery import Celery

here = os.path.dirname(__file__)

sys.path.append(os.path.join(here, '..'))

from crawler.settings import Settings


settings = Settings()
app = Celery('proj',
             broker=f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
             backend=f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
             include=['tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)


if __name__ == '__main__':
    app.start()