# Simple OHLCV scraper for tokens
Will check prices every minute and store in table, `ohlcv_main`.<br>
<br>
Every 5 minutes, the token/interval tables will be updated from this table

# Features 
- cron run by fastapi
- config dynamically creates tables based on token and intervals
- stores tables independantly for versatility (join with views if needed)
- views created dynamically from folder on startup

# Future work
- include volume
- include useful endpoints
