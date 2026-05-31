/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-15 13:02:45 
 */
import{al as c,am as p,ao as u,d as i,at as f,a3 as v,c as s,f as a,p as m,M as o,u as r,a8 as y,n as S,aK as _}from"./index-BZplGa9b.js";const b=c({direction:{type:String,values:["horizontal","vertical"],default:"horizontal"},contentPosition:{type:String,values:["left","center","right"],default:"center"},borderStyle:{type:p(String),default:"solid"}}),h=i({name:"ElDivider"}),P=i({...h,props:b,setup(n){const l=n,e=f("divider"),d=v(()=>e.cssVar({"border-style":l.borderStyle}));return(t,z)=>(a(),s("div",{class:o([r(e).b(),r(e).m(t.direction)]),style:S(r(d)),role:"separator"},[t.$slots.default&&t.direction!=="vertical"?(a(),s("div",{key:0,class:o([r(e).e("text"),r(e).is(t.contentPosition)])},[y(t.$slots,"default")],2)):m("v-if",!0)],6))}});var g=u(P,[["__file","divider.vue"]]);const k=_(g);export{k as E};
