import io, sys

import os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'game.html')
OUT = os.path.join(HERE, '..', 'index.html')
OUT2 = os.path.join(HERE, '..', 'demo3d.html')   # the old demo link keeps working
s = io.open(SRC, encoding='utf-8').read()
subs = []

# ---------------------------------------------------------------- 3D helpers
subs.append(('''// ---- mouse passing
var cam={x:FW/2,y:FH/2}, scale=1, VW=0, VH=0, dpr=1;
function screenToWorld(cx,cy){
  var r=cv.getBoundingClientRect();
  return { x: cam.x + (cx-r.left-VW/2)/scale, y: cam.y + (cy-r.top-VH/2)/scale };
}''', '''// ---- mouse passing
var cam={x:FW/2,y:FH/2}, scale=1, VW=0, VH=0, dpr=1;
function screenToWorld(cx,cy){
  var r=cv.getBoundingClientRect();
  if(VIEW3D && P3LAST){
    var P=P3LAST, sy2=cy-r.top, sx2=cx-r.left;
    var zc=P.K/Math.max(1,(sy2-P.hz));
    return { x: P.camx + (sx2-P.cx)*zc/(P.S0*P.Z0), y: P.camy + P.Z0 - zc };
  }
  return { x: cam.x + (cx-r.left-VW/2)/scale, y: cam.y + (cy-r.top-VH/2)/scale };
}

// ================================================================ 2.5D view
// Flat 2D players standing on a field seen from a broadcast camera up in the
// stands. The ground is drawn in perspective row by row (far rows shrink),
// and each player is drawn at his projected spot, scaled by his distance.
var VIEW3D=true, P3LAST=null;
var Z3=820, TILT3=0.60, BASE3=1.7;    // camera distance, ground foreshortening, base zoom
window.addEventListener('keydown',function(e){
  if(e.key==='v'||e.key==='V'){ VIEW3D=!VIEW3D; }
});
var W3=null, MAIN3=null;
function makeW3(){
  var M=300, MT=640, MB=220;
  var c=document.createElement('canvas');
  c.width=FW+2*M; c.height=MT+FH+MB;
  var base=document.createElement('canvas'); base.width=c.width; base.height=c.height;
  var g=base.getContext('2d');
  // apron round the field
  g.fillStyle='#16311f'; g.fillRect(0,0,base.width,base.height);
  // the far stands: tiers of crowd climbing away from the field
  var top=MT-120;
  var sg=g.createLinearGradient(0,0,0,top);
  sg.addColorStop(0,'#0b0f16'); sg.addColorStop(1,'#1c2433');
  g.fillStyle=sg; g.fillRect(0,0,base.width,top);
  var seed=7; function rnd(){ seed=(seed*16807)%2147483647; return seed/2147483647; }
  var cols=['#c9d3e0','#2d477f','#8c1a24','#e8c14a','#f1f1ec','#51607a','#a8232f','#233a6e'];
  for(var ty=18; ty<top-8; ty+=9){
    g.fillStyle='rgba(0,0,0,.35)'; g.fillRect(0,ty+6,base.width,2);        // tier edge
    for(var tx=4; tx<base.width; tx+=5+rnd()*3){
      g.fillStyle=cols[(rnd()*cols.length)|0];
      g.globalAlpha=0.45+rnd()*0.45;
      g.fillRect(tx, ty+rnd()*2, 3, 4);
    }
  }
  g.globalAlpha=1;
  // wall and ad boards between the stands and the field
  g.fillStyle='#0d1a2e'; g.fillRect(0,top,base.width,26);
  g.fillStyle='#ffd23f'; g.font='700 18px "Anton", sans-serif'; g.textBaseline='middle';
  for(var ax=40; ax<base.width; ax+=420){
    g.fillText('GRIDIRON HEROES', ax, top+13);
  }
  // near side: bench area
  g.fillStyle='#12281a'; g.fillRect(0,MT+FH+40,base.width,MB-40);
  // the field itself
  g.drawImage(fieldCanvas, M, MT);
  // the white border: out of bounds starts on the paint
  var BW=YD*0.9;
  g.fillStyle='#eef3e8';
  g.fillRect(M-BW, MT-BW, FW+2*BW, BW);            // far sideline
  g.fillRect(M-BW, MT+FH, FW+2*BW, BW);            // near sideline
  g.fillRect(M-BW, MT-BW, BW, FH+2*BW);            // end lines
  g.fillRect(M+FW, MT-BW, BW, FH+2*BW);
  // coaching box dashes on the near side
  g.strokeStyle='rgba(255,210,63,.55)'; g.lineWidth=2; g.setLineDash([10,8]);
  g.beginPath(); g.moveTo(M+EZ+25*YD, MT+FH+BW+2.2*YD); g.lineTo(M+FW-EZ-25*YD, MT+FH+BW+2.2*YD); g.stroke();
  g.setLineDash([]);
  return {cv:c, g:c.getContext('2d'), base:base, M:M, MT:MT};
}
// Everything that must stay on screen this frame.
function camPoints(){
  var pts=[]; if(!G) return pts;
  if(G.ball) pts.push([G.ball.x,G.ball.y]);
  if(G.thrown){
    pts.push([G.thrown.tx,G.thrown.ty]);
    if(G.thrown.target) pts.push([G.thrown.target.x,G.thrown.target.y]);
  }
  var c=G.carrier, bx=G.ball?G.ball.x:FW/2, by=G.ball?G.ball.y:FH/2;
  var live=(G.phase==='live');
  var passing=live && c && c.role==='QB' && !G.thrown && !pastTheLine(c);
  for(var i=0;i<G.players.length;i++){
    var q=G.players[i];
    if(!isFinite(q.x)||!isFinite(q.y)) continue;
    if(!live){
      if(Math.hypot(q.x-bx,q.y-by)<24*YD) pts.push([q.x,q.y]);
      continue;
    }
    if(q===c || q===G.controlled){ pts.push([q.x,q.y]); continue; }
    // while you are passing, every man you can throw to has to be visible
    if(passing && q.team===G.offense && q.role!=='C' && q.role!=='OL' && q.role!=='BL'){
      if(Math.hypot(q.x-c.x,q.y-c.y)<45*YD) pts.push([q.x,q.y]);
      continue;
    }
    // with a runner, the men closing on him
    if(c && !passing && q.team!==c.team && Math.hypot(q.x-c.x,q.y-c.y)<9*YD) pts.push([q.x,q.y]);
  }
  return pts;
}
// Largest zoom that keeps every point inside the safe frame. Screen offsets
// from centre are exactly proportional to the zoom for a fixed camera, so
// this is one pass, no search.
function camFit(pts,camx,camy){
  var Z0=Z3, c=TILT3, best=9;
  for(var i=0;i<pts.length;i++){
    var zc=Math.max(160, Z0-(pts[i][1]-camy));
    var ox=(pts[i][0]-camx)*Z0/zc, oy=c*Z0*(Z0/zc-1);
    if(Math.abs(ox)>1) best=Math.min(best,(VW/2-60)/Math.abs(ox));
    if(oy<-1) best=Math.min(best,(VH/2-100)/(-oy));
    else if(oy>1) best=Math.min(best,(VH/2-80)/oy);
  }
  return best;
}
function setupProj(sx,sy){
  var want=BASE3*CAM3.z, fit=camFit(camPoints(),cam.x,cam.y);
  var tgt=Math.max(0.35,Math.min(want,fit));
  if(!CAM3.S) CAM3.S=tgt;
  // pull out fast so nothing leaves the frame, push in gently
  CAM3.S += (tgt-CAM3.S)*(tgt<CAM3.S?0.3:0.06);
  var S0=CAM3.S, Z0=Z3, c=TILT3;
  var K=c*S0*Z0*Z0;
  var P={S0:S0, Z0:Z0, K:K, hz:VH/2+sy - c*S0*Z0, cx:VW/2+sx, camx:cam.x, camy:cam.y};
  P3LAST=P; return P;
}
function proj3(P,wx,wy){
  var zc=Math.max(60, P.Z0-(wy-P.camy)), s=P.S0*P.Z0/zc;
  return {x:P.cx+(wx-P.camx)*s, y:P.hz+P.K/zc, s:s};
}
function at3D(P,wx,wy){
  var q=proj3(P,wx,wy);
  ctx.setTransform(dpr*q.s,0,0,dpr*q.s, dpr*(q.x-wx*q.s), dpr*(q.y-wy*q.s));
}
function blit3D(P){
  ctx.setTransform(dpr,0,0,dpr,0,0);
  // night sky and the upper deck, behind everything
  var sk=ctx.createLinearGradient(0,0,0,VH*0.5);
  sk.addColorStop(0,'#05070b'); sk.addColorStop(1,'#141b27');
  ctx.fillStyle=sk; ctx.fillRect(0,0,VW,VH);
  var src=W3.cv, STEP=2;
  for(var y=0; y<VH; y+=STEP){
    if(y-P.hz<2) continue;
    var zc0=P.K/(y-P.hz), zc1=P.K/(y+STEP-P.hz);
    var wy0=P.camy+P.Z0-zc0, wy1=P.camy+P.Z0-zc1;
    var s=P.S0*P.Z0/zc0, hw=(VW/2)/s;
    var sx0=P.camx-hw+W3.M, sy0=wy0+W3.MT, sw=2*hw, sh=Math.max(0.35,wy1-wy0);
    var dx=P.cx-VW/2, dw=VW;
    // clip the source to the canvas, moving the destination with it
    if(sy0<0 || sy0+sh>src.height) continue;
    if(sx0<0){ var cut=-sx0; dx+=cut*s; dw-=cut*s; sw-=cut; sx0=0; }
    if(sx0+sw>src.width){ var cut2=sx0+sw-src.width; dw-=cut2*s; sw-=cut2; }
    if(sw<=1||dw<=1) continue;
    ctx.drawImage(src, sx0, sy0, sw, sh, dx, y, dw, STEP+0.6);
  }
  // haze toward the far side sells the distance
  var hz=ctx.createLinearGradient(0,0,0,VH*0.45);
  hz.addColorStop(0,'rgba(10,14,22,.55)'); hz.addColorStop(1,'rgba(10,14,22,0)');
  ctx.fillStyle=hz; ctx.fillRect(0,0,VW,VH*0.45);
  // stadium lights
  for(var li=0; li<4; li++){
    var lx=VW*(0.12+li*0.25), ly=VH*0.03;
    var lg=ctx.createRadialGradient(lx,ly,0,lx,ly,VW*0.14);
    lg.addColorStop(0,'rgba(255,250,225,.30)'); lg.addColorStop(1,'rgba(255,250,225,0)');
    ctx.fillStyle=lg; ctx.fillRect(lx-VW*0.14,0,VW*0.28,VW*0.14);
  }
}

// ---- dynamic camera: wide before the snap, tight on the action, a quick
// punch-in on big hits and hero moves, and a pull-back on a breakaway so you
// can see the end zone and whoever is chasing.
var CAM3={z:0.86, actUntil:0, ax:0, ay:0, prevShake:0, prevSpin:0};
function camMood(now){
  if(CAM3.actUntil>now) return 1.55;
  if(!G || G.phase!=='live') return 0.86;
  if(G.thrown) return 0.92;
  var c=G.carrier;
  if(!c) return 1.0;
  if(c.role==='QB' && !pastTheLine(c)) return 1.0;
  var dfn=nearestOf(c, c.team==='H'?'A':'H');
  var dd=dfn?Math.hypot(dfn.x-c.x,dfn.y-c.y):999;
  var past=(c.x-G.los)*dir();
  if(dd>8*YD && past>3*YD) return 0.8;
  return 1.14;
}
function camDirect(){
  var now=performance.now();
  if(G && G.phase==='live'){
    var c=G.carrier, sp=c?(c.spin||0):0;
    if(G.shake > CAM3.prevShake+2 || (sp>0.85 && CAM3.prevSpin<=0.85)){
      CAM3.actUntil=now+620; CAM3.ax=G.ball.x; CAM3.ay=G.ball.y;
    }
    CAM3.prevSpin=sp;
  }
  CAM3.prevShake=G?G.shake:0;
  var zt=camMood(now), act=CAM3.actUntil>now;
  CAM3.z += (zt-CAM3.z)*(act?0.2:0.05);
  return act;
}

// A proper spin: two quick turns, a whirl round his waist, afterimages.
function swirl(p,lift,front){
  var u=p.spin, ph=u*Math.PI*6;
  ctx.save();
  ctx.lineCap='round';
  for(var k=0;k<3;k++){
    var a0=ph+k*2.09;
    var a=((a0%(Math.PI*2))+Math.PI*2)%(Math.PI*2);
    var isFront = a<Math.PI;
    if(isFront!==front) continue;
    ctx.strokeStyle='rgba(190,230,255,'+(0.75*Math.min(1,u*2)).toFixed(2)+')';
    ctx.lineWidth=2.2;
    ctx.beginPath();
    ctx.ellipse(p.x, p.y-15-lift, 14, 5, 0, a, a+1.1);
    ctx.stroke();
  }
  ctx.restore();
}'''))

