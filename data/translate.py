#!/usr/bin/env python3
"""Übersetzt neue (fehlende) Aufgabentexte automatisch mit der Claude-API und baut die Daten neu.
Braucht die Umgebungsvariable ANTHROPIC_API_KEY. Ohne Key passiert nichts (Texte bleiben Englisch)."""
import json, os, re, subprocess, sys
from urllib.request import Request, urlopen

HERE = os.path.dirname(os.path.abspath(__file__))
MISSING = os.path.join(HERE, 'missing.json')
TRANS = os.path.join(HERE, 'translations.json')
MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-5-5')

def main():
    if not os.path.exists(MISSING): return
    miss = json.load(open(MISSING))
    items = {f'd{i}': t for i, t in enumerate(miss['desc'])}
    items.update({f'g{k}': v for k, v in miss['gdesc'].items()})
    if not items: print('Keine fehlenden Übersetzungen.'); return
    key = os.environ.get('ANTHROPIC_API_KEY')
    if not key: print(f'{len(items)} Texte ohne Übersetzung, aber kein ANTHROPIC_API_KEY gesetzt – bleiben Englisch.'); return
    tr = json.load(open(TRANS))
    examples = list(tr['desc'].items())[:12]
    prompt = ('Übersetze diese Aufgabentexte des Spiels EA SPORTS FC 27 (Ultimate Team) ins Deutsche, für einen Jugendlichen. '
        'Nutze die gewohnte Spielterminologie: Startelf, Squad Battles, Rivals, Champions, Live Events, Rush, Transfermarkt, Münzen, '
        'SBC (Spielerbau-Aufgabe), Vorlage, Chemie, Erstbesitz (First Owned), Verbrauchs-Item. Eigennamen, Liga- und Vereinsnamen und '
        'Modusnamen bleiben unverändert. Zahlen exakt übernehmen. Antworte NUR mit einem JSON-Objekt {schlüssel: deutscher Text}.\n\n'
        'Beispiele für den Stil (Englisch -> Deutsch):\n' + json.dumps(dict(examples), ensure_ascii=False, indent=1) +
        '\n\nZu übersetzen:\n' + json.dumps(items, ensure_ascii=False, indent=1))
    body = json.dumps({'model': MODEL, 'max_tokens': 16000, 'messages': [{'role': 'user', 'content': prompt}]}).encode()
    req = Request('https://api.anthropic.com/v1/messages', data=body, headers={
        'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    with urlopen(req, timeout=300) as r:
        out = json.load(r)
    text = ''.join(b.get('text', '') for b in out['content'])
    m = re.search(r'\{.*\}', text, re.S)
    res = json.loads(m[0])
    n = 0
    for k, v in res.items():
        if k in items and isinstance(v, str) and v.strip():
            if k.startswith('d'): tr['desc'][items[k]] = v.strip()
            else: tr['gdesc'][k[1:]] = v.strip()
            n += 1
    json.dump(tr, open(TRANS, 'w'), ensure_ascii=False, indent=1)
    print(f'{n} Texte übersetzt.')
    subprocess.run([sys.executable, os.path.join(HERE, 'build.py')], check=True)

if __name__ == '__main__':
    try: main()
    except Exception as e:
        print('Übersetzung fehlgeschlagen (Texte bleiben Englisch):', e)
