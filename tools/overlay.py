import sys, math
from PIL import Image, ImageDraw, ImageFont
import json
P=json.load(open(sys.argv[-1]))
W,H=700,210; FPS=30000/1001; DUR=P["dur"]; IV=P["interval"]
nfr=int(DUR*FPS)+2
start=P["start"]
fs="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
fr="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
Fbig=ImageFont.truetype(fs,74,index=2); Fsm=ImageFont.truetype(fr,26,index=2); Fnote=ImageFont.truetype(fs,27,index=2)
SS=2
def frame(i):
    t=i/FPS; clock=start+i*IV
    img=Image.new("RGBA",(W*SS,H*SS),(0,0,0,0)); d=ImageDraw.Draw(img)
    d.rounded_rectangle([0,0,W*SS-1,H*SS-1],radius=26*SS,fill=(12,16,24,185))
    cx,cy,R=105*SS,105*SS,78*SS
    d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(250,248,242,255),outline=(255,170,60,255),width=5*SS)
    for k in range(12):
        a=k/12*2*math.pi; r1=R*(0.80 if k%3 else 0.72); r2=R*0.92
        d.line([cx+r1*math.sin(a),cy-r1*math.cos(a),cx+r2*math.sin(a),cy-r2*math.cos(a)],fill=(30,30,36,255),width=(5 if k%3==0 else 3)*SS)
    h=(clock/3600)%12; m=(clock/60)%60
    for ang,L,wd,c in [(h/12*2*math.pi,0.50,8,(30,30,36,255)),(m/60*2*math.pi,0.76,5,(220,60,50,255))]:
        d.line([cx,cy,cx+R*L*math.sin(ang),cy-R*L*math.cos(ang)],fill=c,width=wd*SS)
    d.ellipse([cx-7*SS,cy-7*SS,cx+7*SS,cy+7*SS],fill=(220,60,50,255))
    hh=int(clock//3600)%24; mm=int(clock//60)%60
    x0=210*SS
    d.text((x0,4*SS),P["date"],font=Fsm.font_variant(size=26*SS),fill=(200,206,216,255))
    d.text((x0,30*SS),f"{hh:02d}:{mm:02d}",font=Fbig.font_variant(size=74*SS),fill=(255,255,255,255))
    el=i*IV; eh=int(el//3600); em=int(el//60)%60
    d.text((x0+215*SS,62*SS),f"已奮鬥 {eh}h{em:02d}m",font=Fsm.font_variant(size=26*SS),fill=(255,170,60,255))
    d.text((x0,140*SS),P["note"],font=Fnote.font_variant(size=27*SS),fill=(255,255,255,255))
    # progress bar
    p=min(1,t/DUR); d.rounded_rectangle([x0,186*SS,x0+460*SS,192*SS],radius=3*SS,fill=(255,255,255,60))
    d.rounded_rectangle([x0,186*SS,x0+int(460*p)*SS+2,192*SS],radius=3*SS,fill=(255,170,60,255))
    return img.resize((W,H),Image.LANCZOS)
if sys.argv[1]=="png":
    frame(int(float(sys.argv[2])*FPS)).save(sys.argv[3])
else:
    o=sys.stdout.buffer
    for i in range(nfr): o.write(frame(i).tobytes())