# ---------------------------------------------------------------- draw(): ground into the world canvas
subs.append(('''  ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.fillStyle='#0c1114'; ctx.fillRect(0,0,VW,VH);
  ctx.save();
  ctx.translate(VW/2+sx,VH/2+sy); ctx.scale(scale,scale); ctx.translate(-cam.x,-cam.y);
''', '''  ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.fillStyle='#0c1114'; ctx.fillRect(0,0,VW,VH);
  if(!MAIN3) MAIN3=ctx;
  ctx=MAIN3;                         // never left pointing at the ground canvas
  var P3 = VIEW3D ? setupProj(sx,sy) : null, realCtx3=ctx;
  if(P3){
    if(!W3) W3=makeW3();
    ctx=W3.g; ctx.setTransform(1,0,0,1,0,0); ctx.drawImage(W3.base,0,0);
    ctx.save(); ctx.translate(W3.M, W3.MT);
  } else {
    ctx.save();
    ctx.translate(VW/2+sx,VH/2+sy); ctx.scale(scale,scale); ctx.translate(-cam.x,-cam.y);
  }
'''))

subs.append(('''  // depth sort so players nearer the bottom overlap the ones behind them
  var order=G.players.slice().sort(function(a,b){ return a.y-b.y; });
  for(var i=0;i<order.length;i++) drawGuy(order[i]);
''', '''  if(P3){ ctx.restore(); ctx=realCtx3; blit3D(P3); ctx.save(); }

  // depth sort so players nearer the bottom overlap the ones behind them
  var order=G.players.slice().sort(function(a,b){ return a.y-b.y; });
  for(var i=0;i<order.length;i++){
    if(P3) at3D(P3,order[i].x,order[i].y);
    drawGuy(order[i]);
  }
'''))

