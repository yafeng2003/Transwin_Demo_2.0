/**
 * 港股产品表现与恒生指数数据解析 Hook
 * 数据来源: 根目录 data/港股收益数据.csv 与 data/恒生指数数据.csv
 * 逻辑:
 *  - 解析 CSV 原始字符串 (通过 vite 的 ?raw 导入)
 *  - 对齐两个数据集中均存在的交易日期 (过滤掉港股收益里周末等无指数的日期)
 *  - 将累计收益率(如 1.035)转换为百分比形式 (3.5%) 用于折线图展示
 *  - 计算最后一天的累计收益与当日增量收益
 */
import { ref } from 'vue'

// raw 导入 CSV 内容 (相对路径: 当前文件位于 src/hooks)
import hsiRaw from '../../data/恒生指数数据.csv?raw'
import hkRaw from '../../data/港股收益数据.csv?raw'

export interface HkPerformanceData {
  dates: string[]              // 日期: MM-DD 用于折线图
  productReturnPercents: number[] // 产品累计收益率百分数 (例如 3.5 表示 3.5%)
  hangSengReturnPercents: number[] // 恒生指数累计收益率百分数
  lastTotalReturnRate: number  // 最后一天累计收益率百分数 (例如 12.3)
  lastTotalProfit: number      // 最后一天累计总收益 (金额)
  lastDayReturnRateDiff: number // 最后一天相对前一天的日收益率百分数
  lastDayProfitDiff: number    // 最后一天增量收益 (金额)
}

const INITIAL_CAPITAL = 25_000_000 // 初始资金 2500万

function parseCsv(raw: string): string[][] {
  return raw
    .trim()
    .split(/\r?\n/) // 按行
    .map(line => line.split(','))
}

function formatDateToLabel(dateStr: string): string {
  // 输入格式: YYYY/M/D 或 YYYY/MM/DD -> 输出: YYYY-MM-DD
  const parts = dateStr.split('/')
  if (parts.length < 3) return dateStr
  const year = parts[0].padStart(4, '0')
  const month = parts[1].padStart(2, '0')
  const day = parts[2].padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function useHkPerformance(initialCapital: number = INITIAL_CAPITAL) {
  const dataRef = ref<HkPerformanceData | null>(null)

  if (!dataRef.value) {
    try {
      // 解析港股收益 (表头: 收益率,日期)
      const hkRows = parseCsv(hkRaw)
      const [hkHeader, ...hkBody] = hkRows
      const dateIndexHK = hkHeader.indexOf('日期')
      const returnIndexHK = hkHeader.indexOf('收益率')

      // 解析恒生指数 (表头: 日期,收盘数值,收益率)
      const hsiRows = parseCsv(hsiRaw)
      const [hsiHeader, ...hsiBody] = hsiRows
      const dateIndexHSI = hsiHeader.indexOf('日期')
      const returnIndexHSI = hsiHeader.lastIndexOf('收益率') // 防止同名列冲突

      // 构造恒生指数 map 方便按日期查找
      const hsiMap = new Map<string, number>()
      hsiBody.forEach(cols => {
        const date = cols[dateIndexHSI]
        const ratioStr = cols[returnIndexHSI]
        if (date && ratioStr) {
          const ratio = Number(ratioStr)
          if (!Number.isNaN(ratio)) hsiMap.set(date, ratio)
        }
      })

      const alignedDates: string[] = []
      const productRatios: number[] = []
      const hsiRatios: number[] = []

      hkBody.forEach(cols => {
        const date = cols[dateIndexHK]
        const ratioStr = cols[returnIndexHK]
        if (!date || !ratioStr) return
        if (!hsiMap.has(date)) return // 仅保留恒生指数也有的交易日
        const pRatio = Number(ratioStr)
        const hRatio = hsiMap.get(date) as number
        if (Number.isNaN(pRatio) || Number.isNaN(hRatio)) return
        alignedDates.push(date)
        productRatios.push(pRatio)
        hsiRatios.push(hRatio)
      })

      if (alignedDates.length === 0) throw new Error('未找到对齐日期数据')

      // 转换为百分数 (累计收益率 = (ratio - 1) * 100)
      const productReturnPercents = productRatios.map(r => (r - 1) * 100)
      const hangSengReturnPercents = hsiRatios.map(r => (r - 1) * 100)

      // 计算最后一天累计收益
      const lastRatio = productRatios[productRatios.length - 1]
      const prevRatio = productRatios[productRatios.length - 2] || productRatios[productRatios.length - 1]
      const lastTotalReturnRate = (lastRatio - 1) * 100
      const lastTotalProfit = initialCapital * (lastRatio - 1)
      const lastDayReturnRateDiff = (lastRatio / prevRatio - 1) * 100
      const lastDayProfitDiff = initialCapital * (lastRatio - prevRatio)

      dataRef.value = {
        dates: alignedDates.map(formatDateToLabel),
        productReturnPercents,
        hangSengReturnPercents,
        lastTotalReturnRate,
        lastTotalProfit,
        lastDayReturnRateDiff,
        lastDayProfitDiff,
      }
    } catch (e) {
      // 简单错误兜底：保证组件不崩溃
      console.error('useHkPerformance 解析失败', e)
      dataRef.value = {
        dates: [],
        productReturnPercents: [],
        hangSengReturnPercents: [],
        lastTotalReturnRate: 0,
        lastTotalProfit: 0,
        lastDayReturnRateDiff: 0,
        lastDayProfitDiff: 0,
      }
    }
  }

  return dataRef
}

export default useHkPerformance
