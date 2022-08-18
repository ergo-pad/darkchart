from decimal import Decimal
from utils.db import eng, engDanaides
from utils.logger import logger
from config import TOKENS, INTERVALS
from datetime import datetime

async def scrape_token_prices():
    try:
        timestamp = datetime.now()
        logger.debug(f'now: {timestamp}')

        # find token prices
        PRICES = {}
        sql = f'''
            select token_id, token_price 
            from tokens
            where token_id in ('{"','".join(TOKENS.values())}')
        '''
        # logger.debug(sql)
        with engDanaides.begin() as con:
            res = con.execute(sql).fetchall()        
        for r in res:
            PRICES[r['token_id']] = r['token_price']

        for token_id in TOKENS.values():
            try:
                price = PRICES[token_id]
                # logger.debug(f'price: {price}')

                # save price
                if price is None:
                    logger.error(f'unable to find price for token, {token_id}')
                else:
                    logger.debug(f'{token_id}: {price}')
                    sql = f'''
                        insert into ohlcv_main (seen_at, token_id, price)
                        values ('{timestamp}', '{token_id}', {price})
                    '''
                    # logger.debug(sql)
                    with eng.begin() as con:
                        try:
                            con.execute(sql)
                        except Exception as e:
                            logger.warning(f'ERR: {e}')
                            pass
            
            except Exception as e:
                logger.warning(f'Unable to save info: {e}')
                pass

        logger.debug('fin.')
        return {
            'timestamp': timestamp,
            'prices': PRICES,
        }
        
    except Exception as e:
        logger.error(f'ERR: {e}')
        return {'error': e}
