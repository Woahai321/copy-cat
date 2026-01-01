<template>
  <div class="wizard-container min-h-screen">
    <!-- Step Indicator -->
    <div class="step-indicator sticky top-0 z-40 bg-[#000000]/90 backdrop-blur-md border-b border-slate-700/50">
      <div class="max-w-4xl mx-auto px-3 sm:px-6 py-3 sm:py-4 flex items-center justify-center gap-4 sm:gap-8">
        <div 
          class="step-item"
          :class="{ 'active': step === 1, 'completed': step > 1 }"
        >
          <div class="step-number">
            <UIcon v-if="step > 1" name="i-heroicons-check" class="w-4 h-4 sm:w-5 sm:h-5" />
            <span v-else class="text-sm sm:text-base">1</span>
          </div>
          <span class="step-label hidden sm:inline">Choose Source</span>
          <span class="step-label sm:hidden text-xs">Source</span>
        </div>
        
        <div class="step-divider"></div>
        
        <div 
          class="step-item"
          :class="{ 'active': step === 2, 'completed': step > 2 }"
        >
          <div class="step-number">
            <UIcon v-if="step > 2" name="i-heroicons-check" class="w-4 h-4 sm:w-5 sm:h-5" />
            <span v-else class="text-sm sm:text-base">2</span>
          </div>
          <span class="step-label hidden sm:inline">Choose Destination</span>
          <span class="step-label sm:hidden text-xs">Dest</span>
        </div>
        
        <div class="step-divider"></div>
        
        <div 
          class="step-item"
          :class="{ 'active': step === 3 }"
        >
          <div class="step-number">
            <span class="text-sm sm:text-base">3</span>
          </div>
          <span class="step-label hidden sm:inline">Confirm & Copy</span>
          <span class="step-label sm:hidden text-xs">Confirm</span>
        </div>
      </div>
    </div>

    <!-- Step 1: Source Selection -->
    <div v-if="step === 1" class="step-content">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 py-4 sm:py-8 pb-32 sm:pb-28 animate-fade-in-up">
        <div class="mb-4 sm:mb-6">
          <h1 class="text-2xl sm:text-3xl font-bold gradient-brand-text mb-2">Select Source Folder</h1>
          <p class="text-sm sm:text-base text-slate-400">Choose the folder you want to copy from Zurg drive</p>
        </div>
        
        <FileExplorer
          :key="`source-${step}`"
          source="zurg"
          title="Zurg Drive (Source)"
          :selectable="true"
          @selection-change="onSelectionChange"
          class="wizard-explorer"
        />
      </div>
    </div>

    <!-- Step 2: Destination Selection -->
    <div v-if="step === 2" class="step-content">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 py-4 sm:py-8 pb-32 sm:pb-28 animate-fade-in-up">
        <div class="mb-4 sm:mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold gradient-brand-text mb-2">Select Destination</h1>
            <p class="text-sm sm:text-base text-slate-400">Choose where to copy to on your 16TB drive</p>
          </div>
          <button
            @click="prevStep"
            class="btn-secondary flex items-center gap-2 w-full sm:w-auto touch-target"
          >
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4 sm:w-5 sm:h-5" />
            <span class="text-sm sm:text-base">Back</span>
          </button>
        </div>
        
        <FileExplorer
          :key="`dest-${step}`"
          source="16tb"
          title="16TB Drive (Destination)"
          :selectable="true"
          @selection-change="onSelectionChange"
          class="wizard-explorer"
        />
      </div>
    </div>

    <!-- Step 3: Summary & Confirm -->
    <div v-if="step === 3" class="step-content">
      <div class="max-w-5xl mx-auto px-3 sm:px-6 py-6 sm:py-12 animate-fade-in-up">
        <div class="mb-6 sm:mb-8 text-center">
          <h1 class="text-2xl sm:text-3xl font-bold gradient-brand-text mb-2">Confirm Copy</h1>
          <p class="text-sm sm:text-base text-slate-400">Review your selection and start the copy</p>
        </div>

        <div class="summary-grid" :class="{ 'bulk-grid': isBulk }">
          <!-- Source Card -->
          <div class="summary-card">
            <div class="card-header">
              <UIcon name="i-heroicons-folder-open" class="w-5 h-5 sm:w-6 sm:h-6 text-[var(--brand-1)]" />
              <h3 class="text-base sm:text-lg">Source</h3>
            </div>
            <div class="card-content">
              <div class="path-display">
                <UIcon name="i-heroicons-server" class="w-4 h-4 sm:w-5 sm:h-5 text-[var(--win-accent)]" />
                <span class="font-mono text-xs sm:text-sm">Zurg</span>
              </div>
              
              <div v-if="isBulk" class="space-y-3 mt-2 flex flex-col flex-1 min-h-0">
                <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
                  <span class="font-bold text-white">{{ sourceItems.length }} items selected</span>
                  <span class="text-[var(--win-accent)] font-mono">{{ totalBulkSize }}</span>
                </div>
                <div class="flex-1 overflow-y-auto pr-2 custom-scrollbar min-h-0 bg-black/20 rounded border border-white/5 p-2">
                  <div v-for="item in sourceItems" :key="item.path" class="text-[10px] mb-2 last:mb-0 border-b border-white/5 last:border-0 pb-1 last:pb-0">
                    <div class="font-mono text-gray-300 break-all leading-tight">{{ item.path }}</div>
                    <div class="text-[9px] text-gray-500 mt-0.5 text-right font-mono">{{ item.size_formatted || formatSize(item.size) }}</div>
                  </div>
                </div>
              </div>
              <p v-else class="path-text">{{ sourcePath || 'Not selected' }}</p>
              
              <div v-if="sourceInfo && !isBulk" class="mt-2 sm:mt-3 text-xs sm:text-sm text-slate-400">
                <span>Size: {{ sourceInfo.size_formatted }}</span>
              </div>
            </div>
            <button @click="goToStep(1)" class="card-button touch-target">
              <UIcon name="i-heroicons-pencil" class="w-4 h-4" />
              <span class="text-sm sm:text-base">Change Source</span>
            </button>
          </div>

          <!-- Arrow -->
          <div class="arrow-container" v-if="!isBulk">
            <UIcon name="i-heroicons-arrow-right" class="w-8 h-8 sm:w-12 sm:h-12 text-[var(--win-accent)]" />
          </div>

          <!-- Destination Card -->
          <div class="summary-card">
            <div class="card-header">
              <UIcon name="i-heroicons-folder" class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-400" />
              <h3 class="text-base sm:text-lg">Destination</h3>
            </div>
            <div class="card-content">
              <div class="path-display">
                <UIcon name="i-heroicons-server" class="w-4 h-4 sm:w-5 sm:h-5 text-[var(--win-accent)]" />
                <span class="font-mono text-xs sm:text-sm">16TB</span>
              </div>
              <p class="path-text">{{ destPath || 'Not selected' }}</p>
            </div>
            <button @click="goToStep(2)" class="card-button touch-target">
              <UIcon name="i-heroicons-pencil" class="w-4 h-4" />
              <span class="text-sm sm:text-base">Change Destination</span>
            </button>
          </div>
        </div>

        <!-- Start Copy Button -->
        <div class="mt-8 sm:mt-12 flex flex-col items-center gap-3 sm:gap-4">
          <button
            @click="handleStartCopy"
            :disabled="copying"
            class="btn-primary-large w-full sm:w-auto"
          >
            <UIcon v-if="copying" name="i-heroicons-arrow-path" class="w-5 h-5 sm:w-6 sm:h-6 mr-2 sm:mr-3 animate-spin" />
            <UIcon v-else name="i-heroicons-play" class="w-5 h-5 sm:w-6 sm:h-6 mr-2 sm:mr-3" />
            <span class="text-base sm:text-lg">{{ copying ? 'Starting Copy...' : 'Start Copy' }}</span>
          </button>
          <UButton
            @click="reset"
            variant="ghost"
            color="gray"
            class="text-slate-400 hover:text-slate-200 w-full sm:w-auto touch-target"
          >
            Cancel & Reset Wizard
          </UButton>
        </div>
      </div>
    </div>
    <!-- Global Sticky Footers (Teleported to Body for Viewport Pinning) -->
    <Teleport to="body">
        <div 
            v-if="step === 1" 
            class="fixed bottom-0 right-0 bg-[#0a0a0a]/98 border-t border-white/10 p-4 pb-safe backdrop-blur-xl z-[100] flex flex-col sm:flex-row items-center justify-between gap-4 shadow-[0_-20px_50px_rgba(0,0,0,0.9)] transition-all duration-300"
            :style="footerStyle"
        >
            <div class="flex-1 w-full sm:w-auto overflow-hidden min-w-0">
                <div class="text-[10px] text-gray-500 uppercase font-bold mb-1 tracking-wider">Source Selected</div>
                <div class="font-mono text-sm text-[var(--brand-1)] break-all truncate" :title="tempSelectedPaths.join(', ')">
                    {{ tempSelectedPaths.length > 1 ? `${tempSelectedPaths.length} items selected` : (tempSelectedPaths[0] || 'Select a folder or file') }}
                </div>
            </div>
            <button 
                @click="confirmSourceSelection"
                :disabled="tempSelectedPaths.length === 0"
                class="w-full sm:w-auto px-10 py-3.5 rounded-xl bg-[var(--win-accent)] text-black font-bold hover:scale-105 active:scale-95 transition-all disabled:opacity-30 disabled:hover:scale-100 flex-shrink-0 shadow-lg shadow-[var(--brand-1)]/20"
            >
                Next Step
            </button>
        </div>

        <div 
            v-if="step === 2"
            class="fixed bottom-0 right-0 bg-[#0a0a0a]/98 border-t border-white/10 p-4 pb-safe backdrop-blur-xl z-[100] flex flex-col sm:flex-row items-center justify-between gap-4 shadow-[0_-20px_50px_rgba(0,0,0,0.9)] transition-all duration-300"
            :style="footerStyle"
        >
            <div class="flex-1 w-full sm:w-auto overflow-hidden min-w-0">
                <div class="text-[10px] text-gray-500 uppercase font-bold mb-1 tracking-wider">Destination Selected</div>
                <div class="font-mono text-sm text-emerald-400 break-all truncate" :title="tempSelectedPaths[0]">
                    {{ tempSelectedPaths[0] || 'Select destination path' }}
                </div>
            </div>
            <button 
                @click="confirmDestSelection"
                :disabled="tempSelectedPaths.length === 0"
                class="w-full sm:w-auto px-10 py-3.5 rounded-xl bg-emerald-500 text-black font-bold hover:scale-105 active:scale-95 transition-all disabled:opacity-30 disabled:hover:scale-100 flex-shrink-0 shadow-lg shadow-emerald-500/20"
            >
                Review & Copy
            </button>
        </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '#imports'
