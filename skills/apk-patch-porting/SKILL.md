---
name: apk-patch-porting
description: "把某个 Android APK 的定制补丁（smali 层）从旧版本移植到新版本，并完成汇编、重打包与静态校验。当用户说“把 X 版的功能/补丁移植到 Y 版”、要求“完全移植”、两份 APK 是同一应用的混淆前后版本（R8 类名不同、行号相近但名字不同），或需要只替换 classes.dex 重打包时使用。环境：Eta 的 Linux(Debian) 环境 + java + apktool.jar。"
---

# APK 补丁跨版本移植

目标：把旧版 APK 里的定制补丁，逐条映射到新版 APK 的混淆代码上，汇编、重打包、静态校验，并如实说明没搬的部分和风险。

## 硬性前提

1. **先找“干净对照”**：必须有同版本、无补丁的解码树，才能枚举出完整补丁集。没有就用独特字符串/调用点缩小范围，并明确告诉用户“补丁集可能不全”。
2. 只做静态层面：产物**未在设备实跑**，不要含糊成“能装上”。产物不带签名是常态、不是待办——本机签名校验已绕过（实测：用户装的就是无签名的 classes.dex 替换包），交付后可选 `pm install -r <apk>` 直接装上（覆盖当前版本，需先征得同意）。
3. 不覆盖用户的原包和已交付产物，新产物换新文件名。

## 流程

1. **定版本**：`java -jar /workspace/apktool/apktool.jar d -r -f -o <dir> <apk>`，从 `a.smali` 之类的版本字符串确认 versionName/versionCode；确认包名一致。
2. **枚举补丁集**：`diff -rq stock/smali mod/smali` 得差异类；逐个跑 `scripts/semantic_diff.py`（去 `.line`/`.local`/标签重编号后 diff），区分真改动与重打包产物：
   - 字段初值写法差异（`= false` / `= null`）、try 块边界移动、合成 lambda 类增删 → **重打包产物，不是补丁**。
3. **建符号映射**：用“独特字符串 + 指令上下文 + 调用点”匹配新旧类，**不要靠类名**（混淆名每版都变）。把映射写成显式表（`Luw0;->cln` → `Ly21;->cln` 之类）留在脚本里。
4. **落补丁**：写脚本做**锚点文本替换 + `count == 1` 断言**，不要按行号（前面的插入会位移）。锚点要带足够上下文（前后各 2–4 行）。
5. **插入前做寄存器检查**：`scripts/reg_free.py <file> <line>`（见下节，这是最容易翻车的一步）。
6. **汇编**：`scripts/BuildDex.java` 全量汇编，`fail` 必须为 0（见 `scripts/README.md`）。
7. **重打包**：`scripts/repack_apk.py <src.apk> <classes.dex> <out.apk>`，只替换 `classes.dex`，其余条目逐条原样复制。
8. **校验**（缺一不可）：
   - 反解成品（`apktool d -r`）能通过 → dex 结构可解析；
   - 与上一版解码树 `diff -rq`，确认只有预期文件不同；
   - `dex2oat --dex-file=... --oat-file=... --instruction-set=arm64 --compiler-filter=verify` 无报错；
   - 记录 APK 与 `classes.dex` 的 sha256。
9. **交付**：列出“搬了什么 / 有意没搬什么 / 与旧版的偏离 / 需要用户实跑验证的行为”。

## 寄存器与标签（血的教训）

- **临时寄存器必须先证明是死的**：`reg_free.py` 给出插入点之后该寄存器的第一次出现；若是**读**（或在分支合并处要沿用）就不能用。
- 新版的**长生命周期寄存器**最容易踩：旧版作者可能在每个使用点都重新 `const-string` 设一遍常量，新版只在开头设一次、后面长期复用同一个寄存器。照抄旧版代码就会把它覆盖，运行期静默出错（案例见 `references/case-hchat-647.md`）。
- `invoke-kind {vA, vB}` 是 35c 格式，**只能用 v0–v15**；需要更高寄存器就改 `/range` 形式。
- 新增标签（`:cond_xx`）前先列出该方法内已有标签名，重名汇编直接失败。
- 分支合并点：同一寄存器在不同路径分别是 int 和对象，只要合并后到下一次写之间没有读，一般能过验证；有读就会 VerifyError。
- 最小空值守卫：旧版能跑不代表新版下游接受 null，必要时加 `if-eqz` 守卫，并在交付说明里写明这是有意偏离原版。

