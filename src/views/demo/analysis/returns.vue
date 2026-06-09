<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>收益分析</h2>
      <p class="page-desc">综合展示净值走势、回撤、收益分布、月度表现与年度对比等专业分析图表。</p>
    </div>

    <!-- 核心指标（两行） -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="3">
        <el-card shadow="hover"><div class="stat-label">累计收益</div><div class="stat-value" :class="summary.totalReturn >= 0 ? 'up' : 'down'">{{ summary.totalReturn?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="3">
        <el-card shadow="hover"><div class="stat-label">年化收益</div><div class="stat-value" :class="summary.annualReturn >= 0 ? 'up' : 'down'">{{ summary.annualReturn?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="3">
        <el-card shadow="hover"><div class="stat-label">Sharpe</div><div class="stat-value">{{ summary.sharpeRatio?.toFixed(2) }}</div></el-card>
      </el-col>
      <el-col :span="3">
        <el-card shadow="hover"><div class="stat-label">最大回撤</div><div class="stat-value down">{{ summary.maxDrawdown?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="3">
        <el-card shadow="hover"><div class="stat-label">Calmar</div><div class="stat-value">{{ summary.calmarRatio?.toFixed(2) }}</div></el-card>
      </el-col>
      <el-col :span="3">
        <el-card shadow="hover"><div class="stat-label">年化波动</div><div class="stat-value">{{ summary.volatility?.toFixed(2) }}%</div></el-card>
      </el-col>
      <el-col :span="3">
        <el-card shadow="hover"><div class="stat-label">Sortino</div><div class="stat-value">{{ summary.sortinoRatio?.toFixed(2) }}</div></el-card>
      </el-col>
      <el-col :span="3">
        <el-card shadow="hover"><div class="stat-label">信息比率</div><div class="stat-value">{{ summary.informationRatio?.toFixed(2) }}</div></el-card>
      </el-col>
    </el-row>

    <!-- 第一行：净值走势+回撤 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="16">
        <el-card>
          <template #header><span class="section-title">净值走势 & 回撤</span></template>
          <vab-chart :option="navDrawdownOption" class="demo-chart-lg" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header><span class="section-title">月度收益热力图</span></template>
          <vab-chart :option="monthlyHeatmapOption" class="demo-chart-lg" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：收益分布 + 年度对比 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header><span class="section-title">日收益分布</span></template>
          <vab-chart :option="distOption" class="demo-chart-md" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span class="section-title">年度收益对比</span></template>
          <vab-chart :option="annualOption" class="demo-chart-md" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：累计收益曲线（保留原图） -->
    <el-card style="margin-top:16px">
      <template #header><span class="section-title">累计收益 & 日收益率</span></template>
      <vab-chart :option="returnsOption" class="demo-chart-md" />
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { getAnalysisReturns } from '/@/api/demo/index'

defineOptions({ name: 'DemoAnalysisReturns' })

const dailyReturns = ref<any[]>([])
const navSeries = ref<number[]>([])
const drawdownSeries = ref<number[]>([])
const monthlyReturns = ref<any[]>([])
const dailyReturnDist = ref<any[]>([])
const annualReturns = ref<any[]>([])
const summary = ref<any>({})

// ====== 1. 净值走势 & 回撤面积图 ======
const navDrawdownOption = computed(() => {
  const dates = dailyReturns.value.map((d: any) => d.date)
  return {
    grid: { top: 58, right: 58, bottom: 44, left: 54, containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        const navItem = params.find((p: any) => p.seriesName === '净值')
        const ddItem = params.find((p: any) => p.seriesName === '回撤')
        return `${params[0].axisValue}<br/>
          ${navItem ? `净值：<b>${navItem.value.toFixed(4)}</b>` : ''}
          ${ddItem ? `<br/>回撤：<b style="color:#27ae60">${ddItem.value.toFixed(2)}%</b>` : ''}`
      },
    },
    legend: { data: ['净值', '回撤(%)'], top: 12, itemWidth: 12, itemHeight: 8, textStyle: { fontSize: 12, color: '#526071' } },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 35, fontSize: 11, interval: 8, color: '#7a8699' } },
    yAxis: [
      {
        type: 'value', name: '净值', min: (v: any) => (v.min * 0.98).toFixed(4),
        axisLabel: { formatter: '{value}', color: '#7a8699' },
      },
      {
        type: 'value', name: '回撤(%)', inverse: true,
        axisLabel: { formatter: '{value}%', color: '#7a8699' },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '回撤(%)', type: 'line', yAxisIndex: 1, data: drawdownSeries.value,
        lineStyle: { color: '#27ae60', width: 0 },
        itemStyle: { color: '#27ae60' },
        areaStyle: { color: 'rgba(39,174,96,0.15)' },
        symbol: 'none',
      },
      {
        name: '净值', type: 'line', data: navSeries.value,
        smooth: true, symbol: 'none',
        lineStyle: { color: '#409EFF', width: 2.5 },
        itemStyle: { color: '#409EFF' },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64,158,255,0.25)' },
              { offset: 1, color: 'rgba(64,158,255,0.02)' },
            ],
          },
        },
      },
    ],
  }
})

