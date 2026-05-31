/**
 * Demo 智能投资系统 - Mock 数据
 * 覆盖：Dashboard、策略展示、风控展示、数据分析、报表、日志、人工干预
 */
import type { MockMethod } from 'vite-plugin-mock'

// ==================== 工具函数 ====================
const randomNum = (min: number, max: number, decimals = 2) =>
  parseFloat((Math.random() * (max - min) + min).toFixed(decimals))

const randomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min

const randomPick = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)]

const dayBefore = (n: number) => {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d.toISOString().split('T')[0]
}

const nowDateTime = () => new Date().toISOString().replace('T', ' ').slice(0, 19)

// ==================== 种子数据 ====================
const stocks = [
  { code: '000001', name: '平安银行' },
  { code: '600519', name: '贵州茅台' },
  { code: '000858', name: '五粮液' },
  { code: '300750', name: '宁德时代' },
  { code: '601318', name: '中国平安' },
  { code: '600036', name: '招商银行' },
  { code: '002415', name: '海康威视' },
  { code: '000333', name: '美的集团' },
  { code: '00700', name: '腾讯控股' },
  { code: '09988', name: '阿里巴巴' },
  { code: '01810', name: '小米集团' },
  { code: '09618', name: '京东集团' },
]

const strategies = ['ma_cross', 'momentum_v1', 'mean_reversion', 'ml_predictor']
const accounts = ['acc_main', 'acc_growth', 'acc_hedge']
const markets = [
  { id: 1, name: '沪深A股' },
  { id: 2, name: '港股' },
]

const directionMap: Record<number, string> = { 1: '多头', 2: '空头' }
const orderTypeMap: Record<number, string> = { 1: '市价', 2: '限价' }
const statusMap: Record<number, string> = { 0: '待执行', 1: '已成交', 2: '失败', 3: '部分成交', 4: '已撤销' }

