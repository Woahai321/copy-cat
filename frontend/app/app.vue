<template>
  <div>
    <UNotifications />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>

    <!-- PWA Install Prompt (Mobile Only, Top Aligned) -->
    <Transition name="slide-down">
      <div 
        v-if="showInstallPrompt && !dismissed" 
        class="fixed top-4 left-4 right-4 z-[100] glass-panel p-4 rounded-2xl border border-white/10 shadow-2xl lg:hidden"
      >
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 rounded-xl bg-[var(--win-accent)]/10 border border-[var(--win-accent)]/20 flex items-center justify-center flex-shrink-0">
            <img src="/copycat.webp" alt="CopyCat" class="w-8 h-8 rounded" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-sm font-bold text-[var(--win-text-primary)]">Install CopyCat</h3>
            <p class="text-xs text-[var(--win-text-muted)] mt-0.5">Add to your home screen for quick access</p>>
          </div>
          <button @click="dismissed = true" class="text-gray-500 hover:text-white p-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex gap-2 mt-4">
          <button 
            @click="dismissed = true" 
            class="flex-1 py-2.5 text-xs font-bold text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] transition-colors rounded-xl border border-white/10 hover:bg-[var(--glass-level-1-bg)]"
          >
            Not Now
          </button>
          <button 
            @click="installApp" 
            class="flex-1 py-2.5 text-xs font-bold bg-[var(--win-accent)] text-black rounded-xl hover:bg-white transition-colors flex items-center justify-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Install
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
// PWA Install Prompt
const deferredPrompt = ref<any>(null)
const showInstallPrompt = ref(false)
const dismissed = ref(false)

onMounted(() => {
  // Initialize Theme
  const { initTheme } = useTheme()
  initTheme()

  // Register service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').then((registration) => {
      console.log('SW registered:', registration.scope)
    }).catch((error) => {
      console.log('SW registration failed:', error)
    })
  }

  // Check if already dismissed in this session
  if (sessionStorage.getItem('pwa-dismissed')) {
    dismissed.value = true
  }

  // Listen for the beforeinstallprompt event
  window.addEventListener('beforeinstallprompt', (e: Event) => {
    e.preventDefault()
    deferredPrompt.value = e
    showInstallPrompt.value = true
  })

  // Listen for app installed event
  window.addEventListener('appinstalled', () => {
    showInstallPrompt.value = false
    deferredPrompt.value = null
  })
})

const installApp = async () => {
  if (!deferredPrompt.value) return

  deferredPrompt.value.prompt()
  const { outcome } = await deferredPrompt.value.userChoice
  
  if (outcome === 'accepted') {
    showInstallPrompt.value = false
  }
  
  deferredPrompt.value = null
}

watch(dismissed, (val) => {
  if (val) {
    sessionStorage.setItem('pwa-dismissed', 'true')
  }
})
</script>

<style>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
