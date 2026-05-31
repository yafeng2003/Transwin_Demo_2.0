<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>📊 可视化图表</h2>
      <p class="page-desc">集中展示 K线图、收益曲线、持仓分布、风险热力图、资金曲线等可视化图表（当前为占位，待接入 ECharts）。</p>
    </div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header><span class="section-title">📈 K线图</span></template>
          <vab-chart :option="klineOption" style="height:220px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header><span class="section-title">📉 收益曲线</span></template>
          <vab-chart :option="lineOption" style="height:220px" />
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-top:16px">
        <el-card class="chart-card">
          <template #header><span class="section-title">🍩 持仓分布</span></template>
          <vab-chart :option="pieOption" style="height:220px" />
        </el-card>
      </el-col>
      <el-col :span="12" style="margin-top:16px">
        <el-card class="chart-card">
          <template #header><span class="section-title">🔥 风险热力图</span></template>
          <vab-chart :option="heatmapOption" style="height:220px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

defineOptions({ name: 'DemoAnalysisCharts' })

// ---- K 线图 (模拟 OHLC) ----
const klineData = computed(() => {
  const data: number[][] = []
  let close = 100
  for (let i = 0; i < 60; i++) {
    const open = close
    close = Math.max(30, Math.min(180, close + (Math.random() - 0.48) * 8))
    const low = Math.min(open, close) * (0.98 + Math.random() * 0.02)
    const high = Math.max(open, close) * (1.02 - Math.random() * 0.02)
    data.push([open, close, low, high])
  }
  return data
})

const klineOption = computed(() => ({
  grid: { top: 10, right: 20, bottom: 30, left: 60 },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: Array.from({ length: klineData.value.length }, (_, i) => `D${i + 1}`), axisLabel: { interval: 9, fontSize: 10 } },
  yAxis: { type: 'value', scale: true },
  series: [{
    type: 'candlestick',
    data: klineData.value,
    itemStyle: { color: '#e74c3c', color0: '#27ae60', borderColor: '#e74c3c', borderColor0: '#27ae60' },
  }],
}))

// ---- 收益曲线 ----
const lineOption = computed(() => {
  const dates = Array.from({ length: 60 }, (_, i) => `05-${(i + 1).toString().padStart(2, '0')}`)
  const values: number[] = []
  let cum = 0
  for (let i = 0; i < 60; i++) {
    cum += (Math.random() - 0.45) * 5
    values.push(parseFloat(cum.toFixed(2)))
  }
  return {
    grid: { top: 10, right: 20, bottom: 30, left: 50 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates, axisLabel: { interval: 9, fontSize: 10 } },
    yAxis: { type: 'value', name: '%', axisLabel: { formatter: '{value}%' } },
    series: [{
      type: 'line', data: values, smooth: true,
      lineStyle: { color: '#409EFF', width: 2 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(64,158,255,0.25)' }, { offset: 1, color: 'rgba(64,158,255,0.02)' }] } },
      symbol: 'none',
    }],
  }
})

// ---- 持仓饼图 ----
const pieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, textStyle: { fontSize: 11 } },
  series: [{
    type: 'pie', radius: ['45%', '75%'], center: ['50%', '45%'],
    label: { formatter: '{b}\n{d}%', fontSize: 11 },
    itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
    data: [
      { value: 35, name: '金融' },
      { value: 25, name: '科技' },
      { value: 20, name: '消费' },
      { value: 12, name: '医药' },
      { value: 8, name: '其他' },
    ],
  }],
}))

// ---- 风险热力图 ----
const heatmapOption = computed(() => {
  const hours = ['9:30', '10:30', '11:30', '14:00', '15:00']
  const days = ['周一', '周二', '周三', '周四', '周五']
  const data: number[][] = []
  for (let d = 0; d < 5; d++)
    for (let h = 0; h < 5; h++)
      data.push([h, d, Math.floor(Math.random() * 100)])
  return {
    grid: { top: 10, right: 80, bottom: 30, left: 50 },
    tooltip: {},
    xAxis: { type: 'category', data: hours, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'category', data: days, axisLabel: { fontSize: 10 } },
    visualMap: { min: 0, max: 100, orient: 'vertical', right: 0, inRange: { color: ['#fdecea', '#f5a092', '#e74c3c', '#8b0000'] } },
    series: [{ type: 'heatmap', data, label: { show: true, fontSize: 10 } }],
  }
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.section-title { font-weight: 600; font-size: 15px; }
.chart-card { }
</style>
