#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语义 diff：去掉 .line/.source/.local 噪音、把标签重编号、解码 \\uXXXX 后再 diff。

用法:
    python3 semantic_diff.py <old.smali> <new.smali> [--context 3]
    python3 semantic_diff.py <old_tree> <new_tree> --tree

为什么需要它：直接 diff 两个 apktool 解码结果会被标签编号、.line 数量、字段初值写法
（`= false` vs `= null`）淹没；语义 diff 才能看清真正的代码改动。
"""
import sys, re, difflib, pathlib

SKIP_PREFIX = ('#', '.line ', '.source ', '.param ', '.end param', '.local ',
               '.end local ', '.restart local', '.prologue', '.epilogue')


def clean(text):
    out, labels = [], {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(SKIP_PREFIX):
            continue
        if s.startswith('.method'):
            labels = {}
        s = re.sub(r':(?:cond|goto|try_start|try_end|catch|catchall|pswitch|sswitch|array)_[a-z0-9_]+',
                   lambda m: labels.setdefault(m[0], ':L%d' % len(labels)), s)
        s = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), s)
        out.append(s)
    return out


def diff_files(a, b, context=3):
    return list(difflib.unified_diff(clean(pathlib.Path(a).read_text(errors='replace')),
                                     clean(pathlib.Path(b).read_text(errors='replace')),
                                     fromfile=str(a), tofile=str(b), lineterm='', n=context))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ctx = 3
    if '--context' in sys.argv:
        ctx = int(sys.argv[sys.argv.index('--context') + 1])
    if len(args) != 2:
        print(__doc__)
        return 1
    a, b = args
    if pathlib.Path(a).is_dir():
        pa, pb = pathlib.Path(a), pathlib.Path(b)
        fa = {str(f.relative_to(pa)) for f in pa.rglob('*.smali')}
        fb = {str(f.relative_to(pb)) for f in pb.rglob('*.smali')}
        only_a, only_b = sorted(fa - fb), sorted(fb - fa)
        print('只在前者存在 %d 个：%s' % (len(only_a), ', '.join(only_a[:20])))
        print('只在后者存在 %d 个：%s' % (len(only_b), ', '.join(only_b[:20])))
        n = 0
        for rel in sorted(fa & fb):
            d = diff_files(pa / rel, pb / rel, ctx)
            if d:
                n += 1
                print('\n######## %s (%d 行差异)' % (rel, len(d)))
                print('\n'.join(d))
        print('\n共有且内容不同：%d 个' % n)
    else:
        print('\n'.join(diff_files(a, b, ctx)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
