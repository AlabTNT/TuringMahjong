using Godot;
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;

public partial class Transmitter : Node
{
    WebSocketPeer ws;
    public string username;
    public string room;
    public TileDealer dealer;

    public override void _Ready()
    {
        dealer = GetNode<TileDealer>("/root/Room/TileDealer");
        ws = new WebSocketPeer();
        var err = ws.ConnectToUrl("ws://127.0.0.1:11555");

        if (err != Error.Ok)
        {
            GD.PrintErr("连接失败: ", err);
        }
        else
        {
            GD.Print("连接成功");
            username = "jayi0908"; // 替换为实际用户名
            room = "114514"; // 替换为实际房间号
            SendInitialConnectionInfo();
        }
    }

    public override void _Process(double delta)
    {
        if (ws == null)
            return;

        ws.Poll(); // 必须每帧轮询！

        var state = ws.GetReadyState();

        if (state == WebSocketPeer.State.Open)
        {
            while (ws.GetAvailablePacketCount() > 0)
            {
                var packet = ws.GetPacket();
                var msg = Encoding.UTF8.GetString(packet);
                GD.Print("收到消息：", msg);
                ReceiveServerMessage(msg);
            }

            if (Input.IsActionJustPressed("0"))
            {
                string jsonMsg = "{\"type\":\"Message\",\"msg\":\"你好，服务器！\"}"; // 示例消息
                ws.SendText(jsonMsg);
                GD.Print("已发送：", jsonMsg);
            }
        }
    }

    private void SendInitialConnectionInfo()
    {
        string jsonMsg = $"{{\"username\":\"{username}\",\"room\":\"{room}\"}}";
        ws.SendText(jsonMsg);
        GD.Print("已发送初始连接信息：", jsonMsg);
    }

