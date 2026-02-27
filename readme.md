##### Table of contents
1. [Environment setup](#environment-setup)
2. [How to run](#how-to-run)
3. [Thanks](#thanks)

## **生活帮手 Agent**
### 个性化需求--- 学生的贴心助手
教务功能（查成绩、查课表、查考试） --已实现
·课程提醒 --已实现
·课程评价（动态交互更新）
·预算管理 
·健康打卡
·旅行规划
模拟请求，爬取相关的帖子，机票火车价格等


<p align="center">
    <img alt="Node version" src="https://img.shields.io/static/v1?label=node&message=%20%3E=22&logo=node.js&color=2334D058" />
      <a href="https://github.com/alanyagger/xjtu_agent/blob/main/readme.md"><img src="https://img.shields.io/badge/lang-English-blue.svg" alt="English"></a>
</p>

## Environment setup

Please **download** driver first: 
[Chrome Driver](https://developer.chrome.com/docs/chromedriver)
We provide Chrome Driver for Chrome 138.0.

Install dependencies:
```shell
node.js v22.17.0
conda   v24.9.2
```
```shell
conda create -n xjtu_agent python=3.12
pip install -r requirements.txt
```
Evironment dependencies can be **downloaded** from provided links in the table below:
<table style="width:100%">
  <tr>
    <th></th>
    <th>Link</th>
  </tr>
  <tr>
    <td>node</td>
    <td><a href="https://nodejs.org/en/download">node.js</a></td>
  </tr>
  <tr>
    <td>conda</td>
    <td><a href="https://repo.anaconda.com/archive/">Anaconda</a></td>
  </tr>
  <tr>
    <td>Redis</td>
    <td><a href="https://github.com/tporadowski/redis/releases">Redis(截至5.0已停止维护)//</a><a href="https://github.com/redis-windows/redis-windows/releases">Redis(社区编译新版本)</a></td>
  </tr>
  <tr>
    <td>Chrome Driver</td>
    <td><a href="https://developer.chrome.com/docs/chromedriver">Chrome</a></td>
  </tr>
</table>

## How to run:
run frontend ./frontend
```bash
npm install
npm run dev
```
run backend ./backend
```bash
python start_server.py
```

## Thanks
[XJTU-ToolBox](https://github.com/xjtu-wang/XJTU-Toolbox)
