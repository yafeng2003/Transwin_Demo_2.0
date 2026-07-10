<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>人工干预</h2>
      <p class="page-desc">手动提交买入、卖出、改单操作，后端通过 is_manual 标记区分系统成交与人工成交。</p>
    </div>

    <el-row :gutter="16">
      <!-- 买入表单 -->
      <el-col :span="8">
        <el-card>
          <template #header><span class="section-title">买入</span></template>
          <el-form :model="buyForm" label-width="80px" size="default">
            <el-form-item label="市场">
              <el-select v-model="buyForm.marketId" style="width:100%" @change="onMarketChange">
                <el-option v-for="m in demoStore.markets" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="账户">
              <el-select v-model="buyForm.accountId" style="width:100%" @change="onAccountChange">
                <el-option v-for="a in demoStore.accounts" :key="a.id" :label="a.label || a.name || a.id" :value="a.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="股票代码">
              <el-input v-model="buyForm.symbolCode" placeholder="如 00005" />
            </el-form-item>
            <el-form-item label="价格类型">
              <el-radio-group v-model="buyForm.orderType">
                <el-radio :value="1">市价</el-radio>
                <el-radio :value="2">限价</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="价格" v-if="buyForm.orderType === 2">
              <el-input v-model="buyForm.price" placeholder="委托价格" />
            </el-form-item>
            <el-form-item label="数量">
              <el-input v-model="buyForm.quantity" placeholder="委托数量（股）" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="submitBuy" :loading="submitting">提交买入</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 卖出表单 -->
      <el-col :span="8">
        <el-card>
          <template #header><span class="section-title">卖出</span></template>
          <el-form :model="sellForm" label-width="80px" size="default">
            <el-form-item label="市场">
              <el-select v-model="sellForm.marketId" style="width:100%" @change="onMarketChange">
                <el-option v-for="m in demoStore.markets" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="账户">
              <el-select v-model="sellForm.accountId" style="width:100%" @change="onAccountChange">
                <el-option v-for="a in demoStore.accounts" :key="a.id" :label="a.label || a.name || a.id" :value="a.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="持仓选择">
              <el-select v-model="sellForm.symbolCode" placeholder="从持仓中选择" style="width:100%" filterable @change="(val: string) => {
                const pos = positions.find(p => p.symbolCode === val)
                if (pos) onSellPositionSelect(pos)
              }">
                <el-option v-for="p in positions" :key="p.symbolCode"
                  :label="`${p.symbolCode} | ${p.direction===1?'多':'空'} | ${p.holdingQuantity}股`"
                  :value="p.symbolCode" />
              </el-select>
            </el-form-item>
            <el-form-item label="股票代码">
              <el-input v-model="sellForm.symbolCode" placeholder="或手动输入代码" />
            </el-form-item>
            <el-form-item label="价格类型">
              <el-radio-group v-model="sellForm.orderType">
                <el-radio :value="1">市价</el-radio>
                <el-radio :value="2">限价</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="价格" v-if="sellForm.orderType === 2">
              <el-input v-model="sellForm.price" placeholder="委托价格" />
            </el-form-item>
            <el-form-item label="数量">
              <el-input v-model="sellForm.quantity" placeholder="委托数量（股），填0为全部" />
            </el-form-item>
            <el-form-item>
              <el-button type="danger" @click="submitSell" :loading="submitting">提交卖出</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 改单表单 + 操作结果 -->
      <el-col :span="8">
        <el-card>
          <template #header><span class="section-title">改单</span></template>
          <el-form :model="modifyForm" label-width="80px" size="default">
            <el-form-item label="选择订单">
              <el-select v-model="modifyForm.orderId" placeholder="从活跃订单中选择" style="width:100%" filterable @change="(val: string) => {
                const order = orders.find(o => o.id?.toString() === val)
                if (order) onModifyOrderSelect(order)
              }">
                <el-option v-for="o in orders" :key="o.id"
                  :label="`#${o.id} ${o.symbolCode} ${o.direction===1?'多':'空'} ${o.quantity}股`"
                  :value="o.id?.toString()" />
              </el-select>
            </el-form-item>
            <el-form-item label="账户">
              <el-select v-model="modifyForm.accountId" style="width:100%" @change="onAccountChange">
                <el-option v-for="a in demoStore.accounts" :key="a.id" :label="a.label || a.name || a.id" :value="a.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="订单ID">
              <el-input v-model="modifyForm.orderId" placeholder="或手动输入订单ID" />
            </el-form-item>
            <el-form-item label="新价格">
              <el-input v-model="modifyForm.price" placeholder="修改后的价格（留空不变）" />
            </el-form-item>
            <el-form-item label="新数量">
              <el-input v-model="modifyForm.quantity" placeholder="修改后的数量（留空不变）" />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="submitModify" :loading="submitting">提交修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 操作结果 -->
        <el-card v-if="lastResult" style="margin-top:16px" class="result-card">
          <template #header><span class="section-title">操作结果</span></template>
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="订单ID">{{ lastResult.orderId }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="lastResult.status === 'submitted' ? 'success' : 'warning'" size="small">
                {{ lastResult.status === 'submitted' ? '已提交' : lastResult.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="消息">{{ lastResult.message }}</el-descriptions-item>
            <el-descriptions-item label="时间">{{ lastResult.dealTime || lastResult.modifyTime }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref, watch } from 'vue'
import { getCurrentPositions, getOrders, manualBuy, manualModifyOrder, manualSell } from '/@/api/demo/index'
import { useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoManual' })

const demoStore = useDemoStore()
const submitting = ref(false)
const lastResult = ref<any>(null)
const positions = ref<any[]>([])
const orders = ref<any[]>([])

const buyForm = reactive({ marketId: 2, accountId: 'ggt', symbolCode: '', orderType: 1, price: '', quantity: '' })
const sellForm = reactive({ marketId: 2, accountId: 'ggt', symbolCode: '', orderType: 1, price: '', quantity: '' })
const modifyForm = reactive({ orderId: '', accountId: 'ggt', price: '', quantity: '' })

function syncSelectionToForms() {
  buyForm.marketId = demoStore.marketId || 2
  sellForm.marketId = demoStore.marketId || 2
  buyForm.accountId = demoStore.accountId || ''
  sellForm.accountId = demoStore.accountId || ''
  modifyForm.accountId = demoStore.accountId || ''
}

async function loadPositions() {
  try {
    const res = await getCurrentPositions({ market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId })
    positions.value = res.data || []
  } catch { positions.value = [] }
}

async function loadOrders() {
  try {
    const res = await getOrders({ page: 1, size: 100, market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId })
    orders.value = (res.data.list || []).filter((o: any) => [0, 3].includes(o.status))
  } catch { orders.value = [] }
}

async function reloadRelatedData() {
  await Promise.all([loadPositions(), loadOrders()])
}

async function onMarketChange(marketId: number) {
  await demoStore.switchMarket(marketId)
  syncSelectionToForms()
  await reloadRelatedData()
}

async function onAccountChange(accountId: string) {
  demoStore.switchAccount(accountId)
  syncSelectionToForms()
  await reloadRelatedData()
}

function onSellPositionSelect(pos: any) {
  sellForm.symbolCode = pos.symbolCode
  sellForm.quantity = pos.holdingQuantity?.toString() || ''
}

function onModifyOrderSelect(order: any) {
  modifyForm.orderId = order.id?.toString() || ''
  modifyForm.price = order.price?.toString() || ''
  modifyForm.quantity = order.quantity?.toString() || ''
  modifyForm.accountId = order.accountId || 'ggt'
}

async function submitBuy() {
  submitting.value = true
  try {
    const res = await manualBuy({ ...buyForm })
    lastResult.value = res.data
    ElMessage.success('买入委托已提交')
  } catch { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

async function submitSell() {
  submitting.value = true
  try {
    const res = await manualSell({ ...sellForm })
    lastResult.value = res.data
    ElMessage.success('卖出委托已提交')
  } catch { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

async function submitModify() {
  submitting.value = true
  try {
    const res = await manualModifyOrder({ ...modifyForm })
    lastResult.value = res.data
    ElMessage.success('订单修改成功')
  } catch { ElMessage.error('修改失败') }
  finally { submitting.value = false }
}

onMounted(async () => {
  if (demoStore.markets.length === 0) await demoStore.fetchMarketsAndAccounts()
  syncSelectionToForms()
  await reloadRelatedData()
})

watch(() => demoStore.switchVersion, async () => {
  syncSelectionToForms()
  await reloadRelatedData()
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.section-title { font-weight: 600; font-size: 15px; }
.result-card { border: 1px solid #67C23A; }
</style>
