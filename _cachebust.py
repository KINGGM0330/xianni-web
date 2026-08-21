#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_破快取版本號.py —— 自動更新 index.html 裡每個 <script src="assets/xxx.js?v=…"> 的版本號

由 `更新官網.bat` 在 git add 之前自動呼叫，平常不用自己跑。

★ 這在解決什麼問題（2026-08-22 被咬過）

index.html 是這樣載入 JS 的：

    <script src="assets/game-data.js?v=20260819"></script>

`?v=` 後面那串**對伺服器完全沒有意義**，它唯一的用途是「讓網址看起來不一樣」。
瀏覽器與 Cloudflare 都是**用網址當快取的鑰匙**：

    網址一樣  ⇒ 不管檔案內容改成什麼，都直接吐舊的快取
    網址不同  ⇒ 才會真的去重新下載

所以「改了 assets\\*.js 卻沒改 ?v=」的結果是：檔案確實推上 GitHub 了、
Cloudflare 也確實部署了，**但玩家打開官網看到的還是舊資料**，
而且怎麼重整都一樣 —— 看起來就像更新完全沒生效。

⇒ 這支改用**檔案內容的 MD5 前 8 碼**當版本號，而不是日期：
   內容有變 ⇒ 雜湊變 ⇒ 網址變 ⇒ 一定會重新下載
   內容沒變 ⇒ 雜湊不變 ⇒ 網址不變 ⇒ 沿用快取（正確且省流量）
   完全不用記得手動改，也不會「同一天改兩次結果第二次沒生效」。
"""
import os, re, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
IDX = os.path.join(HERE, 'index.html')


def main():
    if not os.path.exists(IDX):
        print('  [skip] 找不到 index.html')
        return 0

    t = open(IDX, encoding='utf-8').read()
    orig = t
    changed, kept, missing = [], [], []

    def repl(m):
        rel, ver = m.group(1), m.group(2)
        f = os.path.join(HERE, rel.replace('/', os.sep))
        if not os.path.exists(f):
            missing.append(rel)
            return m.group(0)
        h = hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]
        if h == ver:
            kept.append(rel)
        else:
            changed.append('%s  %s -> %s' % (rel, ver, h))
        return 'src="%s?v=%s"' % (rel, h)

    t = re.sub(r'src="(assets/[^"?]+\.js)\?v=([^"]*)"', repl, t)

    if t == orig:
        print('  版本號都是最新的（%d 支）' % len(kept))
        return 0

    data = t.encode('utf-8')        # ★ 先 encode，過了才開檔
    open(IDX, 'wb').write(data)     # ★ 兩句分開，別合成一句（合起來會先清空檔案）

    chk = open(IDX, encoding='utf-8').read()
    if len(chk) < 10 * 1024:
        print('  [ERROR] index.html 寫壞了，只剩 %d bytes' % len(chk))
        return 1

    for c in changed:
        print('  更新  ' + c)
    for x in missing:
        print('  [警告] 找不到檔案，版本號沒動：' + x)
    return 0


if __name__ == '__main__':
    sys.exit(main())
