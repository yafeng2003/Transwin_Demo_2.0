<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>账户风险监控</h2>
      <p class="page-desc">监控账户维度的风险指标：单日亏损、最大回撤、连续亏损。</p>
    </div>

    <!-- 三大风险指标 -->
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-title">单日亏损监控</div>
          <div class="metric-body">
            <div class="metric-row">
              <span>当前亏损</span>
              <span class="metric-val" :class="dailyLossPercent > 50 ? 'danger' : ''">{{ formatMoney(metrics.dailyLoss?.current) }}</span>
            </div>
            <div class="metric-row">
              <span>亏损阈值</span>
              <span class="metric-val">{{ formatMoney(metrics.dailyLoss?.threshold) }}</span>
            </div>
            <el-progress :percentage="dailyLossPercent" :color="dailyLossPercent > 80 ? '#e74c3c' : dailyLossPercent > 50 ? '#e67e22' : '#27ae60'" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-title">最大回撤监控</div>
          <div class="metric-body">
            <div class="metric-row">
              <span>当前回撤</span>
              <span class="metric-val" :class="drawdownPercent > 50 ? 'danger' : ''">{{ formatPercent(metrics.maxDrawdown?.current) }}</span>
            </div>
            <div class="metric-row">
              <span>回撤阈值</span>
              <span class="metric-val">{{ formatPercent(metrics.maxDrawdown?.threshold) }}</span>
            </div>
            <el-progress :percentage="drawdownPercent" :color="drawdownPercent > 80 ? '#e74c3c' : drawdownPercent > 50 ? '#e67e22' : '#27ae60'" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-title">连续亏损监控</div>
          <div class="metric-body">
            <div class="metric-row">
              <span>连续亏损次数</span>
              <span class="metric-val" :class="consecutiveLosses >= lossThreshold ? 'danger' : consecutiveLosses >= Math.ceil(lossThreshold * 0.6) ? 'warn' : ''">{{ consecutiveLosses }} 次</span>
            </div>
            <div class="metric-row">
              <span>阈值</span>
              <span class="metric-val">{{ lossThreshold }} 次</span>
            </div>
            <el-progress :percentage="lossPercent" :color="lossPercent > 80 ? '#e74c3c' : lossPercent > 50 ? '#e67e22' : '#27ae60'" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 风险阈值配置表 -->
    <el-card style="margin-top:16px">
      <template #header><span class="section-title">风险阈值配置</span></template>
      <el-table :data="thresholds" stripe size="small">
        <el-table-column prop="name" label="指标名称" width="180" />
        <el-table-column prop="threshold" label="阈值" width="150" />
        <el-table-column prop="action" label="触发动作" width="150" />
        <el-table-column prop="status" label="当前状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.breached ? 'danger' : 'success'" size="small">
              {{ row.breached ? '已触发' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" />
      </el-table>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue'
import { getRiskAccountMetrics } from '/@/api/demo/index'
import { useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoRiskAccount' })

const demoStore = useDemoStore()
const metrics = ref<any>({})

const consecutiveLosses = computed(() => Number(metrics.value.consecutiveLosses?.current || 0))
const lossThreshold = computed(() => Number(metrics.value.consecutiveLosses?.threshold || 5))
const dailyLossPercent = computed(() => ratio(metrics.value.dailyLoss?.current, metrics.value.dailyLoss?.threshold))
const drawdownPercent = computed(() => ratio(metrics.value.maxDrawdown?.current, metrics.value.maxDrawdown?.threshold))
const lossPercent = computed(() => ratio(consecutiveLosses.value, lossThreshold.value))

const thresholds = computed(() => metrics.value.thresholds || [])

function ratio(current: number, threshold: number) {
  const t = Number(threshold || 0)
  if (!t) return 0
  return Math.min(100, Math.round((Math.abs(Number(current || 0)) / t) * 10000) / 100)
}

function formatMoney(v: number) {
  if (v == null) return '-'
  return (v >= 0 ? '¥' : '-¥') + Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatPercent(v: number) {
  if (v == null) return '-'
  return `${Number(v).toFixed(2)}%`
}

async function fetchData() {
  try {
    const res = await getRiskAccountMetrics({ market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId })
    metrics.value = res.data || {}
  } catch {
    metrics.value = {}
  }
}

onMounted(fetchData)
watch(() => demoStore.switchVersion, fetchData)
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.metric-card .metric-title { font-size: 15px; font-weight: 600; margin-bottom: 16px; }
.metric-body { padding: 4px 0; }
.metric-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; }
.metric-val { font-weight: 600; }
.danger { color: #e74c3c; }
.warn { color: #e67e22; }
.section-title { font-weight: 600; font-size: 15px; }
</style>
