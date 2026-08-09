import rpyc

try:
    connection = rpyc.connect('localhost', 18911)
except:
    print("Server not running or wrong credentials")

data = {"TIMES_PUMP_ON": ["7:00:10", "9:00:00", "13:25:00", "19:34:00"]}

try:
    print(connection.root.write_config(data))
except:
    print("connection failed")