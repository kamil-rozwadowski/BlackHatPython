import  socket

target_host="127.0.0.1"
target_port = 9997

#tworzenie obiektu gniazda
client =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#wysyanie danych
mess ="AAABBBCCC"
client.sendto(mess.encode(),(target_host,target_port))

#odbieranie danych
data, addr= client.recvfrom(4096)

print(data.decode())
client.close()
