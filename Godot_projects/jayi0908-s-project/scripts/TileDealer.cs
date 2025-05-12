using Godot;
using System;
using System.Collections.Generic;
using System.Linq;

public partial class TileDealer : Node
{
	public List<string> playerHand; // 玩家手牌
	public bool shouldInitialDeal{ get; set; } = true; // 是否应该发初始牌
    private int currentDealIndex = 0; // 当前发牌索引
    private int hasInitialDealedCnt = 0; // 已经发过初始牌数
	private Timer dealTimer; // 发牌计时器
    private SubViewport subViewport; // 混合视窗节点
    // public bool canChi{ get; set; } = false; // 是否可以吃
    // public bool canPon{ get; set; } = false; // 是否可以碰
    // public bool canKan{ get; set; } = false; // 是否可以明杠
    // public bool canRon{ get; set; } = false; // 是否可以荣和
    // public bool canRiichi{ get; set; } = false; // 是否可以立直
    // public bool canTsumo{ get; set; } = false; // 是否可以自摸
    // public bool canPei{ get; set; } = false; // 是否可以拔北
    // public bool canRian{ get; set; } = false; // 是否可以流局
    // public bool canAnkan{ get; set; } = false; // 是否可以暗杠
    
	public override void _Ready()
	{
		playerHand = new List<string>();
		subViewport = GetNode<SubViewport>("/root/Room/SubViewportContainer/SubViewport");
        // playerHand.AddRange(new string[]{"9m", "9m", "1m", "9p", "9s", "1s", "6z", "5z", "3z", "4z", "2z", "1z", "7z"});
	}

	public override void _Process(double delta)
    {
        // 只在需要发牌且没有活动定时器时创建新定时器
        if(shouldInitialDeal && currentDealIndex < playerHand.Count && (dealTimer == null || !IsInstanceValid(dealTimer)))
        {
            dealTimer = new Timer();
            dealTimer.WaitTime = 0.25f;
            
            // 使用局部变量捕获当前索引值
            int indexToDeal = currentDealIndex;
            
            dealTimer.Timeout += () => {
                if(indexToDeal < playerHand.Count) // 再次检查索引有效性
                {
                    DisplayHand(playerHand[indexToDeal], indexToDeal, indexToDeal == 13, false);
                    currentDealIndex++;
                    // 如果是最后一张牌，开始排序
                    if(currentDealIndex >= playerHand.Count)
                    {
                        SortHand(playerHand);
                        shouldInitialDeal = false;
                        currentDealIndex = 0;
                    }
                }               
                // 释放当前定时器
                if(dealTimer != null && IsInstanceValid(dealTimer))
                {
                    dealTimer.QueueFree();
                    dealTimer = null;
                }
            };
            
            AddChild(dealTimer);
            dealTimer.Start();
        }
    }

	private void DisplayHand(string tile, int index, bool isTeki, bool isBack) // 刚开始发牌时显示手牌, index为当前玩家的手牌数, isTeki为手牌是否为摸切, isBack为是否实例化为牌背，false则实例化为牌面
    {
        float cardWidth = 80 * 0.75f; // 牌宽，由于资源为80*129，经调整后缩放0.75倍
        float y = subViewport.Size.Y - 10 - 129 * 0.75f;
        float totalWidth = cardWidth * 14; // 计算所有手牌的总宽度
        float startX = (subViewport.Size.X - totalWidth) / 2; // 计算起始 X 坐标，使手牌居中显示

        TextureRect textureRect = new TextureRect(); // “实例化”手牌
		textureRect.Scale = new Vector2(0.75f, 0.75f);
		if(isBack) textureRect.Texture = ResourceLoader.Load<Texture2D>("res://assets/tiles/back.png"); // 从仓库中读取牌背的纹理
			else textureRect.Texture = ResourceLoader.Load<Texture2D>($"res://assets/tiles/{tile}.png"); // 从仓库中读取同名的牌的纹理
		if(!isTeki) textureRect.Position = new Vector2(startX + (index - 1) * cardWidth, y);
			else textureRect.Position = new Vector2(startX + 13 * cardWidth + 10, y);
        subViewport.AddChild(textureRect);
    }

    private void InstanceHand(List<string> hand, bool isBack) // 实例化全部手牌
    {
        for(int i = 0; i < hand.Count; i++) DisplayHand(hand[i], i, false, isBack);
    }

	private void RemoveCard(Type type) // 移除手牌，为了可维护性，这里使用泛型参数
	{
		foreach(var child in subViewport.GetChildren())
        {
            if(type.IsInstanceOfType(child))
            {
                subViewport.RemoveChild(child);
                child.QueueFree();
            }
        }
	}

    private void SortHand(List<string> hand)
    {
        // 创建一个Timer用于延迟显示洗好的手牌
        Timer delayTimer = new Timer();
        delayTimer.WaitTime = 0.25f;
        delayTimer.Timeout += () => {
            RemoveCard(typeof(TextureRect)); // 移除牌背
			InstanceHand(hand, false); // 实例化洗好的手牌
            hasInitialDealedCnt = 0; // 重置发牌计数器
            shouldInitialDeal = false; // 重置发牌标志
        };
        AddChild(delayTimer);

        // 移除之前显示的手牌并替换为牌背
        RemoveCard(typeof(TextureRect));
		InstanceHand(hand, true); // 实例化牌背

        delayTimer.Start();

		// 在此期间洗牌
		hand = hand.OrderBy(x =>
        { // 为每张牌生成一个的排序值，规则为：花色 * 1000 + 点数 * 10
        // 对于赤宝牌，排序值为花色 * 1000 + 45，这样可以使其排在普通4点牌和5点牌之间
            char suit = x[1];
            int rank = int.Parse(x[0].ToString());
            if(rank == 0) return suit * 1000 + 45;
            return suit * 1000 + rank * 10;
        }).ToList();
    }
}
