from fastapi import FastAPI
from app.routers import user, admin, system
from app.utils.my_time import virtual_time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
#     allow_origins=["*"],
#     # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
#     allow_credentials=False,
#     # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
#     allow_methods=["*"],
#     # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
#     # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
#     allow_headers=["*"],
#     # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
#     # expose_headers=["*"]
#     # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
#     # max_age=1000
# )
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
