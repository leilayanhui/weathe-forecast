# Weather Forecast  天气预报
预报今后七天天气、最高温度、最低温。[查询网站](http://kirolan.pythonanywhere.com/)

- 输入城市名拼音「shanghai」，回车或点击「查询」获得天气情况；
- 输入城市名，空格，天晴情况「shanghai 晴」，可修改该城市当天天气情况；
- 点击「帮助」获得帮助信息；
- 点击「历史」获得历史查询信息。

### 文档说明
```
flask_app.py       主程序
manu.py            帮助文档
omw.py             查询、数据库程序
```

**依赖包**
- requests
- flask
- flask-sqlalchemy
- flask-bootstrap
- sqlalchemy
