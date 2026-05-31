/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-22 10:57:39 
 */
import{E as f}from"./index-CYwmiXF5.js";import{d as p,r as l,W as r,c as e,f as t,aV as m,p as c,u as o,L as v,M as h,O as k}from"./index-C5ztgtHd.js";const y={class:"infinite-list-wrapper",style:{overflow:"auto"}},b=["infinite-scroll-disabled"],g={key:0},w={key:1},B=p({__name:"InfiniteScrollDisableLoading",setup(D){const i=l(10),s=l(!1),n=r(()=>i.value>=20),u=r(()=>s.value||n.value),d=()=>{s.value=!0,setTimeout(()=>{i.value+=2,s.value=!1},1e3*2)};return(E,L)=>{const _=f;return t(),e("div",y,[m((t(),e("ul",{class:"list","infinite-scroll-disabled":o(u)},[(t(!0),e(v,null,h(o(i),a=>(t(),e("li",{key:a,class:"list-item"},k(a),1))),128))],8,b)),[[_,d]]),o(s)?(t(),e("p",g,"加载中...")):c("",!0),o(n)?(t(),e("p",w,"没有更多了")):c("",!0)])}}});export{B as _};
