#!/usr/bin/env python3
"""Convert downloaded Sogou plant SCEL dictionaries; Python standard library only.

Usage: python convert.py SOURCE_DIR OUTPUT_DICT OUTPUT_MANIFEST
SOURCE_DIR contains sources.json and scel/<id>.scel.
Fails on truncated or unsupported files instead of silently dropping records.
"""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path


def parse_scel(data):
    if data[:12] != bytes.fromhex('401500004443530101000000'):
        raise ValueError('Unsupported SCEL header')
    groups, expected_words = struct.unpack_from('<II', data, 0x120)
    offset = 0x1540

    def take(size):
        nonlocal offset
        if offset + size > len(data):
            raise ValueError('Truncated SCEL record')
        value = data[offset:offset + size]
        offset += size
        return value

    def u16():
        return struct.unpack('<H', take(2))[0]

    syllables = {}
    for _ in range(struct.unpack('<I', take(4))[0]):
        index, size = u16(), u16()
        syllables[index] = take(size).decode('utf-16le').replace('ü', 'v')
    rows = []
    for _ in range(groups):
        count, size = u16(), u16()
        if size % 2:
            raise ValueError('Invalid pinyin index length')
        indices = struct.unpack('<' + 'H' * (size // 2), take(size))
        code = ' '.join(syllables[i] for i in indices)
        if not re.fullmatch(r'[a-z]+(?: [a-z]+)*', code):
            raise ValueError(f'Invalid pinyin: {code!r}')
        for _ in range(count):
            word = take(u16()).decode('utf-16le')
            take(u16())  # Frequency and reserved fields; use a consistent Rime weight.
            if not word or any(c.isspace() or ord(c) < 32 for c in word):
                raise ValueError(f'Invalid word: {word!r}')
            rows.append((word, code))
    if len(rows) != expected_words or offset != len(data):
        raise ValueError(f'Count/length mismatch: {len(rows)}/{expected_words}, {offset}/{len(data)}')
    return rows


def main():
    source_dir, output_dict, output_manifest = map(Path, sys.argv[1:])
    sources = json.loads((source_dir / 'sources.json').read_text())
    unique = set()
    for source in sources:
        data = (source_dir / 'scel' / (source['id'] + '.scel')).read_bytes()
        rows = parse_scel(data)
        source.update(records=len(rows), sha256=hashlib.sha256(data).hexdigest(),
                      detail_url='https://pinyin.sogou.com/dict/detail/index/' + source['id'])
        unique.update(rows)
    header = '''# Rime dictionary
# encoding: utf-8
# 搜狗植物分类（37 个词库）合并；同词同音去重，保留不同读音。
# 来源、文件校验值与转换说明：others/script/sogou_plants/
# 下载日期：2026-09-21；词条和拼音来自原始 SCEL，未人工逐条校对。
# 原始词库权利归各自作者；不因格式转换而改变授权。
---
name: plants_sogou
version: "2026-09-21"
sort: by_weight
use_preset_vocabulary: false
...
'''
    output_dict.write_text(header + ''.join(f'{w}\t{p}\t100\n' for w, p in sorted(unique, key=lambda r: (r[1], r[0]))), encoding='utf-8')
    manifest = dict(category_url='https://pinyin.sogou.com/dict/cate/index/16',
                    downloaded_on='2026-09-21', source_count=len(sources),
                    original_records=sum(s['records'] for s in sources),
                    unique_records=len(unique), sources=sources)
    output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'sources'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