    public void ReceiveServerMessage(string jsonMessage)
    {
        try
        {
            JsonDocument jsonDoc = JsonDocument.Parse(jsonMessage);
            JsonElement root = jsonDoc.RootElement;
            string type = root.GetProperty("type").ToString();
            switch (type)
            {
                case "Message":
                    string msg = root.GetProperty("msg").ToString();
                    GD.Print($"收到消息：{msg}");
                    // 这里可以添加将消息显示在屏幕上的逻辑，暂不实现
                    break;
                case "Join":
                    string joinName = root.GetProperty("name").ToString();
                    GD.Print($"玩家 {joinName} 加入房间");
                    break;
                case "Leave":
                    string leaveName = root.GetProperty("name").ToString();
                    GD.Print($"玩家 {leaveName} 离开房间");
                    break;
                case "Start":
                    JsonElement locationElement = root.GetProperty("location");
                    string eastUsername = locationElement.GetProperty("E").ToString();
                    string southUsername = locationElement.GetProperty("S").ToString();
                    string westUsername = locationElement.GetProperty("W").ToString();
                    string northUsername = locationElement.GetProperty("N").ToString();
                    GD.Print($"游戏开始，东家：{eastUsername}，南家：{southUsername}，西家：{westUsername}，北家：{northUsername}");
                    break;
                case "Next":
                    string windElement = root.GetProperty("wind").ToString();
                    int num = root.GetProperty("num").GetInt32();
                    int honka = root.GetProperty("honka").GetInt32();
                    string eUsername = root.GetProperty("E").ToString();
                    string sUsername = root.GetProperty("S").ToString();
                    string wUsername = root.GetProperty("W").ToString();
                    string nUsername = root.GetProperty("N").ToString();
                    JsonElement handElement = root.GetProperty("hand");
                    string sha256 = root.GetProperty("sha256").ToString();
                    // 将读入的手牌写入 TileDealer.playerHand
                    foreach(JsonElement cardElement in handElement.EnumerateArray())
                    {
                        try
                        {
                            // 尝试将字符串转换为整数
                            int cardValue;
                            if(int.TryParse(cardElement.GetString(), out cardValue))
                            {
                                string cardName = ConvertCardValueToName(cardValue);
                                dealer.playerHand.Add(cardName);
                            }
                        }
                        catch(Exception ex)
                        {
                            GD.PrintErr($"解析手牌信息出错：{ex.Message}");
                        }
                    }
                    // 这里可以根据 dealer.playerHand 进行后续处理，比如更新界面显示手牌等
                    dealer.shouldInitialDeal = true;
                    GD.Print($"下一局信息：场风 {windElement}，局数 {num}，本场数 {honka}，亲家 {eUsername}，南风 {sUsername}，西风 {wUsername}，北风 {nUsername}，牌山sha256 {sha256}");
                    break;
                case "Got":
                    int pai = root.GetProperty("pai").GetInt32();
                    int update = root.GetProperty("update").GetInt32();
                    JsonElement actionElement = root.GetProperty("action");
                    bool canRiichi = actionElement.TryGetProperty("riichi", out JsonElement riichiElement) 
                        && riichiElement.ValueKind == JsonValueKind.Array 
                        && riichiElement.GetArrayLength() > 0;
                    bool canTsumo = actionElement.TryGetProperty("tsumo", out JsonElement tsumoElement) && tsumoElement.GetInt32() == 1;
                    bool canPei = actionElement.TryGetProperty("pei", out JsonElement peiElement) && peiElement.GetInt32() == 1;
                    bool canRian = actionElement.TryGetProperty("rian", out JsonElement rianElement) && rianElement.GetInt32() == 1;
                    bool canKan = actionElement.TryGetProperty("kan", out JsonElement kanElement) && kanElement.GetInt32() == 1;
                    // dealer.canRiichi = canRiichi;
                    // dealer.canTsumo = canTsumo;
                    // dealer.canPei = canPei;
                    // dealer.canRian = canRian;
                    // dealer.canAnkan = canKan;
                    dealer.playerHand.Add(ConvertCardValueToName(pai));

                    GD.Print($"收到摸牌信息，牌面：{ConvertCardValueToName(pai)}，剩余牌数：{update}，可立直：{canRiichi}，可自摸：{canTsumo}，可拔北：{canPei}，可流局：{canRian}，可开暗杠：{canKan}");
                    break;
                case "Out":
                    string person = root.GetProperty("person").ToString();
                    int outPai = root.GetProperty("pai").GetInt32();
                    int teki = root.GetProperty("teki").GetInt32();
                    JsonElement outActionElement = root.GetProperty("action");

                    GD.Print($"玩家 {person} 出牌，牌面：{ConvertCardValueToName(outPai)}，手切：{teki == 1}");

                    if (outActionElement.ValueKind == JsonValueKind.Object)
                    {
                        bool canChi = outActionElement.TryGetProperty("chi", out JsonElement chiElement_out) 
                            && chiElement_out.ValueKind == JsonValueKind.Array;
                        bool canPon = outActionElement.TryGetProperty("pon", out JsonElement ponElement_out) && ponElement_out.GetInt32() == 1;
                        bool canKanOut = outActionElement.TryGetProperty("kan", out JsonElement kanElement_out) && kanElement_out.GetInt32() == 1;
                        bool canRon = outActionElement.TryGetProperty("ron", out JsonElement ronElement_out) && ronElement_out.GetInt32() == 1;

                        GD.Print($"可执行操作：吃牌 {canChi}，碰牌 {canPon}，杠牌 {canKanOut}，荣和 {canRon}");
                    }
                    break;
                case "Action":
                    if (root.TryGetProperty("got", out JsonElement gotElement))
                    {
                        int gotUpdate = gotElement.GetInt32();
                        GD.Print($"有人摸牌，剩余牌数：{gotUpdate}");
                    }
                    if (root.TryGetProperty("chi", out JsonElement chiElement))
                    {
                        string chiPerson = chiElement.GetProperty("username").ToString();
                        int pist = chiElement.GetProperty("pist").GetInt32();
                        GD.Print($"玩家 {chiPerson} 吃牌，持牌方式：{pist}");
                    }
                    if (root.TryGetProperty("pon", out JsonElement ponElement))
                    {
                        string ponPerson = ponElement.ToString();
                        GD.Print($"有人碰牌，碰牌者：{ponPerson}");
                    }
                    if (root.TryGetProperty("kan", out JsonElement kanElement_action))
                    {
                        string kanUsername = kanElement_action.GetProperty("username").ToString();
                        string dorasign = kanElement_action.GetProperty("dorasign").ToString();
                        GD.Print($"有人明杠，杠牌者：{kanUsername}，新开朵拉指示牌：{dorasign}");
                    }
                    if (root.TryGetProperty("ron", out JsonElement ronElement))
                    {
                        string ronUsername = ronElement.GetProperty("username").ToString();
                        JsonElement handElement_action = ronElement.GetProperty("hand");
                        JsonElement yisElement = ronElement.GetProperty("yis");
                        int fan = ronElement.GetProperty("fan").GetInt32();
                        int fu = ronElement.GetProperty("fu").GetInt32();
                        JsonElement moneyElement_action = ronElement.GetProperty("money");
                        JsonElement payElement_action = ronElement.GetProperty("pay");

                        GD.Print($"有人荣和，荣和者：{ronUsername}，荣和役种 {yisElement}，翻数 {fan}，符数 {fu}，获得点棒 {moneyElement_action}，点棒流水 {payElement_action}");
                    }
                    if (root.TryGetProperty("tsumo", out JsonElement tsumoElement_action))
                    {
                        string tsumoUsername = tsumoElement_action.GetProperty("username").ToString();
                        JsonElement handElement_action = tsumoElement_action.GetProperty("hand");
                        JsonElement yisElement = tsumoElement_action.GetProperty("yis");
                        int fan = tsumoElement_action.GetProperty("fan").GetInt32();
                        int fu = tsumoElement_action.GetProperty("fu").GetInt32();
                        JsonElement moneyElement_action = tsumoElement_action.GetProperty("money");
                        JsonElement payElement_action = tsumoElement_action.GetProperty("pay");

                        GD.Print($"有人自摸，自摸者：{tsumoUsername}，自摸手牌 {handElement_action}，荣和役种 {yisElement}，翻数 {fan}，符数 {fu}，获得点棒 {moneyElement_action}，点棒流水 {payElement_action}");
                    }
                    if (root.TryGetProperty("ankan", out JsonElement ankanElement))
                    {
                        string ankanUsername = ankanElement.GetProperty("username").ToString();
                        int value = ankanElement.GetProperty("value").GetInt32();
                        string dorasign = ankanElement.GetProperty("dorasign").ToString();

                        GD.Print($"有人暗杠，暗杠者：{ankanUsername}，暗杠牌值 {value}，新开朵拉指示牌 {dorasign}");
                    }
                    if (root.TryGetProperty("pukan", out JsonElement pukanElement))
                    {
                        string pukanUsername = pukanElement.GetProperty("username").ToString();
                        int value = pukanElement.GetProperty("value").GetInt32();
                        string dorasign = pukanElement.GetProperty("dorasign").ToString();

                        GD.Print($"有人补杠，补杠者：{pukanUsername}，补杠牌值 {value}，新开朵拉指示牌 {dorasign}");
                    }
                    if (root.TryGetProperty("pei", out JsonElement peiElement_action))
                    {
                        string peiUsername = peiElement_action.ToString();
                        GD.Print($"有人拔北，拔北者：{peiUsername}");
                    }
                    break;
                case "Riu":
                    JsonElement tenpaiElement = root.GetProperty("tenpai");
                    string tenpaiUsername = tenpaiElement.GetProperty("username").ToString();
                    JsonElement handTenpaiElement = tenpaiElement.GetProperty("hand");
                    JsonElement tenpaiContentElement = tenpaiElement.GetProperty("tenpai");
                    JsonElement payElement = root.GetProperty("pay");

                    GD.Print($"流局，听牌家 {tenpaiUsername}，手牌 {handTenpaiElement}，听牌内容 {tenpaiContentElement}，点棒流水 {payElement}");
                    break;
                case "End":
                    JsonElement rankElement = root.GetProperty("rank");
                    JsonElement moneyElement = root.GetProperty("money");
                    JsonElement scoreElement = root.GetProperty("score");

                    GD.Print($"终局，顺位信息 {rankElement}，终了时点棒数 {moneyElement}，分数变动 {scoreElement}");
                    break;
                default:
                    GD.Print($"未知的消息类型：{type}");
                    break;
            }
        }
        catch (Exception ex)
        {
            GD.PrintErr($"解析服务器消息出错：{ex.Message}");
        }
    }

    private string ConvertCardValueToName(int cardValue)
    {
        switch (cardValue)
        {
            case 0: return "1m";
            case 1: return "2m";
            case 2: return "3m";
            case 3: return "4m";
            case 4: return "5m";
            case 5: return "6m";
            case 6: return "7m";
            case 7: return "8m";
            case 8: return "9m";
            case 9: return "1p";
            case 10: return "2p";
            case 11: return "3p";
            case 12: return "4p";
            case 13: return "5p";
            case 14: return "6p";
            case 15: return "7p";
            case 16: return "8p";
            case 17: return "9p";
            case 18: return "1s";
            case 19: return "2s";
            case 20: return "3s";
            case 21: return "4s";
            case 22: return "5s";
            case 23: return "6s";
            case 24: return "7s";
            case 25: return "8s";
            case 26: return "9s";
            case 27: return "1z";
            case 28: return "2z";
            case 29: return "3z";
            case 30: return "4z";
            case 31: return "5z";
            case 32: return "6z";
            case 33: return "7z";
            case 34: return "0m";
            case 35: return "0p";
            case 36: return "0s";
            default: return null;
        }
    }
}