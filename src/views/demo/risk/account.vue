<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>📉 账户风险监控</h2>
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
              <span class="metric-val" :class="dailyLossPercent > 50 ? 'danger' : ''">¥{{ mockDailyLoss.toLocaleString() }}</span>
            </div>
            <div class="metric-row">
              <span>亏损阈值</span>
              <span class="metric-val">¥500,000.00</span>
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
              <span class="metric-val" :class="drawdownPercent > 50 ? 'danger' : ''">{{ mockDrawdown }}%</span>
            </div>
            <div class="metric-row">
              <span>回撤阈值</span>
              <span class="metric-val">20%</span>
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
              <span class="metric-val" :class="consecutiveLosses >= 5 ? 'danger' : consecutiveLosses >= 3 ? 'warn' : ''">{{ consecutiveLosses }} 次</span>
            </div>
            <div class="metric-row">
              <span>阈值</span>
              <span class="metric-val">5 次</span>
            </div>
            <el-progress :percentage="consecutiveLosses / 5 * 100" :color="consecutiveLosses > 4 ? '#e74c3c' : consecutiveLosses > 2 ? '#e67e22' : '#27ae60'" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 风险阈值配置表 -->
    <el-card style="margin-top:16px">
      <template #header><span class="section-title">⚙️ 风险阈值配置</span></template>
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
import { computed } from 'vue'

defineOptions({ name: 'DemoRiskAccount' })

const mockDailyLoss = 324000
const mockDrawdown = 15.6
const consecutiveLosses = 2

const dailyLossPercent = computed(() => Math.min(100, (mockDailyLoss / 500000) * 100))
const drawdownPercent = computed(() => Math.min(100, (mockDrawdown / 20) * 100))

const thresholds = [
  { name: '单日亏损超限', threshold: '¥500,000', action: '暂停交易 + 通知', breached: false, description: '当日累计亏损超过阈值时触发' },
  { name: '最大回撤超限', threshold: '20%', action: '熔断 + 通知', breached: false, description: '从最高点回撤超过阈值时触发' },
  { name: '连续亏损次数', threshold: '5次', action: '暂停策略 + 通知', breached: false, description: '连续亏损交易次数超过阈值时触发' },
]
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
