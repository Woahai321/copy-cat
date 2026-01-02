<template>
  <div class="h-[calc(100vh-theme('spacing.14'))] flex flex-col">
    <!-- Header -->
    <div class="page-header px-6 pt-6 pb-2 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="page-header-title flex items-center gap-3">
          <UIcon name="i-heroicons-folder-open" class="page-header-icon" />
          File Browser
        </h1>
        <p class="page-header-subtitle">Explore and manage your files</p>
      </div>

      <!-- Tab Switcher -->
      <div class="flex bg-[var(--glass-level-2-bg)] p-1 rounded-xl border border-white/5 self-start sm:self-auto">
        <button 
          @click="currentTab = 'source'"
          class="px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2"
          :class="currentTab === 'source' ? 'bg-[var(--brand-1)] text-black shadow-lg shadow-[var(--brand-1)]/20' : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-secondary)]'"
        >
          <UIcon name="i-heroicons-cloud" class="w-4 h-4" />
          Source
        </button>
        <button 
          @click="currentTab = 'destination'"
          class="px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2"
          :class="currentTab === 'destination' ? 'bg-[var(--status-success)] text-black shadow-lg shadow-[var(--status-success)]/20' : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-secondary)]'"
        >
        >
          <UIcon name="i-heroicons-server" class="w-4 h-4" />
          Destination
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex min-h-0 relative z-0 p-6 pt-0">
      <div class="w-full h-full glass-panel overflow-hidden flex flex-col">
          <FileExplorer 
             :key="currentTab"
             ref="explorer"
             :initial-path="'/'"
             :source="currentTab"
             :is-destination="currentTab === 'destination'"
             class="flex-1 min-h-0"
          />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import FileExplorer from '~/components/FileExplorer.vue'

definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const currentTab = ref<'source' | 'destination'>((route.query.tab as 'source' | 'destination') || 'source')

// Watch query for external navigation changes
watch(() => route.query.tab, (newTab) => {
  if (newTab && (newTab === 'source' || newTab === 'destination')) {
    currentTab.value = newTab
  }
})

const explorer = ref<InstanceType<typeof FileExplorer> | null>(null)
</script>
