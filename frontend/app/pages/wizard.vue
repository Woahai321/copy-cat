<template>
  <div class="h-[calc(100vh-theme('spacing.14'))] flex flex-col relative overflow-hidden">
    
    <!-- Wizard Progress / Header -->
    <div class="px-8 py-6 border-b border-white/5 bg-[var(--glass-level-2-bg)] flex flex-col md:flex-row items-center justify-between gap-4">
       <div>
          <h1 class="text-2xl font-bold text-[var(--win-text-primary)] flex items-center gap-3">
             <div class="p-2 rounded-lg bg-gradient-to-br from-[var(--brand-1)]/20 to-[var(--brand-5)]/20 border border-[var(--brand-1)]/30">
                <UIcon name="i-heroicons-wand-sparkles" class="w-6 h-6 text-[var(--brand-1)]" />
             </div>
             Copy Wizard
          </h1>
          <p class="text-sm text-[var(--win-text-muted)] mt-1">Step-by-step file transfer assistance</p>
       </div>

       <!-- Steps Indicator -->
       <div class="flex items-center gap-2">
          <div class="flex flex-col items-center gap-1 cursor-pointer" @click="canGoToStep(1) && (step = 1)">
             <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border transition-all"
                :class="step >= 1 ? 'bg-[var(--win-accent)] text-[var(--win-bg-base)] border-[var(--win-accent)] shadow-[0_0_10px_rgba(96,205,255,0.4)]' : 'bg-[var(--glass-level-1-bg)] text-[var(--win-text-muted)] border-white/10'"
             >1</div>
             <span class="text-[10px] font-medium uppercase tracking-wider" :class="step >= 1 ? 'text-[var(--win-accent)]' : 'text-[var(--win-text-secondary)]'">Source</span>
          </div>
          <div class="w-12 h-0.5" :class="step >= 2 ? 'bg-[var(--win-accent)]/50' : 'bg-[var(--glass-level-1-bg)]'"></div>
          <div class="flex flex-col items-center gap-1 cursor-pointer" @click="canGoToStep(2) && (step = 2)">
             <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border transition-all"
                :class="step >= 2 ? 'bg-[var(--win-accent)] text-[var(--win-bg-base)] border-[var(--win-accent)] shadow-[0_0_10px_rgba(96,205,255,0.4)]' : 'bg-[var(--glass-level-1-bg)] text-[var(--win-text-muted)] border-white/10'"
             >2</div>
             <span class="text-[10px] font-medium uppercase tracking-wider" :class="step >= 2 ? 'text-[var(--win-accent)]' : 'text-[var(--win-text-secondary)]'">Dest</span>
          </div>
          <div class="w-12 h-0.5" :class="step >= 3 ? 'bg-[var(--win-accent)]/50' : 'bg-[var(--glass-level-1-bg)]'"></div>
          <div class="flex flex-col items-center gap-1">
             <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border transition-all"
                :class="step >= 3 ? 'bg-[var(--win-accent)] text-[var(--win-bg-base)] border-[var(--win-accent)] shadow-[0_0_10px_rgba(96,205,255,0.4)]' : 'bg-[var(--glass-level-1-bg)] text-[var(--win-text-muted)] border-white/10'"
             >3</div>
             <span class="text-[10px] font-medium uppercase tracking-wider" :class="step >= 3 ? 'text-[var(--win-accent)]' : 'text-[var(--win-text-secondary)]'">Review</span>
          </div>
       </div>
    </div>

    <!-- Step 1: Source Selection -->
    <div v-show="step === 1" class="flex-1 flex flex-col min-h-0 animate-in slide-in-from-right-10 fade-in duration-300">
       <div class="px-8 py-3 bg-[var(--win-accent)]/5 border-b border-[var(--win-accent)]/10 text-[var(--brand-1)] text-sm flex items-center gap-2">
          <UIcon name="i-heroicons-information-circle" class="w-5 h-5" />
          Select the files or folders you want to copy.
       </div>
       <div class="flex-1 relative">
          <FileExplorer 
             ref="sourceExplorer"
             :initial-path="'/'"
             @selection-change="updateSourceSelection"
          />
       </div>
       <!-- Footer Action -->
       <div class="p-6 border-t border-white/10 flex justify-between items-center bg-[var(--glass-level-3-bg)]">
          <div class="text-sm text-[var(--win-text-muted)]">
             Selected: <span class="text-[var(--win-text-primary)] font-bold">{{ sourceSelection.size }}</span> items
          </div>
          <button 
             @click="step = 2" 
             :disabled="sourceSelection.size === 0"
             class="btn-primary flex items-center gap-2 px-8"
          >
             Next: Select Destination <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
          </button>
       </div>
    </div>

    <!-- Step 2: Destination Selection -->
    <div v-show="step === 2" class="flex-1 flex flex-col min-h-0 animate-in slide-in-from-right-10 fade-in duration-300">
       <div class="px-8 py-3 bg-[var(--status-success)]/5 border-b border-[var(--status-success)]/10 text-[var(--status-success)] text-sm flex items-center gap-2">
          <UIcon name="i-heroicons-folder-open" class="w-5 h-5" />
          Navigate to the folder where you want to copy items to.
       </div>
       <div class="flex-1 relative">
          <FileExplorer 
             ref="destinationExplorer"
             :initial-path="'/'"
             :is-destination="true"
          />
       </div>
       <!-- Footer Action -->
       <div class="p-6 border-t border-white/10 flex justify-between items-center bg-[var(--glass-level-3-bg)]">
          <button @click="step = 1" class="btn-ghost flex items-center gap-2">
             <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Back
          </button>
          <div class="text-center text-sm text-[var(--win-text-muted)]">
              Current Path: <span class="text-[var(--win-text-primary)] font-mono bg-[var(--glass-level-1-bg)] px-2 py-1 rounded-lg ml-1">{{ destinationPath }}</span>
          </div>
          <button 
             @click="goToReview" 
             class="btn-primary flex items-center gap-2 px-8"
          >
             Next: Review & Confirm <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
          </button>
       </div>
    </div>

    <!-- Step 3: Confirmation -->
    <div v-if="step === 3" class="flex-1 flex flex-col items-center justify-center p-8 animate-in zoom-in-95 fade-in duration-300 relative">
       <!-- Background Glow -->
       <div class="absolute w-[500px] h-[500px] bg-[var(--win-accent)]/10 blur-[120px] rounded-full pointer-events-none -top-20 -left-20"></div>
       <div class="absolute w-[500px] h-[500px] bg-[var(--status-success)]/10 blur-[120px] rounded-full pointer-events-none -bottom-20 -right-20"></div>

       <!-- Manifest Card -->
       <div class="glass-panel w-full max-w-6xl relative overflow-hidden shadow-2xl">
           <!-- Gradient Border Line Top -->
           <div class="h-1 w-full bg-gradient-to-r from-[var(--win-accent)] via-white/20 to-[var(--status-success)] opacity-50"></div>
           
           <!-- Content Container -->
           <div class="flex flex-col md:flex-row relative z-10 max-h-[70vh] md:max-h-none overflow-y-auto md:overflow-visible">
               
               <!-- SOURCE COLUMN -->
               <div class="flex-1 p-6 md:p-8 border-b md:border-b-0 md:border-r border-white/5 bg-gradient-to-b from-[var(--win-accent)]/5 to-transparent relative">
                   <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-[var(--win-accent)]/20 to-transparent"></div>
                   
                   <div class="flex items-center justify-between mb-6">
                       <div class="text-xs font-bold text-[var(--win-accent)] uppercase tracking-widest flex items-center gap-2">
                           <div class="w-2 h-2 rounded-full bg-[var(--win-accent)] shadow-[0_0_10px_rgba(96,205,255,0.8)] animate-pulse"></div>
                           Source Manifest
                       </div>
                       <div class="text-xs font-mono text-[var(--win-text-muted)] bg-white/5 px-2 py-1 rounded-lg">
                           {{ sourceSelection.size }} Items
                       </div>
                   </div>

                   <!-- File Stack Visual -->
                   <div class="space-y-2 max-h-[200px] md:max-h-[300px] overflow-y-auto pr-2 custom-scrollbar mask-gradient-bottom">
                       <div v-for="(item, index) in Array.from(sourceSelection).slice(0, 50)" :key="item" 
                            class="group flex items-center gap-3 p-3 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] transition-all duration-200"
                            :style="{ animationDelay: `${index * 20}ms` }"
                       >
                           <UIcon name="i-heroicons-document" class="w-4 h-4 text-[var(--win-text-muted)] group-hover:text-[var(--win-accent)] transition-colors" />
                           <span class="text-sm text-[var(--win-text-secondary)] font-mono truncate w-full group-hover:text-[var(--win-text-primary)] transition-colors">
                               {{ item.split('/').pop() }}
                           </span>
                       </div>
                       <div v-if="sourceSelection.size > 50" class="text-center py-2 text-xs text-[var(--win-text-muted)] font-mono italic">
                            + {{ sourceSelection.size - 50 }} additional files
                       </div>
                   </div>
               </div>

               <!-- CENTER CONNECTOR (Desktop) -->
               <div class="hidden md:flex w-16 relative items-center justify-center pointer-events-none">
                    <div class="absolute h-[80%] w-px border-l border-dashed border-white/10"></div>
                     <div class="w-10 h-10 rounded-xl bg-[var(--glass-level-4-bg)] border border-white/10 flex items-center justify-center z-10 shadow-xl">
                        <UIcon name="i-heroicons-arrow-right" class="w-5 h-5 text-[var(--win-text-muted)]" />
                    </div>
               </div>

               <!-- CENTER CONNECTOR (Mobile) -->
               <div class="md:hidden w-full h-12 relative flex items-center justify-center pointer-events-none -my-4 z-20">
                    <div class="w-10 h-10 rounded-xl bg-black/80 border border-white/10 flex items-center justify-center z-10 shadow-xl">
                        <UIcon name="i-heroicons-arrow-down" class="w-4 h-4 text-[var(--win-text-muted)]" />
                    </div>
               </div>

               <!-- DESTINATION COLUMN -->
               <div class="flex-1 p-6 md:p-8 bg-gradient-to-b from-[var(--status-success)]/5 to-transparent relative flex flex-col">
                   <div class="flex items-center justify-between mb-6">
                        <div class="text-xs text-[var(--win-text-muted)] font-mono">Target</div>
                        <div class="text-xs font-bold text-[var(--status-success)] uppercase tracking-widest flex items-center gap-2">
                           Destination <div class="w-2 h-2 rounded-full bg-[var(--status-success)] shadow-[0_0_10px_rgba(52,211,153,0.8)]"></div>
                       </div>
                   </div>

                   <div class="flex-1 flex flex-col items-center justify-center py-4 md:py-8">
                       <!-- Folder Card -->
                       <div class="relative group cursor-default">
                           <div class="absolute inset-0 bg-[var(--status-success)]/20 blur-2xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                           <div class="w-24 h-24 md:w-32 md:h-32 rounded-3xl bg-gradient-to-br from-white/5 to-black border border-white/10 flex flex-col items-center justify-center shadow-2xl relative z-10 group-hover:border-[var(--status-success)]/30 transition-all duration-300 group-hover:-translate-y-1">
                               <UIcon name="i-heroicons-folder" class="w-10 h-10 md:w-12 md:h-12 text-[var(--status-success)] mb-2" />
                               <div class="text-[10px] text-[var(--win-text-muted)] uppercase tracking-wider">Drive</div>
                           </div>
                       </div>

                       <div class="mt-6 md:mt-8 w-full">
                           <div class="text-xs text-center text-[var(--win-text-muted)] uppercase tracking-widest mb-2">Writing To</div>
                           <div class="bg-black/40 border border-white/10 rounded-xl p-4 flex items-center justify-center gap-3 group hover:border-[var(--status-success)]/20 transition-colors">
                               <span class="font-mono text-xs md:text-sm text-[var(--status-success)] truncate max-w-[250px] md:max-w-none">{{ destinationPath }}</span>
                           </div>
                       </div>
                   </div>
               </div>

           </div>

           <!-- Action Footer -->
           <div class="p-6 bg-black/60 border-t border-white/10 flex justify-between items-center relative z-20">
              <button @click="step = 2" class="btn-ghost text-sm">
                 <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Change Destination
              </button>
              
              <button 
                 @click="startTransfer" 
                 class="btn-primary px-8 py-3 text-sm font-bold"
              >
                 <span class="flex items-center gap-2">
                    Start Copy Protocol <UIcon name="i-heroicons-rocket-launch" class="w-4 h-4" />
                 </span>
              </button>
           </div>
       </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import FileExplorer from '~/components/FileExplorer.vue'

