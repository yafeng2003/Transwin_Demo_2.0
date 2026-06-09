<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>账户中心</h2>
      <p class="page-desc">展示账户资产状况与历史变化记录。</p>
    </div>

    <!-- 资产卡片 -->
    <el-row :gutter="16" class="asset-cards">
      <el-col :span="6">
        <el-card shadow="hover"><div class="card-label">总资产</div><div class="card-value">{{ formatMoney(current.totalAsset) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="card-label">净值</div><div class="card-value">{{ current.netValue?.toFixed(4) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="card-label">持仓市值</div><div class="card-value">{{ formatMoney(current.marketValue) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="card-label">现金余额</div><div class="card-value">{{ formatMoney(current.cashBalance) }}</div></el-card>
      </el-col>
    </el-row>

    <!-- 净值走势 + 资产变化记录 -->
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card>
          <template #header><span class="section-title">资产净值走势（近30日）</span></template>
          <vab-chart :option="navOption" class="demo-chart-md" />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <template #header><span class="section-title">资产变化记录</span></template>
          <el-table :data="history.slice(-10).reverse()" stripe size="small" max-height="360">
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="totalAsset" label="总资产" width="120">
              <template #default="{ row }">{{ formatMoney(row.totalAsset) }}</template>
            </el-table-column>
            <el-table-column prop="netValue" label="净值" width="90">
              <template #default="{ row }">{{ row.netValue?.toFixed(4) }}</template>
            </el-table-column>
            <el-table-column label="变化" width="80">
              <template #default="{ row, $index }">
                <span v-if="$index < history.slice(-10).reverse().length - 1" :class="(row.netValue - history.slice(-10).reverse()[$index + 1]?.netValue) >= 0 ? 'up' : 'down'">
                  {{ ((row.netValue - history.slice(-10).reverse()[$index + 1]?.netValue) * 100).toFixed(2) }}%
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { getAccountAssets } from '/@/api/demo/index'

defineOptions({ name: 'DemoStrategyAccount' })

const history = ref<any[]>([])
const current = ref<any>({})

const formatMoney = (v: number) => {
  if (v == null) return '-'
  return (v >= 0 ? '¥' : '-¥') + Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const navOption = computed(() => ({
  grid: { top: 28, right: 28, bottom: 40, left: 52, containLabel: true },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: history.value.map((h: any) => h.date), axisLabel: { rotate: 45, fontSize: 10 } },
  yAxis: { type: 'value', name: '净值' },
  series: [{
    type: 'line',
    data: history.value.map((h: any) => h.netValue),
    smooth: true,
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(64,158,255,0.3)' }, { offset: 1, color: 'rgba(64,158,255,0.02)' }] } },
    lineStyle: { color: '#409EFF', width: 2 },
    itemStyle: { color: '#409EFF' },
  }],
}))

onMounted(async () => {
  const res = await getAccountAssets({ days: 30 })
  history.value = res.data.history
  current.value = res.data.current
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.asset-cards { margin-bottom: 16px; }
.asset-cards .card-label { font-size: 13px; color: #909399; }
.asset-cards .card-value { font-size: 22px; font-weight: 700; margin-top: 4px; }
.section-title { font-weight: 600; font-size: 15px; }
.up { color: #e74c3c; }
.down { color: #27ae60; }
.chart-placeholder { padding: 8px 0; }
.chart-mock { display: flex; align-items: flex-end; height: 280px; gap: 2px; }
.chart-bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.chart-bar { width: 100%; max-width: 20px; background: linear-gradient(180deg, #e74c3c 0%, #409EFF 100%); border-radius: 2px 2px 0 0; min-height: 2px; }
.chart-label { font-size: 10px; color: #909399; margin-top: 4px; transform: rotate(-45deg); white-space: nowrap; }
</style>
