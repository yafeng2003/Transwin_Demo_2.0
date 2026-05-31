<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>📊 交易分析</h2>
      <p class="page-desc">分析交易胜率、盈亏比、交易频率、手续费与滑点等交易执行质量指标。</p>
    </div>

    <!-- 指标卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">胜率</div><div class="stat-value">{{ data.winRate?.toFixed(1) }}%</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">盈亏比</div><div class="stat-value">{{ data.profitLossRatio?.toFixed(2) }}</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">平均盈利</div><div class="stat-value up">¥{{ data.avgProfit?.toLocaleString() }}</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">平均亏损</div><div class="stat-value down">¥{{ Math.abs(data.avgLoss)?.toLocaleString() }}</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">交易次数</div><div class="stat-value">{{ data.tradeCount }}</div></el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover"><div class="stat-label">总手续费</div><div class="stat-value">¥{{ data.totalCommission?.toLocaleString() }}</div></el-card>
      </el-col>
    </el-row>

    <!-- 月度交易统计 -->
    <el-card style="margin-top:16px">
      <template #header><span class="section-title">📅 月度交易统计</span></template>
      <el-table :data="data.monthlyTrades || []" stripe size="small">
        <el-table-column prop="month" label="月份" width="120" />
        <el-table-column prop="count" label="交易次数" width="120" />
        <el-table-column prop="winRate" label="胜率" width="120">
          <template #default="{ row }">{{ row.winRate?.toFixed(1) }}%</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 频率与滑点 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header><span class="section-title">⏱ 交易频率（日均）</span></template>
          <div class="big-number">{{ data.tradeFrequency?.toFixed(1) }} 笔/天</div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span class="section-title">📏 滑点分析</span></template>
          <div class="big-number">{{ data.slippage?.toFixed(2) }}%</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { getAnalysisTrading } from '/@/api/demo/index'

defineOptions({ name: 'DemoAnalysisTrading' })

const data = ref<any>({})

onMounted(async () => {
  const res = await getAnalysisTrading()
  data.value = res.data
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
.big-number { font-size: 32px; font-weight: 700; text-align: center; padding: 24px 0; color: #303133; }
</style>
