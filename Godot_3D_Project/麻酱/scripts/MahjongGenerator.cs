using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.WebSockets;
using System.Security.Cryptography.X509Certificates;

public partial class MahjongGenerator : Node3D
{
	// public PackedScene Node3D = (PackedScene)GD.Load("res://scenes/Node3D.tscn");
    Random random=new Random();
	public PackedScene Pai = (PackedScene)GD.Load("res://pai/majiang.tscn");
	// 存储所有牌的列表
    public List<string> allTiles = new List<string>();
    // 存储玩家手中的牌
    public List<string> playerTiles = new List<string>();
    public int Create_Or_Join{get;set;}=0;//1为创建房间，2为加入房间
    public bool gameStart{get;set;} = false; // 游戏是否开始
    public int PlayerNum{get;set;}=14;//玩家手牌数
    public int allNum{get;set;}=108;//总牌数
    private float dealTimer = 0f; // 发牌计时器
    public  int dealIndex{get;set;} = 0; // 发牌数
    // 洗牌标志
    public bool shouldSort{get;set;} = false; // 是否需要排序
    public bool hasSorted{get;set;} = false; // 是否已经排序
    private float SortTimer = 0f; // 排序计时器
    public bool isRotatingFirst{get;set;} = false; //翻回来
    private float rotatingTimer = 0f; // 翻转计时器
	public bool isMyRound = false; // 是否是我的回合
    public string[] name{get;set;}=new string[]{"w_1","w_2","w_3","w_4","w_5","w_6","w_7","w_8","w_9","t_1","t_2","t_3","t_4","t_5","t_6","t_7","t_8","t_9","o_1","o_2","o_3","o_4","o_5","o_6","o_7","o_8","o_9"};
    public override void _Ready()
    {
        for(int i=0;i<=26;i++)
        {
            for(int j=0;j<4;j++)
            allTiles.Add(name[i]);
        }//初始化牌堆
    }
    public override void _Process(double delta)
    {
		//每隔0.2s发一张牌
        if(!gameStart)return;

        if (dealIndex < PlayerNum)
        {
            dealTimer += (float)delta;
            if (dealTimer >= 0.2f)
            {
                int a=random.Next(0,allNum);
                playerTiles.Add(allTiles[a]);
                allTiles.RemoveAt(a);
                allNum--;
                Node pai=Pai.Instantiate();
                AddChild(pai);
                dealTimer = 0f;
                dealIndex++;
            }//直接实例化，位置在牌的代码里面自己调整
        }
        else if (!shouldSort&&!hasSorted)//发完牌后排序
        {
            hasSorted = true;
            shouldSort = true;
            SortTimer = 0f;
        }
		//发牌后先翻牌，然后排序，再翻过来
        if (shouldSort)//翻拍+排序
        {
            SortTimer += (float)delta;
            if (SortTimer >= 0.4f)
            {
                playerTiles=SortTiles(playerTiles);
                if (!isRotatingFirst)//翻回来
                {
                    isRotatingFirst = true;
                    SortTimer = 0f;
                }
                else
                {
                    shouldSort = false;
                    isRotatingFirst = false;
                    SortTimer=0f;
                }
            }
        }
    }
        private List<string> SortTiles(List<string> tiles)
        {
            return tiles
                .OrderByDescending(tile => tiles.Count(t => t[0] == tile[0])) // 牌数多的花色排前
                .ThenBy(tile => tile[0])   // 同牌数时，按花色排序（w < o < t）
                .ThenBy(tile => int.Parse(tile.Substring(2)))  // 同花色时，按点数升序
                .ToList();
        }
	// //摸牌时调整牌的位置
    // private void AdjustTilePosition(MahjongTile tile, int index)
    // {
    //     float tileWidth = 0.18f; // 假设牌的宽度
    //     float offsetZ = 1.44f;
    //     float x = 2.3f;
    //     float y = 1.4f;
    //     float z = offsetZ - index * tileWidth;
    //     tile.Scale = new Vector3(0.75f, 0.75f, 0.75f);
    //     tile.RotateZ(Mathf.DegToRad(80));
    //     tile.Position = new Vector3(x, y, z);
    // }

	//旋转Z坐标
    // private void ZRotateTiles(float degrees)
    // {
    //     foreach (MahjongTile tile in playerTiles) tile.RotateZ(Mathf.DegToRad(degrees));
    // }

	// //给牌排序，用到了一个非常NB的Linq库，妈妈再也不用担心我的排序辣（
	// private void SortTiles()
	// {
	//     playerTiles = playerTiles
	//         .OrderByDescending(tile => GetTileCount(tile)) // 先按每种花色的牌数降序排列
	//         .ThenBy(tile => GetTileType(tile)) // 再按花色顺序（万 -> 条 -> 筒）
	//         .ThenBy(tile => GetTileNumber(tile)) // 最后按点数排序（1~9）
	//         .ToList();
	// }//基本是自然语言.jpg

	// // 获取花色的索引 (万:0, 条:1, 筒:2)
	// private int GetTileType(MahjongTile tile)
	// {
	//     string path = tile.SceneFilePath.ToLower(); // 获取路径
	//     if (path.Contains("wan")) return 0;
	//     if (path.Contains("tiao")) return 1;
	//     if (path.Contains("tong")) return 2;
	//     return 3; // 避免异常情况
	// }

	// // 获取具体的牌值 (1~9)
	// private int GetTileNumber(MahjongTile tile)
	// {
	//     string path = tile.SceneFilePath.ToLower();
	//     string name = path.Split("/").Last().Replace(".glb", ""); // 提取文件名
	//     return int.Parse(new string(name.Where(char.IsDigit).ToArray())); // 提取数字部分
	// }

	// // 获取当前花色的牌总数
	// private int GetTileCount(MahjongTile tile)
	// {
	//     int type = GetTileType(tile);
	//     return playerTiles.Count(t => GetTileType(t) == type);
	// }

	// //排序后调整牌的位置
    // private void AdjustTilePositionsAfterSort()
    // {
    //     for (int i = 0; i < playerTiles.Count; i++) AdjustTilePosition(playerTiles[i], i);
    // }
}