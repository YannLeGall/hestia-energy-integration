import {LitElement,html,nothing,css,type TemplateResult} from 'lit';
import {customElement,property,state} from 'lit/decorators.js';
import {hubStyles,modernStyles,pageStyles,pageHead,noteBox,frame,todoFrame,kpis,listSection,listRow,extensionsFrame,aboutPage,saveBar,numberField,segmented,type NkLine} from './socle/ui';

/* The « Énergie » tab of the Hestia-FB panel (CAHIER-DES-CHARGES.md G4, demo/maquette.html « Onglet Énergie »):
   Vue d'ensemble · Sources · Appareils · Contrat · Réglages · Extensions · Bilan · À propos.
   Everything shown comes from the integration (hestia_energy/view, sources, settings, periods); the tab computes nothing. */

type Hass={callWS:<T>(msg:Record<string,unknown>)=>Promise<T>;states:Record<string,{state:string;attributes:Record<string,unknown>}>};
type Verdict={retenu:string|null;valeur:number|null;ecartes:{source:string;raison:string}[]};
type View={pret:boolean;palier:number;equipement:{facture?:boolean;direct?:boolean;appareils?:boolean;soleil?:boolean;manque?:string[]};
 mois?:{euros:number|null;euros_energie:number|null};veille:{w:number;euros_par_an:number|null}|null;heures_creuses:[string,string][]|null;
 contrat:{option:string;kva:number;prix:Record<string,number>;revente:number|null};constats:{id:string;stat:string;texte:string|null;niveau:string}[];
 extensions:{period:string|null;tempo_today:string|null;inverter:string|null;channels:string[];kva:number|null;comwatt?:boolean;prevision?:boolean;pellets?:unknown;meteo?:boolean;confort?:boolean};
 source?:{compteurs:{type:string;stat:string;periode:string|null;nom:string}[];direct:boolean;officielles:{type:string;nom:string;materiel:boolean;direct:boolean;lien:string}[]};
 bilans?:{id:string;titre:string;texte:string}[];
 direct?:{en_marche:{nom:string;type:string;w:number}[];prochain_changement:{a:string;periode:string}|null;periode:string|null;prix:number|null;sources:Record<string,Verdict>}};
type Sources={compteurs:{type:string;stat:string;nom:string|null;periode:string|null;puissance:string[]}[];format_page:string|null};
type Reglages={kva:number|null;margin:number;export_price:number|null;option:string|null;bag_price:number|null;notify_service:string|null;notify_hour:number;offpeak:string|null};
type Settings={reglages:Reglages;trouve:{kva:number|null;option:string|null;export_price:number|null;poele?:boolean;heures_creuses?:string|null}};
type Period={debut:string;kwh_achetes:number;euros:number|null;euros_energie:number|null;soleil_couvre:number|null;revendu_euros:number|null;heures_inconnues:number};

const REPO='https://github.com/hestiaFB/hestia-energy-integration';
const VERSION='1.0.0b1';
const MONTHS=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
const num=(v:number,d=1)=>v.toLocaleString('fr-FR',{maximumFractionDigits:d,useGrouping:'always' as unknown as boolean});
const eur=(v:number|null|undefined)=>v==null?'—':Math.abs(v)<10?v.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2})+' €':num(v,0)+' €';
const QUANTITY:Record<string,string>={achat:'Achat au réseau',revente:'Revente',soleil:'Production'};
const KIND:Record<string,string>={import:'Achat au réseau',export:'Revente',solar:'Panneaux',gas:'Gaz',water:'Eau',device:'Appareil',water_device:'Eau (appareil)',battery_in:'Batterie (charge)',battery_out:'Batterie (décharge)'};
const REASON:Record<string,string>={controle:'contrôle',fige:'écartée : ne bouge plus',muet:'en attente : ne répond plus',indisponible:'indisponible'};
// What one more piece of equipment would bring (PHRASES.md p_palier_plus).
const PLUS:Record<string,[string,string]>={
 direct:['Voir la maison en direct','Un module sur la prise TIC du Linky (LiXee, linkytic, ESPHome) : prix de l’heure, pointe, bon moment pour une machine.'],
 appareils:['Mesurer un premier appareil','Une prise mesurée sur le frigo ou le chauffe-eau dirait d’où vient la veille.'],
 compteur:['Ajouter la consommation','Dans Paramètres → Tableaux de bord → Énergie : le Linky (HA Linky, sans matériel) ou un compteur.'],
};
const STEPS:[string,string][]=[['0 · La facture','bilans, veille, contrat'],['1 · En direct','prix de l’heure, pointe'],['2 · Les appareils','par usage, cycles'],['3 · Le soleil','panneaux, prévision'],['4 · Appareils confiés','planificateur']];

