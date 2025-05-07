import socket
import threading

clients = []

class Client_:
    def __init__(self, conn:socket, addr, username:str, room_number:str):
        self.conn = conn
        self.addr = addr
        self.username = username
        self.room_number = room_number
        
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
        elif username in clients:
            conn.send("用户名已存在，请重新输入".encode('utf-8'))
            conn.close()
            return
        elif "$" not in username:
            conn.send("不合法的连接，请确认客户端版本正确。".encode('utf-8'))
            conn.close()
            return
        else:
            room_number=username.split("$")[1]
            username=username.split("$")[0]
            
        _tmp=Client_(conn, addr, username, room_number)
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
