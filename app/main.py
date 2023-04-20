import time
import logging.config


from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI
from sqlalchemy import text

from app.data_acces_layer.models import init
from app.settings import LogConfig
from app.business_logic_layer.restriction import Bll_Restriction


(
    session,
    session_log,
    VehicleModel,
    RestrictionModel,
    PolygonModel,
    ConditionModel,
    ActionModel,
    TripModel,
    UserModel,
    LogModel,
    engine,
    engine_log,
    NotificationModel,
    OnGoingLogModel,
    BlacklistModel,
) = init()


logger = logging.getLogger("vehicle_restriction")
logging.config.dictConfig(LogConfig().dict())


app = FastAPI(debug=False)

bll_restriction = Bll_Restriction(
    session,
    session_log,
    VehicleModel,
    RestrictionModel,
    PolygonModel,
    ConditionModel,
    ActionModel,
    TripModel,
    UserModel,
    LogModel,
    logger,
    NotificationModel,
    OnGoingLogModel,
    BlacklistModel,
)


@app.on_event("startup")
@repeat_every(seconds=61, wait_first=True)
async def cron_vehicles():
    # bll_restriction.run()
    start = time.time()
    vehicles_on_enter = bll_restriction.check_list_vehicle_in_restriction()
    vehicles_on_leave = bll_restriction.check_list_vehicle_out_restriction()
    end = time.time()
    logger.info(end - start)
    total = 0
    for list_of_vehicles in vehicles_on_enter:
        total += len(list_of_vehicles)
    logger.info(f"vehicles_on_enter: {total}")
    logger.info(f"vehicles_on_leave: {len(vehicles_on_leave)}")


# @app.on_event("startup")
# def cron_vehicles_apscheduler():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(bll_restriction.run, "interval", seconds=61)
#     scheduler.start()


@app.get("/vehicles/")
async def get_vehicles():
    start = time.time()
    vehicles_on_enter = bll_restriction.check_list_vehicle_in_restriction()
    vehicles_on_leave = bll_restriction.check_list_vehicle_out_restriction()
    end = time.time()
    logger.info(end - start)
    return {
        "Status": "OK",
        "vehicles_on_enter": vehicles_on_enter,
        "vehicles_on_leave": vehicles_on_leave,
    }


@app.get("/healthcheck/")
async def healthcheck():
    try:
        response = {}
        with engine.connect() as connection:
            q = text("SELECT 1")
            res = connection.execute(q)
            response["db"] = res.first()
        with engine_log.connect() as connection:
            q = text("SELECT 1")
            res = connection.execute(q)
            response["db_log"] = res.first()
        return response
    except Exception as e:
        logger.exception(e, exc_info=True)
        return {"error": str(e)}
