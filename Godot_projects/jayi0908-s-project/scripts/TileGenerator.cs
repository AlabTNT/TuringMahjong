using Godot;
using System;
using System.Collections.Generic;
using System.Linq;

public partial class TileGenerator : Node
{
    private string[] tileDeck = {
        "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "0p",
        "1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "0s",
        "1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "0m",
        "1z", "2z", "3z", "4z", "5z", "6z", "7z"
    };
    private List<string> fullDeck;
    private List<string>[] playerHands; // 所有玩家手牌，二维数组
    private string[] winds = { "east", "south", "west", "north" }; // 东南西北
    private int currentPlayerIndex; // 当前被发到牌的玩家对应的自风，0 - 3 分别代表东南西北
    private string selfWind; // 自风
    private int dealtCardCount; // 已发牌数量
    private Timer dealTimer; // 发牌计时器
    private SubViewport subViewport; // 混合视窗节点
    private int currentHandIndex; // 当前玩家手牌数

    public override void _Ready()
    {
        InitializeDeck();
        playerHands = new List<string>[4];
        for (int i = 0; i < 4; i++) playerHands[i] = new List<string>();
        currentPlayerIndex = 0;
        dealtCardCount = 0;
        currentHandIndex = 0;

        // 创建并配置 Timer
        dealTimer = new Timer();
        dealTimer.WaitTime = 0.05; // 每 0.05 秒发一张牌
        dealTimer.Timeout += DealSingleCard; // 每次计时结束时调用 DealSingleCard 函数，发一张单牌
        AddChild(dealTimer);
        dealTimer.Start();

        // 获取 SubViewport 节点
        subViewport = GetNode<SubViewport>("/root/Room/SubViewportContainer/SubViewport");

        // 随机分配当前玩家的风
        Random random = new Random();
        int windIndex = random.Next(4);
        selfWind = winds[windIndex];
    }

    private void InitializeDeck() // 初始化牌堆
    {
        fullDeck = new List<string>(tileDeck); // 将静态字符串组赋值给动态List fullDeck
        fullDeck.AddRange(tileDeck);

        // 使用 LINQ 进行洗牌
        Random random = new Random();
        fullDeck = fullDeck.OrderBy(x => random.Next()).ToList();

        // fullDeck.RemoveRange(fullDeck.Count - 14, 14);
    }

    private void DealSingleCard()
    {
        if(dealtCardCount < 13 * 4 + 1)
        {
            playerHands[currentPlayerIndex].Add(fullDeck[0]);
            fullDeck.RemoveAt(0);

            // 如果发牌到自家，在手牌中显示这张牌
            if(currentPlayerIndex == Array.IndexOf(winds, selfWind))
            {
                AddCardToHandDisplay(playerHands[currentPlayerIndex][currentHandIndex]);
                currentHandIndex++;
            }

            currentPlayerIndex = (currentPlayerIndex + 1) % 4; // mod 4 递增
            dealtCardCount++;

            if(dealtCardCount == 13 * 4 + 1)
            {
                dealTimer.Stop();
                // 发牌结束后对当前玩家手牌排序
                playerHands[Array.IndexOf(winds, selfWind)] = SortHand(playerHands[Array.IndexOf(winds, selfWind)]);
                // 重新显示排序后的手牌
                ReDisplayHand(playerHands[Array.IndexOf(winds, selfWind)]);
            }
        }
    }

    private void AddCardToHandDisplay(string tile)
    {
        float cardWidth = 80 * 0.75f; // 牌宽，由于资源为80*129，经调整后缩放0.75倍
        float y = subViewport.Size.Y - 10 - 129 * 0.75f;

        // 计算所有手牌的总宽度
        float totalWidth = cardWidth * 14;
        // 计算起始 X 坐标，使手牌居中显示
        float startX = (subViewport.Size.X - totalWidth) / 2;

        TextureRect textureRect = new TextureRect(); // “实例化”手牌
        textureRect.Texture = ResourceLoader.Load<Texture2D>($"res://assets/tiles/{tile}.png"); // 从仓库中读取同名的牌的纹理
        textureRect.Scale = new Vector2(0.75f, 0.75f);
        textureRect.Position = new Vector2(startX + (currentHandIndex - 1) * cardWidth, y);
        subViewport.AddChild(textureRect);
    }

    private List<string> SortHand(List<string> hand)
    {
        return hand.OrderBy(x =>
        { // 为每张牌生成一个的排序值，规则为：花色 * 1000 + 点数 * 10
        // 对于赤宝牌，排序值为花色 * 1000 + 45，这样可以使其排在普通4点牌和5点牌之间
            char suit = x[1];
            int rank = int.Parse(x[0].ToString());
            if(rank == 0) return suit * 1000 + 45;
            return suit * 1000 + rank * 10;
        }).ToList();
    }

    private void ReDisplayHand(List<string> hand)
    {
        // 创建一个Timer用于延迟显示实际手牌
        Timer delayTimer = new Timer();
        delayTimer.WaitTime = 0.25f;
        delayTimer.Timeout += () => {
            // 移除牌背
            foreach (var child in subViewport.GetChildren())
            {
                if (child is TextureRect)
                {
                    subViewport.RemoveChild(child);
                    child.QueueFree();
                }
            }

            float cardWidth = 80 * 0.75f; // 牌宽，由于资源为80*129，经调整后缩放0.75倍
            float y = subViewport.Size.Y - 10 - 129 * 0.75f;

            // 计算所有手牌的总宽度
            float totalWidth = cardWidth * 14;
            // 计算起始X坐标，使手牌居中显示
            float startX = (subViewport.Size.X - totalWidth) / 2;

            for (int i = 0; i < hand.Count; i++)
            {
                string tile = hand[i];
                TextureRect textureRect = new TextureRect(); // “实例化”手牌
                textureRect.Texture = ResourceLoader.Load<Texture2D>($"res://assets/tiles/{tile}.png"); // 从仓库中读取同名的牌的纹理
                textureRect.Scale = new Vector2(0.75f, 0.75f);
                textureRect.Position = new Vector2(startX + (i - 1) * cardWidth, y);
                subViewport.AddChild(textureRect);
            }
        };
        AddChild(delayTimer);

        // 移除之前显示的手牌并替换为牌背
        foreach (var child in subViewport.GetChildren())
        {
            if (child is TextureRect)
            {
                subViewport.RemoveChild(child);
                child.QueueFree();
            }
        }

        float cardWidth = 80 * 0.75f; // 牌宽，由于资源为80*129，经调整后缩放0.75倍
        float y = subViewport.Size.Y - 10 - 129 * 0.75f;

        // 计算所有手牌的总宽度
        float totalWidth = cardWidth * 14;
        // 计算起始X坐标，使手牌居中显示
        float startX = (subViewport.Size.X - totalWidth) / 2;

        for (int i = 0; i < hand.Count; i++)
        {
            TextureRect textureRect = new TextureRect(); // “实例化”手牌
            textureRect.Texture = ResourceLoader.Load<Texture2D>("res://assets/tiles/back.png"); // 从仓库中读取牌背的纹理
            textureRect.Scale = new Vector2(0.75f, 0.75f);
            textureRect.Position = new Vector2(startX + (i - 1) * cardWidth, y);
            subViewport.AddChild(textureRect);
        }

        delayTimer.Start();
    }
}