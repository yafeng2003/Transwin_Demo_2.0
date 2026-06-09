<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>策略分析</h2>
      <p class="page-desc">多策略收益/风险对比、贡献度分析与相关性矩阵。</p>
    </div>

    <div class="compact-row">
    <!-- 策略对比表格 -->
    <el-card class="fit-card">
      <template #header><span class="section-title">策略绩效对比</span></template>
      <el-table :data="list" stripe v-loading="loading" style="width: 610px">
        <el-table-column prop="strategyName" label="策略" width="134" />
        <el-table-column prop="totalReturn" label="总收益" width="84">
          <template #default="{ row }">
            <span :class="row.totalReturn >= 0 ? 'up' : 'down'">{{ row.totalReturn?.toFixed(2) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="sharpeRatio" label="Sharpe" width="76">
          <template #default="{ row }">{{ row.sharpeRatio?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="maxDrawdown" label="最大回撤" width="86">
          <template #default="{ row }">{{ row.maxDrawdown?.toFixed(2) }}%</template>
        </el-table-column>
        <el-table-column prop="winRate" label="胜率" width="70">
          <template #default="{ row }">{{ row.winRate?.toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="tradeCount" label="交易数" width="68" />
        <el-table-column prop="contribution" label="贡献度" width="92">
          <template #default="{ row }">
            <el-progress :percentage="row.contribution" :stroke-width="8" :show-text="true" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 相关性矩阵 -->
    <el-card class="fit-card">
      <template #header><span class="section-title">策略相关性矩阵</span></template>
      <div class="corr-matrix" v-if="list.length > 0">
        <div class="corr-header">
          <div class="corr-empty" />
          <div v-for="s in list" :key="s.strategyId" class="corr-col-label">{{ s.strategyName }}</div>
        </div>
        <div v-for="row in list" :key="row.strategyId" class="corr-row">
          <div class="corr-row-label">{{ row.strategyName }}</div>
          <div v-for="col in list" :key="col.strategyId" class="corr-cell">
            <div v-if="row.correlation" class="corr-value" :style="{ background: corrColor(row.correlation.find((c: any) => c.strategy === col.strategyId)?.value || 0) }">
              {{ row.correlation.find((c: any) => c.strategy === col.strategyId)?.value?.toFixed(2) || '-' }}
            </div>
          </div>
        </div>
      </div>
    </el-card>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { getAnalysisStrategy } from '/@/api/demo/index'

defineOptions({ name: 'DemoAnalysisStrategy' })

const loading = ref(false)
const list = ref<any[]>([])

function corrColor(v: number) {
  if (v > 0.5) return 'rgba(231,76,60,0.6)'
  if (v > 0) return 'rgba(230,126,34,0.4)'
  if (v > -0.3) return 'rgba(149,165,166,0.3)'
  return 'rgba(39,174,96,0.5)'
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getAnalysisStrategy()
    list.value = res.data
  } finally { loading.value = false }
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.section-title { font-weight: 600; font-size: 15px; }
.up { color: #e74c3c; }
.down { color: #27ae60; }
/* 绩效表 + 相关性矩阵 紧凑并排一行 */
.compact-row { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
.compact-row .fit-card { flex: 0 0 auto; width: fit-content; }
.corr-matrix { overflow-x: auto; }
.corr-header, .corr-row { display: flex; }
.corr-empty, .corr-row-label { width: 102px; min-width: 102px; padding: 8px 6px; font-weight: 600; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.corr-col-label { width: 66px; min-width: 66px; padding: 8px 4px; font-weight: 600; font-size: 11px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.corr-cell { width: 66px; min-width: 66px; padding: 4px; }
.corr-value { text-align: center; padding: 8px 4px; border-radius: 4px; font-size: 12px; font-weight: 600; color: #fff; }
</style>
