import rpyc

def send_data():
    connection = rpyc.connect('127.0.0.1', 18711)
    print("Connection established")

    #data = {"Ist_temp": 35}
    data =""
    #data = {"TIMES_PUMP_ON": ["7:00:12", "9:00:00", "13:25:00", "19:34:00"], "Ist_Temp": 35}
    result = connection.root.write_config(data)
  
    #result = await connection.root.write_config(data,timeout=10)
    print(result)
    connection.close()
    
send_data()
