import socket
import threading

bind_ip= "0.0.0.0"
bind_port= 9998
def main(IP,PORT):
    server= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(((IP,PORT)))
    server.listen(5)
    print(f'[*] Nasluchiwanie na {IP}:{PORT}')

    while True:
        client, addres = server.accept()
        print(f'[*] Przyjeto polaczenie od {addres[0]}:{addres[1]}')
        client_hanlder = threading.Thread(target=handle_client,args=(client,))
        client_hanlder.start()
def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Odebrano: {request.decode("utf-8")}')
        sock.send(b'ACKKK')
if __name__=='__main__':
    main(bind_ip,bind_port)
    socket.close()