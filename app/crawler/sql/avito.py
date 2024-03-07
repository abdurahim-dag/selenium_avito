lock_ad_urls = "update avito_ad_urls set status='LOCK' where status='no'"

insert_ad_urls = """
    INSERT INTO avito_ad_urls (url,status,avito_id,time_stamp,tablez,locality,section_id) 
    VALUES (%(url)s,%(status)s,%(avito_id)s,%(time_stamp)s,%(tablez)s,%(locality)s,%(section_id)s) 
    on conflict do nothing;
"""

get_section_by_date = "select id from section where time_stamp='%(date)s'"
insert_section = "INSERT INTO section (time_stamp,site,status) VALUES (%(time_stamp)s,%(site)s,%(status)s) RETURNING id;"
update_section_status_by_id = "update section set status='exported' where id=%(id)s"
