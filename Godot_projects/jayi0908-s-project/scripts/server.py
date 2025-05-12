import asyncio
import websockets
import json

# 存储连接的客户端
clients = []

async def handle_client(websocket):
    try:
        # 接收客户端初始连接时发送的 JSON
        init_data = await websocket.recv()
        init_json = json.loads(init_data)
        username = init_json.get("username")
        room_number = init_json.get("room")
        
        # 简单处理用户名重复的情况
        if any(c.get("username") == username for c in clients):
            await websocket.send(json.dumps({"error": "用户名已存在"}))
            return
        
        client_info = {
            "websocket": websocket,
            "username": username,
            "room_number": room_number
        }
        clients.append(client_info)
        
        # 模拟向客户端发送消息
        # await client_info["websocket"].send(json.dumps({"type": "Message", "msg": f"欢迎 {username} 加入房间 {room_number}！"}))
        # await client_info["websocket"].send(json.dumps({"type": "Join", "name": "哈基筒"}))
        # await client_info["websocket"].send(json.dumps({"type": "Leave", "name": "学姐"}))
        # await client_info["websocket"].send(json.dumps({"type": "Start", "location": {"E": "哈基筒", "W": "学姐", "S": "TNT", "N": "哈基洋"}}))
        hand_list = ["30", "18", "29", "27", "8", "26", "17", "28", "8", "0", "31", "32", "33"]
        await client_info["websocket"].send(json.dumps({"type": "Next", "wind": "E", "num": 1, "honka": 6, "E": "学姐", "S": "哈基筒", "N": "哈基洋", "W": "TNT", "hand": hand_list, "sha256": "1145141919810"}))
        # riichi_list = list({"8"})
        # await client_info["websocket"].send(json.dumps({"type": "Got", "pai": 9, "update": 20, "action": {"riichi": riichi_list, "tsumo": 1, "pei": 1, "rian": 0, "kan": 0}}))
        # await client_info["websocket"].send(json.dumps({"type": "Out", "person": "哈基筒", "pai": 34, "teki": 0, "action": {}}))
        # await client_info["websocket"].send(json.dumps({"type": "Action", "got": 18, "chi": "哈基洋"}))
        
       
        # 持续接收客户端消息并处理
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                if msg_type == "Message":
                    # 简单广播消息给所有客户端（这里未区分房间）
                    broadcast_msg = {
                        "type": "Message",
                        "msg": f"{username}: {data['msg']}"
                    }
                    await broadcast(broadcast_msg)
                else:
                    print(f"收到未知类型消息: {data}")
            except json.JSONDecodeError:
                print("接收到的消息不是有效的 JSON 格式")
    except websockets.ConnectionClosed:
        print(f"[-] {username} 断开连接")
    finally:
        if client_info in clients:
            clients.remove(client_info)

async def broadcast(message):
    for client in clients:
        try:
            await client["websocket"].send(json.dumps(message))
        except websockets.ConnectionClosed:
            continue

async def main():
    async with websockets.serve(handle_client, "", 11555):
        print("[*] WebSocket 服务器监听端口 11555")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())