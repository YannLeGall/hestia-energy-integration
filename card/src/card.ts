import {LitElement,html,nothing,unsafeCSS,type TemplateResult} from 'lit';
import {unsafeHTML} from 'lit/directives/unsafe-html.js';
import charte from './ui/hestia-charte.css';
import energy from './energy.css';
import './editor';

/* Hestia Énergie's card (demo/maquette.html, 7 Nov. 2026): three reading levels.
   1 · the tile: one sentence, one figure (card: tuile)
   2 · the full card: the banner, « À savoir », the moment, the rubrics (card: complete, by default)
   3 · the detail cards, over the page from a rubric or alone (card: chauffage | veille | contrat | soleil | eau | appareils | pointe)
   Every figure and every sentence comes from the integration (hestia_energy/view): the card computes nothing. */

type Hass={callWS:<T>(msg:Record<string,unknown>)=>Promise<T>;states:Record<string,{last_updated:string}>};
type Banner={id:string;couleur:string;pastille:string;titre:string;pourquoi:string};
type Period={euros:number|null;euros_energie:number|null;kwh_achetes:number;soleil_kwh:number|null;revendu_kwh:number|null;revendu_euros:number|null;soleil_couvre:number|null;soleil_garde:number|null;heures_inconnues:number;debut:string};
type Hour={h:number;achat:number|null;soleil:number|null;revente:number|null};
type View={pret:boolean;palier:number;equipement:{direct?:boolean;soleil?:boolean;appareils?:boolean};
 direct?:{achat_w:number|null;revente_w:number|null;soleil_w:number|null;maison_w:number|null;periode:string|null;prix:number|null;
  prochain_changement:{a:string;periode:string}|null;en_marche:{nom:string;type:string;w:number}[];bandeau:Banner;fuite:{minutes:number|null;debit:number};
  chauffage?:{pieces:{nom:string;w:number|null}[];w:number|null;euros_de_l_heure:number|null;sans_puissance:string[];poele:boolean}|null;
  sources:Record<string,{retenu:string|null;valeur:number|null;ecartes:{source:string;raison:string}[]}>};
 jour?:Period;hier?:Period;mois?:Period;mois_an_dernier?:Period;projection:number|null;
 veille:{w:number;euros_par_an:number|null;nuits:number}|null;veille_historique:{jour:string;w:number}[];
 heures_creuses:[string,string][]|null;contrat:{option:string;kva:number;prix:Record<string,number>;revente:number|null};
 heures:{aujourdhui:Hour[];hier:Hour[]};eau:{jour_l:number;mois_l:number;mois_euros:number|null;prix_m3:number|null}|null;
 a_savoir:{rubrique:string;titre:string;texte:string}[];
 jusqu_ici?:{euros:number|null;kwh:number;hier_euros:number|null;hier_kwh:number;jusqu_a:string}|null;
 panneaux?:{hier:{nom:string;kwh:number}[];en_retrait:{nom:string;pourcent_de_moins:number}[];onduleur_muet_min:number|null}|null;
 chauffage?:{etat:string;mois?:Heat|null;hiver_dernier?:(Heat&{du:string;au:string})|null;poele?:Stove|null}};
type Stove={mois:{kg:number;eur:number|null}|null;saison:{kg:number;eur:number|null};prix_kg:number|null;sac_kg:number|null};
type Heat={kwh:number;eur:number|null;jours:number};
type Config={type:string;card?:string;name?:string};

const RUBRICS=['chauffage','veille','contrat','soleil','eau','appareils','pointe'] as const;
type Rubric=typeof RUBRICS[number];

/* Icons of the mock-up, drawn at the stroke (constants: never built from data). */
const I:Record<string,string>={
 sun:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg>',
 home:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3.5 11 12 4l8.5 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5.5h4V20"/></svg>',
 grid:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M8 21 11 3h2l3 18"/><path d="M5 7h14M6.5 12h11M9.5 16.5l5-4.5M14.5 16.5l-5-4.5"/></svg>',
 bolt:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M13 2.5 5 13.5h6l-1 8 8-11h-6z"/></svg>',
 drop:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3s6.5 7 6.5 11.2A6.5 6.5 0 0 1 5.5 14.2C5.5 10 12 3 12 3z"/></svg>',
 euro:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17.5 6.5a6.5 6.5 0 1 0 0 11"/><path d="M4.5 10.5h9M4.5 13.5h8"/></svg>',
 clock:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
 moon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z"/></svg>',
 plug:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3v5M15 3v5M6.5 8h11v3.5a5.5 5.5 0 0 1-11 0z"/><path d="M12 17v4"/></svg>',
 doc:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 3h8.5L19 7.5V21H6z"/><path d="M14 3v5h5M9 12.5h7M9 16.5h7"/></svg>',
 flame:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 21.5a6.5 6.5 0 0 0 6.5-6.5c0-4.5-4-6.5-4.5-11-2.5 2-4 4.5-4 7-1-.5-2-1.8-2.2-3C6.5 9.8 5.5 12.3 5.5 15a6.5 6.5 0 0 0 6.5 6.5z"/></svg>',
 chev:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>',
};
const icon=(k:string)=>unsafeHTML(I[k]??I.bolt);

