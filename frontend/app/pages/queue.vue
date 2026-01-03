<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-header-title flex items-center gap-3">
          <UIcon name="i-heroicons-queue-list" class="page-header-icon" />
          Active Queue 
          <span class="text-base font-normal text-[var(--win-text-muted)]" v-if="jobs.length">({{ jobs.length }})</span>
        </h1>
        <p class="page-header-subtitle">Monitor and manage active copy operations • Drag to reorder</p>
      </div>
      <div class="flex gap-2">
        <button
          v-if="jobs.length > 0"
          @click="handleClearQueue"
          class="btn-danger"
        >
          <UIcon name="i-heroicons-trash" class="w-4 h-4" />
          <span>Clear All</span>
        </button>
        <button
          @click="loadQueue"
          class="btn-ghost"
        >
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="flex flex-col items-center gap-3">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-[var(--win-accent)] animate-spin" />
        <p class="text-sm text-[var(--win-text-muted)]">Loading queue...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="jobs.length === 0">
      <div class="empty-state">
        <div class="empty-state-icon">
           <UIcon name="i-heroicons-queue-list" class="w-8 h-8 text-[var(--win-text-muted)]" />
        </div>
        <h3 class="empty-state-title">Queue is Empty</h3>
        <p class="empty-state-description">There are no active copy operations at the moment.</p>
        
        <button
           @click="navigateTo('/history')"
           class="btn-primary"
        >
          <UIcon name="i-heroicons-clock" class="w-5 h-5 mr-2" />
          View History
        </button>
      </div>
    </div>

    <!-- Speed Graph (Moved to Top) -->
    <div v-if="jobs.length > 0" class="animate-in fade-in slide-in-from-top-4 duration-500">
        <SpeedGraph :history="speedHistory" />
    </div>

    <!-- Job List with Drag and Drop -->
    <div v-if="jobs.length > 0" class="space-y-3">
      <div
        v-for="(job, index) in jobs"
        :key="job.id"
        :draggable="job.status === 'queued'"
        @dragstart="handleDragStart($event, index)"
        @dragover.prevent="handleDragOver($event, index)"
        @dragenter.prevent
        @drop="handleDrop($event, index)"
        @dragend="handleDragEnd"
        class="relative"
        :class="{ 
          'opacity-50': draggedIndex === index,
          'cursor-move': job.status === 'queued',
          'border-t-2 border-[var(--win-accent)]': dropTargetIndex === index && draggedIndex !== null && draggedIndex !== index
        }"
      >
        <!-- Priority & Drag Handle (for queued jobs) -->
        <div v-if="job.status === 'queued'" class="absolute -left-8 top-1/2 -translate-y-1/2 hidden md:flex flex-col items-center gap-1 z-20">
          <button
            @click="handleMoveToTop(job.id)"
            class="p-1 text-[var(--win-text-muted)] hover:text-[var(--win-accent)] transition-colors"
            title="Move to top"
          >
            <UIcon name="i-heroicons-chevron-double-up" class="w-4 h-4" />
          </button>
          <UIcon name="i-heroicons-bars-3" class="w-4 h-4 text-[var(--win-text-muted)] cursor-move" />
        </div>

        <!-- Priority Badge -->
        <div 
          v-if="job.status === 'queued'" 
          class="absolute -right-2 -top-2 z-20"
        >
          <button
            @click="cyclePriority(job)"
            class="priority-badge"
            :class="getPriorityBadgeClass(job.priority)"
            :title="`Priority: ${getPriorityLabel(job.priority)} (click to change)`"
          >
            <UIcon :name="getPriorityIcon(job.priority)" class="w-3 h-3" />
          </button>
        </div>

        <CopyJobCard
          :job="job"
          :realtime-progress="getJobProgress(job.id)"
          :show-actions="true"
          class="animate-fade-in-up"
          :style="{ animationDelay: `${index * 50}ms` }"
          @cancel="handleCancel"
          @click="selectedJob = job"
        />
      </div>
    </div>



    <!-- Job Detail Modal -->
    <MediaDetailModal 
        v-if="selectedJob"
        :show="!!selectedJob" 
        :item="selectedJob.media_item || selectedJob"
        :job="selectedJob"
        @close="selectedJob = null"
        @cancel="handleCancel"
    />
  </div>
</template>

