# UI component catalog

All take `(parent, options)`; `x,y,w,h` absolute in px (omit for flow layout); `t0` = absolute start time; every component returns `{el, at(t)}` (+ `body` for containers). Add to a scene with `S.add(...)`.

| component | options → returns |
|---|---|
| `UI.window` | `{x,y,w,h,title,kind:'mac'|'win'|'flat',t0,enter}` → `{el, body, bar}` |
| `UI.browser` | `{x,y,w,h,url,t0}` → `{el, body}` (traffic lights + address pill) |
| `UI.phone` | `{x,y,w,h,radius,notch,t0}` → `{el, body}` (screen = body, 1080×1920 content must be scaled or authored at screen size) |
| `UI.card` | `{x,y,w,h,html,t0}` → `{el, body}` surface with border/shadow |
| `UI.typing` | `UI.typing(el, text, t0, cps, {caret})` → typewriter with blinking caret |
| `UI.input` | `{x,y,w,h,placeholder,text,t0,tType,cps,icon}` → field that shows placeholder, then types |
| `UI.button` | `{x,y,w,h,label,icon,ghost,t0,press,pressedLabel}` → press scale+glow at time `press` |
| `UI.badge` | `{x,y,label,tone:'good'|'bad'|'warn'|'accent',t0}` |
| `UI.avatars` | `{x,y,n,size,names,hues,t0}` overlapping initials |
| `UI.chat` | `{x,y,w,h,messages:[{who:'user'|'ai',text,t,cps,think}]}` bubbles, typing dots, streaming AI text |
| `UI.list` | `{x,y,w,items:[{icon,title,sub,right}],t0,stagger,select:{t,i}}` |
| `UI.table` | `{x,y,w,cols,rows,t0,highlight:{t,i}}` |
| `UI.sidebar` | `{x,y,w,h,items:[{icon,label}],active:[{t,i}],t0}` |
| `UI.tabs` | `{x,y,items,sel:[{t,i}],t0}` sliding indicator |
| `UI.toggle` | `{x,y,at,t0}` springs on at time `at` |
| `UI.kpi` | `{x,y,w,label,from,to,prefix,suffix,decimals,delta,size,t0,dur}` counts up |
| `UI.barChart` | `{x,y,w,h,data,labels,hi,max,t0}` springy bars |
| `UI.lineChart` | `{x,y,w,h,data,min,max,t0,dur}` self-drawing line + area + travelling dot |
| `UI.donut` | `{x,y,size,value,t0,dur}` |
| `UI.progress` | `{x,y,w,h,t0,dur,ease}` |
| `UI.skeleton` | `{x,y,w,h,t0,t1}` shimmer placeholder |
| `UI.toast` | `{x,y,w,title,sub,icon,tone,t0,dur}` slide-in/out |
| `UI.modal` | `{x,y,w,title,body,t0,t1,sw,sh}` scrim + pop |
| `UI.palette` | `{x,y,w,query,items:[{icon,label,key}],t0,t1,select,selectT,cps}` command palette that types and filters |
| `UI.code` | `{x,y,w,h,lines,t0,cps,size}` typed code with syntax colours |
| `UI.notifications` | `{x,y,w,gap,items:[toast opts]}` stack |
| `UI.pages` | `UI.pages([el,…],[{t,i}],{kind:'slide'|'fade'|'rise',dur})` route change |
| `UI.cursor` | `UI.cursor(parent, keys:[{t,x,y,click?,ease?}], {arc,travel,scale,fill})` |
| `UI.camera` | `UI.camera(stage,{w,h,persp,keys:[{t,x,y,zoom,rot,rx,ry,ease}]})` → `.at(t, {x,y,r})` |

**Icons:** `UI.icon(name,size,color,strokeWidth)` → SVG string. Names: check, x, plus, search, bell, user, home, chart, settings, send, spark, file, folder, arrow, cloud, lock, star, play, heart, mail, calendar, bolt, dots, menu, clock, trend, code, globe, image, mic, link.

**Themes:** `UI.theme(name|tokens, overrides)` → tokens: bg, surface, surface2, border, text, muted, accent, accent2, good, bad, warn, radius, shadow, font, mono.
