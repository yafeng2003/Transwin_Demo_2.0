/**
 * Demo 智能投资系统 - 前端 API 接口定义
 * 所有接口对应后端接口需求文档中的定义
 */
import request from '/@/utils/request'

// ==================== 基础 ====================
export function getHealth() {
  return request({ url: '/api/demo/health', method: 'get' })
}
export function getMarkets() {
  return request({ url: '/api/demo/markets', method: 'get' })
}
export function getAccounts() {
  return request({ url: '/api/demo/accounts', method: 'get' })
}

// ==================== Dashboard ====================
export function getAssetSummary(params?: Record<string, any>) {
  return request({ url: '/api/demo/dashboard/asset-summary', method: 'get', params })
}
export function getPositionOverview(params?: Record<string, any>) {
  return request({ url: '/api/demo/dashboard/position-overview', method: 'get', params })
}
export function getRiskStatus(params?: Record<string, any>) {
  return request({ url: '/api/demo/dashboard/risk-status', method: 'get', params })
}
export function getRecentDeals(params?: Record<string, any>) {
  return request({ url: '/api/demo/dashboard/recent-deals', method: 'get', params })
}

// ==================== 策略展示 - 订单 ====================
export function getOrders(params?: Record<string, any>) {
  return request({ url: '/api/demo/orders', method: 'get', params })
}

// ==================== 策略展示 - 成交 ====================
export function getDeals(params?: Record<string, any>) {
  return request({ url: '/api/demo/deals', method: 'get', params })
}
export function getDealStats(params?: Record<string, any>) {
  return request({ url: '/api/demo/deals/stats', method: 'get', params })
}

// ==================== 策略展示 - 持仓 ====================
export function getCurrentPositions(params?: Record<string, any>) {
  return request({ url: '/api/demo/positions/current', method: 'get', params })
}

// ==================== 策略展示 - 账户 ====================
export function getAccountAssets(params?: Record<string, any>) {
  return request({ url: '/api/demo/account/assets', method: 'get', params })
}

// ==================== 风控 ====================
export function getRiskOverview(params?: Record<string, any>) {
  return request({ url: '/api/demo/risk/overview', method: 'get', params })
}
export function getRiskEvents(params?: Record<string, any>) {
  return request({ url: '/api/demo/risk/events', method: 'get', params })
}
export function getRiskNotifications(params?: Record<string, any>) {
  return request({ url: '/api/demo/risk/notifications', method: 'get', params })
}

// ==================== 数据分析 ====================
export function getAnalysisReturns(params?: Record<string, any>) {
  return request({ url: '/api/demo/analysis/returns', method: 'get', params })
}
export function getAnalysisTrading(params?: Record<string, any>) {
  return request({ url: '/api/demo/analysis/trading', method: 'get', params })
}
export function getAnalysisStrategy(params?: Record<string, any>) {
  return request({ url: '/api/demo/analysis/strategy', method: 'get', params })
}

// ==================== 报表 ====================
export function getReports(params?: Record<string, any>) {
  return request({ url: '/api/demo/reports', method: 'get', params })
}

// ==================== 日志 ====================
export function getSystemLogs(params?: Record<string, any>) {
  return request({ url: '/api/demo/logs/system', method: 'get', params })
}
export function getTradingLogs(params?: Record<string, any>) {
  return request({ url: '/api/demo/logs/trading', method: 'get', params })
}

// ==================== 人工干预 ====================
export function manualBuy(data: Record<string, any>) {
  return request({ url: '/api/demo/manual/buy', method: 'post', data })
}
export function manualSell(data: Record<string, any>) {
  return request({ url: '/api/demo/manual/sell', method: 'post', data })
}
export function manualModifyOrder(data: Record<string, any>) {
  return request({ url: '/api/demo/manual/modify-order', method: 'post', data })
}
