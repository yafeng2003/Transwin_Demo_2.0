<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>风控总览</h2>
      <p class="page-desc">汇总展示当前风险等级、风险指标与趋势。</p>
    </div>

    <!-- 风险等级 + 核心指标 -->
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card shadow="hover" class="risk-level-card" :class="'border-' + riskLevelClass">
          <div class="risk-big-label">当前风险等级</div>
          <div class="risk-big-value" :class="'level-' + riskLevelClass">
            {{ ['低', '中', '高'][data.riskLevel - 1] || '-' }}
          </div>
          <div class="risk-big-score">综合评分：{{ data.riskScore }} 分</div>
        </el-card>
      </el-col>
      <el-col :span="18">
        <div class="risk-stats">
          <el-card shadow="hover" class="risk-stat-item"><div class="stat-label">今日事件</div><div class="stat-value">{{ data.todayEvents }}</div></el-card>
          <el-card shadow="hover" class="risk-stat-item"><div class="stat-label">未处理事件</div><div class="stat-value" :class="data.unresolvedEvents > 0 ? 'warn' : ''">{{ data.unresolvedEvents }}</div></el-card>
          <el-card shadow="hover" class="risk-stat-item"><div class="stat-label">本周事件</div><div class="stat-value">{{ data.weekEvents }}</div></el-card>
          <el-card shadow="hover" class="risk-stat-item"><div class="stat-label">最大回撤</div><div class="stat-value down">{{ data.maxDrawdown?.toFixed(2) }}%</div></el-card>
          <el-card shadow="hover" class="risk-stat-item"><div class="stat-label">日VaR</div><div class="stat-value">{{ formatMoney(data.dailyVar) }}</div></el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 风险趋势 -->
    <el-card style="margin-top:16px">
      <template #header><span class="section-title">风险评分趋势（近30日）</span></template>
      <vab-chart :option="trendOption" class="demo-chart-sm" />
    </el-card>

    <!-- 快捷入口 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="8">
        <el-card shadow="hover" class="quick-link" @click="$router.push('/demo/risk/execution')">
          <el-icon><WarningFilled /></el-icon>
          <span>执行风险监控 →</span>
          <p>下单/撤单失败、API异常</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="quick-link" @click="$router.push('/demo/risk/account')">
          <el-icon><DataAnalysis /></el-icon>
          <span>账户风险监控 →</span>
          <p>回撤、亏损阈值监控</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="quick-link" @click="$router.push('/demo/risk/events')">
          <el-icon><Bell /></el-icon>
          <span>风险事件中心 →</span>
          <p>全部风险事件列表</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { Bell, DataAnalysis, WarningFilled } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { getRiskOverview } from '/@/api/demo/index'

defineOptions({ name: 'DemoRiskOverview' })

const data = ref<any>({ trend: [] })

const riskLevelClass = computed(() => {
  const l = data.value.riskLevel
  return l === 1 ? 'low' : l === 2 ? 'mid' : 'high'
})

const formatMoney = (v: number) => {
  if (v == null) return '-'
  return (v >= 0 ? '¥' : '-¥') + Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const trendOption = computed(() => ({
  grid: { top: 28, right: 28, bottom: 36, left: 46, containLabel: true },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (data.value.trend || []).map((t: any) => t.date), axisLabel: { rotate: 45, fontSize: 10 } },
  yAxis: { type: 'value', name: '评分', min: 0, max: 100 },
  visualMap: { show: false, pieces: [{ lte: 30, color: '#27ae60' }, { gt: 30, lte: 60, color: '#e67e22' }, { gt: 60, color: '#e74c3c' }] },
  series: [{
    type: 'line',
    data: (data.value.trend || []).map((t: any) => t.riskScore),
    smooth: true,
    areaStyle: { opacity: 0.3 },
    lineStyle: { width: 2 },
  }],
}))

onMounted(async () => {
  const res = await getRiskOverview()
  data.value = res.data
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.risk-stats { display: flex; gap: 12px; height: 100%; }
.risk-stats .risk-stat-item { flex: 1; min-width: 0; }
.risk-stats .risk-stat-item :deep(.el-card__body) { height: 100%; display: flex; flex-direction: column; justify-content: center; }
.stat-label { font-size: 13px; color: #909399; }
.stat-value { font-size: 22px; font-weight: 700; margin-top: 4px; color: #303133; }
.warn { color: #e67e22; }
.down { color: #27ae60; }
.risk-level-card { text-align: center; }
.border-low { border-top: 3px solid #27ae60; }
.border-mid { border-top: 3px solid #e67e22; }
.border-high { border-top: 3px solid #e74c3c; }
.risk-big-label { font-size: 14px; color: #909399; }
.risk-big-value { font-size: 48px; font-weight: 800; margin: 8px 0; }
.risk-big-value.level-low { color: #27ae60; }
.risk-big-value.level-mid { color: #e67e22; }
.risk-big-value.level-high { color: #e74c3c; }
.risk-big-score { color: #909399; font-size: 14px; }
.section-title { font-weight: 600; font-size: 15px; }
.chart-placeholder { padding: 8px 0; }
.trend-chart { display: flex; align-items: flex-end; height: 220px; gap: 2px; }
.trend-bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.trend-bar { width: 100%; max-width: 16px; border-radius: 2px 2px 0 0; min-height: 2px; }
.trend-label { font-size: 10px; color: #909399; margin-top: 4px; transform: rotate(-45deg); white-space: nowrap; }
.quick-link { cursor: pointer; transition: all 0.2s; }
.quick-link:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.quick-link span { font-weight: 600; font-size: 15px; margin-left: 8px; }
.quick-link p { color: #909399; font-size: 13px; margin: 8px 0 0 28px; }
</style>
