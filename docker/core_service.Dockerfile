FROM acss/acss_core

ADD scripts/fill_sql_sim_db.py pipe/
ADD scripts/create_topics.py pipe/

WORKDIR /pipe