import { useCopyWizard } from '~/composables/useCopyWizard'

definePageMeta({
  middleware: 'auth'
})

const { step, sourcePath, destPath, sourceInfo, sourceItems, isBulk, setSource, setDestination, nextStep, prevStep, goToStep, reset } = useCopyWizard()
const { startCopy, batchCopyItems, getFolderInfo } = useApi()
const toast = useToast()
const router = useRouter()
const sidebarOpen = useState('sidebarOpen')

const footerStyle = computed(() => {
    if (window.innerWidth < 1024) return { left: '0px' }
    return { left: sidebarOpen.value ? '260px' : '80px' }
})

const copying = ref(false)
const tempSelectedPaths = ref<string[]>([])

const formatSize = (bytes: number | undefined) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const totalBulkSize = computed(() => {
    if (!isBulk.value || !sourceItems.value) return '0 B'
    const total = sourceItems.value.reduce((acc, item) => acc + (item.size || 0), 0)
    return formatSize(total)
})

// Reset temp selection when step changes
watch(step, () => {
    tempSelectedPaths.value = []
})

const onSelectionChange = (files: Set<string>) => {
    tempSelectedPaths.value = Array.from(files)
}

const confirmSourceSelection = async () => {
    if (tempSelectedPaths.value.length === 0) return
    await handleSourceSelect(tempSelectedPaths.value)
}

