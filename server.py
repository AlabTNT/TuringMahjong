import socket
import threading

clients = []
rooms={}
from json import load
from hashlib import sha256
from datetime import datetime
import random


with open("./data/name.json",'r',encoding='utf-8') as f:
    mname=load(f)

class Mahjong:
    def __init__(self, code:int):
        self.code=code
        self.cate=self.code//4
        self.name:list=mname[str(self.cate)]
        if self.code in [16,52,98] :
            self.name:list=mname[str(self.code//36 +34)]
            self.dora:list=mname[str((self.code//36)*9+5)]
        elif self.cate not in [8,17,26,30,33]:
            self.dora:list=mname[str(self.cate+1)]
        elif self.cate in [8,17,26]:
            self.dora:list=mname[str(self.cate-8)]
        else:
            self.dora:list=mname["27" if self.cate==30 else "31"]
    
    def __str__(self):
        return self.name[0]

class MahjongGame:
    @staticmethod
    def generate_mountain(gsd:int)->list:
        """
        生成山牌
        """
        x=0
        for i in random.randint(0,100):
           x+=hash(random.randint(0,100)) 
        seed=sha256((str(x)+str(gsd)+datetime.now().strftime("%Y-%m-%d %H:%M:%S")).encode()).hexdigest()
        random.seed(seed)
            
        mountain=[Mahjong(i) for i in range(136)]
        random.shuffle(mountain)
        
        start=((random.randint(1,6)+random.randint(1,6))%4)*34+((random.randint(1,6)+random.randint(1,6))%4)*2
        
        mountain=mountain[start:]+mountain[:start]
        return mountain

    
    def __init__(self, players:list):
        self.players=players
        self.mountain=MahjongGame.generate_mountain(hash(self.players))
        self.s256=sha256(str([str(i) for i in self.mountain]))
        self.dorasign=[self.mountain[-10]]
        self.ridorasign=[self.mountain[-9]]
        self.dora=[self.dorasign[0].dora]
        self.ridora=[self.ridorasign[0].dora]
        self.lingshang=[self.mountain[-11],self.mountain[-12],self.mountain[-13],self.mountain[-14]] 
    
    def kaigang(self):
        self.dorasign.append(self.mountain[len(self.dorasign)*2-10])
        self.ridorasign.append(self.mountain[len(self.ridorasign)*2-9])
        self.dora.append(self.dorasign[-1].dora)
        self.ridora.append(self.ridorasign[-1].dora)
        return self.lingshang.pop()
           

class Client_:
    def __init__(self, conn: socket.socket, addr, username: str, room_number: str, shenfen:str="player"):
        self.conn = conn
        self.addr = addr
        self.username = username
        self.room_number = room_number
        self.shenfen=shenfen
        self.is_ready=False

    def __str__(self):
        return f"{self.addr}: {self.username}"

    def send_msg(self, msg: str):
        try:
            self.conn.send(msg.encode('utf-8'))
        except Exception as e:
            print(f"[-] 发送消息失败: {e}")
            return False
        return True

    def handle_msg(self, rmsg: str):
        if "$" not in rmsg:
            return
        else:
            msg= rmsg.split("$")
        if msg[1] == "Message":
            broadcast(f"$Message${self.username}: {msg[2]}")
        elif msg[1] == "Start":
            if self.shenfen=="host":
                broadcast("$Mahjong$start")
                
            else:
                self.is_ready=True
                self.send_msg(f"$Message$已准备！")
                broadcast(f"$Mahjong$ready${self.username}")
        

    def run(self):
        print(f"[+] {self.addr} connected.")

        try:
            clients.append(self)
            broadcast(f"$Message$📢 {self.username} 加入了房间")
            broadcast(f"$Join${self.username}")

            while True:
                msg = self.conn.recv(1024).decode('utf-8')
                if not msg:
                    break
                print(f"[{self.username}] {msg}")
                self.handle_msg(msg)
        except:
            pass
        finally:
            print(f"[-] {self.addr} ({self.username}) disconnected.")
            clients.remove(self)
            broadcast(f"$Message$📢 {self.username} 离开了房间")
            broadcast(f"$Leave${self.username}")
            self.conn.close()
            if self.room_number in rooms.keys():
                rooms[self.room_number].remove(self)
                if len(rooms[self.room_number]) == 0:
                    del rooms[self.room_number]
                    print(f"[-] 房间 {self.room_number} 已关闭")

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
            room_number = username_raw.split("$")[2]
            username = username_raw.split("$")[1]
            # 检查用户名是否已存在
            if any(c.username == username for c in clients):
                conn.send("用户名已存在，请重新输入".encode('utf-8'))
                conn.close()
                return

            client = Client_(conn, addr, username, room_number)
            threading.Thread(target=client.run, daemon=True).start()
            print(f"[+] {addr} ({username}) 连接成功")
            client.send_msg(f"$Message$已成功以 {username} 连接到房间 {room_number}")
            if room_number not in rooms.keys():
                rooms[room_number] = [client]
                client.send_msg(f"$Message$由于房间无人，已成功创建房间 {room_number}")
                client.shenfen="host"
            else:
                rooms[room_number].append(client)
                if len(rooms[room_number])>4:
                    client.send_msg(f"$Message$房间 {room_number} 已满，已更改你的身份为旁观者")
                    client.shenfen="spectator"

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
