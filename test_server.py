import time
import threading
from socketIO_client import SocketIO


def start_runner():
    def start_loop():
        not_started = True
        n_tries = 0
        max_tries = 5

        while not_started:
            print('In start loop')
            try:
                n_tries += 1
                if n_tries > max_tries:
                    break

                connect_and_test()
                not_started = False
            except:
                print('Server not yet started')
            time.sleep(1.5)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


def connect_and_test():
    socketIO = SocketIO('localhost', 420)
    socketIO.wait(1)
    socketIO.emit('new-mapping', {'sick': ', man'})
    socketIO.disconnect()


if __name__ == '__main__':
    connect_and_test()
