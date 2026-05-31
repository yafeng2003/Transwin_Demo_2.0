/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-15 13:02:45 
 */
System.register(["./index-legacy-Cqstv5ZE.js"],(function(e,t){"use strict";var n;return{setters:[e=>{n=e.bc}],execute:function(){const t=100,o=600;e("v",{beforeMount(e,r){const s=r.value,{interval:u=t,delay:c=o}=n(s)?{}:s;let a,i;const d=()=>n(s)?s():s.handler(),l=()=>{i&&(clearTimeout(i),i=void 0),a&&(clearInterval(a),a=void 0)};e.addEventListener("mousedown",(e=>{0===e.button&&(l(),d(),document.addEventListener("mouseup",(()=>l()),{once:!0}),i=setTimeout((()=>{a=setInterval((()=>{d()}),u)}),c))}))}})}}}));
