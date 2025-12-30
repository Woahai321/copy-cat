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
        
        <!-- Icon & Header -->
        <div class="flex flex-col items-center mb-8">
          <div class="relative mb-6">
            <div class="absolute inset-0 bg-gradient-to-br from-[var(--brand-10)] to-[var(--brand-1)] rounded-3xl blur-2xl opacity-40 animate-pulse-slow"></div>
            <div class="relative w-24 h-24 rounded-3xl bg-gradient-to-br from-[var(--brand-1)]/20 to-[var(--brand-5)]/20 flex items-center justify-center border border-[var(--brand-1)]/30 shadow-2xl">
               <UIcon name="i-heroicons-shield-exclamation" class="w-12 h-12 text-[var(--brand-1)]" />
            </div>
          </div>
          
          <h1 class="text-3xl font-bold bg-gradient-to-r from-white via-[var(--brand-1)] to-[var(--brand-5)] bg-clip-text text-transparent mb-2">
            Change Password
          </h1>
          <p class="text-sm text-gray-400 text-center max-w-sm">
            For your security, you must change your password before proceeding.
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl backdrop-blur-sm">
          <div class="flex items-center gap-3 text-red-300">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 flex-shrink-0" />
            <span class="text-sm">{{ error }}</span>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <!-- Current Password -->
          <div class="relative group">
            <label class="text-xs text-gray-400 uppercase font-bold mb-2 block">Current Password</label>
            <div class="absolute bottom-0 left-0 pl-4 flex items-center pointer-events-none" style="bottom: 14px;">
              <UIcon name="i-heroicons-lock-closed" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
            </div>
            <input
                v-model="currentPassword"
                type="password"
                required
                class="w-full bg-black/20 border border-white/10 focus:border-[var(--win-accent)]/50 text-white pl-12 pr-4 py-3.5 rounded-xl outline-none transition-all placeholder-gray-500 focus:bg-black/30 focus:shadow-[0_0_20px_rgba(96,205,255,0.15)]"
                placeholder="Enter current password"
            />
          </div>

          <!-- New Password -->
          <div class="relative group">
            <label class="text-xs text-gray-400 uppercase font-bold mb-2 block">New Password</label>
            <div class="absolute bottom-0 left-0 pl-4 flex items-center pointer-events-none" style="bottom: 14px;">
              <UIcon name="i-heroicons-key" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
            </div>
            <input
                v-model="newPassword"
                type="password"
                required
                class="w-full bg-black/20 border border-white/10 focus:border-[var(--win-accent)]/50 text-white pl-12 pr-4 py-3.5 rounded-xl outline-none transition-all placeholder-gray-500 focus:bg-black/30 focus:shadow-[0_0_20px_rgba(96,205,255,0.15)]"
                placeholder="Enter new password"
            />
          </div>

          <!-- Confirm Password -->
          <div class="relative group">
            <label class="text-xs text-gray-400 uppercase font-bold mb-2 block">Confirm New Password</label>
            <div class="absolute bottom-0 left-0 pl-4 flex items-center pointer-events-none" style="bottom: 14px;">
              <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
            </div>
            <input
                v-model="confirmPassword"
                type="password"
                required
                class="w-full bg-black/20 border border-white/10 focus:border-[var(--win-accent)]/50 text-white pl-12 pr-4 py-3.5 rounded-xl outline-none transition-all placeholder-gray-500 focus:bg-black/30 focus:shadow-[0_0_20px_rgba(96,205,255,0.15)]"
                placeholder="Confirm new password"
            />
          </div>

          <!-- Submit Button -->
          <button
              type="submit"
              class="btn-primary w-full py-4 text-base shadow-[0_0_20px_rgba(96,205,255,0.3)] mt-2"
              :disabled="loading"
          >
            <span v-if="!loading" class="flex items-center justify-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5" />
              <span>Update Password</span>
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
              <span>Updating...</span>
            </span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false
})

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

const { token } = useAuth()
const config = useRuntimeConfig()

const handleSubmit = async () => {
    if (newPassword.value !== confirmPassword.value) {
        error.value = "Passwords do not match"
        return
    }
    
    loading.value = true
    error.value = ''
    
    try {
        const res = await $fetch(`${config.public.apiBase}/api/users/change-password`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token.value}`,
                'Content-Type': 'application/json'
            },
            body: {
                current_password: currentPassword.value,
                new_password: newPassword.value
            }
        })
        
        // Success: Check if paths are configured before going to dashboard
        try {
            const { getSettings } = useApi()
            const settings = await getSettings()
            
            if (!settings.default_movies_path || !settings.default_series_path || !settings.trakt_configured) {
                navigateTo('/setup-paths')
            } else {
                navigateTo('/')
            }
        } catch (e) {
            console.error("Failed to check settings after password change", e)
            navigateTo('/')
        }
    } catch (e: any) {
        error.value = e.data?.detail || 'Failed to update password'
    } finally {
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