<script setup lang="ts">
import SpeedGraph from '~/components/SpeedGraph.vue'
import MediaDetailModal from '~/components/MediaDetailModal.vue'

definePageMeta({
  middleware: 'auth'
})

const { getQueue, cancelJob, clearQueue, setJobPriority, reorderQueue } = useApi()
const { getJobProgress } = useWebSocket()
const toast = useToast()

const jobs = ref<any[]>([])
const loading = ref(false)
const speedHistory = ref<number[]>([])

const selectedJob = ref<any>(null)

// Drag and Drop State
const draggedIndex = ref<number | null>(null)
const dropTargetIndex = ref<number | null>(null)

const loadQueue = async (background = false) => {
  if (!background) loading.value = true
  try {
    const data = await getQueue()
    // Sort by priority (desc), then created_at (asc)
    jobs.value = data.sort((a: any, b: any) => {
      if ((b.priority || 1) !== (a.priority || 1)) {
        return (b.priority || 1) - (a.priority || 1)
      }
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    })
  } catch (error) {
    console.error('Failed to load queue:', error)
  } finally {
    if (!background) loading.value = false
  }
}

// Priority helpers
const getPriorityLabel = (priority: number) => {
  if (priority >= 2 || priority > 100) return 'High'
  if (priority === 0) return 'Low'
  return 'Normal'
}

const getPriorityIcon = (priority: number) => {
  if (priority >= 2 || priority > 100) return 'i-heroicons-chevron-double-up'
  if (priority === 0) return 'i-heroicons-chevron-double-down'
  return 'i-heroicons-minus'
}

const getPriorityBadgeClass = (priority: number) => {
  if (priority >= 2 || priority > 100) return 'bg-[var(--brand-1)]/20 text-[var(--brand-1)] border-[var(--brand-1)]/30'
  if (priority === 0) return 'bg-[var(--glass-level-2-bg)] text-[var(--win-text-muted)] border-white/5'
  return 'bg-[var(--brand-10)]/20 text-[var(--brand-10)] border-[var(--brand-10)]/30'
}

const cyclePriority = async (job: any) => {
  const currentPriority = job.priority ?? 1
  let newPriority: number
  
  // Cycle: Normal (1) -> High (2) -> Low (0) -> Normal (1)
  if (currentPriority === 0) newPriority = 1
  else if (currentPriority === 1) newPriority = 2
  else newPriority = 0
  
  try {
    await setJobPriority(job.id, newPriority)
    job.priority = newPriority
    toast.add({
      title: 'Priority Updated',
      description: `Job priority set to ${getPriorityLabel(newPriority)}`,
      color: 'green',
      icon: 'i-heroicons-check-circle',
      timeout: 2000
    })
  } catch (error) {
    console.error('Failed to set priority:', error)
    toast.add({
      title: 'Failed',
      description: 'Could not update priority',
      color: 'red',
      timeout: 3000
    })
  }
}

const handleMoveToTop = async (jobId: number) => {
  try {
    await setJobPriority(jobId, 2)
    await loadQueue()
    toast.add({
      title: 'Moved to Top',
      description: 'Job priority set to High',
      color: 'green',
      icon: 'i-heroicons-check-circle',
      timeout: 2000
    })
  } catch (error) {
    console.error('Failed to move to top:', error)
  }
}

// Drag and Drop Handlers
const handleDragStart = (e: DragEvent, index: number) => {
  if (jobs.value[index].status !== 'queued') {
    e.preventDefault()
    return
  }
  draggedIndex.value = index
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', index.toString())
  }
}

const handleDragOver = (e: DragEvent, index: number) => {
  if (draggedIndex.value === null) return
  if (jobs.value[index].status !== 'queued') return
  dropTargetIndex.value = index
}

const handleDrop = async (e: DragEvent, targetIndex: number) => {
  if (draggedIndex.value === null) return
  if (draggedIndex.value === targetIndex) return
  if (jobs.value[targetIndex].status !== 'queued') return
  
  // Reorder locally first for instant feedback
  const draggedJob = jobs.value[draggedIndex.value]
  const newJobs = [...jobs.value]
  newJobs.splice(draggedIndex.value, 1)
  newJobs.splice(targetIndex, 0, draggedJob)
  jobs.value = newJobs
  
  // Get all queued job IDs in new order
  const queuedJobIds = newJobs
    .filter(j => j.status === 'queued')
    .map(j => j.id)
  
  try {
    await reorderQueue(queuedJobIds)
    toast.add({
      title: 'Queue Reordered',
      description: 'Job order updated',
      color: 'green',
      icon: 'i-heroicons-check-circle',
      timeout: 2000
    })
  } catch (error) {
    console.error('Failed to reorder:', error)
    loadQueue() // Reload to reset
    toast.add({
      title: 'Reorder Failed',
      description: 'Could not save new order',
      color: 'red',
      timeout: 3000
    })
  }
  
  draggedIndex.value = null
  dropTargetIndex.value = null
}

