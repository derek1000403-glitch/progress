# 2026-11-22 依老師建議重排（11/23 起整段重排；11/22 以前不動）
#  - 先留兩天消化天體（LEC31 推導），再看完第二期影片
#  - 第二期影片看完就每週六寫一份初選歷屆卷、週日檢討
#  - 第三期上完開始複選歷屆卷；第四期放慢（一部影片配它的題目，平日一天只做一樣）
#  - 決選不排
import json, datetime as dt, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mark
D = dt.date
START = D(2026, 11, 23); EXAM = D(2027, 11, 7)
DIGEST = [D(2026, 11, 23), D(2026, 11, 24)]
d = mark.load()
WK = "日一二三四五六"
wk = lambda x: WK[(x.weekday() + 1) % 7]
iso = lambda x: x.isoformat()

keep = [x for x in d['days'] if x['date'] < iso(START)]
later = [x for x in d['days'] if x['date'] >= iso(START)]
bydate = {x['date']: x for x in keep}
pend = []
for day in keep:                       # 11/22 以前沒看完的影片也拿出來重排
    for it in list(day['items']):
        if 900 < it['id'] < 1000 and not it.get('done'):
            day['items'].remove(it); pend.append(it)
for day in later:
    for it in day['items']:
        if it.get('done') or it.get('redo'):
            bydate.get(it.get('doneAt') or '', keep[-1])['items'].append(it); continue
        pend.append(it)
vid2 = sorted([i for i in pend if 900 < i['id'] < 1000], key=lambda i: i['id'])
q1 = sorted([i for i in pend if i['id'] < 900], key=lambda i: i['id'])
q2 = sorted([i for i in pend if 1000 < i['id'] < 2000], key=lambda i: 1025.5 if i['id'] == 1100 else i['id'])
probs12 = q1 + q2

# ---------- 行事曆 ----------
WINTER = (D(2027, 1, 21), D(2027, 2, 14)); SUMMER = (D(2027, 7, 1), D(2027, 8, 29))
REST = {D(2027, 2, 5), D(2027, 2, 6)}
FINAL = {D(2027, 1, 18), D(2027, 1, 19), D(2027, 1, 20)}
HOL = {D(2026, 12, 25), D(2027, 1, 1), D(2027, 3, 1), D(2027, 4, 5), D(2027, 6, 9), D(2027, 9, 15), D(2027, 9, 28), D(2027, 10, 11), D(2027, 10, 25)}
MOCK = {D(2027, 10, 23): 1, D(2027, 10, 27): 2, D(2027, 10, 30): 3, D(2027, 11, 3): 4}
MOCKR = {D(2027, 10, 24): 1, D(2027, 10, 28): 2, D(2027, 10, 31): 3, D(2027, 11, 4): 4}
invac = lambda x: WINTER[0] <= x <= WINTER[1] or SUMMER[0] <= x <= SUMMER[1]
def kind(x):
    if x == EXAM: return 'exam'
    if x in REST: return 'rest'
    if x in FINAL: return 'final'
    if invac(x): return 'vac'
    if x.weekday() == 5: return 'sat'
    if x.weekday() == 6: return 'sun'
    if x in HOL: return 'hol'
    return 'school'
buffer_day = lambda x: x.weekday() == 6 and x.day <= 7 and x not in REST and x < D(2027, 10, 1)

days = []
x = START
while x <= EXAM:
    days.append({'date': iso(x), 'weekday': wk(x), 'items': [], 'plan': {}, '_k': kind(x), '_d': x}); x += dt.timedelta(1)

def mk(id_, lesson, topic, q, note=None):
    it = {'id': id_, 'lesson': lesson, 'topic': topic, 'q': q, 'diff': '', 'done': False, 'doneAt': None, 'slot': '圖書館'}
    if note: it['note'] = note
    return it
