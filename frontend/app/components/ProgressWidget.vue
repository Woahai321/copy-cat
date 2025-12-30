<template>
  <Teleport to="body">
    <div v-if="hasActiveJobs || isExpanded" class="floating-widget" :class="{ minimized: !isExpanded, expanded: isExpanded }">
      <!-- Minimized state -->
      <div v-if="!isExpanded" @click="isExpanded = true" class="flex items-center gap-3 cursor-pointer">
        <div class="relative">
          <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 text-[#9d34da] animate-spin" />
        </div>
        <div>
          <p class="text-sm font-semibold text-slate-200">{{ activeJobsCount }} Active Job{{ activeJobsCount !== 1 ? 's' : '' }}</p>
          <p v-if="currentJob" class="text-xs text-slate-400">
            {{ currentJob.progress_percent }}% · {{ currentJobEta || 'Calculating...' }}
          </p>
        </div>
        <UIcon name="i-heroicons-chevron-up" class="w-4 h-4 text-slate-400 ml-2" />
      </div>

      <!-- Expanded state -->
      <div v-else class="flex flex-col h-full">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-slate-700/50">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-queue-list" class="w-5 h-5 text-[#bd73e8]" />
            <h3 class="font-semibold text-slate-200">Active Jobs</h3>
          </div>
          <button @click="isExpanded = false" class="text-slate-400 hover:text-slate-200 transition">
            <UIcon name="i-heroicons-chevron-down" class="w-5 h-5" />
          </button>
        </div>

        <!-- Current job -->
        <div v-if="currentJob" class="p-4 border-b border-slate-700/50">
          <div class="mb-3">
            <div class="flex items-center justify-between mb-2">
              <p class="text-sm font-semibold text-slate-200 truncate flex-1">
                {{ getJobName(currentJob.source_path) }}
              </p>
              <span class="text-xs font-bold text-[#9d34da] ml-2">{{ currentJob.progress_percent }}%</span>
            </div>
            <div class="progress-bar mb-2">
              <div class="progress-bar-fill" :style="{ width: `${currentJob.progress_percent}%` }"></div>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400">{{ formatSize(currentJob.copied_size_bytes) }}</span>
              <span v-if="currentJobEta" class="text-[#9d34da] font-medium">{{ currentJobEta }}</span>
              <span class="text-slate-400">{{ formatSize(currentJob.total_size_bytes) }}</span>
            </div>
          </div>
          <p class="text-xs text-slate-500 truncate">→ {{ currentJob.destination_path }}</p>
        </div>

        <!-- Queue list -->
        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="queuedJobs.length > 0" class="space-y-2">
            <p class="text-xs font-semibold text-slate-400 mb-2">QUEUED ({{ queuedJobs.length }})</p>
            <div
              v-for="job in queuedJobs"
              :key="job.id"
              class="card p-3 flex items-center justify-between"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm text-slate-200 truncate">{{ getJobName(job.source_path) }}</p>
                <p class="text-xs text-slate-500 truncate">{{ job.destination_path }}</p>
              </div>
              <UBadge color="gray" variant="soft" size="xs">Queued</UBadge>
            </div>
          </div>
          <div v-else-if="!currentJob" class="text-center py-8">
            <p class="text-sm text-slate-400">No active jobs</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t border-slate-700/50">
          <UButton
            to="/queue"
            variant="ghost"
            color="cyan"
            block
            size="sm"
            @click="isExpanded = false"
          >
            View All Jobs
          </UButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const { getQueue } = useApi()
const { getJobProgress } = useWebSocket()
const { updateProgress, getEstimatedTimeRemaining } = useTransferStats()

const isExpanded = ref(false)
const jobs = ref<any[]>([])

const hasActiveJobs = computed(() => jobs.value.length > 0)
const activeJobsCount = computed(() => jobs.value.length)

const currentJob = computed(() => {
  const processingJob = jobs.value.find(j => j.status === 'processing')
  if (processingJob) {
    // Check for real-time progress from WebSocket
    const realtimeProgress = getJobProgress(processingJob.id)
    if (realtimeProgress) {
      return {
        ...processingJob,
        progress_percent: realtimeProgress.progress_percent,
        copied_size_bytes: realtimeProgress.copied_size_bytes,
        total_size_bytes: realtimeProgress.total_size_bytes
      }
    }
    return processingJob
  }
  return null
})

const currentJobEta = computed(() => {
  if (!currentJob.value || currentJob.value.status !== 'processing') return null
  return getEstimatedTimeRemaining(currentJob.value)
})

// Update transfer stats when job progresses
watch(() => currentJob.value?.copied_size_bytes, (newCopied) => {
  if (currentJob.value && newCopied !== undefined) {
    updateProgress(currentJob.value.id, newCopied)
  }
})

const queuedJobs = computed(() => {
  return jobs.value.filter(j => j.status === 'queued')
})

const getJobName = (path: string) => {
  return path.split('/').pop() || path
}

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const loadJobs = async () => {
  try {
    jobs.value = await getQueue()
  } catch (error) {
    // Silently fail
  }
}

// Load jobs on mount and refresh periodically
onMounted(() => {
  loadJobs()
})

// Refresh every 3 seconds
useIntervalFn(() => {
  loadJobs()
}, 3000)

// Close expanded view when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  if (isExpanded.value) {
    const widget = document.querySelector('.floating-widget.expanded')
    if (widget && !widget.contains(event.target as Node)) {
      isExpanded.value = false
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Additional widget styles are in main.css */
</style>

