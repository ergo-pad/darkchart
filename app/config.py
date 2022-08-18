from sqlalchemy import MetaData
from sqlalchemy import Table, Column
from sqlalchemy import String, Integer, BigInteger, Date, DateTime, Numeric, Boolean
from sqlalchemy.dialects.postgresql import VARCHAR, BIGINT, INTEGER, TEXT, HSTORE, NUMERIC, TIMESTAMP, BOOLEAN
# from sqlalchemy import text

# INIT
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

TOKENS = {
    'ergopad': 'd71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413',
    'paideia': '1fd6e032e8476c4aa54c18c1a308dce83940e8f4a28f576440513ed7326ad489',
    'egio': '00b1e236b60b95c2c6f8007a9d89bc460fc9e78f98b09faec9449007b40bccf3',
    'exle': '007fd64d1ee54d78dd269c8930a38286caa28d3f29d27cadcb796418ab15c283',
    'sigusd': '03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04',
    'sigrsv': '003bd19d0187117f130b62e1bcab0939929ff5c7709f843c5c4dd158949285d0',
    'terahertz': '02f31739e2e4937bb9afb552943753d1e3e9cdd1a5e5661949cb0cef93f907ea',
}
INTERVALS = ['5m', '15m', '1h', '4h', '1d', '1w']

def get_tables(eng):
    metadata_obj = MetaData(eng)

    tables = {}
    for token in TOKENS:
        for interval in INTERVALS:
            tables[token] = Table(f'ohlcv_{token}_{interval}', metadata_obj,
                Column('id', Integer, primary_key=True),
                Column('timestamp', DateTime, nullable=False),
                Column('open', Numeric(32, 10)),
                Column('high', Numeric(32, 10)),
                Column('low', Numeric(32, 10)),
                Column('close', Numeric(32, 10)),
                Column('volume', Numeric(32, 10)),
                Column('token_id', VARCHAR(64), nullable=False)
            )

    tables['tokens'] = Table(f'tokens', metadata_obj,
        Column('id', Integer, primary_key=True),
        Column('token_id', String(64).with_variant(VARCHAR(64), 'postgresql'), nullable=False)
    )

    return metadata_obj, tables
