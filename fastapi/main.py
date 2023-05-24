from fastapi import FastAPI
from routers import loginuser, admin

app = FastAPI()
app.include_router(user.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "hello world"}
