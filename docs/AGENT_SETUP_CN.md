# MiniMax H3 三段拼接工作流 · Agent 自动搭建流程

> 本文件是写给 **Codex / OpenClaw 等 AI Agent** 的指令：让 AI 读懂后可以自动下载插件、打补丁、放模型、装工作流并跑起来。
> 复现目标：**3 × 5 秒 → 15 秒 1080p** 的 MiniMax H3 分段拼接视频。画面、运镜、音效等具体内容由提示词自由决定（仓库示例只是其中一种风格，可按需改提示词）。

---

## 1. 环境要求

- Windows / Linux 均可；ComfyUI ≥ 0.30（推荐 0.31.x），能加载官方 MiniMax H3 节点
- Python 3.10+
- 参考显卡：RTX 4080 16G（16G 显存是这套分段方案的动机：1080p 直出 10 秒+会 OOM）
- 网络：GitHub + HuggingFace（国内可用 `gh-proxy.com` 镜像和 `hf-mirror.com`）

## 2. 安装插件（按顺序）

在 `ComfyUI/custom_nodes/` 下安装：

```bash
# 1) 导演台（必须，且必须打第 3 节的补丁）
git clone https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director.git
# 国内镜像：git clone https://gh-proxy.com/https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director.git

# 2) 本仓库（提供 ListToAudio / ConcatImageBatches，工作流必需）
git clone https://github.com/luxu1999/ComfyUI-ListUnwrap.git

# 3) 其余依赖
git clone https://github.com/kijai/ComfyUI-KJNodes.git
git clone https://github.com/yolain/ComfyUI-Easy-Use.git
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
```

安装 Python 依赖：

```bash
# 4) 导演台的依赖（scenedetect / opencv / imageio-ffmpeg 等）
pip install -r ComfyUI_MiniMaxH3_Director/requirements.txt

# 5) SageAttention（KJ 的 Sage 节点需要；必须 1.x，2.x 与 H3 不兼容会崩）
pip install sageattention==1.0.6
```

## 3. 给导演台打两个补丁（关键！）

原版导演台有 2 个问题，不打补丁工作流会报错或衔接失效：

| 补丁 | 解决 | 文件 |
|---|---|---|
| 1. Combine autogrow 兼容 | `Director Groups Combine: connect at least one group` | `nodes/director_groups.py` |
| 2. 外部组连续性 | 段间「尾帧→下一段首帧」不生效、衔接硬切 | `director/external_groups.py` |

**推荐方式**：运行本仓库的自动打补丁脚本

```bash
cd ComfyUI-ListUnwrap
python patches/apply_patches.py            # 自动定位到 custom_nodes/ComfyUI_MiniMaxH3_Director
# 或显式指定 ComfyUI 根目录：
python patches/apply_patches.py D:/path/to/ComfyUI
```

脚本会做精确字符串替换并打印 `[OK]` / `[SKIP]`。也可以用 `patches/01_*.patch` / `02_*.patch` 手动 `git apply` 或 `patch -p1`。

**打完补丁必须重启 ComfyUI。**

> 版本说明：补丁在 ComfyUI 0.31.x 上验证。如果你用的是 0.40+ 的新前端，autogrow 可能原生兼容，可先只打补丁 2（连续性）试跑，报 Combine 错误再打补丁 1。

## 4. 模型、LoRA 与参考图

### 4.1 模型与 LoRA（放到对应目录）

| 文件 | 目录 |
|---|---|
| `minimax_h3_ref2va_pruned_int8_convrot.safetensors`（第一段 r2v 底座） | `models/diffusion_models/` |
| `minimax_h3_fl2va_pruned_int8_convrot.safetensors`（第二三段 i2v 底座） | `models/diffusion_models/` |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`（CLIP） | `models/text_encoders/` |
| `minimax_h3_video_vae_fp16.safetensors` | `models/vae/` |
| `minimax_h3_audio_vae_fp32.safetensors` | `models/vae/` |
| `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy_resized_avg_rank_21_bf16.safetensors`（FL2V turbo LoRA，来自 [Kijai/MiniMax-H3_comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy)） | `models/loras/` |

国内下载：把 HuggingFace 链接换成 `https://hf-mirror.com/...`。

