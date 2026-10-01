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
  var M=700, MT=640, MB=220;        // wide margins: the stadium carries on past both end zones
  var c=document.createElement('canvas');
  c.width=FW+2*M; c.height=MT+FH+MB;
  var base=document.createElement('canvas'); base.width=c.width; base.height=c.height;
  var g=base.getContext('2d');
  // apron round the field
  g.fillStyle='#1d4a2c'; g.fillRect(0,0,base.width,base.height);
  // the far stands: tiers of crowd climbing away from the field
  var top=MT-120;
  // The crowd is painted three times with the same fans in the same seats;
  // in frames 1 and 2 a different handful are up with their arms raised.
  // Cycling the frames makes the stands move, faster when they are cheering.
  function paintCrowd(gc, frame){
    var sg=gc.createLinearGradient(0,0,0,top);
    sg.addColorStop(0,'#0b0f16'); sg.addColorStop(1,'#1c2433');
    gc.fillStyle=sg; gc.fillRect(0,0,base.width,top);
    var seed=7; function rnd(){ seed=(seed*16807)%2147483647; return seed/2147483647; }
    var s2=frame*977+13; function rnd2(){ s2=(s2*16807)%2147483647; return s2/2147483647; }
    var cols=['#c9d3e0','#2d477f','#8c1a24','#e8c14a','#f1f1ec','#51607a','#a8232f','#233a6e'];
    for(var ty=18; ty<top-8; ty+=9){
      gc.fillStyle='rgba(0,0,0,.35)'; gc.fillRect(0,ty+6,base.width,2);       // tier edge
      for(var tx=4; tx<base.width; tx+=5+rnd()*3){
        var col=cols[(rnd()*cols.length)|0], al=0.45+rnd()*0.45, jy=rnd()*2;
        var up = frame>0 && rnd2()<0.28;
        gc.fillStyle=col; gc.globalAlpha=al;
        gc.fillRect(tx, ty+jy-(up?2:0), 3, 4);
        if(up){ gc.fillStyle='rgba(240,220,190,.85)'; gc.fillRect(tx+0.5, ty+jy-4.5, 2, 2); }   // hands up
      }
    }
    gc.globalAlpha=1;
  }
  paintCrowd(g,0);
  var crowd=[];
  for(var cf=0;cf<3;cf++){
    var ccv=document.createElement('canvas'); ccv.width=base.width; ccv.height=top;
    paintCrowd(ccv.getContext('2d'),cf); crowd.push(ccv);
  }
  // wall and ad boards between the stands and the field
  g.fillStyle='#0d1a2e'; g.fillRect(0,top,base.width,26);
  g.fillStyle='#ffd23f'; g.font='700 18px "Anton", sans-serif'; g.textBaseline='middle';
  for(var ax=40; ax<base.width; ax+=420){
    g.fillText('HAIL MYTHERY', ax, top+13);
  }
  // near side: bench area
  g.fillStyle='#173d25'; g.fillRect(0,MT+FH+40,base.width,MB-40);
  function bench(wx0,wx1,wy,col){
    var by=MT+wy;
    g.fillStyle='rgba(0,0,0,.35)'; g.fillRect(M+wx0, by+10, wx1-wx0, 6);   // its shadow
    g.fillStyle='#3b4452'; g.fillRect(M+wx0, by, wx1-wx0, 10);
    g.fillStyle=col; g.fillRect(M+wx0, by, wx1-wx0, 3);
  }
  function tent(wx,wy,col,label){
    var tx2=M+wx, ty2=MT+wy;
    g.fillStyle='rgba(0,0,0,.3)'; g.fillRect(tx2-38,ty2+22,76,8);
    g.fillStyle=col; g.fillRect(tx2-36,ty2-14,72,36);
    g.fillStyle='rgba(255,255,255,.16)'; for(var sti=0;sti<6;sti++) g.fillRect(tx2-36+sti*12,ty2-14,6,36);
    g.fillStyle='#f1f1ec'; g.font='700 16px "Anton", sans-serif';
    g.textAlign='center'; g.textBaseline='middle'; g.fillText(label,tx2,ty2+4); g.textAlign='left';
  }
  bench(FW*0.36, FW*0.64, FH+7*YD, '#2d477f');                    // home bench, near side
  tent(FW*0.33, FH+8*YD, '#1f2d54', 'HM'); tent(FW*0.67, FH+8*YD, '#1f2d54', 'HM');
  bench(FW*0.36, FW*0.64, -5.4*YD, '#8c1a24');                    // visitors, far side
  tent(FW*0.33, -5.2*YD, '#6e1520', 'RIV'); tent(FW*0.67, -5.2*YD, '#6e1520', 'RIV');
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
  // pools of light on the turf under each tower, baked in once
  g.save(); g.globalCompositeOperation='lighter';
  [0.18,0.4,0.6,0.82].forEach(function(fx){
    var px=M+FW*fx, py=MT+FH*0.5, pr=FH*0.75;
    var pg=g.createRadialGradient(px,py,0,px,py,pr);
    pg.addColorStop(0,'rgba(255,248,225,.075)'); pg.addColorStop(1,'rgba(255,248,225,0)');
    g.fillStyle=pg; g.fillRect(px-pr,py-pr,pr*2,pr*2);
  });
  g.restore();
  var w3g=c.getContext('2d'); w3g.drawImage(base,0,0);   // painted in full once, then patched
  return {cv:c, g:w3g, base:base, M:M, MT:MT, dirty:[], crowd:crowd};
}
// Everything that must stay on screen this frame.
function camPoints(){
  var pts=[]; if(!G) return pts;
  if(G.broadcast && G.broadcast.until>performance.now() && G.broadcast.p){
    return [[G.broadcast.p.x, G.broadcast.p.y]];            // only him, so the zoom can go in
  }
  if(G.phase==='live' && G.carrier && G.brawlUntil>performance.now()){
    return [[G.carrier.x, G.carrier.y]];                    // a clinch with your man in it: only the fight
  }
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
      if(Math.hypot(q.x-bx,q.y-by)<(TOUCH_UI?15:24)*YD) pts.push([q.x,q.y]);
      continue;
    }
    if(q===c || q===G.controlled){ pts.push([q.x,q.y]); continue; }
    // while you are passing, every man you can throw to has to be visible
    if(passing && q.team===G.offense && q.role!=='C' && q.role!=='OL' && q.role!=='BL'){
      if(Math.hypot(q.x-c.x,q.y-c.y)<(TOUCH_UI?34:45)*YD) pts.push([q.x,q.y]);   // deep men pull it back, never in
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
    var mx=TOUCH_UI?VW*0.05:60, mt=TOUCH_UI?VH*0.16:100, mb=TOUCH_UI?VH*0.24:80;   // phone: clear of the move buttons along the bottom
    if(Math.abs(ox)>1) best=Math.min(best,(VW/2-mx)/Math.abs(ox));
    if(oy<-1) best=Math.min(best,(VH/2+STAND_OFF()-mt)/(-oy));
    else if(oy>1) best=Math.min(best,(VH/2-STAND_OFF()-mb)/oy);
  }
  return best;
}
// Where the ground marks will be drawn this frame, in world-canvas pixels.
function dirtyRects3(){
  var out=[], M=W3.M, MT=W3.MT, cw=W3.cv.width, ch=W3.cv.height;
  function add(x,y,w,h){
    x=Math.max(0,Math.floor(x)); y=Math.max(0,Math.floor(y));
    w=Math.min(cw-x,Math.ceil(w)); h=Math.min(ch-y,Math.ceil(h));
    if(w>0&&h>0) out.push([x,y,w,h]);
  }
  add(M+G.los-5, MT-2, 10, FH+4);                               // line of scrimmage
  var fd=G.los+G.toGo*YD*dir();
  add(M+fd-5, MT-2, 10, FH+4);                                  // first-down line
  if(G.carrier && G.mouse && G.mouse.on){                       // pass aim marker
    var tg=aimTarget(), cx=G.carrier.x, cy=G.carrier.y;
    var x0=Math.min(cx, tg?tg.x:cx)-45, x1=Math.max(cx, tg?tg.x:cx)+45;
    var y0=Math.min(cy, tg?tg.y:cy)-45, y1=Math.max(cy, tg?tg.y:cy)+30;
    add(M+x0, MT+y0, x1-x0, y1-y0);
  }
  if(G.drag && G.controlled){                                   // tackle wind-up line
    add(M+G.controlled.x-90, MT+G.controlled.y-100, 180, 180);
  }
  return out;
}
// Players standing on both sidelines: not in the game, just there. They sway
// in place and the scoring side jumps around on a touchdown. Only the ones on
// screen are drawn.
var SIDE3=null;
function sidelineGuys(P){
  if(!SIDE3){
    SIDE3=[];
    for(var i=0;i<16;i++){
      var home=i<8, k=i%8;
      SIDE3.push({team:home?'H':'A', role:(k%3===0)?'OL':'WR', pos:'', num:(home?40:60)+k*3, name:'',
        x:FW*(0.38+k*0.034)+(k%2?6:-6), y: home ? FH+5.4*YD+(k%2)*8 : -3.6*YD-(k%2)*8,
        vx:0, vy:0, face:(k%2?1:-1), run:k*1.7, spd:1, pwr:1, agi:1, lean:0, spin:0, z:0, arm:0,
        throwArm:0, phase:0, stun:0, cel:0, celKind:'pump', burst:0, hero:false, stance:0,
        hp:100, down:0, iFrames:0, wrapped:0});
    }
  }
  var out=[], cheer=(G.celebrate>0)?G.scoringTeam:null, tt=performance.now()/1000;
  for(var j=0;j<SIDE3.length;j++){
    var sp=SIDE3[j], q=proj3(P,sp.x,sp.y);
    if(q.y<-80 || q.y>VH+120 || q.x<-80 || q.x>VW+80) continue;
    sp.run+=0.02;
    sp.cel = (cheer===sp.team) ? 0.25+0.25*Math.abs(Math.sin(tt*5+j)) : 0;
    out.push(sp);
  }
  return out;
}
function STAND_OFF(){ return TOUCH_UI ? VH*0.08 : VH*0.08; }   // how far the field sits below centre (a phone keeps it high: less stand, more field)
function setupProj(sx,sy){
  var want=BASE3*CAM3.z, fit=camFit(camPoints(),cam.x,cam.y);
  // How far out the camera may pull scales with the screen's height: a phone
  // held sideways has under 400 pixels for the field, and with a fixed floor
  // half the play hung off the bottom of it (players get smaller, never cut)
  var floor=BASE3*0.62*Math.max(0.5, Math.min(1, VH/700));
  var tgt=Math.max(floor, Math.min(want,fit));
  if(!CAM3.S) CAM3.S=tgt;
  // pull out fast so nothing leaves the frame, push in gently
  CAM3.S += (tgt-CAM3.S)*(tgt<CAM3.S?(TOUCH_UI?0.12:0.3):((G && G.brawlUntil>performance.now())?0.1:(TOUCH_UI?0.035:0.06)));
  var S0=CAM3.S, Z0=Z3, c=TILT3;
  var K=c*S0*Z0*Z0;
  var P={S0:S0, Z0:Z0, K:K, hz:VH/2+STAND_OFF()+sy - c*S0*Z0, cx:VW/2+sx, camx:cam.x, camy:cam.y};
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
  hz.addColorStop(0,'rgba(10,14,22,.38)'); hz.addColorStop(1,'rgba(10,14,22,0)');
  ctx.fillStyle=hz; ctx.fillRect(0,0,VW,VH*0.45);
  // Light towers and the scoreboard are planted at the back of the stands and
  // projected like everything else, so they stay put as the camera moves.
  // (They used to be drawn at fixed screen positions and slid with the pan.)
  // Across the screen they sit where the stadium puts them, so they pan with
  // the stands. Up and down they are held in the strip of stands along the top
  // of the screen (below the scoreboard bar), and hidden when the camera is too
  // close for that strip to exist, rather than hanging over the field.
  var LT=[0.1,0.37,0.63,0.9], backY=-W3.MT+40;
  var wallY=proj3(P, FW/2, -120).y, topBand=3;
  ctx.save();
  for(var li=0; li<LT.length; li++){
    var tq=proj3(P, FW*LT[li], backY), ls=Math.max(0.55,tq.s), lamp=6*ls;
    var lx=tq.x, ly=Math.max(topBand+lamp*2, tq.y-120*ls);
    if(lx<-VW*0.3 || lx>VW*1.3 || ly>wallY-lamp*3) continue;
    ctx.globalCompositeOperation='source-over';
    ctx.fillStyle='#1a2130'; ctx.fillRect(lx-lamp*0.4, ly+lamp*1.9, lamp*0.8, Math.max(0,Math.min(tq.y,wallY)-ly-lamp*1.9));   // the mast
    ctx.fillStyle='#0b0f16'; ctx.fillRect(lx-lamp*4.2, ly-lamp*1.9, lamp*8.4, lamp*3.8);          // the frame
    ctx.globalCompositeOperation='lighter';
    ctx.fillStyle='rgba(255,248,220,.95)';
    for(var lr=0; lr<2; lr++) for(var lc=0; lc<5; lc++)
      ctx.fillRect(lx-lamp*3.6+lc*lamp*1.5, ly-lamp*1.4+lr*lamp*1.5, lamp*1.1, lamp*1.1);
    var BR=260*ls;
    var bl=ctx.createRadialGradient(lx,ly,0,lx,ly,BR);
    bl.addColorStop(0,'rgba(255,246,215,.42)'); bl.addColorStop(0.25,'rgba(255,240,200,.12)'); bl.addColorStop(1,'rgba(255,240,200,0)');
    ctx.fillStyle=bl; ctx.fillRect(lx-BR, ly-BR, BR*2, BR*2);
    var FLW=200*ls, fl=ctx.createLinearGradient(lx-FLW,0,lx+FLW,0);
    fl.addColorStop(0,'rgba(255,245,215,0)'); fl.addColorStop(0.5,'rgba(255,245,215,.28)'); fl.addColorStop(1,'rgba(255,245,215,0)');
    ctx.fillStyle=fl; ctx.fillRect(lx-FLW, ly-1, FLW*2, 2);
    var gq=proj3(P, FW*LT[li], FH*0.5), CW=170*gq.s;
    var cone=ctx.createLinearGradient(0,ly,0,gq.y);
    cone.addColorStop(0,'rgba(255,245,215,.07)'); cone.addColorStop(1,'rgba(255,245,215,0)');
    ctx.fillStyle=cone;
    ctx.beginPath(); ctx.moveTo(lx-lamp*4,ly); ctx.lineTo(lx+lamp*4,ly);
    ctx.lineTo(gq.x+CW,gq.y); ctx.lineTo(gq.x-CW,gq.y); ctx.closePath(); ctx.fill();
  }
  // the scoreboard over the stands at midfield
  ctx.globalCompositeOperation='source-over';
  var sbq=proj3(P, FW/2, backY), band=wallY-topBand;
  var sbh=Math.min(104*Math.max(0.55,sbq.s), band*0.82), sbs=sbh/104, sbw=sbh*2.9, sbx=sbq.x-sbw/2;
  var sby=Math.max(topBand+2, sbq.y-190*sbq.s);
  if(sby+sbh>wallY-4) sby=wallY-4-sbh;
  var pinned=TOUCH_UI;
  if(pinned){                                       // a phone: one place, one size, top centre, under the pre-snap bar
    sbh=Math.min(54, band*0.8); sbs=sbh/104; sbw=sbh*2.9; sbx=VW/2-sbw/2; sby=topBand+46;
  }
  if(band>34 && sby>=topBand-2 && (!pinned || sby+sbh<wallY)){
    if(!pinned){ ctx.fillStyle='#1a2130'; ctx.fillRect(sbq.x-6*sbs, sby+sbh, 12*sbs, sbq.y-sby-sbh); }
    ctx.fillStyle='#0b0f16'; ctx.fillRect(sbx-6*sbs, sby-6*sbs, sbw+12*sbs, sbh+12*sbs);
    ctx.fillStyle='#05070b'; ctx.fillRect(sbx, sby, sbw, sbh);
    ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.font='700 '+Math.max(6,22*sbs)+'px "Anton", sans-serif';
    ctx.fillStyle='#ffd23f'; ctx.fillText('HEROES', sbx+sbw*0.25, sby+sbh*0.28);
    ctx.fillStyle=FOE.lite; ctx.fillText(FOE.short, sbx+sbw*0.75, sby+sbh*0.28);
    ctx.font='700 '+Math.max(8,40*sbs)+'px "Anton", sans-serif'; ctx.fillStyle='#f1f1ec';
    ctx.fillText(String(G.scoreH||0), sbx+sbw*0.25, sby+sbh*0.66);
    ctx.fillText(String(G.scoreA||0), sbx+sbw*0.75, sby+sbh*0.66);
    var clk=Math.max(0,Math.ceil(G.clock||0)), mm=Math.floor(clk/60), ss=clk%60;
    ctx.font='700 '+Math.max(6,(G.training?11:18)*sbs)+'px "JetBrains Mono", monospace'; ctx.fillStyle='#ffd23f';
    ctx.fillText(G.training ? 'PRACTICE' : mm+':'+(ss<10?'0':'')+ss, sbx+sbw*0.5, sby+sbh*0.5);
    ctx.textAlign='left';
  }
  ctx.restore();
}

