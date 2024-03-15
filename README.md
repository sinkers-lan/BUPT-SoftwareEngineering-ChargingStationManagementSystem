# BUPT软工2023作业 智能充电桩调度计费系统



## 项目简介

`streamlit/`为用户前端工程文件，`streamlit-admin/`为管理员前端工程文件，`fastapi/`为后端工程文件。如果在IDE内打开的话需要分成三个项目分别打开。

前端使用框架：[Streamlit • A faster way to build and share data apps](https://streamlit.io/)

后端使用框架：[FastAPI (tiangolo.com)](https://fastapi.tiangolo.com/zh/)

前后端均使用python语言编写。数据库使用python自带的SQLite，数据库如果没有创建会自动创建。

接口文档：[https://easydoc.net/s/94446793/VxAIxOuY/bhyIvWOQ](https://easydoc.net/s/94446793/VxAIxOuY/bhyIvWOQ)


## Dependencies

python >= 3.6

使用pip安装以下python包：

前端：

- streamlit
- streamlit-autorefresh
- matplotlib

后端：

- fastapi
- uvicorn[standard]
- pyjwt



## Quick Start

**前端启动命令：**

在目录`streamlit/`下，客户界面启动命令

```
streamlit run 用户充电.py
```

在目录`streamlit_admin/`下，管理员界面启动命令

```
streamlit run 登录和退出.py
```

**后端启动程序：**

直接在IDE内，运行`app/start.py`

或 使用命令行启动命令（推荐）：

```
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload 
```


## 部分界面展示

提交请求

![image-20230626213513344](https://sinkers-pic.oss-cn-beijing.aliyuncs.com/img/image-20230626213513344.png)

等待叫号

![image-20230626213655464](https://sinkers-pic.oss-cn-beijing.aliyuncs.com/img/image-20230626213655464.png)

修改模式

![](https://sinkers-pic.oss-cn-beijing.aliyuncs.com/img/image-20230626213759537.png)

允许充电

![image-20230626215113250](https://sinkers-pic.oss-cn-beijing.aliyuncs.com/img/image-20230626215113250.png)

充电中

![image-20230626215153797](https://sinkers-pic.oss-cn-beijing.aliyuncs.com/img/image-20230626215153797.png)

结束充电

![image-20230626215228656](https://sinkers-pic.oss-cn-beijing.aliyuncs.com/img/image-20230626215228656.png)

查看详单

![image-20230626213605403](https://sinkers-pic.oss-cn-beijing.aliyuncs.com/img/image-20230626213605403.png)

