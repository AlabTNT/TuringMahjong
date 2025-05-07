import asyncio
import websockets
import json
from json import load
from hashlib import sha256
from datetime import datetime
import random

clients = []
rooms = {}

with open("./data/name.json", 'r', encoding='utf-8') as f:
    mname = load(f)

class Mahjong:
    def __init__(self, code: int):
        self.code = code
        self.cate = self.code // 4
        self.name: list = mname[str(self.cate)]
        if self.code in [16, 52, 98]:
            self.name = mname[str(self.code // 36 + 34)]
            self.dora = mname[str((self.code // 36) * 9 + 5)]
        elif self.cate not in [8, 17, 26, 30, 33]:
            self.dora = mname[str(self.cate + 1)]
        elif self.cate in [8, 17, 26]:
            self.dora = mname[str(self.cate - 8)]
        else:
            self.dora = mname["27" if self.cate == 30 else "31"]

    def __str__(self):
        return self.name[0]

class MahjongGame:
    @staticmethod
    def generate_mountain(gsd: int) -> list:
        x = sum(hash(random.randint(0, 100)) for _ in range(random.randint(0, 100)))
        seed = sha256((str(x) + str(gsd) + datetime.now().strftime("%Y-%m-%d %H:%M:%S")).encode()).hexdigest()
        random.seed(seed)
        mountain = [Mahjong(i) for i in range(136)]
        random.shuffle(mountain)
        start = ((random.randint(1, 6) + random.randint(1, 6)) % 4) * 34 + ((random.randint(1, 6) + random.randint(1, 6)) % 4) * 2
        return mountain[start:] + mountain[:start]

    def __init__(self, players: list):
        self.players = players
        self.mountain = MahjongGame.generate_mountain(hash(str(self.players)))
        self.s256 = sha256(str([str(i) for i in self.mountain]).encode())
        self.dorasign = [self.mountain[-10]]
        self.ridorasign = [self.mountain[-9]]
        self.dora = [self.dorasign[0].dora]
        self.ridora = [self.ridorasign[0].dora]
        self.lingshang = self.mountain[-14:-10]

    def kaigang(self):
        self.dorasign.append(self.mountain[len(self.dorasign) * 2 - 10])
        self.ridorasign.append(self.mountain[len(self.ridorasign) * 2 - 9])
        self.dora.append(self.dorasign[-1].dora)
        self.ridora.append(self.ridorasign[-1].dora)
        return self.lingshang.pop()

class Client_:
    def __init__(self, websocket, username: str, room_number: str):
        self.websocket = websocket
        self.username = username
        self.room_number = room_number
        self.shenfen = "player"
        self.is_ready = False

    async def send_msg(self, msg: dict):
        try:
            await self.websocket.send(json.dumps(msg))
        except:
            print(f"[-] 发送消息失败: {msg}")

async def broadcast(msg: dict, room_number=None):
    for c in clients:
        if room_number is None or c.room_number == room_number:
            await c.send_msg(msg)

async def handle_client(websocket):
    try:
        raw = await websocket.recv()
        init = json.loads(raw)
        username = init.get("username")
        room_number = init.get("room")

        if any(c.username == username for c in clients):
            await websocket.send(json.dumps({"error": "用户名已存在"}))
            return

        client = Client_(websocket, username, room_number)
        clients.append(client)

        if room_number not in rooms:
            rooms[room_number] = [client]
            client.shenfen = "host"
            await client.send_msg({"msg": f"创建房间 {room_number}", "type": "system"})
        else:
            rooms[room_number].append(client)
            if len(rooms[room_number]) > 4:
                client.shenfen = "spectator"
                await client.send_msg({"msg": f"房间已满，你是观战者", "type": "system"})

        await broadcast({"msg": f"📢 {username} 加入了房间", "type": "system"}, room_number)

        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "Message":
                await broadcast({"type": "Message", "msg": f"{username}: {data['msg']}"}, room_number)
            elif data.get("type") == "Start" and client.shenfen == "host":
                await broadcast({"type": "Mahjong", "msg": "start"}, room_number)
            elif data.get("type") == "Ready":
                client.is_ready = True
                await broadcast({"type": "Mahjong", "msg": f"ready${username}"}, room_number)
                await client.send_msg({"msg": "已准备！", "type": "system"})

    except websockets.ConnectionClosed:
        print(f"[-] {username} 断开连接")
    finally:
        if client in clients:
            clients.remove(client)
        if client.room_number in rooms:
            rooms[client.room_number].remove(client)
            if not rooms[client.room_number]:
                del rooms[client.room_number]
        await broadcast({"type": "system", "msg": f"{username} 离开了房间"}, client.room_number)

async def main():
    async with websockets.serve(handle_client, "", 11556):
        print("[*] WebSocket 服务器监听端口 11556")
        await asyncio.Future()

asyncio.run(main())
