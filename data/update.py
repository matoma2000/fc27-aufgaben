#!/usr/bin/env python3
"""Holt die aktuellen Aufgaben von fcdata.io, baut js/data.js neu und meldet fehlende Übersetzungen.
Aufruf:  python3 data/update.py
"""
import json, os, re, subprocess, sys
from html.parser import HTMLParser
from urllib.request import Request, urlopen

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://fcdata.io'
VOID = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'wbr', 'col', 'area', 'base', 'embed', 'param', 'track'}


class N:
    def __init__(s, tag, attrs, parent):
        s.tag, s.a, s.parent, s.kids, s.t = tag, dict(attrs), parent, [], []
    def text(s):
        return ''.join(x if isinstance(x, str) else x.text() for x in s.kids)
    def walk(s):
        for k in s.kids:
            if isinstance(k, N):
                yield k
                yield from k.walk()
    def find(s, tag=None, **kw):
        for n in s.walk():
            if (tag is None or n.tag == tag) and all(n.a.get(k.replace('_', '-')) == v for k, v in kw.items()):
                return n
    def anc(s):
        p = s.parent
        while p:
            yield p
            p = p.parent


class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.root = N('root', [], None); s.cur = s.root
    def handle_starttag(s, tag, attrs):
        n = N(tag, [(k, v or '') for k, v in attrs], s.cur); s.cur.kids.append(n)
        if tag not in VOID: s.cur = n
    def handle_startendtag(s, tag, attrs):
        s.cur.kids.append(N(tag, [(k, v or '') for k, v in attrs], s.cur))
    def handle_endtag(s, tag):
        p = s.cur
        while p and p.tag != tag: p = p.parent
        if p and p.parent: s.cur = p.parent
    def handle_data(s, d):
        s.cur.kids.append(d)


def fetch(path):
    req = Request(BASE + path, headers={'User-Agent': 'Mozilla/5.0 (FC27-Aufgaben-Companion update)'})
    with urlopen(req, timeout=60) as r:
        html = r.read().decode('utf-8', 'replace')
    p = P(); p.feed(html)
    return p.root


def absu(u):
    return BASE + u if u and not u.startswith('http') else u


def leaf_text(n):
    return [e.text().strip() for e in n.walk() if e.tag in ('div', 'span') and not any(isinstance(k, N) for k in e.kids) and e.text().strip()]


def rewards(root):
    res = []
    for a in root.walk():
        if a.tag == 'a' and '/fc27/players/' in a.a.get('href', ''):
            label = ''
            for up in a.anc():
                it = next((x for x in up.walk() if x.tag == 'a' and x.a.get('href', '').startswith('/fc27/items/')), None)
                if it: label = it.text().strip(); break
            shell = next((e for e in a.walk() if '--fut-shell' in e.a.get('style', '')), None)
            imgs = [absu(i.a.get('src', '')) for i in a.walk() if i.tag == 'img']
            res.append(dict(type='player', bg=imgs[0] if imgs else None, face=imgs[1] if len(imgs) > 1 else None,
                            badges=[s for s in imgs[2:] if 'fut-objective' not in s], txt=leaf_text(a), label=label,
                            style=shell.a['style'] if shell else ''))
    for p in root.walk():
        if p.tag != 'p': continue
        if any(x.tag == 'a' and '/fc27/players/' in x.a.get('href', '') for x in p.anc()): continue
        if any(x.tag == 'a' and x.a.get('href', '').startswith('/fc27/items/') for x in p.walk()): continue
        box = p.parent
        im = next((k for k in (box.parent.kids if box.parent else []) if isinstance(k, N) and k.tag == 'img'), None) or box.find('img')
        res.append(dict(type='item', text=p.text().strip(), icon=absu(im.a.get('src')) if im else None, inline=[]))
    return res


def parse_group(href, status):
    root = fetch(href)
    main = root.find('main') or root
    h1 = main.find('h1')
    badges = [b.text().strip() for b in main.walk() if b.a.get('data-slot') == 'badge']
    meta = re.sub(r'\s+', ' ', h1.parent.text())
    ends = (re.search(r'Ends\s*(\d+ \w+ \d{4}, \d+:\d+)', meta) or [None, None])[1]
    starts = (re.search(r'Starts\s*(\d+ \w+ \d{4}, \d+:\d+)', meta) or [None, None])[1]
    cards = [c for c in main.walk() if c.a.get('data-slot') == 'card']
    grp = next((c for c in cards if c.a.get('aria-labelledby') == 'group-rewards-title'), None)
    nxt = h1.parent.kids[h1.parent.kids.index(h1) + 1] if h1 in h1.parent.kids else None
    tasks = []
    for c in cards:
        if not c.a.get('id', '').startswith('task-'): continue
        cc = next(k for k in c.kids if isinstance(k, N) and k.a.get('data-slot') == 'card-content')
        desc = next((k.text().strip() for k in cc.kids if isinstance(k, N) and k.tag == 'p'), '')
        title = c.find('h3').text().strip()
        rw = [r for r in rewards(cc) if not (r['type'] == 'item' and r['text'] == desc)]
        tasks.append(dict(n=c.find('span').text().strip(), title=title, desc=desc, rewards=rw))
    return dict(id=re.search(r'/objectives/(\d+)', href)[1], status=status, cat=badges[1] if len(badges) > 1 else '',
                title=h1.text().strip(), desc=nxt.text().strip() if isinstance(nxt, N) else '', ends=ends, starts=starts,
                rewards=rewards(grp) if grp else [], tasks=tasks)


def main():
    listing = fetch('/objectives/')
    seen, todo = set(), []
    for a in listing.walk():
        m = re.match(r'/objectives/(\d+)-', a.a.get('href', '')) if a.tag == 'a' else None
        if not m or m[1] in seen: continue
        seen.add(m[1])
        status = None
        for up in a.anc():
            t = up.text().strip()
            mm = re.match(r'(Active|Upcoming|Expired)', t)
            if mm and len(t) < 4000: status = mm[1]; break
        todo.append((a.a['href'], status))
    wanted = [(h, s) for h, s in todo if s != 'Expired']
    print(f'{len(todo)} Gruppen gefunden, {len(wanted)} aktiv/kommend – lade Details …')
    out = []
    for i, (h, s) in enumerate(wanted, 1):
        try:
            out.append(parse_group(h, s))
        except Exception as e:
            print('  Fehler bei', h, e, file=sys.stderr)
        print(f'  {i}/{len(wanted)}', end='\r')
    if not out:
        sys.exit('Keine Daten erhalten – nichts geändert.')
    json.dump(out, open(os.path.join(HERE, 'clean.json'), 'w'), ensure_ascii=False)
    print(f'\n{len(out)} Gruppen, {sum(len(g["tasks"]) for g in out)} Aufgaben gespeichert. Baue Daten …')
    subprocess.run([sys.executable, os.path.join(HERE, 'build.py')], check=True)


if __name__ == '__main__':
    main()