subs.append(('''    ctx.globalAlpha=k2;
    if(e.ringed){''', '''    if(P3) at3D(P3,e.x,e.y);
    ctx.globalAlpha=k2;
    if(e.ringed){'''))

subs.append(('''  if(G.kick) drawKick();
  else if(G.thrown||(G.ball&&!G.ball.held)) drawBall();
  ctx.restore();
}''', '''  if(P3 && G.ball) at3D(P3,G.ball.x,G.ball.y);
  if(G.kick) drawKick();
  else if(G.thrown||(G.ball&&!G.ball.held)) drawBall();
  ctx.restore();
  if(P3){
    ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.fillStyle='rgba(8,12,16,.55)'; ctx.fillRect(VW/2-80,VH-28,160,18);
    ctx.fillStyle='#ffd23f'; ctx.font='700 12px "Barlow Condensed", sans-serif';
    ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('PRESS V FOR FLAT VIEW', VW/2, VH-19);
  }
}'''))

subs.append(('''  scale += (want-scale)*0.06;

  // centre mostly on the ball so the play stays where your eye already is
  var cx=(minX+maxX)/2, cy=(minY+maxY)/2+(padTop-padBot)/2;
  var tx=bx*0.62+cx*0.38, ty=by*0.62+cy*0.38;
  if(!isFinite(tx)) tx=FW/2;
  if(!isFinite(ty)) ty=FH/2;
  cam.x += (tx-cam.x)*0.11; cam.y += (ty-cam.y)*0.11;''', '''  scale += (want-scale)*0.06;

  // centre mostly on the ball so the play stays where your eye already is
  var cx=(minX+maxX)/2, cy=(minY+maxY)/2+(padTop-padBot)/2;
  var tx=bx*0.62+cx*0.38, ty=by*0.62+cy*0.38;
  var actCam = VIEW3D ? camDirect() : false;
  if(actCam){ tx=CAM3.ax; ty=CAM3.ay; }
  else if(VIEW3D){
    var cp=camPoints();
    if(cp.length){
      var x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
      for(var ci=0;ci<cp.length;ci++){
        x0=Math.min(x0,cp[ci][0]); x1=Math.max(x1,cp[ci][0]);
        y0=Math.min(y0,cp[ci][1]); y1=Math.max(y1,cp[ci][1]);
      }
      tx=(x0+x1)/2*0.6+bx*0.4; ty=(y0+y1)/2*0.6+by*0.4;
    }
  }
  if(!isFinite(tx)) tx=FW/2;
  if(!isFinite(ty)) ty=FH/2;
  var follow = actCam ? 0.2 : (VIEW3D ? 0.15 : 0.11);
  cam.x += (tx-cam.x)*follow; cam.y += (ty-cam.y)*follow;'''))