definePageMeta({
  middleware: 'auth'
})

const { startCopy } = useApi()
const toast = useToast()

const step = ref(1)
const sourceSelection = ref<Set<string>>(new Set())
const destinationPath = ref('')

const sourceExplorer = ref<InstanceType<typeof FileExplorer> | null>(null)
const destinationExplorer = ref<InstanceType<typeof FileExplorer> | null>(null)

const updateSourceSelection = (selection: Set<string>) => {
    sourceSelection.value = selection
}

const canGoToStep = (target: number) => {
    if (target === 1) return true
    if (target === 2) return sourceSelection.value.size > 0
    if (target === 3) return sourceSelection.value.size > 0 && destinationPath.value
    return false
}

const goToReview = () => {
    // Capture current path from component ref
    if (destinationExplorer.value) {
        destinationPath.value = destinationExplorer.value.currentPath
    }
    step.value = 3
}

const startTransfer = async () => {
    const items = Array.from(sourceSelection.value)
    const dest = destinationPath.value
    
    let startedCount = 0
    let failCount = 0

    toast.add({ 
        title: 'Initiating Transfer...', 
        description: 'Please wait while jobs are queued', 
        color: 'blue' 
    })

    for (const src of items) {
       try {
           await startCopy(src, dest)
           startedCount++
       } catch (e) {
           console.error(e)
           failCount++
       }
   }
   
   if (startedCount > 0) {
       toast.add({ 
           title: 'Transfer Launched! 🚀', 
           description: `Successfully queued ${startedCount} items.`, 
           color: 'green' 
       })
       navigateTo('/queue')
   } else if (failCount > 0) {
       toast.add({ title: 'Error', description: 'Failed to start transfer jobs.', color: 'red' })
   }
}
</script>

<style scoped>
/* Steps Animation */
</style>
