import json, re, os, hashlib, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, 'data', 'clean.json')))

# ---- Beschreibungen ------------------------------------------------------
TR = json.load(open(os.path.join(ROOT, 'data', 'translations.json')))
DE = TR['desc']; GDESC = TR['gdesc']
MISSING = {'desc': [], 'gdesc': {}}

# ---- Gruppen-Titel -------------------------------------------------------
GT = {
 "Road to the Knockouts: Group Stage": "Road to the Knockouts: Gruppenphase",
 "Weekly Objectives": "Wochenaufgaben",
 "Daily Objectives": "Tagesaufgaben",
 "Weekly Rush Points": "Wöchentliche Rush-Punkte",
 "Bundesliga x Playmobil Kit": "Bundesliga x Playmobil Trikot",
 "Season 2 Daily Knockout Tournament Weekly Play Completionist": "Season 2 Daily Knockout Tournament: Wochenspiel-Komplettierung",
 "Season 2 Daily Knockout Tournament Weekly Play": "Season 2 Daily Knockout Tournament: Wochenspiel",
 "FC Heritage Circuit Completionist": "FC Heritage Circuit: Komplettierung",
 "Gallery Foundations": "Gallery-Grundlagen",
 "Claim the Armband": "Hol dir die Kapitänsbinde",
 "Ted Lasso's Masterclass": "Ted Lassos Meisterklasse",
 "Champions Milestone": "Champions-Meilenstein",
 "Live Events Milestone": "Live-Events-Meilenstein",
 "Squad Building Milestone": "Spielerbau-Meilenstein",
 "Gallery Milestone": "Gallery-Meilenstein",
 "Champions Mastery": "Champions-Meisterschaft",
 "Squad Building Mastery": "Spielerbau-Meisterschaft",
 "Total Football": "Totaler Fußball",
 "Transfer Market Mastery": "Transfermarkt-Meisterschaft",
 "Squad Battles Milestone": "Squad-Battles-Meilenstein",
 "Rivals Mastery": "Rivals-Meisterschaft",
 "Live Events Mastery": "Live-Events-Meisterschaft",
 "Goals and Assist Mastery": "Tore-und-Vorlagen-Meisterschaft",
 "Rivals Milestone": "Rivals-Meilenstein",
 "Co-Op Milestone": "Co-Op-Meilenstein",
 "Squad Battles Mastery": "Squad-Battles-Meisterschaft",
 "Moments Stars Milestone": "Moments-Sterne-Meilenstein",
 "First Owned Mastery": "Erstbesitz-Meisterschaft",
 "Rush Milestone": "Rush-Meilenstein",
 "Transfer Market Milestone": "Transfermarkt-Meilenstein",
 "Draft Milestone": "Draft-Meilenstein",
}
CAT = {"Campaigns": "Kampagnen", "FC Pro": "FC Pro", "Foundations": "Grundlagen", "Live Events": "Live Events",
       "Mastery": "Meisterschaft", "Milestones": "Meilensteine", "Seasonal": "Saison"}

# ---- Aufgaben-Titel ------------------------------------------------------
def fmt(n):
    return n.replace(',', '.')

