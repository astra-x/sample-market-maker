项目说明

```
 HUDEX-BRUSH-MM 该服务是提供刷成交量的服务机器人，

```

快速开始

```python
 # 注意点
 1.需要确保runserver.py文件中登陆账户是有费用的
 # 启动
  简单启动：python runserver.py
  pm2启动：pm2 start runserver.py --name HUDEX-BRUSH-MM-SDC/USDT --interpreter python3 
```



配置说明

```
{
    "ClientContract": "SDC/USDT",# 交易对
    "Client_HTTP_URL": "http://47.75.14.147:3000", # 客户端地址
    "CycleTime": 1, # 表示1秒执行多少次
    "HighFrequency": 10, # 频率上限
    "LowFrequency": 2, # 频率下限
    "MaxSetPrice": 1, # 价格上限
    "MinSetPrice": 0, # 价格下限
    "OrderMaxQuantity": 0.02, # 订单最大数量
    "OrderMinQuantity": 0.01, # 订单最小数量
    "StartTime": "2020-08-26 10:58:48", # 开始时间
    "EndTime": "2020-08-26 13:58:48", # 结束时间
    "TIMEOUT": 7 # 超时时间
}
```

接口说明

```python

# 重置配置文件接口
url: /reset_config
method: POST 
body:
    {
        "ClientContract": "SDC/USDT",
        "Client_HTTP_URL": "http://47.75.14.147:3000",
        "CycleTime": 1,
        "EndTime": "2020-08-26 13:58:48",
        "HighFrequency": 10,
        "LowFrequency": 2,
        "MaxSetPrice": 1,
        "MinSetPrice": 0,
        "OrderMaxQuantity": 0.02,
        "OrderMinQuantity": 0.01,
        "StartTime": "2020-08-26 10:58:48",
        "TIMEOUT": 7
    }

# 获取配置文件接口
url: /get_config
method: GET
  
# 开启服务接口
url: /start
method: POST

# 暂停服务接口
url: /stop
method: POST
 

```

