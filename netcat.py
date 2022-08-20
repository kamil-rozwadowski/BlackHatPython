import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)
    return output.decode()


class NetCat:
    def __init__(self, args, buffer=None):
        self.args =args
        self.buffer = buffer
        self.socket =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        try:
            while True:
                recv_len=1
                response=''
                while recv_len:
                    data =self.socket.recv(4096)
                    recv_len=len(data)
                    response+=data.decode()
                    if recv_len <4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('Operacja przerwana przez uzytkownika')
            self.socket.close()
            sys.exit()

    #Dodanie funckji nasuchiwania polaczenia
    def listen(self):
        print(f'nasluchiwanie na adresie: {self.args.target} i porcie: {self.args.port}')
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ =self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    # Dodanie interakcji z serwerem
    def handle(self,client_socket):
        # Obsluga arguemntu -e do wykonywania komend
        if self.args.execute:
            output= execute(self.args.execute)
            client_socket.send(output.encode())
        # Obsluga arguemntu -u do zaladowywania plikow
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload,'wb') as f:
                f.write(file_buffer)
            message = f'Zapisano plik {self.args.upload}'
            client_socket.send(message.encode())
        # Obsluga arguemntu -c do otwarcia powloki systemowej
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b' #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer +=client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer= b''
                except Exception as e:
                    print(f'serwer zatrzymany {e}')
                    self.socket.close()
                    sys.exit()

#poczatek dzialania programu
if __name__ == '__main__':
    #tworznie interfejsu i manuala
    parser = argparse.ArgumentParser(description='Narzednie SIS', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''Przykady:
        netcat.py -t 192.168.1.108 -p 5555 -l -c #Powloka systemu
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.whatisup #zaladowanie pliku
        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" #wykonanie polecenia

        echo 'ABCDEFGHI'| ./netcat.py -t 192.168.1.108 -p 135 #wysylanie tekstu do serwera na port 135

        netcat.py 192.168.1.108 -p 5555 #polaczenie z serwerem '''))
    #dodanie paramterow do programu
    parser.add_argument('-c', '--command', action='store_true', help='otwarcie powloki')
    parser.add_argument('-e', '--execute', help='wykonywanie polecenia')
    parser.add_argument('-l', '--listen', action='store_true', help='nasluchiwanie polaczenia')
    parser.add_argument('-p', '--port', type=int, default=5555, help='port docelowy')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='adres docelowy (IPV4)')
    parser.add_argument('-u', '--upload', help='zaladowanie pliku')

    #przekazanie parametrow do zmiennej args
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode('utf-8'))
    nc.run()
