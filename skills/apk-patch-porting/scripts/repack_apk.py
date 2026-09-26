#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只替换 classes.dex 的重打包：其余 zip 条目（res/lib/assets/META-INF 等）逐条原样复制。

用法:
    python3 repack_apk.py <原包.apk> <新的classes.dex> <输出.apk>

注意：
  - 输出包不会有签名（原包的 v2/v3 签名块随重打包失效），需要用户自行签名；
  - 不要覆盖原包，换新文件名。
"""
import sys, zipfile, hashlib, os


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 1
    src, dex, dst = sys.argv[1:4]
    data = open(dex, 'rb').read()
    zin = zipfile.ZipFile(src, 'r')
    zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
    replaced = 0
    for it in zin.infolist():
        if it.filename == 'classes.dex':
            payload = data
            replaced += 1
            print('classes.dex: %d -> %d 字节' % (it.file_size, len(payload)))
        else:
            payload = zin.read(it.filename)
        zi = zipfile.ZipInfo(it.filename, date_time=it.date_time)
        zi.compress_type = it.compress_type
        zi.external_attr = it.external_attr
        zi.internal_attr = it.internal_attr
        zi.create_system = it.create_system
        zout.writestr(zi, payload)
    zout.close()
    zin.close()
    print('替换条目数:', replaced)
    print('输出:', dst, os.path.getsize(dst))
    print('apk sha256 :', hashlib.sha256(open(dst, 'rb').read()).hexdigest())
    print('dex sha256 :', hashlib.sha256(data).hexdigest())
    return 0


if __name__ == '__main__':
    sys.exit(main())
