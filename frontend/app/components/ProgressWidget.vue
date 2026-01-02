<template>
  <Teleport to="body">
    <div v-if="hasActiveJobs || isExpanded" class="floating-widget" :class="{ minimized: !isExpanded, expanded: isExpanded }">
      <!-- Minimized state -->
      <div v-if="!isExpanded" @click="isExpanded = true" class="flex items-center gap-3 cursor-pointer">
        <div class="relative">
          <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 text-[var(--win-accent)] animate-spin" />
        </div>
        <div>
          <p class="text-sm font-semibold text-[var(--win-text-primary)]">{{ activeJobsCount }} Active Job{{ activeJobsCount !== 1 ? 's' : '' }}</p>
          <p v-if="currentJob" class="text-xs text-[var(--win-text-muted)]">
            {{ currentJob.progress_percent }}% · {{ currentJobEta || 'Calculating...' }}
          </p>
        </div>
        <UIcon name="i-heroicons-chevron-up" class="w-4 h-4 text-[var(--win-text-muted)] ml-2" />
      </div>

      <!-- Expanded state -->
      <div v-else class="flex flex-col h-full">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-white/10">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-queue-list" class="w-5 h-5 text-[var(--brand-4)]" />
            <h3 class="font-semibold text-[var(--win-text-primary)]">Active Jobs</h3>
          </div>
          <button @click="isExpanded = false" class="text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] transition">
            <UIcon name="i-heroicons-chevron-down" class="w-5 h-5" />
          </button>
        </div>

        <!-- Current job -->
        <div v-if="currentJob" class="p-4 border-b border-white/10">
          <div class="mb-3">
            <div class="flex items-center justify-between mb-2">
              <p class="text-sm font-semibold text-[var(--win-text-primary)] truncate flex-1">
                {{ getJobName(currentJob.source_path) }}
              </p>
              <span class="text-xs font-bold text-[var(--win-accent)] ml-2">{{ currentJob.progress_percent }}%</span>
            </div>
            <div class="progress-bar mb-2">
              <div class="progress-bar-fill" :style="{ width: `${currentJob.progress_percent}%` }"></div>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-[var(--win-text-muted)]">{{ formatSize(currentJob.copied_size_bytes) }}</span>
              <span v-if="currentJobEta" class="text-[var(--win-accent)] font-medium">{{ currentJobEta }}</span>
              <span class="text-[var(--win-text-muted)]">{{ formatSize(currentJob.total_size_bytes) }}</span>
            </div>
          </div>
          <p class="text-xs text-[var(--win-text-muted)] truncate">→ {{ currentJob.destination_path }}</p>
        </div>

        <!-- Queue list -->
        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="queuedJobs.length > 0" class="space-y-2">
            <p class="text-xs font-semibold text-[var(--win-text-muted)] mb-2">QUEUED ({{ queuedJobs.length }})</p>
            <div
              v-for="job in queuedJobs"
              :key="job.id"
              class="card p-3 flex items-center justify-between"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm text-[var(--win-text-primary)] truncate">{{ getJobName(job.source_path) }}</p>
                <p class="text-xs text-[var(--win-text-muted)] truncate">{{ job.destination_path }}</p>
              </div>
              <UBadge color="gray" variant="soft" size="xs">Queued</UBadge>
            </div>
          </div>
          <div v-else-if="!currentJob" class="text-center py-8">
            <p class="text-sm text-[var(--win-text-muted)]">No active jobs</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t border-white/10">
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