// ====== 2. 月度收益热力图 ======
const monthlyHeatmapOption = computed(() => {
  // 按年份分组
  const yearMap: Record<number, any[]> = {}
  monthlyReturns.value.forEach((m: any) => {
    if (!yearMap[m.year]) yearMap[m.year] = Array(12).fill(null)
    yearMap[m.year][m.monthIdx - 1] = m.return
  })
  const years = Object.keys(yearMap).map(Number).sort()
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  const heatData: any[] = []
  years.forEach((y, yi) => {
    yearMap[y].forEach((val: number | null, mi: number) => {
      if (val !== null) heatData.push([mi, yi, val])
    })
  })

  return {
    grid: { top: 24, right: 30, bottom: 72, left: 46, containLabel: true },
    tooltip: { formatter: (p: any) => `${years[p.value[1]]}年${months[p.value[0]]}：<b>${p.value[2].toFixed(2)}%</b>` },
    xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11, rotate: 28, color: '#7a8699' } },
    yAxis: { type: 'category', data: years.map(String), axisLabel: { fontSize: 11, color: '#7a8699' } },
    visualMap: {
      min: -10, max: 15, calculable: true, orient: 'horizontal', bottom: 0, left: 'center',
      inRange: { color: ['#27ae60', '#ffffff', '#e74c3c'] },
      text: ['赚', '亏'], textStyle: { color: '#667085', fontSize: 11 },
    },
    series: [{
      type: 'heatmap', data: heatData,
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
    }],
  }
})

// ====== 3. 日收益分布直方图 + 正态曲线 ======
const distOption = computed(() => {
  const buckets = dailyReturnDist.value.map((d: any) => d.bucket)
  const counts = dailyReturnDist.value.map((d: any) => d.count)
  // 计算均值和标准差来画正态曲线
  const allReturns = dailyReturns.value.map((d: any) => d.dailyReturn)
  const mean = allReturns.reduce((s: number, v: number) => s + v, 0) / allReturns.length
  const std = Math.sqrt(allReturns.reduce((s: number, v: number) => s + (v - mean) ** 2, 0) / allReturns.length)
  // 生成正态曲线数据
  const normalCurve = buckets.map((_: string, i: number) => {
    const x = -4.5 + i * 1
    return (1 / (std * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * ((x - mean) / std) ** 2) * Math.max(...counts) * 0.25
  })

  return {
    grid: { top: 48, right: 28, bottom: 40, left: 46, containLabel: true },
    tooltip: { trigger: 'axis' },
    legend: { data: ['频次', '正态拟合'], top: 8, itemWidth: 12, itemHeight: 8, textStyle: { fontSize: 12, color: '#526071' } },
    xAxis: { type: 'category', data: buckets, axisLabel: { fontSize: 11, color: '#7a8699' } },
    yAxis: { type: 'value', name: '频次', axisLabel: { color: '#7a8699' } },
    series: [
      {
        name: '频次', type: 'bar', data: counts, barWidth: '60%',
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: (p: any) => {
            const idx = buckets.indexOf(p.name)
            return idx < 5 ? '#27ae60' : '#e74c3c'
          },
        },
      },
      {
        name: '正态拟合', type: 'line', data: normalCurve,
        smooth: true, symbol: 'none',
        lineStyle: { color: '#e6a23c', width: 2, type: 'dashed' },
      },
    ],
  }
})

