<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>风险分析</h2>
      <p class="page-desc">从风险暴露、回撤、波动率、风险分布等维度分析策略风险特征。（使用收益分析数据交叉展示）</p>
    </div>

    <!-- 指标卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">最大回撤</div><div class="stat-value down">{{ summary.maxDrawdown?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">年化波动率</div><div class="stat-value">{{ summary.annualReturn ? (Math.abs(summary.annualReturn) / (summary.sharpeRatio || 1) * 1.2).toFixed(2) : '-' }}%</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">Calmar Ratio</div><div class="stat-value">{{ summary.calmarRatio?.toFixed(2) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">下行波动率</div><div class="stat-value">{{ summary.annualReturn ? (Math.abs(summary.annualReturn) / (summary.sharpeRatio || 1) * 0.8).toFixed(2) : '-' }}%</div></el-card>
      </el-col>
    </el-row>

    <!-- 回撤分析 占位 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header><span class="section-title">回撤分布</span></template>
          <vab-chart :option="drawdownOption" class="demo-chart-sm" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span class="section-title">风险热力矩阵</span></template>
          <vab-chart :option="heatmapOption" class="demo-chart-sm" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { getAnalysisReturns } from '/@/api/demo/index'

defineOptions({ name: 'DemoAnalysisRisk' })

const summary = ref<any>({})

const drawdownOption = computed(() => ({
  grid: { top: 24, right: 24, bottom: 38, left: 44, containLabel: true },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['0~2%', '2~4%', '4~6%', '6~8%', '8~10%', '10~12%', '12~14%', '14~16%'], axisLabel: { color: '#7a8699', fontSize: 11 } },
  yAxis: { type: 'value', name: '次数', axisLabel: { color: '#7a8699' }, splitLine: { lineStyle: { type: 'dashed' } } },
  series: [{
    type: 'bar',
    data: Array.from({ length: 8 }, () => Math.floor(Math.random() * 15 + 2)),
    itemStyle: {
      borderRadius: [4, 4, 0, 0],
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#e74c3c' }, { offset: 1, color: '#f5a092' }] },
    },
  }],
}))

const heatmapOption = computed(() => ({
  grid: { top: 22, right: 92, bottom: 36, left: 72, containLabel: true },
  tooltip: {},
  xAxis: { type: 'category', data: ['金融', '科技', '消费', '医药', '能源'], axisLabel: { fontSize: 11, color: '#7a8699' } },
  yAxis: { type: 'category', data: ['策略A', '策略B', '策略C', '策略D'], axisLabel: { fontSize: 11, color: '#7a8699' } },
  visualMap: { min: 0, max: 100, calculable: true, orient: 'vertical', right: 0, top: 'middle', itemHeight: 140, textStyle: { color: '#667085', fontSize: 11 }, inRange: { color: ['#fdecea', '#f5a092', '#e74c3c', '#8b0000'] } },
  series: [{
    type: 'heatmap',
    data: Array.from({ length: 20 }, (_, i) => [i % 5, Math.floor(i / 5), Math.floor(Math.random() * 100)]),
    label: { show: false },
  }],
}))

onMounted(async () => {
  const res = await getAnalysisReturns()
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
.down { color: #27ae60; }
.section-title { font-weight: 600; font-size: 15px; }
.placeholder-chart { min-height: 220px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.placeholder-text { color: #909399; font-size: 13px; margin-bottom: 16px; }
.mock-bars { display: flex; align-items: flex-end; gap: 8px; height: 140px; width: 100%; padding: 0 20px; }
.mock-bar-item { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.mock-bar { width: 100%; background: linear-gradient(180deg, #e74c3c, #e67e22); border-radius: 2px 2px 0 0; }
.mock-bar-label { font-size: 10px; color: #909399; margin-top: 4px; }
.heatmap-mock { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; width: 80%; margin-top: 12px; }
.heat-cell { aspect-ratio: 1; border-radius: 4px; }
</style>
