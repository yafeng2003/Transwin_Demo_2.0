import { parseCSV } from './parseCSV'

import aRaw from '/data/A股每月交易统计.csv?raw'
import hkRaw from '/data/港股每月交易统计.csv?raw'

type Kind = 'hk' | 'a'

function sortByTimeAsc(rows: Array<Record<string, string>>) {
  return rows.slice().sort((a, b) => (a['时间'] ?? '').localeCompare(b['时间'] ?? ''))
}

/**
 * 从 CSV 原始文本中取出最后 N 条（月度）标签和对应数值
 * @param kind 'hk' 或 'a'，分别对应港股 / A 股 CSV
 * @param n 要取的条数，默认 12
 */
export function getLastNMonthsAndValues(kind: Kind, n = 12) {
  const raw = kind === 'hk' ? hkRaw : aRaw
  const parsed = parseCSV(raw)
  const rows = parsed.data as Array<Record<string, string>>
  const sorted = sortByTimeAsc(rows)
  const last = sorted.slice(-n)
  const labels = last.map((r) => r['时间'] ?? '')
  const values = last.map((r) => Number((r['交易次数'] ?? '').trim() || 0))
  return { labels, values }
}

export default {
  getLastNMonthsAndValues,
}
