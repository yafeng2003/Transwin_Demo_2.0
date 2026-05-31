/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-22 11:26:35 
 */
import{ae as c,af as p,ah as u,d as i,am as f,W as v,c as s,f as a,p as m,N as o,u as r,a1 as y,n as S,aE as _}from"./index-1-YBapYP.js";const h=c({direction:{type:String,values:["horizontal","vertical"],default:"horizontal"},contentPosition:{type:String,values:["left","center","right"],default:"center"},borderStyle:{type:p(String),default:"solid"}}),b=i({name:"ElDivider"}),E=i({...b,props:h,setup(n){const l=n,e=f("divider"),d=v(()=>e.cssVar({"border-style":l.borderStyle}));return(t,g)=>(a(),s("div",{class:o([r(e).b(),r(e).m(t.direction)]),style:S(r(d)),role:"separator"},[t.$slots.default&&t.direction!=="vertical"?(a(),s("div",{key:0,class:o([r(e).e("text"),r(e).is(t.contentPosition)])},[y(t.$slots,"default")],2)):m("v-if",!0)],6))}});var P=u(E,[["__file","divider.vue"]]);const k=_(P);export{k as E};
