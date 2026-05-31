<template>
  <div class="chart-container">
    <h3 class="chart-title">{{ currentTitle }}</h3>
    <vab-chart :option="option" />
  </div>
</template>

<script lang="ts" setup>
import { random } from 'lodash-es'

defineOptions({
  name: 'DataScreenLeft2',
})

// 国际关注主题列表
const themes = [
  "ZiStock",
  "深度感知DPBiO",
  "NeaChat",
  "Archse元构感知",
  "麟纪科技",
  "欧科云链",
  "瑞利光",
  "Jumppoint",
  "食铁兽科技",
  "AotoPay"
]

const currentTitle = ref("ZiStock") // 默认标题

const data = reactive([
  { value: 90, name: '财务质量' },
  { value: 86, name: '市场地位' },
  { value: 75, name: '客户价值' },
  { value: 60, name: '产品竞争力' },
  { value: 45, name: '创新能力' },
  { value: 40, name: '运营效率' },
  { value: 30, name: '人才情况' },
])

const option = reactive<any>({
  grid: {
    left: '20px',
    right: '20px',
    bottom: '20px',
    top: '20px',
    containLabel: true,
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}',
  },
  series: {
    type: 'pie',
    radius: ['35%', '60%'],
    center: ['50%', '50%'],
    itemStyle: {
      borderRadius: 10,
    },
    label: {
      show: true,
      color: '#fff',
      formatter: '{b}: {d}%',
    },
    labelLine: {
      lineStyle: {},
    },
    emphasis: {
      label: {
        show: true,
      },
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)',
      },
    },
    data,
    startAngle: 90,
    clockwise: false,
  },
})

// 更新数据和标题的函数
const updateChart = () => {
  option.series.data = [
    { value: random(10, 100), name: '财务质量' },
    { value: random(10, 100), name: '市场地位' },
    { value: random(10, 100), name: '客户价值' },
    { value: random(10, 100), name: '产品竞争力' },
    { value: random(10, 100), name: '创新能力' },
    { value: random(10, 100), name: '运营效率' },
    { value: random(10, 100), name: '人才情况' },
  ]
  
  // 随机选择一个新主题
  currentTitle.value = themes[Math.floor(Math.random() * themes.length)]
}

// 每5秒更新一次数据和标题
setInterval(updateChart, 1000 * 5)
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-title {
  text-align: center;
  margin-bottom: -10px;
  font-size: 12px; /* 字号调小 */
  font-weight: normal; /* 字体重量调整为普通 */
  color: white; /* 颜色设为白色 */
  transition: all 0.5s ease;
}
</style>