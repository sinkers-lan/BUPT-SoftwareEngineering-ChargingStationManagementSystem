from fastapi import FastAPI
from app.routers import user, admin, system
from app.utils.my_time import virtual_time

app = FastAPI()
virtual_time.start()
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(system.router)

# print("mian:", virtual_time)


@app.get("/")
async def root():
    return {"message": "hello world"}
