import { nextTick, ref } from 'vue';

type LogItem = { level: string; module: string; message: string; timestamp: string }

export default function useTimelineLogs() {
  const currentTime = ref('')
  let timeTimer: NodeJS.Timeout | null = null

  const updateCurrentTime = () => {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')
    currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  const systemLogs = ref<LogItem[]>([])
  const displayedLogs = ref<LogItem[]>([])

  const parseTimestamp = (timestampStr: string): number => {
    const [datePart, timePart] = (timestampStr || '').split(' ')
    const [year, month, day] = (datePart || '').split('-').map(Number)
    const [hours, minutes, seconds] = (timePart || '00:00:00').split(':').map(Number)
    return new Date(year || 0, (month || 1) - 1, day || 1, hours || 0, minutes || 0, seconds || 0).getTime()
  }

  const getCurrentTimestamp = (): number => Date.now()

  const extractTime = (timestamp: string) => {
    const timePart = (timestamp || '').split(' ')[1]
    return timePart || timestamp
  }

  const extractDate = (timestamp: string) => {
    return (timestamp || '').split(' ')[0] || ''
  }

  const formatTimestamp = (timestamp: string) => timestamp

  // 将所有操作类型统一为绿色(success)，与“交易执行”样式保持一致
  const getLogColor = (_level: string) => '#70df39ff'

  const getLogTagType = (_level: string) => 'primary'

  // animation related
  const itemRefs = ref<HTMLElement[]>([])

  const setItemRef = (el: any) => {
    if (el && !itemRefs.value.includes(el.$el)) {
      itemRefs.value.push(el.$el)
    }
  }

  const recordPositions = () => {
    itemRefs.value.forEach((el) => {
      const rect = el.getBoundingClientRect()
      ;(el as any)._top = rect.top
      ;(el as any)._height = rect.height
    })
  }

  const animateScroll = () => {
    itemRefs.value.forEach((el) => {
      const newRect = el.getBoundingClientRect()
      const oldTop = (el as any)._top
      const deltaY = oldTop - newRect.top

      if (deltaY !== 0) {
        el.style.transform = `translateY(${deltaY}px)`
        el.style.transition = 'none'
        el.offsetHeight

        requestAnimationFrame(() => {
          el.style.transition = 'transform 0.5s ease-in-out'
          el.style.transform = 'translateY(0)'
        })

        setTimeout(() => {
          el.style.transition = ''
          el.style.transform = ''
        }, 500)
      }
    })
  }

  // CSV / data parsing logic (similar to log implementation)
  const testData = ref<LogItem[]>([])

  const normalizeTimestamp = (raw: string) => {
    if (!raw) return ''
    const parts = raw.trim().split(' ')
    let datePart = parts[0] || ''
    let timePart = parts[1] || ''
    datePart = datePart.replace(/\//g, '-')
    if (!timePart) timePart = '00:00:00'
    const tparts = timePart.split(':').map((p) => p.padStart(2, '0'))
    if (tparts.length === 1) tparts.push('00', '00')
    if (tparts.length === 2) tparts.push('00')
    return `${datePart} ${tparts.slice(0, 3).join(':')}`
  }

  const detectLevel = (category: string) => {
    if (!category) return 'info'
    if (category.includes('错误') || category.includes('异常')) return 'error'
    if (category.includes('检查') || category.includes('校验')) return 'warning'
    if (category.includes('交易') || category.includes('执行')) return 'success'
    return 'info'
  }

  const parseCsvToLogs = (csvText: string) => {
    const lines = (csvText || '').split(/\r?\n/).filter((l) => l.trim() !== '')
    if (lines.length <= 1) return []
    const header = lines[0].split(',').map((h) => h.trim())
    if (header.length > 0) header[0] = header[0].replace(/^\uFEFF/, '')
    const idxTime = header.indexOf('时间')
    const idxCategory = header.indexOf('动作类别')
    const idxDetail = header.indexOf('具体操作')
    const out: LogItem[] = []
    for (let i = 1; i < lines.length; i++) {
      const row = lines[i]
      const cols = row.split(',')
      const rawTime = (cols[idxTime] || '').trim()
      const category = (cols[idxCategory] || '').trim()
      const detail = cols.slice(idxDetail).join(',').trim()
      const timestamp = normalizeTimestamp(rawTime)
      out.push({ level: detectLevel(category), module: category || '未知', message: detail || '', timestamp })
    }
    out.sort((a, b) => parseTimestamp(b.timestamp) - parseTimestamp(a.timestamp))
    return out
  }

  const loadLogsFromCsv = async (url = '/data/量化系统运行日志.csv') => {
    try {
      // add cache-busting query param to ensure we always fetch latest CSV
      const fetchUrl = url + (url.includes('?') ? '&' : '?') + 't=' + Date.now()
      // debug: log which URL is being fetched
      // console.debug('loadLogsFromCsv fetching:', fetchUrl)
      const resp = await fetch(fetchUrl)
      if (!resp.ok) {
        // keep silent; caller may handle
        return
      }
      const text = await resp.text()
      // console.debug('loadLogsFromCsv: got', text?.length, 'bytes')
      const logs = parseCsvToLogs(text)
      testData.value = logs
      const now = getCurrentTimestamp()
      displayedLogs.value = logs.filter((l) => parseTimestamp(l.timestamp) <= now)
    } catch (e) {
      // console.error('加载日志 CSV 失败', e)
    }
  }

  const checkAndAddLogs = async () => {
    const currentTimestamp = getCurrentTimestamp()
    const eligibleLogs = testData.value.filter((log) => parseTimestamp(log.timestamp) <= currentTimestamp)
    const changed =
      eligibleLogs.length !== displayedLogs.value.length ||
      eligibleLogs.some((l, i) => !displayedLogs.value[i] || displayedLogs.value[i].timestamp !== l.timestamp || displayedLogs.value[i].message !== l.message)

    if (changed) {
      recordPositions()
      displayedLogs.value = eligibleLogs
      await nextTick()
      itemRefs.value = []
      await nextTick()
      setTimeout(() => {
        animateScroll()
      }, 50)
    }
  }

  let timer: NodeJS.Timeout | null = null

  const startTimer = () => {
    stopTimer()
    updateCurrentTime()
    timer = setInterval(() => {
      updateCurrentTime()
      checkAndAddLogs()
    }, 1000)
  }

  const stopTimer = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    if (timeTimer) {
      clearInterval(timeTimer)
      timeTimer = null
    }
  }

  return {
    currentTime,
    displayedLogs,
    setItemRef,
    extractTime,
    extractDate,
    formatTimestamp,
    getLogColor,
    getLogTagType,
    itemRefs,
    testData,
    loadLogsFromCsv,
    startTimer,
    stopTimer,
    parseTimestamp,
  }
}