TT_EXACT = {
 "Score in 14": "Tor in 14 Spielen", "Score in 10": "Tor in 10 Spielen", "Score in 4": "Tor in 4 Spielen",
 "Score in 50": "Tor in 50 Spielen", "Score in 12": "Tor in 12 Spielen", "Score in 5": "Tor in 5 Spielen",
 "Triple Perfect": "Dreimal perfekt", "Double Perfect": "Zweimal perfekt", "Perfect Round": "Perfekte Runde",
 "Score 1": "Erzielle 1", "Legendary": "Legendär", "World Class": "Weltklasse", "Professional": "Profi",
 "Score 10": "Erzielle 10", "Win 10": "Gewinne 10", "Play 10": "Spiele 10", "Buy 10": "Kaufe 10", "List 10": "Stelle 10 ein",
 "Watch 60 minutes": "60 Minuten zuschauen", "Watch 15 minutes": "15 Minuten zuschauen", "Play 1": "Spiele 1",
 "Scoring Success": "Torerfolg", "Score 4": "Erzielle 4", "Play 5": "Spiele 5", "S Rank": "Rang S", "A Rank": "Rang A",
 "B Rank": "Rang B", "C Rank": "Rang C", "D Rank": "Rang D", "Assist in 2": "Vorlage in 2 Spielen", "Play 2": "Spiele 2",
 "5 Completions": "5× abgeschlossen", "4 Completions": "4× abgeschlossen", "3 Completions": "3× abgeschlossen",
 "2 Completions": "2× abgeschlossen", "1 Completion": "1× abgeschlossen",
 "Win Tournament Five Times": "Turnier fünfmal gewinnen", "Win Tournament": "Turnier gewinnen",
 "Score 15": "Erzielle 15", "Play 20": "Spiele 20", "Play 15": "Spiele 15", "Score 20": "Erzielle 20", "Play 50": "Spiele 50",
 "FC Heritage Circuit World Class Challenge": "Heritage Circuit: Weltklasse-Aufgabe",
 "FC Heritage Circuit Professional Challenge": "Heritage Circuit: Profi-Aufgabe",
 "FC Heritage Circuit Semi-Pro Challenge": "Heritage Circuit: Semi-Pro-Aufgabe",
 "Level Up": "Level-Up", "Three of a Kind": "Drei Gleiche", "Set the Standard": "Setz den Standard",
 "Set in Motion": "In Bewegung setzen", "Make the Grade": "Note erreichen",
 "Be a Goldfish": "Sei ein Goldfisch", "Unselfish Play": "Uneigennütziges Spiel", "Football is Life": "Fußball ist Leben",
 "Targeted Investments": "Gezielte Investitionen", "Trading Up": "Aufsteigen durch Handeln",
 "Players Come, Players Go": "Spieler kommen, Spieler gehen", "A Test of Skill": "Ein Test deines Könnens",
 "Finding the Net": "Ins Netz treffen", "Hit the Pitch": "Ab auf den Platz", "Lace 'em Up": "Schuhe schnüren",
 "Consumable Craze": "Verbrauchs-Fieber", "Style and Substance": "Stil und Substanz", "Form Fitting": "Passende Formation",
 "For Club and Crest": "Für Club und Wappen", "Unlikely Hero": "Unerwarteter Held",
 "Pursuit of Excellence": "Streben nach Exzellenz", "Elite Pedigree": "Elite-Stammbaum", "Defensive Steel": "Stahlharte Abwehr",
 "Futbol Aşkına": "Futbol Aşkına", "Best of the Best": "Das Beste vom Besten",
 "Madrid After Midnight": "Madrid nach Mitternacht", "MLS After Dark": "MLS nach Einbruch der Dunkelheit",
 "French Fright": "Französischer Schrecken", "Scream in Serie A": "Schrei in der Serie A", "Heritage Champion": "Heritage-Champion",
 "Thunder Final": "Donner-Finale", "Ligue 1 Finest": "Das Beste der Ligue 1", "Oranje Legacy": "Oranje-Vermächtnis",
 "Madrid Royalty": "Madrider Königshaus", "French Thrill": "Französischer Nervenkitzel", "Serie A after Dark": "Serie A nach Einbruch der Dunkelheit",
 "Premier Pride": "Premier-Stolz", "French Connection": "French Connection", "Belgian Tower": "Belgischer Turm",
 "Three Lions Legacy": "Three-Lions-Vermächtnis", "Bundesliga Backbone": "Rückgrat der Bundesliga", "Bavarian Thunder": "Bayerischer Donner",
 "Paris Power Surge": "Pariser Kraftschub", "Bernabéu Thunder": "Bernabéu-Donner", "Los Campeones": "Los Campeones", "El Tri": "El Tri",
 "El Matón del área": "El Matón del área", "Movember Animated TIFO": "Animiertes Movember-Tifo", "Movember TIFO": "Movember-Tifo",
 "Biscuits with the Boss": "Kekse mit dem Boss", "Barbecue Sauce": "Barbecue-Soße", "Believe": "Believe",
 "Pope's Hail Mary": "Popes Hail Mary", "Grizi's Golazo": "Grizis Golazo", "Harder's Hat-trick": "Harders Hattrick",
 "Venemous Vitinha": "Giftiger Vitinha", "The rise of Gegenpressing": "Der Aufstieg des Gegenpressings", "The 11% Miracle": "Das 11-%-Wunder",
 "Semi-Pro": "Semi-Pro", "Win 5": "Gewinne 5", "Win 3": "Gewinne 3", "Win 1": "Gewinne 1", "Win 25": "Gewinne 25",
 "Win 50": "Gewinne 50", "Win 100": "Gewinne 100",
}

