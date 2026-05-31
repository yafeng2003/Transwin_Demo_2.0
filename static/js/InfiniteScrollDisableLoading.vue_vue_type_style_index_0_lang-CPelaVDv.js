/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-06-16 10:30:48 
 */
import{E as f}from"./index-B66_9Ul5.js";import{d as p,r as l,Z as r,c as e,f as t,aY as m,p as c,u as o,F as v,C as h,B as k}from"./index-DUFSe6Gb.js";const y={class:"infinite-list-wrapper",style:{overflow:"auto"}},b=["infinite-scroll-disabled"],g={key:0},w={key:1},x=p({__name:"InfiniteScrollDisableLoading",setup(B){const i=l(10),s=l(!1),n=r(()=>i.value>=20),u=r(()=>s.value||n.value),d=()=>{s.value=!0,setTimeout(()=>{i.value+=2,s.value=!1},1e3*2)};return(C,D)=>{const _=f;return t(),e("div",y,[m((t(),e("ul",{class:"list","infinite-scroll-disabled":o(u)},[(t(!0),e(v,null,h(o(i),a=>(t(),e("li",{key:a,class:"list-item"},k(a),1))),128))],8,b)),[[_,d]]),o(s)?(t(),e("p",g,"加载中...")):c("",!0),o(n)?(t(),e("p",w,"没有更多了")):c("",!0)])}}});export{x as _};
