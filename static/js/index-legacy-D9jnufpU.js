/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-22 10:57:39 
 */
System.register(["./index-legacy-uOaXdKfA.js"],(function(e,t){"use strict";var n;return{setters:[e=>{n=e.ba}],execute:function(){const t=100,o=600;e("v",{beforeMount(e,r){const s=r.value,{interval:u=t,delay:a=o}=n(s)?{}:s;let c,i;const d=()=>n(s)?s():s.handler(),l=()=>{i&&(clearTimeout(i),i=void 0),c&&(clearInterval(c),c=void 0)};e.addEventListener("mousedown",(e=>{0===e.button&&(l(),d(),document.addEventListener("mouseup",(()=>l()),{once:!0}),i=setTimeout((()=>{c=setInterval((()=>{d()}),u)}),a))}))}})}}}));