def task_title(t):
    if t in TT_EXACT: return TT_EXACT[t]
    m = re.fullmatch(r'([\d,]+) Rush Points', t)
    if m: return f"{fmt(m[1])} Rush-Punkte"
    m = re.fullmatch(r'([\d,]+) SBCs', t)
    if m: return f"{fmt(m[1])} SBCs"
    m = re.fullmatch(r'Level (\d+)', t)
    if m: return f"Level {m[1]}"
    m = re.fullmatch(r'Complete \'(.+)\'', t)
    if m: return f"„{m[1]}“ abschließen"
    m = re.fullmatch(r'List ([\d,]+)', t)
    if m: return f"{fmt(m[1])} einstellen"
    m = re.fullmatch(r'([\d,]+) Buy Now', t)
    if m: return f"{fmt(m[1])}× Sofort kaufen"
    m = re.fullmatch(r'([\d,]+) Assists from Crosses', t)
    if m: return f"{m[1]} Flanken-Vorlagen"
    m = re.fullmatch(r'([\d,]+) Direct Free Kicks', t)
    if m: return f"{m[1]} direkte Freistöße"
    m = re.fullmatch(r'Score ([\d,]+)', t)
    if m: return f"{m[1]} Tore"
    m = re.fullmatch(r'Assist ([\d,]+)', t)
    if m: return f"{m[1]} Vorlagen"
    m = re.fullmatch(r'([\d,]+) Stars', t)
    if m: return f"{m[1]} Sterne"
    m = re.fullmatch(r'First Owned Win (\d+)', t)
    if m: return f"Erstbesitz: {m[1]} Siege"
    m = re.fullmatch(r'Complete (\d+) Bonuses', t)
    if m: return f"{m[1]} Boni abschließen"
    m = re.fullmatch(r'(\d+) Buy Now', t)
    if m: return f"{m[1]}× Sofort kaufen"
    return t

# ---- Belohnungen ---------------------------------------------------------
STYLES = {"Shadow", "Hunter", "Hawk", "Engine", "Anchor", "Sentinel", "Finisher", "Deadeye", "Intercept"}
LEAGUE = {"Premier League": "Premier-League-"}

