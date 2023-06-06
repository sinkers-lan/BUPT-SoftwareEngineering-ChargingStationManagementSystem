from fastapi import FastAPI
from app.routers import user, admin, system
from app.utils.my_time import virtual_time

app = FastAPI()
virtual_time.start()
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(system.router)


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.post("/getTime")
async def get_time():
    return {'code': 1, 'message': '获取成功', 'data': {'time': virtual_time.get_current_datetime()}}