// ---- dynamic camera: wide before the snap, tight on the action, a quick
// punch-in on big hits and hero moves, and a pull-back on a breakaway so you
// can see the end zone and whoever is chasing.
var CAM3={z:0.86, actUntil:0, ax:0, ay:0, prevShake:0, prevSpin:0};
function camMood(now){
  if(CAM3.actUntil>now) return TOUCH_UI?1.25:1.55;
  if(G && G.phase==='heroIntro') return 1.9;        // close on the star as he walks out
  if(G && G.broadcast && G.broadcast.until>now) return G.broadcast.td ? (G.broadcast.wide ? 1.45 : (TOUCH_UI?2.2:2.4)) : (TOUCH_UI ? 1.3 : 1.85);   // in on the man who made the play (close in on a touchdown)
  if(G && G.phase==='live' && G.carrier && G.brawlUntil>now) return TOUCH_UI?1.05:1.45;   // in on a clinch your man is in, so you can see the punches
  if(G && playArtOn()) return 0.7;                   // pull back to read the play
  if(!G || G.phase!=='live') return TOUCH_UI ? 0.72 : 0.86;   // before the snap on a phone: the same framing as the play, no jump at the snap
  if(TOUCH_UI) return 0.72;                          // a phone holds one zoom through the play
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
    // no punch-in while the quarterback still has it behind the line: a hit on
    // him zoomed in and pushed the receivers off the screen mid-throw
    var passing3 = c && c.role==='QB' && !G.thrown && !pastTheLine(c);
    if(!TOUCH_UI && !passing3 && (G.shake > CAM3.prevShake+2 || (sp>0.85 && CAM3.prevSpin<=0.85))){   // no punch-ins on a phone
      CAM3.actUntil=now+620; CAM3.ax=G.ball.x; CAM3.ay=G.ball.y;
    }
    CAM3.prevSpin=sp;
  }
  CAM3.prevShake=G?G.shake:0;
  var zt=camMood(now), act=CAM3.actUntil>now;
  var tdz=!!(G && G.broadcast && G.broadcast.td && G.broadcast.until>now);
  var brz=!!(G && G.phase==='live' && G.brawlUntil>now);
  CAM3.z += (zt-CAM3.z)*(act?0.2:(tdz?0.08:(brz?0.12:(TOUCH_UI?0.03:0.05))));   // a phone eases between zooms; a touchdown or a clinch pushes in
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
    G._p3=true;
    ctx=W3.g; ctx.setTransform(1,0,0,1,0,0);
    // Only the lines and the aim marker change on the ground. Repainting the
    // whole field and stands every frame was millions of pixels a frame, which
    // made every input feel late. Put back just last frame's marks.
    for(var di=0;di<W3.dirty.length;di++){
      var rr=W3.dirty[di]; ctx.drawImage(W3.base,rr[0],rr[1],rr[2],rr[3],rr[0],rr[1],rr[2],rr[3]);
    }
    W3.dirty=dirtyRects3();
    var nowc=performance.now(), crowdMs=(G.celebrate>0 || G.phase==='heroIntro') ? 110 : 340;
    if(!W3.crowdT || nowc-W3.crowdT>crowdMs){
      W3.crowdT=nowc; W3.crowdK=((W3.crowdK||0)+1)%W3.crowd.length;
      ctx.drawImage(W3.crowd[W3.crowdK],0,0);
    }
    SKIP_FIELD=true;
    ctx.save(); ctx.translate(W3.M, W3.MT);
  } else {
    G._p3=false;
    ctx.save();
    ctx.translate(VW/2+sx,VH/2+sy); ctx.scale(scale,scale); ctx.translate(-cam.x,-cam.y);
  }
