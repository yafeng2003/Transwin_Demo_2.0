<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>策略分析</h2>
      <p class="page-desc">多策略收益、风险、胜率与贡献度对比。</p>
    </div>

    <!-- 策略对比表格 -->
    <el-card>
      <template #header><span class="section-title">策略绩效对比</span></template>
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="strategyName" label="策略" min-width="140" />
        <el-table-column prop="totalReturn" label="总收益" min-width="110" sortable>
          <template #default="{ row }">
            <span :class="row.totalReturn >= 0 ? 'up' : 'down'">{{ row.totalReturn?.toFixed(2) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="sharpeRatio" label="Sharpe" min-width="100" sortable>
          <template #default="{ row }">{{ row.sharpeRatio?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="maxDrawdown" label="最大回撤" min-width="120" sortable>
          <template #default="{ row }">{{ row.maxDrawdown?.toFixed(2) }}%</template>
        </el-table-column>
        <el-table-column prop="winRate" label="胜率" min-width="100" sortable>
          <template #default="{ row }">{{ row.winRate?.toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="tradeCount" label="交易数" min-width="100" sortable />
        <el-table-column prop="contribution" label="贡献度" min-width="160">
          <template #default="{ row }">
            <el-progress :percentage="row.contribution" :stroke-width="8" :show-text="true" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue'
import { getAnalysisStrategy } from '/@/api/demo/index'
import { useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoAnalysisStrategy' })
const demoStore = useDemoStore()

const loading = ref(false)
const list = ref<any[]>([])

async function fetchData() {
  loading.value = true
  try {
    const strategyIds = demoStore.availableStrategies.length ? demoStore.availableStrategies : [demoStore.strategyId]
    const res = await getAnalysisStrategy({ market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_ids: strategyIds })
    list.value = res.data
  } finally { loading.value = false }
}

onMounted(fetchData)
watch(() => demoStore.switchVersion, fetchData)
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.section-title { font-weight: 600; font-size: 15px; }
.up { color: #e74c3c; }
.down { color: #27ae60; }
</style>
