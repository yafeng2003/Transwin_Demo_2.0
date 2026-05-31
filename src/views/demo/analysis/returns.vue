<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>💰 收益分析</h2>
      <p class="page-desc">展示累计收益、年化收益、Sharpe Ratio、最大回撤等核心收益指标。</p>
    </div>

    <!-- 核心指标 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">累计收益</div><div class="stat-value" :class="summary.totalReturn >= 0 ? 'up' : 'down'">{{ summary.totalReturn?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">年化收益</div><div class="stat-value" :class="summary.annualReturn >= 0 ? 'up' : 'down'">{{ summary.annualReturn?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">Sharpe Ratio</div><div class="stat-value">{{ summary.sharpeRatio?.toFixed(2) }}</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">最大回撤</div><div class="stat-value down">{{ summary.maxDrawdown?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">Calmar Ratio</div><div class="stat-value">{{ summary.calmarRatio?.toFixed(2) }}</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">胜率</div><div class="stat-value">{{ summary.winRate?.toFixed(1) }}%</div></el-card>
      </el-col>
    </el-row>

    <!-- 累计收益曲线 -->
    <el-card style="margin-top:16px">
      <template #header><span class="section-title">📈 累计收益曲线（近90日）</span></template>
      <vab-chart :option="returnsOption" style="height:320px" />
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { getAnalysisReturns } from '/@/api/demo/index'

defineOptions({ name: 'DemoAnalysisReturns' })

const dailyReturns = ref<any[]>([])
const summary = ref<any>({})

const returnsOption = computed(() => {
  const dates = dailyReturns.value.map((d: any) => d.date)
  const cumReturns = dailyReturns.value.map((d: any) => d.cumulativeReturn)
  const dayReturns = dailyReturns.value.map((d: any) => d.dailyReturn)
  return {
    grid: { top: 40, right: 60, bottom: 40, left: 60 },
    tooltip: { trigger: 'axis' },
    legend: { data: ['日收益率(%)', '累计收益(%)'], top: 10 },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, fontSize: 10, interval: 6 } },
    yAxis: [
      { type: 'value', name: '日收益率(%)', axisLabel: { formatter: '{value}%' } },
      { type: 'value', name: '累计收益(%)', axisLabel: { formatter: '{value}%' } },
    ],
    series: [
      {
        name: '日收益率(%)', type: 'bar', data: dayReturns,
        itemStyle: { color: (p: any) => p.value >= 0 ? '#e74c3c' : '#27ae60' },
      },
      {
        name: '累计收益(%)', type: 'line', yAxisIndex: 1, data: cumReturns,
        smooth: true, lineStyle: { color: '#409EFF', width: 2 }, itemStyle: { color: '#409EFF' },
        symbol: 'none',
      },
    ],
  }
})

onMounted(async () => {
  const res = await getAnalysisReturns()
  dailyReturns.value = res.data.dailyReturns
  summary.value = res.data.summary
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.stats-row { margin-bottom: 0; }
.stat-label { font-size: 13px; color: #909399; }
.stat-value { font-size: 20px; font-weight: 700; margin-top: 4px; color: #303133; }
.up { color: #e74c3c; }
.down { color: #27ae60; }
.section-title { font-weight: 600; font-size: 15px; }
.chart-placeholder { padding: 8px 0; }
.line-chart { display: flex; align-items: flex-end; height: 180px; gap: 1px; }
.line-bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.line-bar { width: 100%; max-width: 6px; border-radius: 1px; min-height: 2px; }
.bar-up { background: #e74c3c; }
.bar-down { background: #27ae60; }
.line-label { font-size: 9px; color: #909399; margin-top: 4px; transform: rotate(-60deg); white-space: nowrap; }
</style>
