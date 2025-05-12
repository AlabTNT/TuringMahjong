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
        self.sorting = float(self.cate) if self.code not in [16,52,98] else self.cate-0.5
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
    
    def __lt__(self, value):
        if type(value) == type(self):
            return self.sorting < value.sorting
        return False
    
    def __eq__(self, value):
        if type(value) == type(self) and self.sorting == value.sorting:
            return True
        return False
    
    def __repr__(self):
        return self.name[1]

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
        self.archive = tuple(self.mountain.copy())
        self.s256 = sha256(str([str(i) for i in self.mountain]).encode())
        self.dorasign = [self.mountain[-10]]
        self.ridorasign = [self.mountain[-9]]
        self.dora = [self.dorasign[0].dora]
        self.ridora = [self.ridorasign[0].dora]
        self.lingshang = self.mountain[-14:-10]
        self.handTiles = {i.username: [] for i in players}
        
        #$ 配牌操作
        for _ in range(3):
            for i in self.players:
                for __ in range(4):
                    self.handTiles[i.name].append(self.mountain.pop(0))
        for i in self.players:
            self.handTiles[i.name].append(self.mountain.pop(0))
    
    def mopai(self, player):
        if self.mountain:
            tile = self.mountain.pop(0)
            self.handTiles[player.username].append(tile)
            return tile
        else:
            return None

    def kaigang(self):
        self.dorasign.append(self.mountain[len(self.dorasign) * 2 - 10])
        self.ridorasign.append(self.mountain[len(self.ridorasign) * 2 - 9])
        self.dora.append(self.dorasign[-1].dora)
        self.ridora.append(self.ridorasign[-1].dora)
        return self.lingshang.pop(0)

class MahjongRoom:
    WiNd={"1":"东风","2":"南风","3":"西风","4":"北风"}
    
    def __init__(self, players: list, room_number: str, host):
        self.players = players
        self.host= host
        self.room_number = room_number
        self.games = []
        self.current_game = None
        random.shuffle(self.players)
        self.money = {p.username: 25000 for p in players}
        self.current_wind = 1 #0=东风，1=南风，2=西风，3=北风
        self.current_num = 0 #东X局
        self.current_honka = 0 #X本场
        broadcast({"type":"Start","location":{"E":self.players[0].username,"S":self.players[1].username,"W":self.players[2].username,"N":self.players[3].username}})
        self.newGame()
        
    def newGame(self, keep=False):
        self.current_game = MahjongGame(self.players)
        if keep:
            self.current_honka += 1
        else:
            self.current_num += 1
            self.current_honka = 0
            if self.current_num == 5:
                self.current_num = 1
                self.current_wind = (self.current_wind + 1)
        for i in self.players:
            i.send_msg({"type":"Next", "wind":MahjongRoom.WiNd[str(self.current_wind)],"num":self.current_num,"honka":self.current_honka,"E":self.players[0].username,"S":self.players[1].username,"W":self.players[2].username,"N":self.players[3].username,"hand":self.current_game.handTiles[i.username]})
        
        


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
        except Exception as e:
            print(f"[-] 发送消息失败: {msg}, 错误: {e}")

async def broadcast(msg: dict, room_number=None):
    for c in clients:
        if room_number is None or c.room_number == room_number:
            await c.send_msg(msg)

def handle_message(data: dict, client: Client_): #! 在此实现client-server消息处理
    execute = data.get("type")
    match execute:
        case "Message":
            pass

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
            rooms[room_number] = MahjongRoom([client], room_number, client)
            client.shenfen = "host"
            await client.send_msg({"type": "Message", "msg": f"创建房间 {room_number}"})
        else:
            rooms[room_number].players.append(client)
            if len(rooms[room_number]) > 4:
                client.shenfen = "spectator"
                await client.send_msg({"type": "Message", "msg": f"房间已满，你是观战者"})

        await broadcast({"type": "Join", "name": f"{username}"})
        await broadcast({"type": "Message", "msg": f"📢 {username} 加入了房间"}, room_number)

        async for message in websocket:
            data = json.loads(message)
            handle_message(data, client)
            # if data.get("type") == "Message":
            #     await broadcast({"type": "Message", "msg": f"{username}: {data['msg']}"}, room_number)
            # elif data.get("type") == "Start" and client.shenfen == "host":
            #     await broadcast({"type": "Mahjong", "msg": "start"}, room_number)
            # elif data.get("type") == "Ready":
            #     client.is_ready = True
            #     await broadcast({"type": "Mahjong", "msg": f"ready${username}"}, room_number)
            #     await client.send_msg({"msg": "已准备！", "type": "system"})

    except websockets.ConnectionClosed:
        print(f"[-] {username} 断开连接")
        if client and client.room_number in rooms:
            if client.shenfen == "host":
                await broadcast({"type": "Message", "msg": f"房主 {username} 已断开连接，房间解散"}, client.room_number)
                del rooms[client.room_number]
            else:
                await broadcast({"type": "Leave", "name": f"{username}"}, client.room_number)
                await broadcast({"type": "Message", "msg": f"{username} 离开了房间"}, client.room_number)
    finally:
        if client in clients:
            clients.remove(client)
        if client.room_number in rooms:
            rooms[client.room_number].players.remove(client)
            if not rooms[client.room_number]:
                del rooms[client.room_number]
        await broadcast({"type": "Leave", "name": f"{username}"}, client.room_number)
        await broadcast({"type": "Message", "msg": f"{username} 离开了房间"}, client.room_number)

async def main():
    async with websockets.serve(handle_client, "", 11556):
        print("[*] WebSocket 服务器监听端口 11556")
        await asyncio.Future()

asyncio.run(main())
