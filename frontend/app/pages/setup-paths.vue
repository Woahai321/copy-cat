<template>
  <div class="min-h-screen flex items-center justify-center bg-[var(--win-bg-base)] relative overflow-hidden">
    <!-- Animated Background Lines -->
    <div class="app-background-lines">
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
       <div class="app-background-line"></div>
    </div>

    <!-- Container -->
    <div class="w-full max-w-5xl z-10 animate-fade-in-up flex flex-col items-center justify-center px-6 py-8">
      
      <!-- Progress Steps -->
      <div class="w-full max-w-xl mb-12 flex items-center justify-between relative px-4">
          <div class="absolute left-4 right-4 top-[20px] h-[1px] bg-white/5 -z-10"></div>
          
          <!-- Step 1: Enrich -->
          <div class="flex flex-col items-center gap-3 z-10">
              <div 
                class="w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-500 shadow-2xl relative group"
                :class="step >= 1 ? 'border-[var(--win-accent)]/50 bg-[var(--win-accent)]/10 text-[var(--win-accent)] shadow-[0_0_20px_rgba(96,205,255,0.2)]' : 'border-white/5 bg-white/5 text-gray-500'"
              >
                  <div v-if="step === 1" class="absolute -inset-1 bg-[var(--win-accent)]/20 blur-sm rounded-xl animate-pulse"></div>
                  <UIcon name="i-heroicons-sparkles" class="w-5 h-5 relative z-10" />
              </div>
              <span class="text-[9px] uppercase font-bold tracking-[0.2em]" :class="step === 1 ? 'text-[var(--win-accent)]' : 'text-gray-500'">Metadata</span>
          </div>

          <!-- Step 2: Movies -->
          <div class="flex flex-col items-center gap-3 z-10">
              <div 
                class="w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-500 shadow-2xl relative"
                :class="step >= 2 ? 'border-[var(--win-accent)]/50 bg-[var(--win-accent)]/10 text-[var(--win-accent)] shadow-[0_0_20px_rgba(96,205,255,0.2)]' : 'border-white/5 bg-white/5 text-gray-500'"
              >
                  <div v-if="step === 2" class="absolute -inset-1 bg-[var(--win-accent)]/20 blur-sm rounded-xl animate-pulse"></div>
                  <UIcon name="i-heroicons-film" class="w-5 h-5 relative z-10" />
              </div>
              <span class="text-[9px] uppercase font-bold tracking-[0.2em]" :class="step === 2 ? 'text-[var(--win-accent)]' : 'text-gray-500'">Movies</span>
          </div>

          <!-- Step 3: Series -->
          <div class="flex flex-col items-center gap-3 z-10">
              <div 
                class="w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-500 shadow-2xl relative"
                :class="step >= 3 ? 'border-[var(--win-accent)]/50 bg-[var(--win-accent)]/10 text-[var(--win-accent)] shadow-[0_0_20px_rgba(96,205,255,0.2)]' : 'border-white/5 bg-white/5 text-gray-500'"
              >
                  <div v-if="step === 3" class="absolute -inset-1 bg-[var(--win-accent)]/20 blur-sm rounded-xl animate-pulse"></div>
                  <UIcon name="i-heroicons-tv" class="w-5 h-5 relative z-10" />
              </div>
              <span class="text-[9px] uppercase font-bold tracking-[0.2em]" :class="step === 3 ? 'text-[var(--win-accent)]' : 'text-gray-500'">Series</span>
          </div>

          <!-- Step 4: Password -->
          <div class="flex flex-col items-center gap-3 z-10">
              <div 
                class="w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-500 shadow-2xl relative"
                :class="step >= 4 ? 'border-[var(--win-accent)]/50 bg-[var(--win-accent)]/10 text-[var(--win-accent)] shadow-[0_0_20px_rgba(96,205,255,0.2)]' : 'border-white/5 bg-white/5 text-gray-500'"
              >
                  <div v-if="step === 4" class="absolute -inset-1 bg-[var(--win-accent)]/20 blur-sm rounded-xl animate-pulse"></div>
                  <UIcon name="i-heroicons-shield-check" class="w-5 h-5 relative z-10" />
              </div>
              <span class="text-[9px] uppercase font-bold tracking-[0.2em]" :class="step === 4 ? 'text-[var(--win-accent)]' : 'text-gray-500'">Security</span>
          </div>
      </div>

      <!-- Main Content Card -->
      <div class="glass-panel w-full !rounded-[2rem] border-white/5 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col h-[70vh] backdrop-blur-3xl animate-fade-in">
          
          <!-- Header -->
          <div class="px-8 py-10 border-b border-white/5 bg-white/[0.02] flex-shrink-0 relative overflow-hidden">
              <div class="absolute top-0 right-0 w-64 h-64 bg-[var(--win-accent)]/5 blur-[80px] rounded-full -translate-y-1/2 translate-x-1/2"></div>
              
              <h1 class="text-3xl md:text-4xl font-bold text-white tracking-tight mb-3">
                  <span v-if="step === 1" class="bg-gradient-to-r from-[var(--brand-1)] to-[var(--brand-5)] bg-clip-text text-transparent">Automatic Metadata</span>
                  <span v-else-if="step === 2" class="bg-gradient-to-r from-[var(--brand-1)] to-[var(--brand-10)] bg-clip-text text-transparent">Movies Library</span>
                  <span v-else-if="step === 3" class="bg-gradient-to-r from-[var(--brand-5)] to-[var(--brand-10)] bg-clip-text text-transparent">TV Shows Library</span>
                  <span v-else class="bg-gradient-to-r from-[var(--brand-1)] to-[var(--brand-8)] bg-clip-text text-transparent">Security Setup</span>
              </h1>
              <p class="text-gray-400 text-sm max-w-xl font-light leading-relaxed">
                  <span v-if="step === 1">Linking your Trakt account allows us to automatically fetch posters, ratings, and detailed descriptions for your entire collection.</span>
                  <span v-else-if="step === 2">Tell us which folder on your local storage should be the destination for movie transfers.</span>
                  <span v-else-if="step === 3">Configure the default landing zone for TV series to keep your library organized.</span>
                  <span v-else>To keep your account secure, please update your temporary credentials to a personal password.</span>
              </p>
          </div>

          <!-- Content Area -->
          <div class="flex-1 relative overflow-hidden min-h-0">
             
             <!-- Step 1: Trakt -->
             <div v-if="step === 1" class="h-full flex flex-col items-center justify-center p-12 text-center">
                <div class="w-24 h-24 rounded-[2rem] bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center mb-10 border border-white/10 shadow-inner group">
                   <UIcon name="i-heroicons-sparkles" class="w-12 h-12 text-[var(--win-accent)] group-hover:scale-110 transition-transform duration-500" />
                </div>
                
                <div class="max-w-md w-full space-y-8">
                   <div class="relative group">
                      <div class="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                        <UIcon name="i-heroicons-key" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
                      </div>
                      <input 
                        v-model="traktKey"
                        type="password"
                        placeholder="Paste Trakt Client ID"
                        class="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-5 pl-14 pr-4 text-white outline-none focus:border-[var(--win-accent)]/50 focus:bg-white/[0.05] transition-all font-mono text-sm shadow-inner"
                      />
                   </div>

                   <p class="text-[11px] text-gray-500 uppercase tracking-widest font-bold">
                       Required for Posters & Metadata
                   </p>
                </div>
             </div>

             <!-- Step 2 & 3: Folders -->
             <FileExplorer
                v-else-if="step === 2 || step === 3"
                :key="`step-${step}`"
                source="16tb"
                :initialPath="initialPath"
                :selectable="true"
                @selection-change="onSelectionChange"
                class="h-full absolute inset-0"
             />

             <!-- Step 4: Password Change -->
             <div v-else class="h-full flex flex-col items-center justify-center p-12 text-center animate-fade-in">
                <div class="w-24 h-24 rounded-[2rem] bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center mb-10 border border-white/10 shadow-inner group">
                   <UIcon name="i-heroicons-shield-check" class="w-12 h-12 text-[var(--win-accent)] group-hover:scale-110 transition-transform duration-500" />
                </div>
                
                <div class="max-w-md w-full space-y-6">
                    <div class="relative group">
                      <div class="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                        <UIcon name="i-heroicons-lock-closed" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
                      </div>
                      <input 
                        v-model="pwdForm.new"
                        type="password"
                        placeholder="New Password"
                        class="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-5 pl-14 pr-4 text-white outline-none focus:border-[var(--win-accent)]/50 focus:bg-white/[0.05] transition-all text-sm shadow-inner"
                      />
                    </div>

                    <div class="relative group">
                      <div class="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                        <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
                      </div>
                      <input 
                        v-model="pwdForm.confirm"
                        type="password"
                        placeholder="Confirm New Password"
                        class="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-5 pl-14 pr-4 text-white outline-none focus:border-[var(--win-accent)]/50 focus:bg-white/[0.05] transition-all text-sm shadow-inner"
                      />
                    </div>

                    <p v-if="pwdForm.new && pwdForm.confirm && (pwdForm.new !== pwdForm.confirm)" class="text-[10px] text-red-500 uppercase tracking-widest font-bold animate-pulse">
                       Passwords do not match
                    </p>
                    <p v-else class="text-[10px] text-gray-500 uppercase tracking-widest font-bold">
                       Final Security Check
                    </p>
                </div>
             </div>

          </div>

          <!-- Footer Actions -->
          <div class="p-8 border-t border-white/5 bg-white/[0.02] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-6 flex-shrink-0 relative overflow-hidden">
              <div class="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[var(--win-accent)]/20 to-transparent"></div>
              
              <!-- Info / Selection -->
              <div class="flex-1 overflow-hidden">
                  <div v-if="step === 2 || step === 3" class="animate-fade-in">
                      <div class="text-[10px] text-gray-500 uppercase font-bold tracking-[0.2em] mb-1">Target Path</div>
                      <div class="font-mono text-sm text-[var(--win-accent)] truncate flex items-center gap-2">
                          <UIcon name="i-heroicons-folder-open" class="w-4 h-4" />
                          {{ selectedPath || 'Select a folder below' }}
                      </div>
                  </div>
                  <div v-else class="text-xs text-gray-400 font-light italic">
                      {{ step === 1 ? 'Tip: You can find your Trakt Client ID in your application settings.' : 'Tip: Use a strong, unique password for your account security.' }}
                  </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center gap-4">
                  <button 
                    v-if="step < 4"
                    @click="skipStep"
                    class="px-6 py-3.5 rounded-2xl text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-white hover:bg-white/5 transition-all"
                    :disabled="loading"
                  >
                    {{ step === 1 ? 'Skip' : 'Skip Step' }}
                  </button>
                  <button 
                    @click="handleNext"
                    :disabled="loading || ( (step === 2 || step === 3) && !selectedPath ) || (step === 4 && (!pwdForm.new || pwdForm.new !== pwdForm.confirm))"
                    class="min-w-[160px] bg-white text-black hover:bg-white/90 disabled:bg-white/20 disabled:text-black/50 disabled:cursor-not-allowed rounded-2xl py-4 px-6 text-xs font-bold uppercase tracking-widest transition-all shadow-[0_10px_20px_-5px_rgba(255,255,255,0.1)] flex items-center justify-center gap-3 active:scale-95"
                  >
                    <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                    <span>{{ step < 4 ? 'Continue' : 'Complete Setup' }}</span>
                    <UIcon v-if="!loading" :name="step < 4 ? 'i-heroicons-arrow-right' : 'i-heroicons-check-badge'" class="w-4 h-4" />
                  </button>
              </div>
          </div>

      </div>

      <!-- Help Link -->
      <div class="text-center mt-10">
        <p class="text-[10px] uppercase tracking-[0.2em] text-gray-600">
            CopyCat &copy; 2025 &bull; <a href="#" class="text-gray-400 hover:text-[var(--win-accent)] transition-colors">Documentation</a>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
  middleware: 'auth'
})

