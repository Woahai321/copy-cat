interface ProgressUpdate {
  job_id: number
  status: string
  progress_percent: number
  copied_size_bytes: number
  total_size_bytes: number
}

// --- Singleton State (Module Scope) ---
const socket = ref<WebSocket | null>(null)
const isConnected = ref(false)
const progressUpdates = ref<Map<number, ProgressUpdate>>(new Map())
// Stats now includes speedHistory for smoothing
const jobStats = ref<Map<number, { lastBytes: number; lastTime: number; speed: number; speedHistory: number[] }>>(new Map())
const subscriberCount = ref(0)
let reconnectTimer: any = null

export const useWebSocket = () => {
  const config = useRuntimeConfig()

  const getEstimatedTimeRemaining = (jobId: number): string | null => {
    const job = progressUpdates.value.get(jobId)
    const stats = jobStats.value.get(jobId)

    if (!job || !stats || stats.speed === 0) return null
    if (job.status !== 'processing') return null

    const remainingBytes = job.total_size_bytes - job.copied_size_bytes
    if (remainingBytes <= 0) return null

    const seconds = remainingBytes / stats.speed

    if (seconds < 60) return `${Math.ceil(seconds)}s`
    if (seconds < 3600) return `${Math.ceil(seconds / 60)}m`
    return `${(seconds / 3600).toFixed(1)}h`
  }

  const connect = () => {
    // Singleton check: If connected or connecting, do nothing
    if (socket.value?.readyState === WebSocket.OPEN || socket.value?.readyState === WebSocket.CONNECTING) {
      return
    }

    // Build WebSocket URL
    let wsUrl: string
    if (config.public.apiBase) {
      wsUrl = config.public.apiBase.replace('http://', 'ws://').replace('https://', 'wss://')
    } else {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.hostname
      // Docker port mapping: frontend on 4222, backend on 4223
      // When accessing from host, we need to redirect WebSocket to backend port
      const port = window.location.port === '4222' ? '4223' : window.location.port
      wsUrl = `${protocol}//${host}:${port}`
    }

    console.log('[WebSocket] Connecting singleton:', `${wsUrl}/ws/progress`)
    socket.value = new WebSocket(`${wsUrl}/ws/progress`)

    socket.value.onopen = () => {
      console.log('[WebSocket] Connected')
      isConnected.value = true
    }

    socket.value.onmessage = (event) => {
      try {
        const data: ProgressUpdate = JSON.parse(event.data)
        const now = Date.now()

        // Calculate Speed with Moving Average
        const stats = jobStats.value.get(data.job_id)
        if (stats) {
          const timeDiff = (now - stats.lastTime) / 1000 // seconds
          const bytesDiff = data.copied_size_bytes - stats.lastBytes

          // Only update speed if enough time passed (avoid jitter)
          if (timeDiff > 0.5) {
            const currentSpeed = bytesDiff / timeDiff
            const history = [...stats.speedHistory, currentSpeed].slice(-5) // Keep last 5 samples
            const avgSpeed = history.reduce((a, b) => a + b, 0) / history.length

            jobStats.value.set(data.job_id, {
              lastBytes: data.copied_size_bytes,
              lastTime: now,
              speed: avgSpeed,
              speedHistory: history
            })
          }
        } else {
          // Initialize
          jobStats.value.set(data.job_id, {
            lastBytes: data.copied_size_bytes,
            lastTime: now,
            speed: 0,
            speedHistory: []
          })
        }

        progressUpdates.value.set(data.job_id, data)
      } catch (error) {
        console.error('[WebSocket] Parse error:', error)
      }
    }

    socket.value.onerror = (error) => {
      console.error('[WebSocket] Error:', error)
    }

    socket.value.onclose = () => {
      console.log('[WebSocket] Disconnected')
      isConnected.value = false
      socket.value = null

      // Auto-reconnect only if we have subscribers
      if (subscriberCount.value > 0) {
        clearTimeout(reconnectTimer)
        reconnectTimer = setTimeout(() => {
          if (process.client && subscriberCount.value > 0) {
            connect()
          }
        }, 3000)
      }
    }
  }

  const disconnect = () => {
    // Only close if no one is listening anymore
    if (subscriberCount.value <= 0 && socket.value) {
      console.log('[WebSocket] No subscribers, closing connection')
      socket.value.close()
      socket.value = null
      isConnected.value = false
    }
  }

  const getJobProgress = (jobId: number): ProgressUpdate | undefined => {
    return progressUpdates.value.get(jobId)
  }

  // Component usage lifecycle
  onMounted(() => {
    subscriberCount.value++
    // Always ensure connection is alive when a component mounts
    connect()
  })

  onUnmounted(() => {
    subscriberCount.value--
    // small delay to prevent rapid close/open on navigation
    setTimeout(() => {
      if (subscriberCount.value <= 0) {
        disconnect()
      }
    }, 100)
  })

  // Expose shared state
  return {
    isConnected,
    progressUpdates,
    connect,
    disconnect,
    getJobProgress,
    getEstimatedTimeRemaining
  }
}
