/*!  build: Vue Shop Vite 
     copyright: https://vuejs-core.cn/shop-vite   
     time: 2025-08-15 13:02:45 
 */
import{P as i}from"./index.min-CG5AiEXt.js";import{d as s,r as c,j as l,o as u,be as f,c as d,f as p}from"./index-BZplGa9b.js";const m=["id"],P=s({name:"VabPlayer",__name:"index",props:{config:{type:Object,default:()=>({id:"mse",url:""})}},emits:["player"],setup(n,{emit:a}){const o=n,e=c(null),r=a,t=()=>{o.config.url&&o.config.url!==""&&(e.value=new i(o.config),r("player",e.value))};return l(o.config,()=>{t()},{deep:!0}),u(()=>{t()}),f(()=>{e.value&&typeof e.value.destroy=="function"&&e.value.destroy()}),(y,_)=>(p(),d("div",{id:n.config.id},null,8,m))}});export{P as _};
