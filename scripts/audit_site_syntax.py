import os
import re

manual_dirs = ['src/content/manual', 'src/data']
dollar_re = re.compile(r'(?<!\\)\$([^$\n]+)\$')
forbidden_words = ['审美', '文献案例 1', '全息', '黄金三联', '闭环', '审计']

findings = []

for mdir in manual_dirs:
    for root, _, files in os.walk(mdir):
        for f in sorted(files):
            if not f.endswith('.md'):
                continue
            p = os.path.join(root, f)
            in_code_block = False
            with open(p, 'r', encoding='utf-8') as fh:
                for lnum, line in enumerate(fh, 1):
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        continue
                    clean_line = re.sub(r'`[^`]*`', '', line)
                    m = dollar_re.search(clean_line)
                    if m:
                        findings.append((p, lnum, 'RAW_DOLLAR', m.group(0), line.strip()))
                    for w in forbidden_words:
                        if w in clean_line:
                            findings.append((p, lnum, 'FORBIDDEN_WORD', w, line.strip()))

if findings:
    print(f'Found {len(findings)} issues:')
    for item in findings:
        print(f'{item[0]}:{item[1]} [{item[2]}] {item[3]} -> {item[4]}')
else:
    print('ALL CLEAR! 0 raw dollars, 0 forbidden words found in manual md files.')
