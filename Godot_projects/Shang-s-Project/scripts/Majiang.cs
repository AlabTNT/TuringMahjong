using Godot;
using System;

public partial class Majiang : StaticBody3D
{
	// Called when the node enters the scene tree for the first time.
	public RayCast3D MouseRayCast; // 连接 RayCast3D 节点
	public Marker3D marker;
	public AnimatedSprite3D Zi;
	public MahjongGenerator main;
	public StaticBody3D chosenBody;
	public bool isPicking{ get; set; } = false;
	public bool hasPicked{ get; set; } = false;
	public float V,X;
	public int myNumber;//手牌编号
	public MeshInstance3D ChosenArea;
	public Godot.Vector3 originPosition;
	public override void _Ready()
	{
		MouseRayCast = GetNode<RayCast3D>("/root/Node3D/Camera3D/MouseRayCast"); // 获取 RayCast3D 节点
		marker = GetNode<Marker3D>("/root/Node3D/Dong");
		main = GetNode<MahjongGenerator>("/root/Node3D/MahjongGenerator");
		Zi = GetNode<AnimatedSprite3D>("Zi");
		chosenBody = GetNode<StaticBody3D>("Chosen");
		ChosenArea = GetNode<MeshInstance3D>("ChosenArea");
		myNumber=main.dealIndex;
		originPosition=new Godot.Vector3(marker.GlobalPosition.X,marker.GlobalPosition.Y,marker.GlobalPosition.Z+(main.PlayerNum-1)*0.24f/2-main.dealIndex*0.24f);
		GlobalPosition=originPosition;
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
		if(main.shouldSort)
		{
			RotationDegrees=new Godot.Vector3(180,0,90);
		}
		if(main.isRotatingFirst)
		{
			RotationDegrees=new Godot.Vector3(0,0,90);
		}
		Zi.Play(main.playerTiles[myNumber]);
		if(MouseRayCast.IsColliding())
		{
			if(MouseRayCast.GetCollider()==this)
			{
				isPicking=true;
				if(Input.IsActionJustPressed("LeftClick"))
				{
					if(hasPicked==false)
					{
						hasPicked=true;
					}
					else
					{
						QueueFree();
						//出牌
					}
				}
			}
			else if(isPicking&&MouseRayCast.GetCollider()==chosenBody)
			{
				isPicking=true;
				if(Input.IsActionJustPressed("LeftClick"))
				{
					hasPicked=false;
				}
			}
			else
			{
				isPicking=false;
				if(Input.IsActionJustPressed("LeftClick"))
				{
					hasPicked=false;
				}
			}
		}
		else 
		{
			isPicking=false;
			if(Input.IsActionJustPressed("LeftClick"))
			{
				hasPicked=false;
			}
		}
		if(hasPicked==true)
		{
			ChosenArea.Show();
		}
		else ChosenArea.Hide();
		if(isPicking||V!=0)
		{
			V=0.01f;
			if(X<=0.1)X+=V;
			GlobalPosition=new Godot.Vector3(originPosition.X-X,originPosition.Y,originPosition.Z);
		}
		if(!isPicking)
		{
			X=0;
			V=0;
			GlobalPosition=originPosition;
		}
	}
}
