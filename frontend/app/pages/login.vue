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
      <div class="glass-panel p-8 md:p-10 !rounded-3xl !border-white/10">
        
        <!-- Logo & Branding -->
        <div class="flex flex-col items-center mb-8">
          <div class="relative mb-6">
            <!-- Glow effect behind logo -->
            <div class="absolute inset-0 bg-gradient-to-br from-[var(--brand-10)] to-[var(--brand-1)] rounded-3xl blur-2xl opacity-40 animate-pulse-slow"></div>
            <!-- Logo -->
            <div class="relative w-40 h-40 rounded-3xl bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] flex items-center justify-center border border-white/10 shadow-2xl p-6">
               <img src="/copycat.webp" alt="CopyCat Logo" class="w-full h-full object-contain drop-shadow-[0_0_15px_rgba(96,205,255,0.6)]" />
            </div>
          </div>
          
          <h1 class="text-3xl font-bold bg-gradient-to-r from-white via-[var(--brand-1)] to-[var(--brand-5)] bg-clip-text text-transparent mb-2">
            Welcome Back
          </h1>
          <div class="flex items-center gap-2 mb-8">
            <span class="font-semibold text-white">Copy<span class="text-[var(--brand-1)]">Cat</span></span>
            <span class="text-[10px] text-[var(--brand-1)]/60 font-mono">v0.0.1</span>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl backdrop-blur-sm">
          <div class="flex items-center gap-3 text-red-300">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 flex-shrink-0" />
            <span class="text-sm">{{ error }}</span>
          </div>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Username Field -->
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <UIcon name="i-heroicons-user" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
            </div>
            <input
              id="username"
              v-model="username"
              type="text"
              placeholder="Username"
              required
              class="w-full bg-black/20 border border-white/10 focus:border-[var(--win-accent)]/50 text-white pl-12 pr-4 py-3.5 rounded-xl outline-none transition-all placeholder-gray-500 focus:bg-black/30 focus:shadow-[0_0_20px_rgba(96,205,255,0.15)]"
              :disabled="loading"
            />
          </div>

          <!-- Password Field -->
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <UIcon name="i-heroicons-lock-closed" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
            </div>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="Password"
              required
              class="w-full bg-black/20 border border-white/10 focus:border-[var(--win-accent)]/50 text-white pl-12 pr-4 py-3.5 rounded-xl outline-none transition-all placeholder-gray-500 focus:bg-black/30 focus:shadow-[0_0_20px_rgba(96,205,255,0.15)]"
              :disabled="loading"
            />
          </div>

          <!-- Sign In Button -->
          <button
            type="submit"
            class="btn-primary w-full py-4 text-base shadow-[0_0_20px_rgba(96,205,255,0.3)] mt-2"
            :disabled="loading"
          >
            <span v-if="!loading" class="flex items-center justify-center gap-2">
              <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-5 h-5" />
              <span>Sign In</span>
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
              <span>Verifying...</span>
            </span>
          </button>
        </form>

        <!-- Footer Link -->
        <div class="text-center mt-8 pt-6 border-t border-white/5">
           <a href="#" class="text-xs text-gray-500 hover:text-[var(--win-accent)] transition-colors inline-flex items-center gap-1">
             <UIcon name="i-heroicons-question-mark-circle" class="w-3.5 h-3.5" />
             <span>Forgot your password?</span>
           </a>
        </div>
      </div>

      <!-- Version Badge -->
      <div class="text-center mt-6 text-xs text-gray-600">
        <p>CopyCat Media Manager</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false
})

const { login, user } = useAuth()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const res = await login(username.value, password.value)
    
    if (res) {
        if (user.value) {
            // Check if ANY setup is needed
            const { getSettingsStatus } = useApi()
            let status: any = { movies_configured: false, series_configured: false, has_trakt_key: false }
            
            try {
                status = await getSettingsStatus()
            } catch (se) {
                console.error("Failed to fetch settings status on login", se)
            }

            const needsSetup = user.value.require_password_change || 
                               !status.movies_configured || 
                               !status.series_configured ||
                               !status.has_trakt_key

            if (needsSetup) {
                navigateTo('/setup-paths')
            } else {
                navigateTo('/')
            }
        }
    } else {
        error.value = 'Invalid username or password'
    }
  } catch (e: any) {
    error.value = e.message || 'Login failed'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  document.getElementById('username')?.focus()
})
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

/* Enhance fade-in animation */
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
