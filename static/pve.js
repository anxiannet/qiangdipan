let cardsData=null,duelData=null,base=[],G=null,chosen=null;
const $=id=>document.getElementById(id);
async function boot(){
  try{
    const [c,d]=await Promise.all([
      fetch('./data/cards.v1.json').then(r=>r.json()),
      fetch('./data/duel.v01.json').then(r=>r.json())
    ]);
    cardsData=c;duelData=d;buildBaseDeck();
    $('loading').style.display='none';
    log('数据已读取：cards.v1.json / duel.v01.json');
    render();
  }catch(e){
    $('loading').textContent='数据读取失败，请刷新或检查 data/*.json。';
  }
}
function buildBaseDeck(){
  const byId=new Map(cardsData.cards.map(c=>[c.id,c]));
  base=[];
  duelData.supported_cards.forEach(sc=>{
    const c=byId.get(sc.card_id); if(!c)return;
    for(let i=0;i<sc.copies;i++) base.push({id:sc.card_id+'-'+i,name:c.name,star:c.star,text:sc.duel_text||c.card_text});
  });
  base=base.slice(0,duelData.deck_building.deck_size);
}
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function clone(c,o){return {...c,o,uid:o+'-'+c.id+'-'+Math.random().toString(36).slice(2),dmg:0,ready:false,used:false}}
function player(name,o,life){return {name,o,life,maxLife:life,deck:shuffle(base.map(c=>clone(c,o))),hand:[],board:[],discard:[],energy:0,turn:0}}
function log(t){const d=document.createElement('div');d.textContent=t;$('log').prepend(d);while($('log').children.length>80)$('log').lastChild.remove()}
function draw(p,n=1){for(let i=0;i<n;i++){if(p.deck.length)p.hand.push(p.deck.shift());else{p.life--;log(p.name+'牌组为空，失去1点地盘生命。');checkWin()}}}
function startGame(){const life=Number($('life').value);$('log').innerHTML='';$('result').textContent='';chosen=null;G={p:[player('你',0,life),player('AI',1,life)],cur:0,win:null};G.p.forEach(p=>draw(p,duelData.setup.starting_hand));log('开局完成，自动进入你的回合。');beginHuman();render()}
function beginHuman(){if(!G||G.win)return;G.cur=0;const p=G.p[0];p.turn++;p.energy=Math.min(p.turn,duelData.energy.max);p.board.forEach(c=>{c.ready=true;c.used=false;c.dmg=0});if(p.turn>1)draw(p,1);else log('先手第一回合不抽牌。');log('你的回合开始，获得'+p.energy+'妖气。')}
function endTurn(){if(!G||G.win||G.cur!==0)return;G.p[0].energy=0;chosen=null;log('你结束回合。');G.cur=1;render();setTimeout(()=>{aiTurn();if(!G.win)beginHuman();render()},350)}
function remove(c){const p=G.p[c.o];const i=p.board.indexOf(c);if(i>=0)return p.board.splice(i,1)[0]}
function destroy(c){const p=G.p[c.o];const x=remove(c);if(!x)return;if(x.name==='白骨精'){x.dmg=0;x.used=false;x.ready=false;p.deck.push(x);shuffle(p.deck);log('白骨精被消灭，回到牌组并重洗。')}else{p.discard.push(x);log(x.name+'被消灭。')}}
function bounce(c){const p=G.p[c.o];const x=remove(c);if(x){x.dmg=0;x.used=false;x.ready=false;p.hand.push(x);log(x.name+'被吹回手牌。')}}
function skill(c){const p=G.p[c.o],e=G.p[1-c.o];if(c.name==='有来有去'){draw(p,1);p.hand.sort((a,b)=>a.star-b.star);const q=p.hand.shift();if(q){p.discard.push(q);log(p.name+'弃掉 '+q.name)}}else if(c.name==='急如火'){draw(p,1);draw(e,1)}else if(c.name==='快如风'){if(e.deck.length)e.deck.push(e.deck.shift())}else if(c.name==='云里雾'){shuffle(e.deck)}else if(c.name==='雾里云'){shuffle(p.deck)}else if(c.name==='银角大王'){const t=p.deck.splice(0,3).sort((a,b)=>b.star-a.star);p.deck.unshift(...t)}else if(c.name==='铁扇公主'){const t=e.board.slice().sort((a,b)=>b.star-a.star)[0];if(t)bounce(t)}else if(c.name==='红孩儿'){G.p[0].board.concat(G.p[1].board).filter(x=>x.star===1).forEach(destroy)}else if(c.name==='黄风怪'){e.board.filter(x=>x.star<3).slice(0,2).forEach(bounce)}else if(c.name==='青狮精'){const t=e.board.filter(x=>x.star<=4).sort((a,b)=>b.star-a.star)[0];if(t)destroy(t)}else if(c.name==='大鹏精'){c.ready=true;resolveStrike(c,bestTarget(c));log('大鹏精技能行动不受召唤延迟限制。')}}
function play(i){if(!G||G.win||G.cur!==0)return;const p=G.p[0],c=p.hand[i];if(p.energy<c.star)return alert('妖气不足');p.energy-=c.star;p.hand.splice(i,1);c.ready=false;p.board.push(c);log('你打出 '+c.name);skill(c);checkWin();render()}
function bestTarget(a){const e=G.p[1-a.o];if(!e.board.length)return null;return e.board.filter(x=>x.star-x.dmg<=a.star).sort((x,y)=>(x.star-x.dmg)-(y.star-y.dmg))[0]||e.board.slice().sort((x,y)=>x.star-y.star)[0]}
function resolveStrike(a,t){if(!a||a.used||!a.ready||G.win)return;const e=G.p[1-a.o];if(!t){e.life-=a.star;a.used=true;log(a.name+'直取地盘生命 '+a.star+' 点。');checkWin();return}a.dmg+=t.star;t.dmg+=a.star;a.used=true;log(a.name+'挑战 '+t.name);if(t.dmg>=t.star)destroy(t);if(a.dmg>=a.star)destroy(a);checkWin()}
function clickBoard(o,i){if(!G||G.cur!==0||G.win)return;const c=G.p[o].board[i];if(o===0){chosen=c;render();if(!c.ready)log(c.name+'正在休整，本回合不能普通行动。');return}if(chosen){resolveStrike(chosen,c);chosen=null;render()}}
function directOrSelect(i){if(!G||G.cur!==0||G.win)return;const c=G.p[0].board[i];if(G.p[1].board.length){chosen=c;render();return}resolveStrike(c,null);render()}
function aiTurn(){const p=G.p[1];p.turn++;p.energy=Math.min(p.turn,duelData.energy.max);p.board.forEach(c=>{c.ready=true;c.used=false;c.dmg=0});draw(p,1);log('AI回合，获得'+p.energy+'妖气。');let guard=0;while(!G.win&&guard++<20){const c=p.hand.filter(x=>x.star<=p.energy).sort((a,b)=>b.star-a.star)[0];if(!c)break;p.energy-=c.star;p.hand.splice(p.hand.indexOf(c),1);c.ready=false;p.board.push(c);log('AI打出 '+c.name);skill(c)}p.board.slice().filter(c=>c.ready&&!c.used).sort((a,b)=>a.star-b.star).forEach(c=>resolveStrike(c,bestTarget(c)));p.energy=0;log('AI结束回合。')}
function hint(){if(!G||G.cur!==0)return;const p=G.p[0];const c=p.hand.filter(x=>x.star<=p.energy).sort((a,b)=>b.star-a.star)[0];log(c?'建议打出：'+c.name+'。':'建议：行动或结束回合。')}
function checkWin(){if(!G)return;G.p.forEach(p=>{if(p.life<=0&&!G.win){G.win=G.p[1-p.o];$('result').textContent=G.win.name+'获胜';log(G.win.name+'获胜。')}})}
function cardHTML(c,o,i,hand){const dim=hand?(G&&G.p[o].energy<c.star):(!c.ready);const sel=chosen===c;const click=hand?'play('+i+')':(o===0?'directOrSelect('+i+')':'clickBoard('+o+','+i+')');return '<div class="card '+(dim?'dim ':'')+(sel?'sel ':'')+'" onclick="'+click+'"><span class="star">'+c.star+'</span><b>'+c.name+'</b><div>'+c.text+'</div><div>'+(c.used?'已行动':'伤害 '+c.dmg)+'</div></div>'}
function render(){if(!G){$('p0s').innerHTML='<span class="stat">未开始</span>';$('p1s').innerHTML='<span class="stat">未开始</span>';$('phase').textContent='请选择生命并开始';return}G.p.forEach((p,i)=>{$('p'+i+'s').innerHTML='<span class="stat">生命 '+p.life+'/'+p.maxLife+'</span><span class="stat">妖气 '+p.energy+'</span><span class="stat">牌组 '+p.deck.length+'</span><span class="stat">手牌 '+p.hand.length+'</span>';$('b'+i).innerHTML=p.board.map((c,k)=>cardHTML(c,i,k,false)).join('')});$('hand').innerHTML=G.p[0].hand.map((c,k)=>cardHTML(c,0,k,true)).join('');$('phase').textContent=G.win?(G.win.name+'获胜'):(G.cur===0?'你的回合：出牌、行动或结束回合':'AI行动中')}
boot();
