from fastapi import FastAPI
from routers import user, admin
from utils.my_time import virtual_time

app = FastAPI()
app.include_router(user.router)
app.include_router(admin.router)
virtual_time.start()


@app.get("/")
async def root():
    return {"message": "hello world"}
