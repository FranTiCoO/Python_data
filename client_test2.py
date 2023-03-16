nt.py
from threading import Thread
import rpyc
import logging
import time

class ClientWrapper(Thread):

    def __init__(self):
        Thread.__init__(self)
        logging.info('client - before connect')
        self._connection = rpyc.connect('127.0.0.1',18111)
        logging.info('client - after connect')
        logging.info('client - before retrieving method proxy')
        self._sync_execute = self._connection.root.execute
        logging.info('client - after retrieving method proxy')

    def run(self):
        logging.info('client - before sync exec')
        self._sync_execute(self)
        logging.info('client - after sync exec')

    def stop(self):
        logging.info('client - before Thread.join')
        self.join()
        logging.info('client - after Thread.join')
        self._sync_execute = None
        self._connection.close()

    def exposed_callback(self):
        logging.info('client - callback')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format = '%(asctime)s - p=%(process)d - t=%(thread)d - %(name)s - %(levelname)s - %(message)s')
    wrapper = ClientWrapper()
    wrapper.start()
    logging.info('client - before sleep 5 seconds')
    time.sleep(5)
    logging.info('client - after sleep 5 seconds')
    wrapper.stop()