# ---------------------------------------------------------------- camera clamp + out of bounds
subs.append(("""  var halfW=VW/scale/2, halfH=VH/scale/2;
  cam.x = (FW>halfW*2) ? Math.max(halfW,Math.min(FW-halfW,cam.x)) : FW/2;
  cam.y = (FH>halfH*2) ? Math.max(halfH,Math.min(FH-halfH,cam.y)) : FH/2;""",
"""  var halfW=VW/scale/2, halfH=VH/scale/2;
  if(VIEW3D){
    // The 3D camera frames the play itself (camFit). The flat view's limits
    // pinned it near midfield, so a return toward either end zone ran off
    // the screen while the camera zoomed out after it.
    cam.x=Math.max(0,Math.min(FW,cam.x)); cam.y=Math.max(0,Math.min(FH,cam.y));
  } else {
    cam.x = (FW>halfW*2) ? Math.max(halfW,Math.min(FW-halfW,cam.x)) : FW/2;
    cam.y = (FH>halfH*2) ? Math.max(halfH,Math.min(FH-halfH,cam.y)) : FH/2;
  }"""))
subs.append(("""    if(G.carrier.y<=9 || G.carrier.y>=FH-9){""",
             """    if(G.carrier.y<=0 || G.carrier.y>=FH){          // over the white line"""))
