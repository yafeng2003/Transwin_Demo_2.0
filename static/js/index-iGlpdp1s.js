/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-15 13:02:45 
 */
import{bc as r}from"./index-BZplGa9b.js";const u=100,v=600,m={beforeMount(l,s){const e=s.value,{interval:c=u,delay:i=v}=r(e)?{}:e;let t,n;const o=()=>r(e)?e():e.handler(),a=()=>{n&&(clearTimeout(n),n=void 0),t&&(clearInterval(t),t=void 0)};l.addEventListener("mousedown",d=>{d.button===0&&(a(),o(),document.addEventListener("mouseup",()=>a(),{once:!0}),n=setTimeout(()=>{t=setInterval(()=>{o()},c)},i))})}};export{m as v};