def pack_name(s):
    s = s.strip()
    m = re.fullmatch(r'(\d+) ?[x×] (\d+(?:[-+]\d*)?\+?) (Premier League )?Gold Players? Pack', s)
    if m:
        lg = "Premier-League-" if m[3] else ""
        return f"{m[1]}× {lg}Gold-Spielerpack {m[2].replace('-', '–')}"
    m = re.fullmatch(r'x(\d+) Players Pack', s)
    if m: return f"{m[1]}× Spielerpack"
    m = re.fullmatch(r'(\d+)x Premier League Gold Players Pack', s)
    if m: return f"{m[1]}× Premier-League-Gold-Spielerpack"
    m = re.fullmatch(r'(\d+(?:-\d+)?\+?) Gold Player Pack', s)
    if m: return f"Gold-Spielerpack {m[1].replace('-', '–')}"
    m = re.fullmatch(r'1 Of (\d+) (\d+\+) (Premier League )?Gold Player Pick', s)
    if m: return f"1 aus {m[1]}: {'Premier-League-' if m[3] else ''}Gold-Spieler {m[2]}"
    m = re.fullmatch(r'1 Of (\d+) Squad Foundations Pick', s)
    if m: return f"1 aus {m[1]}: Squad-Foundations-Spieler"
    m = re.fullmatch(r'1 Of (\d+) (\d+\+ )?Holographic Base (Icon|Hero) Player Pick', s)
    if m: return f"1 aus {m[1]}: Holografischer Basis-{m[3]} {m[2] or ''}".strip()
    sizes = {"Small": "Kleines", "Large": "Großes", "Giant": "Riesiges", "Jumbo": "Jumbo"}
    m = re.fullmatch(r'(Small|Large|Giant|Jumbo) (Gold|Silver|Bronze)( Players)? Pack', s)
    if m:
        col = {"Gold": "Gold", "Silver": "Silber", "Bronze": "Bronze"}[m[2]]
        return f"{sizes[m[1]]} {col}-{'Spielerpack' if m[3] else 'Pack'}"
    if s == "Gold Players Pack": return "Gold-Spielerpack"
    if s == "Silver Pack": return "Silber-Pack"
    if s == "Bronze Pack": return "Bronze-Pack"
    if s == "Consumables Pack": return "Verbrauchs-Pack"
    return None

OTHER = {
 "Coin Boost": "Münz-Boost", "Stadium Trophy": "Stadion-Trophäe", "Award": "Auszeichnung", "Badge": "Abzeichen",
 "Manager": "Trainer-Item", "Transfer Market Access": "Transfermarkt-Zugang", "Consumable": "Verbrauchsgegenstand",
 "Stadium Tifo": "Stadion-Tifo", "Stadium Background Tifo": "Stadion-Hintergrund-Tifo",
 "Stadium Stadium Theme": "Stadion-Thema", "Movember Stadium Theme": "Movember-Stadion-Thema",
 "Ultimate Scream Stadium Theme": "Ultimate-Scream-Stadion-Thema", "Movember Background Tifo": "Movember-Hintergrund-Tifo",
 "Liga Bbva Mx - Día De Muertos": "Liga BBVA MX – Día de Muertos", "Bundesliga X Playmobil": "Bundesliga x Playmobil",
 "Adidas Cnxt25 Pro Ball": "adidas Cnxt25 Pro Ball", "Halloween Vip": "Halloween VIP", "Gallery Excellence": "Gallery Excellence",
}

def reward(r):
    """-> dict(kind, text, icon?)"""
    t = r['text'].strip()
    icon = r.get('icon') or ''
    if 'season-points' in icon:
        return dict(kind='season', text=f"{t.replace(',', '.')} Saisonpunkte")
    if 'champions-token' in icon:
        m = re.match(r'(\d+) Champions Tokens', t)
        return dict(kind='champtoken', text=f"{m[1]} Champions-Tokens" if m else t)
    if 'gallery-token' in icon:
        m = re.match(r'(\d+) Gallery Tokens', t)
        return dict(kind='gallerytoken', text=f"{m[1]} Gallery-Tokens" if m else t)
    m = re.fullmatch(r'([\d,]+) Coins', t)
    if m: return dict(kind='coins', text=f"{fmt(m[1])} Münzen")
    if 'pick.webp' in icon:
        return dict(kind='pick', text=pack_name(t) or t)
    if 'pack-fc27' in icon:
        return dict(kind='pack', text=pack_name(t) or t)
    if t in STYLES:
        return dict(kind='style', text=t)
    if t in OTHER:
        k = 'item'
        if t == 'Coin Boost': k = 'boost'
        if t == 'Transfer Market Access': k = 'access'
        return dict(kind=k, text=OTHER[t])
    return dict(kind='item', text=t)