### 4.2 参考图

输入参考图放到 `ComfyUI/input/`：

- 场景图（工作流默认名 `桌面.jpg`，换成你自己的场景图后记得改提示词）
- 角色图（默认 `陈千语_mid20.png`，角色占画面约 20% 高度）

用本仓库脚本把任意角色图处理成约 20% 高度、白底 1920×1088 的参考图（避免模型把角色画大）：

```bash
python scripts/prepare_char_ref.py 你的角色图.png 陈千语_mid20.png 0.20
# 输出文件放到 ComfyUI/input/
```

## 5. 放入工作流（本仓库提供两份，任选其一）

**推荐直接下载这两个文件**（同一套「三段拼合视频生成工作流」）：

- `workflows/三段拼合视频生成工作流.png`（带内嵌工作流，**直接拖进 ComfyUI 即可加载**）
- `workflows/三段拼合视频生成工作流.json`（前端格式，ComfyUI 打开/导入用）

等价文件（英文名，方便脚本/命令行下载）：

- `workflows/minimax_h3_3seg_15s_1080p_audio.png`
- `workflows/minimax_h3_3seg_15s_1080p_audio.json`

打开后检查：

- 节点 `ListToAudio`、`ConcatImageBatches` 已注册（来自本仓库）
- 三个 `MiniMaxH3Director` 节点已加载（补丁后）
- 提示词按 `docs/通用提示词填写方法.md` 填写或替换

## 6. 启动参数（重要）

启动 ComfyUI 时：

- **不要加全局 `--use-sage-attention`**：H3 会被全局 Sage 补丁污染，输出纯噪声（本工作流用 KJ 节点的 Sage 补丁即可）
- 建议设置环境变量 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`，降低显存碎片、提高 1080p 稳定性

```bash
# Windows PowerShell 示例
$env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"
python main.py --preview-method auto --disable-cuda-malloc
```

## 7. 运行与耗时

一次 Queue 全自动完成：三段生成 → 自动取第 123 帧 → 拼接 372 帧 → 保存视频 + 工作流 PNG。

| 配置 | 分辨率 | 每段帧数 | 步数建议 | 15 秒总耗时（4080 16G） |
|---|---|---|---|---|
| 480p | 864×480 | 124 | 4 | ≈ 4 分钟 |
| 720p | 1280×736 | 124 | 4 | ≈ 8–10 分钟 |
| 1080p | 1920×1088 | 124 | 第一段 8、后两段 4 | ≈ 31–33 分钟 |

## 8. 常见问题

| 现象 | 原因 / 处理 |
|---|---|
| `Director Groups Combine: connect at least one group` | 补丁 1 未生效 |
| 段间硬切 / 角色消失 1 秒 | 补丁 2 未生效（连续性未开启） |
| 找不到 `ListToAudio` / `ConcatImageBatches` | 本仓库没装或没重启 ComfyUI |
| 1080p 直出爆显存 | 这是本方案要绕开的问题，用分段方案即可 |
| 画面出现多余玩偶/道具 | 提示词里用「画面物品白名单」约束（见提示词指南，可选） |

## 9. 补丁内容速览（人类可读）

**补丁 1**：`nodes/director_groups.py` 的 `MiniMaxH3DirectorGroupsCombine.execute` 改为兼容 `**kwargs`，把 `group_0/group_1/...` 槽位收进字典再合并，解决 ComfyUI 0.31 autogrow 传参不兼容。

**补丁 2**：`director/external_groups.py` 的 `build_plan_from_external_groups` 构造 `DirectorPlan` 时读取 `resolve_continuity_settings(timeline)` 并传入 `continuity_enabled / continuity_overlap_frames`，让外部组路径真正启用「上一段尾帧 → 下一段首帧」衔接。

---

许可证：MIT（本仓库）。导演台插件版权归 AIMixer，MiniMax H3 模型版权归 MiniMax / LightX2V。