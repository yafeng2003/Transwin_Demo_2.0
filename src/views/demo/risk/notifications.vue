<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>🔔 风险通知中心</h2>
      <p class="page-desc">展示风险报警、熔断通知、异常通知与策略暂停通知记录。</p>
    </div>

    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="风险报警" name="risk_alert" />
        <el-tab-pane label="熔断通知" name="circuit_breaker" />
        <el-tab-pane label="异常通知" name="anomaly" />
        <el-tab-pane label="策略暂停" name="strategy_pause" />
      </el-tabs>

      <el-table :data="filteredList" stripe v-loading="loading" max-height="500" @row-click="showDetail">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="状态" width="70">
          <template #default="{ row }">
            <el-icon v-if="!row.isRead" color="#e74c3c"><WarningFilled /></el-icon>
            <el-icon v-else color="#909399"><CircleCheckFilled /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="typeLabel" label="类型" width="110">
          <template #default="{ row }">
            <el-tag :type="row.type === 'risk_alert' ? 'danger' : row.type === 'circuit_breaker' ? 'danger' : row.type === 'anomaly' ? 'warning' : 'info'" size="small">
              {{ row.typeLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="70">
          <template #default="{ row }">
            <el-tag :type="row.level >= 3 ? 'danger' : row.level === 2 ? 'warning' : 'info'" size="small">
              {{ ['', '低', '中', '高'][row.level] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="250" />
        <el-table-column prop="createdAt" label="时间" width="170" />
        <el-table-column label="操作" width="100">
          <template><el-button text type="primary" size="small">查看</el-button></template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page" v-model:page-size="size"
          :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
          @size-change="fetchData" @current-change="fetchData" />
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { CircleCheckFilled, WarningFilled } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { getRiskNotifications } from '/@/api/demo/index'

defineOptions({ name: 'DemoRiskNotifications' })

const loading = ref(false)
const list = ref<any[]>([])
const activeTab = ref('all')
const page = ref(1)
const size = ref(20)
const total = ref(0)

const filteredList = computed(() =>
  activeTab.value === 'all' ? list.value : list.value.filter((i: any) => i.type === activeTab.value)
)

function showDetail(row: any) {
  // demo: just mark as read
  row.isRead = true
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getRiskNotifications({ page: page.value, size: size.value })
    list.value = res.data.list
    total.value = res.data.total
  } finally { loading.value = false }
}

onMounted(fetchData)
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