const handleDragEnd = () => {
  draggedIndex.value = null
  dropTargetIndex.value = null
}

// Speed Calculation Logic
const lastTotalBytes = ref(0)
const lastTime = ref(Date.now())

useIntervalFn(() => {
    if (jobs.value.length === 0) {
        speedHistory.value.push(0)
        // Keep moving window
        if (speedHistory.value.length > 50) speedHistory.value.shift()
        lastTotalBytes.value = 0
        return
    }

    // CRITICAL FIX: Calculate total bytes from WebSocket (Realtime) not stale jobs.value
    const currentTotalBytes = jobs.value.reduce((acc, job) => {
        const liveData = getJobProgress(job.id)
        return acc + (liveData?.copied_size_bytes ?? job.copied_size_bytes ?? 0)
    }, 0)

    // Calculate Average Speed over the last 10 seconds
    const now = Date.now()
    const timeDiff = (now - lastTime.value) / 1000 // seconds

    if (timeDiff > 0.1 && lastTotalBytes.value > 0) { 
        const bytesDiff = currentTotalBytes - lastTotalBytes.value
        
        if (bytesDiff < 0) {
             speedHistory.value.push(0)
        } else {
            // Raw Average Speed over the interval (10s)
            // This inherently smoothes out "1 tick peaks"
            const avgSpeed = bytesDiff / timeDiff
            speedHistory.value.push(avgSpeed)
        }
    } else if (lastTotalBytes.value === 0) {
        speedHistory.value.push(0)
    }

    lastTotalBytes.value = currentTotalBytes
    lastTime.value = now
    
    // Keep history length manageable (50 * 10s = ~8 minutes history)
    if (speedHistory.value.length > 50) speedHistory.value.shift()
}, 10000)

const handleCancel = async (jobId: number) => {
  // 1. Optimistically update UI
  const originalJobs = [...jobs.value]
  jobs.value = jobs.value.filter(j => j.id !== jobId)
  
  try {
    // 2. Make API call
    await cancelJob(jobId)
    
    // 3. Show success toast
    toast.add({
      title: 'Job Cancelled',
      description: 'The copy job has been cancelled successfully',
      color: 'green',
      icon: 'i-heroicons-check-circle',
      timeout: 3000
    })
  } catch (error: any) {
    // 4. Rollback on error
    jobs.value = originalJobs
    console.error('Failed to cancel job:', error)
    
    // 5. Show error toast
    toast.add({
      title: 'Cancellation Failed',
      description: error.message || 'Failed to cancel the job',
      color: 'red',
      icon: 'i-heroicons-x-circle',
      timeout: 5000
    })
  }
}

const handleClearQueue = async () => {
    if (!confirm('Are you sure you want to cancel all active jobs? This action cannot be undone.')) return
    
    // 1. Optimistically clear
    const originalJobs = [...jobs.value]
    loading.value = true
    
    try {
        const res = await clearQueue()
        jobs.value = []
        
        toast.add({
          title: 'Queue Cleared',
          description: res.message || 'All jobs have been cancelled',
          color: 'green',
          icon: 'i-heroicons-trash'
        })
    } catch (error: any) {
        jobs.value = originalJobs
        console.error('Failed to clear queue:', error)
        toast.add({
          title: 'Failed to Clear',
          description: error.message || 'Could not clear queue',
          color: 'red'
        })
    } finally {
        loading.value = false
        loadQueue() // Reload to be safe
    }
}

onMounted(() => {
  loadQueue()
})

// Refresh queue every 5 seconds
useIntervalFn(() => {
  loadQueue(true)
}, 5000)
</script>

<style scoped>
.priority-badge {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-width: 1px;
  transition: all 0.2s;
  cursor: pointer;
}

.priority-badge:hover {
  transform: scale(1.1);
}

.priority-badge:active {
  transform: scale(0.95);
}
</style>
