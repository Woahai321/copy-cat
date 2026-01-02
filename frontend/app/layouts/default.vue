<template>
  <div class="min-h-screen flex text-white relative">
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

    <!-- Sidebar -->
    <aside 
      class="sidebar" 
      :class="{ 'sidebar-open': sidebarOpen, 'sidebar-closed': !sidebarOpen }"
    >
      <div class="flex flex-col h-full">
        
        <!-- Logo/Brand & Sidebar Toggle -->
        <div class="p-6 pb-2 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 flex items-center justify-center bg-transparent rounded-xl flex-shrink-0">
                    <img src="/copycat.webp" alt="CopyCat Logo" class="w-full h-full object-contain drop-shadow-[0_0_8px_rgba(96,205,255,0.6)]" />
                </div>
                <div>
                   <h1 class="text-base font-bold text-[var(--win-text-primary)] leading-tight tracking-wide">Copy<span class="text-[var(--brand-1)]">Cat</span></h1>
                   <p class="text-[10px] uppercase tracking-wider text-[var(--win-text-muted)] font-semibold">System v0.0.1</p>
                </div>
            </div>
            <!-- Close Toggle (Desktop/Mobile) -->
             <button
              @click="sidebarOpen = !sidebarOpen"
              class="text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] transition-colors p-1"
              :aria-label="sidebarOpen ? 'Close menu' : 'Open menu'"
            >
              <UIcon name="i-heroicons-chevron-double-left" class="w-5 h-5" />
            </button>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 py-4 overflow-y-auto space-y-1 px-3 custom-scrollbar">
          <NuxtLink
            to="/"
            class="sidebar-nav-item"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <UIcon name="i-heroicons-squares-2x2" class="w-5 h-5 flex-shrink-0" />
            <span class="truncate">Dashboard</span>
          </NuxtLink>

          <!-- Queue -->
          <NuxtLink
            to="/queue"
            class="sidebar-nav-item"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <UIcon name="i-heroicons-queue-list" class="w-5 h-5 flex-shrink-0" />
            <span class="truncate">Queue</span>
            <span v-if="activeJobsCount > 0" class="ml-auto bg-[var(--win-accent)] text-black text-[10px] font-bold px-2 py-0.5 rounded-full shadow-[0_0_10px_rgba(96,205,255,0.4)]">
              {{ activeJobsCount }}
            </span>
          </NuxtLink>

          <!-- Library Group -->
          <div class="space-y-1">
             <button 
               @click="libraryMenuOpen = !libraryMenuOpen"
               class="sidebar-nav-item w-full justify-between group"
               :class="{ 'text-[var(--win-text-primary)]': libraryMenuOpen }"
             >
               <div class="flex items-center gap-3">
                 <UIcon name="i-heroicons-building-library" class="w-5 h-5 flex-shrink-0" />
                 <span class="truncate">Library</span>
               </div>
               <UIcon 
                 name="i-heroicons-chevron-right" 
                 class="w-4 h-4 transition-transform duration-200"
                 :class="{ 'rotate-90': libraryMenuOpen }"
               />
             </button>
             
             <!-- Dropdown Items -->
             <div v-show="libraryMenuOpen" class="space-y-0.5 animate-in slide-in-from-top-2 duration-200">
               <NuxtLink
                 to="/library"
                 class="sidebar-nav-item !pl-11 !py-2 !text-xs"
                 active-class="active"
                 @click="closeSidebarOnMobile"
               >
                 <UIcon name="i-heroicons-film" class="w-4 h-4 flex-shrink-0 opacity-70" />
                 <span class="truncate">Media Library</span>
               </NuxtLink>
               <NuxtLink
                 to="/copy-wizard"
                 class="sidebar-nav-item !pl-11 !py-2 !text-xs"
                 active-class="active"
                 @click="closeSidebarOnMobile"
               >
                 <UIcon name="i-heroicons-sparkles" class="w-4 h-4 flex-shrink-0 opacity-70" />
                 <span class="truncate">Copy Wizard</span>
               </NuxtLink>
               <NuxtLink
                 to="/browse"
                 class="sidebar-nav-item !pl-11 !py-2 !text-xs"
                 active-class="active"
                 @click="closeSidebarOnMobile"
               >
                 <UIcon name="i-heroicons-folder-open" class="w-4 h-4 flex-shrink-0 opacity-70" />
                 <span class="truncate">File Explorer</span>
               </NuxtLink>
             </div>
          </div>

          <!-- Analytics Group -->
          <div class="space-y-1">
            <button 
               @click="analyticsMenuOpen = !analyticsMenuOpen"
               class="sidebar-nav-item w-full justify-between group"
               :class="{ 'text-[var(--win-text-primary)]': analyticsMenuOpen }"
             >
               <div class="flex items-center gap-3">
                 <UIcon name="i-heroicons-chart-bar" class="w-5 h-5 flex-shrink-0" />
                 <span class="truncate">Analytics</span>
               </div>
               <UIcon 
                 name="i-heroicons-chevron-right" 
                 class="w-4 h-4 transition-transform duration-200"
                 :class="{ 'rotate-90': analyticsMenuOpen }"
               />
             </button>
             
             <!-- Dropdown Items -->
             <div v-show="analyticsMenuOpen" class="space-y-0.5 animate-in slide-in-from-top-2 duration-200">
               <NuxtLink
                to="/stats"
                class="sidebar-nav-item !pl-11 !py-2 !text-xs"
                active-class="active"
                @click="closeSidebarOnMobile"
              >
                <UIcon name="i-heroicons-chart-pie" class="w-4 h-4 flex-shrink-0 opacity-70" />
                <span class="truncate">Statistics</span>
              </NuxtLink>
              <NuxtLink
                to="/history"
                class="sidebar-nav-item !pl-11 !py-2 !text-xs"
                active-class="active"
                @click="closeSidebarOnMobile"
              >
                <UIcon name="i-heroicons-clock" class="w-4 h-4 flex-shrink-0 opacity-70" />
                <span class="truncate">History</span>
              </NuxtLink>
             </div>
          </div>
          

          <NuxtLink
            to="/settings"
            class="sidebar-nav-item"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 flex-shrink-0" />
            <span class="truncate">Settings</span>
          </NuxtLink>
        </nav>

        <!-- User section -->
        <div class="px-4 py-4 border-t border-white/5 bg-[var(--glass-level-2-bg)] backdrop-blur-sm">
          <div class="flex items-center gap-3 mb-3 px-1">
            <div class="w-9 h-9 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center flex-shrink-0 border border-white/10 shadow-lg">
              <UIcon name="i-heroicons-user" class="w-4 h-4 text-gray-300" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-[var(--win-text-primary)] truncate">{{ currentUser?.username || 'User' }}</p>
              <div class="flex items-center gap-1.5">
                  <div class="w-1.5 h-1.5 rounded-full bg-[var(--status-success)] shadow-[0_0_5px_rgba(16,185,129,0.5)]"></div>
                  <p class="text-xs text-[var(--win-text-muted)]">Online</p>
              </div>
            </div>
          </div>
          <button
            @click="handleLogout"
            class="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-white/5 border border-transparent hover:border-white/5 rounded-lg transition-all"
          >
            <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-4 h-4" />
            <span>Sign out</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Overlay (click to close sidebar) -->
    <div
      v-if="sidebarOpen"
      @click="sidebarOpen = false"
      class="sidebar-overlay"
    ></div>

    <!-- Main content -->
    <main 
      class="main-content" 
      :class="{ 'main-with-sidebar': sidebarOpen, 'main-full': !sidebarOpen }"
    >
      <!-- Closed Sidebar Toggle (Only visible when sidebar is closed) -->
      <button
          v-if="!sidebarOpen"
          @click="sidebarOpen = true"
          class="fixed top-4 left-4 z-50 p-2 bg-[var(--glass-level-3-bg)] backdrop-blur-md border border-white/10 rounded-lg text-white shadow-lg hover:bg-[var(--glass-level-4-bg)] transition-colors"
          aria-label="Open menu"
        >
          <UIcon name="i-heroicons-bars-3" class="w-6 h-6" />
        </button>

      <!-- Global System Warning -->
      <div v-if="systemWarning" class="mx-4 mt-4 bg-[var(--brand-1)]/10 border border-[var(--brand-1)]/20 rounded-xl px-4 py-3 backdrop-blur-sm">
           <div class="flex items-start gap-3">
           <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-[var(--brand-1)] flex-shrink-0" />
           <div>
             <h3 class="text-sm font-bold text-[var(--win-text-primary)]">System Configuration Issue</h3>
             <p class="text-xs text-[var(--brand-1)]/70">{{ systemWarning }}</p>
           </div>
        </div>
      </div>

      <div class="container mx-auto px-6 py-8 max-w-[1600px] animate-in">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const { logout } = useAuth()
