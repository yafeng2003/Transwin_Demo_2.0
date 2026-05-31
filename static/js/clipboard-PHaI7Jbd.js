/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-22 11:26:35 
 */
import{fj as a,fk as c,fl as e}from"./index-1-YBapYP.js";const i=s=>{e.$baseMessage("拷贝".concat(s,"成功"),"success","hey")},p=s=>{e.$baseMessage("拷贝".concat(s,"失败"),"error","hey")},b=s=>{const{isSupported:r,copy:o}=a({legacy:!0});r||c("clipboard-write"),o(s).then(()=>{i(s)}).catch(()=>{p(s)})};export{b as h};
