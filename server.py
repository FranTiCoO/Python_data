import rpyc

from main import logging
from rpyc.core.protocol import Connection
from rpyc.utils.server import ThreadedServer

@rpyc.service
class Server(rpyc.Service):
    
    @rpyc.exposed
    def write_config(self, data):
        #create a proper dict out of netref
        logging.debug("Yoyoyoyo")
        data = {key: data[key] for key in data}
        
        with open('config.py', 'r') as f:
            lines = f.readlines()
        
        # create a list to store the modified lines
        modified_lines = []
        
        for key in data.keys():

            # read each line
            for line in lines:
                if key in line:
                    #create string out of dict
                    new_text = (f'{key} = {data[key]} \n')
                    modified_lines.append(new_text)  # add the new text to the list
                else:
                    modified_lines.append(line)
            
            lines = modified_lines
            modified_lines = []

        with open('config.py', 'w') as f:
            f.writelines(lines)
            
        print("config.py was modified!")
        return "config.py was modified!"

#async def handle_connection(reader, writer):
#    data = await reader.read()
#    connection = Server(Connection(reader, writer))
#    server = rpyc.utils.server.ThreadedServer(connection, port=0, auto_register=False, protocol_config={'allow_public_attrs': True})
#    server.start()

def start_server():
    server = rpyc.utils.server.ThreadedServer(Server, reuse_addr=True,port=18711, protocol_config={'allow_public_attrs': True})
    logging.debug("start")
    server.start()
    logging.debug("started")
    #server = await asyncio.start_server(handle_connection, '127.0.0.1', 18511)
    #print('Listening on port 18861')
    #async with server:
    #    print(f"Serving on {server.sockets[0].getsockname()}")
    #    await server.serve_forever()


