# 让 Agent 从 GitHub 安装切片skill

这是给负责安装的 Agent 的执行说明。用户要求“从这个 GitHub 安装 Skill”即授权下载及在当前 Agent 的正常技能范围内创建本技能；不自动授权覆盖已有安装、配置凭据、启用新插件、发布或上传素材。遵守当前环境已有的权限边界。

仓库：https://github.com/0L2Y0230/qiepian-skill

最新正式版本：https://github.com/0L2Y0230/qiepian-skill/releases/latest

## 1. 确认实际宿主

根据当前真实环境判断是 DeepSeek Harness、豆包工作、Kimi Code CLI 还是 Codex，不以模型名称替代宿主。读取仓库 [安装与兼容性.md](安装与兼容性.md)，按当前宿主分流。不要调用当前宿主不存在的 `$skill-installer` 或其他厂商工具。

## 2. 下载完整包并检查

优先从最新正式 Release 下载版本化的 `qiepian-skill-v<版本>.zip` 和 `SHA256SUMS.txt`；可以使用已有浏览器/下载工具，或已配置的 gh CLI。无需登录此公开仓库，不要求用户创建 GitHub 令牌。

有 gh CLI 时，先读取 Release 信息，再按该版本的实际文件名下载到独立临时目录：

```text
gh release view --repo 0L2Y0230/qiepian-skill --json tagName,assets
gh release download --repo 0L2Y0230/qiepian-skill --pattern "qiepian-skill-v*.zip" --pattern "SHA256SUMS.txt" --dir <独立临时目录>
```

也可以通过公开接口 `https://api.github.com/repos/0L2Y0230/qiepian-skill/releases/latest` 读取 `tag_name` 与资产的 `browser_download_url`，下载该 Release 的 ZIP 和校验文件。不要只取 GitHub 网页 HTML 或单个 SKILL.md。下载到已有文件时不要覆盖，改用新临时目录。

核对 SHA256SUMS.txt 中对应 ZIP 的 SHA-256；只能证明下载一致性，不能将同源校验宣称为独立信任背书。确认 ZIP 只有 qiepian-skill/ 根目录，拒绝绝对路径、`..`、反斜杠、驱动器路径或重复条目，安全解压到临时目录。若有 Python 3.9+，使用解压包的 `scripts/verify_package.py <ZIP路径>` 核对 manifest.json 与每个文件。先读脚本再执行；没有 Python 可用等效文件/校验工具逐文件验证，不因缺 Python 自动安装 Runtime。

若 Release 资产下载不可用，可从仓库获取一个**具体正式发布标签**的完整目录（git clone 或下载标签源码归档），读取 VERSION.json 确认版本，并检查入口和完整规则文件。此方式不是 Release ZIP 的校验路径，不能假称已通过其 SHA256SUMS。只获取稳定标签，不拼用不同分支或版本。不要使用硬编码作者电脑路径。

## 3. 按宿主安装

- **DeepSeek Harness**：将完整目录安装到当前项目 `.dsh/skills/qiepian-skill/` 或 `.agents/skills/qiepian-skill/`，或用户 DSH_HOME（默认 ~/.dsh）的 skills 子目录。有 Python 可在解压包内执行 `python scripts/install_agent.py --agent deepseek`。检查技能组件是否已启用；缺少组件时说明需配置的具体项目，不自动重写插件配置。
- **Kimi Code CLI**：默认用户目录 `~/.kimi-code/skills/qiepian-skill/`，有 KIMI_CODE_HOME 时使用其 skills 子目录；有 Python 可运行 `python scripts/install_agent.py --agent kimi`。可用 `/skill:qiepian-skill` 检查发现与调用。
- **Codex**：使用当前 CODEX_HOME 下的 skills，未设置时为 `~/.codex/skills/`；有 Python 可运行 `python scripts/install_agent.py --agent codex`。也可使用当前确实可用的仓库技能安装器，仓库技能位于根目录。
- **豆包工作**：通过“插件·技能·伙伴 → 技能 → 添加 → 上传技能”导入解压后的完整目录，包含 references/。若当前 Agent 有界面操作能力，可在用户已登录的客户端内完成此安装；否则给出已下载目录及该最少导入步骤，标明“待导入”，不要声称已安装，也不要自行操作登录或猜测内部技能路径。

所有宿主都必须保留完整规则资源。目标存在同名技能则停止覆盖，先报告版本与路径，由使用者决定更新；安装器也会拒绝覆盖。不得复制 config.local.json、.git、缓存、原始素材或输出，不能修改其他技能或全局认证。

## 4. 验证完成

1. 确认安装后的 SKILL.md、VERSION.json 和 references/ 全部可读，版本一致。
2. 确认当前宿主已发现该技能；需要新会话或刷新时明确说明，不以目录存在代替发现成功。
3. 调用“qiepian-skill 安装自检，不生成文案”，按 SKILL.md 实际完整读取规则。自检只能报告已执行项，不拿哈希或摘要替代全文读取，不将 SRT-only 标成已核音画。
4. 安装与自检完成后发送：

> 切片skill 已安装完成！你可以直接发送 SRT 字幕文件，或者 MP4 视频＋对应的 SRT 字幕文件。素材里有多件商品时，请告诉我要剪哪件。

同时简要报告版本、实际安装位置及未完成的检查。没有安装/写入/发现/导入能力时报告具体停在哪一步，提供最少操作，不给出虚假成功提示。安装自检不等于 T0–T5 的业务行为及真实视频测试全部通过，实际测试边界见 [验证记录](验证记录.md)。