/* Numbers in the family's words (PHRASES.md rule 7): kW to 0.1, € to the cent under 10 €, to the euro above. */
// « always »: French leaves 4-digit numbers ungrouped by default (« 1749 »); the family reads « 1 749 ».
const num=(v:number,d=1)=>v.toLocaleString('fr-FR',{maximumFractionDigits:d,minimumFractionDigits:0,useGrouping:'always' as unknown as boolean});
const kw=(w:number|null|undefined)=>w==null?'—':num(w/1000,1);
const eur=(v:number|null|undefined)=>v==null?'—':Math.abs(v)<10?v.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2}):num(v,0);
const kwh=(v:number|null|undefined)=>v==null?'—':num(v,v<10?1:0);
const MONTHS=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
const LEVEL:Record<string,string>={bleu:'ok',vert:'benefit',orange:'action',rouge:'urgent'};
const TONE:Record<string,string>={bleu:'--nw-ok',vert:'--nw-benefit',orange:'--nw-act',rouge:'--nw-alert'};
const BANNER_ICON:Record<string,string>={fuite_eau:'drop',disjoncteur:'bolt',chauffe_eau_reseau:'drop',soleil_en_trop:'sun',soleil_machine_ok:'sun',
 soleil_chaleur:'sun',machines_ensemble:'plug',machine_sans_soleil:'sun',machine_heures_pleines:'clock',oublie:'plug',rien_hc:'clock',rien_hc_bientot:'clock',
 rien_soleil_juste:'sun',rien_soleil_petit:'sun',rien_soleil_plus_tard:'sun',rien:'home'};

/* Bars of the mock-up: a colour per bar, background bands (off-peak hours), the highest value set on it. Numbers only. */
function bars(vals:(number|null)[],o:{color?:(i:number)=>string;bands?:[number,number][];ticks?:[number,string][];h?:number;unit?:string;W?:number}={}):TemplateResult{
 const v=vals.map(x=>x??0),n=v.length||1,W=o.W??300,h=o.h??70,gap=n>20?1.2:3,bw=(W-gap*(n-1))/n,top=Math.max(...v,0),max=top*1.12||1;
 let s=`<svg class="chart" viewBox="0 -16 ${W} ${h+32}" role="img">`;
 (o.bands??[]).forEach(([a,b])=>{s+=`<rect x="${a*(bw+gap)-gap/2}" y="0" width="${(b-a)*(bw+gap)}" height="${h}" rx="3" style="fill:var(--nw-cold);fill-opacity:.16"/>`;});
 v.forEach((x,i)=>{const bh=Math.max(1.5,x/max*h);s+=`<rect x="${i*(bw+gap)}" y="${h-bh}" width="${bw}" height="${bh}" rx="${Math.min(3,bw/2)}" fill="${(o.color??(()=>'var(--nw-home)'))(i)}"${vals[i]==null?' opacity=".25"':''}/>`;});
 if(top>0){const m=v.indexOf(top),x=Math.min(W-26,Math.max(26,m*(bw+gap)+bw/2)),y=h-top/max*h,txt=num(top,1)+(o.unit??''),w=txt.length*5.6+12;
  s+=`<g font-size="10" font-weight="700" text-anchor="middle"><rect x="${x-w/2}" y="${y-18}" width="${w}" height="14" rx="7" fill="var(--nw-bg)" stroke="var(--nw-line)"/><text x="${x}" y="${y-8}" fill="var(--nw-fg)">${txt}</text></g>`;}
 s+=`<g font-size="9.5" fill="var(--nw-fg2)">`+(o.ticks??[]).map(([i,l])=>{const x=i*(bw+gap)+bw/2,a=i===0?'start':(i>=n-1?'end':'middle');return `<text x="${a==='start'?0:(a==='end'?W:x)}" y="${h+13}" text-anchor="${a}">${l}</text>`;}).join('')+'</g></svg>';
 return html`${unsafeHTML(s)}`;
}
const H_TICKS:[number,string][]=[[0,'0 h'],[6,'6 h'],[12,'12 h'],[18,'18 h'],[23,'23 h']];
/** The off-peak hours as hour bands, from « 0 h 14 » – « 8 h 19 ». */
function offpeakBands(ranges:[string,string][]|null):[number,number][]{
 const h=(t:string)=>{const m=t.match(/(\d+) h(?: (\d+))?/);return m?Number(m[1])+(m[2]?Number(m[2])/60:0):0;};
 return (ranges??[]).flatMap(([a,b])=>{const x=h(a),y=h(b);return y>x?[[x,y] as [number,number]]:[[x,24] as [number,number],[0,y] as [number,number]];});
}
const share=(v:View)=>{const d=v.direct;return v.equipement.soleil&&d?.maison_w?Math.round(Math.min(1,(d.soleil_w??0)/d.maison_w)*100):null;};

class HestiaEnergyCard extends LitElement {
 static styles=[unsafeCSS(charte),unsafeCSS(energy)];
 static properties={_view:{state:true},_open:{state:true},_folded:{state:true},_error:{state:true}};
 declare _view?:View;declare _open?:Rubric;declare _folded:Set<string>;declare _error?:string;
 private _hass?:Hass;private _config:Config={type:'custom:hestia-energy-card',card:'complete'};private _stamp='';private _asked=0;private _timer?:number;
 constructor(){super();this._folded=new Set();}

