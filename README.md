# Hchat-skills

Eta 用的 Skills 仓库。每个 Skill 是 `skills/<skill-id>/SKILL.md` 一个目录，可以单独安装。

## 安装

在 Eta 里用 `$skill-installer` 指定本仓库即可：

```
https://github.com/SamrtinSinale/Hchat-skills
```

安装器会列出所有含 `SKILL.md` 的目录，选中要装的路径后安装；已安装的 Skill 从下一轮对话开始可用。

## 已有 Skills

| Skill | 用途 |
|---|---|
| `apk-patch-porting` | 把某个 APK 的定制补丁（smali 层）从旧版本移植到新版本：枚举补丁集、混淆符号映射、汇编、重打包、静态校验，附带寄存器活跃性检查等防翻车工具。 |

## 目录约定

```text
skills/<skill-id>/
├── SKILL.md          # 必需，YAML frontmatter: name / description
├── scripts/          # 可选，可复用脚本
├── references/       # 可选，按需读取的详细资料
└── assets/           # 可选，模板等
```
