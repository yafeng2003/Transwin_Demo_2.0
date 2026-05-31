/**
 * A股产品表现与沪深300数据解析 Hook
 */
import { ref } from 'vue'

import aRaw from '../../data/A股收益数据.csv?raw'
import hs300Raw from '../../data/沪深300数据.csv?raw'

export interface APerformanceData {
  dates: string[]
  productReturnPercents: number[]
  hs300ReturnPercents: number[]
  lastTotalReturnRate: number
  lastTotalProfit: number
  lastDayReturnRateDiff: number
  lastDayProfitDiff: number
}

const INITIAL_CAPITAL = 25_000_000

function parseCsv(raw: string): string[][] {
  return raw
    .trim()
    .split(/\r?\n/)
    .map(line => line.split(','))
}

function formatDateToLabel(dateStr: string): string {
  const parts = dateStr.split('/')
  if (parts.length < 3) return dateStr
  const year = parts[0].padStart(4, '0')
  const month = parts[1].padStart(2, '0')
  const day = parts[2].padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function useAPerformance(initialCapital: number = INITIAL_CAPITAL) {
  const dataRef = ref<APerformanceData | null>(null)

  if (!dataRef.value) {
    try {
      const aRows = parseCsv(aRaw)
      const [aHeader, ...aBody] = aRows
      const dateIndexA = aHeader.indexOf('日期')
      const returnIndexA = aHeader.indexOf('收益率')

      const hsRows = parseCsv(hs300Raw)
      const [hsHeader, ...hsBody] = hsRows
      const dateIndexHS = hsHeader.indexOf('日期')
      const returnIndexHS = hsHeader.lastIndexOf('收益率')

      const hsMap = new Map<string, number>()
      hsBody.forEach(cols => {
        const date = cols[dateIndexHS]
        const ratioStr = cols[returnIndexHS]
        if (date && ratioStr) {
          const ratio = Number(ratioStr)
          if (!Number.isNaN(ratio)) hsMap.set(date, ratio)
        }
      })

      const alignedDates: string[] = []
      const productRatios: number[] = []
      const hsRatios: number[] = []

      aBody.forEach(cols => {
        const date = cols[dateIndexA]
        const ratioStr = cols[returnIndexA]
        if (!date || !ratioStr) return
        if (!hsMap.has(date)) return
        const pRatio = Number(ratioStr)
        const hRatio = hsMap.get(date) as number
        if (Number.isNaN(pRatio) || Number.isNaN(hRatio)) return
        alignedDates.push(date)
        productRatios.push(pRatio)
        hsRatios.push(hRatio)
      })

      if (alignedDates.length === 0) throw new Error('未找到对齐日期数据')

      const productReturnPercents = productRatios.map(r => (r - 1) * 100)
      const hs300ReturnPercents = hsRatios.map(r => (r - 1) * 100)

      const lastRatio = productRatios[productRatios.length - 1]
      const prevRatio = productRatios[productRatios.length - 2] || productRatios[productRatios.length - 1]
      const lastTotalReturnRate = (lastRatio - 1) * 100
      const lastTotalProfit = initialCapital * (lastRatio - 1)
      const lastDayReturnRateDiff = (lastRatio / prevRatio - 1) * 100
      const lastDayProfitDiff = initialCapital * (lastRatio - prevRatio)

      dataRef.value = {
        dates: alignedDates.map(formatDateToLabel),
        productReturnPercents,
        hs300ReturnPercents,
        lastTotalReturnRate,
        lastTotalProfit,
        lastDayReturnRateDiff,
        lastDayProfitDiff,
      }
    } catch (e) {
      console.error('useAPerformance 解析失败', e)
      dataRef.value = {
        dates: [],
        productReturnPercents: [],
        hs300ReturnPercents: [],
        lastTotalReturnRate: 0,
        lastTotalProfit: 0,
        lastDayReturnRateDiff: 0,
        lastDayProfitDiff: 0,
      }
    }
  }

  return dataRef
}

export default useAPerformance