const { updateSettings, changePassword, validateSettings } = useApi()
const router = useRouter()
const toast = useToast()
const auth = useAuth()

const step = ref(1)
const loading = ref(false)

// Data
const traktKey = ref('')
const moviePath = ref('')
const seriesPath = ref('')
const selectedPath = ref('')
const initialPath = ref('/')

const pwdForm = reactive({
    new: '',
    confirm: ''
})

const onSelectionChange = (files: Set<string>) => {
    if (files.size > 0) {
        selectedPath.value = Array.from(files).pop() || ''
    } else {
        selectedPath.value = ''
    }
}

const skipStep = () => {
    if (step.value === 1) {
        step.value = 2
        selectedPath.value = ''
        initialPath.value = '/'
    } else if (step.value === 2) {
        step.value = 3
        selectedPath.value = ''
        initialPath.value = '/'
    } else if (step.value === 3) {
        step.value = 4
    }
}

const handleNext = async () => {
    if (step.value === 1) {
        // Step 1: Metadata - Validate and Save immediately to start fetching
        if (traktKey.value) {
            loading.value = true
            try {
                // Validate Trakt Key
                await validateSettings({ trakt_client_id: traktKey.value })
                
                // Save it immediately to trigger background enrichment
                await updateSettings({ trakt_client_id: traktKey.value })
                
                toast.add({
                    title: 'Trakt Configured',
                    description: 'Metadata fetching has started in the background.',
                    color: 'green'
                })
            } catch (e: any) {
                toast.add({
                    title: 'Invalid Trakt ID',
                    description: e.data?.detail || 'Please check your Client ID and try again.',
                    color: 'red'
                })
                loading.value = false
                return
            } finally {
                loading.value = false
            }
        }
        
        step.value = 2
        selectedPath.value = ''
        initialPath.value = '/'
    } else if (step.value === 2) {
        // Step 2: Movies
        if (!selectedPath.value) return
        moviePath.value = selectedPath.value
        step.value = 3
        selectedPath.value = ''
        initialPath.value = '/'
    } else if (step.value === 3) {
        // Step 3: Series
        if (!selectedPath.value) return
        seriesPath.value = selectedPath.value
        step.value = 4
    } else if (step.value === 4) {
        // Step 4: Finish (Password + Settings)
        await finishSetup()
    }
}

const finishSetup = async () => {
    loading.value = true
    try {
        // 1. Update Core Settings
        await updateSettings({
            default_movies_path: moviePath.value || undefined,
            default_series_path: seriesPath.value || undefined,
            trakt_client_id: traktKey.value || undefined
        })

        // 2. Change Password (if provided)
        if (pwdForm.new && pwdForm.new === pwdForm.confirm) {
            // We use 'changeme' as the current password because this flow is for first-run
            // or we could ask for it, but user said "reset the default pw"
            try {
                await changePassword('changeme', pwdForm.new)
                // Refresh auth state to clear require_password_change
                if (auth.user.value) {
                    auth.user.value.require_password_change = false
                }
            } catch (pE) {
                console.error("Failed to change password (maybe it was already changed)", pE)
            }
        }

        toast.add({
            title: 'Welcome to CopyCat!',
            description: 'Your setup is complete. Starting scanning in the background.',
            color: 'green'
        })
        
        router.push('/')
    } catch (e: any) {
        console.error("Setup Completion error:", e)
        toast.add({
            title: 'Setup Error',
            description: e.message || 'Something went wrong during setup.',
            color: 'red'
        })
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.6s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-in {
  animation: fade-in 0.4s ease-out;
}
</style>
