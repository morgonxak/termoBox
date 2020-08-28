
import socket

sock = socket.socket()
sock.connect(('127.0.0.1', 5000))
#sock.send('hello, world!')
while 1:
    data = sock.recv(1024)
    if not data:
        continue
    print(data)
    print(type(data))



sock.close()

print (data)