const { getQueue, getSystemStatus, getUserInfo } = useApi()

// Spotlight Effect: Global Mouse Tracking
if (process.client) {
  useEventListener(window, 'mousemove', (e) => {
    const x = e.clientX
    const y = e.clientY
    document.body.style.setProperty('--mouse-x', `${x}px`)
    document.body.style.setProperty('--mouse-y', `${y}px`)
  })
}

// Persist sidebar state
const sidebarOpen = useState('sidebarOpen', () => true) 
const libraryMenuOpen = useState('libraryMenuOpen', () => true)
const analyticsMenuOpen = useState('analyticsMenuOpen', () => true)
const activeJobsCount = ref(0)
const systemWarning = ref<string | null>(null)
const currentUser = ref<any>(null)

const handleLogout = () => {
  logout()
  navigateTo('/login')
}


const checkSystemStatus = async () => {
    try {
        const status = await getSystemStatus()
        if (!status) {
            systemWarning.value = null
            return
        }
        const zurgHasContents = status.zurg?.contents_preview && status.zurg.contents_preview.length > 0;
        const hdHasContents = status.harddrive?.contents_preview && status.harddrive.contents_preview.length > 0;
        
        const zurgIssue = !status.zurg?.exists || (!zurgHasContents && status.zurg?.empty);
        const hdIssue = !status.harddrive?.exists;
        
        if (zurgIssue && hdIssue) {
            if (!status.zurg?.exists) systemWarning.value = "Source (Zurg) and Destination (16TB) unmounted.";
            else systemWarning.value = null; 
        } else if (zurgIssue) {
             if (!status.zurg?.exists) systemWarning.value = "Source (Zurg) path not found.";
             else systemWarning.value = null;
        } else if (hdIssue) {
            systemWarning.value = "Destination (16TB) path not found.";
        } else {
            systemWarning.value = null
        }
    } catch (e) {
        console.error("Status check failed", e)
        systemWarning.value = null
    }
}

