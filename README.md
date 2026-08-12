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

更完整的「3 段拼接 + 首帧锁定 + 固定机位 + 动作音效」工作流，见仓库配套说明与提示词指南。

## 兼容性

- ComfyUI ≥ 0.30（含新 comfy_api 节点框架）
- 依赖：`torch`（ComfyUI 自带）

## License

MIT

## 致谢

- [ComfyUI_MiniMaxH3_Director](https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director)（AIMixer）
- MiniMax H3 / LightX2V
