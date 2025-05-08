import asyncio
import websockets
import json

connected = set()

async def handler(websocket):
    print("新客户端连接")
    connected.add(websocket)
    try:
        await websocket.send(json.dumps({"msg": "欢迎来到麻将服务器！"}))

        async for message in websocket:
            print("收到：", message)
            data = json.loads(message)
            # 你可以在这里处理出牌逻辑
            response = {"echo": data}
            await websocket.send(json.dumps(response))
    except websockets.ConnectionClosed:
        print("客户端断开连接")
    finally:
        connected.remove(websocket)

async def main():
    async with websockets.serve(handler, "127.0.0.1", 11556):
        print("WebSocket 服务器已启动，监听端口 11556")
        await asyncio.Future()  # 永远运行

asyncio.run(main())