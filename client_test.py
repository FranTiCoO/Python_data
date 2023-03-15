import rpyc

connection = rpyc.connect('localhost', 18711)

data = {"TIMES_PUMP_ON": ["7:00:12", "9:00:00", "13:25:00", "19:34:00"], "Ist_Temp": 35}

print(connection.root.write_config(data))
