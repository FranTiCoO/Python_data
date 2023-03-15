import rpyc
from rpyc.utils.server import ThreadedServer
import time

@rpyc.service
class Server(rpyc.Service):
    
    @rpyc.exposed
    def write_config(self, data):
        #create a proper dict out of netref
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


print('Listening on port 18711')
server = ThreadedServer(Server, port=18711, protocol_config={'allow_public_attrs': True})
server.start()