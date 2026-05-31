export type PanelRow = Record<string, string>

export async function getTodayPanelData(): Promise<PanelRow | null> {
  const now = new Date()
  const yyyy = now.getFullYear()
  const mm = String(now.getMonth() + 1).padStart(2, '0')
  const dd = String(now.getDate()).padStart(2, '0')
  const dateStr = `${yyyy}/${mm}/${dd}`

  try {
    const res = await fetch('/data/量化系统面板数据.csv')
    if (!res.ok) return null
    const text = await res.text()
    const lines = text.trim().split(/\r?\n/)
    if (lines.length < 2) return null
    const headers = lines[0].split(',').map(h => h.trim())
    const rows = lines.slice(1).map(l => l.split(',').map(cell => cell.trim()))
    const row = rows.find(r => r[0] === dateStr)
    if (!row) return null
    const obj: PanelRow = {}
    headers.forEach((h, i) => {
      obj[h] = row[i] ?? ''
    })
    return obj
  } catch (e) {
    return null
  }
}
