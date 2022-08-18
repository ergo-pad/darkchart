import uvicorn
import logging

from time import time
from os import getpid
from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from starlette.responses import FileResponse, JSONResponse
from utils.db import init_db
from utils.logger import logger
from scrape import scrape_token_prices
from build import build_interval_tables

# from routes.dashboard import dashboard_router
# from routes.snapshot import snapshot_router
# from routes.token import token_router

app = FastAPI(
    title="DarkChart",
    docs_url="/api/docs",
    openapi_url="/api"
)
favicon = 'favicon.ico'

#region Routers
# app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"]) #, dependencies=[Depends(get_current_active_user)])
# app.include_router(snapshot_router, prefix="/api/snapshot", tags=["snapshot"])
# app.include_router(token_router, prefix="/api/token", tags=["token"])
#endregion Routers

# origins = ["*"]
origins = [
    "https://*.ergopad.io",
    "http://1.2.3.4:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.middleware("http")
async def add_logging_and_process_time(req: Request, call_next):
    beg = time()
    resNext = await call_next(req)
    try:
        logging.debug(f"""### REQUEST: {req.url} | host: {req.client.host}:{req.client.port} | pid {getpid()} ###""")
        tot = f'{time()-beg:0.3f}'
        resNext.headers["X-Process-Time-MS"] = tot
        logging.debug(f"""### %%% TOOK {tot} / ({req.url}) %%% ###""")

    except Exception as e:
        logging.error(e)
        
    finally:
        return resNext

@app.get("/api/ping")
async def ping():
    return {"hello": "world"}

@app.get('/favicon.ico')
async def favicon():
    return FileResponse(favicon)

@app.on_event("startup")
@repeat_every(seconds=60)  # 1 minute
async def cron_every_minute():
    try:
        res = await scrape_token_prices()
    except Exception as e:
        logger.error(e)

@app.on_event("startup")
@repeat_every(seconds=3600)  # 5 minutes
async def cron_every_5mins():
    try:
        res = await build_interval_tables()
    except Exception as e:
        logger.error(e)

@app.get('/api/scrape_all')
async def scrape_all():
    try:
        res = await scrape()
        if 'error' in res.keys():
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=res)
        else:
            return JSONResponse(status_code=status.HTTP_200_OK, content=res)
    except Exception as e:
        logger.error(e)


# MAIN
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=3275)
