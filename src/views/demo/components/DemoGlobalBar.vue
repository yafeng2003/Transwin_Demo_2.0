<template>
  <el-row :gutter="16" class="demo-global-bar">
    <el-col :span="6">
      <el-select
        v-model="demoStore.marketId"
        placeholder="选择市场"
        @change="$emit('change')"
      >
        <el-option v-if="showAllMarkets" label="🌐 全市场总览" :value="0" />
        <el-option v-for="m in demoStore.markets" :key="m.id" :label="m.name" :value="m.id" />
      </el-select>
    </el-col>
    <el-col :span="6">
      <el-select
        v-model="demoStore.accountId"
        placeholder="选择账户"
        @change="$emit('change')"
      >
        <el-option v-for="a in demoStore.accounts" :key="a.id" :label="a.label" :value="a.id" />
      </el-select>
    </el-col>
    <el-col :span="12" class="text-right">
      <el-tag :type="health.status === 'running' ? 'success' : 'danger'" size="large">
        系统状态：{{ health.status === 'running' ? '运行中' : '异常' }}
      </el-tag>
      <span class="health-detail">
        策略{{ health.services?.strategy === 'ok' ? '✓' : '✗' }}
        执行{{ health.services?.executor === 'ok' ? '✓' : '✗' }}
        风控{{ health.services?.risk === 'ok' ? '✓' : '✗' }}
      </span>
    </el-col>
  </el-row>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { getHealth } from '/@/api/demo/index'
import { useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoGlobalBar' })

const props = defineProps<{ showAllMarkets?: boolean }>()
defineEmits<{ change: [] }>()

const demoStore = useDemoStore()
const health = ref<any>({ status: 'loading', services: {} })

// 离开总览页面时，如果还是"全市场总览"则重置为第一个市场
watch(() => props.showAllMarkets, (val) => {
  if (!val && demoStore.marketId === 0 && demoStore.markets.length > 0) {
    demoStore.marketId = demoStore.markets[0].id
  }
})

onMounted(async () => {
  await demoStore.fetchMarketsAndAccounts()
  try {
    const hRes = await getHealth()
    health.value = hRes.data
  } catch { /* ignore */ }
})
</script>

<style scoped>
.demo-global-bar {
  margin-bottom: 16px;
  align-items: center;
}
.demo-global-bar .text-right {
  text-align: right;
}
.health-detail {
  margin-left: 12px;
  color: #909399;
  font-size: 13px;
}
</style>