'''))

subs.append(('''  // depth sort so players nearer the bottom overlap the ones behind them
  var order=G.players.slice().sort(function(a,b){ return a.y-b.y; });
  for(var i=0;i<order.length;i++) drawGuy(order[i]);
''', '''  if(P3){ ctx.restore(); ctx=realCtx3; SKIP_FIELD=false; blit3D(P3); drawGoalposts(); ctx.save(); drawCracks(P3); }

  // depth sort so players nearer the bottom overlap the ones behind them
  var order=G.players.concat(P3?sidelineGuys(P3):[]).sort(function(a,b){ return a.y-b.y; });
  for(var i=0;i<order.length;i++){
    if(P3) at3D(P3,order[i].x,order[i].y);
    drawGuy(order[i]);
  }
'''))

subs.append(('''    ctx.globalAlpha=k2;
    if(e.ringed){''', '''    if(P3) at3D(P3,e.x,e.y);
    ctx.globalAlpha=k2;
    if(e.ringed){'''))

subs.append(('''  if(!G._p3) drawSnap(null);
  if(G.kick) drawKick();
  else if(G.thrown||(G.ball&&!G.ball.held)) drawBall();
  ctx.restore();
}''', '''  drawSnap(P3);
  if(P3 && G.ball) at3D(P3,G.ball.x,G.ball.y);
  if(G.kick) drawKick();
  else if(G.thrown||(G.ball&&!G.ball.held)) drawBall();
  ctx.restore();
  if(P3 && !TOUCH_UI){                            // no V key on a phone
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
  else if(VIEW3D && G.broadcast && G.broadcast.until>performance.now() && G.broadcast.p){
    tx=G.broadcast.p.x; ty=G.broadcast.p.y;
  }
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
  var tdCam=!!(G.broadcast && G.broadcast.td && G.broadcast.until>performance.now());
  if(TOUCH_UI && VIEW3D && G.phase!=='live' && !actCam && !tdCam) ty-=3*YD;   // a little tilt toward the stands before the snap
  if(!isFinite(tx)) tx=FW/2;
  if(!isFinite(ty)) ty=FH/2;
  var follow = actCam ? (TOUCH_UI?0.12:0.2) : (VIEW3D ? (TOUCH_UI?0.09:0.15) : 0.11);
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
