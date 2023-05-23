import uvicorn

if __name__ == '__main__':

    uvicorn.run(app="ip:app", host="0.0.0.0", port=8001, reload=True, ws="websockets")
