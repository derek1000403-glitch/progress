import json, datetime as dt, sys, copy
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import mark
D=dt.date
START=D(2026,11,29); EXAM=D(2027,11,7)
d=mark.load()
WK="日一二三四五六"
def wk(x): return WK[(x.weekday()+1)%7]
def iso(x): return x.isoformat()

# ---------- 收集要重排的項目 ----------
keep_days=[x for x in d['days'] if x['date']<iso(START)]
later=[x for x in d['days'] if x['date']>=iso(START)]
bydate={x['date']:x for x in keep_days}
pend=[]
for day in later:
    for it in day['items']:
        if it.get('done') or it.get('redo'):
            tgt=bydate.get(it.get('doneAt') or '') or keep_days[-1]
            tgt['items'].append(it); continue
        pend.append(it)
q1=sorted([i for i in pend if i['id']<900],key=lambda i:i['id'])
q2=sorted([i for i in pend if 1000<=i['id']<2000],key=lambda i:(i['id']==1100, i['id']))
# 1100 (LEC26 P09) 放到 LEC26 的題目後面
q2=sorted(q2,key=lambda i:(1025.5 if i['id']==1100 else i['id']))
rev=sorted([i for i in pend if 4000<=i['id']<5000],key=lambda i:i['id'])
other=[i for i in pend if not (i['id']<900 or 1000<=i['id']<2000 or 4000<=i['id']<5000 or 2000<=i['id']<3000)]
assert not other, other
done_mem=max([i['id'] for x in keep_days for i in x['items'] if 2000<=i['id']<3000])

def req_rev(i):
    if i['id']<900: return 4000+int(i['lesson'][1:])
    n=int(i['lesson'].replace('二期LEC',''))
    return min(4046,4000+n+1)

# ---------- 行事曆 ----------
WINTER=(D(2027,1,21),D(2027,2,14)); SUMMER=(D(2027,7,1),D(2027,8,29))
REST={D(2027,2,5),D(2027,2,6)}
FINAL={D(2027,1,18),D(2027,1,19),D(2027,1,20)}
HOL={D(2026,12,25),D(2027,1,1),D(2027,3,1),D(2027,4,5),D(2027,6,9),D(2027,9,15),D(2027,9,28),D(2027,10,11),D(2027,10,25)}
def invac(x): return WINTER[0]<=x<=WINTER[1] or SUMMER[0]<=x<=SUMMER[1]
def kind(x):
    if x in REST: return 'rest'
    if x in FINAL: return 'final'
    if invac(x): return 'vac'
    if x.weekday()==5: return 'sat'
    if x.weekday()==6: return 'sun'
    if x in HOL: return 'hol'
    return 'school'
def buffer_day(x):  # 每月第一個週日當緩衝日（內容學習期）
    return x.weekday()==6 and x.day<=7 and x not in REST
def cap(x):
    k=kind(x)
    if k=='rest': return 0,0
    if k=='final': return 0,2
    if k=='vac':
        if x.weekday()==6: return 2,6
        return (3 if x.weekday()==5 else 2),8
    return {'school':(1,4),'sat':(3,8),'sun':(2,6),'hol':(2,8)}[k]

days=[]
x=START
while x<EXAM:
    days.append({'date':iso(x),'weekday':wk(x),'items':[],'plan':{},'_k':kind(x),'_d':x}); x+=dt.timedelta(1)
days.append({'date':iso(EXAM),'weekday':wk(EXAM),'items':[],'plan':{},'_k':'exam','_d':EXAM})

def mk(id_,lesson,topic,q,slot,note=None):
    it={'id':id_,'lesson':lesson,'topic':topic,'q':q,'diff':'','done':False,'doneAt':None,'slot':slot}
    if note: it['note']=note
    return it