subs.append(("""    pp3.y=Math.max(8,Math.min(FH-8,pp3.y));""",
             """    pp3.y=Math.max(-SIDE_OUT,Math.min(FH+SIDE_OUT,pp3.y));"""))
subs.append(("""var TACKLE_R=23, CATCH_R=17, BLOCK_R=21;""",
             """var TACKLE_R=23, CATCH_R=17, BLOCK_R=21;
var SIDE_OUT=3*14;   // how far past the sideline a man can run: the out of bounds area"""))


# ---------------------------------------------------------------- click picking uses the 3D projection
subs.append(("""function worldToScreen(wx,wy){""",
             """function worldToScreen(wx,wy){
  if(VIEW3D && P3LAST) return proj3(P3LAST,wx,wy);"""))

# ---------------------------------------------------------------- spin
subs.append(('''  ctx.save();
  ctx.translate(p.x,p.y-lift);
  ctx.scale(p.face,1);
  if(p.spin>0){
    var spc=Math.cos(p.spin*Math.PI*2);''', '''  if(p.spin>0) swirl(p,lift,false);
  ctx.save();
  ctx.translate(p.x,p.y-lift);
  ctx.scale(p.face,1);
  if(p.spin>0){
    var spc=Math.cos(p.spin*Math.PI*4);'''))
subs.append(('''  if(SPR.ready){ drawSprite(p); ctx.restore(); heroTag(p,lift); return; }''',
             '''  if(SPR.ready){ drawSprite(p); ctx.restore(); if(p.spin>0) swirl(p,lift,true); heroTag(p,lift); return; }'''))
subs.append(('''    if(q.spin>0) q.spin=Math.max(0,q.spin-dt*2.1);''',
             '''    if(q.spin>0){ q.spin=Math.max(0,q.spin-dt*2.1); if(Math.random()<dt*45) ghost(q); }'''))


ok = True
for old, new in subs:
    n = s.count(old)
    if n != 1:
        print('ANCHOR FAIL (%d matches): %r' % (n, old[:80])); ok = False
if not ok:
    print('NOTHING WRITTEN'); sys.exit(1)
for old, new in subs:
    s = s.replace(old, new, 1)
CL_OLD="q.y=Math.max(8,Math.min(FH-8,q.y)); q.x=Math.max(6,Math.min(FW-6,q.x));"
assert s.count(CL_OLD)==2, 'clamp count'
s=s.replace(CL_OLD,"q.y=Math.max(-SIDE_OUT,Math.min(FH+SIDE_OUT,q.y)); q.x=Math.max(6,Math.min(FW-6,q.x));")
io.open(OUT, 'w', encoding='utf-8', newline='').write(s)
io.open(OUT2, 'w', encoding='utf-8', newline='').write(s)
print('wrote index.html (3D) and demo3d.html with %d anchors' % len(subs))