@customElement('hestia-energy-setup')
export class HestiaEnergySetup extends LitElement {
 static styles=[hubStyles,modernStyles,pageStyles,css`
  .steps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
  .step{border:1px solid var(--divider-color);border-radius:10px;padding:10px;font-size:13px}
  .step b{display:block;font-size:13px}.step span{color:var(--secondary-text-color);font-size:12px;display:block;margin-top:2px}
  .step.on{border-color:var(--primary-color);box-shadow:inset 0 0 0 1px var(--primary-color)}.step.on b::before{content:"✓ ";color:var(--primary-color)}
  .step.next{border-style:dashed}
  .tscroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px;min-width:520px}
  th{text-align:left;color:var(--secondary-text-color);font-weight:500;padding:6px 8px;border-bottom:1px solid var(--divider-color)}
  td{padding:8px;border-bottom:1px solid var(--divider-color);vertical-align:top}td.pick{color:var(--primary-color);font-weight:600}td.off{color:var(--secondary-text-color)}
  .num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
  code{font-size:12px;border:1px solid var(--divider-color);border-radius:6px;padding:1px 6px;word-break:break-all}
  @media(max-width:820px){.steps{grid-template-columns:repeat(2,minmax(0,1fr))}}`];
 @property({attribute:false}) hass?:Hass;
 @property({attribute:false}) route?:{prefix?:string;path:string};
 @property({type:Boolean}) narrow=false;
 @state() private view?:View;
 @state() private sources?:Sources;
 @state() private settings?:Settings;
 @state() private draft:Partial<Reglages>={};
 @state() private months?:Period[];
 @state() private error?:string;
 @state() private saving=false;
 @state() private saved=false;

