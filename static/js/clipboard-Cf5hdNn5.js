/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-15 13:02:45 
 */
import{ff as a,fg as c,fh as e}from"./index-BZplGa9b.js";const i=s=>{e.$baseMessage("拷贝".concat(s,"成功"),"success","hey")},p=s=>{e.$baseMessage("拷贝".concat(s,"失败"),"error","hey")},d=s=>{const{isSupported:r,copy:o}=a({legacy:!0});r||c("clipboard-write"),o(s).then(()=>{i(s)}).catch(()=>{p(s)})};export{d as h};