const confirmDestSelection = () => {
    if (tempSelectedPaths.value.length === 0) return
    handleDestinationSelect(tempSelectedPaths.value[0])
}

const handleSourceSelect = async (path: string | string[]) => {
  try {
    const paths = Array.isArray(path) ? path : [path]
    
    // Get info for all selected items
    const infoPromises = paths.map(p => getFolderInfo('zurg', p, true))
    const infos = await Promise.all(infoPromises)
    
    const wizardInfos = infos.map((info, index) => ({
      name: paths[index].split('/').pop() || paths[index],
      path: paths[index],
      size: info.size,
      size_formatted: info.size_formatted
    }))

    if (wizardInfos.length === 1) {
        setSource(paths[0], wizardInfos[0])
    } else {
        setSource(paths, wizardInfos)
    }
    nextStep()
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to get folder info',
      color: 'red',
      timeout: 3000
    })
  }
}

const handleDestinationSelect = (path: string) => {
  setDestination(path)
  nextStep()
}

const handleStartCopy = async () => {
  if (!sourcePath.value || !destPath.value) {
    if (!isBulk.value || !destPath.value) {
        toast.add({
          title: 'Error',
          description: 'Please select destination',
          color: 'red',
          timeout: 3000
        })
        return
    }
  }

  copying.value = true

  try {
    if (isBulk.value) {
        const itemIds = sourceItems.value.map(i => (i as any).id).filter(Boolean)
        // If items from library don't have IDs, we'd need to handle that, but typically they do.
        // For now, let's assume library items passed via URL/state have IDs if coming from library
        await batchCopyItems(itemIds, destPath.value)
    } else {
        await startCopy(sourcePath.value, destPath.value)
    }

    toast.add({
      title: 'Success',
      description: isBulk.value ? 'Batch copy jobs started' : 'Copy job started successfully',
      color: 'green',
      icon: 'i-heroicons-check-circle',
      timeout: 3000
    })
    reset() // Reset wizard after starting copy
    router.push('/queue') // Redirect to queue page
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to start copy job',
      color: 'red',
      icon: 'i-heroicons-x-circle',
      timeout: 5000
    })
  } finally {
    copying.value = false
  }
}