 connectedCallback(){super.connectedCallback();void this.load();}
 private async load(){
  if(!this.hass)return;
  try{
   [this.view,this.sources]=await Promise.all([this.hass.callWS<View>({type:'hestia_energy/view'}),this.hass.callWS<Sources>({type:'hestia_energy/sources'})]);
   this.error=undefined;
  }catch(e){this.error=(e as {message?:string}).message??'Hestia Énergie ne répond pas.';}
 }
 updated(changed:Map<string,unknown>){
  if(changed.has('hass')&&!this.view&&!this.error)void this.load();
  if(changed.has('route')||changed.has('hass')){const page=this.page();
   if(page==='reglages'&&!this.settings&&this.hass)void this.loadSettings();
   if(page==='bilan'&&!this.months&&this.hass)void this.loadMonths();}
 }
 private async loadMonths(){
  this.months=[];
  const end=new Date(),start=new Date(end.getFullYear()-1,end.getMonth()+1,1);
  const iso=(d:Date)=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  // Just after a restart the reports are not ready yet: asked again a few seconds later, never an error left unseen.
  try{const r=await this.hass!.callWS<{periodes:Period[]}>({type:'hestia_energy/periods',du:iso(start),au:iso(end),pas:'mois'});this.months=r.periodes;}
  catch{this.months=undefined;setTimeout(()=>{if(this.page()==='bilan'&&!this.months)void this.loadMonths();},5000);}
 }
 private async loadSettings(){
  try{this.settings=await this.hass!.callWS<Settings>({type:'hestia_energy/settings'});}
  catch{setTimeout(()=>{if(this.page()==='reglages'&&!this.settings)void this.loadSettings();},5000);}
 }
 private page(){return (this.route?.path??'').replace(/^\//,'').split('/')[0];}
 private go(path:string){history.pushState(null,'',(this.route?.prefix??'/hestia/energie')+(path?'/'+path:''));window.dispatchEvent(new CustomEvent('location-changed'));}

 render(){
  const header=this.hasAttribute('embedded')?nothing:html`<header><strong>Hestia Énergie</strong></header>`;
  const v=this.view;
  if(this.error)return html`${header}<main>${pageHead({title:'Énergie',state:{level:'todo',text:this.error}})}</main>`;
  if(!v||!v.pret)return html`${header}<main>${pageHead({title:'Énergie',subtitle:'Lecture de la page Énergie et de ses statistiques…'})}</main>`;
  const pages:Record<string,()=>TemplateResult>={'':()=>this.overview(v),sources:()=>this.sourcesPage(v),appareils:()=>this.devicesPage(v),contrat:()=>this.contractPage(v),
   reglages:()=>this.settingsPage(),extensions:()=>this.extensionsPage(v),bilan:()=>this.reviewPage(),'a-propos':()=>this.aboutPage(v)};
  return html`${header}<main>${(pages[this.page()]??pages[''])()}</main>`;
 }

 /* ── Vue d'ensemble ── */
 private overview(v:View){
  const constats=(v.constats??[]).filter(c=>c.niveau==='regler');
  const todo:NkLine[]=constats.filter(c=>c.texte).slice(0,5).map(c=>({level:'todo',text:c.texte!,go:{label:'Sources',onClick:()=>this.go('sources')}}));
  const tips:NkLine[]=(v.equipement.manque??[]).filter(k=>PLUS[k]).map(k=>({level:'tip',text:PLUS[k][0],why:PLUS[k][1]}));
  const more=constats.length-todo.length;
  return html`${pageHead({title:'Énergie',subtitle:'Le conseiller énergie de la maison.',state:constats.length?{level:'todo',text:`${constats.length} point(s) à régler`,detail:`${(v.constats?.length??0)-constats.length} autres corrigés par Hestia`}:{level:'ok',text:'Tout est suivi'}})}
   ${kpis([{value:`Palier ${v.palier}`,label:'sur 4'},{value:eur(v.mois?.euros??v.mois?.euros_energie),label:'ce mois',go:()=>this.go('bilan')},
    ...(v.veille?[{value:`${v.veille.w} W`,label:'veille de nuit'}]:[])])}
   ${todoFrame(todo,tips)}${more>0?html`<p class="muted">Et ${more} autre(s) dans « Sources ».</p>`:nothing}
   ${frame(`Ce que Hestia Énergie voit · palier ${v.palier} sur 4`,html`<div class="steps">${STEPS.map(([b,s],i)=>html`<div class=${'step'+(i<=v.palier?' on':i===v.palier+1?' next':'')}><b>${b}</b><span>${s}</span></div>`)}</div>`)}
   ${frame('Avec les autres briques',html`<ul class="nk-lines">${this.brick('Hestia Météo','sensor.hestia_weather_','degrés-jours, ensoleillement, soleil mesuré : lus, jamais recalculés')}
    ${this.brick('Hestia Confort','sensor.hestia_comfort_','reçoit les prix (coût d’une aération) ; donne l’inertie et les kWh de chaque geste')}</ul>`)}
   ${noteBox('Préversion 1.0.0b1.','Le simulateur de contrat, les appareils par usage, la prévision solaire recalée et les appareils confiés arrivent avec les prochaines versions.')}`;
 }
 private brick(name:string,prefix:string,use:string){
  const on=Object.keys(this.hass?.states??{}).some(e=>e.startsWith(prefix));
  return html`<li class=${'nk-line '+(on?'ok':'none')}><span class="nk-dot"></span><div><strong>${name}</strong><span class="nk-why">${on?use:'non installé'}</span></div></li>`;
 }

 /* ── Sources : l'arbitre, une vérité par mesure ── */
 private sourcesPage(v:View){
  const live=v.direct?.sources??{};
  const rows=Object.entries(live).flatMap(([k,x])=>[html`<tr><td><b>${QUANTITY[k]??k}</b></td><td>${x.retenu??'—'}</td><td class="pick">${x.retenu?'retenue':'aucune'}</td><td class="num">${x.valeur==null?'—':num(x.valeur,0)+' W'}</td></tr>`,
   ...x.ecartes.map(e=>html`<tr><td></td><td>${e.source}</td><td class="off">${REASON[e.raison]??e.raison}</td><td></td></tr>`)]);
  const meters=this.sources?.compteurs??[];
  return html`${pageHead({title:'Sources',subtitle:'Une vérité par mesure : la plus fraîche et la plus cohérente gagne ; à égalité, la source locale.'})}
   ${frame('En direct',html`<div class="tscroll"><table><thead><tr><th>Mesure</th><th>Source</th><th>Rôle</th><th class="num">Maintenant</th></tr></thead><tbody>${rows}</tbody></table></div>`)}
   ${listSection('À régler',(v.constats??[]).filter(c=>c.niveau==='regler').map(c=>listRow({label:c.texte??c.id,sub:c.stat||undefined,level:'todo'})))}
   ${(v.constats??[]).some(c=>c.id.startsWith('p_reference'))?listSection('Comparé à Enedis (fait foi pour la facture)',[...(v.constats??[]).filter(c=>c.id.startsWith('p_reference')).map(c=>listRow({label:c.texte??c.id})),listRow({label:'Vos bilans et vos euros suivent Enedis, jour par jour.'})]):nothing}
   ${listSection('Corrigé par Hestia',(v.constats??[]).filter(c=>c.niveau!=='regler'&&!c.id.startsWith('p_reference')).map(c=>listRow({label:c.texte??c.id,sub:c.stat||undefined})))}
   ${listSection(`La page Énergie · format ${this.sources?.format_page??'?'}`,meters.map(m=>listRow({label:html`<b>${KIND[m.type]??m.type}</b> · ${m.nom??m.stat}`,
    sub:html`<code>${m.stat}</code>${m.periode?` · ${m.periode==='hc'?'heures creuses':'heures pleines'}`:''}${m.puissance.length?html` · puissance <code>${m.puissance.join(', ')}</code>`:nothing}`})))}`;
 }

 /* ── Appareils ── */
 private devicesPage(v:View){
  const running=[...(v.direct?.en_marche??[])].sort((a,b)=>b.w-a.w),devices=(this.sources?.compteurs??[]).filter(m=>m.type==='device');
  return html`${pageHead({title:'Appareils',subtitle:'Les appareils mesurés par la page Énergie, et ceux qu’on pourra confier à Hestia.'})}
   ${listSection('En marche',running.length?running.map(r=>listRow({label:r.nom,value:`${num(r.w/1000,1)} kW`})):listRow({label:'Rien de gros ne tourne.'}))}
   ${listSection(`Mesurés · ${devices.length}`,devices.map(d=>listRow({label:d.nom??d.stat,sub:html`<code>${d.stat}</code>`})))}
   ${noteBox('Appareils confiés.','Le chauffe-eau, la piscine, les machines : Hestia pourra les placer au bon moment, avec des garanties. Rien n’est commandé dans cette préversion.')}`;
 }

 /* ── Contrat ── */
 private contractPage(v:View){
  const c=v.contrat,p=c.prix??{},next=v.direct?.prochain_changement;
  const option=c.option==='hphc'?'Heures pleines / heures creuses':c.option==='tempo'?'Tempo':'Base';
  const price=(label:string,x:number|undefined|null)=>x!=null?[listRow({label,value:`${num(x,4)} € le kWh`})]:[];
  return html`${pageHead({title:'Contrat',subtitle:'Lu sur le compteur et dans la page Énergie ; les tarifs réglementés embarqués complètent ce qui manque.'})}
   ${listSection('Votre contrat',[listRow({label:'Option',value:option}),listRow({label:'Puissance souscrite',value:c.kva?`${c.kva} kVA`:'—',go:()=>this.go('reglages')}),
    ...price('Heures pleines',p.hp),...price('Heures creuses',p.hc),...price('Base',p.base),...price('Revente du surplus',c.revente)])}
   ${listSection('Heures creuses',[listRow({label:v.heures_creuses?.length?v.heures_creuses.map(([a,b])=>`De ${a} à ${b}`).join(' et '):'Pas d’heures creuses lues',sub:'Apprises sur les deux compteurs heures pleines / heures creuses, sur 28 jours.'}),
    ...(next?[listRow({label:'Prochain changement',value:new Date(next.a).toLocaleString('fr-FR',{weekday:'long',hour:'numeric',minute:'2-digit'})})]:[])])}
   ${noteBox('Simulateur de contrat.','Vos 12 derniers mois recalculés avec Base, heures creuses et Tempo, et la puissance souscrite : avec la première version stable.')}`;
 }

 /* ── Réglages ── */
 private settingsPage(){
  const s=this.settings;
  if(!s)return html`${pageHead({title:'Réglages'})}<p class="muted">Lecture…</p>`;
  const value=<K extends keyof Reglages>(k:K):Reglages[K]=>(k in this.draft?this.draft[k]:s.reglages[k]) as Reglages[K];
  const set=(k:keyof Reglages,x:unknown)=>{this.draft={...this.draft,[k]:x};this.saved=false;};
  const count=(Object.keys(this.draft) as (keyof Reglages)[]).filter(k=>this.draft[k]!==s.reglages[k]).length;
  const kva=value('kva');
  return html`${pageHead({title:'Réglages',subtitle:'Ce qui dépend du foyer. Laissé vide, Hestia prend ce qu’elle a trouvé.'})}
   ${listSection('Le contrat',[
    listRow({label:'Puissance souscrite',sub:`Trouvée : ${s.trouve.kva??'?'} kVA`,control:true,value:segmented('Puissance souscrite',[['auto','Trouvée'],['3','3'],['6','6'],['9','9'],['12','12'],['15','15'],['18','18']],kva==null?'auto':String(kva),(x:string)=>set('kva',x==='auto'?null:Number(x)))}),
    listRow({label:'Marge sous la puissance souscrite',sub:'Pour la puissance maximale donnée au délestage de Versatile Thermostat.',control:true,value:numberField({label:'Marge',value:Math.round((value('margin')??0.1)*100),unit:'%',dflt:10,min:0,max:30,step:1,set:(x:number|undefined)=>set('margin',(x??10)/100)})}),
    listRow({label:'Heures creuses',sub:s.trouve.heures_creuses?`Lues sur le compteur, ${s.trouve.heures_creuses}. Laissez vide.`:'Un seul compteur : indiquez-les, par exemple 22:00-06:00.',control:true,
     value:html`<input type="text" aria-label="Heures creuses" placeholder=${s.trouve.heures_creuses?'':'22:00-06:00'} .value=${value('offpeak')??''} @input=${(e:Event)=>set('offpeak',(e.target as HTMLInputElement).value.trim()||null)}>`}),
    listRow({label:'Prix de revente du surplus',sub:'Vide : celui de la page Énergie.',control:true,value:numberField({label:'Prix de revente',value:value('export_price')??undefined,unit:'€ le kWh',dflt:s.trouve.export_price??undefined,min:0,max:1,step:0.0001,set:(x:number|undefined)=>set('export_price',x??null)})}),
   ])}
   ${listSection('Bilans par notification',[
    listRow({label:'Envoyer les bilans à',sub:'Chaque matin, le bilan d’hier ; le lundi, celui de la semaine ; le 1er, celui du mois.',control:true,
     value:html`<select aria-label="Envoyer les bilans à" @change=${(e:Event)=>{const x=(e.target as HTMLSelectElement).value;set('notify_service',x==='aucun'?null:x);}}>
      <option value="aucun" ?selected=${!value('notify_service')}>Personne</option>
      ${Object.keys((this.hass as unknown as {services:Record<string,Record<string,unknown>>}).services?.notify??{}).filter(n=>n!=='send_message').sort().map(n=>html`<option value=${'notify.'+n} ?selected=${value('notify_service')==='notify.'+n}>${n}</option>`)}
     </select>`}),
    ...(value('notify_service')?[listRow({label:'À quelle heure',control:true,value:numberField({label:'Heure',value:value('notify_hour')??8,unit:'h',dflt:8,min:0,max:23,step:1,set:(x:number|undefined)=>set('notify_hour',x??8)})})]:[]),
   ])}
   ${s.trouve.poele?listSection('Le poêle',[
    listRow({label:'Prix du sac de granulés',sub:'Utilisé tant qu’aucun achat n’est saisi dans Suivi Stock Pellet.',control:true,value:numberField({label:'Prix du sac',value:value('bag_price')??undefined,unit:'€',min:0,max:100,step:0.01,set:(x:number|undefined)=>set('bag_price',x??null)})}),
   ]):nothing}
   ${saveBar({count,busy:this.saving,done:this.saved?'Enregistré':undefined,cancel:()=>{this.draft={};},save:()=>void this.save()})}`;
 }
 private async save(){
  this.saving=true;
  try{
   await this.hass!.callWS({type:'hestia_energy/set_settings',reglages:this.draft});
   this.settings=await this.hass!.callWS<Settings>({type:'hestia_energy/settings'});this.draft={};this.saved=true;void this.load();
  }finally{this.saving=false;}
 }

 /* ── Extensions ── */
 private extensionsPage(v:View){
  const e=v.extensions,has=(prefix:string)=>Object.keys(this.hass?.states??{}).some(x=>x.startsWith(prefix));
  const pill=(on:boolean,text='lue')=>({text:on?text:'non trouvée',level:(on?'ok':'none') as 'ok'|'none'});
  const src=v.source,names=[...new Set((src?.compteurs??[]).map(m=>m.nom))];
  const how=(o:{materiel:boolean;direct:boolean})=>`${o.materiel?'avec un module':'sans matériel'}, ${o.direct?'en direct':'la veille'}`;
  return html`${pageHead({title:'Extensions',subtitle:'Ce que Hestia Énergie lit. Une source de consommation est obligatoire ; le reste est facultatif.'})}
   ${listSection('Source de consommation · obligatoire',names.length
    ?[listRow({label:names.join(', '),sub:`${src!.compteurs.length>1?`${src!.compteurs.length} compteurs`:'Un compteur'} dans la page Énergie, ${src!.direct?'en direct':'la veille'}.`,value:'lue'})]
    :(src?.officielles??[]).map(o=>listRow({label:o.nom,sub:how(o)+'.',value:html`<a href=${o.lien} target="_blank" rel="noreferrer">Installer</a>`})))}
   ${extensionsFrame([
    {name:'Compteur Linky en direct (TIC : LiXee, linkytic)',group:'Électricité',pill:pill(!!e?.period,'période lue')},
    {name:'Tempo (couleur du jour et du lendemain)',group:'Électricité',pill:pill(!!e?.tempo_today)},
    {name:`OpenDTU (onduleurs${e?.channels?.length?`, ${e.channels.length} voies`:''})`,group:'Soleil',pill:pill(!!e?.inverter)},
    {name:'Prévision solaire (Forecast.Solar, Solcast)',group:'Soleil',pill:e?.prevision?{text:'trouvée · servira à la 2ᵉ préversion',level:'none'}:pill(false)},
    {name:'Comwatt (appareils et pinces, en cloud)',group:'Appareils',pill:pill(!!e?.comwatt)},
    {name:'Suivi Stock Pellet (poêle à granulés)',group:'Chauffage',pill:pill(!!e?.pellets)},
    {name:'Hestia Météo',group:'Hestia-FB',pill:pill(e?.meteo??has('sensor.hestia_weather_'),'liée')},
    {name:'Hestia Confort',group:'Hestia-FB',pill:pill(e?.confort??has('sensor.hestia_comfort_'),'liée')},
   ])}`;
 }

 /* ── Bilan ── */
 private reviewPage(){
  const m=this.months;
  const last=this.view?.bilans??[];
  return html`${pageHead({title:'Bilan',subtitle:'Les 12 derniers mois, tirés des statistiques de la page Énergie. Un prix inconnu n’est jamais compté gratuit.'})}
   ${last.length?listSection('Les derniers bilans',last.map(b=>listRow({label:b.titre,sub:b.texte}))):nothing}
   ${m?.length?frame('Mois par mois',html`<div class="tscroll"><table><thead><tr><th>Mois</th><th class="num">Acheté</th><th class="num">Électricité</th><th class="num">Avec l’abonnement</th><th class="num">Soleil</th></tr></thead><tbody>
    ${m.map(p=>{const d=new Date(p.debut);return html`<tr><td>${MONTHS[d.getMonth()]} ${d.getFullYear()}</td><td class="num">${num(p.kwh_achetes,0)} kWh</td><td class="num">${eur(p.euros_energie)}</td><td class="num">${eur(p.euros)}</td><td class="num">${p.soleil_couvre==null?'—':p.soleil_couvre+' %'}</td></tr>`;})}
   </tbody></table></div><p class="muted">« — » : le prix de cette période n’est pas dans la table des tarifs réglementés embarquée.</p>`):html`<p class="muted">Calcul…</p>`}`;
 }

 /* ── À propos ── */
 private aboutPage(v:View){
  const entities=Object.keys(this.hass?.states??{}).filter(e=>/^(binary_)?sensor\.hestia_energy_/.test(e)).sort();
  return html`${aboutPage({name:'Hestia Énergie',versions:[['Hestia Énergie',VERSION],['Interface hestia_energy_api','v1'],['Palier',String(v.palier)]],repository:REPO,card:'custom:hestia-energy-card'})}
   ${listSection(`Entités publiées · ${entities.length}`,entities.map(e=>listRow({label:html`<code>${e}</code>`,value:this.hass!.states[e].state})))}`;
 }
}
