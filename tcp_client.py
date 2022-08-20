import  socket

target_host="0.0.0.0"
target_port = 9998

#tworzenie obiektu gniazda
client =socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#tworznie polaczenia z serwerem
client.connect((target_host,target_port))

#wysyanie danych
mess ="GET / HTTPS/1.1\r\nHost: google.com\r\n\r\n"
client.send(mess.encode())

#odbieranie danych
response= client.recv(4096)

print(response.decode())
client.close()