onMounted(async () => {
  const route = useRoute()
  const sourceParam = route.query.source as string
  const typeParam = route.query.type as string

  if (sourceParam) {
    // Auto-select source from URL
    await handleSourceSelect(sourceParam)
    
    // Auto-select destination from defaults if type provided
    if (typeParam) {
        try {
            const { token } = useAuth()
            const config = useRuntimeConfig()
            if (token.value) {
                const settings = await $fetch<any>(`${config.public.apiBase}/api/settings`, {
                    headers: { 'Authorization': `Bearer ${token.value}` }
                })
                
                let defaultPath = ''
                if (typeParam === 'movie' && settings.default_movies_path) {
                    defaultPath = settings.default_movies_path
                } else if ((typeParam === 'tv' || typeParam === 'show') && settings.default_series_path) {
                    defaultPath = settings.default_series_path
                }

                if (defaultPath) {
                    handleDestinationSelect(defaultPath)
                }
            }
        } catch (e) {
            console.error("Failed to load defaults", e)
        }
    }

  } else {
    // Reset wizard state if user navigates directly to this page without a source and state is incomplete
    if (step.value !== 1 && (!sourcePath.value || !destPath.value)) {
      reset()
    }
  }
})
</script>

<style scoped>
.wizard-container {
  background: transparent;
}