CN = "零一二三四五六七八九十"
def cnum(n):
    if n <= 10: return CN[n]
    if n < 20: return '十' + CN[n - 10]
    return CN[n // 10] + '十' + (CN[n % 10] if n % 10 else '')
def term(t, vid0, prob0):
    T = {3: '三', 4: '四'}[t]
    seq = []; n = 0
    for k in range(1, 25):
        seq.append(mk(vid0 + k, f'{T}期影片', f'第{T}期第{cnum(k)}部', f'{T}期第{k}部'))
        for _ in range(5 if k <= 4 else 4):   # 100 題（暫定，拿到講義再改）
            n += 1; seq.append(mk(prob0 + n, f'{T}期第{k}部', f'第{T}期第{cnum(n)}題', f'{T}期習題 #{n}'))
    return seq
seq3 = term(3, 6000, 7000); seq4 = term(4, 8000, 9000)
isvid = lambda i: 900 < i['id'] < 1000 or 6000 < i['id'] < 7000 or 8000 < i['id'] < 9000

# ---------- 歷屆卷 ----------
cnt = {'c': 0, 'c2': 0, 'f': 0, 'adv': 0}
C_MAX, F_MAX = 16, 12   # 初選 2026→2011、複選 2026→2015（老師：古題一律從近年往前寫、每次都計時）
def paper_c():
    if cnt['c'] < C_MAX:
        cnt['c'] += 1; return mk(10000 + cnt['c'], '初選歷屆', f'初選 {2027 - cnt["c"]}', '計時作答', '從近年往前寫；照考試時間計時、不看講義')
    cnt['c2'] += 1; return mk(10200 + cnt['c2'], '初選歷屆', f'初選卷二刷 #{cnt["c2"]}', '重寫錯題', '把之前錯過的題重寫一次，不看解答')
def paper_f():
    cnt['f'] += 1; return mk(11000 + cnt['f'], '複選歷屆', f'複選 {2027 - cnt["f"]}', '計時作答', '從近年往前寫；照複選時間計時，不會的先標起來，檢討時再查')
def review(it):
    off = 50 if 10200 < it['id'] < 10300 else 100
    return mk(it['id'] + off, it['lesson'], it['topic'] + ' 檢討', '檢討', '每題寫錯因，回寫到講義那一招')
# 灰二十（老師給的 20 份例題彙編）：全部上完後才寫；每份分 6 段，照課程順序。題數未知，寫完一份可提早進下一份
GRAY = [('質點力學例題彙編 (一)', 57), ('質點力學例題彙編 (二)', 84), ('剛體力學例題彙編', 85), ('流體、振動和波例題彙編', 41),
        ('理想氣體例題彙編', 28), ('氣體動力論例題彙編', 17), ('熱力過程例題彙編', 22), ('物態變化、熱膨脹、熱傳導例題彙編', 29), ('熱輻射例題彙編', 16), ('大氣例題彙編', 10),
        ('電學例題彙編', 73), ('磁學例題彙編', 35), ('電磁感應例題彙編 (一)', 33), ('電磁感應例題彙編 (二)', 40), ('電子電路例題彙編', 44),
        ('光學例題彙編', 79), ('物質例題彙編', 39), ('近代物理例題彙編', 75), ('超導體例題彙編', 52), ('綜合題例題彙編', 22)]
PPS = 7   # 一段約 7 頁
NQ = []
for g, pg in GRAY:
    n = -(-pg // PPS)
    for k in range(n):
        a_ = k * pg // n + 1; b_ = (k + 1) * pg // n
        NQ.append((g, f'p.{a_}–{b_}'))
def adv():
    cnt['adv'] += 1
    if NQ:
        g, k = NQ.pop(0)
        return mk(13000 + cnt['adv'], '灰二十', g, k, '照老師教的方法，官方解答常有錯，以老師的為準')
    return mk(13000 + cnt['adv'], '錯題重寫', '錯題重寫', f'#{cnt["adv"]}', '挑之前寫錯的題（歷屆卷、難題集萃）重寫，不看解答')

# ---------- 排程 ----------
stage = 'v2'              # 11/22 決定 LEC31 當天推完，11/23 直接看 LEC32；原本： digest → v2 → p12 → t3 → t4 → free
papers_on = False; f_on = False; f_toggle = False
pending = []
endinfo = {}
for day in days:
    x = day['_d']; k = day['_k']; it = day['items']; wd = x.weekday()
    if k == 'exam':
        it.append(mk(3002, '初選', '2027 物奧初選', '考試日', '提早到考場；帶身分證、准考證、文具、計算機')); continue
    if k == 'rest': continue
    if x in MOCK:
        n = MOCK[x]; it.append(mk(12000 + n, '模擬考', f'全卷模擬：重寫初選 {2027 - n}', '計時作答', '最近四年的卷子第二次完整重寫，照考試時間與規則')); continue
    if x in MOCKR:
        n = MOCKR[x]; it.append(mk(12100 + n, '模擬考', f'全卷模擬：初選 {2027 - n} 檢討', '檢討', '每題寫錯因，回寫到講義那一招')); continue
    if x >= D(2027, 11, 5):
        day['plan']['圖書館'] = '只看錯題本與講義速覽，不做新題' + ('；今晚早睡' if x == D(2027, 11, 6) else ''); continue
    if x >= D(2027, 10, 23):
        it.append(adv()); continue
    if stage == 'digest':
        # 11/22 已把 14001（比奈公式）移到 11/22；11/23 推軌道方程，11/24 當緩衝
        if x == DIGEST[0]:
            it.append(mk(14002, 'LEC31', '天體消化', '軌道方程（圓錐曲線）自己推一遍', '照老師的推法，不看筆記從頭推；卡住先翻講義，再拿來問'))
            day['plan']['圖書館'] = '天體消化：先把比奈公式推完，再推軌道方程（圓錐曲線）'
        else:
            day['plan']['圖書館'] = '緩衝：天體推導沒推完的補完；推完就先看 LEC32'
        if x == DIGEST[-1]: stage = 'v2'
        continue
    if buffer_day(x) and stage in ('v2', 'p12', 't3'):
        day['plan']['圖書館'] = '緩衝日：補前面落後的項目；沒落後就休息'; continue

    # --- 週末的歷屆卷（第二期影片看完後才開始） ---
    if papers_on and wd == 5 and cnt['c2'] < C_MAX:
        p = paper_c(); it.append(p); pending.append(p); continue
    rev_today = []
    if pending and (wd == 6 or k in ('vac',) or stage in ('t4', 'free')):
        while pending: rev_today.append(review(pending.pop(0)))
        it += rev_today

    # --- 複選歷屆卷 ---
    if f_on and cnt['f'] < F_MAX and not rev_today:
        if SUMMER[0] <= x <= SUMMER[1]:
            if wd in (0, 3): p = paper_f(); it.append(p); pending.append(p); continue
        elif wd == 2:
            f_toggle = not f_toggle
            if f_toggle: p = paper_f(); it.append(p); pending.append(p); continue

    # --- 內容 ---
    vac = k in ('vac', 'hol')
    if stage == 'v2':
        nv = 2 if wd == 5 else 1
        for _ in range(nv):
            if vid2: it.append(vid2.pop(0))
        for _ in range(3 if wd >= 5 else 2):
            if probs12: it.append(probs12.pop(0))
        if not vid2:
            stage = 'p12'; papers_on = True; endinfo['二期影片'] = iso(x)
        continue
    if stage == 'p12':
        cap = 2 if k == 'final' else 3 if rev_today else 8 if vac else 4
        for _ in range(cap):
            if probs12: it.append(probs12.pop(0))
        if not probs12: stage = 't3'; endinfo['一二期習題'] = iso(x)
        continue
    if stage in ('t3', 't4'):
        seq = seq3 if stage == 't3' else seq4
        if k == 'final': continue
        if stage == 't4' and x.weekday() == 6: continue   # 難題集萃等全部上完才寫
        if stage == 't3': budget = 3 if rev_today else 8 if vac else 4
        else: budget = 2 if rev_today else 6 if vac else 3     # 第四期放慢
        used = 0
        while seq and used < budget:
            c = (4 if stage == 't3' else 3) if isvid(seq[0]) else 1   # 一部影片＝平日一天的額度
            if used and used + c > budget: break
            it.append(seq.pop(0)); used += c
        if not seq:
            endinfo['第三期' if stage == 't3' else '第四期'] = iso(x)
            if stage == 't3': stage = 't4'; f_on = True
            else: stage = 'free'
        continue
    # free：進階題
    it.append(adv())
    if (SUMMER[0] <= x <= SUMMER[1] or k == 'hol') and not rev_today: it.append(adv())
for nm, e in endinfo.items(): print(nm, '結束', e)
print('counts', cnt, '剩', len(vid2), len(probs12), len(seq3), len(seq4))
assert not vid2 and not probs12 and not seq3 and not seq4

# ---------- 每日計畫文字 ----------
for day in days:
    x = day['_d']; k = day['_k']; its = day['items']; P = {}
    if k == 'rest': day['plan'] = {'圖書館': '春節：休息一天，不排進度'}; continue
    if k == 'exam': day['plan'] = {'圖書館': '2027 物奧初選，加油！'}; continue
    weekend = x.weekday() >= 5 or k in ('vac', 'hol')
    vids = [i for i in its if isvid(i)]
    probs = [i for i in its if i['id'] < 900 or 1000 < i['id'] < 2000 or 7000 < i['id'] < 8000 or 9000 < i['id'] < 10000]
    past = [i for i in its if 10000 < i['id'] < 13000]
    advs = [i for i in its if 13000 < i['id'] < 14000]
    dig = [i for i in its if 14000 < i['id'] < 15000]
    if k == 'final': P['學校'] = '期末考週（日期為假設，請以學校行事曆為準）：先顧考試'
    elif weekend: P['學校'] = ('寒假' if WINTER[0] <= x <= WINTER[1] else '暑假' if SUMMER[0] <= x <= SUMMER[1] else '週末／假日') + '：這段併進圖書館'
    else: P['學校'] = '學校課業；有空翻講義（當字典用）'
    parts = []
    if dig and not day['plan'].get('圖書館'): parts.append('天體消化：' + dig[0]['q'])
    if vids: parts.append('看 ' + '、'.join(i['q'] for i in vids))
    if probs: parts.append(f'{len(probs)} 題')
    for p in past:
        parts.append(('計時作答：' + p['topic']) if p['q'] in ('計時作答', '重寫錯題') else ('檢討' + p['topic'].replace(' 檢討', '')))
    if advs: parts.append('、'.join(('灰二十 ' + i['topic'].replace('例題彙編', '').strip() + ' ' + i['q']) if i['lesson'] == '灰二十' else '錯題重寫' for i in advs))
    if parts: P['圖書館'] = '＋'.join(parts)
    elif day['plan'].get('圖書館'): P['圖書館'] = day['plan']['圖書館']
    P['晚通勤'] = '通勤：今天不熟的地方翻講義查一下（當字典用）'
    day['plan'] = P
for day in days:
    for kk in [k for k in day if k.startswith('_')]: day.pop(kk)
    if not day['plan']: day.pop('plan')
d['days'] = keep + [x for x in days if x['items'] or x.get('plan')]
d['updated'] = dt.date.today().isoformat()
allit = [i for x in d['days'] for i in x['items']]
ids_ = [i['id'] for i in allit]
assert len(ids_) == len(set(ids_)), [i for i in ids_ if ids_.count(i) > 1][:10]
if '--dry' not in sys.argv: mark.save(d)
print('items', len(allit), 'days', len(d['days']))