# ---- Bilder: bewusst keine fremden Bilder übernehmen --------------------
img_map = {}
def local(url):
    if not url: return None
    if url in img_map: return img_map[url]
    u = url.split('?')[0]
    ext = os.path.splitext(u)[1] or '.png'
    name = hashlib.md5(u.encode()).hexdigest()[:10] + ext
    img_map[url] = 'img/' + name
    return img_map[url]

def parse_player(r):
    txt = r['txt']
    while not txt[0].isdigit(): txt = txt[1:]
    rating = txt[0]
    i = 1
    pos = []
    while i < len(txt) and txt[i] not in ('R', 'L'):
        pos.append(txt[i]); i += 1
    # nach den Positionen: Fuß, Schwacher Fuß, Skill ... bis zum Namen
    j = i
    while j < len(txt) and txt[j] != 'PAC': j += 1
    name = txt[j - 1]
    stats = []
    k = j
    while k + 1 < len(txt) and txt[k] in ('PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY'):
        stats.append([txt[k], txt[k + 1]]); k += 2
    col = {}
    for key in ('header', 'name', 'attribute-values', 'chip-bg'):
        m = re.search(rf'--fut-{key}:(#[0-9a-fA-F]{{3,8}})', r['style'])
        if m: col[key] = m[1]
    return dict(kind='player', rating=rating, pos=pos[:4], name=name, stats=stats, label=r['label'],
                col=col)

def conv(r):
    return parse_player(r) if r['type'] == 'player' else reward(r)

# ---- Zusammenbauen -------------------------------------------------------
def tr_desc(en):
    if en in DE: return DE[en]
    if en not in MISSING['desc']: MISSING['desc'].append(en)
    return en
def tr_gdesc(g):
    if g['id'] in GDESC: return GDESC[g['id']]
    MISSING['gdesc'][g['id']] = g['desc']
    return g['desc']

MONTHS = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
def to_iso(s):
    # "13 Nov 2026, 17:59"  (Zeitzone der Seite: UTC)
    m = re.match(r'(\d+) (\w+) (\d{4}), (\d+):(\d+)', s)
    return f"{m[3]}-{MONTHS[m[2][:3]]:02d}-{int(m[1]):02d}T{int(m[4]):02d}:{m[5]}:00Z"

out = []
for g in d:
    tasks = []
    for t in g['tasks']:
        tasks.append(dict(n=int(t['n']), title=task_title(t['title']), desc=tr_desc(t['desc']),
                          rewards=[conv(x) for x in t['rewards']]))
    out.append(dict(id=g['id'], cat=CAT.get(g['cat'], g['cat']), catKey=g['cat'], title=GT.get(g['title'], g['title']),
                    desc=tr_gdesc(g), ends=to_iso(g['ends']), starts=to_iso(g['starts']),
                    rewards=[conv(x) for x in g['rewards']], tasks=tasks))

os.makedirs(os.path.join(ROOT, 'js'), exist_ok=True)
import datetime
_m = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']
_t = datetime.date.today()
with open(os.path.join(ROOT, 'js', 'data.js'), 'w') as f:
    f.write(f"window.SNAPSHOT = '{_t.day}. {_m[_t.month-1]} {_t.year}';\n")
    f.write('window.OBJECTIVES = ' + json.dumps(out, ensure_ascii=False, indent=1) + ';\n')

print('groups', len(out), 'tasks', sum(len(g['tasks']) for g in out))
json.dump(MISSING, open(os.path.join(ROOT, 'data', 'missing.json'), 'w'), ensure_ascii=False, indent=1)
if MISSING['desc'] or MISSING['gdesc']:
    print(f"ACHTUNG: {len(MISSING['desc'])} Aufgabentexte und {len(MISSING['gdesc'])} Gruppentexte ohne Übersetzung -> data/missing.json")
