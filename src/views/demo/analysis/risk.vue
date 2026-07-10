<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>风险分析</h2>
      <p class="page-desc">从风险暴露、回撤、波动率、风险分布等维度分析策略风险特征。</p>
    </div>

    <!-- 指标卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">最大回撤</div><div class="stat-value down">{{ summary.maxDrawdown?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">年化波动率</div><div class="stat-value">{{ formatNumber(riskData.volatility) }}%</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">Calmar Ratio</div><div class="stat-value">{{ summary.calmarRatio?.toFixed(2) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">下行风险(VaR)</div><div class="stat-value">{{ formatNumber(riskData.downsideVolatility) }}%</div></el-card>
      </el-col>
    </el-row>

    <!-- 回撤分析 占位 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header><span class="section-title">收益/回撤分布</span></template>
          <vab-chart :option="drawdownOption" class="demo-chart-sm" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span class="section-title">风险暴露概览</span></template>
          <vab-chart :option="heatmapOption" class="demo-chart-sm" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue'
import { getAnalysisReturns, getAnalysisRisk } from '/@/api/demo/index'
import { useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoAnalysisRisk' })
const demoStore = useDemoStore()

const summary = ref<any>({})
const riskData = ref<any>({})

const drawdownOption = computed(() => ({
  grid: { top: 24, right: 24, bottom: 38, left: 44, containLabel: true },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (riskData.value.drawdownDistribution || []).map((i: any) => i.range), axisLabel: { color: '#7a8699', fontSize: 11 } },
  yAxis: { type: 'value', name: '次数', axisLabel: { color: '#7a8699' }, splitLine: { lineStyle: { type: 'dashed' } } },
  series: [{
    type: 'bar',
    data: (riskData.value.drawdownDistribution || []).map((i: any) => i.count),
    itemStyle: {
      borderRadius: [4, 4, 0, 0],
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#e74c3c' }, { offset: 1, color: '#f5a092' }] },
    },
  }],
}))

const heatmapOption = computed(() => ({
  grid: { top: 22, right: 92, bottom: 36, left: 72, containLabel: true },
  tooltip: {},
  xAxis: { type: 'category', data: exposureSectors.value, axisLabel: { fontSize: 11, color: '#7a8699' } },
  yAxis: { type: 'category', data: exposureStrategies.value, axisLabel: { fontSize: 11, color: '#7a8699' } },
  visualMap: { min: 0, max: 100, calculable: true, orient: 'vertical', right: 0, top: 'middle', itemHeight: 140, textStyle: { color: '#667085', fontSize: 11 }, inRange: { color: ['#fdecea', '#f5a092', '#e74c3c', '#8b0000'] } },
  series: [{
    type: 'heatmap',
    data: exposureHeatmap.value,
    label: { show: false },
  }],
}))

const exposureSectors = computed(() => {
  const sectors = riskData.value.riskExposure?.sectors || []
  return sectors.length ? sectors : ['账户整体']
})
const exposureStrategies = computed(() => {
  const strategies = riskData.value.riskExposure?.strategies || []
  return strategies.length ? strategies : [demoStore.strategyId || '当前策略']
})
const exposureHeatmap = computed(() => {
  const raw = riskData.value.riskExposure?.heatmapData || []
  if (raw.length) return raw
  return exposureStrategies.value.flatMap((_: string, row: number) => exposureSectors.value.map((__: string, col: number) => [col, row, Math.round(Number(riskData.value.volatility || 0))]))
})

function formatNumber(v: number) {
  if (v == null) return '-'
  return Number(v).toFixed(2)
}

async function fetchData() {
  try {
    const [retRes, riskRes] = await Promise.all([
      getAnalysisReturns({ market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId, period: '1y' }),
      getAnalysisRisk({ market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId, period: '1y' }),
    ])
    summary.value = retRes.data.summary
    riskData.value = riskRes.data
  } catch { /* ignore */ }
}

onMounted(fetchData)
watch(() => demoStore.switchVersion, fetchData)
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.stats-row { margin-bottom: 0; }
.stat-label { font-size: 13px; color: #909399; }
.stat-value { font-size: 20px; font-weight: 700; margin-top: 4px; color: #303133; }
.down { color: #27ae60; }
.section-title { font-weight: 600; font-size: 15px; }
</style>
