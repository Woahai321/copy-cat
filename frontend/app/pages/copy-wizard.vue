<template>
  <div class="wizard-container min-h-screen">
    <!-- Step Indicator -->
    <div class="step-indicator sticky top-0 z-40 bg-[var(--win-bg-base)]/90 backdrop-blur-md border-b border-slate-700/50">
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

    <!-- Step 3: Confirmation (Transfer Manifest Loop) -->
    <div v-if="step === 3" class="step-content">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 py-6 sm:py-12 animate-fade-in-up">
        <div class="mb-6 sm:mb-10 text-center">
          <h1 class="text-2xl sm:text-3xl font-bold gradient-brand-text mb-2">Confirm Logic</h1>
          <p class="text-sm sm:text-base text-slate-400">Review the transfer manifest before execution</p>
        </div>

        <div class="relative grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-12 items-stretch">
            
            <!-- Central Flow Arrow (Desktop) -->
            <div class="hidden md:flex absolute inset-0 items-center justify-center pointer-events-none z-10">
                <div class="w-12 h-12 rounded-full bg-[var(--win-bg-base)] border border-[var(--win-accent)] flex items-center justify-center shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                    <UIcon name="i-heroicons-arrow-right" class="w-6 h-6 text-[var(--win-accent)] animate-pulse" />
                </div>
            </div>

            <!-- Mobile Flow Arrow -->
            <div class="md:hidden flex justify-center py-2">
                 <UIcon name="i-heroicons-arrow-down" class="w-8 h-8 text-[var(--win-accent)] animate-bounce" />
            </div>

            <!-- Panel 1: Source (Manifest) -->
            <div class="summary-card h-full flex flex-col">
                <div class="card-header pb-4 border-b border-white/5 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                         <div class="p-2 rounded-lg bg-[var(--brand-1)]/10">
                            <UIcon name="i-heroicons-squares-2x2" class="w-5 h-5 text-[var(--brand-1)]" />
                         </div>
                         <div>
                             <h3 class="text-base font-bold text-white">Source Items</h3>
                             <p class="text-xs text-slate-400">{{ sourceItems.length }} item{{ sourceItems.length !== 1 ? 's' : '' }} selected</p>
                         </div>
                    </div>
                    <span class="text-xs font-mono px-2 py-1 rounded bg-white/5 text-[var(--brand-1)]">{{ totalBulkSize }}</span>
                </div>

                <div class="flex-1 overflow-y-auto custom-scrollbar min-h-[300px] max-h-[50vh] p-1 mt-2 space-y-2">
                    <div v-for="item in sourceItems" :key="item.path" class="group p-3 rounded-xl bg-white/5 border border-white/5 hover:border-[var(--brand-1)]/30 transition-all">
                        <div class="flex items-start gap-3">
                            <UIcon :name="item.path.includes('.') ? 'i-heroicons-document' : 'i-heroicons-folder'" class="w-5 h-5 text-slate-400 mt-0.5 flex-shrink-0" />
                            <div class="flex-1 min-w-0">
                                <div class="text-sm font-medium text-white truncate">{{ item.name }}</div>
                                <div class="text-[10px] text-slate-500 font-mono break-all leading-tight mt-0.5">{{ item.path }}</div>
                            </div>
                            <div class="text-[10px] font-mono text-slate-400 whitespace-nowrap pt-1">
                                {{ item.size_formatted || formatSize(item.size) }}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4 pt-4 border-t border-white/5">
                    <button @click="goToStep(1)" class="w-full py-2 text-xs font-medium text-slate-400 hover:text-white transition-colors flex items-center justify-center gap-2">
                        <UIcon name="i-heroicons-pencil" class="w-3 h-3" />
                        Modify Selection
                    </button>
                </div>
            </div>

            <!-- Panel 2: Destination (Projection) -->
            <div class="summary-card h-full flex flex-col relative text-left">
                <!-- Theme Accent Glow on this card to indicate target -->
                <div class="absolute -inset-[1px] rounded-[0.8rem] bg-gradient-to-b from-[var(--win-accent)]/20 to-transparent opacity-50 pointer-events-none"></div>

                <div class="card-header pb-4 border-b border-white/5 flex items-center justify-between relative z-10">
                    <div class="flex items-center gap-3">
                         <div class="p-2 rounded-lg bg-[var(--win-accent)]/10">
                            <UIcon name="i-heroicons-arrow-down-tray" class="w-5 h-5 text-[var(--win-accent)]" />
                         </div>
                         <div>
                             <h3 class="text-base font-bold text-white">Target Location</h3>
                             <p class="text-xs text-slate-400">Projected Final Paths</p>
                         </div>
                    </div>
                </div>

                <div class="flex-1 overflow-y-auto custom-scrollbar min-h-[300px] max-h-[50vh] p-1 mt-2 space-y-2 relative z-10">
                     <div v-for="item in sourceItems" :key="item.path + '-dest'" class="group p-3 rounded-xl bg-[var(--win-accent)]/5 border border-[var(--win-accent)]/10 hover:border-[var(--win-accent)]/30 transition-all">
                        <div class="flex items-start gap-3">
                            <!-- Visual Consistency: Show same icon type in destination -->
                            <UIcon :name="item.path.includes('.') ? 'i-heroicons-document' : 'i-heroicons-folder'" class="w-5 h-5 text-[var(--win-accent)] mt-0.5 flex-shrink-0" />
                            <div class="flex-1 min-w-0">
                                <div class="flex flex-wrap items-baseline gap-1.5">
                                    <span class="text-sm font-medium text-[var(--win-accent)] truncate">{{ item.name }}</span>
                                    <span class="text-[9px] uppercase tracking-wide px-1.5 py-px rounded bg-[var(--win-accent)] text-[var(--win-bg-base)] font-bold">New</span>
                                </div>
                                <!-- Projected Path Logic: Destination + / + Name -->
                                <div class="text-[10px] text-slate-400 font-mono break-all leading-tight mt-1">
                                    <span class="opacity-50">{{ destPath }}/</span><span class="text-[var(--win-accent)]">{{ item.name }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-4 pt-4 border-t border-white/5 relative z-10">
                    <button @click="goToStep(2)" class="w-full py-2 text-xs font-medium text-slate-400 hover:text-white transition-colors flex items-center justify-center gap-2">
                         <UIcon name="i-heroicons-map" class="w-3 h-3" />
                        Change Target
                    </button>
                </div>
            </div>
        </div>

        <!-- Start Copy Action Bar -->
        <div class="mt-8 sm:mt-12 flex flex-col-reverse sm:flex-row items-center justify-center gap-4 max-w-2xl mx-auto">
           <UButton
            @click="reset"
            variant="ghost"
            color="gray"
            class="w-full sm:w-1/3 h-12 text-slate-400 hover:text-white hover:bg-white/5"
          >
            Cancel & Reset
          </UButton>
          
          <button
            @click="handleStartCopy"
            :disabled="copying"
            class="btn-primary-large w-full sm:w-2/3 h-12 shadow-[0_0_30px_-5px_var(--win-accent)] hover:shadow-[0_0_50px_-10px_var(--win-accent)] transition-all duration-300"
          >
            <UIcon v-if="copying" name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin mr-2" />
            <UIcon v-else name="i-heroicons-bolt" class="w-5 h-5 mr-2" />
            <span class="text-lg">{{ copying ? 'Initializing Transfer...' : 'Start Copy Operation' }}</span>
          </button>
        </div>
      </div>
    </div>
    <!-- Global Sticky Footers (Teleported to Body for Viewport Pinning) -->
    <Teleport to="body">
        <div 
            v-if="step === 1" 
            class="fixed bottom-0 right-0 bg-[var(--glass-level-4-bg)]/98 border-t border-white/10 p-4 pb-safe backdrop-blur-xl z-[100] flex flex-col sm:flex-row items-center justify-between gap-4 shadow-[0_-20px_50px_rgba(0,0,0,0.9)] transition-all duration-300"
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
            class="fixed bottom-0 right-0 bg-[var(--glass-level-4-bg)]/98 border-t border-white/10 p-4 pb-safe backdrop-blur-xl z-[100] flex flex-col sm:flex-row items-center justify-between gap-4 shadow-[0_-20px_50px_rgba(0,0,0,0.9)] transition-all duration-300"
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

/* Step Number */
.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  background: var(--glass-level-2-bg);
  color: var(--win-text-muted);
  border: 2px solid var(--glass-level-2-border);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

/* Step Item Active - Number */
.step-item.active .step-number {
  background: linear-gradient(135deg, var(--win-accent) 0%, var(--brand-5) 100%);
  color: black;
  border-color: var(--win-accent);
  box-shadow: 0 0 20px var(--win-accent);
}

/* Step Divider */
.step-divider {
  width: 30px;
  height: 2px;
  background: var(--glass-level-2-border);
  flex-shrink: 0;
}

/* Summary Card */
.summary-card {
  background: var(--glass-level-1-bg);
  border: 2px solid var(--glass-level-1-border);
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.summary-card:hover {
  border-color: var(--win-accent);
  background: var(--glass-level-2-bg);
}

/* Card Button */
.card-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.625rem;
  background: var(--glass-level-2-bg);
  color: var(--win-accent);
  border: 1px solid var(--glass-level-2-border);
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s ease;
  justify-content: center;
  font-size: 0.875rem;
}

.card-button:hover {
  background: var(--glass-level-3-bg);
  border-color: var(--win-accent);
}

/* Primary Button Large */
.btn-primary-large {
  padding: 0.875rem 2rem;
  font-size: 1rem;
  font-weight: 700;
  background: var(--win-accent);
  color: black;
  border: none;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
  justify-content: center;
  min-height: 44px;
}

.btn-primary-large:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 20px var(--win-accent);
}

.gradient-brand-text {
  color: var(--win-accent);
  background: none;
  -webkit-text-fill-color: initial;
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

