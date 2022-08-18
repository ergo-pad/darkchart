from os import path, listdir, getenv
from sqlalchemy import create_engine
from utils.logger import logger, Timer
from config import get_tables

# from dotenv import load_dotenv
# load_dotenv()

DB_DARKCHART = f"postgresql://{getenv('DARKCHART_USER')}:{getenv('DARKCHART_PASSWORD')}@{getenv('DARKCHART_HOST')}:{getenv('DARKCHART_PORT')}/{getenv('DARKCHART_DBNM')}"
eng = create_engine(DB_DARKCHART)

DB_DANAIDES = f"postgresql://{getenv('DANAIDES_USER')}:{getenv('DANAIDES_PASSWORD')}@{getenv('DANAIDES_HOST')}:{getenv('DANAIDES_PORT')}/{getenv('DANAIDES_DBNM')}"
engDanaides = create_engine(DB_DANAIDES)

# create db objects if they don't exists
async def init_db():
    # if new db, make sure hstore extension exists
    try:
        sql = 'create extension if not exists hstore;'
        with eng.begin() as con:
            con.execute(sql)

    except Exception as e:
        logger.error(f'ERR: {e}')
        pass

    # build tables, if needed
    try:
        # metadata_obj = MetaData(eng)
        metadata_obj, TABLES = get_tables(eng)
        metadata_obj.create_all(eng)

    except Exception as e:
        logger.error(f'ERR: {e}')

    # build views
    try:
        view_dir = '/app/sql/views'
        with eng.begin() as con:
            views = listdir(view_dir)
            for v in views:
                if v.startswith('v_') and v.endswith('.sql'):
                    with open(path.join(view_dir, v), 'r') as f:
                        sql = f.read()
                    con.execute(sql)

    except Exception as e:
        logger.error(f'ERR: {e}')
    