.step-indicator {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

@media (min-width: 640px) {
  .step-item {
    gap: 0.75rem;
  }
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  background: rgba(96, 205, 255, 0.1);
  color: #94a3b8;
  border: 2px solid rgba(96, 205, 255, 0.2);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

@media (min-width: 640px) {
  .step-number {
    width: 40px;
    height: 40px;
  }
}

.step-item.active .step-number {
  background: linear-gradient(135deg, var(--brand-1) 0%, var(--brand-5) 100%);
  color: black;
  border-color: var(--brand-1);
  box-shadow: 0 0 20px rgba(96, 205, 255, 0.4);
}

.step-item.completed .step-number {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.step-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  transition: color 0.3s ease;
}

@media (min-width: 640px) {
  .step-label {
    font-size: 0.875rem;
  }
}

.step-item.active .step-label {
  color: #ffffff;
  font-weight: 600;
}

.step-divider {
  width: 30px;
  height: 2px;
  background: rgba(96, 205, 255, 0.2);
  flex-shrink: 0;
}

@media (min-width: 640px) {
  .step-divider {
    width: 60px;
  }
}

.step-content {
  min-height: calc(100vh - 80px);
  position: relative;
  padding-bottom: 0;
}

@media (max-width: 639px) {
  .step-content {
    min-height: calc(100vh - 70px);
  }
}

.wizard-explorer {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  max-height: calc(100vh - 400px);
  height: calc(100vh - 400px);
  min-height: 400px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

@media (max-width: 1024px) {
  .wizard-explorer {
    max-height: calc(100vh - 450px);
    height: calc(100vh - 450px);
  }
}

@media (max-width: 767px) {
  .wizard-explorer {
    max-height: 60vh;
    height: 60vh;
  }
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  align-items: stretch;
}

@media (max-width: 767px) {
  .summary-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .arrow-container {
    transform: rotate(90deg);
  }
}

.summary-card {
  background: rgba(96, 205, 255, 0.05);
  border: 2px solid rgba(96, 205, 255, 0.2);
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

@media (min-width: 640px) {
  .summary-card {
    border-radius: 1rem;
    padding: 2rem;
  }
}

.summary-card:hover {
  border-color: rgba(96, 205, 255, 0.4);
  background: rgba(96, 205, 255, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

@media (min-width: 640px) {
  .card-header {
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }
}

.card-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
}

@media (min-width: 640px) {
  .card-header h3 {
    font-size: 1.25rem;
  }
}

.card-content {
  margin-bottom: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

@media (min-width: 640px) {
  .card-content {
    margin-bottom: 1.5rem;
  }
}

.path-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
}

@media (min-width: 640px) {
  .path-display {
    margin-bottom: 0.75rem;
  }
}

.path-text {
  font-size: 0.75rem;
  color: #cbd5e1;
  word-break: break-all;
  font-family: monospace;
  line-height: 1.5;
}

@media (min-width: 640px) {
  .path-text {
    font-size: 0.875rem;
  }
}

.card-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.625rem;
  background: rgba(96, 205, 255, 0.1);
  color: #60cdff;
  border: 1px solid rgba(96, 205, 255, 0.3);
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s ease;
  justify-content: center;
  font-size: 0.875rem;
}

@media (min-width: 640px) {
  .card-button {
    padding: 0.75rem;
    font-size: 1rem;
  }
}

.card-button:hover {
  background: rgba(96, 205, 255, 0.2);
  border-color: var(--brand-1);
}

.arrow-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.btn-primary-large {
  padding: 0.875rem 2rem;
  font-size: 1rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--brand-1) 0%, var(--brand-10) 100%);
  color: white;
  border: none;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  box-shadow: 0 8px 16px rgba(96, 205, 255, 0.3);
  justify-content: center;
  min-height: 44px;
}

@media (min-width: 640px) {
  .btn-primary-large {
    padding: 1rem 3rem;
    font-size: 1.125rem;
    min-width: 280px;
  }
}

.btn-primary-large:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(96, 205, 255, 0.4);
}

.btn-primary-large:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.gradient-brand-text {
  background: linear-gradient(135deg, var(--brand-1) 0%, var(--brand-10) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Standardized Page Components (Ported for Copy Wizard) */
.bulk-grid {
    grid-template-columns: 1fr 1fr !important;
}

@media (max-width: 767px) {
    .bulk-grid {
        grid-template-columns: 1fr !important;
    }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

/* Safe area support for mobile devices */
.pb-safe {
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}

/* Ensure footer is always visible */
.fixed.bottom-0 {
  position: fixed;
  bottom: 0;
  right: 0;
  z-index: 1000; /* High z-index for teleported layer */
}
</style>

