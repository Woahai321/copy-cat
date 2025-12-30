interface TransferDataPoint {
  timestamp: number
  copied: number
}

interface CopyJob {
  id: number
  progress_percent: number
  total_size_bytes: number
  copied_size_bytes: number
  status: string
}

export const useTransferStats = () => {
  // Store transfer history for each job
  const transferHistoryMap = useState<Map<number, TransferDataPoint[]>>(
    'transfer-history',
    () => new Map()
  )

  const updateProgress = (jobId: number, copiedBytes: number) => {
    const history = transferHistoryMap.value.get(jobId) || []
    
    history.push({
      timestamp: Date.now(),
      copied: copiedBytes
    })
    
    // Keep only last 10 data points (about 1 minute of data if updated every 6 seconds)
    if (history.length > 10) {
      history.shift()
    }
    
    transferHistoryMap.value.set(jobId, history)
  }

  const getTransferRate = (jobId: number): number => {
    const history = transferHistoryMap.value.get(jobId)
    
    if (!history || history.length < 2) {
      return 0
    }
    
    const first = history[0]
    const last = history[history.length - 1]
    
    const bytesDiff = last.copied - first.copied
    const timeDiff = (last.timestamp - first.timestamp) / 1000 // Convert to seconds
    
    if (timeDiff === 0) return 0
    
    return bytesDiff / timeDiff // bytes per second
  }

  const getEstimatedTimeRemaining = (job: CopyJob): string | null => {
    if (job.status !== 'processing') return null
    
    const rate = getTransferRate(job.id)
    
    if (rate === 0 || !transferHistoryMap.value.get(job.id) || (transferHistoryMap.value.get(job.id)?.length || 0) < 2) {
      return 'Calculating...'
    }
    
    const remainingBytes = job.total_size_bytes - job.copied_size_bytes
    
    if (remainingBytes <= 0) return null
    
    const secondsRemaining = remainingBytes / rate
    
    return formatTimeRemaining(secondsRemaining)
  }

  const formatTimeRemaining = (seconds: number): string => {
    if (seconds < 0) return 'Calculating...'
    if (seconds < 60) return `~${Math.round(seconds)}s`
    if (seconds < 3600) {
      const minutes = Math.round(seconds / 60)
      return `~${minutes}m`
    }
    if (seconds < 86400) {
      const hours = Math.round(seconds / 3600)
      return `~${hours}h`
    }
    const days = Math.round(seconds / 86400)
    return `~${days}d`
  }

  const formatTransferRate = (bytesPerSecond: number): string => {
    if (bytesPerSecond === 0) return '0 B/s'
    
    const k = 1024
    const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s']
    const i = Math.floor(Math.log(bytesPerSecond) / Math.log(k))
    
    return `${parseFloat((bytesPerSecond / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }

  const clearJobHistory = (jobId: number) => {
    transferHistoryMap.value.delete(jobId)
  }

  return {
    updateProgress,
    getTransferRate,
    getEstimatedTimeRemaining,
    formatTransferRate,
    clearJobHistory
  }
}

