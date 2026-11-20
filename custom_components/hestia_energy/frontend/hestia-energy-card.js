// Home Assistant frontend#53890: wait for the final custom element registry.
while (!customElements.get('home-assistant')) {
  await customElements.whenDefined('home-assistant');
}
"use strict";(()=>{var je=globalThis,Se=je.ShadowRoot&&(je.ShadyCSS===void 0||je.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Te=Symbol(),dn=new WeakMap,le=class{constructor(s,e,n){if(this._$cssResult$=!0,n!==Te)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=s,this.t=e}get styleSheet(){let s=this.o,e=this.t;if(Se&&s===void 0){let n=e!==void 0&&e.length===1;n&&(s=dn.get(e)),s===void 0&&((this.o=s=new CSSStyleSheet).replaceSync(this.cssText),n&&dn.set(e,s))}return s}toString(){return this.cssText}},ue=o=>new le(typeof o=="string"?o:o+"",void 0,Te),Ve=(o,...s)=>{let e=o.length===1?o[0]:s.reduce((n,t,r)=>n+(a=>{if(a._$cssResult$===!0)return a.cssText;if(typeof a=="number")return a;throw Error("Value passed to 'css' function must be a 'css' function result: "+a+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(t)+o[r+1],o[0]);return new le(e,o,Te)},hn=(o,s)=>{if(Se)o.adoptedStyleSheets=s.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of s){let n=document.createElement("style"),t=je.litNonce;t!==void 0&&n.setAttribute("nonce",t),n.textContent=e.cssText,o.appendChild(n)}},Ue=Se?o=>o:o=>o instanceof CSSStyleSheet?(s=>{let e="";for(let n of s.cssRules)e+=n.cssText;return ue(e)})(o):o;var{is:Xn,defineProperty:Zn,getOwnPropertyDescriptor:et,getOwnPropertyNames:nt,getOwnPropertySymbols:tt,getPrototypeOf:st}=Object,Ce=globalThis,mn=Ce.trustedTypes,rt=mn?mn.emptyScript:"",it=Ce.reactiveElementPolyfillSupport,ce=(o,s)=>o,De={toAttribute(o,s){switch(s){case Boolean:o=o?rt:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,s){let e=o;switch(s){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},fn=(o,s)=>!Xn(o,s),gn={attribute:!0,type:String,converter:De,reflect:!1,useDefault:!1,hasChanged:fn};Symbol.metadata??=Symbol("metadata"),Ce.litPropertyMetadata??=new WeakMap;var U=class extends HTMLElement{static addInitializer(s){this._$Ei(),(this.l??=[]).push(s)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(s,e=gn){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(s)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(s,e),!e.noAccessor){let n=Symbol(),t=this.getPropertyDescriptor(s,n,e);t!==void 0&&Zn(this.prototype,s,t)}}static getPropertyDescriptor(s,e,n){let{get:t,set:r}=et(this.prototype,s)??{get(){return this[e]},set(a){this[e]=a}};return{get:t,set(a){let l=t?.call(this);r?.call(this,a),this.requestUpdate(s,l,n)},configurable:!0,enumerable:!0}}static getPropertyOptions(s){return this.elementProperties.get(s)??gn}static _$Ei(){if(this.hasOwnProperty(ce("elementProperties")))return;let s=st(this);s.finalize(),s.l!==void 0&&(this.l=[...s.l]),this.elementProperties=new Map(s.elementProperties)}static finalize(){if(this.hasOwnProperty(ce("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(ce("properties"))){let e=this.properties,n=[...nt(e),...tt(e)];for(let t of n)this.createProperty(t,e[t])}let s=this[Symbol.metadata];if(s!==null){let e=litPropertyMetadata.get(s);if(e!==void 0)for(let[n,t]of e)this.elementProperties.set(n,t)}this._$Eh=new Map;for(let[e,n]of this.elementProperties){let t=this._$Eu(e,n);t!==void 0&&this._$Eh.set(t,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(s){let e=[];if(Array.isArray(s)){let n=new Set(s.flat(1/0).reverse());for(let t of n)e.unshift(Ue(t))}else s!==void 0&&e.push(Ue(s));return e}static _$Eu(s,e){let n=e.attribute;return n===!1?void 0:typeof n=="string"?n:typeof s=="string"?s.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(s=>this.enableUpdating=s),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(s=>s(this))}addController(s){(this._$EO??=new Set).add(s),this.renderRoot!==void 0&&this.isConnected&&s.hostConnected?.()}removeController(s){this._$EO?.delete(s)}_$E_(){let s=new Map,e=this.constructor.elementProperties;for(let n of e.keys())this.hasOwnProperty(n)&&(s.set(n,this[n]),delete this[n]);s.size>0&&(this._$Ep=s)}createRenderRoot(){let s=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return hn(s,this.constructor.elementStyles),s}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(s=>s.hostConnected?.())}enableUpdating(s){}disconnectedCallback(){this._$EO?.forEach(s=>s.hostDisconnected?.())}attributeChangedCallback(s,e,n){this._$AK(s,n)}_$ET(s,e){let n=this.constructor.elementProperties.get(s),t=this.constructor._$Eu(s,n);if(t!==void 0&&n.reflect===!0){let r=(n.converter?.toAttribute!==void 0?n.converter:De).toAttribute(e,n.type);this._$Em=s,r==null?this.removeAttribute(t):this.setAttribute(t,r),this._$Em=null}}_$AK(s,e){let n=this.constructor,t=n._$Eh.get(s);if(t!==void 0&&this._$Em!==t){let r=n.getPropertyOptions(t),a=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:De;this._$Em=t;let l=a.fromAttribute(e,r.type);this[t]=l??this._$Ej?.get(t)??l,this._$Em=null}}requestUpdate(s,e,n,t=!1,r){if(s!==void 0){let a=this.constructor;if(t===!1&&(r=this[s]),n??=a.getPropertyOptions(s),!((n.hasChanged??fn)(r,e)||n.useDefault&&n.reflect&&r===this._$Ej?.get(s)&&!this.hasAttribute(a._$Eu(s,n))))return;this.C(s,e,n)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(s,e,{useDefault:n,reflect:t,wrapped:r},a){n&&!(this._$Ej??=new Map).has(s)&&(this._$Ej.set(s,a??e??this[s]),r!==!0||a!==void 0)||(this._$AL.has(s)||(this.hasUpdated||n||(e=void 0),this._$AL.set(s,e)),t===!0&&this._$Em!==s&&(this._$Eq??=new Set).add(s))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let s=this.scheduleUpdate();return s!=null&&await s,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[t,r]of this._$Ep)this[t]=r;this._$Ep=void 0}let n=this.constructor.elementProperties;if(n.size>0)for(let[t,r]of n){let{wrapped:a}=r,l=this[t];a!==!0||this._$AL.has(t)||l===void 0||this.C(t,void 0,r,l)}}let s=!1,e=this._$AL;try{s=this.shouldUpdate(e),s?(this.willUpdate(e),this._$EO?.forEach(n=>n.hostUpdate?.()),this.update(e)):this._$EM()}catch(n){throw s=!1,this._$EM(),n}s&&this._$AE(e)}willUpdate(s){}_$AE(s){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(s)),this.updated(s)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(s){return!0}update(s){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(s){}firstUpdated(s){}};U.elementStyles=[],U.shadowRootOptions={mode:"open"},U[ce("elementProperties")]=new Map,U[ce("finalized")]=new Map,it?.({ReactiveElement:U}),(Ce.reactiveElementVersions??=[]).push("2.1.2");var Je=globalThis,wn=o=>o,Me=Je.trustedTypes,bn=Me?Me.createPolicy("lit-html",{createHTML:o=>o}):void 0,yn="$lit$",N=`lit$${Math.random().toFixed(9).slice(2)}$`,An="?"+N,at=`<${An}>`,Y=document,de=()=>Y.createComment(""),he=o=>o===null||typeof o!="object"&&typeof o!="function",Ge=Array.isArray,ot=o=>Ge(o)||typeof o?.[Symbol.iterator]=="function",Be=`[ 	
\f\r]`,pe=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,vn=/-->/g,xn=/>/g,J=RegExp(`>|${Be}(?:([^\\s"'>=/]+)(${Be}*=${Be}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),$n=/'/g,_n=/"/g,jn=/^(?:script|style|textarea|title)$/i,Ye=o=>(s,...e)=>({_$litType$:o,strings:s,values:e}),i=Ye(1),I=Ye(2),yt=Ye(3),D=Symbol.for("lit-noChange"),c=Symbol.for("lit-nothing"),kn=new WeakMap,G=Y.createTreeWalker(Y,129);function Sn(o,s){if(!Ge(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return bn!==void 0?bn.createHTML(s):s}var lt=(o,s)=>{let e=o.length-1,n=[],t,r=s===2?"<svg>":s===3?"<math>":"",a=pe;for(let l=0;l<e;l++){let u=o[l],p,g,d=-1,f=0;for(;f<u.length&&(a.lastIndex=f,g=a.exec(u),g!==null);)f=a.lastIndex,a===pe?g[1]==="!--"?a=vn:g[1]!==void 0?a=xn:g[2]!==void 0?(jn.test(g[2])&&(t=RegExp("</"+g[2],"g")),a=J):g[3]!==void 0&&(a=J):a===J?g[0]===">"?(a=t??pe,d=-1):g[1]===void 0?d=-2:(d=a.lastIndex-g[2].length,p=g[1],a=g[3]===void 0?J:g[3]==='"'?_n:$n):a===_n||a===$n?a=J:a===vn||a===xn?a=pe:(a=J,t=void 0);let h=a===J&&o[l+1].startsWith("/>")?" ":"";r+=a===pe?u+at:d>=0?(n.push(p),u.slice(0,d)+yn+u.slice(d)+N+h):u+N+(d===-2?l:h)}return[Sn(o,r+(o[e]||"<?>")+(s===2?"</svg>":s===3?"</math>":"")),n]},me=class o{constructor({strings:s,_$litType$:e},n){let t;this.parts=[];let r=0,a=0,l=s.length-1,u=this.parts,[p,g]=lt(s,e);if(this.el=o.createElement(p,n),G.currentNode=this.el.content,e===2||e===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(t=G.nextNode())!==null&&u.length<l;){if(t.nodeType===1){if(t.hasAttributes())for(let d of t.getAttributeNames())if(d.endsWith(yn)){let f=g[a++],h=t.getAttribute(d).split(N),w=/([.?@])?(.*)/.exec(f);u.push({type:1,index:r,name:w[2],strings:h,ctor:w[1]==="."?Ne:w[1]==="?"?Ie:w[1]==="@"?Fe:se}),t.removeAttribute(d)}else d.startsWith(N)&&(u.push({type:6,index:r}),t.removeAttribute(d));if(jn.test(t.tagName)){let d=t.textContent.split(N),f=d.length-1;if(f>0){t.textContent=Me?Me.emptyScript:"";for(let h=0;h<f;h++)t.append(d[h],de()),G.nextNode(),u.push({type:2,index:++r});t.append(d[f],de())}}}else if(t.nodeType===8)if(t.data===An)u.push({type:2,index:r});else{let d=-1;for(;(d=t.data.indexOf(N,d+1))!==-1;)u.push({type:7,index:r}),d+=N.length-1}r++}}static createElement(s,e){let n=Y.createElement("template");return n.innerHTML=s,n}};function te(o,s,e=o,n){if(s===D)return s;let t=n!==void 0?e._$Co?.[n]:e._$Cl,r=he(s)?void 0:s._$litDirective$;return t?.constructor!==r&&(t?._$AO?.(!1),r===void 0?t=void 0:(t=new r(o),t._$AT(o,e,n)),n!==void 0?(e._$Co??=[])[n]=t:e._$Cl=t),t!==void 0&&(s=te(o,t._$AS(o,s.values),t,n)),s}var Oe=class{constructor(s,e){this._$AV=[],this._$AN=void 0,this._$AD=s,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(s){let{el:{content:e},parts:n}=this._$AD,t=(s?.creationScope??Y).importNode(e,!0);G.currentNode=t;let r=G.nextNode(),a=0,l=0,u=n[0];for(;u!==void 0;){if(a===u.index){let p;u.type===2?p=new ge(r,r.nextSibling,this,s):u.type===1?p=new u.ctor(r,u.name,u.strings,this,s):u.type===6&&(p=new Ke(r,this,s)),this._$AV.push(p),u=n[++l]}a!==u?.index&&(r=G.nextNode(),a++)}return G.currentNode=Y,t}p(s){let e=0;for(let n of this._$AV)n!==void 0&&(n.strings!==void 0?(n._$AI(s,n,e),e+=n.strings.length-2):n._$AI(s[e])),e++}},ge=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(s,e,n,t){this.type=2,this._$AH=c,this._$AN=void 0,this._$AA=s,this._$AB=e,this._$AM=n,this.options=t,this._$Cv=t?.isConnected??!0}get parentNode(){let s=this._$AA.parentNode,e=this._$AM;return e!==void 0&&s?.nodeType===11&&(s=e.parentNode),s}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(s,e=this){s=te(this,s,e),he(s)?s===c||s==null||s===""?(this._$AH!==c&&this._$AR(),this._$AH=c):s!==this._$AH&&s!==D&&this._(s):s._$litType$!==void 0?this.$(s):s.nodeType!==void 0?this.T(s):ot(s)?this.k(s):this._(s)}O(s){return this._$AA.parentNode.insertBefore(s,this._$AB)}T(s){this._$AH!==s&&(this._$AR(),this._$AH=this.O(s))}_(s){this._$AH!==c&&he(this._$AH)?this._$AA.nextSibling.data=s:this.T(Y.createTextNode(s)),this._$AH=s}$(s){let{values:e,_$litType$:n}=s,t=typeof n=="number"?this._$AC(s):(n.el===void 0&&(n.el=me.createElement(Sn(n.h,n.h[0]),this.options)),n);if(this._$AH?._$AD===t)this._$AH.p(e);else{let r=new Oe(t,this),a=r.u(this.options);r.p(e),this.T(a),this._$AH=r}}_$AC(s){let e=kn.get(s.strings);return e===void 0&&kn.set(s.strings,e=new me(s)),e}k(s){Ge(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,n,t=0;for(let r of s)t===e.length?e.push(n=new o(this.O(de()),this.O(de()),this,this.options)):n=e[t],n._$AI(r),t++;t<e.length&&(this._$AR(n&&n._$AB.nextSibling,t),e.length=t)}_$AR(s=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);s!==this._$AB;){let n=wn(s).nextSibling;wn(s).remove(),s=n}}setConnected(s){this._$AM===void 0&&(this._$Cv=s,this._$AP?.(s))}},se=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(s,e,n,t,r){this.type=1,this._$AH=c,this._$AN=void 0,this.element=s,this.name=e,this._$AM=t,this.options=r,n.length>2||n[0]!==""||n[1]!==""?(this._$AH=Array(n.length-1).fill(new String),this.strings=n):this._$AH=c}_$AI(s,e=this,n,t){let r=this.strings,a=!1;if(r===void 0)s=te(this,s,e,0),a=!he(s)||s!==this._$AH&&s!==D,a&&(this._$AH=s);else{let l=s,u,p;for(s=r[0],u=0;u<r.length-1;u++)p=te(this,l[n+u],e,u),p===D&&(p=this._$AH[u]),a||=!he(p)||p!==this._$AH[u],p===c?s=c:s!==c&&(s+=(p??"")+r[u+1]),this._$AH[u]=p}a&&!t&&this.j(s)}j(s){s===c?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,s??"")}},Ne=class extends se{constructor(){super(...arguments),this.type=3}j(s){this.element[this.name]=s===c?void 0:s}},Ie=class extends se{constructor(){super(...arguments),this.type=4}j(s){this.element.toggleAttribute(this.name,!!s&&s!==c)}},Fe=class extends se{constructor(s,e,n,t,r){super(s,e,n,t,r),this.type=5}_$AI(s,e=this){if((s=te(this,s,e,0)??c)===D)return;let n=this._$AH,t=s===c&&n!==c||s.capture!==n.capture||s.once!==n.once||s.passive!==n.passive,r=s!==c&&(n===c||t);t&&this.element.removeEventListener(this.name,this,n),r&&this.element.addEventListener(this.name,this,s),this._$AH=s}handleEvent(s){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,s):this._$AH.handleEvent(s)}},Ke=class{constructor(s,e,n){this.element=s,this.type=6,this._$AN=void 0,this._$AM=e,this.options=n}get _$AU(){return this._$AM._$AU}_$AI(s){te(this,s)}};var ut=Je.litHtmlPolyfillSupport;ut?.(me,ge),(Je.litHtmlVersions??=[]).push("3.3.3");var Cn=(o,s,e)=>{let n=e?.renderBefore??s,t=n._$litPart$;if(t===void 0){let r=e?.renderBefore??null;n._$litPart$=t=new ge(s.insertBefore(de(),r),r,void 0,e??{})}return t._$AI(o),t};var Qe=globalThis,R=class extends U{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let s=super.createRenderRoot();return this.renderOptions.renderBefore??=s.firstChild,s}update(s){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(s),this._$Do=Cn(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return D}};R._$litElement$=!0,R.finalized=!0,Qe.litElementHydrateSupport?.({LitElement:R});var ct=Qe.litElementPolyfillSupport;ct?.({LitElement:R});(Qe.litElementVersions??=[]).push("4.2.2");var Mn={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},En=o=>(...s)=>({_$litDirective$:o,values:s}),Ee=class{constructor(s){}get _$AU(){return this._$AM._$AU}_$AT(s,e,n){this._$Ct=s,this._$AM=e,this._$Ci=n}_$AS(s,e){return this.update(s,e)}update(s,e){return this.render(...e)}};var fe=class extends Ee{constructor(s){if(super(s),this.it=c,s.type!==Mn.CHILD)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(s){if(s===c||s==null)return this._t=void 0,this.it=s;if(s===D)return s;if(typeof s!="string")throw Error(this.constructor.directiveName+"() called with a non-string value");if(s===this.it)return this._t;this.it=s;let e=[s];return e.raw=e,this._t={_$litType$:this.constructor.resultType,strings:e,values:[]}}};fe.directiveName="unsafeHTML",fe.resultType=1;var zn=En(fe);var Ln=`/* CHARTE COMMUNE HESTIA \u2014 jetons et pi\xE8ces partag\xE9s par toutes les cartes Hestia.
   Valeurs reprises de la carte Hestia Weather (card/src/ui/charter.ts), qui fait r\xE9f\xE9rence.
   Modifier ICI, puis recopier avec charte/copier.sh dans chaque carte : jamais directement dans une brique. */
:host {
  /* Couleurs du th\xE8me Home Assistant, avec replis. */
  --nw-fg: var(--primary-text-color, #212121);
  --nw-fg2: var(--secondary-text-color, #727272);
  --nw-bg: var(--ha-card-background, var(--card-background-color, #fff));
  --nw-accent: var(--primary-color, #03a9f4);
  /* Contours et arrondis : un seul arrondi pour toutes les bo\xEEtes, un pour les pastilles. */
  --nw-line: color-mix(in srgb, var(--nw-fg) 13%, transparent);
  --nw-line-soft: color-mix(in srgb, var(--nw-fg) 8%, transparent);
  --nw-radius-card: var(--ha-card-border-radius, 12px);
  --nw-radius: 14px;
  --nw-radius-pill: 999px;
  --nw-glass-strong: color-mix(in srgb, var(--nw-bg) 84%, transparent);
  --nw-blur: blur(6px) saturate(1.2);
  /* Verre d\xE9poli pos\xE9 sur le fond color\xE9 (frise de Weather, \xE9chelle de Confort) : plus clair, plus flou. */
  --nw-glass-clear: color-mix(in srgb, var(--nw-bg) 45%, transparent);
  --nw-frost: blur(14px) saturate(1.6);
  --nw-frame-line: color-mix(in srgb, var(--nw-fg) 16%, transparent);
  --nw-pad-panel: 18px 20px;
  /* Sept tailles de texte, rien d'autre (\xE9chelle C, 3 novembre) : \xE9tiquette 11 \xB7 secondaire 12 \xB7 texte et titre de case 14 \xB7
     titre de carte et de section 17 \xB7 valeur de case 21 \xB7 conseil et valeur vedette 34 \xB7 temp\xE9rature 58. */
  --nw-fs-label: 11px; --nw-fs-small: 12px; --nw-fs-text: 14px; --nw-fs-title: 17px; --nw-fs-case: 21px; --nw-fs-value: 34px; --nw-fs-temp: 58px;
  --nw-label-spacing: .6px;
  /* Couleurs de sens, palette \xAB Aube \xBB (OKLCH, m\xEAme clart\xE9 et m\xEAme saturation). Un th\xE8me peut les remplacer. */
  --nw-rain: var(--hestia-rain-color, oklch(.8 .07 190));
  --nw-wind: var(--hestia-wind-color, oklch(.79 .075 280));
  --nw-heat: var(--hestia-heat-color, oklch(.83 .085 42));
  --nw-cold: var(--hestia-cold-color, oklch(.85 .05 220));
  --nw-calm: var(--hestia-calm-color, oklch(.83 .075 150));
  --nw-pressure: var(--hestia-pressure-color, oklch(.78 .07 315));
  --nw-level1: var(--hestia-level1-color, oklch(.88 .1 96));
  --nw-level2: var(--hestia-level2-color, oklch(.81 .105 64));
  --nw-level3: var(--hestia-level3-color, oklch(.74 .115 18));
  /* Couleurs d'\xE9tat, communes \xE0 toutes les cartes : elles disent s'il y a quelque chose \xE0 FAIRE, pas o\xF9 tombe une mesure.
     Bleu tout va bien \xB7 vert b\xE9n\xE9fice \xE0 saisir ou en cours \xB7 orange geste utile maintenant \xB7 rouge urgent \xB7
     ambre mesure hors de votre plage, sans geste demand\xE9 \xB7 gris (texte secondaire) \xE0 v\xE9rifier.
     La vigilance m\xE9t\xE9o garde sa propre \xE9chelle jaune / orange / rouge (--nw-level1 \xE0 3). */
  --nw-ok: var(--hestia-ok-color, var(--nw-cold));
  --nw-benefit: var(--hestia-benefit-color, var(--nw-calm));
  --nw-act: var(--hestia-act-color, var(--nw-level2));
  --nw-alert: var(--hestia-alert-color, var(--nw-level3));
  --nw-watch: var(--hestia-watch-color, oklch(.84 .13 86));
  /* Part de couleur dans un texte color\xE9 : 34 % reste lisible (contraste 4,5:1). */
  --nw-ink: 34%;
  --nw-ease: cubic-bezier(.2, .8, .2, 1);
  --nw-expand: .45s;
}
button { font:inherit; color:inherit; }
button:focus-visible { outline:2px solid var(--nw-accent); outline-offset:2px; }
.sr { position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap; }
/* \xC9tiquette en petites capitales, une seule taille partout (style Trait, 3 novembre). */
.nw-label { font-size:var(--nw-fs-label); line-height:14px; font-weight:650; letter-spacing:.08em; text-transform:uppercase; color:var(--nw-fg2); white-space:nowrap; }
/* Texte color\xE9 toujours lisible : la couleur de sens m\xE9lang\xE9e au texte. */
.nw-ink { font-size:var(--nw-fs-small); font-weight:600; color:color-mix(in oklab, var(--c) var(--nw-ink), var(--nw-fg)); }
/* Pastille de source : une seule r\xE8gle. */
.nw-badge { display:inline-flex; align-items:center; font-size:var(--nw-fs-small); line-height:18px; font-weight:500; white-space:nowrap; padding:3px 10px;
  border-radius:var(--nw-radius-pill); border:1px solid var(--nw-line); background:color-mix(in srgb, var(--nw-bg) 70%, transparent); color:var(--nw-fg);
  max-width:100%; overflow:hidden; text-overflow:ellipsis; box-sizing:border-box; }
/* Pastille d'info teint\xE9e. */
.nw-chip { display:inline-flex; align-items:center; gap:5px; padding:3px 10px; border-radius:var(--nw-radius-pill); font-size:var(--nw-fs-small); line-height:18px; font-weight:600;
  white-space:nowrap; border:1px solid transparent; background:color-mix(in oklab, var(--c) 24%, transparent); color:color-mix(in oklab, var(--c) var(--nw-ink), var(--nw-fg)); }
.nw-chips { display:flex; flex-wrap:wrap; gap:8px; }
/* ---------- Structure commune des cartes (style Trait, 3 novembre) : la m\xEAme dans Weather, Confort et les prochaines briques. ---------- */
/* La carte : Manrope, angles de 22 px ; la surface teint\xE9e des panneaux. */
ha-card { font-family:Manrope, var(--ha-font-family-body, Roboto), system-ui, sans-serif; line-height:1.5; border-radius:22px;
  --nw-surface:color-mix(in srgb, var(--nw-fg) 3.5%, var(--nw-bg)); }
/* Le titre de la carte (\xAB Synth\xE8se \xBB, le nom de la pi\xE8ce) et la grande temp\xE9rature fine. */
.nw-title { margin:0; font-size:var(--nw-fs-title); line-height:1.25; font-weight:700; letter-spacing:-.02em; }
/* La lecture (3 novembre) : la grande temp\xE9rature, son unit\xE9 en exposant hors du bloc des chiffres, le mini\u2013maxi align\xE9 \xE0 droite
   sur la fin des chiffres (apr\xE8s la virgule, avant \xAB \xB0C \xBB). La m\xEAme dans Weather et Confort (hestia-lecture.ts). */
.nw-reading { display:inline-grid; justify-items:end; padding-right:26px; }
.nw-reading .nw-temp { position:relative; }
.nw-reading .nw-temp sup { position:absolute; left:100%; top:.3em; margin-left:3px; font-size:var(--nw-fs-text); line-height:1; font-weight:500; letter-spacing:0; color:var(--nw-fg2); }
.nw-reading-tap { all:unset; cursor:pointer; border-radius:8px; }
.nw-reading-tap:focus-visible { outline:2px solid var(--nw-accent); outline-offset:2px; }
.nw-reading-more { margin-top:4px; font-size:var(--nw-fs-small); color:var(--nw-fg2); white-space:nowrap; }
.nw-range { margin-top:4px; font-size:var(--nw-fs-small); font-weight:500; color:var(--nw-fg2); font-variant-numeric:tabular-nums; white-space:nowrap; }
/* 58 px au plus, plus petite dans une carte \xE9troite (15 % de sa largeur) : le titre et son \xAB i \xBB gardent leur ligne. */
.nw-temp { font-size:min(var(--nw-fs-temp), 15cqi); font-weight:300; letter-spacing:-.05em; line-height:1; font-variant-numeric:tabular-nums; }
/* Le titre d'une section (\xAB Aujourd'hui \xBB, \xAB Maintenant \xBB) : en clair, son r\xE9sum\xE9 \xE0 c\xF4t\xE9, le chevron rond \xE0 droite s'il se replie. */
.nw-section-head { display:flex; align-items:center; gap:10px; min-width:0; }
.nw-section-head h2 { margin:0; font-size:var(--nw-fs-title); line-height:1.3; font-weight:700; letter-spacing:-.2px; }
.nw-section-head .nw-sum { flex:1; min-width:0; font-size:var(--nw-fs-text); color:var(--nw-fg2); }
/* Le panneau : une surface teint\xE9e, sans contour, arrondie dans l'arrondi de la carte. */
.nw-panel { min-width:0; box-sizing:border-box; padding:14px 16px; border:0; border-radius:16px; background:var(--nw-surface); }
/* Son en-t\xEAte : un pictogramme au trait, le titre et son \xAB i \xBB, un mot ou des onglets \xE0 droite. */
.nw-panel-head { display:flex; flex-wrap:wrap; align-items:center; gap:8px; min-width:0; }
.nw-panel-icon { display:grid; place-items:center; flex:none; color:var(--nw-fg2); }
.nw-panel-icon ha-icon { --mdc-icon-size:18px; display:flex; } .nw-panel-icon svg { width:18px; height:18px; }
.nw-panel-head h3 { display:flex; align-items:center; gap:8px; margin:0; min-width:0; font-size:var(--nw-fs-text); line-height:1.3; font-weight:650; letter-spacing:0; white-space:nowrap; }
.nw-panel-head h3 > span { overflow:hidden; text-overflow:ellipsis; }
.nw-panel-head .aside { margin-left:auto; font-size:var(--nw-fs-small); line-height:1.4; font-weight:500; color:var(--nw-fg2); }
.nw-panel-head .seg { margin-left:auto; }
/* La grande valeur fine et son unit\xE9 ; la phrase grise qui la suit. */
.nw-value { display:flex; align-items:baseline; gap:5px; }
.nw-value b { font-size:var(--nw-fs-value); font-weight:300; letter-spacing:-.04em; line-height:1.1; font-variant-numeric:tabular-nums; }
.nw-value > span, .nw-value b small { font-size:var(--nw-fs-text); line-height:1.1; font-weight:500; letter-spacing:0; color:var(--nw-fg2); }
/* Dans une grille de petites cases (.nw-cases), la valeur passe \xE0 21 demi-gras : la grande valeur fine reste \xE0 la case pleine largeur. */
.nw-cases .nw-value b { font-size:var(--nw-fs-case); font-weight:600; letter-spacing:-.015em; line-height:1.2; }
.nw-say { font-size:var(--nw-fs-small); color:var(--nw-fg2); }
/* Les chiffres sous un panneau : leur nom en petits mots simples, jamais coup\xE9s, la valeur en gras. */
.nw-stats { display:grid; grid-template-columns:repeat(var(--n, 3), minmax(0,1fr)); gap:8px; margin-top:auto; padding-top:10px; border-top:1px solid color-mix(in srgb, var(--nw-fg) 6%, transparent); }
.nw-stats > * { display:flex; flex-direction:column; gap:2px; min-width:0; }
.nw-stats > * > :first-child { font-size:var(--nw-fs-label); line-height:1.35; font-weight:500; letter-spacing:0; text-transform:none; color:var(--nw-fg2); white-space:normal; }
.nw-stats b { font-size:var(--nw-fs-text); line-height:1.35; font-weight:650; font-variant-numeric:tabular-nums; }
/* L\xE9gende : toujours centr\xE9e sous son graphique. */
.nw-legend { display:flex; justify-content:center; flex-wrap:wrap; gap:6px 16px; font-size:var(--nw-fs-small); color:var(--nw-fg2); }
.nw-legend span { display:inline-flex; align-items:center; gap:6px; }
/* Une valeur pos\xE9e sur un graphique. */
.nw-pill { position:absolute; transform:translate(-50%, -130%); font-size:var(--nw-fs-small); font-weight:700; padding:2px 8px; border-radius:var(--nw-radius-pill);
  background:var(--nw-bg); border:1px solid var(--nw-line); box-shadow:0 2px 6px #0001; white-space:nowrap; }
/* Bouton \xAB i \xBB (3 novembre) : un petit disque gris, sans contour ; la lettre est dessin\xE9e ici, la m\xEAme dans toutes les cartes.
   Le bouton reste vide (son aria-label dit ce qu'il explique). */
.nw-info { display:inline-grid; place-items:center; width:18px; height:18px; min-height:0; margin:0; padding:0; flex:none; border-radius:50%; border:0;
  background:color-mix(in srgb, var(--nw-fg) 6%, transparent); color:var(--nw-fg2); cursor:pointer; font:700 var(--nw-fs-label)/1 Manrope, system-ui, sans-serif; }
.nw-info::before { content:'i'; }
.nw-info > * { display:none; }
.nw-info:hover { color:var(--nw-fg); background:color-mix(in srgb, var(--nw-fg) 10%, transparent); }
/* Section repliable : \xE9tiquette, r\xE9sum\xE9, chevron rond (vers le bas repli\xE9, vers le haut ouvert). */
.nw-fold-head { display:flex; align-items:center; gap:10px; width:100%; border:0; background:none; padding:0; cursor:pointer; text-align:left; }
.nw-fold-head .nw-sum { flex:1; min-width:0; font-size:var(--nw-fs-small); color:var(--nw-fg2); }
.nw-chevron { display:grid; place-items:center; width:30px; height:30px; flex:none; border-radius:50%; border:1px solid var(--nw-line); transition:transform var(--nw-expand) var(--nw-ease); }
.nw-fold-head[aria-expanded="true"] .nw-chevron { transform:rotate(180deg); }
/* Survol d'une section : pas de bandeau gris, c'est le chevron qui s'allume et le titre qui se renforce. */
.nw-fold-head:hover { background:none; }
.nw-chevron { transition:transform var(--nw-expand) var(--nw-ease), background .2s, border-color .2s; }
.nw-fold-head:hover .nw-chevron { background:color-mix(in srgb, var(--nw-fg) 8%, transparent); border-color:color-mix(in srgb, var(--nw-fg) 32%, transparent); }
.nw-fold-head:hover .nw-label { color:var(--nw-fg); }
@media (prefers-reduced-motion:reduce) { .nw-chevron { transition:none; } }
/* Cadre de verre d\xE9poli (le fil de Weather, le bandeau de Confort) : verre clair, liser\xE9 net, angles de 16 px, jamais d'ombre.
   Le r\xE9glage \xAB Effet de verre \xBB d\xE9coch\xE9 (:host([flat])) le rend opaque et sans flou. */
.nw-glass { background:var(--nw-glass-clear); backdrop-filter:var(--nw-frost); -webkit-backdrop-filter:var(--nw-frost);
  border:1px solid var(--nw-frame-line, color-mix(in srgb, var(--nw-fg) 16%, transparent)); border-radius:16px; box-shadow:none; }
/* Le m\xEAme cadre, plus opaque, quand il porte les chiffres cl\xE9s sur un ciel clair (\xAB En ce moment \xBB) : ils restent lisibles. */
.nw-glass.nw-glass-solid { background:color-mix(in srgb, var(--nw-bg) 68%, transparent); }
:host([flat]) { --nw-blur:none; --nw-frost:none; --nw-glass-clear:var(--nw-bg); --nw-glass-strong:var(--nw-bg); }

/* ---------- Le bandeau (5 novembre, carte \xAB Mon logement \xBB) : le geste du moment, le m\xEAme dans toutes les cartes. ----------
   Le cadre (.nw-band, pos\xE9 avec .nw-glass) prend la couleur de son \xE9tat par data-level ; dedans, une rang\xE9e (.nw-band-row) :
   la sc\xE8ne ou le pictogramme \xE0 gauche (.nw-band-pic), puis le texte (.nw-band-text) : au-dessus, la pi\xE8ce ou le moment
   (.nw-band-kicker) ; le geste en 34 (.nw-band-title), color\xE9 quand il y a un geste \xE0 faire ; pourquoi (.nw-band-line) ;
   une note grise (.nw-band-note : \xAB Puis refermez \xBB, la preuve). Plusieurs conseils : des barres en bas du cadre (.nw-band-bars). */
.nw-band { --c:var(--nw-ok); position:relative; box-sizing:border-box; min-width:0; padding:16px; }
.nw-band[data-level="benefit"] { --c:var(--nw-benefit); } .nw-band[data-level="action"] { --c:var(--nw-act); } .nw-band[data-level="urgent"] { --c:var(--nw-alert); }
.nw-band[data-level="neutral"] { --c:color-mix(in srgb, var(--nw-fg) 25%, transparent); }
.nw-band:has(.nw-band-bars) { padding-bottom:26px; }
.nw-band-row { display:flex; align-items:center; gap:16px; min-width:0; }
.nw-band-pic { display:grid; place-items:center; flex:none; order:-1; }
/* Sans sc\xE8ne (mesures en chargement, capteurs muets) : le pictogramme dans un carr\xE9 teint\xE9. */
.nw-band-pic.box { width:60px; height:72px; border-radius:10px; background:color-mix(in srgb, var(--c) 34%, transparent); color:var(--nw-fg); }
.nw-band-pic.box svg, .nw-band-pic.box ha-icon { width:34px; height:34px; --mdc-icon-size:34px; }
.nw-band-text { flex:1; min-width:0; }
.nw-band-text p { margin:0; }
.nw-band-kicker { display:flex; align-items:center; flex-wrap:wrap; gap:4px 8px; margin-bottom:4px; font-size:var(--nw-fs-label); line-height:14px; font-weight:650;
  letter-spacing:.08em; text-transform:uppercase; color:var(--nw-fg); }
.nw-band-kicker i { font-style:normal; font-weight:600; letter-spacing:0; text-transform:none; color:var(--nw-fg2); }
.nw-band-title { font-size:var(--nw-fs-value); font-weight:650; letter-spacing:-.03em; line-height:1.1; text-wrap:balance; }
/* Color\xE9 pour un geste seulement : un \xAB Rien \xE0 faire \xBB qui garde quelque chose \xAB \xE0 saisir \xBB ne s'\xE9crit jamais en vert (5 novembre). */
.nw-band:is([data-level="action"], [data-level="urgent"]) .nw-band-title { color:color-mix(in oklab, var(--c) 45%, var(--nw-fg)); }
.nw-band-line { margin-top:6px !important; font-size:var(--nw-fs-text); line-height:1.5; color:var(--nw-fg2); }
.nw-band-line b { color:var(--nw-fg); font-weight:650; }
.nw-band-note { display:flex; align-items:center; gap:6px; margin-top:6px !important; font-size:var(--nw-fs-small); color:var(--nw-fg2); }
.nw-band-note svg, .nw-band-note ha-icon { width:13px; height:13px; flex:none; --mdc-icon-size:13px; }
.nw-band-bars { position:absolute; left:16px; right:16px; bottom:6px; display:flex; gap:6px; }
.nw-band-bars button { flex:1; min-height:0; margin:0; padding:6px 0; border:0; background:none; cursor:pointer; }
.nw-band-bars span { display:block; height:3px; border-radius:2px; background:color-mix(in srgb, var(--nw-fg) 16%, transparent); }
.nw-band-bars button[aria-current="true"] span { background:color-mix(in oklab, var(--c) 70%, var(--nw-fg)); }

/* ---------- Le petit rond de valeur (3 novembre) : la valeur sur une piste (\xE9chelles) et la bulle affich\xE9e du fil. ---------- */
.nw-dot { position:absolute; z-index:3; width:8px; height:8px; margin-left:-4px; border-radius:50%; background:var(--nw-fg); box-shadow:0 0 0 1.5px var(--nw-bg); }
.nw-dot::after { content:''; position:absolute; inset:-2px; border-radius:50%; border:1.5px solid var(--nw-fg);
  animation:nw-ripple 2.4s var(--nw-ease) infinite; animation-play-state:var(--nw-motion, running); }
@keyframes nw-ripple { from { transform:scale(.6); opacity:.9; } to { transform:scale(2.2); opacity:0; } }

/* ---------- L'\xE9chelle fa\xE7on fil (3 novembre, maquettes/planche-echelles.html) : Ressenti de Weather, temp\xE9rature de Confort. ----------
   Une piste en relief d\xE9coup\xE9e en tron\xE7ons nomm\xE9s ; la valeur dans une bulle teint\xE9e de son tron\xE7on (--tone), un trait fin jusqu'\xE0 la piste,
   le petit rond sur la piste ; les rep\xE8res dessous (ligne basse) ou dessus (ligne haute) ; le min\u2013max en fin trait ; un rep\xE8re creux (dehors). */
.nw-scale { position:relative; height:84px; margin:0 6px; }
.nw-scale-lane { position:absolute; left:0; right:0; top:44px; height:18px; display:flex; gap:3px; }
.nw-scale-part { display:grid; place-items:center; min-width:0; overflow:hidden; border-radius:6px; font-style:normal; transform-origin:left; container-type:inline-size;
  background:linear-gradient(180deg, color-mix(in oklab, var(--tone) 85%, #fff), color-mix(in oklab, var(--tone) 78%, transparent));
  box-shadow:inset 0 1px 0 rgb(255 255 255 / .35), inset 0 -1px 0 rgb(0 0 0 / .08); animation:nw-grow .52s var(--nw-ease) both; animation-delay:calc(var(--n, 0) * 90ms); }
.nw-scale-part:first-child { border-radius:9px 6px 6px 9px; } .nw-scale-part:last-child { border-radius:6px 9px 9px 6px; } .nw-scale-part:only-child { border-radius:9px; }
.nw-scale-part span { font-size:var(--nw-fs-label); line-height:1; font-weight:700; letter-spacing:.02em; color:rgb(20 26 45 / .72); white-space:nowrap; }
@container (max-width:62px) { .nw-scale-part span { display:none; } }
.nw-scale-part.wl { place-items:center start; padding-left:10px; } .nw-scale-part.wr { place-items:center end; padding-right:10px; }
@keyframes nw-grow { from { transform:scaleX(0); } }
/* La bulle peut \xEAtre un bouton (un appui ouvre le d\xE9tail) : la r\xE8gle passe devant celles des boutons d'une brique.
   Son fond prend 40 % de la teinte au plus : le texte garde un contraste de 4,5 en th\xE8me sombre, quelle que soit la teinte. */
.nw-scale .nw-scale-pin { --tx:-50%; position:absolute; min-height:0; margin:0; font-family:inherit; top:8px; z-index:2; display:inline-flex; align-items:center; padding:3px 9px; border:0; border-radius:var(--nw-radius-pill);
  white-space:nowrap; font-size:var(--nw-fs-small); font-weight:700; line-height:18px; font-variant-numeric:tabular-nums; color:var(--nw-fg); transform:translateX(var(--tx)) translateY(-2px) scale(1.04);
  background:color-mix(in oklab, var(--tone) 40%, var(--nw-bg)); box-shadow:0 0 0 1px var(--nw-line), 0 4px 10px -4px rgb(0 0 0 / .35); animation:nw-pop .3s var(--nw-ease) .2s both; }
.nw-scale .nw-scale-pin.edge-l { --tx:-14px; } .nw-scale .nw-scale-pin.edge-r { --tx:calc(-100% + 14px); }
@keyframes nw-pop { from { opacity:0; transform:translateX(var(--tx)) translateY(6px) scale(.92); } }
.nw-scale-stem { position:absolute; top:31px; z-index:1; width:1.5px; height:13px; margin-left:-.75px; background:color-mix(in oklab, var(--tone) 70%, var(--nw-fg)); }
.nw-scale .nw-dot { top:49px; }
.nw-scale-span { position:absolute; top:37px; height:3px; border-radius:2px; background:color-mix(in srgb, var(--nw-fg) 45%, transparent); }
.nw-scale-span::before, .nw-scale-span::after { content:''; position:absolute; top:-2px; width:1.5px; height:7px; border-radius:1px; background:inherit; }
.nw-scale-span::before { left:0; } .nw-scale-span::after { right:0; }
/* La temp\xE9rature r\xE9elle \xE0 c\xF4t\xE9 du ressenti (Weather) ou dehors (Confort) : un trait fin en travers de l'\xE9chelle (3 novembre, \xAB partout sur le trait \xBB). */
.nw-scale .nw-scale-mk { position:absolute; top:40px; z-index:2; width:2px; height:26px; min-height:0; margin:0 0 0 -1px; padding:0; box-sizing:border-box; border:0; border-radius:1px;
  background:color-mix(in srgb, var(--nw-fg) 85%, transparent); box-shadow:0 0 0 1px color-mix(in srgb, var(--nw-bg) 60%, transparent); }
/* Le doigt le trouve : la zone d'appui est plus large que le trait. */
button.nw-scale-mk::before { content:''; position:absolute; inset:-6px -10px; }
.nw-scale-lb { position:absolute; top:66px; translate:-50% 0; font-size:var(--nw-fs-label); line-height:16px; color:var(--nw-fg2); white-space:nowrap; font-variant-numeric:tabular-nums; }
.nw-scale-lb.up { top:22px; } .nw-scale-lb.first { translate:0 0; } .nw-scale-lb.last { translate:-100% 0; } .nw-scale-lb b { color:var(--nw-fg); font-weight:650; }
@media (prefers-reduced-motion:reduce) { .nw-scale-part, .nw-scale-pin, .nw-dot::after { animation:none; } }
/* La frise compacte (4 novembre, maquettes/planche-ressenti-condense.html, variante D) : la m\xEAme piste et ses mots, une bulle plus petite,
   sans ligne de rep\xE8res ; la plage et le dehors se disent ailleurs. Le Ressenti de la carte compl\xE8te de Confort. */
.nw-scale.compact { height:46px; margin:0 2px; }
.nw-scale.compact .nw-scale-lane { top:26px; height:16px; }
.nw-scale.compact .nw-scale-pin { top:0; padding:0 7px; font-size:var(--nw-fs-label); line-height:16px; transform:translateX(var(--tx)); box-shadow:0 0 0 1px var(--nw-line); }
.nw-scale.compact .nw-scale-stem { top:16px; height:10px; }
.nw-scale.compact .nw-dot { top:30px; }

/* ---------- Fl\xE8ches et chevrons (3 novembre, maquettes/planche-fleches.html) : un seul dessin au trait, pos\xE9 par la charte. ----------
   La tendance (.nw-trend) ne s'affiche que si la mesure monte ou baisse vraiment ; \xAB stable \xBB garde sa place sans rien montrer.
   Sa couleur : vert, elle revient vers votre plage ; orange, elle s'en \xE9loigne ; gris sinon. Elle glisse d'un cran en apparaissant, jamais en boucle.
   Le vent prend la m\xEAme fl\xE8che, tourn\xE9e vers o\xF9 il va (--r). Le chevron (.nw-chev) ouvre et replie ; il tourne d'un quart en s'ouvrant. */
.nw-trend, .nw-chev { display:inline-block; flex:none; background:currentColor; vertical-align:-1px; transform:rotate(var(--r, 0deg));
  -webkit-mask:var(--nw-glyph) center / contain no-repeat; mask:var(--nw-glyph) center / contain no-repeat; }
.nw-trend { width:12px; height:12px; color:var(--nw-fg2);
  --nw-glyph:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 10.5V1.8M2.4 5.2 6 1.6l3.6 3.6'/%3E%3C/svg%3E");
  animation:nw-nudge .5s var(--nw-ease) both; }
.nw-trend[data-way="down"] { --r:180deg; }
.nw-trend[data-way="stable"] { visibility:hidden; animation:none; }
/* Apr\xE8s une grande valeur, \xAB stable \xBB ne laisse pas m\xEAme de place ; dans une liste, il la garde pour l'alignement. */
.nw-value .nw-trend[data-way="stable"] { display:none; }
.nw-trend[data-tone="better"] { color:color-mix(in oklab, var(--nw-calm) 75%, var(--nw-fg)); }
.nw-trend[data-tone="worse"] { color:color-mix(in oklab, var(--nw-level2) 80%, var(--nw-fg)); }
@keyframes nw-nudge { from { opacity:0; translate:0 3px; } }
.nw-trend[data-way="down"] { animation-name:nw-nudge-down; } @keyframes nw-nudge-down { from { opacity:0; translate:0 -3px; } }
.nw-chev { width:14px; height:14px; color:var(--nw-fg2); transition:transform .22s var(--nw-ease);
  --nw-glyph:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 6l6 6-6 6'/%3E%3C/svg%3E"); }
.nw-chev.open, [aria-expanded="true"] > .nw-chev, details[open] > summary .nw-chev { --r:90deg; }
/* Le vent : la m\xEAme fl\xE8che, tourn\xE9e vers o\xF9 il va, \xE0 sa couleur, sans entr\xE9e anim\xE9e. */
.nw-trend.wind { width:10px; height:10px; color:color-mix(in oklab, var(--nw-wind) 70%, var(--nw-fg)); animation:none; }
/* Une fl\xE8che suivie de mots ou d'un chiffre gris (\xAB +4,4 \xB0C/h \xBB, \xAB s'approchent \xBB) : sur une ligne, un petit \xE9cart. */
.nw-say:has(> .nw-trend) { display:inline-flex; align-items:center; gap:5px; }
/* Dans le bouton rond d'une section, le chevron pointe vers le bas ; c'est le bouton qui tourne en s'ouvrant. */
.nw-chevron .nw-chev { --r:90deg; }
@media (prefers-reduced-motion:reduce) { .nw-trend { animation:none; } .nw-chev { transition:none; } }


/* ---------- Le Ressenti (3 novembre, maquettes/maquette-ressenti-piece.html) : celui de Weather dehors, celui d'une pi\xE8ce de Confort. ----------
   La valeur et son mot, l'\xE9chelle, puis ce qui joue en cases d\xE9limit\xE9es : leur titre, leur effet en un mot teint\xE9, la valeur, une note.
   Quatre cases par ligne dans une carte large, ou --nw-ff-cols. */
.nw-feel-row { display:flex; align-items:baseline; flex-wrap:wrap; gap:4px 12px; }
.nw-feel-word { font-size:var(--nw-fs-text); font-weight:650; }
.nw-feel-say { font-size:var(--nw-fs-small); color:var(--nw-fg2); }
.nw-feel-ends { display:flex; justify-content:space-between; margin:2px 6px 0; font-size:var(--nw-fs-label); color:var(--nw-fg2); font-variant-numeric:tabular-nums; }
.nw-feel-factors { display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:8px; }
@container (min-width:600px) { .nw-feel-factors { grid-template-columns:repeat(var(--nw-ff-cols, 4), minmax(0,1fr)); } }
.nw-feel-factors > * { container-type:inline-size; display:grid; gap:2px; align-content:start; padding:10px 12px; border-radius:12px; min-width:0;
  background:var(--nw-bg); border:1px solid color-mix(in srgb, var(--nw-fg) 14%, transparent); }
.nw-ff-head { display:flex; justify-content:space-between; align-items:center; gap:6px; font-size:var(--nw-fs-small); color:var(--nw-fg2); min-width:0; }
.nw-ff-t { display:flex; align-items:center; gap:6px; min-width:0; line-height:1.3; }
.nw-ff-t ha-icon, .nw-ff-t svg { flex:none; } .nw-ff-head ha-icon { --mdc-icon-size:15px; } .nw-ff-t svg { width:15px; height:15px; }
/* Une case \xE9troite : l'effet sous le titre, dans toutes les cases pareil. */
@container (max-width:150px) { .nw-ff-head { flex-direction:column; align-items:flex-start; gap:4px; } }
.nw-ff-eff { flex:none; padding:0 6px; border-radius:var(--nw-radius-pill); font-size:var(--nw-fs-label); font-weight:700; white-space:nowrap;
  background:color-mix(in oklab, var(--c) 28%, transparent); color:color-mix(in oklab, var(--c) 40%, var(--nw-fg)); }
.nw-feel-factors b { font-size:var(--nw-fs-title); font-weight:500; letter-spacing:-.02em; font-variant-numeric:tabular-nums; }
.nw-feel-factors small { font-size:var(--nw-fs-small); color:var(--nw-fg2); }
.nw-feel-why { padding:10px 12px; border-radius:12px; background:var(--nw-bg); border:1px solid var(--nw-line); font-size:var(--nw-fs-text); }
.nw-feel-why p { margin:4px 0; } .nw-feel-why .ex { color:var(--nw-fg2); }
`;var qn=`/* Hestia \xC9nergie : seulement ses exceptions. Toute la structure (carte, bandeau, panneaux, sections, \xE9tiquettes) vient de
   hestia-charte.css. Ici, d'apr\xE8s la maquette des cartes 2 (docs/maquette-cartes-2.html, valid\xE9e le 8 nov. 2026), a\xE9r\xE9e
   le 17 nov. comme les cartes Hestia Weather (maquette des cartes 4) : le chiffre en grand, les mots en petit, de l'espace.
   Couleurs de sens propres \xE0 l'\xE9nergie, prises dans la palette Aube : jamais d'autres. */
:host { --nw-sun:var(--nw-level1); --nw-grid:var(--nw-wind); --nw-home:var(--nw-heat); --nw-water:var(--nw-rain); display:block; }
ha-card { display:flex; flex-direction:column; gap:16px; padding:18px 20px 20px; background:var(--nw-bg); color:var(--nw-fg); container-type:inline-size; box-sizing:border-box; }
.ico { display:grid; place-items:center; width:30px; height:30px; flex:none; border-radius:9px; background:color-mix(in oklab, var(--c) 30%, transparent); color:color-mix(in oklab, var(--c) 55%, var(--nw-fg)); }
.ico svg { width:17px; height:17px; }

/* L'en-t\xEAte, le m\xEAme pour toutes les cartes (comme le titre d'une carte Weather) : le sujet en titre, sa p\xE9riode en gris \xE0 c\xF4t\xE9 ;
   puis le chiffre en grand et ses mots en petit (comme la temp\xE9rature de Weather) ; puis pourquoi, en gris. */
.ans-k { display:flex; align-items:center; gap:10px; min-width:0; }
.ans-k .nw-title { white-space:nowrap; }
.ans-k .per { flex:1; min-width:0; font-size:var(--nw-fs-small); color:var(--nw-fg2); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.ans-k .pastille { margin-left:0; }
.ans { display:flex; flex-direction:column; gap:6px; }
.hero { display:flex; align-items:baseline; flex-wrap:wrap; gap:2px 10px; margin:0; }
.hero b { font-size:var(--nw-fs-value); font-weight:300; letter-spacing:-.04em; line-height:1.05; font-variant-numeric:tabular-nums; white-space:nowrap; }
.hero b small { margin-left:4px; font-size:var(--nw-fs-text); font-weight:500; letter-spacing:0; color:var(--nw-fg2); }
.hero > span { font-size:var(--nw-fs-text); color:var(--nw-fg2); }
.hero > span b { font-size:inherit; font-weight:650; letter-spacing:0; color:var(--nw-fg); }
.ans-m { margin:0; font-size:var(--nw-fs-title); font-weight:650; line-height:1.3; }
.ans-w { margin:0; font-size:var(--nw-fs-text); line-height:1.5; color:var(--nw-fg2); text-wrap:pretty; max-width:62ch; }
.ans-w b { color:var(--nw-fg); font-weight:650; }

/* Les encarts : un titre en mots simples, une phrase avec un chiffre, puis le dessin. */
.encs { display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:12px; }
.encs > .wide { grid-column:1 / -1; }
.nw-panel { display:flex; flex-direction:column; gap:12px; }
.nw-panel-head h3 { font-size:var(--nw-fs-text); }
/* La phrase d'un encart : petite et grise, son chiffre en gras (comme les notes des panneaux de Weather). */
.say { margin:0; font-size:var(--nw-fs-small); line-height:1.5; color:var(--nw-fg2); text-wrap:pretty; }
.say b { font-weight:650; color:var(--nw-fg); }
.foot { font-size:var(--nw-fs-small); color:var(--nw-fg2); border-top:1px solid var(--nw-line-soft); padding-top:8px; }
.foot b { color:var(--nw-fg); font-weight:650; }

/* Barres couch\xE9es : un nom, une barre, une valeur (comme le bilan fait main). */
.hb { display:grid; grid-template-columns:minmax(84px, max-content) 1fr auto; gap:10px 12px; align-items:center; font-size:var(--nw-fs-text); }
.hb.list { grid-template-columns:1fr auto; }
.hb .n { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:flex; align-items:center; gap:6px; min-width:0; }
.hb .n > span:first-child { overflow:hidden; text-overflow:ellipsis; }
.hb .n.muted, .hb .v.muted { color:var(--nw-fg2); }
.hb .t { height:8px; border-radius:4px; background:color-mix(in srgb, var(--nw-fg) 7%, transparent); overflow:hidden; }
.hb .t i { display:block; height:100%; border-radius:4px; background:var(--c, var(--nw-home)); }
.hb .t i.soft { opacity:.45; }
.hb .t.dash i { background:repeating-linear-gradient(90deg, color-mix(in srgb, var(--nw-fg) 28%, transparent) 0 6px, transparent 6px 9px); }
.hb .v { text-align:right; font-weight:650; font-variant-numeric:tabular-nums; white-space:nowrap; }
.hb .v small { font-weight:500; color:var(--nw-fg2); margin-left:6px; }
.live { display:inline-flex; align-items:center; gap:5px; font-size:var(--nw-fs-label); font-weight:650; color:var(--nw-fg2); white-space:nowrap; }
.live::before { content:''; width:7px; height:7px; border-radius:50%; background:var(--nw-fg); animation:pulse 1.8s var(--nw-ease) infinite; }
@keyframes pulse { 50% { opacity:.25; } }

/* Barres debout : heures, jours, nuits. En CSS, pour garder un texte lisible \xE0 toutes les largeurs. */
.cols { position:relative; display:flex; align-items:flex-end; gap:2px; height:96px; padding-top:18px; }
.cols.tall { height:120px; }
.cols .c { position:relative; flex:1; height:100%; display:flex; align-items:flex-end; border-radius:4px; }
.cols .c.band { background:color-mix(in oklab, var(--nw-cold) 22%, transparent); }
.cols .c i { display:block; width:100%; min-height:2px; border-radius:3px 3px 1px 1px; background:var(--c); }
.cols .c i.part { opacity:.4; }
.cols .c i.none { background:color-mix(in srgb, var(--nw-fg) 10%, transparent); }
.cols .c .pin { position:absolute; left:50%; transform:translate(-50%, -4px); font-size:var(--nw-fs-small); font-weight:700; padding:1px 7px; border-radius:999px;
  background:var(--nw-bg); border:1px solid var(--nw-line); white-space:nowrap; z-index:2; font-variant-numeric:tabular-nums; }
.cols .c .pin.l { left:0; transform:translate(0, -4px); } .cols .c .pin.r { left:auto; right:0; transform:translate(0, -4px); }
.cols .limit { position:absolute; left:0; right:0; border-top:2px dashed color-mix(in oklab, var(--nw-act) 70%, var(--nw-fg)); z-index:1; }
.cols .limit span { position:absolute; right:0; top:-20px; font-size:var(--nw-fs-small); font-weight:650; color:var(--nw-fg2); background:var(--nw-bg); padding:0 4px; }
.ticks { display:flex; justify-content:space-between; font-size:var(--nw-fs-small); color:var(--nw-fg2); margin-top:4px; font-variant-numeric:tabular-nums; }
.ticks.days span { flex:1; text-align:center; white-space:nowrap; }
.nw-legend i { width:9px; height:9px; border-radius:3px; background:var(--c); flex:none; display:inline-block; }

/* Une barre partag\xE9e : deux parts d'un tout, chacune nomm\xE9e. */
.split { display:flex; height:12px; border-radius:6px; overflow:hidden; gap:2px; }
.split i { display:block; height:100%; background:var(--c); }
.split-l { display:flex; justify-content:space-between; gap:10px; font-size:var(--nw-fs-small); color:var(--nw-fg2); margin-top:6px; }
.split-l b { color:var(--nw-fg); font-weight:650; }

/* La journ\xE9e sur 24 h : heures creuses et pleines, et l'heure qu'il est. */
.day { position:relative; height:26px; border-radius:8px; background:color-mix(in oklab, var(--nw-heat) 34%, transparent); overflow:hidden; }
.day i { position:absolute; top:0; bottom:0; background:var(--nw-cold); }
.day .now { position:absolute; top:0; bottom:0; width:2px; background:var(--nw-fg); }

/* Une piste : une part d'un total, un rep\xE8re. */
.track { position:relative; height:10px; border-radius:5px; background:color-mix(in srgb, var(--nw-fg) 7%, transparent); }
.track i { position:absolute; left:0; top:0; bottom:0; border-radius:5px; background:var(--c); }
.track .mark { position:absolute; top:-5px; bottom:-5px; width:2px; background:var(--nw-fg2); }
.track-l { display:flex; justify-content:space-between; gap:8px; margin-top:6px; font-size:var(--nw-fs-small); color:var(--nw-fg2); }
.track-l b { color:var(--nw-fg); font-weight:650; }

/* La pastille d'\xE9tat (tuile, eau, pointe). */
.pastille { margin-left:auto; display:inline-flex; align-items:center; gap:6px; font-size:var(--nw-fs-small); font-weight:650; color:color-mix(in oklab, var(--c) var(--nw-ink), var(--nw-fg)); white-space:nowrap; }
.pastille::before { content:''; width:8px; height:8px; border-radius:50%; background:var(--c); box-shadow:0 0 0 3px color-mix(in oklab, var(--c) 30%, transparent); }

/* La tuile. */
ha-card.tile { gap:12px; }

/* La carte compl\xE8te : ses sections, une p\xE9riode chacune, \xE9crite dans le titre. */
.head { display:flex; align-items:baseline; gap:10px; min-width:0; }
.head .nw-title { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.head .when { margin-left:auto; font-size:var(--nw-fs-small); color:var(--nw-fg2); white-space:nowrap; }
.sec { border-top:1px solid var(--nw-line-soft); padding-top:16px; display:flex; flex-direction:column; gap:12px; min-width:0; }
/* Sur un grand \xE9cran, les trois p\xE9riodes c\xF4te \xE0 c\xF4te, chacune dans son panneau. */
.periods { display:flex; flex-direction:column; gap:16px; }
@container (min-width:680px) {
 .periods { display:grid; grid-template-columns:1.25fr 1fr 1fr; gap:12px; align-items:stretch; }
 .periods.two { grid-template-columns:1fr 1fr; }
 .periods .sec { border-top:0; padding:16px 18px; border-radius:16px; background:var(--nw-surface); }
 .periods .nw-fold-head .nw-chevron { display:none; } .periods .nw-fold-head { cursor:default; pointer-events:none; }
 .more { grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); }
 .pistes { grid-template-columns:repeat(auto-fill, minmax(340px, 1fr)); }
}
.lines { display:grid; gap:8px; }
.line { display:flex; gap:10px; align-items:flex-start; font-size:var(--nw-fs-text); line-height:1.5; }
.line .ico { width:26px; height:26px; border-radius:8px; } .line .ico svg { width:15px; height:15px; }
.line b { font-weight:650; }
/* \xAB En ce moment \xBB (le mod\xE8le de Frank, 20 nov. 2026) : un halo par c\xF4t\xE9, des bulles qui grossissent au milieu du trait. */
:host { --nw-prod:color-mix(in oklab, var(--nw-level1) 45%, var(--nw-level2)); }
.flow2 { position:relative; display:grid; grid-template-columns:auto minmax(0,1fr) auto minmax(0,1fr) auto; align-items:start; gap:0 6px; padding:18px 12px 14px; border-radius:16px; isolation:isolate;
 background:
  radial-gradient(60% 120% at 0% 30%, color-mix(in oklab, var(--nw-prod) calc(var(--sunA) * 42%), transparent), transparent 70%),
  radial-gradient(60% 120% at 100% 30%, color-mix(in oklab, var(--tone) calc(var(--gridA) * 42%), transparent), transparent 70%),
  radial-gradient(40% 80% at 50% 25%, color-mix(in oklab, var(--tone) 10%, transparent), transparent 70%); }
.flow2.two { grid-template-columns:auto minmax(0,1fr) auto; justify-content:center; }
.fnode { display:flex; flex-direction:column; align-items:center; gap:2px; text-align:center; min-width:64px; }
@container (max-width:420px) { .fdot { width:44px; height:44px; } .fdot svg { width:20px; height:20px; } .fl { font-size:11px; } .fv { font-size:14.5px; } .flow2 { padding:14px 6px 12px; gap:0 2px; } .fnode { min-width:58px; } }
.fdot { width:52px; height:52px; border-radius:50%; display:grid; place-items:center; margin-bottom:6px;
 background:color-mix(in oklab, var(--c) 26%, var(--nw-bg)); border:1.5px solid color-mix(in oklab, var(--c) 60%, transparent);
 box-shadow:0 0 22px color-mix(in oklab, var(--c) 38%, transparent), inset 0 0 12px color-mix(in oklab, var(--c) 18%, transparent); }
.fdot svg { width:24px; height:24px; color:color-mix(in oklab, var(--c) 70%, var(--nw-fg)); }
.fl { font-size:var(--nw-fs-small); color:var(--nw-fg2); font-weight:600; white-space:nowrap; }
.fv { font-size:16px; font-weight:750; color:color-mix(in oklab, var(--c) 75%, var(--nw-fg)); font-variant-numeric:tabular-nums; white-space:nowrap; }
.fnode.dim .fdot { box-shadow:none; opacity:.55; } .fnode.dim .fv { color:var(--nw-fg2); }
.fmid { display:flex; flex-direction:column; align-items:center; }
.fwater { display:flex; flex-direction:column; align-items:center; }
.fstem { width:2px; height:18px; margin:4px 0; border-radius:1px; background:color-mix(in oklab, var(--nw-water) 35%, transparent); }
.flink { display:flex; flex-direction:column; align-items:stretch; gap:4px; min-width:0; }
.fsay { min-height:28px; font-size:11px; line-height:1.25; color:color-mix(in oklab, var(--c) 75%, var(--nw-fg)); text-align:center; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; white-space:nowrap; }
.fsay b { font-weight:750; } .fsay span { font-weight:600; opacity:.85; }
.fline { position:relative; height:2px; margin-top:4px; border-radius:1px; background:color-mix(in oklab, var(--c) 28%, transparent); }
.flink.off .fline { background:color-mix(in srgb, var(--nw-fg) 9%, transparent); }
.fline i { position:absolute; top:50%; left:0; width:8px; height:8px; border-radius:50%; background:var(--c); box-shadow:0 0 10px var(--c);
 animation:bubble var(--dur) linear infinite; }
.fline i:nth-child(2) { animation-delay:calc(var(--dur) / -3); } .fline i:nth-child(3) { animation-delay:calc(var(--dur) / -1.5); }
.flink.back .fline i { animation-direction:reverse; }
@keyframes bubble {
 0% { left:0; transform:translate(-50%, -50%) scale(.45); opacity:0; }
 15% { opacity:.6; }
 50% { left:50%; transform:translate(-50%, -50%) scale(1.7); opacity:1; }
 85% { opacity:.6; }
 100% { left:100%; transform:translate(-50%, -50%) scale(.45); opacity:0; } }
@media (prefers-reduced-motion:reduce) { .fline i { animation:none; left:50%; transform:translate(-50%, -50%) scale(1.3); } .fline i + i { display:none; } }
.chips { display:flex; flex-wrap:wrap; gap:6px; align-items:center; }
.chips .nw-label { margin-right:2px; }
.chip { display:inline-flex; gap:6px; align-items:baseline; padding:3px 10px; border-radius:999px; background:var(--nw-surface); font-size:var(--nw-fs-small); white-space:nowrap; }
.chip b { font-weight:650; font-variant-numeric:tabular-nums; }
.big { display:flex; align-items:baseline; gap:8px; flex-wrap:wrap; }
.big b { font-size:var(--nw-fs-value); font-weight:300; letter-spacing:-.04em; line-height:1; font-variant-numeric:tabular-nums; }
.big span { font-size:var(--nw-fs-text); color:var(--nw-fg2); font-weight:500; }
/* \xAB En d\xE9tail \xBB : chaque encart touchable dit son sujet ET sa p\xE9riode. */
.more { display:grid; grid-template-columns:repeat(auto-fill, minmax(140px, 1fr)); gap:10px; }
.go { all:unset; box-sizing:border-box; display:flex; flex-direction:column; gap:6px; padding:14px 16px; border-radius:var(--nw-radius); cursor:pointer;
  background:linear-gradient(160deg, color-mix(in oklab, var(--c) 16%, var(--nw-bg)), var(--nw-surface) 75%); border:1px solid var(--nw-line-soft); min-width:0; }
.go:hover { border-color:color-mix(in oklab, var(--c) 70%, var(--nw-line)); }
.go:focus-visible { outline:2px solid var(--nw-accent); outline-offset:2px; }
.go .g-h { display:flex; align-items:center; gap:10px; }
.go .g-t { display:flex; flex-direction:column; min-width:0; font-size:var(--nw-fs-text); font-weight:650; line-height:1.25; }
.go .g-t small { font-size:var(--nw-fs-small); font-weight:500; color:var(--nw-fg2); } .go .g-h .ar { margin-left:auto; color:var(--nw-fg2); font-size:18px; line-height:1; }
.go .ico { width:26px; height:26px; border-radius:8px; } .go .ico svg { width:15px; height:15px; }
.go .g-v { font-size:var(--nw-fs-case); font-weight:600; letter-spacing:-.015em; line-height:1.2; font-variant-numeric:tabular-nums; }
.go .g-v small { font-size:var(--nw-fs-small); font-weight:500; color:var(--nw-fg2); margin-left:4px; letter-spacing:0; }
.go .g-s { font-size:var(--nw-fs-small); color:var(--nw-fg2); }

/* La carte de d\xE9tail ouverte depuis la carte compl\xE8te, par-dessus la page. */
.ov { position:fixed; inset:0; z-index:10; display:flex; justify-content:center; align-items:flex-start; padding:24px 12px; background:color-mix(in srgb, #000 45%, transparent); overflow:auto; }
.ov .sheet { width:min(860px, 100%); animation:up .3s var(--nw-ease); }
@keyframes up { from { transform:translateY(16px); } to { transform:none; } }
.d-close { all:unset; box-sizing:border-box; display:grid; place-items:center; flex:none; width:32px; height:32px; border-radius:50%; border:1px solid var(--nw-line); cursor:pointer; font-size:18px; line-height:1; color:var(--nw-fg2); }
.d-close:focus-visible { outline:2px solid var(--nw-accent); outline-offset:2px; }
.ans-k .d-close { margin-left:4px; }
.empty { font-size:var(--nw-fs-small); color:var(--nw-fg2); }
@media (prefers-reduced-motion:reduce) { .live::before, .ov .sheet { animation:none !important; } }

/* The link to the hub under an answer: what is only supposed, to confirm in R\xE9glages (palier 0). */
.to-hub{color:var(--nw-ok);text-decoration:none;white-space:nowrap}.to-hub:hover{text-decoration:underline}

/* \xAB Pour \xE9conomiser \xBB (maquette des cartes 3): the advice \xAB \xE0 froid \xBB, one line each, the gesture and what it brings. */
.pistes { display:grid; gap:10px; }
.piste { all:unset; box-sizing:border-box; display:grid; grid-template-columns:auto 1fr auto; gap:2px 10px; align-items:center; padding:12px 14px; border-radius:var(--nw-radius);
  background:var(--nw-surface); min-width:0; }
button.piste { cursor:pointer; } button.piste:hover { box-shadow:inset 0 0 0 1px color-mix(in oklab, var(--c) 60%, var(--nw-line)); }
button.piste:focus-visible { outline:2px solid var(--nw-accent); outline-offset:2px; }
.piste .ico { grid-row:1 / span 2; }
.piste .pt { font-size:var(--nw-fs-text); font-weight:650; line-height:1.35; }
.piste .pw { grid-column:2; font-size:var(--nw-fs-small); color:var(--nw-fg2); line-height:1.45; }
.piste .pe { grid-row:1 / span 2; grid-column:3; text-align:right; font-variant-numeric:tabular-nums; }
.piste .pe b { display:block; font-size:var(--nw-fs-case); font-weight:600; letter-spacing:-.015em; line-height:1.1; }
.piste .pe small { font-size:var(--nw-fs-small); color:var(--nw-fg2); }
/* What one more piece of equipment would bring: dashed, never counted as advice. */
/* \xAB Pour \xE9conomiser \xBB (maquette D) : aujourd'hui \u2192 mieux \u2192 gain. Sur un t\xE9l\xE9phone, l'un sous l'autre. */
.pistes.better { grid-template-columns:1fr; }
.piste.wide { grid-template-columns:auto minmax(0,1fr) auto; gap:8px 12px; }
.piste.wide .ico { grid-column:1; grid-row:1; }
.piste.wide .bt { grid-column:2; grid-row:1; font-size:var(--nw-fs-text); font-weight:700; line-height:1.3; }
.piste.wide .pe { grid-column:3; grid-row:1; }
.piste.wide .pe small { display:block; max-width:150px; margin-left:auto; }
.piste.wide .bn, .piste.wide .bm { grid-column:1 / -1; font-size:var(--nw-fs-small); line-height:1.45; color:var(--nw-fg2); min-width:0; }
.piste.wide .bn { grid-row:2; } .piste.wide .bm { grid-row:3; color:var(--nw-fg); font-weight:600; }
.piste.wide .bn small, .piste.wide .bm small { display:block; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; font-weight:700; color:var(--nw-fg2); margin-bottom:2px; }
.piste.wide .ba { display:none; }
.hrs { display:block; width:100%; max-width:300px; margin-top:6px; }
.hrs-b { display:flex; gap:1px; height:10px; border-radius:4px; overflow:hidden; background:color-mix(in srgb, var(--nw-fg) 6%, transparent); }
.hrs-b i { flex:1; background:var(--h, transparent); }
.hrs-x { display:flex; justify-content:space-between; font-size:10px; color:var(--nw-fg2); margin-top:2px; font-weight:400; letter-spacing:0; }
@container (min-width:680px) {
 .piste.wide { grid-template-columns:auto 150px minmax(0,1fr) 20px minmax(0,1fr) 130px; gap:0 14px; }
 .piste.wide .bn, .piste.wide .bm, .piste.wide .ba, .piste.wide .pe { grid-row:1; }
 .piste.wide .bn { grid-column:3; } .piste.wide .ba { grid-column:4; display:block; color:var(--nw-fg2); font-size:18px; text-align:center; }
 .piste.wide .bm { grid-column:5; } .piste.wide .pe { grid-column:6; }
}
.piste.up { background:none; border:1px dashed var(--nw-line); }
.piste.up .pt { font-weight:600; }
.piste.up .ico { background:color-mix(in srgb, var(--nw-fg) 6%, transparent); color:var(--nw-fg2); }

/* L'horloge de 24 heures, en haut de la carte compl\xE8te (maquette \xAB Bandeaux de la carte compl\xE8te \xBB, B, choisie par Frank le
   19 nov. 2026) : un trait par heure, vers l'ext\xE9rieur ce qui est achet\xE9 (heures pleines chaudes, heures creuses froides),
   vers le centre le soleil, en gris les heures \xE0 venir d'hier, une aiguille sur l'heure. \xC0 c\xF4t\xE9, le conseil et les chiffres
   du moment. \xC9troite : l'horloge au-dessus, centr\xE9e. */
.clock { --c:var(--nw-ok); display:flex; flex-direction:column; align-items:center; gap:14px; min-width:0; }
.clock[data-level="benefit"] { --c:var(--nw-benefit); } .clock[data-level="action"] { --c:var(--nw-act); } .clock[data-level="urgent"] { --c:var(--nw-alert); }
.dial { display:block; width:100%; max-width:300px; height:auto; flex:none; overflow:visible; }
.dial .ring { fill:none; stroke:var(--nw-line-soft); stroke-width:1; }
.dial .bars path { fill:none; stroke-width:8; stroke-linecap:round; }
.dial .peak { stroke:var(--nw-home); } .dial .off { stroke:var(--nw-cold); } .dial .sun { stroke:var(--nw-sun); }
.dial .next { stroke:color-mix(in srgb, var(--nw-fg) 13%, transparent); }
.dial .hand { fill:none; stroke:var(--nw-fg); stroke-width:2; stroke-linecap:round; }
.dial .tip, .dial .ping { fill:var(--nw-fg); }
.dial text { fill:var(--nw-fg2); font-size:11px; font-weight:600; }
.dial .cv { fill:var(--nw-fg); font-size:30px; font-weight:300; letter-spacing:-.03em; text-anchor:middle; font-variant-numeric:tabular-nums; }
.dial .cl { font-size:12px; text-anchor:middle; }
.dial .bars { transform-box:view-box; transform-origin:50% 50%; animation:nw-dial-in 1.2s cubic-bezier(.2,.8,.2,1) both; }
.dial .ping { transform-box:fill-box; transform-origin:center; animation:nw-ping 2.4s ease-out infinite; }
@keyframes nw-dial-in { from { transform:rotate(-35deg); opacity:0; } to { transform:none; opacity:1; } }
@keyframes nw-ping { from { transform:scale(1); opacity:.6; } to { transform:scale(3); opacity:0; } }
@media (prefers-reduced-motion:reduce) { .dial .bars, .dial .ping { animation:none; } .dial .ping { display:none; } }
.clock .ct { display:flex; flex-direction:column; gap:10px; min-width:0; width:100%; }
.clock .ct p { margin:0; }
.clock .ctt { font-size:var(--nw-fs-case); font-weight:700; letter-spacing:-.015em; line-height:1.25; text-wrap:balance; }
.clock[data-level="action"] .ctt, .clock[data-level="urgent"] .ctt { color:color-mix(in oklab, var(--c) 70%, var(--nw-fg)); }
.cstats { display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:10px; margin-top:4px; }
.cstat { display:flex; flex-direction:column; gap:2px; padding:12px 14px; border-radius:var(--nw-radius); background:var(--nw-surface); min-width:0; }
.cstat span { font-size:var(--nw-fs-small); color:var(--nw-fg2); font-weight:600; }
.cstat b { font-size:var(--nw-fs-value); font-weight:300; letter-spacing:-.04em; line-height:1.1; white-space:nowrap; font-variant-numeric:tabular-nums;
  color:color-mix(in oklab, var(--c) 55%, var(--nw-fg)); }
.cstat small { font-size:var(--nw-fs-small); color:var(--nw-fg2); }
.clock .nw-legend { justify-content:flex-start; }
@container (min-width:680px) {
 .clock { flex-direction:row; gap:28px; }
 .dial { width:300px; }
}
/* La loupe : l'heure survol\xE9e, touch\xE9e ou atteinte au clavier grandit avec ses voisines, les autres s'effacent ; ses
   chiffres prennent le centre. Un appui la fige, un second la rel\xE2che. */
.dial .h path { transition:stroke-width .22s ease, opacity .22s ease, d .22s ease; }
.dial .h.on path { stroke-width:14; } .dial .h.near path { stroke-width:10; }
.dial .bars.picking .h.far path { opacity:.28; }
.dial .h.on .peak { stroke:color-mix(in oklab, var(--nw-home) 80%, var(--nw-fg)); } .dial .h.on .off { stroke:color-mix(in oklab, var(--nw-cold) 80%, var(--nw-fg)); }
.dial .h.on .next { stroke:color-mix(in srgb, var(--nw-fg) 30%, transparent); }
.dial .hit { fill:none; stroke:transparent; stroke-width:30; pointer-events:stroke; cursor:pointer; outline:none; -webkit-tap-highlight-color:transparent; }
.dial .cv.pk { font-size:28px; }
.dial .cs { fill:var(--nw-fg); font-weight:650; }
.clock .nw-legend .hint { color:color-mix(in srgb, var(--nw-fg2) 80%, transparent); font-style:italic; }
@media (prefers-reduced-motion:reduce) { .dial .h path { transition:none; } }

/* \xAB Votre contrat, bien utilis\xE9 \xBB (maquette A) and \xAB Quand tournent vos machines \xBB (maquette C), 19 Nov. 2026 */
.usage { display:grid; gap:10px; }
.u-top { display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px; }
.u-gauge, .u-verdict { padding:14px 16px; border-radius:var(--nw-radius); background:color-mix(in srgb, var(--nw-fg) 5%, transparent); display:grid; gap:6px; align-content:start; }
.u-verdict.good { background:color-mix(in oklab, var(--nw-ok) 14%, transparent); }
.u-k { margin:0; font-size:var(--nw-fs-small); color:var(--nw-fg2); font-weight:600; }
.u-v { margin:0; display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 12px; }
.u-v > b { font-size:var(--nw-fs-case); font-weight:300; letter-spacing:-.03em; color:var(--nw-cold); }
.u-v span { font-size:var(--nw-fs-small); color:var(--nw-fg2); } .u-v .ok { color:var(--nw-ok); font-weight:700; }
.u-big { margin:0; font-size:var(--nw-fs-text); font-weight:700; color:var(--nw-fg); }
.u-verdict.good .u-big { color:var(--nw-ok); }
.u-n { margin:0; font-size:var(--nw-fs-small); color:var(--nw-fg2); line-height:1.45; } .u-n b { color:var(--nw-fg); font-weight:650; }
.track i.next { background:color-mix(in oklab, var(--nw-ok) 40%, transparent); }
.mach { display:grid; grid-template-columns:minmax(90px, auto) 1fr auto; gap:10px 12px; align-items:center; }
.mach .mn { font-size:var(--nw-fs-text); font-weight:650; display:grid; } .mach .mn small, .mach .me small { font-size:var(--nw-fs-small); color:var(--nw-fg2); font-weight:400; }
.mach .stack { display:flex; height:14px; border-radius:7px; overflow:hidden; background:color-mix(in srgb, var(--nw-fg) 7%, transparent); }
.mach .stack i { background:var(--c); }
.mach .me { text-align:right; display:grid; font-variant-numeric:tabular-nums; } .mach .me b { font-weight:600; }
.smonths { display:grid; grid-template-columns:repeat(12, minmax(0, 1fr)); gap:6px; height:84px; align-items:end; }
.smonths .sm { display:grid; grid-template-rows:1fr auto; height:100%; gap:4px; text-align:center; }
.smonths .sm i { align-self:end; border-radius:4px 4px 2px 2px; background:var(--nw-sun); }
.smonths .sm small { font-size:var(--nw-fs-small); color:var(--nw-fg2); }
.u-kva { margin-top:auto; padding-top:6px; }
`;var ht=[["complete","mdi:page-layout-body","Compl\xE8te","en ce moment, aujourd\u2019hui, ce mois-ci, puis le d\xE9tail"],["tuile","mdi:dock-window","Tuile","en ce moment : une phrase, un chiffre"],["conseils","mdi:piggy-bank-outline","Conseils","ce qui ferait \xE9conomiser, en euros par an"],["soleil","mdi:solar-power-variant","Soleil","ce que les panneaux ont produit aujourd\u2019hui"],["chauffage","mdi:fire","Chauffage","ce qu\u2019a co\xFBt\xE9 la saison, depuis le 1er octobre"],["veille","mdi:weather-night","Veille","ce qui tourne la nuit, les 30 derni\xE8res nuits"],["eau","mdi:water","Eau","les litres et les euros du mois"],["appareils","mdi:power-plug","Appareils","ce que chaque appareil a consomm\xE9 aujourd\u2019hui"],["pointe","mdi:transmission-tower","Pointe","la plus forte puissance prise aujourd\u2019hui"],["contrat","mdi:file-document-outline","Contrat","vos heures creuses et vos prix, ce mois-ci"]],mt=o=>{o.preventDefault(),history.pushState(null,"",o.currentTarget.getAttribute("href")??"/hestia/energie"),window.dispatchEvent(new CustomEvent("location-changed",{bubbles:!0,composed:!0}))},Xe=class extends R{static{this.properties={hass:{attribute:!1},config:{state:!0}}}static{this.styles=Ve`.note{color:var(--secondary-text-color);font-size:12px;line-height:1.6;margin:0 0 16px}a{color:var(--primary-color)}
  .formats{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin:4px 0 16px}
  .formats button{all:unset;box-sizing:border-box;display:flex;flex-direction:column;gap:4px;padding:10px 12px;border:1px solid var(--divider-color);border-radius:12px;cursor:pointer;color:var(--primary-text-color);font-size:12px;line-height:1.45}
  .formats button:hover{border-color:var(--secondary-text-color)}
  .formats button:focus-visible{outline:2px solid var(--primary-color);outline-offset:2px}
  .formats button.on{border:2px solid var(--primary-color);padding:9px 11px}
  .formats ha-icon{--mdc-icon-size:20px;color:var(--secondary-text-color)}.formats button.on ha-icon{color:var(--primary-color)}
  .formats b{font-size:14px;font-weight:500}.formats span{color:var(--secondary-text-color)}`}setConfig(s){this.config={...s}}set(s){let e={...this.config,...s};e.name||delete e.name,e.card==="complete"&&delete e.card,this.config=e,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:e},bubbles:!0,composed:!0}))}render(){if(!this.config)return c;let s=this.config.card??"complete";return i`<p class="note">Choisissez ce que montre la carte. Le contrat, les réglages et les extensions se règlent dans
    <a href="/hestia/energie" @click=${mt}>l’onglet Énergie</a>.</p>
   <div class="formats" role="radiogroup" aria-label="Format">${ht.map(([e,n,t,r])=>i`<button type="button" role="radio" aria-checked=${e===s}
     class=${e===s?"on":""} @click=${()=>{e!==s&&this.set({card:e})}}><ha-icon icon=${n}></ha-icon><b>${t}</b><span>${r}</span></button>`)}</div>
   <ha-form .hass=${this.hass} .data=${{name:this.config.name??""}} .schema=${[{name:"name",selector:{text:{}}}]}
     .computeLabel=${()=>"Titre facultatif"} .computeHelper=${()=>"Vide : \xAB Maison \xBB."}
     @value-changed=${e=>{e.stopPropagation(),this.set({name:(e.detail.value.name??"").trim()})}}></ha-form>`}};customElements.get("hestia-energy-card-editor")||customElements.define("hestia-energy-card-editor",Xe);var re=new WeakMap;function Pn(o,s){re.get(o)===s&&re.delete(o),clearTimeout(s.closing),s.stop?.then(e=>e()).catch(()=>{})}function Hn(o,s,e,n){let t=re.get(o),r={view:s,error:e,reload:n};if(t){clearTimeout(t.closing),t.closing=void 0;let l=t.last;l&&queueMicrotask(()=>{t.listeners.has(r)&&s(l)})}else{let l={listeners:new Set};t=l,re.set(o,l),l.stop=o.subscribeMessage(u=>{if(u.reload){Pn(o,l);for(let g of[...l.listeners])g.reload();return}let p;if(u.changes){if(!l.last)return;p={...l.last,...u.changes};for(let g of u.removed??[])delete p[g]}else if(u.view)p=u.view;else return;l.last=p;for(let g of[...l.listeners])g.view(p)},{type:"hestia_energy/subscribe"}),l.stop.catch(u=>{re.get(o)===l&&re.delete(o);for(let p of[...l.listeners])p.error(u)})}let a=t;return a.listeners.add(r),()=>{!a.listeners.delete(r)||a.listeners.size||(clearTimeout(a.closing),a.closing=setTimeout(()=>{a.listeners.size||Pn(o,a)},5e3))}}var ze=["soleil","chauffage","veille","eau","appareils","pointe","contrat"],Wn={veille_haute:["moon","--nw-watch"],chauffage_degre:["flame","--nw-heat"],contrat_base:["doc","--nw-ok"],jour_inhabituel:["home","--nw-home"],budget_mois:["doc","--nw-home"],chauffe_eau_heures:["drop","--nw-cold"],machine_heures:["clock","--nw-home"]},Rn={sun:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg>',home:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3.5 11 12 4l8.5 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5.5h4V20"/></svg>',grid:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M8 21 11 3h2l3 18"/><path d="M5 7h14M6.5 12h11M9.5 16.5l5-4.5M14.5 16.5l-5-4.5"/></svg>',bolt:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M13 2.5 5 13.5h6l-1 8 8-11h-6z"/></svg>',drop:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3s6.5 7 6.5 11.2A6.5 6.5 0 0 1 5.5 14.2C5.5 10 12 3 12 3z"/></svg>',clock:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',moon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z"/></svg>',plug:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3v5M15 3v5M6.5 8h11v3.5a5.5 5.5 0 0 1-11 0z"/><path d="M12 17v4"/></svg>',doc:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 3h8.5L19 7.5V21H6z"/><path d="M14 3v5h5M9 12.5h7M9 16.5h7"/></svg>',flame:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 21.5a6.5 6.5 0 0 0 6.5-6.5c0-4.5-4-6.5-4.5-11-2.5 2-4 4.5-4 7-1-.5-2-1.8-2.2-3C6.5 9.8 5.5 12.3 5.5 15a6.5 6.5 0 0 0 6.5 6.5z"/></svg>',chev:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>'},T=o=>zn(Rn[o]??Rn.bolt),$=(o,s=1)=>{let e=o.toLocaleString("fr-FR",{maximumFractionDigits:s,minimumFractionDigits:0,useGrouping:!1}),[n,t]=e.split(",");return n.replace(/\B(?=(\d{3})+(?!\d))/g,"\u202F")+(t?","+t:"")},ae=o=>o.toLocaleString("fr-FR",{minimumFractionDigits:2,maximumFractionDigits:2}),E=o=>o==null?"\u2014":$(o/1e3,1),v=o=>o==null?"\u2014":Math.abs(o)<10?ae(o):$(o,0),Ze=o=>o==null?"\u2014":ae(o),we=o=>o==null?"\u2014":$(Math.abs(o)>=100?Math.round(o/10)*10:Math.round(o),0),x=o=>o==null?"\u2014":$(o,Math.abs(o)<20?1:0),L=o=>o==null?"\u2014":ae(o),gt=["dimanche","lundi","mardi","mercredi","jeudi","vendredi","samedi"],Q=o=>{if(!o)return"hier";let s=new Date(o+"T12:00"),e=new Date;e.setHours(12,0,0,0);let n=Math.round((e.getTime()-s.getTime())/864e5);return n===1?"hier":n===2?"avant-hier":gt[s.getDay()]},en=o=>o.charAt(0).toUpperCase()+o.slice(1),ft=o=>{o.preventDefault(),history.pushState(null,"",o.currentTarget.getAttribute("href")??"/hestia/energie"),window.dispatchEvent(new CustomEvent("location-changed",{bubbles:!0,composed:!0}))},Pe=["janvier","f\xE9vrier","mars","avril","mai","juin","juillet","ao\xFBt","septembre","octobre","novembre","d\xE9cembre"],wt=["janv.","f\xE9vr.","mars","avr.","mai","juin","juil.","ao\xFBt","sept.","oct.","nov.","d\xE9c."],Tn={bleu:"ok",vert:"benefit",orange:"action",rouge:"urgent"},bt={bleu:"--nw-ok",vert:"--nw-benefit",orange:"--nw-act",rouge:"--nw-alert"},vt={fuite_eau:"drop",disjoncteur:"bolt",chauffe_eau_reseau:"drop",soleil_en_trop:"sun",soleil_machine_ok:"sun",soleil_chaleur:"sun",machines_ensemble:"plug",machine_sans_soleil:"sun",machine_heures_pleines:"clock",oublie:"plug",rien_hc:"clock",rien_hc_bientot:"clock",rien_soleil_juste:"sun",rien_soleil_petit:"sun",rien_soleil_plus_tard:"sun",rien:"home"},H=o=>o===12?"midi":o===0||o===24?"minuit":`${o}\xA0h`,X=o=>o.replace(/ /g,"\xA0"),be=o=>o.getHours()+"\xA0h\xA0"+String(o.getMinutes()).padStart(2,"0"),He=o=>new Date(o+"T12:00:00"),Bn=o=>{let s=He(o).getDate();return s===1?"1er":String(s)},Vn=o=>`${Bn(o)} ${Pe[He(o).getMonth()]}`,Un=o=>o<=.3?"un quart":o<=.4?"un tiers":o<=.58?"la moiti\xE9":o<=.7?"deux tiers":o<=.85?"trois quarts":"presque tout",tn=o=>{let s=o.match(/(\d+) h(?: (\d+))?/);return s?Number(s[1])*60+(s[2]?Number(s[2]):0):0};function ie(o){return(o??[]).flatMap(([s,e])=>{let n=tn(s),t=tn(e);return t>n?[[n,t]]:[[n,1440],[0,t]]})}var Le=o=>o.length>0&&o.every(([s,e])=>s>=1200||e<=570);function ve(o,s){let e=Math.max(...o.map(n=>n.v),0)||1;return i`<div class="hb" style="--c:var(${s})">${o.map(n=>i`<span class="n${n.muted?" muted":""}"><span>${n.n}</span>${n.live?i`<span class="live">${n.live}</span>`:c}</span>
  <span class="t${n.dash?" dash":""}"><i class=${n.soft?"soft":""} style="width:${Math.max(1,n.v/e*100)}%"></i></span>
  <span class="v${n.muted?" muted":""}">${n.txt}${n.sub?i`<small>${n.sub}</small>`:c}</span>`)}</div>`}function Dn(o,s){let e=o.filter((r,a)=>a<5||r.live),n=o.filter(r=>!e.includes(r));if(n.length<2)return o;let t=n.reduce((r,a)=>r+a.v,0);return[...e,{n:`Et ${n.length} autres`,v:t,txt:s(t),muted:!0,soft:!0}]}function qe(o,s,e={}){let n=Math.max(...o.map(l=>l??0),0),t=e.max??(n*1.15||1),r=n>0?o.indexOf(n):-1,a=o.length;return i`<div class="cols${e.tall?" tall":""}" style="--c:var(${s})">${o.map((l,u)=>{let p=l==null?2:Math.max(2,l/t*100);return i`<div class="c${e.bands?.(u)?" band":""}">${u===r&&e.pin?i`<span class="pin ${u<2?"l":u>a-3?"r":""}" style="bottom:${p}%">${e.pin(l)}</span>`:c}<i class="${l==null?"none":""}${e.part===u?" part":""}" style="height:${p}%"></i></div>`})}
  ${e.limit?i`<div class="limit" style="bottom:${e.limit/t*100}%"><span>${e.limitLabel}</span></div>`:c}</div>`}var nn=i`<div class="ticks"><span>0 h</span><span>6 h</span><span>12 h</span><span>18 h</span><span>24 h</span></div>`,sn=class extends R{constructor(){super();this._config={type:"custom:hestia-energy-card",card:"complete"};this._folded=new Set}static{this.styles=[ue(Ln),ue(qn)]}static{this.properties={_view:{state:!0},_open:{state:!0},_folded:{state:!0},_error:{state:!0},_hover:{state:!0},_pin:{state:!0}}}static getStubConfig(){return{card:"complete"}}static getConfigElement(){return document.createElement("hestia-energy-card-editor")}setConfig(e){let n=e.card??"complete";if(n!=="complete"&&n!=="tuile"&&n!=="conseils"&&!ze.includes(n))throw new Error(`card: ${n} ? (complete, tuile, conseils, ${ze.join(", ")})`);this._config={...e,card:n}}getCardSize(){return this._config.card==="tuile"?2:8}getGridOptions(){let e=this._config.card;return e==="complete"||e==="conseils"?{columns:"full",rows:"auto"}:{columns:12,rows:"auto",min_columns:6}}set hass(e){let n=this._hass?.connection!==e.connection;this._hass=e,(n||!this._stop)&&this._follow()}connectedCallback(){super.connectedCallback(),this._follow()}disconnectedCallback(){super.disconnectedCallback(),this._unfollow()}_unfollow(){this._stop?.(),this._stop=void 0,window.clearTimeout(this._again)}_follow(){this._unfollow(),!(!this._hass||!this.isConnected)&&(this._stop=Hn(this._hass.connection,e=>{this._view=e,this._error=void 0},e=>{this._stop=void 0,this._error=e.message??"Hestia \xC9nergie ne r\xE9pond pas.",this._again=window.setTimeout(()=>this._follow(),3e4)},()=>{this._stop=void 0,this._again=window.setTimeout(()=>this._follow(),2e3)}))}render(){let e=this._view;if(this._error&&!e)return i`<ha-card><div class="empty">${this._error}</div></ha-card>`;if(!e||!e.pret)return i`<ha-card><div class="empty">Hestia Énergie lit la page Énergie…</div></ha-card>`;let n=this._config.card;return n==="tuile"?this._tile(e):n==="conseils"?this._advice(e):n!=="complete"?i`<ha-card>${this._detail(e,n,!1)}</ha-card>`:i`${this._full(e)}${this._open?i`<div class="ov" @click=${t=>{t.target===t.currentTarget&&(this._open=void 0)}}
   @keydown=${t=>{t.key==="Escape"&&(this._open=void 0)}}><ha-card class="sheet" role="dialog" aria-modal="true">${this._detail(e,this._open,!0)}</ha-card></div>`:c}`}_name(){return this._config.name??"Maison"}_live(e){return!!(e.equipement.direct&&e.direct?.maison_w!=null)}_when(e){return e?.periode==="hc"?"en heures creuses":e?.periode==="hp"?"en heures pleines":""}_nowSay(e,n){let t=e.direct,r=t.maison_w??0,a=Math.min(t.soleil_w??0,r),l=t.achat_w??0,u=t.revente_w??0,p=this._when(t),g=t.prix!=null?i`<b>${v(l/1e3*t.prix)} € de l'heure</b>${p?`, ${p}`:""}`:null,d=n?i`La maison consomme <b>${E(r)} kW</b>. `:c;return e.equipement.soleil&&u>=30&&l<30?i`${d}Le soleil couvre tout, et <b>${E(u)} kW</b> partent au réseau.`:e.equipement.soleil&&a>=30?n?i`${d}Le soleil en couvre <b>${Math.round(a/r*100)} %</b>, le reste vient du réseau${g?i` : ${g}`:""}.`:i`Le soleil en donne <b>${E(a)} kW</b> ; le reste vient du réseau${g?i` : ${g}`:""}.`:g?i`${d}Tout vient du réseau : ${g}.`:d}_tile(e){let n=e.direct?.bandeau,t=n?bt[n.couleur]??"--nw-ok":"--nw-ok",r=this._live(e),a=n?[n.pastille,t]:void 0,l={ic:"home",c:"--nw-home",subject:"\xC9nergie",pill:a,over:!1},u=(e.pistes??[]).find(d=>d.euros_an!=null);if(r)return i`<ha-card class="tile">${this._ans({...l,period:"en ce moment",val:E(e.direct.maison_w),unit:"kW",cap:"pour toute la maison",why:n?.couleur==="bleu"&&u?i`Rien à faire maintenant. ${this._saySave(u)}`:this._nowSay(e,!1)})}</ha-card>`;let p=e.dernier_jour,g=Q(p?.jour);return p?i`<ha-card class="tile">${this._ans({...l,period:g,...p.euros!=null?{val:v(p.euros),unit:"\u20AC"}:{val:x(p.kwh_achetes),unit:"kWh"},cap:"pour toute la maison",why:u?this._saySave(u):p.euros!=null?i`<b>${x(p.kwh_achetes)} kWh</b> achetés au réseau${p.soleil_couvre!=null?i` ; le soleil a couvert <b>${p.soleil_couvre} %</b> de la maison`:""}.`:"Le prix sera connu avec le contrat."})}</ha-card>`:i`<ha-card class="tile">${this._ans({...l,period:"",msg:"Les premiers jours arrivent",why:"Enedis envoie chaque journ\xE9e le lendemain."})}</ha-card>`}_full(e){let n=e.direct?.bandeau,t=new Date,r=t.toLocaleDateString("fr-FR",{weekday:"long",day:"numeric",month:"long"})+" \xB7 "+be(t),a=this._clock(e),l=[a&&!this._live(e)?c:this._nowSection(e),this._todaySection(e),this._monthSection(e)].filter(u=>u!==c);return i`<ha-card>
   <div class="head"><div style="min-width:0"><div class="nw-label">Énergie</div><div class="nw-title">${this._name()}</div></div><div class="when">${r}</div></div>
   ${a??(n&&this._live(e)?i`<div class="nw-band nw-glass" data-level=${Tn[n.couleur]??"ok"}><div class="nw-band-row"><span class="nw-band-pic box">${T(vt[n.id]??"home")}</span>
    <div class="nw-band-text"><p class="nw-band-kicker">En ce moment</p><p class="nw-band-title">${n.titre}</p>${n.pourquoi||this._periodSay(e)?i`<p class="nw-band-line">${n.pourquoi||this._periodSay(e)}</p>`:c}</div></div></div>`:c)}
   <div class="periods${l.length===2?" two":""}">${l}</div>
   ${e.usage?this._section("usage","Votre contrat, bien utilis\xE9","sur 12 mois",this._usage(e)):c}
   ${e.pistes?.length?this._section("save","Pour \xE9conomiser","sur 12 mois, en euros",i`<div class="pistes better">${e.pistes.slice(0,6).map(u=>u.maintenant?this._better(u):this._piste(u))}</div>`):c}
   ${this._section("more","En d\xE9tail","touchez pour ouvrir",i`<div class="more">${this._goes(e)}</div>`)}
  </ha-card>`}_clock(e){let n=e.heures?.aujourdhui??[],t=e.heures?.hier??[],r=n.some(m=>m.achat!=null),a=r?n:t;if(!a.some(m=>m.achat!=null))return;let l=new Date,u=l.getHours()+l.getMinutes()/60,p=ie(e.heures_creuses),g=m=>p.some(([k,S])=>m*60+30>=k&&m*60+30<S),d=Math.max(.3,...a.map(m=>m.achat??0),...r?t.map(m=>m.achat??0):[]),f=Math.max(.3,...a.map(m=>m.soleil??0)),h=170,w=98,b=46,y=86,P=32,A=m=>m/24*Math.PI*2-Math.PI/2,j=(m,k)=>`${(h+Math.cos(A(m))*k).toFixed(1)} ${(h+Math.sin(A(m))*k).toFixed(1)}`,_=(m,k,S)=>`M${j(m+.5,k)} L${j(m+.5,S)} `,M=e.contrat,z=M?.prix_hp??null,C=M?.prix_hc??null,W=M?.prix_base??null,Z=m=>M?.option==="base"?W:M?.option==="hphc"?g(m)?C:z:null,xe=[],Re=0,rn=!1,an=!1;for(let m=0;m<24;m++){let k=a[m],S=r&&m>l.getHours(),O=S?t[m]?.achat??null:k?.achat??null,Ae=S?null:(k?.soleil??0)>=.01?k.soleil:null;!S&&O!=null&&(Re+=O),Ae!=null&&(rn=!0),S&&O!=null&&(an=!0),xe.push({i:m,cls:S?"next":g(m)?"off":"peak",val:O,sun:Ae,future:S})}let $e=m=>m<1?$(m,2):x(m),V=this._pin??this._hover,_e=(m,k)=>{let S=Math.abs(m-k);return Math.min(S,24-S)},On=m=>V==null?0:_e(m,V)===0?16:_e(m,V)===1?5:0,Nn=m=>{let k=m.val!=null?Z(m.i):null;return`de ${H(m.i)} \xE0 ${H(m.i+1)} : ${m.val!=null?`${$e(m.val)} kWh ${m.future?"hier":"achet\xE9s"}`:"rien de mesur\xE9"}${k!=null&&m.val!=null?`, environ ${ae(m.val*k)} \u20AC`:""}${m.sun!=null?`, ${$e(m.sun)} kWh de soleil`:""}`},In=xe.map(m=>{let k=On(m.i),S=V==null?"":_e(m.i,V)===0?" on":_e(m.i,V)===1?" near":" far";return I`<g class=${`h${S}`}>${m.val!=null?I`<path class=${m.cls} d=${_(m.i,w-(k?2:0),w+3+m.val/d*b+k)}></path>`:c}
    ${m.sun!=null?I`<path class="sun" d=${_(m.i,y+(k?2:0),y-3-m.sun/f*P-k*.6)}></path>`:c}</g>`}),ke=m=>{this._hover=m},on=m=>{this._pin=this._pin===m?void 0:m},Fn=xe.map(m=>I`<path class="hit" d=${_(m.i,44,164)} tabindex="0" role="button" aria-label=${Nn(m)} aria-pressed=${this._pin===m.i?"true":"false"}
   @pointerenter=${()=>ke(m.i)} @focus=${()=>ke(m.i)} @blur=${()=>ke()} @click=${()=>on(m.i)}
   @keydown=${k=>{k.key==="Enter"||k.key===" "?(k.preventDefault(),on(m.i)):k.key==="Escape"&&(this._pin=void 0)}}></path>`),oe=this._live(e),F=e.direct,K=F?.bandeau,ln=e.jusqu_ici,B=e.dernier_jour,un=oe?[`${E(F.maison_w)} kW`,"en ce moment"]:r&&ln?.euros!=null?[`${v(ln.euros)} \u20AC`,"depuis minuit"]:!r&&B?.euros!=null?[`${v(B.euros)} \u20AC`,Q(B.jour)]:[`${x(Re)} kWh`,r?"depuis minuit":Q(B?.jour)],q=V!=null?xe[V]:void 0,ee=q?[q.val!=null?`${$e(q.val)} kWh`:"\u2014",`${H(q.i)} \u2013 ${H(q.i+1)}${q.future?" \xB7 hier":""}`,[q.val!=null&&Z(q.i)!=null?`\u2248 ${ae(q.val*Z(q.i))} \u20AC`:"",q.sun!=null?`soleil ${$e(q.sun)} kWh`:""].filter(Boolean).join(" \xB7 ")]:[un[0],un[1],""],ne=r?e.jour?.soleil_kwh:B?.soleil_kwh,Kn=F?.prix!=null&&!(e.contrat?.a_confirmer??[]).includes("option"),Jn=F?.prochain_changement?` jusqu'\xE0 ${be(new Date(F.prochain_changement.a))}`:"",cn=[...Kn?[["Le kWh maintenant",`${L(F.prix)} \u20AC`,`${this._when(F)}${Jn}`.trim()||"\xE0 toute heure","--nw-home"]]:[],...r&&e.pointe?[["Heure la plus charg\xE9e",`${E(e.pointe.kw*1e3)} kW`,`entre ${H(e.pointe.h)} et ${H(e.pointe.h+1)}`,"--nw-grid"]]:[],...e.equipement.soleil&&ne!=null&&ne>=.05?[["Soleil",`${x(ne)} kWh`,r?"produits aujourd'hui":`produits ${Q(B?.jour)}`,"--nw-sun"]]:[]],Gn=oe&&K?K.titre:`${r?"Aujourd'hui":en(Q(B?.jour))}, en un tour d'horloge`,pn=oe&&K?K.pourquoi||this._periodSay(e):r?"":"Le compteur envoie chaque journ\xE9e le lendemain.",Yn=`${r?"Aujourd'hui":en(Q(B?.jour))} heure par heure : ${x(Re)} kWh achet\xE9s au r\xE9seau${ne!=null&&ne>=.05?`, ${x(ne)} kWh de soleil`:""}.`,ye=(m,k,S,O=4)=>{let[Ae,Qn]=j(m,w+b+16).split(" ");return I`<text x=${Ae} y=${Number(Qn)+O} text-anchor=${S}>${k}</text>`};return i`<div class="clock" data-level=${oe&&K?Tn[K.couleur]??"ok":"ok"}>
   <svg class="dial" viewBox="0 0 340 340" role="group" aria-label=${Yn} @pointerleave=${()=>ke()}>
    <circle class="ring" cx="170" cy="170" r=${w}></circle>
    <g class=${`bars${V!=null?" picking":""}`}>${In}</g>
    ${ye(0,"0 h","middle",0)}${ye(6,"6 h","end")}${ye(12,"12 h","middle",7)}${ye(18,"18 h","start")}
    ${r?I`<path class="hand" d=${`M${j(u,w-6)} L${j(u,w+b+6)}`}></path>
     <circle class="ping" cx=${j(u,w+b+6).split(" ")[0]} cy=${j(u,w+b+6).split(" ")[1]} r="4.5"></circle>
     <circle class="tip" cx=${j(u,w+b+6).split(" ")[0]} cy=${j(u,w+b+6).split(" ")[1]} r="4.5"></circle>`:c}
    <text class=${`cv${q?" pk":""}`} x="170" y=${ee[2]?166:172}>${ee[0]}</text><text class="cl" x="170" y=${ee[2]?188:194}>${ee[1]}</text>
    ${ee[2]?I`<text class="cl cs" x="170" y="206">${ee[2]}</text>`:c}
    <g class="hits">${Fn}</g>
   </svg>
   <div class="ct">
    ${oe&&K?i`<p class="nw-label">En ce moment</p>`:c}
    <p class="ctt">${Gn}</p>${pn?i`<p class="ans-w">${pn}</p>`:c}
    ${cn.length?i`<div class="cstats">${cn.map(([m,k,S,O])=>i`<div class="cstat" style="--c:var(${O})"><span>${m}</span><b>${k}</b><small>${S}</small></div>`)}</div>`:c}
    <div class="nw-legend"><span><i style="--c:var(--nw-home)"></i>acheté en heures pleines</span>${p.length?i`<span><i style="--c:var(--nw-cold)"></i>en heures creuses</span>`:c}
     ${rn?i`<span><i style="--c:var(--nw-sun)"></i>soleil, vers le centre</span>`:c}${an?i`<span><i style="--c:color-mix(in srgb, var(--nw-fg) 18%, transparent)"></i>hier, aux heures à venir</span>`:c}
     <span class="hint">touchez une heure pour ses chiffres</span></div>
   </div>
  </div>`}_periodSay(e){let n=e.direct,t=n?.prochain_changement;if(!t||n?.periode!=="hp"&&n?.periode!=="hc")return"";let r=new Date(t.a),a=n.periode==="hp"?"Heures pleines":"Heures creuses",l=r.getHours()*60+r.getMinutes(),u=(e.heures_creuses??[]).find(([g])=>tn(g)===l),p=t.periode==="hc"&&u?`, puis heures creuses jusqu'\xE0 ${X(u[1])}`:"";return`${a} jusqu'\xE0 ${be(r)}${p}.`}_section(e,n,t,r){let a=!this._folded.has(e);return i`<div class="sec"><button class="nw-fold-head" aria-expanded=${String(a)} @click=${()=>{let l=new Set(this._folded);a?l.add(e):l.delete(e),this._folded=l}}>
   <span class="nw-title">${n}</span><span class="nw-sum">${t}</span><span class="nw-chevron">${T("chev")}</span></button>${a?r:c}</div>`}_flow(e){let n=e.direct,t=(n.periode??"").includes("hc"),r=t?"--nw-cold":"--nw-level3",a=e.equipement.soleil?Math.max(0,n.soleil_w??0):null,l=Math.max(0,n.maison_w??0),u=(n.achat_w??0)>=30,p=!u&&(n.revente_w??0)>=30,g=a==null?0:Math.min(a,l),d=A=>A<1e3?`${$(A,0)} W`:`${$(A/1e3,2)} kW`,f=(A,j,_,M,z=!1)=>i`<div class="fnode${z?" dim":""}" style="--c:var(${j})"><span class="fdot">${T(A)}</span><span class="fl">${M}</span><span class="fv">${_}</span></div>`,h=(A,j,_,M=!1)=>{let z=j>=30,C=z?Math.max(1.2,3.2-j/1500):0;return i`<div class="flink${z?"":" off"}${M?" back":""}" style="--c:var(${A});--dur:${C.toFixed(2)}s"><span class="fsay">${z?i`<b>${_[0]}</b><span>${_[1]}</span>`:""}</span><span class="fline">${z?i`<i></i><i></i><i></i>`:c}</span></div>`},w=u?n.achat_w:p?n.revente_w:0,b=u?[`\u2199 ${d(w)}`,"achet\xE9s"]:[`\u2197 ${d(w)}`,"revendus"],y=e.eau&&e.eau.jour_l>0?i`<div class="fwater"><span class="fstem"></span>${f("drop","--nw-water",`${$(e.eau.jour_l,0)} L`,"Eau aujourd'hui")}</div>`:c,P=`--sunA:${a==null?0:Math.min(1,a/1500).toFixed(2)};--gridA:${u||p?Math.min(1,.35+w/2e3).toFixed(2):".25"};--tone:var(${r})`;return i`<div class="flow2${a==null?" two":""}" style=${P}>
   ${a!=null?i`${f("sun","--nw-prod",d(a),"Production",a<30)}${h("--nw-prod",g,[d(g),"en direct"])}`:c}
   <div class="fmid">${f("home",r,d(l),"Maison")}${y}</div>
   ${h(r,w,b,u)}
   ${f("grid",r,`${p?"+":""}${d(w)}`,"R\xE9seau",!u&&!p)}
  </div>`}_nowSection(e){let n=e.direct;if(!n)return c;if(!this._live(e)){if(n.prix==null||(e.contrat?.a_confirmer??[]).includes("option"))return c;let l=n.prochain_changement?` jusqu'\xE0 ${be(new Date(n.prochain_changement.a))}`:"";return this._section("now","En ce moment",this._when(n),i`<div class="lines"><div class="line"><span class="ico" style="--c:var(--nw-grid)">${T("clock")}</span>
    <span>Le kWh coûte <b>${L(n.prix)} €</b>${this._when(n)?` ${this._when(n)}`:""}${l}.</span></div></div>`)}let t=n.chauffage,r=[...n.en_marche].sort((l,u)=>u.w-l.w),a=[...t?.poele?[i`<span class="chip">Poêle <b>allumé</b></span>`]:[],...(t?.pieces??[]).map(l=>i`<span class="chip">Chauffage ${l.nom}${l.w!=null?i` <b>${E(l.w)} kW</b>`:c}</span>`),...r.slice(0,5).map(l=>i`<span class="chip">${l.nom} <b>${E(l.w)} kW</b></span>`)];return this._section("now","En ce moment",`${E(n.maison_w)}\xA0kW pour toute la maison`,i`${this._flow(e)}
   <div class="lines"><div class="line"><span class="ico" style="--c:var(--nw-home)">${T("home")}</span><span>${this._nowSay(e,!0)}</span></div>
    ${a.length?i`<div class="chips"><span class="nw-label">En marche</span>${a}</div>`:c}</div>`)}_todaySection(e){let n=e.jusqu_ici;if(n){let r=new Date(n.jusqu_a).getHours(),a=n.euros!=null&&n.hier_euros!=null,l=a?n.euros:n.kwh,u=a?n.hier_euros:n.hier_kwh,p=l-u,g=a?Math.abs(p)<.1:Math.abs(p)<.5,d=a?"\u20AC":"kWh",f=h=>a?v(h):x(h);return this._section("today","Aujourd'hui","depuis minuit",i`<div class="big"><b>${f(l)} ${d}</b><span>${a?"d\xE9pens\xE9s":"consomm\xE9s"} depuis minuit</span></div>
    <p class="say">${g?i`Comme hier à la même heure.`:i`<b>${f(Math.abs(p))} ${d} de ${p>0?"plus":"moins"}</b> qu'hier à la même heure.`}</p>
    ${ve([{n:"Aujourd'hui",v:l,txt:`${f(l)} ${d}`},{n:`Hier \xE0 ${H(r)}`,v:u,txt:`${f(u)} ${d}`,muted:!0,soft:!0}],"--nw-home")}`)}let t=e.dernier_jour;return t?this._section("today",en(Q(t.jour)),"toute la journ\xE9e",i`<div class="big"><b>${t.euros!=null?`${v(t.euros)}\xA0\u20AC`:`${x(t.kwh_achetes)}\xA0kWh`}</b><span>${t.euros!=null?"pour toute la journ\xE9e":"achet\xE9s au r\xE9seau"}</span></div>
   ${t.euros!=null?i`<p class="say"><b>${x(t.kwh_achetes)} kWh</b> achetés au réseau${t.soleil_couvre!=null?i` ; le soleil a couvert <b>${t.soleil_couvre} %</b> de la maison`:""}.</p>`:c}`):c}_monthSection(e){let n=e.mois;if(!n)return c;let t=new Date,r=n.euros??n.euros_energie,a=e.mois_an_dernier,l=e.projection,u=a?.euros!=null?` L'an dernier, ${Pe[t.getMonth()]} avait co\xFBt\xE9 ${v(a.euros)}\xA0\u20AC.`:"";return this._section("month","Ce mois-ci",`depuis le 1er ${Pe[t.getMonth()]}`,i`<div class="big"><b>${r!=null?`${Ze(r)}\xA0\u20AC`:`${x(n.kwh_achetes)}\xA0kWh`}</b><span>${r==null?"achet\xE9s au r\xE9seau":n.euros!=null?"abonnement compris":"sans l'abonnement"}</span></div>
   ${l!=null?i`<p class="say">Au même rythme, <b>environ ${v(l)} €</b> à la fin du mois.${u}</p>
    <div><div class="track" style="--c:var(--nw-ok)"><i style="width:${Math.min(100,(r??0)/l*100)}%"></i></div>
     <div class="track-l"><span>déjà <b>${v(r)} €</b></span><span>fin du mois <b>${v(l)} €</b></span></div></div>`:u?i`<p class="say">${u.trim()}</p>`:c}`)}_go(e,n,t,r,a,l,u){let[p,g]=r.split(" \xB7 ");return i`<button class="go" style="--c:var(${t})" @click=${()=>{this._open=e}}><span class="g-h"><span class="ico">${T(n)}</span><span class="g-t">${p}<small>${g}</small></span><span class="ar">›</span></span>
   <span class="g-v">${a}<small>${l}</small></span><span class="g-s">${u}</span></button>`}_goes(e){let n=[],t=e.jour;e.equipement.soleil&&t?.soleil_kwh!=null&&n.push(this._go("soleil","sun","--nw-sun","Soleil \xB7 aujourd'hui",x(t.soleil_kwh),"kWh produits",t.soleil_garde!=null?`La maison en a gard\xE9 ${t.soleil_garde}\xA0%.`:t.soleil_kwh>0?"Une partie de la production n'a pas \xE9t\xE9 mesur\xE9e.":"Rien encore aujourd'hui."));let r=this._heatSum(e);r&&n.push(this._go("chauffage","flame","--nw-heat","Chauffage \xB7 depuis le 1er octobre",r.val,r.unit,r.say)),e.veille&&n.push(this._go("veille","moon","--nw-watch","Veille \xB7 chaque nuit",String(e.veille.w),"W quand tout dort",e.veille.euros_par_an!=null?`Environ ${we(e.veille.euros_par_an)}\xA0\u20AC par an.`:"Ce que tire la maison quand tout dort."));let a=e.eau,l=e.direct?.fuite?.minutes;a&&n.push(this._go("eau","drop","--nw-water","Eau \xB7 ce mois-ci",a.mois_euros!=null?Ze(a.mois_euros):$(a.mois_l,0),a.mois_euros!=null?"\u20AC":"litres",`${a.mois_euros!=null?`${$(a.mois_l,0)}\xA0litres. `:""}${l?`L'eau coule depuis ${Math.round(l)}\xA0min.`:"Pas de fuite."}`));let u=e.appareils_jour?.appareils?.[0];u&&n.push(this._go("appareils","plug","--nw-home","Appareils \xB7 aujourd'hui",x(u.kwh),`kWh \xB7 ${u.nom}`,"Celui qui a le plus consomm\xE9."));let p=e.pointe;p&&n.push(this._go("pointe","bolt","--nw-grid","Pointe \xB7 aujourd'hui",E(p.kw*1e3),"kW au plus fort",e.contrat?.kva?`Sur ${e.contrat.kva}\xA0kVA : ${p.part!=null&&p.part>=.7?"pr\xE8s de la limite":"de la marge"}.`:"L'heure la plus charg\xE9e."));let g=e.contrat;return g?.option==="hphc"&&g.part_hc!=null?n.push(this._go("contrat","doc","--nw-ok","Contrat \xB7 ce mois-ci",String(Math.round(g.part_hc*100)),Le(ie(e.heures_creuses))?"% la nuit":"% en heures creuses","de vos achats en heures creuses.")):g&&n.push(this._go("contrat","doc","--nw-ok","Contrat \xB7 ce mois-ci",g.option==="tempo"?"Tempo":g.option==="hphc"?"HP / HC":"Base",g.kva?` \xB7 ${g.kva}\xA0kVA`:"",g.option==="base"&&g.prix_base!=null?`${L(g.prix_base)}\xA0\u20AC le kWh \xE0 toute heure.`:"Vos prix et vos heures.")),n}_heatSum(e){let n=e.chauffage,t=n?.etat==="pret"?n.saison:null,r=n?.poele?.saison;return t?.eur!=null&&r?.eur!=null?{val:v(t.eur+r.eur),unit:"\u20AC",say:`Po\xEAle ${v(r.eur)}\xA0\u20AC, radiateurs ${v(t.eur)}\xA0\u20AC.`,both:!0}:r?{val:r.eur!=null?v(r.eur):$(r.kg,0),unit:r.eur!=null?"\u20AC":"kg",say:`Po\xEAle : ${$(r.kg,0)}\xA0kg de granul\xE9s.`,both:!1}:t?{val:t.eur!=null?v(t.eur):x(t.kwh),unit:t.eur!=null?"\u20AC":"kWh",say:"Radiateurs, estim\xE9s d'apr\xE8s le froid.",both:!1}:n?.etat==="peu_lie"?{val:"\u2014",unit:"",say:"Vous chauffez sans doute avec une autre \xE9nergie.",both:!1}:null}_usage(e){let n=e.usage,t=Le(ie(e.heures_creuses)),r=t?"la nuit":"en heures creuses",a=n.appareils.find(A=>A.type==="chauffe_eau"&&A.euros_an>=2),l=A=>Math.round(A*100),u=n.part_hc_chauffe_eau!=null&&a&&n.part_hc_chauffe_eau-n.part_hc>=.02?n.part_hc_chauffe_eau:null,p=e.contrat?.part_hc,g=i`<div class="u-gauge"><p class="u-k">Vos achats pris ${r}</p>
    <p class="u-v"><b>${l(n.part_hc)} %</b>${u!=null?i`<span>→ <b class="ok">${l(u)} %</b> avec le chauffe-eau ${r}</span>`:c}</p>
    <div class="track" style="--c:var(--nw-cold)">${u!=null?i`<i class="next" style="width:${u*100}%"></i>`:c}<i style="width:${n.part_hc*100}%"></i>
     ${n.seuil_hc!=null?i`<span class="mark" style="left:${Math.min(100,n.seuil_hc*100)}%"></span>`:c}</div>
    <div class="track-l"><span>sur 12 mois</span>${n.seuil_hc!=null?i`<span>rentable dès <b>${l(n.seuil_hc)} %</b></span>`:c}</div>
    ${p!=null&&Math.abs(p-n.part_hc)>=.05?i`<p class="u-n">Ce mois-ci : ${l(p)} %.${p<n.part_hc&&a?" En hiver, le chauffe-eau chauffe sans soleil, en heures pleines.":""}</p>`:c}</div>`,d=n.puissance,f=d?.plus_bas,h=d&&f?i`<p class="u-n u-kva">${f.jours_au_dessus===0&&f.euros_an!=null&&f.euros_an>=5?i`Puissance : <b>${f.kva} kVA suffiraient</b>, ${$(f.euros_an,0)} € de moins par an d'abonnement. Votre plus forte pointe : ${E(d.pointe_w)} kW.`:i`Puissance : <b>gardez ${d.kva} kVA</b>. La maison a dépassé ${f.kva} kW ${f.jours_au_dessus} jour${f.jours_au_dessus>1?"s":""} en 12 mois.`}</p>`:c,w=n.base_de_plus,b=a!=null&&w!=null&&w<0&&a.euros_an>-w,y=w==null?c:w>=0?i`<div class="u-verdict good"><p class="u-k">Votre option heures creuses</p><p class="u-big">C'est la bonne</p>
    <p class="u-n">En Base, ces 12 mois auraient coûté <b>${v(w)} € de plus</b>.${a?i` Avec le chauffe-eau ${r}, l'écart passerait à <b>${$(w+a.euros_an,0)} €</b>.`:""}</p>${h}</div>`:i`<div class="u-verdict"><p class="u-k">Votre option heures creuses</p><p class="u-big">${b?"Rentable, si\u2026":"La Base co\xFBterait moins"}</p>
    <p class="u-n">En Base, ces 12 mois auraient coûté <b>${v(-w)} € de moins</b>.${b?` Avec le chauffe-eau ${r}, les heures creuses redeviendraient rentables.`:""}</p>${h}</div>`,P=y===c?d&&f?i`<div class="u-verdict"><p class="u-k">Votre contrat</p>${h}</div>`:c:i`${y}`;return i`<div class="usage"><div class="u-top">${g}${P}</div></div>`}_machines(e){let n=e.usage;if(!n?.appareils.length)return c;let t=!!e.equipement.soleil,r=Le(ie(e.heures_creuses)),a=h=>Math.round(h*100),l=n.prix,u=i`${t&&l.soleil!=null?i`Au soleil, un kWh ne coûte que la revente perdue, <b>${L(l.soleil)} €</b> ; `:""}${r?"la nuit":"en heures creuses"}, <b>${L(l.hc)} €</b> ; en heures pleines, <b>${L(l.hp)} €</b>.`,p=i`<div class="mach">${n.appareils.map(h=>i`<span class="mn">${h.nom}<small>${x(h.kwh)} kWh par an</small></span>
    <span class="stack" role="img" aria-label="${t?`${a(h.soleil)}\xA0% au soleil, `:""}${a(h.nuit)} % ${r?"la nuit":"en heures creuses"}, ${a(h.pleines)} % en heures pleines">${t?i`<i style="width:${h.soleil*100}%;--c:var(--nw-sun)"></i>`:c}<i style="width:${h.nuit*100}%;--c:var(--nw-cold)"></i><i style="width:${h.pleines*100}%;--c:var(--nw-home)"></i></span>
    <span class="me">${h.euros_an>=1?i`<b>${$(h.euros_an,0)} €</b><small>par an</small>`:i`<small>rien à gagner</small>`}</span>`)}</div>
   <div class="nw-legend">${t?i`<span><i style="--c:var(--nw-sun)"></i>au soleil</span>`:c}<span><i style="--c:var(--nw-cold)"></i>${r?"la nuit":"en heures creuses"}</span><span><i style="--c:var(--nw-home)"></i>en heures pleines</span></div>`,g=n.soleil_mois.filter(h=>h.sur>=20),d="JFMAMJJASOND",f=t&&g.length>=6?this._enc("Du soleil en trop, mois par mois",`Les jours o\xF9 le soleil en trop suffit pour une machine. Les autres jours, Hestia dit d'attendre ${r?"la nuit":"les heures creuses"}, d'apr\xE8s la pr\xE9vision du jour.`,i`<div class="smonths">${g.map(h=>i`<span class="sm" title="${h.jours} jours sur ${h.sur}"><i style="height:${Math.max(4,h.jours/h.sur*100)}%"></i><small>${d[Number(h.mois.slice(5))-1]}</small></span>`)}</div>`,{wide:!0}):c;return i`${this._enc("Quand tournent vos machines",u,p,{wide:!0,aside:"12 derniers mois"})}${f}`}_saySave(e){return i`Pour économiser : ${e.titre.charAt(0).toLowerCase()+e.titre.slice(1)}, <b>${$(e.euros_an,0)} € ${e.unite??"par an"}</b>.`}_better(e){let n=p=>p.replace(/ ([:;!?%€])/g,"\xA0$1").replace(/(\d) (?=(W|kWh|h|centimes)(\s|$|[ .,:]))/g,"$1\xA0").replace(/ h (\d)/g,"\xA0h\xA0$1"),[t,r]=Wn[e.id]??["home","--nw-home"],a=e.rubrique&&ze.includes(e.rubrique)?e.rubrique:void 0,l=e.gain??e.euros_an,u=i`<span class="ico" style="--c:var(${r})">${T(t)}</span><span class="bt">${e.nom??e.titre}</span>
   <span class="bn"><small>Aujourd'hui</small>${n(e.maintenant)}${e.profil?this._hoursNow(e.profil):c}</span>
   <span class="ba" aria-hidden="true">→</span>
   <span class="bm"><small>Mieux</small>${n(e.mieux??"")}${e.mieux_heures?this._hoursBetter(e.mieux_heures):c}</span>
   ${l!=null?i`<span class="pe"><b>${$(l,0)} €</b><small>${n(e.sous??e.unite??"par an")}</small></span>`:c}`;return a?i`<button class="piste wide" style="--c:var(${r})" @click=${()=>{this._open=a}}>${u}</button>`:i`<div class="piste wide" style="--c:var(${r})">${u}</div>`}_hoursNow(e){let n=Math.max(...e.map(r=>r[0]+r[1]+r[2]),1e-9),t=["--nw-sun","--nw-cold","--nw-home"];return this._hours(e.map(r=>{let a=r[0]+r[1]+r[2];if(a<n*.08)return null;let l=r.indexOf(Math.max(...r));return[t[l],Math.max(.35,a/n)]}))}_hoursBetter(e){let n=Array(24).fill(null);for(let[t,r,a]of e)for(let l=t;l<r;l++)n[l%24]=[a==="soleil"?"--nw-sun":"--nw-cold",1];return this._hours(n)}_hours(e){return i`<span class="hrs" aria-hidden="true"><span class="hrs-b">${e.map(n=>n?i`<i style="--h:var(${n[0]});opacity:${n[1].toFixed(2)}"></i>`:i`<i></i>`)}</span>
   <span class="hrs-x"><span>0 h</span><span>6 h</span><span>12 h</span><span>18 h</span><span>24 h</span></span></span>`}_piste(e){let[n,t]=Wn[e.id]??["home","--nw-home"],r=e.rubrique&&ze.includes(e.rubrique)?e.rubrique:void 0,a=i`<span class="ico" style="--c:var(${t})">${T(n)}</span><span class="pt">${e.titre}</span><span class="pw">${e.pourquoi}</span>
   ${e.euros_an!=null?i`<span class="pe"><b>${$(e.euros_an,0)} €</b><small>${e.unite??"par an"}</small></span>`:c}`;return r?i`<button class="piste" style="--c:var(${t})" @click=${()=>{this._open=r}}>${a}</button>`:i`<div class="piste" style="--c:var(${t})">${a}</div>`}_ups(e){let n=[];return(e.contrat?.a_confirmer??[]).includes("option")&&n.push(["doc","Un conseil sur votre contrat ?","Dites votre option et vos heures creuses dans les R\xE9glages : Hestia vous dira si elles rapportent."]),e.equipement.direct?e.equipement.appareils||n.push(["plug","Savoir ce qui consomme","Une prise mesur\xE9e sur le frigo ou le chauffe-eau : la veille appareil par appareil, l\u2019appareil oubli\xE9."]):n.push(["bolt","Les gestes au bon moment","Un module sur la prise du Linky : heures creuses, disjoncteur, le prix de l\u2019heure."]),n.map(([t,r,a])=>i`<div class="piste up"><span class="ico">${T(t)}</span><span class="pt">${r}</span><span class="pw">${a}</span></div>`)}_advice(e){let n=e.pistes??[],t=n.filter(l=>l.unite==="par an").reduce((l,u)=>l+(u.euros_an??0),0),r=t>0?{val:$(t,0),unit:"\u20AC",cap:"par an \xE0 gagner, au plus"}:n.length?{val:String(n.length),cap:`conseil${n.length>1?"s":""} pour vous`}:{msg:"Rien \xE0 changer pour l\u2019instant"},a=n.length?`${n.length>1?`${n.length} conseils tir\xE9s`:"Un conseil tir\xE9"} de vos 12 derniers mois, du plus rentable au moins rentable.`:"Hestia regarde chaque jour vos habitudes et votre contrat ; un conseil appara\xEEtra ici d\xE8s qu\u2019il vaut la peine.";return i`<ha-card>${this._ans({ic:"home",c:"--nw-home",subject:"Pour \xE9conomiser",period:"\xE0 froid, en euros",...r,why:a,over:!1})}
   <div class="pistes">${n.map(l=>this._piste(l))}${this._ups(e)}</div></ha-card>
   ${this._open?i`<div class="ov" @click=${l=>{l.target===l.currentTarget&&(this._open=void 0)}}
    @keydown=${l=>{l.key==="Escape"&&(this._open=void 0)}}><ha-card class="sheet" role="dialog" aria-modal="true">${this._detail(e,this._open,!0)}</ha-card></div>`:c}`}_ans(e){return i`<div class="ans-k"><span class="ico" style="--c:var(${e.c})">${T(e.ic)}</span><span class="nw-title">${e.subject}</span><span class="per">${e.period}</span>
    ${e.pill?i`<span class="pastille" style="--c:var(${e.pill[1]})">${e.pill[0]}</span>`:c}
    ${e.over?i`<button class="d-close" aria-label="Fermer" @click=${()=>{this._open=void 0}}>×</button>`:c}</div>
   <div class="ans">${e.val!=null?i`<p class="hero"><b>${e.val}${e.unit?i`<small>${e.unit}</small>`:c}</b>${e.cap?i`<span>${e.cap}</span>`:c}</p>`:e.msg?i`<p class="ans-m">${e.msg}</p>`:c}${e.why?i`<p class="ans-w">${e.why}</p>`:c}</div>`}_enc(e,n,t,r={}){return i`<div class="nw-panel${r.wide?" wide":""}"><div class="nw-panel-head"><h3><span>${e}</span></h3>${r.aside?i`<span class="aside">${r.aside}</span>`:c}</div>
   ${n?i`<p class="say">${n}</p>`:c}${t??c}${r.foot?i`<div class="foot">${r.foot}</div>`:c}</div>`}_until(e){let n=e.jusqu_ici;return n?`aujourd'hui, jusqu'\xE0 ${H(new Date(n.jusqu_a).getHours())}`:"aujourd'hui"}_detail(e,n,t){switch(n){case"soleil":return this._sun(e,t);case"chauffage":return this._heat(e,t);case"veille":return this._night(e,t);case"eau":return this._water(e,t);case"appareils":return this._devices(e,t);case"pointe":return this._peak(e,t);default:return this._contract(e,t)}}_sun(e,n){let t=e.jour,r=e.soleil_jour,a={ic:"sun",c:"--nw-sun",subject:"Soleil",period:this._until(e),over:n};if(!e.equipement.soleil||t?.soleil_kwh==null)return this._ans({...a,period:"aujourd'hui",msg:"Pas de panneaux dans la page \xC9nergie",why:"Ajoutez leur production dans la page \xC9nergie de Home Assistant : Hestia la lira."});if(t.soleil_kwh<.05)return this._ans({...a,msg:"Les panneaux n'ont encore rien produit",why:"Le soleil arrive : cette carte se remplit au fil des heures."});let l=t.revendu_kwh??0,u=Math.max(0,t.soleil_kwh-l),p=r?.plus_fort,g=(e.heures?.aujourdhui??[]).map(w=>w.soleil),d=e.panneaux,f=r?.groupes??[],h=d?.onduleur_muet_min?i`L'onduleur ne répond plus depuis <b>${d.onduleur_muet_min<120?`${d.onduleur_muet_min}\xA0min`:`${Math.round(d.onduleur_muet_min/60)} h`}</b>.`:d?.en_retrait?.length?i`<b>${d.en_retrait[0].nom}</b> produit ${d.en_retrait[0].pourcent_de_moins} % de moins que d'habitude : à regarder.`:i`Les <b>${f.length} groupes</b> ont produit comme d'habitude : aucun ne faiblit.`;return i`${this._ans({...a,val:x(t.soleil_kwh),unit:"kWh",cap:"produits par les panneaux",why:t.soleil_garde!=null?i`La maison en a gardé <b>${t.soleil_garde} %</b>.${l>=.05?i` Le reste, ${x(l)} kWh, est parti au réseau${t.revendu_euros!=null?i` pour <b>${v(t.revendu_euros)} €</b>`:""}.`:""}`:c})}
   <div class="encs">
    ${this._enc("Heure par heure",p?i`Le soleil a donné le plus entre <b>${H(p.h)} et ${H(p.h+1)} : ${x(p.kwh)} kWh</b>. C'est à ces heures-là qu'une machine tourne au soleil.`:c,i`${qe(g,"--nw-sun",{pin:w=>`${x(w)}\xA0kWh`})}${nn}`,{wide:!0})}
    ${this._enc("O\xF9 est parti le soleil",r?.prix_evite!=null&&e.contrat?.revente!=null?i`Le garder vaut mieux que le vendre : il évite <b>${L(r.prix_evite)} €</b> le kWh, la revente n'en paie que <b>${L(e.contrat.revente)} €</b>.`:i`La maison en a gardé <b>${x(u)} kWh</b>.`,i`<div><div class="split"><i style="width:${u/t.soleil_kwh*100}%;--c:var(--nw-benefit)"></i><i style="width:${l/t.soleil_kwh*100}%;--c:var(--nw-sun)"></i></div>
      <div class="split-l"><span>gardé <b>${x(u)} kWh</b></span><span>vendu <b>${x(l)} kWh${t.revendu_euros!=null?` \xB7 ${v(t.revendu_euros)}\xA0\u20AC`:""}</b></span></div></div>`)}
    ${f.length?this._enc("Chaque groupe de panneaux",h,ve(Dn(f.map(w=>({n:w.nom,v:w.kwh,txt:`${x(w.kwh)}\xA0kWh`})),w=>`${x(w)}\xA0kWh`),"--nw-sun")):c}
   </div>`}_heat(e,n){let t=e.chauffage,r=t?.poele,a=r?.saison,l=t?.etat==="pret"?t.saison:null,u=this._heatSum(e),p={ic:"flame",c:"--nw-heat",subject:"Chauffage",period:"depuis le 1er octobre",over:n},g={sans_meteo:"Pour estimer les radiateurs, Hestia a besoin du froid de chaque jour : ajoutez Hestia M\xE9t\xE9o.",meteo_ancienne:"Pour estimer les radiateurs, Hestia a besoin du froid de chaque jour : mettez Hestia M\xE9t\xE9o \xE0 jour.",meteo_incompatible:"Hestia M\xE9t\xE9o n'a pas la m\xEAme version qu'\xC9nergie : mettez les deux \xE0 jour ensemble.",meteo_sans_lieu:"Pour estimer les radiateurs, ajoutez votre maison dans Hestia M\xE9t\xE9o.",meteo_sans_donnees:"Hestia M\xE9t\xE9o ne donne pas le froid des jours pass\xE9s : choisissez un capteur de temp\xE9rature dans ses r\xE9glages.",apprend:"Il faut quelques semaines de froid pour estimer les radiateurs. Revenez cet hiver.",peu_lie:"Votre \xE9lectricit\xE9 varie peu avec le froid : vous chauffez sans doute surtout avec une autre \xE9nergie."},d="Radiateurs : estim\xE9s en comparant chaque jour votre \xE9lectricit\xE9 au froid qu'il a fait.",f="",h="",w="",b;if(u?.both)f=u.val,h="\u20AC",w="pour se chauffer",b=i`Le poêle <b>${v(a.eur)} €</b> de granulés, les radiateurs électriques <b>environ ${v(l.eur)} €</b>.`;else if(a)[f,h,w]=a.eur!=null?[v(a.eur),"\u20AC","de granul\xE9s pour le po\xEAle"]:[$(a.kg,0),"kg","de granul\xE9s br\xFBl\xE9s"],b=i`${a.eur!=null?i`<b>${$(a.kg,0)} kg</b> de granulés. `:""}${l?i`Les radiateurs, <b>environ ${l.eur!=null?`${v(l.eur)}\xA0\u20AC`:`${x(l.kwh)}\xA0kWh`}</b>.`:g[t?.etat??""]??""}`;else if(l)[f,h,w]=l.eur!=null?[v(l.eur),"\u20AC","de radiateurs, environ"]:[x(l.kwh),"kWh","de radiateurs, environ"],b=d;else return this._ans({...p,msg:t?.etat==="peu_lie"?"Une autre \xE9nergie chauffe la maison":"Le chauffage n'est pas encore estim\xE9",why:g[t?.etat??""]??"Ajoutez Hestia M\xE9t\xE9o, ou le suivi de votre po\xEAle."});let y=u?.both&&l?.eur!=null&&a?.eur!=null?a.eur/(a.eur+l.eur):null,P=y==null?c:this._enc("Qui chauffe",y>=.4&&y<=.6?i`Le poêle et les radiateurs font <b>chacun la moitié</b> de la dépense.`:i`${y>.6?"Le po\xEAle fait":"Les radiateurs font"} <b>${Math.round((y>.6?y:1-y)*100)} %</b> de la dépense.`,ve([{n:"Po\xEAle",v:a.eur,txt:`${v(a.eur)}\xA0\u20AC`,sub:`${$(a.kg,0)}\xA0kg`},{n:"Radiateurs",v:l.eur,txt:`${v(l.eur)}\xA0\u20AC`,sub:`${x(l.kwh)}\xA0kWh`}],"--nw-heat"),{foot:d}),A=t?.euros_par_degre,j=A!=null&&l?this._enc("Le froid fait la facture",i`Chaque degré de froid en plus coûte <b>environ ${ae(A)} € par jour</b> de radiateurs.`,c,{foot:i`Exemple : un jour à 5 °C au lieu de 10 °C, <b>${v(A*5)} €</b> de plus.`}):c,_=r?.stock_kg,M=_!=null&&r?.sac_kg?Math.round(_/r.sac_kg*10)/10:null,z=_!=null&&a?this._enc("Granul\xE9s en stock",_<=0?i`<b>Plus de granulés</b> en stock.`:i`Il reste <b>${M!=null?`${$(M,1)} sac${M>1?"s":""} (${$(_,0)}\xA0kg)`:`${$(_,0)}\xA0kg`}</b>${r?.jours_restants!=null?i` : au rythme de cette saison, <b>environ ${r.jours_restants} jours</b> de poêle`:""}.`,i`<div><div class="track" style="--c:var(--nw-heat)"><i style="width:${a.kg+_>0?a.kg/(a.kg+_)*100:0}%"></i></div>
    <div class="track-l"><span>brûlés <b>${$(a.kg,0)} kg</b></span><span>en stock <b>${$(_,0)} kg</b></span></div></div>`):c;return i`${this._ans({...p,val:f,unit:h,cap:w,why:b})}<div class="encs">${P}${j}${z}</div>`}_night(e,n){let t=e.veille,r=e.veille_historique??[],a={ic:"moon",c:"--nw-watch",subject:"Veille",over:n};if(!t)return this._ans({...a,period:"les derni\xE8res nuits",msg:"La veille n'est pas encore connue",why:"Il faut deux semaines de nuits mesur\xE9es heure par heure."});let l=t.nuit,u=t.evolution,p=(l?.appareils??[]).map(h=>({n:h.nom,v:h.w,txt:`${h.w}\xA0W`,sub:h.euros_par_an!=null?`${we(h.euros_par_an)}\xA0\u20AC par an`:void 0}));l?.sans_prise_w&&p.push({n:"Sans prise mesur\xE9e",v:l.sans_prise_w,txt:`${l.sans_prise_w}\xA0W`,sub:l.sans_prise_euros_par_an!=null?`${we(l.sans_prise_euros_par_an)}\xA0\u20AC par an`:void 0,dash:!0}),p.sort((h,w)=>w.v-h.v);let g=l&&p.length?this._enc("Ce qui tourne la nuit",l.sans_prise_w?i`Les prises mesurées expliquent <b>${l.mesure_w} W</b>. Les <b>${l.sans_prise_w} W</b> qui restent viennent d'appareils sans prise mesurée : c'est là qu'il faut chercher.`:i`Les prises mesurées expliquent toute la veille : <b>${l.mesure_w} W</b>.`,ve(Dn(p,h=>`${Math.round(h)}\xA0W`),"--nw-watch"),{wide:!0,aside:"au plus calme de la nuit"}):c,d=u?Vn(u.debut):"",f=r.length>1?this._enc("Nuit apr\xE8s nuit",u&&Math.abs(u.ecart_w)>=10?i`Elle est passée de <b>${u.debut_w} W à ${t.w} W</b> depuis le ${d}${u.ecart_euros_par_an!=null?i` : <b>environ ${we(Math.abs(u.ecart_euros_par_an))} € par an</b> de ${u.ecart_w<0?"moins":"plus"}`:""}.`:i`Elle reste autour de <b>${t.w} W</b> depuis le ${d}.`,i`${qe(r.map(h=>h.w),"--nw-watch",{pin:h=>`${h}\xA0W`,max:Math.max(...r.map(h=>h.w))*1.09})}<div class="ticks"><span>${Bn(r[0].jour)} ${wt[He(r[0].jour).getMonth()]}</span><span>cette nuit</span></div>`,{wide:!0}):c;return i`${this._ans({...a,period:`les ${r.length>1?r.length:t.nuits} derni\xE8res nuits`,val:String(t.w),unit:"W",cap:"quand tout dort",why:t.euros_par_an!=null?i`La maison les tire jour et nuit, même sans rien allumer : <b>environ ${we(t.euros_par_an)} € par an</b>.`:"Ce fond tourne jour et nuit, m\xEAme sans rien allumer."})}
   <div class="encs">${g}${f}</div>`}_water(e,n){let t=e.eau,r=new Date,a=e.direct?.fuite?.minutes,l={ic:"drop",c:"--nw-water",subject:"Eau",over:n};if(!t)return this._ans({...l,period:"ce mois-ci",msg:"Pas de compteur d'eau",why:"Ajoutez-le dans la page \xC9nergie de Home Assistant : Hestia le lira."});let u=t.jours??[],p=Pe[r.getMonth()],g=a?[`L'eau coule depuis ${Math.round(a)}\xA0min`,a>=60?"--nw-alert":"--nw-act"]:["Pas de fuite","--nw-ok"],d=t.plus_gros,f=u.map((h,w)=>w===u.length-1?"auj.":u.length<=12||[0,7,14,21,28].includes(w)?String(He(h.jour).getDate()):"");return i`${this._ans({...l,period:`${p}, du 1er au ${r.getDate()}`,pill:g,val:$(t.mois_l,0),unit:"litres",cap:t.mois_euros!=null?i`soit <b>${Ze(t.mois_euros)} €</b>`:c,why:i`${t.l_par_jour!=null?i`Environ <b>${$(t.l_par_jour,0)} litres par jour</b>. `:""}${t.prix_m3!=null?i`L'eau coûte ${L(t.prix_m3)} € le m³, soit <b>${L(t.euros_100_l)} € les 100 litres</b>.`:""}`})}
   ${u.length?i`<div class="encs">${this._enc("Jour par jour",d?i`Le plus gros jour : <b>le ${Vn(d.jour)}, ${$(d.l,0)} litres</b>${d.euros!=null?`, soit ${v(d.euros)}\xA0\u20AC`:""}. Un jour qui sort du lot se voit tout de suite.`:c,i`${qe(u.map(h=>h.l),"--nw-water",{pin:h=>`${$(h,0)}\xA0L`,part:u.length-1})}<div class="ticks days">${f.map(h=>i`<span>${h}</span>`)}</div>`,{wide:!0})}</div>`:c}`}_devices(e,n){let t=e.appareils_jour,r=e.direct?.en_marche??[],a={ic:"plug",c:"--nw-home",subject:"Appareils",period:this._until(e),over:n};if(!t||!t.appareils.length)return this._ans({...a,msg:"Aucun appareil mesur\xE9",why:"Ajoutez vos prises mesur\xE9es dans la page \xC9nergie de Home Assistant (consommation individuelle)."});let l=new Map(r.map(b=>[b.nom,b.w])),u=t.appareils[0],p=t.appareils.map(b=>({n:b.nom,v:b.kwh,txt:`${x(b.kwh)}\xA0kWh`,sub:b.euros!=null?`${v(b.euros)}\xA0\u20AC`:void 0,live:l.has(b.nom)?`${E(l.get(b.nom))}\xA0kW`:void 0}));for(let b of r)p.some(y=>y.n===b.nom)||p.push({n:b.nom,v:0,txt:"0 kWh",live:`${E(b.w)}\xA0kW`});let g=p.filter((b,y)=>y<5||b.live),d=p.filter(b=>!g.includes(b)),f=d.reduce((b,y)=>b+y.v,0),h=d.length>1?"s":"",w=d.length||t.sans_prise_kwh?i`${d.length?i`Et ${d.length} autre${h} appareil${h} mesuré${h} : <b>${x(f)} kWh</b>. `:""}${t.sans_prise_kwh?i`Les ${x(t.sans_prise_kwh)} kWh restants viennent d'appareils sans prise mesurée.`:""}`:c;return i`${this._ans({...a,val:x(u.kwh),unit:"kWh",cap:i`<b>${u.nom}</b>, le plus gros`,why:i`Les appareils mesurés font <b>${x(t.mesure_kwh)} kWh</b> sur les ${x(t.maison_kwh)} kWh de la maison.`})}
   <div class="encs">${this._enc("Appareil par appareil",u.euros!=null?i`Ce que chacun a coûté depuis minuit, soleil déduit : ${u.nom} <b>${v(u.euros)} €</b>.`:"Ce que chacun a consomm\xE9 depuis minuit.",ve(g,"--nw-home"),{wide:!0,aside:r.length?i`<span class="live">en marche</span>`:c,foot:w})}</div>`}_peak(e,n){let t=e.pointe,r=e.contrat?.kva,a=(e.heures?.aujourdhui??[]).map(f=>f.achat),l={ic:"bolt",c:"--nw-grid",subject:"Pointe",period:"aujourd'hui",over:n};if(!t)return this._ans({...l,msg:"Pas encore d'heure mesur\xE9e aujourd'hui",why:"La pointe se lit heure par heure : il faut le compteur heure par heure."});let u=t.part!=null&&t.part>=.7,p=ie(e.heures_creuses),g=f=>p.some(([h,w])=>f*60+30>=h&&f*60+30<w),d=t.part==null?"":t.part<.5?"vous en \xEAtes loin":t.part<.8?"il reste de la marge":"vous en \xEAtes tout pr\xE8s";return i`${this._ans({...l,pill:r?u?["Pr\xE8s de la limite","--nw-act"]:["De la marge","--nw-ok"]:void 0,val:E(t.kw*1e3),unit:"kW",cap:`pris au r\xE9seau entre ${H(t.h)} et ${H(t.h+1)}`,why:i`${r?i` Le compteur coupe au-delà de <b>${r} kVA</b> (environ ${r} kW) : ${d}.`:"L'heure la plus charg\xE9e de la journ\xE9e."}`})}
   <div class="encs">${this._enc("Heure par heure",t.part!=null?i`La barre la plus haute reste à <b>${Un(t.part)} de la limite</b> : ${u?"deux gros appareils de plus pourraient faire couper le compteur":"rien ne risque de faire couper le compteur"}.`:c,i`${qe(a,"--nw-grid",{pin:f=>`${E(f*1e3)}\xA0kW`,bands:p.length?g:void 0,tall:!0,...r?{max:r*1.07,limit:r,limitLabel:`limite ${r}\xA0kVA`}:{}})}${nn}
     <div class="nw-legend"><span><i style="--c:var(--nw-grid)"></i>pris au réseau, en moyenne sur l'heure</span>${p.length?i`<span><i style="--c:color-mix(in oklab, var(--nw-cold) 40%, transparent)"></i>heures creuses</span>`:c}</div>`,{wide:!0})}</div>`}_contract(e,n){let t=e.contrat,r=new Date,a={ic:"doc",c:"--nw-ok",subject:"Contrat",period:"ce mois-ci",over:n},l=ie(e.heures_creuses),u=Le(l),p=t?.a_confirmer??[],g=i`${t?.kva?`Puissance : ${t.kva}\xA0kVA${p.includes("kva")?" (suppos\xE9e)":""}.`:""}${p.length?i` <a class="to-hub" href="/hestia/energie/reglages" @click=${ft}>${p.includes("option")?p.length>1?"Option et puissance":"Option":"Puissance"} à confirmer dans les Réglages ›</a>`:c}`,d=[...t?.option==="hphc"?[["Heures pleines",t.prix_hp,"le kWh"],["Heures creuses",t.prix_hc,"le kWh"]]:t?.option==="base"?[["Le kWh",t.prix_base,"\xE0 toute heure"]]:[],[`Abonnement${t?.kva?` ${t.kva}\xA0kVA`:""}`,t?.abonnement_mois,"par mois"],["Revente du soleil",t?.revente,"le kWh"]],f=this._enc("Vos prix",t?.abonnement_mois!=null?i`L'abonnement, <b>${v(t.abonnement_mois)} € par mois</b>, se paie même sans rien consommer.`:c,i`<div class="hb list">${d.filter(C=>C[1]!=null).map(([C,W,Z])=>i`<span class="n">${C}</span><span class="v">${Z==="par mois"?v(W):L(W)} €<small>${Z}</small></span>`)}</div>`);if(t?.option!=="hphc"){let C=t?.option==="base";return i`${this._ans({...a,...C&&t?.prix_base!=null?{val:L(t.prix_base),unit:"\u20AC",cap:`le kWh \xE0 toute heure, option Base${p.includes("option")?" (suppos\xE9e)":""}`}:{msg:`Option ${t?.option==="tempo"?"Tempo":"Base"}`},why:g})}
    <div class="encs">${f}</div>`}let h=e.heures_creuses?.length?e.heures_creuses.map(([C,W])=>`${X(C)} \xE0 ${X(W)}`).join(" et de "):null,w=r.getHours()*60+r.getMinutes(),b=t.prix_hp&&t.prix_hc?1-t.prix_hc/t.prix_hp:null,y=t.part_hc,P=t.seuil_hc,A=e.mois?.euros,j=t.base_euros!=null&&A!=null?t.base_euros-A:null,_=e.usage,M=_&&_.seuil_hc!=null?this._enc("Les heures creuses rapportent-elles ?",i`Sur 12 mois, <b>${Math.round(_.part_hc*100)} %</b> de vos achats sont tombés ${u?"la nuit":"en heures creuses"}${y!=null?` (ce mois-ci ${Math.round(y*100)} %)`:""}. Elles rapportent à partir de <b>${Math.round(_.seuil_hc*100)} %</b>${_.base_de_plus!=null?i` : en Base, vous auriez payé <b>${v(Math.abs(_.base_de_plus))} € de ${_.base_de_plus>=0?"plus":"moins"}</b>`:""}.`,i`<div><div class="track" style="--c:var(--nw-cold)"><i style="width:${_.part_hc*100}%"></i><span class="mark" style="left:${Math.min(100,_.seuil_hc*100)}%"></span></div>
    <div class="track-l"><span>vous <b>${Math.round(_.part_hc*100)} %</b></span><span>rentable dès <b>${Math.round(_.seuil_hc*100)} %</b></span></div></div>`):y!=null&&P!=null?this._enc("Les heures creuses rapportent-elles ?",i`Ce mois-ci, <b>${Math.round(y*100)} %</b> de vos achats sont tombés ${u?"la nuit":"en heures creuses"}. Elles rapportent à partir de <b>${Math.round(P*100)} %</b>${j!=null?i` : sans elles (option Base), vous auriez payé <b>${v(Math.abs(j))} € de ${j<0?"moins":"plus"}</b>`:""}.`,i`<div><div class="track" style="--c:var(--nw-cold)"><i style="width:${y*100}%"></i><span class="mark" style="left:${Math.min(100,P*100)}%"></span></div>
    <div class="track-l"><span>vous <b>${Math.round(y*100)} %</b></span><span>rentable dès <b>${Math.round(P*100)} %</b></span></div></div>`):c,z=e.heures_creuses?.[0];return i`${this._ans({...a,...z?{val:`${X(z[0])} \u2013 ${X(z[1])}`,cap:e.heures_creuses.length>1?`heures creuses, et de ${e.heures_creuses.slice(1).map(([C,W])=>`${X(C)} \xE0 ${X(W)}`).join(", ")}`:"les heures creuses"}:{msg:"Heures pleines et heures creuses"},why:i`${t.prix_hc!=null&&t.prix_hp!=null?i`${u?"La nuit":"En heures creuses"}, le kWh coûte <b>${L(t.prix_hc)} €</b> au lieu de <b>${L(t.prix_hp)} €</b>${u?" le jour":""}. `:""}${g}`})}
   <div class="encs">
    ${l.length?this._enc("Votre journ\xE9e",b!=null?i`En bleu, les heures creuses : tout ce qui peut attendre y coûte <b>${Un(b)} de moins</b>.`:"En bleu, les heures creuses.",i`<div><div class="day">${l.map(([C,W])=>i`<i style="left:${C/14.4}%;width:${(W-C)/14.4}%"></i>`)}<span class="now" style="left:${w/14.4}%"></span></div>${nn}</div>`,{wide:!0,aside:`il est ${be(r)}`}):c}
    ${f}${M}${this._machines(e)}
   </div>`}};customElements.get("hestia-energy-card")||customElements.define("hestia-energy-card",sn);var We=window;We.customCards=We.customCards??[];We.customCards.some(o=>o.type==="hestia-energy-card")||We.customCards.push({type:"hestia-energy-card",name:"Hestia \xC9nergie",description:"Le conseiller \xE9nergie de la maison : tuile, carte compl\xE8te, cartes de d\xE9tail.",preview:!0});})();
