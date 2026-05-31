/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-06-16 10:30:48 
 */
import{ah as c,ai as p,ak as u,d as i,ap as f,Z as v,c as s,f as a,p as m,D as o,u as r,a4 as y,n as S,aH as _}from"./index-DUFSe6Gb.js";const h=c({direction:{type:String,values:["horizontal","vertical"],default:"horizontal"},contentPosition:{type:String,values:["left","center","right"],default:"center"},borderStyle:{type:p(String),default:"solid"}}),b=i({name:"ElDivider"}),P=i({...b,props:h,setup(n){const l=n,e=f("divider"),d=v(()=>e.cssVar({"border-style":l.borderStyle}));return(t,k)=>(a(),s("div",{class:o([r(e).b(),r(e).m(t.direction)]),style:S(r(d)),role:"separator"},[t.$slots.default&&t.direction!=="vertical"?(a(),s("div",{key:0,class:o([r(e).e("text"),r(e).is(t.contentPosition)])},[y(t.$slots,"default")],2)):m("v-if",!0)],6))}});var g=u(P,[["__file","divider.vue"]]);const D=_(g);export{D as E};
