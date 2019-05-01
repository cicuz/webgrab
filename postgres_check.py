import os
import socket
import time


def postgresql_check():
    port = int(os.environ["DATABASE_PORT"])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect(("db", port))
            s.close()
            return 0
        except socket.error:
            time.sleep(0.1)


if __name__ == "__main__":
    postgresql_check()
