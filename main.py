import flet as ft
import socket
import threading
from utils.from_import import *


SERVER_IP = "127.0.0.1"
SERVER_PORT = 11555

def handle_rdata(page:ft.Page,rdata:str):
    data=rdata.split("$")
    if data[1]=="Message":
        page.add(ft.Text(data[2],size=20,color=ft.colors.GREEN))
    elif data[1]=="Mahjong":
        pass
    page.update()

def main(page: ft.Page):
    page.title = "TuringMahjong"

    username = ft.TextField(label="请输入用户名")
    server_ip = ft.TextField(label="请输入服务器IP", value=SERVER_IP)
    server_port = ft.TextField(label="请输入服务器端口", value=str(SERVER_PORT))
    room_number = ft.TextField(label="请输入房间号")
    confirm_button = ft.ElevatedButton(text="确认", width=100)

    def enter_chat(e):
        name = username.value.strip()
        if not name:
            username.error_text = "用户名不能为空"
            page.update()
            return
        if any(i for i in name if i in ["$", "#", "@","\"","\'","\\","/","\n","\t"]):
            username.error_text = "用户名不能包含特殊字符"
            page.update()
            return
        if len(name)>10:
            username.error_text = "用户名不能超过10个字符"
            page.update()
            return
        if len(name)<2:
            username.error_text = "用户名不能少于2个字符"
            page.update()
            return
        if name[0] == "_":
            username.error_text = "用户名不能以_开头"
            page.update()
            return
        if not room_number.value:
            room_number.error_text = "房间号不能为空"
            page.update()
            return
        if not server_ip.value:
            server_ip.error_text = "服务器IP不能为空"
            page.update()
            return
        if not server_port.value:
            server_port.error_text = "服务器端口不能为空"
            page.update()
            return
        if not room_number.value.isdigit():
            room_number.error_text = "房间号必须是数字"
            page.update()
            return
        if len(room_number.value) !=4:
            room_number.error_text = "房间号必须是4位数字"
            page.update()
            return
        if not server_port.value.isdigit():
            server_port.error_text = "端口号必须是数字"
            page.update()
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip.value, int(server_port.value)))
        sock.send(f"${name}${room_number.value}".encode('utf-8'))  # 发送用户名和房间号
        
        if sock.recv(1024).decode('utf-8') == "用户名已存在，请重新输入":
            username.error_text = "用户名已存在，请重新输入"
            page.update()
            return


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
