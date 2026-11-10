# BakeDown

[English](README.md) · [Русский](README.ru.md) · [Español](README.es.md) · [Deutsch](README.de.md) · **简体中文**

**版本 1.2.2 · Blender 4.2+ · GPL-3.0-or-later**

BakeDown 是一款 Blender 插件，可将 AI 生成和摄影测量得到的高面数网格（Hunyuan、Meshy、Tripo、Rodin、扫描模型——通常 5 万面以上并带一张 4K 纹理）转换为**可直接用于游戏的资产**。它只简化活动网格，把原始模型的 PBR 纹理烘焙到轻量网格上，生成 LOD，迁移骨骼绑定，并导出到 Unity、Unreal Engine 或 glTF。

整个流程是**非破坏性**的：原始模型保存为备份，可以随意尝试不同参数，**重置**即可恢复原状。

作者：**Kirill Migachev**

## 安装

1. 从本仓库（或发布页）下载 `bakedown.py`。
2. 在 Blender 中：**Edit → Preferences → Add-ons → Install from Disk…**，选择 `bakedown.py`。
3. 启用 **BakeDown — Game Asset Optimizer**。
4. 按 **N** 打开 3D 视图侧边栏，选择 **BakeDown** 标签页。

更新时，用新的 `bakedown.py` 覆盖安装并重启 Blender。

## 工作流程

静态物体（建筑、道具）：

```text
简化 → 烘焙 → （LOD）→ 导出
```

角色：

```text
简化 → 烘焙 → 绑定 → LOD → 导出
```

请在绑定**之后**生成 LOD，这样各级 LOD 会继承骨架。选中多个物体时，BakeDown 只处理活动网格（轮廓更亮的那个）。

## 功能

### 简化
- 按实际三角面数（滑块 + 1K/3K/5K/10K/20K 预设）或按近似形变预算（二分查找自动确定三角面数）设定目标。
- 合并顶点、清理游离几何体、修复法线（包括 AI 网格的自定义拆分法线）、平面融并和塌陷精简；可选填充孔洞、删除内部面、压平平面和显式三角化。
- 在面板中直接显示以毫米和物体尺寸百分比表示的形变估计。
- **形状**检查视图（实体 + MatCap + 线框）以及原始 ↔ 结果**对比**。

### 纹理烘焙
- 使用 Cycles 将基础色、糙度、金属度以及可选的切线空间法线贴图烘焙到新的 UV 展开上，支持 1K/2K/4K。
- 模态运行，带进度和取消；取消或出错时完整回滚。
- 自动射线距离、实时法线强度、基础色锐化。

### LOD
- LOD0–LOD3，提供策略、3D 射击、移动端和自定义预设。所有 LOD 共用一套纹理。
- 支持骨架：已绑定网格的 LOD 会继承骨架和权重。
- 命名为 `<物体>_LOD0..3`，Unity 会自动创建 LOD Group。
- 重新简化或烘焙后若 LOD 已过期会给出提示，并拒绝导出过期的 LOD。

### 绑定迁移
- 导入带蒙皮的 FBX 作为模板，把骨架和顶点权重迁移到活动网格（适用于相似的人形角色）。
- 在静止姿态（Rest Position）下工作，出错时也会恢复原有姿态状态。

### 导出
- Unity 用 FBX、Unreal 用 FBX（平滑组）以及独立 GLB。
- 模型和 PNG 纹理保存在以 .blend 文件命名的子文件夹中；FBX 以相对路径引用 PNG。
- 选项：翻转法线贴图绿色通道（DirectX 约定）、打包 ORM。
- 可导出单个物体，或将其整个 LOD 集合（连同骨架）导出为一个文件。

## 界面语言

界面源语言为英语，内置**俄语、西班牙语、德语和简体中文**翻译；当 Blender 界面语言设置为相应语言时会自动显示（**Preferences → Interface → Translation**）。

## 使用建议

- 烘焙使用 CPU 上的 Cycles：4K 分辨率下每个物体需要几十秒到几分钟。
- 烘焙后出现黑斑 → 增大**射线距离**；细节发糊 → 改回 0（自动）。
- 默认不进行三角化：引擎导入时会自行三角化，GPU 开销相同。
- 对于 Mixamo 动画：只需绑定一次；动画作为单独的 FBX，在 Unity 中通过 Humanoid Avatar 重定向。

## 限制

- 形变是近似的采样指标，而非精确的豪斯多夫距离。
- 正在进行的烘焙步骤无法中断；取消会在两张贴图之间生效。
- 内部面检测为实验功能，默认关闭。
- 导入引擎前请检查异常的负缩放和非等比缩放。

## 开发

架构与注意事项见 [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)（英文），测试状态见 [docs/VERIFICATION.md](docs/VERIFICATION.md)。无界面运行测试：

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python tests/run_tests.py
```

## 许可证

GNU 通用公共许可证 v3.0 或更高版本。详见 [LICENSE](LICENSE)。