const loadActiveJobsCount = async () => {
  try {
    const queue = await getQueue()
    activeJobsCount.value = queue.length
  } catch (error) {
    console.error("Failed to load active jobs count:", error)
  }
}

const checkMobile = () => {
  if (typeof window !== 'undefined' && window.innerWidth < 768) {
    sidebarOpen.value = false
  } else {
    sidebarOpen.value = true
  }
}

onMounted(async () => {
  loadActiveJobsCount()
  checkMobile() 
  window.addEventListener('resize', checkMobile)
  
  if (window.innerWidth >= 768) {
    sidebarOpen.value = true
  }
  
  try {
    currentUser.value = await getUserInfo()
    checkSystemStatus()
  } catch (e) {
    // Not logged in
  }
})

onUnmounted(() => {
    if (typeof window !== 'undefined') window.removeEventListener('resize', checkMobile)
})

useIntervalFn(() => {
  loadActiveJobsCount()
}, 10000)

const route = useRoute()
watch(() => route.path, () => {
   if (typeof window !== 'undefined' && window.innerWidth < 768) {
      sidebarOpen.value = false
   }
   if (currentUser.value) {
       checkSystemStatus()
   }
})
</script>

<style scoped>
.hamburger-toggle {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-level-2-bg);
  border: 1px solid var(--glass-level-2-border);
  color: white;
  transition: all 0.2s ease;
}

.hamburger-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Sidebar styling using new Global Variables */
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 260px;
  z-index: 60;
  transition: transform 0.3s cubic-bezier(0.2, 0, 0, 1);
  background: var(--glass-level-1-bg);
  backdrop-filter: blur(var(--glass-level-1-blur));
  -webkit-backdrop-filter: blur(var(--glass-level-1-blur));
  border-right: 1px solid var(--glass-level-1-border);
  box-shadow: 4px 0 30px rgba(0,0,0,0.3);
}

.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    margin: 4px 12px;
    border-radius: 8px;
    color: var(--win-text-secondary);
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    position: relative;
}

.sidebar-nav-item:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: white;
}

.sidebar-nav-item.active {
    background: linear-gradient(90deg, color-mix(in srgb, var(--win-accent), transparent 90%) 0%, transparent 100%);
    color: white;
    font-weight: 600;
    border: 1px solid color-mix(in srgb, var(--win-accent), transparent 90%);
}

/* Active Pill Indicator */
.sidebar-nav-item.active::before {
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 16px;
    background: var(--win-accent);
    border-radius: 0 4px 4px 0;
    box-shadow: 0 0 10px var(--win-accent);
}

@media (max-width: 767px) {
  .sidebar {
    width: 280px;
    background: var(--win-bg-base); /* Solid on mobile for perf */
  }
   .hamburger-toggle {
    display: flex; /* Show on mobile */
  }
}

.sidebar-closed {
  transform: translateX(-100%);
}

.sidebar-open {
  transform: translateX(0);
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 30;
  display: none; /* Hidden by default */
}

@media (max-width: 767px) {
  .sidebar-overlay {
    display: block; /* Show only on mobile when needed */
  }
}

.main-content {
  flex: 1;
  min-height: 100vh;
  transition: margin-left 0.2s cubic-bezier(0.2, 0, 0, 1);
  width: 100%;
  position: relative;
  z-index: 2; /* Content above background */
}

.main-full {
  margin-left: 0;
}

.main-with-sidebar {
  margin-left: 260px;
}

@media (max-width: 768px) {
  .main-with-sidebar {
    margin-left: 0;
  }
  .main-content {
    padding-top: 50px; 
  }
}

.touch-target {
  min-height: 44px;
  min-width: 44px;
}
</style>
