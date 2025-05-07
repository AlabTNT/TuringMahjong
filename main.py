import flet as ft
import socket
import threading
from utils.from_import import *


SERVER_IP = "127.0.0.1"
SERVER_PORT = 11555

def handle_rdata(page:ft.Page,rdata:str):
    data=rdata.split("$")
    if data[0]=="Message":
        page.add(ft.Text(data[1],size=20,color=ft.colors.GREEN))
    elif data[1]=="Mahjong":
        pass
    page.update()

def main(page: ft.Page):
    page.title = "Flet 聊天客户端"

    username = ft.TextField(label="请输入用户名")
    confirm_button = ft.ElevatedButton(text="确认", width=100)

    def enter_chat(e):
        name = username.value.strip()
        if not name:
            username.error_text = "用户名不能为空"
            page.update()
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.send(name.encode('utf-8'))  # 第一个消息作为用户名发送

        chat = ft.TextField(multiline=True, read_only=True, expand=True)
        input_box = ft.TextField(label="输入消息")
        button_image = ft.Image(src="/mahjong/op_lizhi.png", width=110, height=54, fit=ft.ImageFit.CONTAIN)
        send_button = ft.Container(width=110, height=54, content=button_image)

        def send_message(e):
            msg = input_box.value.strip()
            if msg:
                try:
                    sock.send(msg.encode('utf-8'))
                    input_box.value = ""
                    page.update()
                except Exception as ex:
                    chat.value += f"\n[发送失败] {ex}"
                    page.update()

        send_button.on_click = send_message

        def receive_messages():
            while True:
                try:
                    data = sock.recv(1024).decode('utf-8')
                    if not data:
                        break
                    handle_rdata(page,data)
                    chat.value += f"\n{data.split("$")[1]}"
                    page.update()
                except:
                    break

        threading.Thread(target=receive_messages, daemon=True).start()

        page.clean()
        page.add(chat, input_box, send_button)

    confirm_button.on_click = enter_chat
    page.add(username, confirm_button)

ft.app(target=main, view=ft.WEB_BROWSER)
