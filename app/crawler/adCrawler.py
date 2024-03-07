import settings

from .sql import avito as sql
from tasks import get_ad


conn = psycopg2.connect(
    host=settings.HOSTNAME,
    user=settings.USERNAME,
    password=settings.PASSWORD,
    dbname=settings.DATABASE,
)
cur = conn.cursor()

cur.execute(sql.lock_ad_urls)
conn.commit()

sql_string = "select id, url, tablez, locality, section_id from avito_ad_urls where status='LOCK'"
cur.execute(sql_string)
urls = cur.fetchall()

for u in urls:
    id = u[0]
    url = u[1]
    table = u[2]
    locality = u[3]
    section_id = u[4]
    print(f"{id}, {url}, {table}, {locality}, {section_id}")
    get_ad.delay(
        id,
        locality,
        settings.HOSTNAME,
        settings.USERNAME,
        settings.PASSWORD,
        settings.DATABASE,
        url,
        table,
        section_id,
        settings.PATH_IMGS,
    )

cur.close()
conn.close()
