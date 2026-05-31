// 轻量 CSV 解析器，兼容常见 CSV 场景：支持 header、跳过空行、双引号包裹字段、双引号内双引号转义、字段内换行
export function parseCSV(text: string, opts: { header?: boolean; skipEmptyLines?: boolean } = { header: true, skipEmptyLines: true }) {
  const header = opts.header ?? true
  const skipEmptyLines = opts.skipEmptyLines ?? true

  const lines: string[] = []
  let cur = ''
  let inQuotes = false
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    const next = text[i + 1]
    if (ch === '"') {
      if (inQuotes && next === '"') {
        cur += '"'
        i++
      } else {
        inQuotes = !inQuotes
      }
    } else if (ch === '\n' && !inQuotes) {
      lines.push(cur.replace(/\r$/, ''))
      cur = ''
    } else {
      cur += ch
    }
  }
  if (cur.length > 0) lines.push(cur.replace(/\r$/, ''))

  const rows: string[][] = []
  for (const line of lines) {
    if (skipEmptyLines && line.trim() === '') continue
    const fields: string[] = []
    let field = ''
    let inQ = false
    for (let i = 0; i < line.length; i++) {
      const ch = line[i]
      const next = line[i + 1]
      if (ch === '"') {
        if (inQ && next === '"') {
          field += '"'
          i++
        } else {
          inQ = !inQ
        }
      } else if (ch === ',' && !inQ) {
        fields.push(field)
        field = ''
      } else {
        field += ch
      }
    }
    fields.push(field)
    rows.push(fields)
  }

  if (header) {
    const headers = (rows.shift() || []).map(h => h.trim())
    const data = rows.map(r => {
      const obj: Record<string, string> = {}
      for (let i = 0; i < headers.length; i++) {
        obj[headers[i]] = (r[i] ?? '').trim()
      }
      return obj
    })
    return { data, meta: { fields: headers } }
  }
  return { data: rows, meta: {} }
}
