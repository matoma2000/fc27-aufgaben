import zlib, struct, os
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def png(path,w,h,rows):
    raw=b''.join(b'\x00'+bytes(r) for r in rows)
    def ch(t,d): c=struct.pack('>I',len(d))+t+d; return c+struct.pack('>I',zlib.crc32(t+d))
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw,9))+ch(b'IEND',b''))
def pip(x,y,poly):
    ins=False;j=len(poly)-1
    for i in range(len(poly)):
        xi,yi=poly[i];xj,yj=poly[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: ins=not ins
        j=i
    return ins
def make(S):
    # Koordinaten in 0..1
    para=[(.30,.2),(.86,.2),(.70,.8),(.14,.8)]
    def seg(x0,y0,x1,y1): 
        return (x0,y0,x1,y1)
    t=.075; # Strichstärke
    def rect(x0,y0,x1,y1): return (x0,y0,x1,y1)
    # Ziffern in Box (Breite .17, Höhe .34), Ursprung links oben
    def digit(ch,ox,oy):
        w,h=.17,.34; r=[]
        top=rect(ox,oy,ox+w,oy+t); mid=rect(ox,oy+h/2-t/2,ox+w,oy+h/2+t/2); bot=rect(ox,oy+h-t,ox+w,oy+h)
        ur=rect(ox+w-t,oy,ox+w,oy+h/2); lr=rect(ox+w-t,oy+h/2,ox+w,oy+h); ll=rect(ox,oy+h/2,ox+t,oy+h)
        if ch=='2': r=[top,ur,mid,ll,bot]
        if ch=='7': r=[top,ur,lr]
        return r
    rects=digit('2',.34,.33)+digit('7',.55,.33)
    shear=.22
    def inrect(x,y):
        for (a,b,c,d) in rects:
            xs=x+(y-.5)*shear   # nach rechts neigen (oben weiter rechts)
            xs=x+( .5-y)*shear*-1
            if a<=x-(.5-y)*shear<=c and b<=y<=d: return True
        return False
    rows=[]
    N=3
    for py in range(S):
        row=[]
        for px in range(S):
            acc=[0,0,0]
            for sy in range(N):
                for sx in range(N):
                    x=(px+(sx+.5)/N)/S; y=(py+(sy+.5)/N)/S
                    bg=(6,10,20)
                    # leichter Cyan-Schimmer oben rechts
                    d=((x-.85)**2+(y)**2)**.5
                    k=max(0,1-d/.9)*.28
                    c=[bg[i]+(( [46,230,255][i])-bg[i])*k for i in range(3)]
                    if pip(x,y,para):
                        u=(x+y)/2
                        c=[212+(46-212)*u,255+(230-255)*u,58+(255-58)*u]
                        if inrect(x,y): c=[8,16,31]
                    for i in range(3): acc[i]+=c[i]
            row+= [int(a/(N*N)) for a in acc]
        rows.append(row)
    return rows
for n,S in (('apple-touch-icon.png',180),('icon-192.png',192),('icon-512.png',512)):
    png(os.path.join(HERE,'icons',n),S,S,make(S))
print('ok')
