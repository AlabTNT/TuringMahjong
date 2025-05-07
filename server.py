import socket
import threading

clients = []

class Client_:
    def __init__(self, conn:socket, addr, username:str):
        self.conn = conn
        self.addr = addr
        self.username = username
        
    def __str__(self):
        return f"{self.addr}: {self.username}"

    def send_msg(self, msg:str):
        try:
            self.conn.send(msg.encode('utf-8'))
        except Exception as e:
            print(f"[-] 发送消息失败: {e}")
            return False
        return True

def handle_client(conn, addr):
    print(f"[+] {addr} connected.")
    try:
        username = conn.recv(1024).decode('utf-8')
        if not username:
            conn.close()
            return
        _tmp=Client_(conn, addr, username)
        clients.append(_tmp)
        broadcast(f"$Message$📢 {username} 加入了房间")

        while True:
            msg = conn.recv(1024).decode('utf-8')
            if not msg:
                break
            print(f"[{username}] {msg}")
            broadcast(f"{username}：{msg}")
    except:
        pass
    finally:
        print(f"[-] {addr} ({clients.get(conn, '未知用户')}) disconnected.")
        broadcast(f"📢 {clients.get(conn, '某用户')} 离开了聊天")
        conn.close()
        if conn in clients:
            del clients[conn]

def broadcast(message):
    print(f"[广播] {message}")
    for clnt in clients:
        clnt:Client_
        try:
            clnt.send_msg(message)
        except:
            pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 11555))
    server.listen()
    print("[*] 服务器监听端口 11555...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
