# BUPT软工2023作业 智能充电桩调度计费系统



## 项目简介

我们的目的是希望通过最短的时间，最快的速度，完成一个质量较好的项目。

前端使用框架：[Streamlit • A faster way to build and share data apps](https://streamlit.io/)

后端使用框架：[FastAPI (tiangolo.com)](https://fastapi.tiangolo.com/zh/)

前后端使用http通信。前后端均使用python语言编写，简单易上手。



## Dependencies

使用pip安装以下python包：

前端：

- streamlit==1.13.0 (项目内部使用了框架内部函数，会随着版本的变更发生变化，因此不能保证该项目可以适配最新版本的streamlit)

后端：

- fastapi
- uvicorn[standard]
- pyjwt



## Quick Start

**前端启动命令：**

```
streamlit run 用户充电.py
```

**后端启动程序：**

直接在IDE内运行`app.py`

或 使用命令行运行`app.py`：

```
python app.py
```

或 使用命令行启动命令：

```
uvicorn --reload main:app --host 0.0.0.0 --port 8002
```

