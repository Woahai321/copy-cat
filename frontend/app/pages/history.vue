<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-header-title flex items-center gap-3">
          <UIcon name="i-heroicons-clock" class="page-header-icon" />
          Copy History
        </h1>
        <p class="page-header-subtitle">View all past copy operations</p>
      </div>
      <button
        @click="loadHistory()"
        class="btn-ghost"
      >
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
        <span>Refresh</span>
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-bar-label">
        <UIcon name="i-heroicons-funnel" class="w-4 h-4" />
        <span>Filter:</span>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="option in statusOptions"
          :key="option.value"
          @click="statusFilter = option.value"
          class="filter-pill"
          :class="statusFilter === option.value ? 'filter-pill-active' : 'filter-pill-inactive'"
        >
          {{ option.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="flex flex-col items-center gap-3">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-[var(--win-accent)] animate-spin" />
        <p class="text-sm text-[var(--win-text-muted)]">Loading history...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredJobs.length === 0">
      <div class="empty-state">
        <div class="empty-state-icon">
           <UIcon name="i-heroicons-clock" class="w-8 h-8 text-[var(--win-text-muted)]" />
        </div>
        <h3 class="empty-state-title">No History Found</h3>
        <p class="empty-state-description">
            {{ statusFilter === 'all' ? 'Start a copy operation to see it here.' : `No jobs found with status "${statusFilter}".` }}
        </p>
        
        <button
           v-if="statusFilter === 'all'"
           @click="navigateTo('/browse')"
           class="btn-primary"
        >
          <UIcon name="i-heroicons-plus" class="w-5 h-5 mr-2" />
          Start New Copy
        </button>
      </div>
    </div>

    <!-- Job List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="(job, index) in filteredJobs"
        :key="job.id"
      >
        <CopyJobCard 
            :job="job" 
            :show-actions="true"
            @click="openJobDetails"
            @retry="handleRetry"
        />
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="flex justify-center pt-4">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="btn-secondary"
        >
          <span v-if="!loadingMore" class="flex items-center gap-2">
            <UIcon name="i-heroicons-arrow-down" class="w-5 h-5" />
            Load More
          </span>
          <span v-else class="flex items-center gap-2">
            <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
            Loading...
          </span>
        </button>
      </div>
    </div>


    <!-- Job Detail Modal -->
    <MediaDetailModal 
        v-if="selectedJob"
        :show="showDetailModal" 
        :item="selectedJob.media_item || selectedJob"
        :job="selectedJob"
        @close="closeModal"
        @retry="handleRetry(selectedJob?.id); closeModal()" 
    />
  </div>
</template>

<script setup lang="ts">

import MediaDetailModal from '~/components/MediaDetailModal.vue' // Import Modal

definePageMeta({
  middleware: 'auth'
})

const { getHistory, retryJob, getJob } = useApi() // Added getJob
const toast = useToast()

const jobs = ref<any[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const statusFilter = ref('all')
const currentOffset = ref(0)
const pageSize = 50
const hasMore = ref(true)

// Modal State
const showDetailModal = ref(false)
const selectedJob = ref<any>(null)
const loadingDetails = ref(false)

const openJobDetails = async (job: any) => {
    selectedJob.value = job // Show immediate data first
    showDetailModal.value = true
    
    // Optional: Fetch fresh details if needed (e.g. for logs unavailable in list view)
    // loadingDetails.value = true
    // try {
    //    selectedJob.value = await getJob(job.id)
    // } catch (e) {
    //    console.error("Failed to refresh job details", e)
    // } finally {
    //    loadingDetails.value = false
    // }
}

const closeModal = () => {
    showDetailModal.value = false
    selectedJob.value = null
}



const statusOptions = [
  { label: 'All', value: 'all' },
  { label: 'Completed', value: 'completed' },
  { label: 'Failed', value: 'failed' },
  { label: 'Cancelled', value: 'cancelled' },
  { label: 'Processing', value: 'processing' },
  { label: 'Queued', value: 'queued' }
]

const filteredJobs = computed(() => {
  if (statusFilter.value === 'all') {
    return jobs.value
  }
  return jobs.value.filter(job => job.status === statusFilter.value)
})

const loadHistory = async (reset = true) => {
  if (reset) {
    // Only show full loading state if we have no jobs
    if (jobs.value.length === 0) {
        loading.value = true
    }
    currentOffset.value = 0
    // Don't clear jobs immediately to avoid flash
  } else {
    loadingMore.value = true
  }
  
  try {
    const newJobs = await getHistory(pageSize, currentOffset.value)
    
    if (reset) {
      jobs.value = newJobs
    } else {
      jobs.value = [...jobs.value, ...newJobs]
    }
    
    hasMore.value = newJobs.length === pageSize
    currentOffset.value += newJobs.length
  } catch (error) {
    console.error('Failed to load history:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  loadHistory(false)
}

const handleRetry = async (jobId: number) => {
  // 1. Find the job to retry
  const jobToRetry = jobs.value.find(j => j.id === jobId)
  if (!jobToRetry) return
  
  // 2. Optimistically update UI - mark as retrying
  const originalJobs = [...jobs.value]
  jobs.value = jobs.value.map(j => 
    j.id === jobId ? { ...j, status: 'queued', error_message: null } : j
  )
  
  try {
    // 3. Make API call
    await retryJob(jobId)
    
    // 4. Show success toast
    toast.add({
      title: 'Job Retrying',
      description: 'The failed job has been added back to the queue',
      color: 'green',
      icon: 'i-heroicons-arrow-path',
      timeout: 3000
    })
    
    // 5. Reload to get fresh data
    await loadHistory()
  } catch (error: any) {
    // 6. Rollback on error
    jobs.value = originalJobs
    console.error('Failed to retry job:', error)
    
    // 7. Show error toast
    toast.add({
      title: 'Retry Failed',
      description: error.message || 'Failed to retry the job',
      color: 'red',
      icon: 'i-heroicons-x-circle',
      timeout: 5000
    })
  }
}

watch(statusFilter, () => {
  // Just filter client-side, don't reload
})

onMounted(() => {
  loadHistory()
})
</script>
