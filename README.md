# 切片skill

跨 Agent 的直播带货原话切片技能，面向 **Codex、DeepSeek Harness、豆包工作、Kimi Code CLI**。读取 MP4 和/或可靠 SRT，产出可直接剪辑的主播原话方案，不自动剪辑或发布视频。

**技能版本：1.1.0 · 业务规则：V5.1**

[已公开发布的版本](https://github.com/0L2Y0230/qiepian-skill/releases) · [版本记录](CHANGELOG.md) · [完整安装与兼容性说明](docs/安装与兼容性.md)

## 安装

使用对应版本的 `qiepian-skill-v1.1.0.zip`，解压得到直接包含 SKILL.md 和 references/ 的 qiepian-skill 文件夹。版本记录存在不代表已经发布到 GitHub；未发布版本以实际交付的本地 ZIP 为准。

| Agent | 安装完整目录 | 使用入口 |
|---|---|---|
| DeepSeek Harness | 项目 `.dsh/skills/` 或 `.agents/skills/`；用户默认 `~/.dsh/skills/` | 确认技能组件启用后，在任务中指定 qiepian-skill |
| 豆包工作 | “插件·技能·伙伴 → 技能 → 添加 → 上传技能”，导入解压后的完整目录 | 工作任务中通过 `/`、`@` 或更多技能选择 |
| Kimi Code CLI | 用户默认 `~/.kimi-code/skills/` 或项目 `.agents/skills/` | `/skill:qiepian-skill` |
| Codex | CODEX_HOME 下的 skills；未设置时 `~/.codex/skills/` | `$qiepian-skill` |

最终目录为 `<技能目录>/qiepian-skill/SKILL.md`，不能只复制入口。设置专属环境变量、插件或使用不同版本时，按完整说明核对实际路径。安装不自动启用 DeepSeek Harness 插件或连接账户；豆包使用官方导入入口。

有 Python 3.9+ 时可在解压目录选择一条命令执行：

```text
python scripts/install_agent.py --agent kimi
python scripts/install_agent.py --agent deepseek
python scripts/install_agent.py --agent codex
```

安装到项目的公共 `.agents/skills/` 目录：

```text
python scripts/install_agent.py --agent kimi --scope project --project-dir /absolute/project
```

同一项目目录只需安装一次，不要用另一个 Agent 名称覆盖同名目标。安装器拒绝覆盖已有安装，支持 `--dry-run`，不复制 config.local.json。没有 Python 可手动安装；生成方案不依赖 Python。

Codex 也可从本地目录安装，或使用其技能安装器安装已公开发布的仓库版本；远程仓库未更新前，不会自动获得本地新版本。

## 安装之后

新开任务，选择技能，发送：

```text
使用 qiepian-skill 安装自检，不生成切片文案。请完整读取规则，报告实际版本和可读取的文件。
```

安装助手确认安装和资源读取后提示：

> 切片skill 已安装完成！你可以直接发送 SRT 字幕文件，或者 MP4 视频＋对应的 SRT 字幕文件，我会按规则生成切片文案。

这是助手回复，不承诺系统弹窗。复制成功不能代替宿主技能发现和行为验收。

首次使用：

```text
使用 qiepian-skill 生成切片文案。指定商品：阔腿牛仔裤。素材：我提供的 SRT。输出到我指定的工作目录。
```

已进入本技能流程的同一会话，后续直接发送字幕或视频＋字幕即可。多商品未指定时先询问。新会话也可用宿主技能调用语法。

- 只有可靠 SRT：正常生成文本方案，画面、原声与精确剪点待核实。
- MP4＋可靠 SRT：先处理字幕，再依据实际媒体能力定向核验。
- 只有视频：依据可靠听辨和画面处理，不能支持关键判断时说明缺项，不编造编号。

默认保留完整原话、来源时间码和可靠原始编号，预计 45–90 秒，四项正文、1 条标题、3 个话题，可靠原始编号置于绝对末行。用户当次要求优先；不足时不凑话术。

## 规则与输出

完整规则在 references/，默认相对路径，不依赖作者盘符、私有云盘或历史聊天。每次正式生成或修改重新完整读取，交付前验收。VERSION.json 分别记录技能和业务规则版本。

默认输出到使用者工作目录的 outputs，可由当次请求或适用项目规则改位置。技能目录不存业务产物。沙箱只报告实际路径/下载附件，不能假称已保存到用户电脑。

如需外部规则，复制 config.example.json 为 config.local.json。规则/环境相对路径以技能目录为基准，输出相对路径以工作目录为基准。一次只选一个完整规则源，显式配置无效时说明问题，不拼补版本。本机配置不进入分享包，也不由安装器复制。

## 更新与验证

更新前保存现有技能、自行修改内容和配置，并由使用者处理旧安装。本包不自动删除、移动或覆盖已有技能。素材与结果留在技能目录之外。

```text
python scripts/verify_package.py /path/to/qiepian-skill-v1.1.0.zip
```

ZIP 内 manifest.json 记录文件校验值，SHA256SUMS.txt 用于核对 ZIP。自动检查证明文件与安装完整性，不能证明模型遵守规则。每个 Agent 应按 [验收测试方案](tests/验收测试方案.md) 执行 T0–T4，有授权视频再执行 T5。演示字幕是虚构素材。

## 维护与发布

四份业务规则保持统一来源，变更须有授权；本次仅改宿主适配，未改业务规则原文字节。agents/openai.yaml 是可选 Codex 元数据，其他宿主可忽略。

```text
python -m unittest discover -s tests -p "test_*.py"
python scripts/build_release.py --output-dir dist/release-v1.1.0
python scripts/verify_package.py dist/release-v1.1.0/qiepian-skill-v1.1.0.zip
```

另行运行技能格式校验，记录实际宿主行为测试范围。打包排除本机配置、Git、缓存、素材和输出。已有同名 ZIP 不覆盖；未获公开发布指令时只构建本地包，不自动推送或发布 Release。
