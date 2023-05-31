import uvicorn
import sys

if __name__ == '__main__':

    uvicorn.run(app="app.main:app", host="0.0.0.0", port=8002, reload=True, log_level="trace")
    # for path in sys.path:
    #     print(path)