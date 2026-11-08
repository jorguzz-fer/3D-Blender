import numpy as np
CLS={'head_top':(1.0,0.70,0.02),'head_bot':(1.0,0.33,0.03),'tail':(0.20,0.04,0.04),
     'slab':(1.0,0.90,0.60),'protein':(0.30,0.38,0.85),'sugar_green':(0.03,0.50,0.15),
     'sugar_pink':(0.75,0.30,0.65),'cholesterol':(0.45,0.80,0.15)}
NAMES=list(CLS); I={n:i for i,n in enumerate(NAMES)}
def classify(co,no,R,th):
    x,y,z=co.T; nv=len(co); lab=np.full(nv,I['tail'])
    top=z>-0.005; bot=z<-0.295; above=z>0.13
    lab[top]=I['head_top']; lab[bot]=I['head_bot']
    planar=((np.abs(no[:,0])>0.95)|(np.abs(no[:,1])>0.95))&(z>-0.29)&(z<-0.01)&(R>0.03)
    lab[planar]=I['slab']
    lab[(z>-0.29)&(z<-0.01)&(th>0.06)]=I['slab']
    lab[above&(R>0.02)]=I['sugar_green']; lab[above&(R<=0.02)]=I['sugar_pink']
    def disk(cx,cy,r): return (x-cx)**2+(y-cy)**2<r*r
    P=np.zeros(nv,bool)
    P|=(x>0.06)&(x<0.42)&(z>-0.45)&(z<0.125)&(((z<=0.0)&(y<-0.35))|(y<-0.56))          # canal
    P|=(x>-0.21)&(x<0.0)&(y<-0.64)&(R<0.03)                               # alfa-helice
    P|=(disk(-0.40,0.20,0.12)&(z>0.10)&(z<0.20))|(disk(-0.40,0.20,0.08)&(z>0.04)&(z<0.2))                  # glicoproteina 1
    P|=(disk(0.18,0.22,0.12)&(z>0.10)&(z<0.20))|(disk(0.18,0.22,0.08)&(z>0.04)&(z<0.2))                   # glicoproteina 2
    P|=disk(-0.65,-0.45,0.12)&(z>0.03)&(z<0.2)                  # globular
    P|=(x>0.55)&(y>-0.12)&(y<0.22)&(R>0.022)                              # integral
    P|=(x>0.45)&(y>-0.34)&(y<-0.10)&(z<-0.33)                   # periferica
    lab[P&~(above&(R<=0.02))]=I['protein']
    lab[(x>0.55)&(y>0.35)&(y<0.56)&(z>-0.16)&(z<0.06)]=I['cholesterol']
    return lab
