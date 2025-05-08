using Godot;
using System;
using System.Text;

public partial class NetworkManager : Node
{
    WebSocketPeer ws;

    public override void _Ready()
    {
        ws = new WebSocketPeer();
        var err = ws.ConnectToUrl("ws://127.0.0.1:11556");

        if (err != Error.Ok)
        {
            GD.PrintErr("连接失败: ", err);
        }
        else
        {
            GD.Print("连接成功");
        }
    }

    public override void _Process(double delta)
    {
        if (ws == null)
            return;

        ws.Poll(); // 必须每帧轮询！

        var state = ws.GetReadyState();
        // GD.Print("连接状态：", state);

        if (state == WebSocketPeer.State.Open)
        {
            while (ws.GetAvailablePacketCount() > 0)
            {
                var packet = ws.GetPacket();
                var msg = Encoding.UTF8.GetString(packet);
                GD.Print("收到消息：", msg);
            }

            if (Input.IsActionJustPressed("1"))
            {
                string jsonMsg = "{\"player\":\"张三\",\"action\":\"play_tile\",\"tile\":\"1_wan\"}";
                ws.SendText(jsonMsg);
                GD.Print("已发送：", jsonMsg);
            }
        }
    }
}
