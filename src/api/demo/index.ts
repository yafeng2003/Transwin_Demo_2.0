/**
 * Demo 智能投资系统 - 前端 API 接口定义
 * 所有接口对应后端接口需求文档中的定义
 */
import request from '/@/utils/request'

// ==================== 基础 ====================
export function getHealth() {
  return request({ url: '/api/v1/health', method: 'get' })
}
export function getMarkets() {
  return request({ url: '/api/v1/markets', method: 'get' })
}
export function getAccounts() {
  return request({ url: '/api/v1/accounts', method: 'get' })
}

// ==================== Dashboard ====================
export function getAssetSummary(params?: Record<string, any>) {
  return request({ url: '/api/v1/dashboard/asset-summary', method: 'get', params })
}
export function getPositionOverview(params?: Record<string, any>) {
  return request({ url: '/api/v1/dashboard/position-overview', method: 'get', params })
}
export function getRiskStatus(params?: Record<string, any>) {
  return request({ url: '/api/v1/dashboard/risk-status', method: 'get', params })
}
export function getRecentDeals(params?: Record<string, any>) {
  return request({ url: '/api/v1/dashboard/recent-deals', method: 'get', params })
}

// ==================== 策略展示 - 订单 ====================
export function getOrders(params?: Record<string, any>) {
  return request({ url: '/api/v1/orders', method: 'get', params })
}

// ==================== 策略展示 - 成交 ====================
export function getDeals(params?: Record<string, any>) {
  return request({ url: '/api/v1/deals', method: 'get', params })
}
export function getDealStats(params?: Record<string, any>) {
  return request({ url: '/api/v1/deals/stats', method: 'get', params })
}

// ==================== 策略展示 - 持仓 ====================
export function getCurrentPositions(params?: Record<string, any>) {
  return request({ url: '/api/v1/positions/current', method: 'get', params })
}

// ==================== 策略展示 - 账户 ====================
export function getAccountAssets(params?: Record<string, any>) {
  return request({ url: '/api/v1/account/assets', method: 'get', params })
}

// ==================== 风控 ====================
export function getRiskOverview(params?: Record<string, any>) {
  return request({ url: '/api/v1/risk/overview', method: 'get', params })
}
export function getRiskEvents(params?: Record<string, any>) {
  return request({ url: '/api/v1/risk/events', method: 'get', params })
}
export function getRiskNotifications(params?: Record<string, any>) {
  return request({ url: '/api/v1/risk/notifications', method: 'get', params })
}
export function resolveRiskEvent(data: { id: number }) {
  // 后端暂未提供 resolve 接口，预留对接
  return request({ url: '/api/v1/risk/events/resolve', method: 'post', data })
}

// ==================== 数据分析 ====================
export function getAnalysisReturns(params?: Record<string, any>) {
  return request({ url: '/api/v1/analysis/returns', method: 'get', params })
}
export function getAnalysisTrading(params?: Record<string, any>) {
  return request({ url: '/api/v1/analysis/trades', method: 'get', params })
}
export function getAnalysisStrategy(params?: Record<string, any>) {
  // 后端路径: /api/v1/analysis/strategies (待确认)
  return request({ url: '/api/v1/analysis/strategies', method: 'get', params })
}

// ==================== 报表 ====================
export function getReports(params?: Record<string, any>) {
  return request({ url: '/api/v1/reports', method: 'get', params })
}

// ==================== 日志 ====================
// 交易日志 (后端: /api/v1/logs/trading)
export function getTradeLogs(params?: Record<string, any>) {
  return request({ url: '/api/v1/logs/trading', method: 'get', params })
}
// 订单状态日志 (后端暂未提供，预留对接)
export function getOrderLogs(params?: Record<string, any>) {
  return request({ url: '/api/v1/logs/order', method: 'get', params })
}
// 错误日志 (后端暂未提供，预留对接)
export function getErrorLogs(params?: Record<string, any>) {
  return request({ url: '/api/v1/logs/error', method: 'get', params })
}

// ==================== 人工干预 ====================
export function manualBuy(data: Record<string, any>) {
  return request({ url: '/api/v1/manual/buy', method: 'post', data })
}
export function manualSell(data: Record<string, any>) {
  return request({ url: '/api/v1/manual/sell', method: 'post', data })
}
export function manualModifyOrder(data: Record<string, any>) {
  return request({ url: '/api/v1/manual/modify-order', method: 'post', data })
}