// ====== 4. 年度收益对比 ======
const annualOption = computed(() => {
  const years = annualReturns.value.map((d: any) => String(d.year))
  const strategyReturns = annualReturns.value.map((d: any) => d.return)
  const benchmarkReturns = annualReturns.value.map((d: any) => d.benchmark)

  return {
    grid: { top: 48, right: 28, bottom: 38, left: 46, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['策略收益(%)', '基准收益(%)'], top: 8, itemWidth: 12, itemHeight: 8, textStyle: { fontSize: 12, color: '#526071' } },
    xAxis: { type: 'category', data: years, axisLabel: { fontSize: 11, color: '#7a8699' } },
    yAxis: { type: 'value', name: '收益率(%)', axisLabel: { formatter: '{value}%', color: '#7a8699' } },
    series: [
      {
        name: '策略收益(%)', type: 'bar', data: strategyReturns, barGap: '10%',
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#409EFF' },
        label: { show: true, position: 'top', fontSize: 10, formatter: '{c}%' },
      },
      {
        name: '基准收益(%)', type: 'bar', data: benchmarkReturns,
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#c0c4cc' },
        label: { show: true, position: 'top', fontSize: 10, formatter: '{c}%' },
      },
    ],
  }
})

// ====== 5. 累计收益 & 日收益率（保留原图，增强） ======
const returnsOption = computed(() => {
  const dates = dailyReturns.value.map((d: any) => d.date)
  const cumReturns = dailyReturns.value.map((d: any) => d.cumulativeReturn)
  const dayReturns = dailyReturns.value.map((d: any) => d.dailyReturn)
  return {
    grid: { top: 56, right: 58, bottom: 42, left: 54, containLabel: true },
    tooltip: { trigger: 'axis' },
    legend: { data: ['日收益率(%)', '累计收益(%)'], top: 12, itemWidth: 12, itemHeight: 8, textStyle: { fontSize: 12, color: '#526071' } },
    dataZoom: [{ type: 'inside', start: 0, end: 100 }],
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 35, fontSize: 11, interval: 8, color: '#7a8699' } },
    yAxis: [
      { type: 'value', name: '日收益率(%)', axisLabel: { formatter: '{value}%', color: '#7a8699' }, splitLine: { lineStyle: { type: 'dashed' } } },
      { type: 'value', name: '累计收益(%)', axisLabel: { formatter: '{value}%', color: '#7a8699' } },
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
        markLine: {
          silent: true,
          data: [{ yAxis: 0, label: { formatter: '盈亏线' }, lineStyle: { color: '#909399', type: 'dashed' } }],
        },
      },
    ],
  }
})

onMounted(async () => {
  const res = await getAnalysisReturns()
  const data = res.data
  dailyReturns.value = data.dailyReturns
  navSeries.value = data.navSeries
  drawdownSeries.value = data.drawdownSeries
  monthlyReturns.value = data.monthlyReturns
  dailyReturnDist.value = data.dailyReturnDist
  annualReturns.value = data.annualReturns
  summary.value = data.summary
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.stats-row { margin-bottom: 0; }
.stat-label { font-size: 12px; color: #909399; }
.stat-value { font-size: 18px; font-weight: 700; margin-top: 4px; color: #303133; }
.up { color: #e74c3c; }
.down { color: #27ae60; }
.section-title { font-weight: 600; font-size: 15px; }
</style>
