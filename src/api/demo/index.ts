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
export function getAnalysisRisk(params?: Record<string, any>) {
  return request({ url: '/api/v1/analysis/risk', method: 'get', params })
}
export function getAnalysisTrading(params?: Record<string, any>) {
  return request({ url: '/api/v1/analysis/trading', method: 'get', params })
}
export function getAnalysisStrategy(params?: Record<string, any>) {
  return request({ url: '/api/v1/analysis/strategy', method: 'get', params })
}

// ==================== 报表 ====================
export function getReports(params?: Record<string, any>) {
  return request({ url: '/api/v1/reports', method: 'get', params })
}
export function exportReport(id: number, format: string = 'pdf') {
  return request({ url: `/api/v1/reports/${id}/export`, method: 'get', params: { format } })
}

// ==================== 日志 ====================
// 系统日志 (v2.0 新增)
export function getSystemLogs(params?: Record<string, any>) {
  return request({ url: '/api/v1/logs/system', method: 'get', params })
}
// 交易日志
export function getTradeLogs(params?: Record<string, any>) {
  return request({ url: '/api/v1/logs/trading', method: 'get', params })
}
// 兼容旧版（订单日志已合并到交易日志，错误日志改为系统日志）
export function getOrderLogs(params?: Record<string, any>) {
  return request({ url: '/api/v1/logs/trading', method: 'get', params: { ...params, type: 'order' } })
}
export function getErrorLogs(params?: Record<string, any>) {
  return request({ url: '/api/v1/logs/system', method: 'get', params: { ...params, level: 'ERROR' } })
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
