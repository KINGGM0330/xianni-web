# -*- coding: utf-8 -*-
"""
官網「真渲染」測試：載入 assets/*.js 的真資料，再跑 index.html 的內嵌 script，
然後對導覽列每一個 data-s 呼叫 go()，檢查沒有例外、而且有渲染出東西。
（skill 的 verify_bigfile.py 對這份新版官網已經失效 —— DB 搬到 assets\game-data.js，
  它的 harness 沒載入那些檔，所以原檔跑它也會噴同一個 TypeError。）
"""
import re, sys, json, subprocess, os
A = '/mnt/user-data/uploads/KINGGM/仙逆天堂官網/assets'
html = open(sys.argv[1], encoding='utf-8').read()
navs = re.findall(r'<a data-s="([^"]+)"', html)
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.S)
inline = [s for s in scripts if s.strip()]
shim = r'''
const _mk=()=>({innerHTML:'',style:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},
  dataset:{},children:[],appendChild(){},addEventListener(){},setAttribute(){},getAttribute(){return null},
  querySelector(){return _mk()},querySelectorAll(){return []},focus(){},blur(){},remove(){},scrollIntoView(){},
  getContext(){return new Proxy({},{get:(o,k)=>{ if(k==='canvas')return _mk(); if(k in o)return o[k]; return (typeof k==='string'&&/^(fillStyle|strokeStyle|lineWidth|globalAlpha|font|shadowBlur|shadowColor|textAlign|textBaseline|lineCap|lineJoin|globalCompositeOperation|filter|miterLimit)$/.test(k))?'':function(){return {addColorStop(){},width:0}}; }, set:()=>true})},
  width:0,height:0,value:'',checked:false,offsetWidth:0,offsetHeight:0,textContent:'',
  getBoundingClientRect(){return {width:1280,height:800,top:0,left:0,right:1280,bottom:800,x:0,y:0}},
  insertAdjacentHTML(){},closest(){return null},contains(){return false},parentNode:null,offsetTop:0,offsetLeft:0,scrollTop:0,scrollHeight:0,clientWidth:1280,clientHeight:800});
global.window=global; global.self=global;
const _cache={}; const _byId=(id)=>(_cache[id]||(_cache[id]=_mk()));
global.__byId=_byId;
global.document={ getElementById:_byId, querySelector:()=>_mk(), querySelectorAll:()=>[],
  createElement:()=>_mk(), addEventListener(){}, body:_mk(), documentElement:_mk(),
  head:_mk(), location:{hash:''}, readyState:'complete', title:'' };
global.location={hash:'',href:'',search:'',replace(){},assign(){}};
global.history={replaceState(s,ti,u){ global.location.hash=u; },pushState(){}};
global.navigator={userAgent:'node',clipboard:{writeText(){return Promise.resolve()}}};
global.localStorage={getItem:()=>null,setItem(){},removeItem(){}};
global.addEventListener=()=>{}; global.removeEventListener=()=>{};
global.requestAnimationFrame=()=>0; global.cancelAnimationFrame=()=>{};
global.setTimeout=(f)=>0; global.setInterval=()=>0; global.clearInterval=()=>{};
global.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
global.fetch=()=>Promise.resolve({json:()=>Promise.resolve({}),text:()=>Promise.resolve('')});
global.alert=()=>{}; global.scrollTo=()=>{};
global.innerWidth=1280; global.innerHeight=800;
global.devicePixelRatio=1;
global.Image=function(){return _mk()};
global.getComputedStyle=()=>({getPropertyValue:()=>''});
'''
data = ''.join(open(os.path.join(A,f), encoding='utf-8').read()+'\n;\n'
               for f in ['game-data.js','news.js','rank.js','upgrade.js'])
js = shim + '\n' + data + '\n' + '\n;\n'.join(inline) + f'''
const NAV = {navs};
let bad=[], empty=[], fell=[];
const app = __byId('app');
for (const k of NAV.concat(['event'])) {{
  try {{
    __go(k);
    const out = app.innerHTML || '';
    const landed = location.hash.replace('#','');
    if (landed !== k) {{ fell.push(k+' -> '+landed); console.log('  ' + k + ' -> 退回 ' + landed + '（' + out.length + ' 字元）'); }}
    else if (out.length < 40) empty.push(k);
    else console.log('  ' + k + ' -> 渲染 ' + out.length + ' 字元 OK');
  }} catch(e) {{ bad.push(k+': '+e.message); }}
}}
console.log('__FELL__=' + JSON.stringify(fell));
console.log('__BAD__=' + JSON.stringify(bad));
console.log('__EMPTY__=' + JSON.stringify(empty));
'''
open('/tmp/rt.js','w',encoding='utf-8').write(js)
p = subprocess.run(['node','/tmp/rt.js'], capture_output=True, text=True)
print(p.stdout[-4000:])
if p.returncode != 0:
    print('node 失敗:\n', p.stderr[-2500:]); sys.exit(1)
bad = json.loads(re.search(r'__BAD__=(.*)', p.stdout).group(1))
emp = json.loads(re.search(r'__EMPTY__=(.*)', p.stdout).group(1))
fell = json.loads(re.search(r'__FELL__=(.*)', p.stdout).group(1))
print('\n退回 home 的:', fell or '無')
print('丟例外的:', bad or '無')
print('渲染空白的:', emp or '無')
sys.exit(0 if not bad and not emp else 1)