CN="零一二三四五六七八九十"
def cnum(n):
    if n<=10: return CN[n]
    if n<20: return '十'+CN[n-10]
    return CN[n//10]+'十'+(CN[n%10] if n%10 else '')

# ---------- 新項目 ----------
def term_items(t, vid0, prob0, rev0, sec0):
    T={3:'三',4:'四'}[t]
    vids=[mk(vid0+k,f'{T}期影片',f'第{T}期第{cnum(k)}部',f'{T}期第{k}部','圖書館') for k in range(1,25)]
    secs=[mk(sec0+k,f'{T}期第{k}部','新課秘笈',f'{T}期第{k}部','晚通勤','看完當天讀；秘笈由逐字稿整理，影片給我後產生') for k in range(1,25)]
    revs=[mk(rev0+k,f'{T}期第{k}部','舊課秘笈＋加練',f'{T}期第{k}部','學校','寫該部習題前讀完，加練寫完對答案') for k in range(1,25)]
    probs=[]; n=0
    for k in range(1,25):
        cnt=5 if k<=4 else 4   # 100 題：前 4 部 5 題，其餘 4 題（暫定，拿到講義再改）
        for _ in range(cnt):
            n+=1; probs.append(mk(prob0+n,f'{T}期第{k}部',f'第{T}期第{cnum(n)}題',f'{T}期習題 #{n}','圖書館'))
    for p in probs: p['_rev']=rev0+int(p['lesson'].split('第')[1].rstrip('部'))
    return vids,secs,revs,probs
v3,s3,r3,p3=term_items(3,6000,7000,4100,5100)
v4,s4,r4,p4=term_items(4,8000,9000,4200,5200)

# ---------- 排程 ----------
i_day=0
mem_lessons=[f'LEC{n:02d}' for n in range(0,47)]
def nxt_free(pred):
    pass

def schedule_problems(probs, revq, reqf, start_i, label):
    """在 start_i 起排題目；每天先排舊課秘笈（1 份，落後時 2 份），再排題。回傳結束後下一天的 index"""
    i=start_i; probs=list(probs); revq=list(revq)
    qids={r['id'] for r in revq}
    revd={reqf(p) for p in probs if reqf(p) not in qids}
    while probs or revq:
        day=days[i]; V,P=cap(day['_d'])
        if day['_k']=='rest' or (buffer_day(day['_d'])): i+=1; continue
        nrev=0
        need=reqf(probs[0]) if probs else None
        while revq and (nrev<1 or (need and need not in revd and nrev<2)):
            r=revq.pop(0); day['items'].append(r); revd.add(r['id']); nrev+=1
        np=0
        while probs and np<P and reqf(probs[0]) in revd|{None}:
            p=probs.pop(0); p.pop('_rev',None); day['items'].append(p); np+=1
        day['_ph']=label
        i+=1
    return i
def schedule_videos(vids, secs, start_i, label):
    i=start_i; vids=list(vids); secs=list(secs)
    while vids:
        day=days[i]; V,P=cap(day['_d'])
        if day['_k']=='rest' or buffer_day(day['_d']): i+=1; continue
        for _ in range(min(V,len(vids))):
            day['items'].append(vids.pop(0)); day['items'].append(secs.pop(0))
        day['_ph']=label; i+=1
    return i

i=0
i=schedule_problems(q1+q2, rev, lambda p: req_rev(p) if 'lesson' in p and not p['id']>=6000 else None, i, 'B')
endB=i
i=schedule_videos(v3,s3,i,'C1'); endC1=i
i=schedule_problems(p3, r3, lambda p: p.get('_rev'), i, 'C2'); endC2=i
i=schedule_videos(v4,s4,i,'D1'); endD1=i
i=schedule_problems(p4, r4, lambda p: p.get('_rev'), i, 'D2'); endD2=i

for nm,e in (('B',endB),('C1',endC1),('C2',endC2),('D1',endD1),('D2',endD2)): print(nm,'ends',days[e-1]['date'])

# ---------- E：歷屆、進階題、模擬考 ----------
ids={'c':10000,'cr':10100,'c2':10200,'f':11000,'fr':11100,'m':12000,'mr':12100,'adv':13000}
cnt={k:0 for k in ids}
def new(kind_,lesson,topic,q,note=None,slot='圖書館'):
    cnt[kind_]+=1; return mk(ids[kind_]+cnt[kind_],lesson,topic,q,slot,note)
C1MAX,F_MAX=15,12
pending_review=[]   # (review item) 下一天放
MOCK={D(2027,10,23):1,D(2027,10,27):2,D(2027,10,30):3,D(2027,11,3):4}
MOCKR={D(2027,10,24):1,D(2027,10,28):2,D(2027,10,31):3,D(2027,11,4):4}
def adv(n=1):
    return [new('adv','進階題','進階題組',f'#{cnt["adv"]+1}（3 題）','各期講義的 M／H 題或複選程度題，照順序做；卡住先查秘笈') for _ in range(n)]
for j in range(endD2,len(days)):
    day=days[j]; x=day['_d']; k=day['_k']; day['_ph']='E'
    if k=='exam':
        day['items'].append(mk(3002,'初選','2027 物奧初選','考試日','圖書館','提早到考場；帶身分證、准考證、文具、計算機')); continue
    if k=='rest': continue
    if x in MOCK:
        n=MOCK[x]; day['items'].append(mk(12000+n,'模擬考',f'全卷模擬 #{n}','計時作答','圖書館','用最新的初選卷，完全照考試時間與規則')); continue
    if x in MOCKR:
        n=MOCKR[x]; day['items'].append(mk(12100+n,'模擬考',f'全卷模擬 #{n} 檢討','檢討','圖書館','每題寫錯因，回寫到秘笈那一招')); continue
    if x>=D(2027,11,5):
        day['plan']['圖書館']='只看錯題本與秘笈速覽，不做新題' + ('；今晚早睡' if x==D(2027,11,6) else ''); continue
    summer = SUMMER[0]<=x<=SUMMER[1]
    wd=x.weekday()
    if x>=D(2027,10,23):   # 最後兩週：模擬考之間只做輕量
        day['items']+=adv(1); continue
    if wd==5:  # 週六：初選歷屆
        if cnt['c']<C1MAX: it=new('c','初選歷屆',f'初選歷屆卷 #{cnt["c"]+1}','計時作答',None)
        else: it=new('c2','初選歷屆',f'初選卷二刷 #{cnt["c2"]+1}','重寫錯題','把之前錯過的題重寫一次，不看解答')
        day['items'].append(it); pending_review.append(it); continue
    if wd==6:  # 週日：檢討＋進階
        while pending_review:
            it=pending_review.pop(0)
            day['items'].append(mk(it['id']+100 if it['id']<10200 else it['id']+50,it['lesson'],it['topic']+' 檢討','檢討','圖書館','每題寫錯因，回寫到秘笈那一招'))
        if not buffer_day(x): day['items']+=adv(1)
        continue
    if summer and wd in (0,3) and cnt['f']<F_MAX:   # 暑假週一、週四：複選歷屆
        it=new('f','複選歷屆',f'複選歷屆卷 #{cnt["f"]+1}','計時作答',None); day['items'].append(it); pending_review.append(it); continue
    if pending_review and summer:
        it=pending_review.pop(0)
        day['items'].append(mk(it['id']+100,it['lesson'],it['topic']+' 檢討','檢討','圖書館','每題寫錯因，回寫到秘笈那一招'))
        day['items']+=adv(1); continue
    if summer or k=='hol': day['items']+=adv(2)
    else: day['items']+=adv(1)
print('counts',cnt)

# ---------- 記憶加強（每天早通勤） ----------
mid=done_mem
watched=list(mem_lessons)
rot=0
for day in days:
    x=day['_d']
    for it in day['items']:
        if 6000<it['id']<7000 or 8000<it['id']<9000: pass
    if day['_k'] in ('rest','exam') or x>=D(2027,11,5): continue
    lesson=watched[rot%len(watched)]; rot+=1
    mid+=1
    day['items'].insert(0,mk(mid,'記憶加強','記憶加強（接話）',lesson,'早通勤','老師原話接話；三、四期的接話檔看完影片後整理'))
    day['_mem']=lesson
    # 看完的三、四期影片加入輪替
    for it in day['items']:
        if 6000<it['id']<7000 or 8000<it['id']<9000: watched.append(it['q'])
assert mid<3000, mid

# 2026-11-18：記憶加強不排進日程
for day in days: day['items']=[i for i in day['items'] if not (2000<=i['id']<3000)]

# ---------- 每日計畫文字 ----------
def names(items):
    return '、'.join(i['q'] for i in items)
for day in days:
    x=day['_d']; k=day['_k']; its=day['items']; P={}
    weekend = x.weekday()>=5 or k in ('vac','hol')
    mem=[i for i in its if 2000<=i['id']<3000]
    revs=[i for i in its if 4000<=i['id']<5000]
    secs=[i for i in its if 5000<=i['id']<6000]
    vids=[i for i in its if 900<=i['id']<1000 or 6000<i['id']<7000 or 8000<i['id']<9000]
    probs=[i for i in its if i['id']<900 or 1000<=i['id']<2000 or 7000<i['id']<8000 or 9000<i['id']<10000]
    past=[i for i in its if 10000<i['id']<13000]
    advs=[i for i in its if 13000<i['id']<14000]
    if k=='rest':
        day['plan']={'圖書館':'春節：休息一天，不排進度'}; continue
    if k=='exam':
        day['plan']={'圖書館':'2027 物奧初選，加油！'}; continue
    if mem: P['早通勤']=f'記憶加強：{mem[0]["q"]} 全部故事線用文字接話'
    if revs: P['學校']='舊課秘笈＋加練：'+'、'.join(i['lesson'] if i['id']>=4100 else i['lesson'] for i in revs)+'（寫該課習題前讀完）'
    elif k=='final': P['學校']='期末考週（日期為假設，請以學校行事曆為準）：先顧考試'
    elif weekend: P['學校']=('寒假' if WINTER[0]<=x<=WINTER[1] else '暑假' if SUMMER[0]<=x<=SUMMER[1] else '週末／假日')+'：這段併進圖書館'
    else: P['學校']='秘笈輪讀：每天一堂，看到→反射默念一遍'
    if vids: P['圖書館']='影片：'+'、'.join(i['topic'] for i in vids)+'＋停點：說「開始上課」拿回來的時間'
    elif probs: P['圖書館']=f'刷題 {len(probs)} 題：圈條件→查秘笈的「看到」→動手→卡住問 Claude'
    elif past:
        p=past[0]
        P['圖書館']=('計時作答：'+p['topic']+'（照考試時間、不看秘笈）') if p['q'] in ('計時作答','重寫錯題') else ('檢討：'+'、'.join(i['topic'] for i in past)+'，每題寫錯因並回寫秘笈')
        if advs: P['圖書館']+='；再做進階題組 '+'、'.join(i['q'] for i in advs)
    elif advs: P['圖書館']='進階題組 '+'、'.join(i['q'] for i in advs)
    elif buffer_day(x): P['圖書館']='緩衝日：補前面落後的項目；沒落後就休息'
    elif k=='final': P['圖書館']='期末考週：只做少量題目'
    if 'plan' in day and day['plan'].get('圖書館') and '圖書館' not in P: P['圖書館']=day['plan']['圖書館']
    P['晚通勤']=('新課秘笈：'+'、'.join(i['q'] for i in secs)+' 整堂讀完、招式打勾') if secs else '錯題回寫：在秘笈那一招旁寫錯因'
    day['plan']=P
for day in days:
    for kk in [k for k in day if k.startswith('_')]: day.pop(kk)
newdays=[x for x in days if x['items'] or x['plan']]
d['days']=keep_days+newdays
d['updated']=dt.date.today().isoformat()
mark.save(d)
allit=[i for x in d['days'] for i in x['items']]
ids_=[i['id'] for i in allit]
assert len(ids_)==len(set(ids_)), [i for i in ids_ if ids_.count(i)>1][:10]
print('items',len(allit),'days',len(d['days']), 'last', d['days'][-1]['date'])
