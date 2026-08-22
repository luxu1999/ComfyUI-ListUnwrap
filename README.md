# ComfyUI-ListUnwrap

ComfyUI 小工具节点包：解决「列表输出 → 单值输入」和「多段图像批次拼接」的问题，专为 MiniMax H3 多段视频拼接工作流设计。

## 节点

| 节点 | 输入 | 输出 | 作用 |
|---|---|---|---|
| `ListToAudio` | `audios`（AUDIO 列表） | AUDIO | 取出列表中的音频，接给只认单个音频的保存节点（如 `VHS_VideoCombine`） |
| `ConcatImageBatches` | `images_A` / `images_B`（IMAGE） | IMAGE | 把两段图像批次按时间轴拼接（`torch.cat`，dim=0），用于多段视频合成 |

## 为什么需要

ComfyUI 中部分节点（如 `ComfyUI_MiniMaxH3_Director` 的导演台节点）会把 `images` / `audio` 以**列表**形式输出（`OUTPUT_IS_LIST = True`），而 `VHS_VideoCombine` 等保存节点只接受单个 `IMAGE` / `AUDIO`，直接连线会报错。

这两个节点负责转换与拼接：

- `Director.audio`（列表） → `ListToAudio` → 单个 AUDIO → `VHS_VideoCombine.audio`
- 多段生成后，每段的 IMAGE 批次 → `ConcatImageBatches` → 拼成整段视频

配合 [ComfyUI_MiniMaxH3_Director](https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director) 可实现「3 × 5 秒 → 15 秒」的分段拼接工作流——16G 显存也能跑 1080p 长视频。

## 安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/luxu1999/ComfyUI-ListUnwrap.git
# 然后重启 ComfyUI
```

也可以手动安装：把本仓库的 `__init__.py` 放到 `custom_nodes/ComfyUI_ListUnwrap/` 下，重启 ComfyUI。

## 用法示例

```
Director.images → easy imageListToImageBatch → 第一段批次(124帧)
Director.audio  → ListToAudio → VHS_VideoCombine.audio

第一段批次 + 第二段批次 → ConcatImageBatches → 248帧 → VHS_VideoCombine.images
```

更完整的「3 段拼接 + 首帧锁定」工作流（示例风格：固定机位、动作音效，均可按需调整），见仓库配套说明与提示词指南。


> 注意：下面的三段拼接工作流还依赖打了补丁的 `ComfyUI_MiniMaxH3_Director`，补丁见下文。

## 配套工作流（3 × 5 秒 → 15 秒）

`workflows/` 目录提供一条可直接跑的 MiniMax H3 三段拼接工作流（1080p，示例含动作音效、无台词，可按需改提示词）：

- `workflows/三段拼合视频生成工作流.png`（带内嵌工作流，**直接拖进 ComfyUI**）
- `workflows/三段拼合视频生成工作流.json`
- 等价英文名：`workflows/minimax_h3_3seg_15s_1080p_audio.png` / `.json`

原理：16G 显存无法 1080p 直出 10 秒以上，所以拆成 3 × 5 秒分段生成，自动取上一段第 123 帧作为下一段首帧（硬锁定、衔接无缝），最后拼接成 372 帧输出。

## 导演台补丁（必需）

工作流依赖 [ComfyUI_MiniMaxH3_Director](https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director)，原版有两个问题需要打补丁：

1. Combine 节点 autogrow 传参不兼容（报 `connect at least one group`）
2. 外部组路径未启用段间连续性（衔接硬切/角色消失）

自动打补丁：

```bash
python patches/apply_patches.py          # 自动定位 custom_nodes/ComfyUI_MiniMaxH3_Director
# 或 python patches/apply_patches.py D:/path/to/ComfyUI
```

也可用 `patches/01_*.patch`、`patches/02_*.patch` 手动 `git apply`。打完重启 ComfyUI。

## 给 AI Agent 的搭建文档

想用 Codex / OpenClaw 等 Agent 自动复现整套流程？直接把 [docs/AGENT_SETUP_CN.md](docs/AGENT_SETUP_CN.md) 交给 Agent，它会照着下载插件、打补丁、放模型、装工作流并运行。

提示词填写方法见：

- [docs/通用提示词填写方法.md](docs/通用提示词填写方法.md)
- [docs/总提示词拆分与一致性指南.md](docs/总提示词拆分与一致性指南.md)
## 兼容性

- ComfyUI ≥ 0.30（含新 comfy_api 节点框架）
- 依赖：`torch`（ComfyUI 自带）

## License

MIT

## 致谢

- [ComfyUI_MiniMaxH3_Director](https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director)（AIMixer）
- MiniMax H3 / LightX2V
