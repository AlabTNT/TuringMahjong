using Godot;
using System;
using System.Net.Sockets;
using System.Text;

public partial class NetCheck : Node3D
{
    public override void _Ready()
    {
        GD.Print("Connecting to Python server...");

        TcpClient client = new TcpClient();
        client.Connect("127.0.0.1", 65432);  // IP和端口
        NetworkStream stream = client.GetStream();

        string message = "Hello from Godot!";
        byte[] data = Encoding.UTF8.GetBytes(message);
        stream.Write(data, 0, data.Length);  // 发送数据

        byte[] buffer = new byte[1024];
        int bytesRead = stream.Read(buffer, 0, buffer.Length);  // 接收响应
        string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);

        GD.Print("Python response: ", response);

        stream.Close();
        client.Close();
    }
}
