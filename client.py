import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if not msg:
                break
            print(f"[Server] {msg}")
        except:
            break

def main():
    server_ip = input("输入服务器IP地址：")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, 11555))
    print("[*] Connected to server.")

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        msg = input(">")
        if msg.lower() == 'quit':
            break
        sock.send(msg.encode('utf-8'))

    sock.close()

if __name__ == "__main__":
    main()