## 排障线索

- **先确认用户装的是哪一版**：`pm path <pkg>` → 解出 `base.apk` 里的 `classes.dex` 算 sha256，跟构建产物比对。
- **通知/Intent 类问题**：`logcat -b all -v brief | grep -E "notification_action_clicked|notification_enqueue"` 能看到点击是否发出、Intent 是否带 extras。
- **模块运行期日志**：`/data/adb/lspd/log/`（modules/verbose 两个文件），先按关键词计数再取上下文。
- **现象反推**：从“哪个功能坏”回溯到“哪个键名/寄存器/字符串被破坏”，再去代码里验证该寄存器在插入点后是否被读。

## 一条命令（hchat_port.py）

Hchat 场景已经全自动，**输入只要新版官方 APK**：

```bash
python3 scripts/hchat_port.py <新版官方.apk> [--work /workspace/port_out] [--out 输出.apk]
```

它按顺序做：解码 → 按锚点自动推导全部符号映射（构建类 / 数据类 / 配置类 / 发布类 /
搜索索引类 / 快速已读类 / 设置 UI 类 / 行点击接口 / Compose / lambda 接口 / 包装类 / Unit /
空判断 / 列表构造 + 8 个图标接管点）→ 复制 `assets/eta_templates/` 里 14 个 `Eta*` 类并替换占位符
→ 落 8 处图标接管与其余 7 类补丁 → 汇编（`fail=0` 才继续）→ 只替换 `classes.dex` 重打包
→ 反解校验（14 类 / 8 接管点 / cln / talker 键）→ 打印 sha256 与完整符号映射。

回归基准（6.5.0）：手工移植与脚本产出**逐字节一致** —— APK `8d30f1cb…`、dex `1f32cf8a…`。

锚点对不上会明确报错（哪个锚点、几个候选），不会猜着改。若新版方法结构变了，先按报错补锚点，
再对 3 个插入点跑 `reg_free.py` 复核寄存器活跃性。

## 资源

- `scripts/semantic_diff.py`：两个 smali 文件的语义 diff（去行号噪音、解码 `\uXXXX`）。
- `scripts/reg_free.py`：给定文件与行号，列出所在方法内各寄存器在插入点是否空闲。
- `scripts/repack_apk.py`：只替换 `classes.dex` 的重打包。
- `scripts/BuildDex.java` + `scripts/README.md`：smali → dex 全量汇编及编译命令。
- `scripts/hchat_port.py`：**全自动移植**（一条命令，Hchat 场景）。
- `assets/eta_templates/`：14 个 `Eta*` 类模板，用 `{{SETTINGS_UI}}` 之类占位符，由脚本替换。
- `references/case-hchat-647.md`：一次真实移植的完整案例（含 v15 覆盖事故复盘）。
- `references/hchat-porting-playbook.md`：Hchat 场景的默认目录、自动发现规则、补丁清单、符号映射与交付模板（一句话触发时按它补齐输入）。

## 一句话触发（Hchat 场景）

用户只说“把旧版 Hchat 功能移植到新版”时，按 `references/hchat-porting-playbook.md` 执行：

1. 自己扫默认工作目录、认版本、分清“官方新版 / 带补丁旧版 / 历史产物”，不要问用户要路径。
2. 找不到同版本的干净对照时，先用独特字符串与调用点缩小补丁集，并在交付里写明“可能不全”。
3. **只有三种情况才回头问一句**：目录里缺旧版带补丁包、缺新版官方包、或找不到同版本干净对照且用户不能接受不完整补丁集。
4. 会改变外观的补丁（通知文字格式）先确认再动手，其余默认全搬。
5. 交付固定四段：产物与 sha256 / 搬了什么 / 有意没搬与偏离 / 你要实跑验证什么。
