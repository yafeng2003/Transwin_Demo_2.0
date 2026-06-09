<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>报表中心</h2>
      <p class="page-desc">展示后端生成的日报、周报、月报，支持导出 PDF / Excel / CSV。</p>
    </div>

    <el-card>
      <el-tabs v-model="reportType" @tab-change="fetchData">
        <el-tab-pane label="日报" name="daily" />
        <el-tab-pane label="周报" name="weekly" />
        <el-tab-pane label="月报" name="monthly" />
      </el-tabs>

      <!-- 报表预览卡片 -->
      <el-row :gutter="16" v-if="list.length > 0" class="report-grid">
        <el-col :span="10">
          <el-card class="preview-card">
            <template #header>
              <div class="preview-title">
                <span>{{ list[0]?.title }}</span>
                <span>{{ list[0]?.createdAt }}</span>
              </div>
            </template>
            <div class="preview-content">
              <div class="preview-section">
                <h4>当日交易记录</h4>
                <p>交易笔数：{{ mockDaily.tradeCount }} 笔</p>
                <p>成交均价：¥{{ mockDaily.avgPrice }}</p>
                <p>总成交金额：¥{{ mockDaily.totalAmount.toLocaleString() }}</p>
              </div>
              <div class="preview-section">
                <h4>持仓结构</h4>
                <p v-for="h in mockDaily.holdings" :key="h.name">{{ h.name }}：{{ h.ratio }}%</p>
              </div>
              <div class="preview-section">
                <h4>净值曲线</h4>
                <vab-chart :option="miniNavOption" class="demo-chart-mini" />
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 报表列表 -->
        <el-col :span="14">
          <el-table :data="list" stripe size="small" max-height="400">
            <el-table-column prop="title" label="报表标题" min-width="160" />
            <el-table-column prop="createdAt" label="生成时间" width="112" />
            <el-table-column prop="fileSize" label="大小" width="76" />
            <el-table-column prop="status" label="状态" width="86">
              <template #default="{ row }">
                <span class="status-badge" :class="row.status === 'generated' ? 'is-success' : 'is-warning'">
                  {{ row.status === 'generated' ? '已生成' : '生成中' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="168">
              <template #default>
                <div class="report-actions">
                  <button type="button">预览</button>
                  <button type="button">PDF</button>
                  <button type="button">Excel</button>
                  <button type="button">CSV</button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { getReports } from '/@/api/demo/index'

defineOptions({ name: 'DemoReports' })

const reportType = ref('daily')
const list = ref<any[]>([])

const mockDaily = {
  tradeCount: 12,
  avgPrice: '38.52',
  totalAmount: 4523800,
  holdings: [
    { name: '金融', ratio: 35 },
    { name: '科技', ratio: 28 },
    { name: '消费', ratio: 20 },
    { name: '其他', ratio: 17 },
  ],
}

const miniNavOption = computed(() => {
  const data = Array.from({ length: 30 }, () => 1.0 + Math.random() * 0.5)
  return {
    grid: { top: 8, right: 8, bottom: 14, left: 40, containLabel: true },
    xAxis: { show: false, data: Array.from({ length: 30 }, (_, i) => i) },
    yAxis: { show: true, splitLine: { show: false }, axisLabel: { fontSize: 10, color: '#7a8699' } },
    series: [{ type: 'line', data, smooth: true, lineStyle: { color: '#409EFF', width: 1.5 }, areaStyle: { color: 'rgba(64,158,255,0.1)' }, symbol: 'none' }],
  }
})

async function fetchData() {
  const res = await getReports({ type: reportType.value })
  list.value = res.data
}

onMounted(fetchData)
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.preview-card { border: 1px solid #e8edf5; }
.report-grid { align-items: stretch; }
.preview-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.preview-title span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.preview-title span:last-child {
  flex: none;
  color: #909399;
  font-size: 12px;
}
.preview-content { font-size: 13px; }
.preview-section {
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f3f8;
}
.preview-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: 0;
}
.preview-section h4 { margin: 0 0 8px 0; font-size: 14px; color: #243142; }
.preview-section p { margin: 4px 0; color: #606f82; line-height: 1.55; }
.status-badge {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 22px;
}
.status-badge.is-success {
  color: #27824c;
  background: #eaf7ef;
}
.status-badge.is-warning {
  color: #9a6400;
  background: #fff5df;
}
.report-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}
.report-actions button {
  appearance: none;
  padding: 0 2px;
  color: #4f7fe8;
  font-size: 12px;
  line-height: 24px;
  background: transparent;
  border: 0;
  cursor: pointer;
}

</style>