 static getStubConfig(){return {card:'complete'};}
 static getConfigElement(){return document.createElement('hestia-energy-card-editor');}
 setConfig(config:Config){
  const card=config.card??'complete';
  if(card!=='complete'&&card!=='tuile'&&!RUBRICS.includes(card as Rubric))throw new Error(`card: ${card} ? (complete, tuile, ${RUBRICS.join(', ')})`);
  this._config={...config,card};
 }
 getCardSize(){return this._config.card==='tuile'?2:8;}
 set hass(hass:Hass){
  this._hass=hass;
  // A new view when the banner's entity changes, and at least every minute: the card never recomputes anything.
  const stamp=hass.states['sensor.hestia_energy_conseil']?.last_updated??'';
  if(stamp!==this._stamp||Date.now()-this._asked>60000){this._stamp=stamp;void this._load();}
 }
 connectedCallback(){super.connectedCallback();this._timer=window.setInterval(()=>void this._load(),60000);}
 disconnectedCallback(){super.disconnectedCallback();window.clearInterval(this._timer);}
 private async _load(){
  if(!this._hass)return;this._asked=Date.now();
  try{this._view=await this._hass.callWS<View>({type:'hestia_energy/view'});this._error=undefined;}
  catch(e){this._error=(e as {message?:string}).message??'Hestia Énergie ne répond pas.';}
 }

 render(){
  const v=this._view;
  if(this._error&&!v)return html`<ha-card><div class="empty">${this._error}</div></ha-card>`;
  if(!v||!v.pret)return html`<ha-card><div class="nw-say">Hestia Énergie lit la page Énergie…</div></ha-card>`;
  const card=this._config.card;
  if(card==='tuile')return this._tile(v);
  if(card!=='complete')return html`<ha-card>${this._detail(v,card as Rubric,false)}</ha-card>`;
  return html`${this._full(v)}${this._open?html`<div class="ov" @click=${(e:Event)=>{if(e.target===e.currentTarget)this._open=undefined;}}
   @keydown=${(e:KeyboardEvent)=>{if(e.key==='Escape')this._open=undefined;}}><ha-card class="sheet" role="dialog" aria-modal="true">${this._detail(v,this._open,true)}</ha-card></div>`:nothing}`;
 }

 private _name(){return this._config.name??'Maison';}
 private _where(){const d=new Date();return d.toLocaleDateString('fr-FR',{weekday:'long'})+' '+d.getHours()+' h '+String(d.getMinutes()).padStart(2,'0');}

 /* ── 1 · The tile ── */
 private _tile(v:View){
  const b=v.direct?.bandeau,d=v.direct,live=!!(v.equipement.direct&&d?.maison_w!=null),c=b?TONE[b.couleur]:'--nw-ok';
  const value=live?kw(d!.maison_w):eur(v.hier?.euros??v.hier?.euros_energie);
  const sub=!live?`${kwh(v.hier?.kwh_achetes)} kWh hier`:(v.equipement.soleil&&d!.soleil_w!=null?`dont ${kw(Math.min(d!.soleil_w,d!.maison_w??0))} kW de soleil`:(d!.prix!=null?`${eur((d!.maison_w??0)/1000*d!.prix)} € de l'heure`:''));
  const p=share(v),say=b?(b.id.startsWith('rien')&&b.pourquoi?b.pourquoi:b.titre):'';
  return html`<ha-card class="tile"><div class="t-top"><div style="min-width:0"><div class="nw-label">${live?'Énergie · maintenant':'Énergie · hier'}</div>
    <div class="name">${this._name()}</div><div class="nw-say">${this._where()}</div></div>
   <div class="t-right">${b?html`<span class="pastille" style="--c:var(${c})">${b.pastille}</span>`:nothing}<div class="t-val">${value}<small>${live?'kW':'€'}</small></div><div class="t-sub">${sub}</div></div>
   ${p!=null?html`<span class="ring" style="--c:var(${c});--p:${p}" aria-label="${p} % de soleil">${icon('sun')}</span>`:nothing}</div>
   ${say?html`<div class="bubble" style="--c:var(${c})">${icon(BANNER_ICON[b!.id]??'home')}<span>${say}</span></div>`:nothing}</ha-card>`;
 }

