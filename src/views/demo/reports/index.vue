<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>📋 报表中心</h2>
      <p class="page-desc">展示后端生成的日报、周报、月报，支持导出 PDF / Excel / CSV。</p>
    </div>

    <el-card>
      <el-tabs v-model="reportType" @tab-change="fetchData">
        <el-tab-pane label="日报" name="daily" />
        <el-tab-pane label="周报" name="weekly" />
        <el-tab-pane label="月报" name="monthly" />
      </el-tabs>

      <!-- 报表预览卡片 -->
      <el-row :gutter="16" v-if="list.length > 0">
        <el-col :span="12">
          <el-card class="preview-card">
            <template #header>
              <span>📄 {{ list[0]?.title }}</span>
              <span style="float:right; color:#909399; font-size:12px">{{ list[0]?.createdAt }}</span>
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
                <vab-chart :option="miniNavOption" style="height:100px" />
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 报表列表 -->
        <el-col :span="12">
          <el-table :data="list" stripe size="small" max-height="400">
            <el-table-column prop="title" label="报表标题" min-width="180" />
            <el-table-column prop="createdAt" label="生成时间" width="120" />
            <el-table-column prop="fileSize" label="大小" width="80" />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status === 'generated' ? 'success' : 'warning'" size="small">
                  {{ row.status === 'generated' ? '已生成' : '生成中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template>
                <el-button text type="primary" size="small">预览</el-button>
                <el-button text type="success" size="small">PDF</el-button>
                <el-button text size="small">Excel</el-button>
                <el-button text size="small">CSV</el-button>
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
    grid: { top: 5, right: 5, bottom: 10, left: 40 },
    xAxis: { show: false, data: Array.from({ length: 30 }, (_, i) => i) },
    yAxis: { show: true, splitLine: { show: false }, axisLabel: { fontSize: 9 } },
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
.preview-card { border: 1px solid #e4e7ed; }
.preview-content { font-size: 13px; }
.preview-section { margin-bottom: 12px; }
.preview-section h4 { margin: 0 0 6px 0; font-size: 14px; color: #303133; }
.preview-section p { margin: 2px 0; color: #606266; }

</style>
