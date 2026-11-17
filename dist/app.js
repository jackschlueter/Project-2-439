const FUNDS=['SGOV','BND','VT','TIP'];
const COLORS={SGOV:'#547b8e',BND:'#8b9da7',VT:'#244466',TIP:'#c3a56b'};
const FULL_NAMES={SGOV:'Short Treasury',BND:'US aggregate bonds',VT:'Global equity',TIP:'Inflation linked bonds'};
const $=id=>document.getElementById(id);
const pct=n=>`${n.toFixed(2)}%`;
const usd=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
let returns=[];
let latest=null;

function moments(windowSize){
  const rows=returns.slice(-windowSize),n=rows.length;
  const mean=FUNDS.map((_,i)=>rows.reduce((s,r)=>s+r[i],0)/n*12*100);
  const cov=FUNDS.map((_,i)=>FUNDS.map((_,j)=>rows.reduce((s,r)=>s+(r[i]-mean[i]/1200)*(r[j]-mean[j]/1200),0)/(n-1)*12*10000));
  return {mean,cov,n};
}
function evaluate(w,mean,cov){
  const ret=w.reduce((s,x,i)=>s+x*mean[i],0);
  let variance=0;for(let i=0;i<4;i++)for(let j=0;j<4;j++)variance+=w[i]*w[j]*cov[i][j];
  return {w,ret,vol:Math.sqrt(Math.max(0,variance))};
}
function search(m,netTarget,fee,floor){
  const mean=[...m.mean];mean[2]+=Number($('haircut').value);
  const eligible=[],points=[];
  for(let a=0;a<=20;a++)for(let b=0;b<=20-a;b++)for(let c=0;c<=20-a-b;c++){
    const d=20-a-b-c,w=[a,b,c,d].map(x=>x/20),p=evaluate(w,mean,m.cov);
    if(w[0]*100+1e-9<floor)continue;
    points.push(p);
    if(p.ret+1e-9>=netTarget+fee)eligible.push(p);
  }
  eligible.sort((x,y)=>x.vol-y.vol||x.ret-y.ret||y.w[0]-x.w[0]);
  return {best:eligible[0]||null,points,eligible:eligible.length,mean};
}
function formatMix(w){return FUNDS.filter((_,i)=>w[i]>0).map((f,i)=>{const j=FUNDS.indexOf(f);return `${Math.round(w[j]*100)}% ${f}`}).join(' / ')}
function renderBars(w){
  $('allocBars').innerHTML=FUNDS.map((f,i)=>w[i]?`<div style="width:${w[i]*100}%;background:${COLORS[f]}">${w[i]>=.12?`${Math.round(w[i]*100)}% ${f}`:''}</div>`:'').join('');
  let old=$('legend');if(old)old.remove();
  const legend=document.createElement('div');legend.id='legend';legend.className='legend';legend.innerHTML=FUNDS.map(f=>`<span><i style="background:${COLORS[f]}"></i>${f}</span>`).join('');$('allocBars').after(legend);
}
function renderChart(points,best,target){
  const svg=$('chart'), W=620,H=226,L=42,R=12,T=12,B=30;
  const maxV=Math.max(20,...points.map(p=>p.vol))*1.04, minR=Math.min(-2,...points.map(p=>p.ret))-1,maxR=Math.max(22,...points.map(p=>p.ret))+1;
  const x=v=>L+(W-L-R)*v/maxV,y=v=>H-B-(H-T-B)*(v-minR)/(maxR-minR);
  let s=`<line x1="${L}" y1="${H-B}" x2="${W-R}" y2="${H-B}" stroke="#cbd3d1"/><line x1="${L}" y1="${T}" x2="${L}" y2="${H-B}" stroke="#cbd3d1"/>`;
  [0,5,10,15,20].forEach(v=>{if(v<=maxV)s+=`<line x1="${x(v)}" y1="${T}" x2="${x(v)}" y2="${H-B}" stroke="#edf0ee"/><text x="${x(v)}" y="${H-9}" text-anchor="middle" fill="#89939c" font-size="10">${v}%</text>`});
  [0,5,10,15,20].forEach(v=>{if(v>=minR&&v<=maxR)s+=`<line x1="${L}" y1="${y(v)}" x2="${W-R}" y2="${y(v)}" stroke="#edf0ee"/><text x="${L-8}" y="${y(v)+3}" text-anchor="end" fill="#89939c" font-size="10">${v}%</text>`});
  s+=`<line x1="${L}" y1="${y(target)}" x2="${W-R}" y2="${y(target)}" stroke="#c3a56b" stroke-dasharray="5 4"/><text x="${W-R-2}" y="${y(target)-5}" text-anchor="end" fill="#a48652" font-size="10">GROSS FLOOR</text>`;
  points.filter((_,i)=>i%4===0).forEach(p=>s+=`<circle cx="${x(p.vol)}" cy="${y(p.ret)}" r="2" fill="#a8bac3" opacity=".7"/>`);
  if(best)s+=`<circle cx="${x(best.vol)}" cy="${y(best.ret)}" r="8" fill="#244466" stroke="#fff" stroke-width="3"/>`;
  svg.innerHTML=s;
}
function readSettings(){return {windowSize:Number($('window').value),netTarget:Number($('target').value),fee:Number($('fee').value),floor:Number($('floor').value)}}
function update(){
  if(!returns.length)return;
  const s=readSettings();
  if(![s.netTarget,s.fee,s.floor].every(Number.isFinite)||s.netTarget<0||s.fee<0||s.floor<0||s.floor>100){$('resultNote').textContent='Enter valid nonnegative settings and a reserve floor from 0% to 100%.';return}
  const m=moments(s.windowSize),r=search(m,s.netTarget,s.fee,s.floor),p=r.best;
  latest={s,m,r};
  $('haircutLabel').textContent=`${Number($('haircut').value)>0?'+':''}${Number($('haircut').value).toFixed(2)} pp`;
  $('qualified').textContent=p?`${r.eligible} QUALIFYING MIXES`:'NO QUALIFYING MIX';$('qualified').classList.toggle('fail',!p);
  if(p){$('mixTitle').textContent=formatMix(p.w);renderBars(p.w);$('netReturn').textContent=pct(p.ret-s.fee);$('returnGap').textContent=`${(p.ret-s.fee-s.netTarget).toFixed(2)} pp over net target`;$('volatility').textContent=pct(p.vol);$('reserve').textContent=`${Math.round(p.w[0]*100)}%`;$('reserveDollars').textContent=`${Math.round(p.w[0]*100-s.floor)} pp above reserve floor`;$('resultNote').textContent=`The chosen mix clears the ${(s.netTarget+s.fee).toFixed(2)}% gross hurdle by ${(p.ret-s.netTarget-s.fee).toFixed(2)} percentage points. It is a minimum sample volatility result, not a forecast or approved trade.`}
  else{$('mixTitle').textContent='No feasible allocation';$('allocBars').innerHTML='';$('netReturn').textContent='—';$('returnGap').textContent='Change assumptions';$('volatility').textContent='—';$('reserve').textContent='—';$('reserveDollars').textContent='—';$('resultNote').textContent='No 5% grid mix meets both the return hurdle and SGOV floor. Review the mandate or forward estimates; do not force an allocation.'}
  renderChart(r.points,p,s.netTarget+s.fee);renderTrades();
}
function renderChallenges(){
  const current=Number($('haircut').value),windowSize=Number($('window').value);
  const base=moments(60),short=moments(36),s={netTarget:8,fee:.2,floor:10};
  $('haircut').value=0;const b=search(base,s.netTarget,s.fee,s.floor).best,shortBest=search(short,s.netTarget,s.fee,s.floor).best;
  $('haircut').value=-1;const stressed=search(base,s.netTarget,s.fee,s.floor).best;
  $('haircut').value=current;
  $('stressText').textContent=`Cut VT’s annual return estimate by one point. The full sample choice moves from ${formatMix(b.w)} to ${formatMix(stressed.w)}; modeled volatility rises from ${pct(b.vol)} to ${pct(stressed.vol)}.`;
  $('windowText').textContent=`Using 36 months instead of 60 moves the selection from ${formatMix(b.w)} to ${formatMix(shortBest.w)}. The largest weight moves 30 percentage points.`;
}
function renderTrades(){
  const p=latest?.r.best,inputs=FUNDS.map(f=>Number($(`hold${f}`).value)),total=inputs.reduce((a,b)=>a+b,0),value=Number($('value').value);
  const valid=inputs.every(x=>Number.isFinite(x)&&x>=0&&x<=100)&&Math.abs(total-100)<.01&&Number.isFinite(value)&&value>0;
  $('holdingError').textContent=valid?'':`Current weights must total 100% and portfolio value must be positive (now ${total.toFixed(1)}%).`;
  $('tradeRows').innerHTML=FUNDS.map((f,i)=>{const target=p?p.w[i]*100:0,delta=valid&&p?(target-inputs[i])*value/100:0;return `<tr><td>${f}<small>${FULL_NAMES[f]}</small></td><td>${inputs[i].toFixed(1)}%</td><td>${p?target.toFixed(0)+'%':'—'}</td><td class="${delta>0?'buy':delta<0?'sell':''}">${valid&&p?`${delta>=0?'+':'−'}${usd(Math.abs(delta))}`:'—'}</td></tr>`}).join('');
  if(valid&&p){const turnover=FUNDS.reduce((z,_,i)=>z+Math.abs(p.w[i]*100-inputs[i]),0)/2;$('turnover').textContent=`Estimated one-way turnover: ${turnover.toFixed(1)}% of portfolio (${usd(value*turnover/100)}). Confirm taxes, transaction costs, account restrictions, and an approved turnover rule before any trade.`}
  else $('turnover').textContent='Enter valid holdings to calculate dollar changes.';
}
async function load(){
  try{const csv=await (await fetch('prices.csv')).text(),lines=csv.trim().split(/\r?\n/),headers=lines[0].split(',');
    if(headers.join(',')!=='Month,SGOV,BND,VT,TIP')throw Error('Unexpected price columns');
    const prices=lines.slice(1).map(line=>line.split(',')).map(row=>row.slice(1).map(Number));
    if(prices.length!==61||prices.some(row=>row.length!==4||row.some(x=>!Number.isFinite(x)||x<=0)))throw Error('Price panel failed validation');
    returns=prices.slice(1).map((row,i)=>row.map((p,j)=>p/prices[i][j]-1));
    renderChallenges();update();
  }catch(e){$('mixTitle').textContent='Price panel unavailable';$('resultNote').textContent=e.message}
}
for(const f of FUNDS){const row=document.createElement('div');row.className='holding';row.innerHTML=`<label for="hold${f}" style="margin:0">${f}</label><div><input id="hold${f}" type="number" min="0" max="100" step="1" value="${f==='SGOV'?45:f==='VT'?55:0}"> %</div>`;$('holdingInputs').append(row)}
['window','haircut','target','fee','floor'].forEach(id=>$(id).addEventListener('input',update));
['value',...FUNDS.map(f=>`hold${f}`)].forEach(id=>$(id).addEventListener('input',renderTrades));
$('reset').onclick=()=>{Object.entries({window:'60',haircut:'0',target:'8.0',fee:'0.20',floor:'10'}).forEach(([id,v])=>$(id).value=v);update()};
$('stressBtn').onclick=()=>{$('window').value='60';$('haircut').value='-1';update();$('workbench').scrollIntoView({behavior:'smooth'})};
$('windowBtn').onclick=()=>{$('window').value='36';$('haircut').value='0';update();$('workbench').scrollIntoView({behavior:'smooth'})};
$('printBtn').onclick=()=>window.print();
load();