 /* ── 2 · The full card ── */
 private _full(v:View){
  const b=v.direct?.bandeau;
  return html`<ha-card>
   <div class="head"><div><div class="nw-label">Synthèse</div><div class="name">${this._name()}</div></div><div class="where">${this._where()}</div></div>
   ${b?html`<div class="nw-band nw-glass" data-level=${LEVEL[b.couleur]??'ok'}><div class="nw-band-row"><span class="nw-band-pic box">${icon(BANNER_ICON[b.id]??'home')}</span>
    <div class="nw-band-text"><p class="nw-band-kicker">${b.titre.startsWith(b.pastille)?'Énergie · maintenant':b.pastille}</p><p class="nw-band-title">${b.titre}</p>${b.pourquoi?html`<p class="nw-band-line">${b.pourquoi}</p>`:nothing}</div></div></div>`:nothing}
   ${v.a_savoir?.length?html`<div class="know">${v.a_savoir.map(k=>html`<div class="k"><span class="nw-label">${k.titre}</span><span>${k.texte}</span></div>`)}</div>`:nothing}
   ${this._section('now',v.equipement.direct?'Maintenant':'Hier',this._nowSum(v),this._now(v))}
   ${this._section('rubs','Rubriques','touchez pour tout voir',this._rubrics(v),'rubs')}
  </ha-card>`;
 }
 private _section(id:string,label:string,sum:string,body:unknown,cls='sec-body'){
  const open=!this._folded.has(id);
  return html`<div class="sec"><button class="nw-fold-head" aria-expanded=${String(open)} @click=${()=>{const f=new Set(this._folded);if(open)f.add(id);else f.delete(id);this._folded=f;}}>
   <span class="nw-title">${label}</span><span class="nw-sum">${sum}</span><span class="nw-chevron">${icon('chev')}</span></button>${open?html`<div class=${cls}>${body}</div>`:nothing}</div>`;
 }
 private _nowSum(v:View){
  const d=v.direct;
  if(v.equipement.direct&&d?.maison_w!=null){const p=share(v);
   return `${kw(d.maison_w)} kW`+(p!=null?` · ${p} % de soleil`:(d.prix!=null?` · ${eur(d.maison_w/1000*d.prix)} € de l'heure`:''));}
  return `${kwh(v.hier?.kwh_achetes)} kWh · ${eur(v.hier?.euros)} €`;
 }
 private _panel(o:{t:string;ic:string;c?:string;src?:string;wide?:boolean;val?:string;unit?:string;say?:unknown;body?:unknown;foot?:unknown}){
  const c=o.c??'--nw-home';
  return html`<div class="nw-panel${o.wide?' wide':''}" style="--c:var(${c})"><div class="nw-panel-head"><span class="nw-panel-icon tint" style="--c:var(${c})">${icon(o.ic)}</span><h3><span>${o.t}</span></h3>${o.src?html`<span class="nw-badge">${o.src}</span>`:nothing}</div>
   ${o.val!=null?html`<div class="nw-cases"><div class="nw-value"><b>${o.val}</b><span>${o.unit??''}</span></div></div>`:nothing}
   ${o.say?html`<div class="m-say">${o.say}</div>`:nothing}${o.body??nothing}${o.foot?html`<div class="m-foot">${o.foot}</div>`:nothing}</div>`;
 }
 private _flow(v:View){
  const d=v.direct!;const node=(ic:string,c:string,val:string,l:string)=>html`<div class="node" style="--c:var(${c})"><span class="dot">${icon(ic)}</span><span class="nv">${val}</span><span class="nl">${l}</span></div>`;
  const link=(c:string,state:string)=>html`<span class="link ${state}" style="--c:var(${c})"><i></i></span>`;
  const buying=(d.achat_w??0)>=30,selling=!buying&&(d.revente_w??0)>=30;
  if(!v.equipement.soleil)return html`<div class="flow two">${node('home','--nw-home',`${kw(d.maison_w)} kW`,'Maison')}${link('--nw-grid','rev')}${node('grid','--nw-grid',`${kw(d.achat_w)} kW`,'Réseau')}</div>`;
  return html`<div class="flow">${node('sun','--nw-sun',`${kw(d.soleil_w)} kW`,'Soleil')}${link('--nw-sun',(d.soleil_w??0)>=30?'':'off')}${node('home','--nw-home',`${kw(d.maison_w)} kW`,'Maison')}${link('--nw-grid',buying?'rev':selling?'':'off')}${node('grid','--nw-grid',`${kw(buying?d.achat_w:selling?d.revente_w:0)} kW`,selling?'Revendu':'Réseau')}</div>`;
 }
 private _now(v:View){
  const d=v.direct,m=v.mois,last=v.mois_an_dernier,now=new Date();
  const lastFoot=last?html`<span>${MONTHS[now.getMonth()]} ${now.getFullYear()-1} : <b>${last.euros!=null?eur(last.euros)+' €':kwh(last.kwh_achetes)+' kWh'}</b>${last.euros!=null?'':' achetés'}</span>`:nothing;
  const sf=v.jusqu_ici,hour=sf?new Date(sf.jusqu_a).getHours():0;
  const euros=sf&&sf.euros!=null&&sf.hier_euros!=null,gap=sf?(euros?sf.euros!-sf.hier_euros!:sf.kwh-sf.hier_kwh):0,small=euros?Math.abs(gap)<0.1:Math.abs(gap)<0.5;
  const todayPanel=sf?this._panel({t:'Aujourd\'hui',src:`jusqu'à ${hour} h`,ic:'clock',c:'--nw-ok',val:euros?eur(sf.euros):kwh(sf.kwh),unit:euros?'€':'kWh',
   say:small?'Comme hier à la même heure.':`${euros?`${eur(Math.abs(gap))} €`:`${kwh(Math.abs(gap))} kWh`} de ${gap>0?'plus':'moins'} qu'hier à la même heure.`}):nothing;
  const monthPanel=this._panel({t:v.equipement.soleil?'Ce mois, électricité':'Ce mois',src:'abonnement compris',ic:'euro',c:'--nw-ok',val:eur(m?.euros??m?.euros_energie),unit:'€ jusqu\'ici',
   say:v.projection!=null?`Environ ${eur(v.projection)} € à la fin du mois.`:nothing,foot:lastFoot});
  if(v.equipement.direct&&d?.maison_w!=null){
   const p=share(v),sources=[...new Set([d.sources?.soleil?.retenu,d.sources?.achat?.retenu].filter(Boolean))].join(' · ');
   const running=[...d.en_marche].sort((a,b)=>b.w-a.w).slice(0,3),h=d.chauffage;
   // The heaters heating now, by their thermostat (9.5); the stove says it is lit, its pellets are not electricity.
   const heatRows=[...(h?.poele?[html`<div class="row"><span>Poêle</span><span class="v muted">allumé</span></div>`]:[]),
    ...(h?.pieces??[]).map(r=>html`<div class="row"><span>Chauffage · ${r.nom}</span><span class=${r.w==null?'v muted':'v'}>${r.w==null?'en marche':`${kw(r.w)} kW`}</span></div>`)];
   return html`${this._panel({t:'En ce moment',src:sources,ic:v.equipement.soleil?'sun':'bolt',c:v.equipement.soleil?'--nw-sun':'--nw-grid',body:this._flow(v),
     foot:html`${p!=null?html`<span>Le soleil couvre <b>${p} %</b> de la maison</span>`:html`<span>${d.periode==='hc'?'Heures creuses':'Heures pleines'}</span>`}${d.prix!=null&&(d.achat_w??0)>=30?html`<span><b>${eur((d.achat_w??0)/1000*d.prix)} €</b> de l'heure</span>`:nothing}`})}
    ${this._panel({t:'En marche',src:'prises · pinces · thermostats',ic:'plug',body:running.length||heatRows.length?html`<div class="rows">${heatRows}${running.map(r=>html`<div class="row"><span>${r.nom}</span><span class="v">${kw(r.w)} kW</span></div>`)}</div>`:html`<div class="nw-say">Rien de gros ne tourne.</div>`,
     foot:h?.euros_de_l_heure!=null&&h.w?html`<span>Chauffage : <b>${eur(h.euros_de_l_heure)} €</b> de l'heure</span>`:nothing})}
    ${todayPanel}${monthPanel}`;
  }
  const hours=v.heures?.hier??[],bands=offpeakBands(v.heures_creuses);
  return html`${this._panel({t:'Hier',src:'statistiques',ic:'bolt',val:eur(v.hier?.euros),unit:'€',body:html`${bars(hours.map(x=>x.achat),{bands,ticks:H_TICKS,color:i=>bands.some(([a,b])=>i>=a&&i<b)?'var(--nw-cold)':'var(--nw-home)'})}
    <div class="nw-legend"><span><i style="--c:var(--nw-home)"></i>heures pleines</span><span><i style="--c:var(--nw-cold)"></i>heures creuses</span></div>`})}${monthPanel}`;
 }

 /* Rubrics: one sentence, one figure; touched, they open their detail card. Only those the home can fill. */
 private _rubric(key:Rubric,ic:string,c:string,title:string,val:string,unit:string,say:string){
  return html`<button class="rub" style="--c:var(${c})" @click=${()=>{this._open=key;}}><span class="r-h"><span class="nw-panel-icon tint" style="--c:var(${c})">${icon(ic)}</span><b>${title}</b><span class="r-go">›</span></span>
   <span class="r-v">${val}<small>${unit}</small></span><span class="r-s">${say}</span></button>`;
 }
 private _rubrics(v:View){
  const out:TemplateResult[]=[],d=v.direct;
  if(v.equipement.soleil&&v.jour?.soleil_kwh!=null)out.push(this._rubric('soleil','sun','--nw-sun','Soleil',kwh(v.jour.soleil_kwh),'kWh aujourd\'hui',
   v.hier?.soleil_garde!=null?`Hier, la maison a gardé ${v.hier.soleil_garde} % de son soleil.`:''));
  const heat=v.chauffage,st=heat?.poele,el=heat?.etat==='pret'?heat.mois:null;
  if(el&&st?.mois&&el.eur!=null&&st.mois.eur!=null)out.push(this._rubric('chauffage','flame','--nw-heat','Chauffage',eur(el.eur+st.mois.eur),'€ ce mois',`Radiateurs ${eur(el.eur)} €, poêle ${eur(st.mois.eur)} €.`));
  else if(el)out.push(this._rubric('chauffage','flame','--nw-heat','Chauffage',el.eur!=null?eur(el.eur):kwh(el.kwh),el.eur!=null?'€ ce mois':'kWh ce mois',st?`Poêle : ${(st.mois??st.saison).eur!=null?`${eur((st.mois??st.saison).eur)} €`:`${num((st.mois??st.saison).kg,0)} kg`} ${st.mois?'ce mois':'depuis octobre'}.`:'Estimé d\'après le froid de chaque jour.'));
  else if(st){const p=st.mois??st.saison,when=st.mois?'ce mois':'depuis octobre';
   out.push(this._rubric('chauffage','flame','--nw-heat','Chauffage',p.eur!=null?eur(p.eur):num(p.kg,0),`${p.eur!=null?'€':'kg'} ${when}`,`Poêle : ${num(p.kg,0)} kg de granulés.`));}
  else if(heat?.etat==='peu_lie')out.push(this._rubric('chauffage','flame','--nw-heat','Chauffage','—','','Vous chauffez sans doute surtout avec une autre énergie.'));
  if(v.veille)out.push(this._rubric('veille','moon','--nw-watch','Veille de nuit',String(v.veille.w),'W',v.veille.euros_par_an!=null?`Environ ${eur(v.veille.euros_par_an)} € par an, sans rien allumer.`:''));
  if(v.eau)out.push(this._rubric('eau','drop','--nw-water','Eau',num(v.eau.jour_l,0),'L aujourd\'hui',d?.fuite?.minutes?`L'eau coule depuis ${Math.round(d.fuite.minutes)} min.`:'Rien ne coule ; pas de fuite.'));
  if(v.equipement.appareils&&d)out.push(this._rubric('appareils','plug','--nw-home','Appareils',String(d.en_marche.length),'en marche',d.en_marche.length?`${[...d.en_marche].sort((a,b)=>b.w-a.w)[0].nom} tire le plus.`:'Rien de gros ne tourne.'));
  if(v.equipement.direct&&v.contrat?.kva)out.push(this._rubric('pointe','grid','--nw-grid','Pointe',kwh(Math.max(0,...(v.heures?.aujourdhui??[]).map(h=>h.achat??0))),'kWh dans l\'heure la plus chargée',`Aujourd'hui, sur ${v.contrat.kva} kVA souscrits.`));
  out.push(this._rubric('contrat','doc','--nw-ok','Contrat',v.contrat?.option==='hphc'?'HP / HC':v.contrat?.option==='tempo'?'Tempo':'Base',v.contrat?.kva?` · ${v.contrat.kva} kVA`:'',
   v.heures_creuses?.length?`Heures creuses de ${v.heures_creuses[0][0]} à ${v.heures_creuses[0][1]}.`:'Le simulateur arrive avec la première version stable.'));
  return out;
 }

 /* ── 3 · The detail cards ── */
 private _detail(v:View,key:Rubric,over:boolean){
  const meta:Record<Rubric,[string,string,string,string]>={
   chauffage:['Chauffage','flame','--nw-heat','Ce que coûte le chauffage de la maison.'],
   veille:['Veille de nuit','moon','--nw-watch','Ce que la maison consomme quand tout dort : la box, le frigo, ce qui reste branché.'],
   contrat:['Mon contrat','doc','--nw-ok','Le contrat lu sur le compteur et la page Énergie, et ses heures creuses.'],
   soleil:['Soleil','sun','--nw-sun','Ce que font les panneaux aujourd\'hui, et ce que la maison en garde.'],
   eau:['Eau','drop','--nw-water','Le compteur d\'eau, et ce qu\'il raconte.'],
   appareils:['Appareils','plug','--nw-home','Ce que mesurent les prises et les pinces.'],
   pointe:['Pointe de puissance','grid','--nw-grid','Au-delà de la puissance souscrite, le disjoncteur coupe.'],
  };
  const [t,ic,c,say]=meta[key];
  return html`<div class="head"><span class="nw-panel-icon tint" style="--c:var(${c});width:36px;height:36px;border-radius:11px">${icon(ic)}</span>
    <div><div class="nw-label">Tout voir — ${this._name()}</div><div class="name">${t}</div></div>${over?html`<button class="d-close" aria-label="Fermer" @click=${()=>{this._open=undefined;}}>×</button>`:nothing}</div>
   <p class="d-say m-say">${say}</p><div class="sec-body">${this._detailBody(v,key)}</div>`;
 }
 /* Each panel yesterday (5.5): its kWh, the one behind its usual share named, the silent inverter said first. */
 private _panelsHealth(v:View){
  const p=v.panneaux;
  if(!p?.hier?.length)return nothing;
  const behind=new Map(p.en_retrait.map(b=>[b.nom,b.pourcent_de_moins]));
  const say=p.onduleur_muet_min?`L'onduleur ne répond plus depuis ${p.onduleur_muet_min<120?`${p.onduleur_muet_min} min`:`${Math.round(p.onduleur_muet_min/60)} h`}.`
   :p.en_retrait.length?`${p.en_retrait[0].nom} a produit ${p.en_retrait[0].pourcent_de_moins} % de moins que d'habitude.`:'Chaque panneau a produit comme d\'habitude.';
  return this._panel({t:'Chaque panneau, hier',src:'onduleurs',ic:'sun',c:p.onduleur_muet_min||p.en_retrait.length?'--nw-act':'--nw-sun',say,
   body:html`<div class="rows">${[...p.hier].sort((a,b)=>b.kwh-a.kwh).map(r=>html`<div class="row"><span>${r.nom}</span><span class="v">${kwh(r.kwh)} kWh${behind.has(r.nom)?html` <span class="muted">· −${behind.get(r.nom)} %</span>`:nothing}</span></div>`)}</div>`});
 }
 private _detailBody(v:View,key:Rubric){
  const d=v.direct,bands=offpeakBands(v.heures_creuses);
  if(key==='chauffage'){
   const h=v.chauffage,m=h?.mois,w=h?.hiver_dernier,st=h?.poele;
   const sp=st?.mois??st?.saison,when=st?.mois?'ce mois':'depuis octobre';
   const stove=st&&sp?this._panel({t:'Poêle à granulés',src:'Suivi Stock Pellet',ic:'flame',c:'--nw-heat',val:sp.eur!=null?eur(sp.eur):num(sp.kg,0),unit:`${sp.eur!=null?'€':'kg'} ${when}`,
    say:st.mois?`${num(st.mois.kg,0)} kg de granulés ce mois, ${num(st.saison.kg,0)} kg depuis octobre${st.saison.eur!=null?` (${eur(st.saison.eur)} €)`:''}.`:`${num(st.saison.kg,0)} kg de granulés depuis octobre.`,
    foot:st.prix_kg==null?html`<span>Indiquez le prix du sac dans les réglages pour voir les euros.</span>`:nothing}):nothing;
   if(h?.etat==='sans_meteo')return html`${stove}${this._panel({t:'Il manque Hestia Météo',ic:'flame',c:'--nw-heat',wide:true,say:'Pour estimer le chauffage, Hestia a besoin de savoir quel froid il a fait chaque jour : ajoutez Hestia Météo.'})}`;
   if(h?.etat==='meteo_ancienne')return html`${stove}${this._panel({t:'Hestia Météo à mettre à jour',ic:'flame',c:'--nw-heat',wide:true,say:'Pour estimer le chauffage, Hestia a besoin du froid de chaque jour : mettez Hestia Météo à jour.'})}`;
   if(h?.etat==='apprend')return html`${stove}${this._panel({t:'En apprentissage',ic:'flame',c:'--nw-heat',wide:true,say:'Il faut quelques semaines de froid pour estimer le chauffage. Revenez cet hiver.'})}`;
   if(h?.etat==='peu_lie')return html`${stove}${this._panel({t:'Une autre énergie',ic:'flame',c:'--nw-heat',wide:true,say:'Votre électricité varie peu avec le froid : vous chauffez sans doute surtout avec une autre énergie (poêle, gaz…).'})}`;
   const val=(x:Heat|null|undefined)=>x?.eur!=null?eur(x.eur):kwh(x?.kwh),unit=(x:Heat|null|undefined)=>x?.eur!=null?'€':'kWh';
   return html`${stove}${this._panel({t:st?'Radiateurs, ce mois':'Ce mois',src:'estimé',ic:'flame',c:'--nw-heat',val:val(m),unit:unit(m),say:m?`Environ ${kwh(m.kwh)} kWh.`:nothing})}
    ${w?this._panel({t:'L\'hiver dernier',src:'octobre à avril',ic:'flame',c:'--nw-heat',val:val(w),unit:unit(w),say:w.eur!=null?`Environ ${kwh(w.kwh)} kWh.`:'Le prix de cet hiver n\'est pas connu de Hestia.'}):nothing}
    ${this._panel({t:'Comment c\'est estimé',ic:'doc',c:'--nw-ok',wide:true,say:'Chaque jour, Hestia compare votre consommation au froid qu\'il a fait : ce qui augmente quand il fait froid, c\'est surtout le chauffage.'})}`;
  }
  if(key==='veille'){
   const hist=v.veille_historique??[];
   return html`${this._panel({t:'La veille, nuit après nuit',src:`appris sur ${v.veille?.nuits??0} nuits`,ic:'moon',c:'--nw-watch',wide:true,val:String(v.veille?.w??'—'),unit:'W',
     say:v.veille?.euros_par_an!=null?`Environ ${eur(v.veille.euros_par_an)} € par an, sans rien allumer.`:nothing,
     body:hist.length?bars(hist.map(x=>x.w),{W:640,h:50,unit:' W',color:()=>'var(--nw-watch)',ticks:[[0,new Date(hist[0].jour).toLocaleDateString('fr-FR',{day:'numeric',month:'short'})],[hist.length-1,'hier']]}):nothing})}
    ${this._panel({t:'Où chercher',ic:'plug',c:'--nw-watch',body:html`<div class="rows"><div class="row"><span>Un chauffage d'appoint en hors-gel</span><span class="v">souvent</span></div><div class="row"><span>Un chargeur, une console en veille</span><span class="v">parfois</span></div><div class="row"><span>Un frigo qui vieillit</span><span class="v">plus rare</span></div></div>`,foot:html`<span>Une prise mesurée le dirait tout de suite</span>`})}`;
  }
  if(key==='contrat'){
   const p=v.contrat?.prix??{},row=(l:string,x:number|null|undefined)=>x!=null?html`<div class="row"><span>${l}</span><span class="v">${num(x,4)} € le kWh</span></div>`:nothing;
   return html`${this._panel({t:'Votre contrat',src:'compteur · page Énergie',ic:'doc',c:'--nw-ok',val:v.contrat?.option==='hphc'?'Heures pleines / creuses':v.contrat?.option==='tempo'?'Tempo':'Base',unit:v.contrat?.kva?`${v.contrat.kva} kVA`:'',
     body:html`<div class="rows">${row('Heures pleines',p.hp)}${row('Heures creuses',p.hc)}${row('Base',p.base)}${row('Revente du surplus',v.contrat?.revente)}</div>`})}
    ${this._panel({t:'Heures creuses',src:'apprises sur le compteur',ic:'clock',c:'--nw-cold',say:v.heures_creuses?.length?v.heures_creuses.map(([a,b])=>`De ${a} à ${b}`).join(' et ')+'.':'Pas d\'heures creuses lues.',
     foot:d?.prochain_changement?html`<span>Prochain passage : <b>${new Date(d.prochain_changement.a).toLocaleTimeString('fr-FR',{hour:'numeric',minute:'2-digit'}).replace(':',' h ')}</b></span>`:nothing})}
    ${this._panel({t:'Sur 12 mois, avec votre vraie consommation',src:'estimation',ic:'doc',c:'--nw-ok',wide:true,body:html`<div class="empty">Le simulateur de contrat (Base, heures creuses, Tempo) arrive avec la première version stable.</div>`})}`;
  }
  if(key==='soleil'){
   const hours=v.heures?.aujourdhui??[],src=d?.sources?.soleil;
   return html`${this._panel({t:'Aujourd\'hui',src:src?.retenu??'',ic:'sun',c:'--nw-sun',wide:true,val:kwh(v.jour?.soleil_kwh),unit:'kWh produits',
     say:v.jour?.revendu_kwh!=null?`${kwh(v.jour.revendu_kwh)} kWh revendus : ${eur(v.jour.revendu_euros)} €.`:nothing,
     body:html`${bars(hours.map(x=>x.soleil),{W:640,h:60,ticks:H_TICKS,unit:' kWh',color:()=>'var(--nw-sun)'})}<div class="nw-legend"><span><i style="--c:var(--nw-sun)"></i>produit, heure par heure</span></div>`})}
    ${this._panel({t:'Hier',ic:'home',c:'--nw-sun',val:v.hier?.soleil_garde!=null?String(v.hier.soleil_garde):'—',unit:'% du soleil gardé',say:v.hier?.soleil_couvre!=null?`Le soleil a couvert ${v.hier.soleil_couvre} % de la maison.`:nothing})}
    ${this._panel({t:'Sources',ic:'doc',c:'--nw-ok',body:html`<div class="rows"><div class="row"><span>Production</span><span class="v">${src?.retenu??'—'}</span></div>${(src?.ecartes??[]).map(e=>html`<div class="row"><span>${e.raison==='controle'?'Contrôle':'Écartée'}</span><span class="v">${e.source}</span></div>`)}</div>`})}
    ${this._panelsHealth(v)}`;
  }
  if(key==='eau'){
   const e=v.eau,f=d?.fuite;
   return html`${this._panel({t:'Aujourd\'hui',src:'compteur',ic:'drop',c:'--nw-water',val:e?num(e.jour_l,0):'—',unit:'L'})}
    ${this._panel({t:'Fuite',src:'débit',ic:'drop',c:f?.minutes?'--nw-alert':'--nw-ok',val:f?.minutes?`${Math.round(f.minutes)} min`:'Aucune',say:f?.minutes?'L\'eau coule sans s\'arrêter.':'Rien ne coule en continu en ce moment.'})}
    ${this._panel({t:'Ce mois',src:e?.prix_m3!=null?`${num(e.prix_m3,2)} € le m³`:'',ic:'euro',c:'--nw-water',val:e?num(e.mois_l/1000,1):'—',unit:'m³',say:e?.mois_euros!=null?`${eur(e.mois_euros)} €.`:nothing})}`;
  }
  if(key==='appareils'){
   const running=[...(d?.en_marche??[])].sort((a,b)=>b.w-a.w);
   return html`${this._panel({t:'En marche',src:'prises · pinces',ic:'plug',wide:true,body:running.length?html`<div class="rows">${running.map(r=>html`<div class="row"><span>${r.nom}</span><span class="v">${kw(r.w)} kW</span></div>`)}</div>`:html`<div class="nw-say">Rien de gros ne tourne.</div>`})}
    ${this._panel({t:'Ce mois, par usage',ic:'plug',body:html`<div class="empty">La répartition par usage et les cycles des machines arrivent avec la deuxième préversion.</div>`})}`;
  }
  const hours=v.heures?.aujourdhui??[];
  return html`${this._panel({t:'Aujourd\'hui, heure par heure',src:'achats au réseau',ic:'bolt',c:'--nw-grid',wide:true,say:`Sur ${v.contrat?.kva??'—'} kVA souscrits.`,
    body:bars(hours.map(x=>x.achat),{W:640,bands,ticks:H_TICKS,unit:' kWh',color:i=>bands.some(([a,b])=>i>=a&&i<b)?'var(--nw-cold)':'var(--nw-wind)'})})}
   ${this._panel({t:'Délestage',src:'Versatile Thermostat',ic:'grid',c:'--nw-grid',say:'Versatile Thermostat coupe un radiateur avant le disjoncteur. Hestia lui donne la puissance de la maison et la limite.'})}`;
 }
}

if(!customElements.get('hestia-energy-card'))customElements.define('hestia-energy-card',HestiaEnergyCard);
const w=window as unknown as {customCards?:unknown[]};
w.customCards=w.customCards??[];
if(!w.customCards.some(c=>(c as {type?:string}).type==='hestia-energy-card'))
 w.customCards.push({type:'hestia-energy-card',name:'Hestia Énergie',description:'Le conseiller énergie de la maison : tuile, carte complète, cartes de détail.',preview:true});