// ==================== Mock 接口 ====================
export default [
  // ---------- 基础 ----------
  {
    url: '/api/demo/health',
    method: 'get',
    response: () => ({
      code: 200,
      data: {
        status: 'running',
        services: { strategy: 'ok', executor: 'ok', risk: 'ok', analysis: 'ok' },
        lastSync: nowDateTime(),
        uptime: `${randomInt(1, 30)}d ${randomInt(0, 23)}h`,
      },
    }),
  },
  {
    url: '/api/demo/markets',
    method: 'get',
    response: () => ({ code: 200, data: markets }),
  },
  {
    url: '/api/demo/accounts',
    method: 'get',
    response: () => ({
      code: 200,
      data: accounts.map((a) => ({ id: a, name: a, label: a.replace('acc_', '').toUpperCase() })),
    }),
  },

  // ---------- Dashboard ----------
  {
    url: '/api/demo/dashboard/asset-summary',
    method: 'get',
    response: () => ({
      code: 200,
      data: {
        totalAsset: randomNum(5000000, 20000000),
        netValue: randomNum(1.05, 2.5),
        todayPnl: randomNum(-50000, 80000),
        totalPnl: randomNum(200000, 2000000),
        marketValue: randomNum(3000000, 15000000),
        cashBalance: randomNum(500000, 3000000),
        todayReturnRate: randomNum(-3, 5),
        totalReturnRate: randomNum(5, 80),
      },
    }),
  },
  {
    url: '/api/demo/dashboard/position-overview',
    method: 'get',
    response: () => {
      const list = stocks.slice(0, 6).map((s) => ({
        symbolCode: s.code,
        symbolName: s.name,
        direction: randomPick([1, 1, 1, 2]),
        quantity: randomInt(1000, 50000),
        avgPrice: randomNum(10, 500),
        marketValue: randomNum(100000, 3000000),
        unrealizedPnl: randomNum(-50000, 100000),
        weight: 0,
      }))
      const total = list.reduce((sum, item) => sum + item.marketValue, 0)
      list.forEach((item) => (item.weight = parseFloat(((item.marketValue / total) * 100).toFixed(1))))
      return { code: 200, data: { positions: list, totalMarketValue: total } }
    },
  },
  {
    url: '/api/demo/dashboard/risk-status',
    method: 'get',
    response: () => ({
      code: 200,
      data: {
        riskLevel: randomPick([1, 1, 2, 2, 2, 3]),
        riskLevelLabel: ['低', '中', '高'],
        todayEvents: randomInt(0, 5),
        maxDrawdown: randomNum(-25, -1),
        dailyLossLimit: randomNum(100000, 500000),
        dailyLoss: randomNum(0, 80000),
        consecutiveLosses: randomInt(0, 3),
      },
    }),
  },
  {
    url: '/api/demo/dashboard/recent-deals',
    method: 'get',
    response: ({ query }: any) => {
      const limit = parseInt(query.limit || '10')
      const list = Array.from({ length: limit }, (_, i) => {
        const s = randomPick(stocks)
        return {
          id: Date.now() - i * 60000,
          symbolCode: s.code,
          symbolName: s.name,
          direction: randomPick([1, 2]),
          dealPrice: randomNum(10, 500),
          dealQuantity: randomInt(100, 5000),
          dealAmount: randomNum(5000, 500000),
          dealTime: nowDateTime(),
          strategyId: randomPick(strategies),
        }
      })
      return { code: 200, data: list }
    },
  },

  // ---------- 订单 ----------
  {
    url: '/api/demo/orders',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const total = randomInt(20, 60)
      const list = Array.from({ length: Math.min(size, total - (page - 1) * size) }, (_, i) => {
        const s = randomPick(stocks)
        const status = randomPick([0, 0, 1, 1, 1, 2, 3, 4])
        return {
          id: 10000 + (page - 1) * size + i,
          marketId: randomPick([1, 2]),
          accountId: randomPick(accounts),
          strategyId: randomPick(strategies),
          symbolCode: s.code,
          symbolName: s.name,
          operationType: randomPick([1, 2]),
          direction: randomPick([1, 2]),
          orderType: randomPick([1, 2]),
          price: randomNum(10, 500),
          quantity: randomInt(100, 10000),
          status,
          statusLabel: statusMap[status],
          createdAt: dayBefore(randomInt(0, 7)) + ' ' + `${randomInt(9, 15)}:${randomInt(0, 59).toString().padStart(2, '0')}:00`,
        }
      })
      return { code: 200, data: { list, total, page, size } }
    },
  },

  // ---------- 成交 ----------
  {
    url: '/api/demo/deals',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const total = randomInt(50, 200)
      const list = Array.from({ length: Math.min(size, total - (page - 1) * size) }, (_, i) => {
        const s = randomPick(stocks)
        return {
          id: 20000 + (page - 1) * size + i,
          operationId: randomInt(10000, 19999),
          marketId: randomPick([1, 2]),
          accountId: randomPick(accounts),
          strategyId: randomPick(strategies),
          symbolCode: s.code,
          symbolName: s.name,
          dealType: randomPick([1, 2]),
          direction: randomPick([1, 2]),
          dealPrice: randomNum(10, 500),
          dealQuantity: randomInt(100, 10000),
          dealAmount: randomNum(5000, 2000000),
          commission: randomNum(5, 500),
          positionAfter: randomInt(0, 50000),
          isManual: randomPick([0, 0, 0, 0, 1]),
          dealTime: dayBefore(randomInt(0, 30)) + ' ' + `${randomInt(9, 15)}:${randomInt(0, 59).toString().padStart(2, '0')}:00`,
        }
      })
      return { code: 200, data: { list, total, page, size } }
    },
  },
  {
    url: '/api/demo/deals/stats',
    method: 'get',
    response: () => ({
      code: 200,
      data: {
        todayCount: randomInt(5, 30),
        todayAmount: randomNum(100000, 5000000),
        todayCommission: randomNum(100, 5000),
        weekCount: randomInt(20, 100),
        monthCount: randomInt(80, 400),
      },
    }),
  },

  // ---------- 持仓 ----------
  {
    url: '/api/demo/positions/current',
    method: 'get',
    response: () => {
      const list = stocks.slice(0, 8).map((s) => ({
        symbolCode: s.code,
        symbolName: s.name,
        direction: randomPick([1, 1, 1, 2]),
        openPrice: randomNum(10, 500),
        currentPrice: randomNum(10, 500),
        holdingQuantity: randomInt(500, 30000),
        holdingAmount: randomNum(100000, 5000000),
        unrealizedPnl: randomNum(-80000, 120000),
        unrealizedPnlRate: randomNum(-15, 25),
        openTime: dayBefore(randomInt(1, 90)),
        strategyId: randomPick(strategies),
      }))
      return { code: 200, data: list }
    },
  },

  // ---------- 账户资产 ----------
  {
    url: '/api/demo/account/assets',
    method: 'get',
    response: ({ query }: any) => {
      const days = parseInt(query.days || '30')
      const history = Array.from({ length: days }, (_, i) => ({
        date: dayBefore(days - 1 - i),
        totalAsset: randomNum(8000000, 12000000),
        netValue: randomNum(1.0, 2.0),
        marketValue: randomNum(5000000, 10000000),
        cashBalance: randomNum(1000000, 3000000),
      }))
      return { code: 200, data: { history, current: history[history.length - 1] } }
    },
  },

  // ---------- 风控 ----------
  {
    url: '/api/demo/risk/overview',
    method: 'get',
    response: () => {
      const level = randomPick([1, 2, 2, 2, 3])
      return {
        code: 200,
        data: {
          riskLevel: level,
          riskScore: level === 1 ? randomInt(10, 30) : level === 2 ? randomInt(31, 60) : randomInt(61, 90),
          todayEvents: randomInt(0, 4),
          unresolvedEvents: randomInt(0, 3),
          weekEvents: randomInt(3, 12),
          maxDrawdown: randomNum(-20, -1),
          dailyVar: randomNum(10000, 100000),
          trend: Array.from({ length: 30 }, (_, i) => ({
            date: dayBefore(29 - i),
            riskScore: randomInt(10, 80),
          })),
        },
      }
    },
  },
  {
    url: '/api/demo/risk/events',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const eventTypes = [
        { type: 'order_failed', label: '下单失败' },
        { type: 'cancel_failed', label: '撤单失败' },
        { type: 'api_error', label: 'API异常' },
        { type: 'timeout', label: '超时异常' },
        { type: 'daily_loss', label: '单日亏损超限' },
        { type: 'drawdown', label: '回撤超限' },
        { type: 'consecutive_loss', label: '连续亏损' },
        { type: 'circuit_breaker', label: '熔断' },
      ]
      const total = randomInt(15, 50)
      const list = Array.from({ length: Math.min(size, total - (page - 1) * size) }, (_, i) => {
        const et = randomPick(eventTypes)
        return {
          id: 30000 + (page - 1) * size + i,
          eventType: et.type,
          eventLabel: et.label,
          level: randomPick([1, 2, 3]),
          accountId: randomPick(accounts),
          strategyId: randomPick(strategies),
          symbolCode: Math.random() > 0.5 ? randomPick(stocks).code : null,
          message: `${et.label}事件：${randomPick(['网络超时', '余额不足', '价格偏离过大', '接口限流', '参数校验失败', '持仓不足'])}`,
          status: randomPick(['pending', 'processing', 'resolved', 'ignored']),
          occurTime: dayBefore(randomInt(0, 14)) + ' ' + `${randomInt(0, 23)}:${randomInt(0, 59).toString().padStart(2, '0')}:00`,
        }
      })
      return { code: 200, data: { list, total, page, size } }
    },
  },
  {
    url: '/api/demo/risk/notifications',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const types = ['risk_alert', 'circuit_breaker', 'anomaly', 'strategy_pause']
      const typeLabels: Record<string, string> = { risk_alert: '风险报警', circuit_breaker: '熔断通知', anomaly: '异常通知', strategy_pause: '策略暂停' }
      const total = randomInt(10, 40)
      const list = Array.from({ length: Math.min(size, total - (page - 1) * size) }, (_, i) => {
        const t = randomPick(types)
        return {
          id: 40000 + i,
          type: t,
          typeLabel: typeLabels[t],
          level: randomPick([1, 2, 3]),
          title: `${typeLabels[t]} - ${randomPick(['账户回撤接近阈值', '系统检测到异常波动', '策略信号异常', 'API连接不稳定'])}`,
          content: '详细通知内容：系统在例行巡检中发现异常指标，建议关注相关风险敞口。',
          isRead: Math.random() > 0.4,
          createdAt: dayBefore(randomInt(0, 7)) + ' ' + `${randomInt(0, 23)}:${randomInt(0, 59).toString().padStart(2, '0')}:00`,
        }
      })
      return { code: 200, data: { list, total, page, size } }
    },
  },

  // ---------- 数据分析 ----------
  {
    url: '/api/demo/analysis/returns',
    method: 'get',
    response: () => {
      const dailyReturns = Array.from({ length: 90 }, (_, i) => ({
        date: dayBefore(89 - i),
        dailyReturn: randomNum(-5, 5),
        cumulativeReturn: randomNum(-10, 40),
        netValue: randomNum(0.95, 1.5),
      }))
      return {
        code: 200,
        data: {
          dailyReturns,
          summary: {
            totalReturn: randomNum(10, 60),
            annualReturn: randomNum(5, 35),
            sharpeRatio: randomNum(0.5, 3.0),
            maxDrawdown: randomNum(-30, -5),
            calmarRatio: randomNum(0.3, 2.5),
            winRate: randomNum(45, 70),
          },
        },
      }
    },
  },
  {
    url: '/api/demo/analysis/trading',
    method: 'get',
    response: () => ({
      code: 200,
      data: {
        winRate: randomNum(45, 70),
        profitLossRatio: randomNum(1.2, 3.5),
        avgProfit: randomNum(500, 5000),
        avgLoss: randomNum(-5000, -200),
        tradeCount: randomInt(50, 300),
        tradeFrequency: randomNum(0.5, 5),
        totalCommission: randomNum(1000, 50000),
        slippage: randomNum(0.01, 0.5),
        monthlyTrades: Array.from({ length: 6 }, (_, i) => ({
          month: `2026-${(i + 1).toString().padStart(2, '0')}`,
          count: randomInt(10, 60),
          winRate: randomNum(40, 75),
        })),
      },
    }),
  },
  {
    url: '/api/demo/analysis/strategy',
    method: 'get',
    response: () => {
      const list = strategies.map((s) => ({
        strategyId: s,
        strategyName: s,
        totalReturn: randomNum(5, 50),
        sharpeRatio: randomNum(0.3, 3.5),
        maxDrawdown: randomNum(-30, -2),
        winRate: randomNum(40, 75),
        tradeCount: randomInt(20, 150),
        contribution: 0,
        correlation: strategies.map((s2) => ({
          strategy: s2,
          value: s === s2 ? 1 : randomNum(-0.3, 0.8),
        })),
      }))
      const totalReturn = list.reduce((sum, item) => sum + Math.abs(item.totalReturn), 0)
      list.forEach((item) => (item.contribution = parseFloat(((Math.abs(item.totalReturn) / totalReturn) * 100).toFixed(1))))
      return { code: 200, data: list }
    },
  },

  // ---------- 报表 ----------
  {
    url: '/api/demo/reports',
    method: 'get',
    response: ({ query }: any) => {
      const type = query.type || 'daily'
      const prefix: Record<string, string> = { daily: '日报', weekly: '周报', monthly: '月报' }
      const list = Array.from({ length: 12 }, (_, i) => ({
        id: 50000 + i,
        title: `${prefix[type] || '报表'} - 2026-${(i + 1).toString().padStart(2, '0')}-${randomInt(1, 28).toString().padStart(2, '0')}`,
        type,
        createdAt: dayBefore(randomInt(0, 90)),
        fileSize: `${randomInt(100, 5000)}KB`,
        status: randomPick(['generated', 'generated', 'generated', 'generating']),
      }))
      return { code: 200, data: list }
    },
  },

  // ---------- 日志 ----------
  {
    url: '/api/demo/logs/system',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const levels = ['INFO', 'INFO', 'INFO', 'WARN', 'ERROR']
      const messages = [
        '策略调度器启动成功',
        '账户数据同步完成',
        '风控检查通过',
        '日报生成完成',
        '数据库连接正常',
        'API连接超时，正在重试',
        '订单执行成功',
        '持仓数据更新完成',
        '定时任务执行完毕',
        '服务心跳检测正常',
      ]
      const total = randomInt(100, 500)
      const list = Array.from({ length: Math.min(size, total - (page - 1) * size) }, (_, i) => ({
        id: 60000 + i,
        level: randomPick(levels),
        module: randomPick(['strategy', 'executor', 'risk', 'analysis', 'system']),
        message: randomPick(messages),
        detail: '详细日志信息...',
        createdAt: dayBefore(randomInt(0, 7)) + ' ' + `${randomInt(0, 23)}:${randomInt(0, 59).toString().padStart(2, '0')}:${randomInt(0, 59).toString().padStart(2, '0')}`,
      }))
      return { code: 200, data: { list, total, page, size } }
    },
  },
  {
    url: '/api/demo/logs/trading',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const types = ['order', 'cancel', 'deal']
      const typeLabels: Record<string, string> = { order: '下单', cancel: '撤单', deal: '成交' }
      const total = randomInt(50, 300)
      const list = Array.from({ length: Math.min(size, total - (page - 1) * size) }, (_, i) => {
        const t = randomPick(types)
        const s = randomPick(stocks)
        return {
          id: 70000 + i,
          type: t,
          typeLabel: typeLabels[t],
          symbolCode: s.code,
          symbolName: s.name,
          message: `${typeLabels[t]}日志：${s.name}(${s.code})，${t === 'deal' ? '成交价' : '委托价'}${randomNum(10, 500)}，数量${randomInt(100, 5000)}`,
          status: randomPick(['success', 'success', 'success', 'failed']),
          createdAt: dayBefore(randomInt(0, 7)) + ' ' + `${randomInt(9, 15)}:${randomInt(0, 59).toString().padStart(2, '0')}:${randomInt(0, 59).toString().padStart(2, '0')}`,
        }
      })
      return { code: 200, data: { list, total, page, size } }
    },
  },

  // ---------- 人工干预 ----------
  {
    url: '/api/demo/manual/buy',
    method: 'post',
    response: () => ({
      code: 200,
      data: {
        orderId: randomInt(80000, 89999),
        status: 'submitted',
        message: '买入委托已提交，等待成交确认。',
        dealTime: nowDateTime(),
      },
    }),
  },
  {
    url: '/api/demo/manual/sell',
    method: 'post',
    response: () => ({
      code: 200,
      data: {
        orderId: randomInt(80000, 89999),
        status: 'submitted',
        message: '卖出委托已提交，等待成交确认。',
        dealTime: nowDateTime(),
      },
    }),
  },
  {
    url: '/api/demo/manual/modify-order',
    method: 'post',
    response: () => ({
      code: 200,
      data: {
        orderId: randomInt(80000, 89999),
        status: 'modified',
        message: '订单修改成功。',
        modifyTime: nowDateTime(),
      },
    }),
  },
] as MockMethod[]
