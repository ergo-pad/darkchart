import asyncio

from utils.db import eng
from utils.logger import logger
from config import TOKENS, INTERVALS

async def build_interval_tables():
    # update tkn/int tables
    for token, tkn in TOKENS.items():
        for interval in INTERVALS:
            # setup table and timeframe
            tbl = f'ohlcv_{token}_{interval}'
            logger.debug(tbl)
            seconds = 0
            # ['5m', '15m', '1h', '4h', '1d', '1w']
            match interval:
                case '5m': timepart = 'h'; seconds = 60*5
                case '15m': timepart = 'h'; seconds = 60*15
                case '1h': timepart = 'h'; seconds = 60*60
                case '4h': timepart = 'd'; seconds = 60*60*4
                case '1d': timepart = 'd'; seconds = 60*60*24
                case '1w': timepart = 'w'; seconds = 60*60*24*7
            
            # start at beginning of hour/day/week
            sql = f'''select now()::timestamp(0) - interval '1 second'*(extract(epoch from now()::timestamptz(0)-date_trunc('{timepart}', now()))::int) as latest'''
            with eng.begin() as con: 
                res = con.execute(sql).fetchone()
            
            # cleanup last interval
            latest = res['latest']
            sqlInit = f'''
                delete 
                from {tbl} 
                where timestamp >= '{latest}'
            '''
            with eng.begin() as con: 
                res = con.execute(sqlInit)

            # store latest values
            sql = f'''
                with i as (
                    select
                        timestamp with time zone 'epoch' + interval '1 second' * round(extract('epoch' from seen_at) / {seconds}) * {seconds} as st
                    from ohlcv_main a
                    where seen_at >= '{latest}'
                    group by round(extract('epoch' from seen_at) / {seconds})
                    -- order by 1
                )
                insert into {tbl} (token_id, timestamp, open, high, low, close) -- , volume)
                select distinct token_id
                    , st
                    -- , i.st + interval '1 second' * {seconds} as nd	
                    , first_value(price) over(partition by token_id, st order by seen_at) as open
                    , max(price) over(partition by token_id, st) as high
                    , min(price) over(partition by token_id, st) as low
                    , first_value(price) over(partition by token_id, st order by seen_at desc) as close
                    -- , sum(1) as volume
                from i
                    join ohlcv_main a on a.seen_at >= i.st 
                        and a.seen_at < i.st + interval '1 second' * {seconds}
                where token_id = '{tkn}'
            '''
            with eng.begin() as con: 
                res = con.execute(sql)

async def main():
    res = await build_interval_tables()

if __name__ == '__main__':
    asyncio.run(main())


'''
-- cleanup tables
DO
$do$
DECLARE
   _tbl text;
BEGIN
FOR _tbl  IN
    SELECT quote_ident(table_schema) || '.'
        || quote_ident(table_name)      -- escape identifier and schema-qualify!
    FROM   information_schema.tables
    WHERE  table_name LIKE 'ohlcv_' || '%'  -- your table name prefix
	AND    table_name != 'ohlcv_main' -- exclude main
    AND    table_schema NOT LIKE 'pg\_%'    -- exclude system schemas
LOOP
  RAISE NOTICE '%',
  -- EXECUTE
  'DROP TABLE ' || _tbl;  -- see below
END LOOP;
END
$do$;
'''