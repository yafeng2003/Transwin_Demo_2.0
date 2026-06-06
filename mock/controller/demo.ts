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
    url: '/api/demo/risk/events/resolve',
    method: 'post',
    response: ({ body }: any) => ({
      code: 200,
      data: { id: body.id, status: 'resolved', message: '已处理' },
    }),
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
      // 生成真实的累计收益模拟数据（随机游走）
      let nav = 1.0
      let peak = 1.0
      let cumReturn = 0
      const dailyReturns: any[] = []
      const navSeries: any[] = []
      const drawdownSeries: any[] = []

      for (let i = 0; i < 90; i++) {
        const dailyRet = randomNum(-4, 4.5) // 日收益率
        nav = nav * (1 + dailyRet / 100)
        if (nav > peak) peak = nav
        const dd = ((nav - peak) / peak) * 100 // 回撤百分比
        cumReturn = ((nav - 1.0) * 100)

        dailyReturns.push({
          date: dayBefore(89 - i),
          dailyReturn: parseFloat(dailyRet.toFixed(2)),
          cumulativeReturn: parseFloat(cumReturn.toFixed(2)),
          netValue: parseFloat(nav.toFixed(4)),
        })
        navSeries.push(parseFloat(nav.toFixed(4)))
        drawdownSeries.push(parseFloat(dd.toFixed(2)))
      }

      // 月度收益（近12个月）
      const monthlyReturns = Array.from({ length: 12 }, (_, i) => {
        const m = ((new Date().getMonth() - 11 + i) % 12 + 12) % 12
        const y = new Date().getFullYear() + Math.floor(((new Date().getMonth() - 11 + i) / 12))
        return {
          month: `${y}-${(m + 1).toString().padStart(2, '0')}`,
          year: y,
          monthIdx: m + 1,
          return: parseFloat(randomNum(-8, 12).toFixed(2)),
        }
      })

      // 日收益分布（分桶统计）
      const buckets = ['<-4%', '-4~-3%', '-3~-2%', '-2~-1%', '-1~0%', '0~1%', '1~2%', '2~3%', '3~4%', '>4%']
      const dist = buckets.map((label, idx) => {
        const weights = [2, 3, 5, 8, 15, 18, 12, 8, 5, 3]
        return { bucket: label, count: randomInt(weights[idx] * 2, weights[idx] * 5) }
      })

      // 年度收益
      const currentYear = new Date().getFullYear()
      const annualReturns = Array.from({ length: 5 }, (_, i) => ({
        year: currentYear - 4 + i,
        return: parseFloat(randomNum(-25, 55).toFixed(2)),
        benchmark: parseFloat(randomNum(-15, 35).toFixed(2)),
      }))

      const totalReturn = parseFloat(cumReturn.toFixed(2))
      const annualReturn = parseFloat((totalReturn * 4).toFixed(2)) // 年化近似
      const sharpeRatio = parseFloat(randomNum(0.8, 3.2).toFixed(2))
      const maxDrawdown = parseFloat((Math.min(...drawdownSeries)).toFixed(2))
      const calmarRatio = maxDrawdown !== 0 ? parseFloat((annualReturn / Math.abs(maxDrawdown)).toFixed(2)) : 0
      const positiveDays = dailyReturns.filter((d: any) => d.dailyReturn > 0).length
      const winRate = parseFloat(((positiveDays / dailyReturns.length) * 100).toFixed(1))

      return {
        code: 200,
        data: {
          dailyReturns,
          navSeries,
          drawdownSeries,
          monthlyReturns,
          dailyReturnDist: dist,
          annualReturns,
          summary: {
            totalReturn,
            annualReturn,
            sharpeRatio,
            maxDrawdown,
            calmarRatio,
            winRate,
            volatility: parseFloat(randomNum(12, 28).toFixed(2)),
            sortinoRatio: parseFloat(randomNum(1.0, 3.5).toFixed(2)),
            informationRatio: parseFloat(randomNum(0.5, 2.0).toFixed(2)),
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
  // 下单日志 (trade_log)
  {
    url: '/api/demo/logs/trade',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const ops = ['买入', '卖出']
      const remarks = ['batch_01_sigA', 'batch_02_sigB', 'rebalance_03', 'signal_ma_cross', 'signal_momentum', '']
      const total = randomInt(30, 200)
      const list = Array.from({ length: Math.min(size, total - (page - 1) * size) }, (_, i) => {
        const s = randomPick(stocks)
        return {
          '时间': dayBefore(randomInt(0, 7)) + ' ' + `${randomInt(9, 15)}:${randomInt(0, 59).toString().padStart(2, '0')}:${randomInt(0, 59).toString().padStart(2, '0')}`,
          '操作': randomPick(ops),
          '代码': `HK.${s.code}`,
          '名称': s.name,
          '数量': randomInt(100, 10000),
          '价格': 0, // 市价单固定传0
          '订单号': String(randomInt(8000000, 8999999)),
          '备注': randomPick(remarks),
        }
      })
      return { code: 200, data: { list, total, page, size } }
    },
  },
  // 订单状态日志 (order_log)
  {
    url: '/api/demo/logs/order',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const envs = ['REAL', 'SIMULATE']
      const ops = ['买入', '卖出']
      const orderTypes = ['MARKET', 'LIMIT']
      const orderStatuses = ['SUBMITTED', 'FILLED_ALL', 'FILLED_PART', 'CANCELLED_ALL', 'FAILED', 'DISABLED', 'DELETED']
      const total = randomInt(40, 250)
      const list = Array.from({ length: Math.min(size, total - (page - 1) * size) }, (_, i) => {
        const s = randomPick(stocks)
        const status = randomPick(orderStatuses)
        const qty = randomInt(100, 10000)
        const filledQty = status === 'FILLED_ALL' ? qty : status === 'FILLED_PART' ? randomInt(1, qty - 1) : 0
        const price = randomNum(10, 500)
        const isFail = ['FAILED', 'DISABLED', 'DELETED'].includes(status)
        const errMsgs = ['余额不足', '市场已关闭', '超出持仓', '接口超时', '参数无效']
        const ts = dayBefore(randomInt(0, 7)) + ' ' + `${randomInt(9, 15)}:${randomInt(0, 59).toString().padStart(2, '0')}:${randomInt(0, 59).toString().padStart(2, '0')}`
        return {
          '记录时间': ts,
          '交易环境': randomPick(envs),
          '操作': randomPick(ops),
          '订单类型': randomPick(orderTypes),
          '订单状态': status,
          '订单号': String(randomInt(8000000, 8999999)),
          '代码': `HK.${s.code}`,
          '名称': s.name,
          '订单数量': qty,
          '订单价格': price,
          '已成交数量': filledQty,
          '成交均价': filledQty > 0 ? randomNum(price * 0.98, price * 1.02) : 0,
          '最后错误': isFail ? randomPick(errMsgs) : '',
          '备注': randomPick(['batch_01', 'batch_02', 'signal_v1', '']),
          '创建时间': ts,
          '更新时间': ts,
        }
      })
      return { code: 200, data: { list, total, page, size } }
    },
  },
  // 错误日志 (error_log)
  {
    url: '/api/demo/logs/error',
    method: 'get',
    response: ({ query }: any) => {
      const page = parseInt(query.page || '1')
      const size = parseInt(query.size || '20')
      const stage = query.stage
      const action = query.action
      const errorType = query.errorType

      const stages = ['executor', 'risk', 'strategy', 'callback', 'cleanup']
      const actions = ['BUY', 'SELL', 'POSITION', 'unlock_trade', 'order_update', 'cleanup']
      const fixedErrorTypes = [
        'unlock_failed', 'invalid_weight', 'account_assets_unavailable', 'price_unavailable',
        'insufficient_cash', 'callback_failed', 'callback_exception', 'qty_below_lot',
        'max_buy_query_failed', 'max_buy_zero', 'place_order_failed', 'no_position',
        'fill_callback_exception', 'position_query_failed', 'buy_not_in_actual_position',
        'position_not_in_actual_position', 'unhandled_exception',
      ]
      const dynamicErrorTypes = ['FAILED', 'DISABLED', 'DELETED']
      const allErrorTypes = [...fixedErrorTypes, ...dynamicErrorTypes]

      const errorDetails: Record<string, string> = {
        unlock_failed: '交易解锁失败：前序订单未完成结算',
        invalid_weight: '权重数据无效：目标权重为空或格式错误',
        account_assets_unavailable: '账户资产查询失败：API 连接超时',
        price_unavailable: '无法获取 HK.00700 最新报价',
        insufficient_cash: '可用资金不足，需 150,000 实际可用 98,500',
        callback_failed: '订单回调处理失败',
        callback_exception: '订单回调异常：NullPointerException',
        qty_below_lot: '下单数量 50 低于最小交易单位 100',
        max_buy_query_failed: '最大可买查询失败：行情服务不可用',
        max_buy_zero: '最大可买数量为 0，可能触及单日买入上限',
        place_order_failed: '下单失败：交易所拒单，错误码 10012',
        no_position: '无持仓可卖：HK.00001 当前持仓为 0',
        fill_callback_exception: '成交回调处理异常：数据解析错误',
        position_query_failed: '持仓查询失败：账户服务暂不可用',
        buy_not_in_actual_position: '买入股票 HK.00700 未在实际持仓中找到',
        position_not_in_actual_position: '目标持仓与实际持仓不一致',
        unhandled_exception: '未处理的异常：IndexOutOfRange',
        FAILED: '订单执行失败',
        DISABLED: '订单已被禁用',
        DELETED: '订单已被删除',
      }

      let rawTotal = randomInt(30, 180)
      let filteredList = Array.from({ length: rawTotal }, (_, i) => {
        const s = randomPick(stocks)
        const et = randomPick(allErrorTypes)
        return {
          '时间': dayBefore(randomInt(0, 14)) + ' ' + `${randomInt(0, 23)}:${randomInt(0, 59).toString().padStart(2, '0')}:${randomInt(0, 59).toString().padStart(2, '0')}`,
          '阶段': randomPick(stages),
          '代码': Math.random() > 0.3 ? `HK.${s.code}` : '',
          '动作': randomPick(actions),
          '错误类型': et,
          '错误详情': errorDetails[et] || `未知错误：${et}`,
          '订单号': Math.random() > 0.3 ? String(randomInt(8000000, 8999999)) : '',
          '备注': randomPick(['batch_01', 'signal_v1', 'rebalance', '']),
        }
      })

      // 支持筛选
      if (stage) filteredList = filteredList.filter((r: any) => r['阶段'] === stage)
      if (action) filteredList = filteredList.filter((r: any) => r['动作'] === action)
      if (errorType) filteredList = filteredList.filter((r: any) => r['错误类型'] === errorType)

      const total = filteredList.length
      const start = (page - 1) * size
      const list = filteredList.slice(start, start + size)

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
