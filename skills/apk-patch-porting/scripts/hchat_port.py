#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hchat_port.py —— 一条命令把 Hchat 定制补丁移植到新版官方 APK。

用法:
    python3 hchat_port.py <新版官方.apk> [--work DIR] [--out APK]
                          [--templates DIR] [--apktool JAR] [--api 29]

流程: 解码 -> 按锚点自动推导符号映射 -> 落补丁 -> 汇编 -> 重打包 -> 反解校验 -> 打印报告。
原则: 符号一律靠锚点推导，不写死混淆名；任何一步对不上就报错，不猜。
"""
import argparse, json, pathlib, re, shutil, subprocess, sys, hashlib, zipfile

APKTOOL_DEFAULT = '/workspace/apktool/apktool.jar'
TPL_DEFAULT = '/workspace/tools/eta_templates'
BUILDDEX_CLASSES = '/workspace/hchat-compare-KgfMMa/build'
OUTPKG = 'h/Hchat/hooks/items/customnotify'
LOG = []


def esc(s):
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in s)


def log(msg):
    LOG.append(msg)
    print(msg, flush=True)


def die(msg):
    log('!! ' + msg)
    sys.exit(1)


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def read(p):
    return pathlib.Path(p).read_text(errors='replace')


def write(p, t):
    pathlib.Path(p).write_text(t, encoding='utf-8')


def cls_of(path):
    m = re.search(r'^\.class [^\n]*?(L[a-z0-9/$]+;)\s*$', read(path), re.M)
    return m.group(1) if m else None


def patch(path, old, new, tag, expect=1):
    t = read(path)
    n = t.count(old)
    if n != expect:
        die('%s 锚点匹配 %d 次（期望 %d）：%s' % (tag, n, expect, pathlib.Path(path).name))
    write(path, t.replace(old, new, expect))
    log('OK %s' % tag)


def decode(apktool, apk, out):
    if pathlib.Path(out).exists():
        shutil.rmtree(out)
    r = sh(['java', '-jar', apktool, 'd', '-r', '-f', '-o', out, apk])
    if r.returncode != 0 or not (pathlib.Path(out) / 'smali').exists():
        die('apktool 解码失败: %s' % (r.stderr or r.stdout)[-300:])
    n = len(list((pathlib.Path(out) / 'smali').rglob('*.smali')))
    log('解码完成: %s（%d 个 smali）' % (out, n))
    return pathlib.Path(out) / 'smali'


def brief(x):
    if isinstance(x, tuple):
        return ':'.join(str(getattr(y, 'name', y)) for y in x[:2])
    return pathlib.Path(x).name


def one(cands, what):
    if len(cands) != 1:
        die('%s 候选 %d 个（期望 1）：%s' % (what, len(cands), ', '.join(brief(x) for x in cands[:6])))
    return cands[0]


def locate(tree):
    files = list(tree.rglob('*.smali'))
    txt = {f: read(f) for f in files}
    sm = {}

    builder = one([f for f in files if 'Landroid/app/Notification$InboxStyle;' in txt[f]], '通知构建类')
    sm['BUILDER'] = cls_of(builder)

    data = one([f for f in files if 'constructor <init>(Ljava/lang/String;Ljava/lang/String;I'
                'Landroid/graphics/Bitmap;JJJLandroid/app/PendingIntent;I)V' in txt[f]], '通知数据类')
    sm['DATA'] = cls_of(data)

    m = re.search(r'\.method public static (\w+)\(Landroid/content/Context;'
                  r'Landroid/app/NotificationManager;(L[a-z0-9]+;)(L[a-z0-9]+;)\)V', txt[builder])
    if not m:
        die('未找到通知构建入口方法')
    if m.group(3) != sm['DATA']:
        die('构建入口第 4 参数 %s != 数据类 %s' % (m.group(3), sm['DATA']))
    sm['CONFIG'], sm['BUILDER_METHOD'] = m.group(2), m.group(1)
    m2 = re.search(r'\.method public static (\w+)\(Landroid/content/Context;%s%s\)V'
                   % (sm['CONFIG'], sm['DATA']), txt[builder])
    if not m2:
        die('未找到注入目标方法（Context;配置;数据）V')
    sm['ENTRY'] = m2.group(1)

    pub = [f for f in files if 'Landroid/app/Notification;->contentIntent' in txt[f]
           and ('%s-><init>(' % sm['DATA']) in txt[f] and f not in (builder, data)]
    sm['PUBLISH'] = cls_of(one(pub, '发布类'))

    sm['SEARCH'] = cls_of(one([f for f in files if esc('艾特全体') in txt[f]], '搜索索引类'))
    sm['QUICKREAD'] = cls_of(one([f for f in files if 'QuickRead' in txt[f]], '快速已读类'))
    for k in ('BUILDER', 'DATA', 'CONFIG', 'ENTRY', 'PUBLISH', 'SEARCH', 'QUICKREAD'):
        log('  符号 %-11s %s' % (k, sm[k]))
    return sm, files, txt


def locate2(sm, files, txt, tree):
    byclass = {}
    for f in files:
        c = cls_of(f)
        if c:
            byclass[c] = f
    row = []
    for f in files:
        for m in re.finditer(r'^\.method public static (?:final )?(\w+)\(Ljava/lang/String;'
                             r'Ljava/lang/String;(L[a-z0-9]+;)(L[a-z0-9]+;)I\)V$', txt[f], re.M):
            p3 = byclass.get(m.group(2))
            if p3 is not None and '.method public abstract invoke()Ljava/lang/Object;' in txt[p3]:
                row.append((f, m.group(1), m.group(2), m.group(3)))
    if not row:
        die('未找到设置行渲染方法（第 3 参数为无参行点击接口）')
    scored = []
    for f, rm, rc, cp in row:
        n = sum(x.count('%s->%s(' % (cls_of(f), rm)) for x in txt.values())
        scored.append((n, f, rm, rc, cp))
    scored.sort(key=lambda x: -x[0])
    log('  行渲染候选: %s' % ', '.join('%s->%s(%d 处)' % (cls_of(x[1]), x[2], x[0]) for x in scored))
    _, ui, rmethod, rowclick, compose = scored[0]
    sm['SETTINGS_UI'], sm['ROW_METHOD'] = cls_of(ui), rmethod
    sm['ROWCLICK'], sm['COMPOSE'] = rowclick, compose

    sm['LAMBDA'] = cls_of(one([f for f in files if '.method public abstract invoke(Ljava/lang/Object;)'
                               'Ljava/lang/Object;' in txt[f]], 'lambda 接口'))

    unit = None
    for f in files:
        if '.implements %s' % sm['ROWCLICK'] in txt[f]:
            m = re.search(r'sget-object v\d+, (L[a-z0-9]+;)->a:\1', txt[f])
            if m:
                unit = m.group(1)
                break
    if not unit:
        die('未找到 Unit 类')
    sm['UNIT'] = unit

    wrapper = one([f for f in files if '.implements %s' % sm['ROWCLICK'] in txt[f]
                   and 'constructor <init>(%sI)V' % sm['LAMBDA'] in txt[f]], 'lambda 包装类')
    sm['WRAPPER'] = cls_of(wrapper)
    pat = re.compile(r'%s-><init>\(%sI\)V(?:[^\n]*\n){0,6}?[^\n]*invoke-virtual \{[^}]*\}, %s->(\w+)\(Ljava/lang/Object;\)V'
                     % (sm['WRAPPER'], sm['LAMBDA'], sm['COMPOSE']))
    names = {}
    for x in txt.values():
        for m in pat.finditer(x):
            names[m.group(1)] = names.get(m.group(1), 0) + 1
    if not names:
        die('未找到 Compose 注册方法名')
    sm['COMPOSE_PUSH'] = max(names, key=names.get)
    log('  Compose 注册方法: %s（%s）' % (sm['COMPOSE_PUSH'], names))

    cnt = {}
    for m in re.finditer(r'invoke-static \{[^}]*\}, (L[a-z0-9]+;)->(\w+)\(Ljava/lang/CharSequence;\)Z', txt[sm['BUILDER'] and [f for f in files if cls_of(f) == sm['BUILDER']][0]]):
        cnt[m.groups()] = cnt.get(m.groups(), 0) + 1
    if not cnt:
        die('构建类里没有 CharSequence 空判断调用')
    sm['BLANK'], sm['BLANK_M'] = max(cnt, key=cnt.get)

    m = re.search(r'invoke-static \{[^}]*\}, (L[a-z0-9]+;)->(\w+)\(\[Ljava/lang/Object;\)Ljava/util/List;',
                  txt[[f for f in files if cls_of(f) == sm['SEARCH']][0]])
    if not m:
        die('搜索索引类里没有列表构造调用')
    sm['LISTHELPER'], sm['LIST_M'] = m.group(1), m.group(2)

    sm['SETTINGS_PAGE'] = cls_of(one([f for f in files if 'custom_notification_enable' in txt[f]
                                      and ('%s->%s(' % (sm['SETTINGS_UI'], sm['ROW_METHOD'])) in txt[f]], '设置页类'))

    sites = []
    for f in files:
        for l in txt[f].splitlines():
            m = re.match(r'\s*invoke-virtual \{([^}]*)\}, Landroid/app/Notification\$Builder;'
                         r'->setSmallIcon\(I\)Landroid/app/Notification\$Builder;', l)
            if m:
                sites.append((str(f.relative_to(tree)), m.group(1)))
    if len(sites) != 8:
        die('setSmallIcon 接管点 %d 个（期望 8）' % len(sites))
    sm['SITES'] = sites
    for k in ('SETTINGS_UI', 'ROW_METHOD', 'ROWCLICK', 'COMPOSE', 'LAMBDA', 'UNIT', 'WRAPPER',
              'COMPOSE_PUSH', 'BLANK', 'LISTHELPER', 'SETTINGS_PAGE'):
        log('  符号 %-12s %s' % (k, sm[k]))
    return sm


def apply_eta(tree, tpl_dir, sm):
    tpl = pathlib.Path(tpl_dir)
    if not tpl.exists():
        die('模板目录不存在: %s' % tpl)
    subs = {'{{SETTINGS_UI}}': sm['SETTINGS_UI'][1:-1], '{{ROWCLICK}}': sm['ROWCLICK'][1:-1],
            '{{COMPOSE}}': sm['COMPOSE'][1:-1], '{{LAMBDA}}': sm['LAMBDA'][1:-1],
            '{{UNIT}}': sm['UNIT'][1:-1], '{{WRAPPER}}': sm['WRAPPER'][1:-1],
            '{{COMPOSE_PUSH}}': sm['COMPOSE_PUSH']}
    dest = tree / OUTPKG
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(tpl.glob('Eta*.smali')):
        t = read(f)
        for a, b in subs.items():
            t = t.replace(a, b)
        if '{{' in t:
            die('模板 %s 仍有未替换的占位符' % f.name)
        write(dest / f.name, t)
        n += 1
    log('OK 复制 Eta* 类 %d 个（占位符已按推导出的符号替换）' % n)


def apply_icons(tree, sm):
    APPLY = ('Lh/Hchat/hooks/items/customnotify/EtaIconStore;->apply'
             '(Landroid/app/Notification$Builder;I)Landroid/app/Notification$Builder;')
    for rel, regs in sm['SITES']:
        f = tree / rel
        old = ('    invoke-virtual {%s}, Landroid/app/Notification$Builder;'
               '->setSmallIcon(I)Landroid/app/Notification$Builder;' % regs)
        new = '    invoke-static {%s}, %s' % (regs, APPLY)
        patch(f, old, new, '图标接管 %s %s' % (pathlib.Path(rel).name, regs))


def apply_builder(tree, sm):
    Y = tree / (sm['BUILDER'][1:-1] + '.smali')
    B, D, BL, BLM = sm['BUILDER'], sm['DATA'], sm['BLANK'], sm['BLANK_M']

    old1 = r'''    if-eqz v12, :cond_a

    .line 131
    .line 132
    const-string v3, "[\u8868\u60c5]"

    .line 133
    .line 134
    goto/16 :goto_f

    .line 135
    .line 136
    :cond_a
'''
    new1 = ('    if-eqz v12, :cond_40\n\n'
            '    invoke-static {v8}, %s->%s(Ljava/lang/CharSequence;)Z\n\n'
            '    move-result v3\n\n'
            '    if-nez v3, :cond_a\n\n'
            '    .line 131\n    .line 132\n'
            '    const-string v3, "[\\u8868\\u60c5]"\n\n'
            '    .line 133\n    .line 134\n'
            '    goto/16 :goto_f\n\n'
            '    :cond_a\n    move-object v3, v8\n\n'
            '    goto/16 :goto_f\n\n'
            '    .line 135\n    .line 136\n    :cond_40\n') % (BL, BLM)
    patch(Y, old1, new1, 'E1 表情空文本判断')

    old2a = '    .line 610\n    :cond_39\n    move-object v12, v7\n'
    new2a = (r'''    .line 610
    :cond_39
    if-eqz v10, :cond_3f

    const-string v14, "^\\[\\d+\u6761]"

    const-string v15, ""

    invoke-virtual {v10, v14, v15}, Ljava/lang/String;->replaceFirst(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    :cond_3f
    move-object v12, v7
''')
    patch(Y, old2a, new2a, 'E2a 正文前缀裁剪')

    old2b = '\n.end method\n\n.method public static c([Ljava/lang/Object;)Ljava/lang/Object;\n'
    new2b = ('\n.end method\n\n.method public static cln(Ljava/lang/String;Ljava/lang/String;)'
             'Ljava/lang/String;\n    .locals 4\n\n    if-nez p0, :cond_0\n\n    return-object p0\n\n'
             '    :cond_0\n    const-string v0, "^\\\\[\\\\d+\\u6761]"\n\n    const-string v1, ""\n\n'
             '    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->replaceFirst(Ljava/lang/String;'
             'Ljava/lang/String;)Ljava/lang/String;\n\n    move-result-object v0\n\n'
             '    if-eqz p1, :cond_1\n\n    new-instance v1, Ljava/lang/StringBuilder;\n\n'
             '    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V\n\n'
             '    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)'
             'Ljava/lang/StringBuilder;\n\n    const-string v2, ":"\n\n'
             '    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)'
             'Ljava/lang/StringBuilder;\n\n    invoke-virtual {v1}, Ljava/lang/StringBuilder;'
             '->toString()Ljava/lang/String;\n\n    move-result-object v1\n\n'
             '    invoke-virtual {v0, v1}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z\n\n'
             '    move-result v2\n\n    if-eqz v2, :cond_1\n\n'
             '    invoke-virtual {v1}, Ljava/lang/String;->length()I\n\n    move-result v2\n\n'
             '    invoke-virtual {v0, v2}, Ljava/lang/String;->substring(I)Ljava/lang/String;\n\n'
             '    move-result-object v0\n\n    :cond_1\n    return-object v0\n.end method\n\n'
             '.method public static c([Ljava/lang/Object;)Ljava/lang/Object;\n')
    patch(Y, old2b, new2b, 'E2b 新增 cln 方法')

    old2c = ('    iget-object v0, v4, %s->b:Ljava/lang/String;\n\n'
             '    .line 450\n    .line 451\n    const/4 v14, 0x1\n\n'
             '    .line 452\n    if-le v12, v14, :cond_15\n\n'
             '    .line 453\n    .line 454\n'
             '    const-string v7, "^\\\\[\\\\d+\\u6761].*"\n') % D
    new2c = ('    iget-object v0, v4, %s->b:Ljava/lang/String;\n\n'
             '    iget-object v2, v4, %s->a:Ljava/lang/String;\n\n'
             '    invoke-static {v0, v2}, %s->cln(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;\n\n'
             '    move-result-object v0\n\n'
             '    .line 450\n    .line 451\n    const/4 v14, 0x1\n\n'
             '    .line 452\n    if-le v12, v14, :cond_15\n\n'
             '    .line 453\n    .line 454\n'
             '    const-string v7, "^\\\\[\\\\d+\\\\].*"\n') % (D, D, B)
    patch(Y, old2c, new2c, 'E2c 汇总正文 cln + 正则')

    patch(Y, '    const-string v14, "\\u6761]"\n', '    const-string v14, "]"\n', 'E2d 条] -> ]')

    old3 = ('    .line 1006\n    invoke-virtual {v0, v2}, Landroid/app/Notification$InboxStyle;'
            '->setSummaryText(Ljava/lang/CharSequence;)Landroid/app/Notification$InboxStyle;\n\n'
            '    .line 1007\n    .line 1008\n    .line 1009\n    move-result-object v0\n')
    new3 = ('    const/4 v14, 0x3\n\n    if-le v12, v14, :cond_41\n\n'
            '    new-instance v14, Ljava/lang/StringBuilder;\n\n'
            '    invoke-direct {v14}, Ljava/lang/StringBuilder;-><init>()V\n\n'
            '    const-string v9, "["\n\n'
            '    invoke-virtual {v14, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)'
            'Ljava/lang/StringBuilder;\n\n'
            '    invoke-virtual {v14, v12}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;\n\n'
            '    const-string v9, "]"\n\n'
            '    invoke-virtual {v14, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)'
            'Ljava/lang/StringBuilder;\n\n'
            '    invoke-virtual {v14}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n\n'
            '    move-result-object v14\n\n'
            '    invoke-virtual {v0, v14}, Landroid/app/Notification$InboxStyle;->addLine'
            '(Ljava/lang/CharSequence;)Landroid/app/Notification$InboxStyle;\n\n    :cond_41\n')
    patch(Y, old3, new3, 'E3 汇总 [N] 追加行')

    t = read(Y)
    m = re.search(r'\.method public static %s\(Landroid/content/Context;%s%s\)V\n'
                  % (sm['ENTRY'], sm['CONFIG'], D), t)
    if not m:
        die('未找到入口方法 %s' % sm['ENTRY'])
    head = t[:m.end()]
    tail = t[m.end():]
    n = re.search(r'\n(\s*move-object/from16 v2, p2\n)', tail)
    if not n:
        die('入口方法里未找到 move-object/from16 v2, p2')
    inject = ('\n    invoke-static {v0}, Lh/Hchat/hooks/items/customnotify/EtaChatClear;'
              '->ensure(Landroid/content/Context;)V\n\n'
              '    sput-object v0, Lh/Hchat/hooks/items/customnotify/EtaIconStore;'
              '->ctx:Landroid/content/Context;\n')
    write(Y, head + tail[:n.end(1)] + inject + tail[n.end(1):])
    log('OK E4 注入 EtaChatClear.ensure + ctx（入口方法 %s）' % sm['ENTRY'])


def apply_others(tree, sm):
    B, D, UI, RM, CMP = sm['BUILDER'], sm['DATA'], sm['SETTINGS_UI'], sm['ROW_METHOD'], sm['COMPOSE']

    U = tree / (sm['PUBLISH'][1:-1] + '.smali')
    old5 = ('    iget-object v0, v1, Landroid/app/Notification;->contentIntent:'
            'Landroid/app/PendingIntent;\n\n    .line 704\n')
    new5 = ('    iget-object v0, v1, Landroid/app/Notification;->contentIntent:'
            'Landroid/app/PendingIntent;\n\n'
            '    move-object/from16 v14, v26\n\n    move-object/from16 v15, v25\n\n'
            '    invoke-static {v14, v15}, %s->cln(Ljava/lang/String;Ljava/lang/String;)'
            'Ljava/lang/String;\n\n    move-result-object v26\n\n    .line 704\n') % B
    patch(U, old5, new5, 'E5 发布路径 cln')

    P = tree / (sm['SETTINGS_PAGE'][1:-1] + '.smali')
    lines = read(P).split('\n')
    idx = [i for i, l in enumerate(lines) if re.match(r'\s*const-string v\d+, "custom_notification_enable"', l)]
    if len(idx) != 1:
        die('设置页 custom_notification_enable 匹配 %d 次' % len(idx))
    pat = re.compile(r'\s*invoke-static \{([^}]*)\}, %s->\w+\(F%sII\)V' % (UI, CMP))
    hit = next(((j, pat.match(lines[j])) for j in range(idx[0], min(idx[0] + 90, len(lines))) if pat.match(lines[j])), None)
    if not hit:
        die('设置页未找到行渲染锚点')
    j, m = hit
    regs = [x.strip() for x in m.group(1).split(',')]
    scope = regs[1] if len(regs) > 1 else 'v6'
    lines.insert(j + 1, '\n    invoke-static {%s}, Lh/Hchat/hooks/items/customnotify/'
                        'EtaIconEntry;->addRows(%s)V\n' % (scope, CMP))
    write(P, '\n'.join(lines))
    log('OK E6 设置页插入 addRows（第 %d 行后，scope 寄存器 %s）' % (j + 1, scope))

    Q = tree / (sm['QUICKREAD'][1:-1] + '.smali')
    lines = read(Q).split('\n')
    hits = [i for i, l in enumerate(lines) if l.strip() == 'move v5, v6' and i >= 4
            and any('move/from16 v24, v4' in lines[k] for k in range(i - 6, i))]
    if len(hits) != 1:
        die('快速已读锚点匹配 %d 次（期望 1）' % len(hits))
    lines[hits[0]] = lines[hits[0]].replace('move v5, v6', 'const/4 v5, 0x1')
    write(Q, '\n'.join(lines))
    log('OK E7 快速已读补丁（第 %d 行）' % (hits[0] + 1))

    A = tree / (sm['SEARCH'][1:-1] + '.smali')
    lines = read(A).split('\n')
    idx = [i for i, l in enumerate(lines) if re.match(r'\s*const-string v\d+, "custom_notification"$', l)]
    if len(idx) != 1:
        die('搜索索引 custom_notification 匹配 %d 次' % len(idx))
    call = next((j for j in range(idx[0], min(idx[0] + 220, len(lines)))
                 if re.match(r'\s*invoke-static \{[^}]*\}, %s->%s\(\[Ljava/lang/Object;\)Ljava/util/List;'
                             % (sm['LISTHELPER'], sm['LIST_M']), lines[j])), None)
    if call is None:
        die('搜索索引未找到列表构造调用')
    res = next((j for j in range(call, min(call + 12, len(lines))) if 'move-result-object v0' in lines[j]), None)
    if res is None:
        die('搜索索引未找到 move-result-object v0')
    block = ['', '    new-instance v13, Ljava/util/ArrayList;', '',
             '    invoke-direct {v13, v0}, Ljava/util/ArrayList;-><init>(Ljava/util/Collection;)V', '',
             '    const-string v1, "%s"' % esc('自定义图标'), '',
             '    invoke-virtual {v13, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z', '',
             '    const-string v1, "%s"' % esc('恢复默认图标'), '',
             '    invoke-virtual {v13, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z', '',
             '    move-object v0, v13', '']
    lines[res + 1:res + 1] = block
    write(A, '\n'.join(lines))
    log('OK E8 搜索索引追加两项（第 %d 行后）' % (res + 1))


def version_of(tree):
    for f in tree.rglob('*.smali'):
        m = re.search(r'u6a21\\u5757\\u7248\\u672c: ([0-9.]+ \([0-9]+\))', read(f))
        if m:
            return m.group(1)
    return 'unknown'


def build_dex(tree, out, api, apktool):
    r = sh(['java', '-cp', apktool + ':' + BUILDDEX_CLASSES, 'BuildDex', str(tree), str(out), str(api)])
    for l in [x for x in r.stdout.splitlines() if x.strip()][-3:]:
        log('  ' + l)
    if 'fail=0' not in r.stdout or not pathlib.Path(out).exists():
        die('汇编失败：%s' % (r.stdout or r.stderr)[-400:])
    return out


def repack(src, dex, out):
    data = open(dex, 'rb').read()
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    n = 0
    for it in zin.infolist():
        payload = data if it.filename == 'classes.dex' else zin.read(it.filename)
        n += it.filename == 'classes.dex'
        zi = zipfile.ZipInfo(it.filename, date_time=it.date_time)
        zi.compress_type, zi.external_attr = it.compress_type, it.external_attr
        zi.internal_attr, zi.create_system = it.internal_attr, it.create_system
        zout.writestr(zi, payload)
    zout.close()
    zin.close()
    if n != 1:
        die('原包里 classes.dex 条目数 %d' % n)
    log('重打包完成: %s（%d 字节）' % (out, pathlib.Path(out).stat().st_size))
    return out


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def verify(apktool, apk, work, sm):
    tree = decode(apktool, apk, str(work / 'verify'))
    pkg = tree / OUTPKG
    n = len(list(pkg.glob('Eta*.smali'))) if pkg.exists() else 0
    if n != 14:
        die('成品里 Eta* 类 %d 个（期望 14）' % n)
    sites = sum(1 for f in tree.rglob('*.smali') if 'EtaIconStore;->apply' in read(f))
    if sites != 8:
        die('成品里图标接管点 %d 个（期望 8）' % sites)
    left = [str(f.relative_to(tree)) for f in tree.rglob('*.smali')
            if 'Builder;->setSmallIcon(I)' in read(f) and 'EtaIconStore' not in str(f)]
    if left:
        die('成品里仍有未接管的 setSmallIcon: %s' % left)
    allt = ''.join(read(f) for f in tree.rglob('*.smali'))
    defs = allt.count('.method public static cln(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;')
    calls = allt.count('->cln(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;')
    if defs != 1 or calls < 2:
        die('cln 方法或调用点异常（定义 %d，调用 %d）' % (defs, calls))
    log('  cln: 定义 %d，调用 %d' % (defs, calls))
    b = read(tree / (sm['BUILDER'][1:-1] + '.smali'))
    if b.count('hchat_custom_notification_talker') != 3:
        die('talker 键出现次数异常（应为 3）')
    log('校验通过: 14 个 Eta 类 / 8 个接管点 / cln 完整 / talker 键未被动过')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apk')
    ap.add_argument('--work', default='/workspace/port_out')
    ap.add_argument('--out')
    ap.add_argument('--templates', default=TPL_DEFAULT)
    ap.add_argument('--apktool', default=APKTOOL_DEFAULT)
    ap.add_argument('--api', default='29')
    ap.add_argument('--no-verify', action='store_true')
    a = ap.parse_args()
    if not pathlib.Path(a.apk).exists():
        die('找不到 APK: %s' % a.apk)
    work = pathlib.Path(a.work)
    work.mkdir(parents=True, exist_ok=True)

    log('=== 1/6 解码 %s' % a.apk)
    tree = decode(a.apktool, a.apk, str(work / 'new'))
    ver = version_of(tree)
    log('=== 2/6 推导符号映射（版本 %s）' % ver)
    sm, files, txt = locate(tree)
    locate2(sm, files, txt, tree)
    log('=== 3/6 落补丁')
    apply_eta(tree, a.templates, sm)
    apply_icons(tree, sm)
    apply_builder(tree, sm)
    apply_others(tree, sm)
    log('=== 4/6 汇编')
    dex = build_dex(tree, work / 'classes_eta.dex', a.api, a.apktool)
    log('=== 5/6 重打包')
    out = a.out or str(work / ('Hchat_eta_%s_unsigned.apk' % ver.split(' ')[0]))
    repack(a.apk, dex, out)
    if not a.no_verify:
        log('=== 6/6 反解校验')
        verify(a.apktool, out, work, sm)
    log('')
    log('完成 —— 产物: %s' % out)
    log('  APK sha256: %s' % sha(out))
    log('  dex sha256: %s' % sha(dex))
    log('  符号映射: %s' % json.dumps({k: v for k, v in sm.items() if k != 'SITES'}, ensure_ascii=False))
    log('提醒: 新版本若方法结构有变，先对 3 个插入点跑 reg_free.py 复核寄存器活跃性。')


if __name__ == '__main__':
    main()
