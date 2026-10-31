# 切片skill

直播带货主播原话切片方案技能。技术标识为 `qiepian-skill`，业务规则为 V5.1（以每次实际读取的主文件为准）。

## 使用

在 Codex 新聊天中提供 MP4 和/或 SRT 路径，然后发送：

```text
使用 $qiepian-skill 生成切片文案，素材路径：……
```

支持 SRT-only；多商品未指定时先确认，保留原话、时间码与可靠的原始 SRT 编号。默认 45–90 秒，四项正文、1 条标题和 3 个话题。音画核实等级按实际证据披露。

## 文件与本机位置

- `SKILL.md`：技能入口和执行流程。
- `agents/openai.yaml`：显示名称、调用提示和自动发现配置。
- `rules/AGENTS.md`、`rules/01_现行规则/`：从 `D:\Daihuo` 按原字节备份的五份规则文件。
- 本机安装位置：`D:\CodexHome\skills\qiepian-skill`，也是本仓库的工作目录。
- 本机现行规则入口：`D:\Daihuo`。每次执行重新读取，不能用仓库备份代替。
- 默认文案输出：`D:\GPTWork\切片带货\outputs`。

## 后续更新

修改本机技能文件后，在 PowerShell 提交并上传：

```powershell
Set-Location -LiteralPath 'D:\CodexHome\skills\qiepian-skill'
git diff
git add -- SKILL.md agents/openai.yaml README.md .gitignore .gitattributes rules
git commit -m "更新切片skill"
git push
```

规则仍在 `D:\Daihuo` 维护。获得规则修改授权并完成修改后，在本仓库目录更新备份，再提交上传：

```powershell
Copy-Item -LiteralPath 'D:\Daihuo\AGENTS.md' -Destination '.\rules\AGENTS.md'
foreach ($ruleFile in @('独立版总控执行卡.md', '切片文案执行卡.md', '切片文案.md', '独立版强制验收卡.md')) {
    Copy-Item -LiteralPath (Join-Path 'D:\Daihuo\01_现行规则' $ruleFile) -Destination (Join-Path '.\rules\01_现行规则' $ruleFile)
}
git diff
git add -- rules
git commit -m "同步现行切片规则"
git push
```

在 GitHub 网页修改仓库后，本地先 `git status` 确认工作区干净，再 `git pull --ff-only`。这会更新仓库文件；不会自动把 `rules/` 部署到 `D:\Daihuo`。规则恢复或部署应明确核对差异并获得相应授权，避免覆盖本机更新。

## 在其他机器部署

将仓库克隆至该机器的 Codex 用户技能目录，文件夹名使用 `qiepian-skill`。本版本依赖 Windows 的 `D:\Daihuo` 规则位置；经确认后将 `rules/` 的内容部署到该目录。若有同名现行文件，先比较，不直接覆盖。不同路径的部署应相应调整技能路径及输出位置。

## 验证边界

已执行技能格式、调用配置和本地规则文件可读性校验。没有进行真实直播视频的音画核验；上传仓库不代表业务选段测试已通过。
