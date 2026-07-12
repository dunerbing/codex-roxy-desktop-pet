# 洛琪希风格 Codex 桌宠

这是一个适用于 Windows 版 Codex 的非官方同人桌宠，包含协调跳跃、辫子和裙摆惯性、
荧光爱心、魔杖宝石发光，以及害羞和开心表情。

![动画预览](docs/animation-preview.gif)

## Windows 一键安装

1. 下载最新 Release 压缩包并解压。
2. 双击 `install.cmd`。
3. 完全退出并重新打开 Codex。
4. 进入 **设置 > Pets**，选择 **Roxy Inspired Mage**。

安装位置：

```text
%USERPROFILE%\.codex\pets\roxy-inspired-mage
```

如果已经安装过旧版本，安装脚本会先自动备份。

## 卸载

双击 `uninstall.cmd`，然后重启 Codex。卸载脚本只会删除 Codex 桌宠目录下的
`roxy-inspired-mage` 文件夹。

## 重新生成动画

仓库已经包含生成好的精灵图，普通用户不需要安装 Python。开发者可以执行：

```powershell
python -m pip install Pillow
python tools/Build-RoxyAnimatedPet.py `
  --source assets/roxy-inspired-cutout.png `
  --sheet pet/spritesheet.png `
  --preview docs/animation-preview.jpg `
  --gif docs/animation-preview.gif
```

Codex 第 2 版精灵图尺寸为 `1536 x 2288`，由 `8 x 11` 个 `192 x 208` 帧组成。
各动作的实际播放帧数受 Codex 桌宠播放器限制。

## 许可证与声明

代码采用 MIT 许可证。角色风格美术属于非官方同人素材，不包含在 MIT 许可证中；
转载或使用前请阅读 [`ASSET_NOTICE.md`](ASSET_NOTICE.md)。

本项目与 OpenAI、Codex、《无职转生》创作者及相关权利方没有隶属或授权关系。

