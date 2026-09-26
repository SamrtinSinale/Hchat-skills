#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""列出某个方法内各寄存器在指定插入点是否空闲 —— 移植补丁前必做的一步。

用法:
    python3 reg_free.py <file.smali> <line>

判定：
    FREE  = 插入点之后第一次出现是“写”，或压根不再出现 → 可当临时寄存器
    LIVE  = 第一次出现是“读” → 它的值还要用，不能覆盖

宽寄存器（long/double 占两格）按操作数位置推断隐含搭档，例如
`move-wide/from16 v24, v10` 同时读 v10 与 v11，`cmp-long vA, vB, vC` 读 vB/vC。
`invoke-*` 的宽参数在 smali 里本来就逐个列出，无需推断。
结果仍是启发式，分支合并点要人工复核。
"""
import sys, re, pathlib

WRITE_MNEMONIC = re.compile(
    r'^(move|const|new-instance|new-array|iget|sget|move-result|array-length|instance-of|'
    r'check-cast|int-to-|long-to-|float-to-|double-to|byte-to-|char-to-|short-to|string-to-|'
    r'neg-|not-|add-|sub-|mul-|div-|rem-|and-|or-|xor-|shl-|shr-|ushr-|rsub-|cmp)')


def split_insn(line):
    m = re.match(r'([a-z0-9/\.\-]+)\s+(.*)$', line.strip())
    return (m.group(1), m.group(2)) if m else (None, '')


def operands(rest):
    return [int(x) for x in re.findall(r'\bv(\d+)\b', rest)]


def wide_regs(mn, ops):
    """这条指令里被当作 64 位值使用的寄存器（低半部分；隐含高位由 touched 补上）。"""
    if not mn or not ops:
        return set()
    if mn.startswith('cmp'):                      # cmp-long vA, vB, vC → vB/vC 宽
        return set(ops[1:])
    if mn.startswith('move-wide'):                # move-wide vA, vB → 两边都宽
        return set(ops[:2])
    if mn.startswith('move-result-wide') or mn.startswith('const-wide'):
        return {ops[0]}
    if re.match(r'^[isa](get|put)-wide', mn):     # iget-wide vA, vB, f → 只有 vA 宽
        return {ops[0]}
    if mn.startswith('neg-') or mn.startswith('not-'):
        return set(ops)
    if re.search(r'-(long|double)(/2addr)?$', mn):
        return set(ops[:2]) if mn.endswith('/2addr') else set(ops)
    if re.search(r'(int|float)-to-(long|double)', mn):
        return {ops[0]}
    if re.search(r'(long|double)-to-', mn):
        return set(ops[1:])
    if mn.startswith(('shl-', 'shr-', 'ushr-')):
        return set(ops[:2])
    return set()


def touched(line):
    mn, rest = split_insn(line)
    ops = operands(rest)
    regs = set(ops)
    for r in wide_regs(mn, ops):
        regs.add(r + 1)
    return regs, wide_regs(mn, ops)


def wide_dest(mn, ops):
    """宽写目标寄存器的低半部分；不是宽写就返回 None。"""
    if not mn or not ops:
        return None
    if mn.startswith('cmp') or re.search(r'(long|double)-to-(int|float)', mn):
        return None
    if mn.startswith(('iput-wide', 'sput-wide', 'aput-wide')):   # 值是被读的
        return None
    if mn.startswith(('move-wide', 'move-result-wide', 'const-wide', 'iget-wide',
                      'sget-wide', 'aget-wide', 'neg-long', 'neg-double', 'not-long', 'not-double')):
        return ops[0]
    if re.search(r'-(long|double)(/2addr)?$', mn):
        return ops[0]
    if re.search(r'(int|float)-to-(long|double)', mn):
        return ops[0]
    return None


def is_write(line, reg):
    mn, rest = split_insn(line)
    ops = operands(rest)
    if not mn:
        return False
    if reg in ops:
        if not WRITE_MNEMONIC.match(mn):
            return False
        if reg in wide_regs(mn, ops) and reg != ops[0]:
            return False            # 宽源操作数 = 读
        return ops[0] == reg
    d = wide_dest(mn, ops)
    return d is not None and reg == d + 1


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    path, line = sys.argv[1], int(sys.argv[2])
    lines = pathlib.Path(path).read_text(errors='replace').splitlines()
    i = line - 1
    s = i
    while s >= 0 and not lines[s].strip().startswith('.method'):
        s -= 1
    e = i
    while e < len(lines) and not lines[e].strip().startswith('.end method'):
        e += 1
    lm = re.search(r'\.locals\s+(\d+)', '\n'.join(lines[s:min(s + 8, e)]))
    n = int(lm.group(1)) if lm else 16
    print('方法: %s' % (lines[s].strip() if s >= 0 else '?'))
    print('范围: %d - %d，.locals %d（可用 v0 - v%d）' % (s + 1, e + 1, n, n - 1))
    print('插入点: 第 %d 行  %s' % (line, lines[i].strip()[:80]))
    print('%-7s %-30s %-44s %s' % ('寄存器', '插入点之前最后一次', '插入点之后第一次', '判定'))
    for r in range(n):
        occ = [j for j in range(s, e) if r in touched(lines[j])[0]]
        b = [x for x in occ if x < i]
        a = [x for x in occ if x >= i]
        bl = '%d %s' % (b[-1] + 1, lines[b[-1]].strip()[:22]) if b else '-'
        if not a:
            al, v = '-', 'FREE(不再出现)'
        else:
            j = a[0]
            al = '%d %s' % (j + 1, lines[j].strip()[:38])
            v = 'FREE(下一次是写)' if is_write(lines[j], r) else 'LIVE(下一次是读)'
        print('v%-6d %-30s %-44s %s' % (r, bl, al, v))
    print('\n提醒：invoke 的 35c 形式只能用 v0-v15；分支合并点要保证类型一致。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
