using Godot;
using System;

public partial class CameraController : Camera3D
{
	public MahjongGenerator main;
	public RayCast3D MouseRayCast; // 连接 RayCast3D 节点

	public override void _Ready()
	{
		MouseRayCast = GetNode<RayCast3D>("MouseRayCast"); // 获取 RayCast3D 节点
		if (MouseRayCast == null) GD.PrintErr("RayCast3D 未绑定！请在 Inspector 面板手动拖入 MouseRayCast。");
	}

	public override void _Process(double delta)
	{
		UpdateRayCast();
	}

    private void UpdateRayCast()
    {
        Vector2 mousePos = GetViewport().GetMousePosition();  // 获取鼠标屏幕位置

        // 计算鼠标射线的起点和方向
        Vector3 rayOrigin = ProjectRayOrigin(mousePos);
        Vector3 rayDirection = ProjectRayNormal(mousePos);

        // 设置 RayCast3D 的位置和方向
        MouseRayCast.GlobalTransform = new Transform3D(Basis.Identity, rayOrigin); // 射线起点
        MouseRayCast.TargetPosition = rayDirection * 10f; // 让射线延伸 10 个单位
        MouseRayCast.ForceRaycastUpdate(); // 立即更新射线检测
    }
}
