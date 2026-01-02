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

    <div class="w-full max-w-md z-10 animate-fade-in-up px-6">
      <!-- Glass Card Container -->
      <div class="bg-[var(--glass-level-4-bg)] backdrop-blur-2xl rounded-3xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.4)] p-8 md:p-10">
        
        <!-- Icon & Header -->
        <div class="flex flex-col items-center mb-8">
          <div class="relative mb-6">
            <div class="absolute inset-0 bg-gradient-to-br from-[var(--brand-10)] to-[var(--brand-1)] rounded-3xl blur-2xl opacity-40 animate-pulse-slow"></div>
            <div class="relative w-24 h-24 rounded-3xl bg-gradient-to-br from-[var(--brand-1)]/20 to-[var(--brand-5)]/20 flex items-center justify-center border border-[var(--brand-1)]/30 shadow-2xl">
               <UIcon name="i-heroicons-key" class="w-12 h-12 text-[var(--win-accent)]" />
            </div>
          </div>
          
          <h1 class="text-3xl font-bold bg-gradient-to-r from-white via-[var(--brand-1)] to-[var(--brand-10)] bg-clip-text text-transparent mb-2">
            Connect Trakt
          </h1>
          <p class="text-sm text-[var(--win-text-muted)] text-center max-w-sm">
            To enable metadata and images, we need your Trakt Client ID.
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-6 p-4 bg-[var(--status-error)]/10 border border-[var(--status-error)]/30 rounded-xl backdrop-blur-sm">
          <div class="flex items-center gap-3 text-[var(--status-error)]">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 flex-shrink-0" />
            <span class="text-sm">{{ error }}</span>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <!-- Trakt Client ID Input -->
          <div v-if="step === 'input'" class="relative group">
            <label class="text-xs text-[var(--win-text-muted)] uppercase font-bold mb-2 block">Trakt Client ID</label>
            <div class="absolute bottom-0 left-0 pl-4 flex items-center pointer-events-none" style="bottom: 14px;">
              <UIcon name="i-heroicons-identification" class="w-5 h-5 text-[var(--win-text-muted)] group-focus-within:text-[var(--brand-1)] transition-colors" />
            </div>
            <input
                v-model="traktClientId"
                type="password"
                required
                placeholder="Enter your Client ID here..."
                class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 focus:border-[var(--brand-1)]/50 text-[var(--win-text-primary)] pl-12 pr-4 py-3.5 rounded-xl outline-none transition-all placeholder-[var(--win-text-muted)] focus:bg-[var(--glass-level-3-bg)] focus:shadow-[0_0_20px_rgba(96,205,255,0.15)] font-mono text-sm"
            />
            <p class="text-xs text-[var(--win-text-muted)] mt-2 ml-1">
                Found in your Trakt API App settings
            </p>
          </div>

          <!-- Submit Button -->
          <button
              v-if="step === 'input'"
              type="button"
              @click.prevent="handleSubmit"
              class="w-full bg-[var(--win-accent)] hover:bg-[var(--win-accent)]/80 text-black font-bold py-4 rounded-xl shadow-[0_0_20px_rgba(96,205,255,0.3)] transition-all duration-300 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed mt-2"
              :disabled="loading"
          >
            <span v-if="!loading" class="flex items-center justify-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="w-5 h-5" />
              <span>Validate & Start Setup</span>
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
              <span>Validating & Starting Scan...</span>
            </span>
          </button>

          <!-- Success State -->
          <div v-else class="text-center animate-fade-in-up">
            <div class="mb-6 p-6 bg-[var(--status-success)]/10 border border-[var(--status-success)]/30 rounded-xl backdrop-blur-sm">
              <UIcon name="i-heroicons-check-circle" class="w-16 h-16 text-[var(--status-success)] mx-auto mb-3" />
              <h3 class="text-[var(--status-success)] font-bold text-lg mb-2">Trakt Connected!</h3>
              <p class="text-sm text-[var(--win-text-muted)]">Scan started in background.</p>
            </div>
            
            <p class="text-white font-semibold flex items-center justify-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <span>Redirecting to path setup...</span>
            </p>
          </div>

        </form>

        <!-- Help Link -->
        <div class="text-center mt-8 pt-6 border-t border-white/5">
           <a href="https://trakt.tv/oauth/applications" target="_blank" class="text-xs text-[var(--win-text-muted)] hover:text-[var(--brand-1)] transition-colors inline-flex items-center gap-1">
             <UIcon name="i-heroicons-question-mark-circle" class="w-3.5 h-3.5" />
             <span>Get your Trakt API key</span>
           </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false
})

const traktClientId = ref('')
const loading = ref(false)
const error = ref('')
const step = ref<'input' | 'success'>('input')

const { token } = useAuth()
const config = useRuntimeConfig()

const handleSubmit = async () => {
    if (!traktClientId.value.trim()) {
        error.value = "Please enter a Trakt Client ID"
        return
    }
    
    loading.value = true
    error.value = ''
    
    try {
        // Save settings
        await $fetch(`${config.public.apiBase}/api/settings`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token.value}`,
                'Content-Type': 'application/json'
            },
            body: {
                trakt_client_id: traktClientId.value
            }
        })
        
        // Trigger scan
        await $fetch(`${config.public.apiBase}/api/library/scan`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token.value}`
            }
        })
        
        // Show success
        step.value = 'success'
        
        // Redirect after delay
        setTimeout(() => {
            navigateTo('/setup-paths')
        }, 2000)
        
    } catch (e: any) {
        error.value = e.data?.detail || 'Failed to save Trakt settings'
        loading.value = false
    }
}
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse-slow {
  animation: pulse-slow 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

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
</style>
