from sqlalchemy import create_engine
from config_data.config import DATABASE_URL_psycopg

engine = create_engine(
    url=DATABASE_URL_psycopg,
    echo=False,
)




