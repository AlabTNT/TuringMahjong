import socket
import threading

clients = []

class Client_:
    def __init__(self, conn: socket.socket, addr, username: str, room_number: str):
        self.conn = conn
        self.addr = addr
        self.username = username
        self.room_number = room_number

    def __str__(self):
        return f"{self.addr}: {self.username}"

    def send_msg(self, msg: str):
        try:
            self.conn.send(msg.encode('utf-8'))
        except Exception as e:
            print(f"[-] 发送消息失败: {e}")
            return False
        return True

    def run(self):
        print(f"[+] {self.addr} connected.")

        try:
            clients.append(self)
            broadcast(f"$Message$📢 {self.username} 加入了房间")

            while True:
                msg = self.conn.recv(1024).decode('utf-8')
                if not msg:
                    break
                print(f"[{self.username}] {msg}")
                broadcast(f"{self.username}: {msg}")
        except:
            pass
        finally:
            print(f"[-] {self.addr} ({self.username}) disconnected.")
            clients.remove(self)
            broadcast(f"$Message$📢 {self.username} 离开了聊天")
            self.conn.close()

def broadcast(message):
    print(f"[广播] {message}")
    for clnt in clients:
        try:
            clnt.send_msg(message)
        except:
            pass

def handle_connection(conn, addr):
    try:
        username_raw = conn.recv(1024).decode('utf-8')
        if not username_raw:
            conn.close()
            return
        elif "$" not in username_raw:
            conn.send("不合法的连接，请确认客户端版本正确。".encode('utf-8'))
            conn.close()
            return
        else:
            username, room_number = username_raw.split("$", 1)
            # 检查用户名是否已存在
            if any(c.username == username for c in clients):
                conn.send("用户名已存在，请重新输入".encode('utf-8'))
                conn.close()
                return

            client = Client_(conn, addr, username, room_number)
            threading.Thread(target=client.run, daemon=True).start()

    except Exception as e:
        print(f"[!] 处理连接时出错: {e}")
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 11555))
    server.listen()
    print("[*] 服务器监听端口 11555...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
