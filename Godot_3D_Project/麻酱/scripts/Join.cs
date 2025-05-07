using Godot;
using System;

public partial class Join : StaticBody3D
{
	// Called when the node enters the scene tree for the first time.
	public RayCast3D MouseRayCast; // 连接 RayCast3D 节点
	public MahjongGenerator main;	
	public AnimatedSprite3D MyShow;
	public override void _Ready()
	{
		MouseRayCast = GetNode<RayCast3D>("/root/Node3D/Camera3D/MouseRayCast"); // 获取 RayCast3D 节点
		main = GetNode<MahjongGenerator>("/root/Node3D/MahjongGenerator");
		MyShow = GetNode<AnimatedSprite3D>("Show");
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
		if(MouseRayCast.IsColliding())
		{
			if(MouseRayCast.GetCollider()==this)
			{
				MyShow.Play("on");
				if(Input.IsActionJustPressed("LeftClick"))
				{
					main.gameStart=true;
					QueueFree();
				}
			}
			else MyShow.Play("off");
		}
		else MyShow.Play("off");
		if(main.gameStart)
		{
			QueueFree();
		}
	}
}
