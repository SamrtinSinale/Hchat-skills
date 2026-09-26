# scripts 说明

所有脚本在 **Linux(Debian) 工具环境**里跑（Android 环境没有 python3/java 工具链）。

## BuildDex.java — smali 树全量汇编成 dex

```bash
# apktool.jar 提供 smali/dexlib2 依赖，常见位置见下
javac -cp /workspace/apktool/apktool.jar -d build BuildDex.java
java  -cp /workspace/apktool/apktool.jar:build BuildDex <smali_root> <out.dex> [api]
```

- `apktool.jar` 通常在 `/workspace/apktool/apktool.jar` 或 `/data/local/tmp/apktool.jar`；
  找不到就先用 `find / -maxdepth 4 -name 'apktool*.jar'` 搜，仍没有就提示用户在
  “Linux 工具环境”里安装 **APK 分析**。
- **必须 `fail=0` 才继续**；有 FAIL/ERR 就回去改 smali（常见：标签重名、寄存器越界）。
- apktool 本身不支持回编译，这个脚本用它的 smali 库绕过该限制，只做汇编。

## repack_apk.py — 只替换 classes.dex

```bash
python3 repack_apk.py <原包.apk> <新的classes.dex> <输出.apk>
```

## 校验三件套

```bash
java -jar /workspace/apktool/apktool.jar d -r -f -o verify <输出.apk>   # 反解，验证 dex 可解析
diff -rq <上一版smali树> verify/smali                                  # 应只有预期文件不同
/apex/com.android.art/bin/dex2oat --dex-file=classes.dex --oat-file=out.oat \
    --instruction-set=arm64 --compiler-filter=verify                    # ART 校验（Android 环境里跑）
```

## semantic_diff.py / reg_free.py

```bash
python3 semantic_diff.py old.smali new.smali        # 语义 diff
python3 semantic_diff.py old_tree new_tree --tree   # 整棵树
python3 reg_free.py y21.smali 9817                  # 插入点寄存器活跃性
```
