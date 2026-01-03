<template>
  <div class="h-full flex flex-col p-6 space-y-8 max-w-7xl mx-auto w-full animate-fade-in text-[var(--win-text-primary)]" @click="closeContextMenu">
    
    <!-- Cinematic Header -->
    <div class="flex items-center justify-between pb-6 border-b border-white/5 relative overflow-hidden group">
      <!-- Glow Effect -->
      <div class="absolute top-0 right-0 w-64 h-64 bg-[var(--win-accent)]/5 blur-[80px] rounded-full -translate-y-1/2 translate-x-1/2 group-hover:bg-[var(--win-accent)]/10 transition-colors"></div>
      
      <div class="flex items-center gap-5 relative z-10">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--glass-level-2-bg)] to-[var(--glass-level-1-bg)] flex items-center justify-center border border-white/10 shadow-2xl">
          <UIcon name="i-heroicons-circle-stack" class="w-8 h-8 text-[var(--win-accent)]" />
        </div>
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Database Viewer</h1>
          <p class="text-sm text-[var(--win-text-muted)] font-light">Inspect and query your application data directly.</p>
        </div>
      </div>
    </div>

    <div class="flex flex-col lg:flex-row gap-8 flex-1 min-h-0">
      
      <!-- Sidebar Navigation (Tables) -->
      <div class="lg:w-64 flex-shrink-0 flex flex-col gap-4">
        <div class="px-4 py-2 uppercase text-[10px] font-bold tracking-[0.2em] text-[var(--win-text-muted)]">
            Tables ({{ tables.length }})
        </div>
        
        <div class="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-1">
          <button
            v-for="table in tables"
            :key="table"
            @click="selectTable(table)"
            class="w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-300 group relative flex items-center gap-3"
            :class="currentTable === table 
              ? 'bg-[var(--glass-level-2-bg)] text-[var(--win-text-primary)] font-bold shadow-lg border border-white/10' 
              : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-[var(--glass-level-1-bg)] border border-transparent'"
          >
             <div v-if="currentTable === table" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-[var(--win-accent)] rounded-full hidden lg:block"></div>
             <UIcon name="i-heroicons-table-cells" class="w-4 h-4 flex-shrink-0" :class="currentTable === table ? 'text-[var(--win-accent)]' : 'opacity-70'" />
             <span class="truncate">{{ table }}</span>
          </button>
        </div>
      </div>

      <!-- Main Content Area (Glass Panel) -->
      <div class="flex-1 min-w-0 bg-[var(--glass-level-1-bg)] glass-panel !rounded-[2rem] border-white/5 shadow-2xl overflow-hidden flex flex-col backdrop-blur-3xl relative transition-all duration-500" :class="{ 'mr-[400px]': showSidePanel }">
        
        <!-- Loading Overlay -->
        <div v-if="loading && !autoRefreshActive" class="absolute inset-0 z-50 bg-[var(--win-bg-base)]/50 backdrop-blur-sm flex items-center justify-center animate-fade-in pointer-events-none">
            <div class="flex flex-col items-center gap-4">
                <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-[var(--win-accent)] animate-spin" />
                <span class="text-xs font-bold uppercase tracking-widest text-[var(--win-text-secondary)]">Loading Data...</span>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="p-6 border-b border-white/5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shrink-0" v-if="currentTable">
           <div class="flex items-center gap-3">
               <h2 class="text-xl font-bold flex items-center gap-3">
                   {{ currentTable }}
               </h2>
               <span class="px-3 py-1 bg-[var(--win-accent)]/10 text-[var(--win-accent)] rounded-lg text-[10px] font-bold tracking-wider uppercase border border-[var(--win-accent)]/20">
                   {{ totalRows }} Rows
               </span>
           </div>
           
           <div class="flex items-center gap-4 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
               <!-- Search Bar -->
               <div class="relative flex-1 md:w-48 group min-w-[150px]">
                   <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                       <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4 text-[var(--win-text-muted)] group-focus-within:text-[var(--win-accent)] transition-colors" />
                   </div>
                   <input 
                       v-model="searchQuery" 
                       @input="handleSearch"
                       type="text" 
                       placeholder="Search..." 
                       class="w-full bg-[var(--glass-level-2-bg)] border border-white/5 rounded-xl py-2 pl-9 pr-3 text-sm text-[var(--win-text-primary)] outline-none focus:border-[var(--win-accent)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all placeholder-[var(--win-text-muted)]/50"
                   />
                   <button v-if="searchQuery" @click="clearSearch" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                        <UIcon name="i-heroicons-x-mark" class="w-4 h-4 text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] cursor-pointer" />
                   </button>
               </div>

               <div class="h-6 w-px bg-white/10 hidden md:block"></div>
               
               <!-- Auto Refresh -->
               <button 
                  @click="toggleAutoRefresh"
                  class="p-2 rounded-xl border transition-all flex items-center gap-2 group relative"
                  :class="autoRefreshActive ? 'bg-[var(--status-success)]/10 text-[var(--status-success)] border-[var(--status-success)]/20 shadow-[0_0_10px_rgba(0,255,100,0.1)]' : 'bg-[var(--glass-level-2-bg)] text-[var(--win-text-muted)] border-white/5 hover:text-[var(--win-text-primary)]'"
                  title="Live Mode (5s)"
               >
                   <UIcon name="i-heroicons-bolt" class="w-4 h-4" :class="{ 'animate-pulse': autoRefreshActive }" />
                   <span v-if="autoRefreshActive" class="text-[10px] font-bold uppercase tracking-wider hidden lg:inline">Live</span>
               </button>

               <!-- Column Visibility -->
               <div class="relative">
                   <button 
                       @click.stop="toggleColumnMenu"
                       class="p-2 rounded-xl bg-[var(--glass-level-2-bg)] text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-[var(--glass-level-3-bg)] border border-white/5 transition-all"
                       title="Columns"
                   >
                       <UIcon name="i-heroicons-view-columns" class="w-4 h-4" />
                   </button>
                   
                   <!-- Column Dropdown -->
                   <div v-if="showColumnMenu" class="absolute right-0 top-full mt-2 w-48 bg-[var(--glass-level-4-bg)] border border-white/10 rounded-xl shadow-2xl p-2 z-50 backdrop-blur-xl animate-fade-in-up" @click.stop>
                       <div class="text-[10px] uppercase font-bold tracking-widest text-[var(--win-text-muted)] px-2 py-1 mb-1">Visible Columns</div>
                       <div class="max-h-60 overflow-y-auto custom-scrollbar">
                           <label v-for="col in allColumns" :key="col" class="flex items-center gap-3 px-2 py-1.5 hover:bg-white/5 rounded-lg cursor-pointer text-xs">
                               <input type="checkbox" :checked="!hiddenColumns.has(col)" @change="toggleColumn(col)" class="rounded bg-white/10 border-white/20 text-[var(--win-accent)] focus:ring-[var(--win-accent)]" />
                               <span class="truncate text-[var(--win-text-primary)]">{{ col }}</span>
                           </label>
                       </div>
                   </div>
               </div>
               
                             <div class="h-6 w-px bg-white/10 hidden md:block"></div>

               <div class="flex items-center gap-2 bg-[var(--glass-level-2-bg)] rounded-xl p-1 border border-white/5">
                   <button 
                       v-for="l in [25, 50, 100]" 
                       :key="l"
                       @click="limit = l; refresh()"
                       class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                       :class="limit === l ? 'bg-[var(--win-accent)] text-[var(--win-bg-base)] shadow-md' : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)]'"
                   >
                       {{ l }}
                   </button>
               </div>
               
               <button @click="refresh" class="p-2 rounded-xl bg-[var(--glass-level-2-bg)] text-[var(--win-text-secondary)] hover:text-[var(--win-text-primary)] hover:bg-[var(--glass-level-3-bg)] border border-white/5 transition-all group" title="Refresh">
                   <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" />
               </button>
           </div>
        </div>

        <!-- SQL Preview (Collapsible) -->
        <div v-if="lastSql" class="px-6 py-2 border-b border-white/5 bg-black/20">
            <button @click="showSql = !showSql" class="flex items-center gap-2 text-[10px] uppercase font-bold tracking-widest text-[var(--win-text-muted)] hover:text-[var(--win-accent)] transition-colors">
                <UIcon :name="showSql ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" class="w-3 h-3" />
                SQL Inspector
            </button>
            <div v-if="showSql" class="mt-2 p-3 bg-black/40 rounded-xl border border-white/5 font-mono text-xs text-[var(--win-text-secondary)] whitespace-pre-wrap break-all shadow-inner">
                {{ lastSql }}
            </div>
        </div>

        <!-- Data Content -->
        <div class="flex-1 overflow-auto custom-scrollbar relative px-6 pb-6" :class="{ 'opacity-50': loading && !autoRefreshActive }">
           <table class="w-full text-left border-separate border-spacing-y-1" v-if="currentTable && visibleColumns.length">
               <thead class="sticky top-0 z-10">
                   <tr>
                       <th 
                           v-for="col in visibleColumns" 
                           :key="col" 
                           @click="handleSort(col)"
                           class="px-4 py-4 text-[10px] uppercase font-bold tracking-[0.1em] text-[var(--win-text-muted)] whitespace-nowrap bg-[var(--glass-level-1-bg)]/95 backdrop-blur-md first:rounded-l-xl last:rounded-r-xl select-none cursor-pointer hover:bg-[var(--glass-level-2-bg)] hover:text-[var(--win-text-primary)] transition-colors group/th"
                       >
                           <div class="flex items-center gap-2">
                               {{ col }}
                               <UIcon 
                                   v-if="sortBy === col" 
                                   :name="sortOrder === 'asc' ? 'i-heroicons-bars-arrow-up' : 'i-heroicons-bars-arrow-down'" 
                                   class="w-3 h-3 text-[var(--win-accent)]"
                               />
                               <UIcon 
                                   v-else
                                   name="i-heroicons-arrows-up-down" 
                                   class="w-3 h-3 opacity-0 group-hover/th:opacity-30 transition-opacity"
                               />
                           </div>
                       </th>
                   </tr>
               </thead>
               <tbody class="text-sm">
                   <tr 
                      v-for="(row, idx) in rows" 
                      :key="idx" 
                      class="group hover:bg-[var(--glass-level-2-bg)] transition-colors cursor-pointer"
                      @click="openSidePanel(row)"
                      @contextmenu.prevent="showContextMenu($event, row)"
                    >
                       <td v-for="(col, cIdx) in visibleColumns" :key="col" 
                           class="px-4 py-3 border-b border-white/[0.02] whitespace-nowrap max-w-[300px] truncate group-hover:text-[var(--win-text-primary)] text-[var(--win-text-secondary)] transition-colors first:rounded-l-lg last:rounded-r-lg relative"
                           :class="{ 'font-mono text-xs': true }"
                           @mouseenter="handleCellHover($event, row[col], col)"
                           @mouseleave="handleCellLeave"
                       >
                           <!-- Boolean Chips -->
                           <span v-if="typeof row[col] === 'boolean'" 
                                 class="px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider"
                                 :class="row[col] ? 'bg-[var(--status-success)]/10 text-[var(--status-success)] border border-[var(--status-success)]/20' : 'bg-[var(--status-error)]/10 text-[var(--status-error)] border border-[var(--status-error)]/20'"
                           >
                               {{ row[col] ? 'YES' : 'NO' }}
                           </span>
                           <!-- Null -->
                           <span v-else-if="row[col] === null" class="text-[var(--win-text-muted)]/40 italic">NULL</span>
                           <!-- Text -->
                           <span v-else>{{ formatValue(row[col]) }}</span>
                       </td>
                   </tr>
               </tbody>
           </table>

           <!-- Empty States -->
           <div v-else-if="currentTable && !visibleColumns.length" class="flex flex-col items-center justify-center h-full text-[var(--win-text-muted)] gap-4">
              <UIcon name="i-heroicons-eye-slash" class="w-12 h-12 opacity-20" />
              <p>All columns are hidden.</p>
           </div>

           <div v-else-if="!currentTable" class="flex flex-col items-center justify-center h-full text-[var(--win-text-muted)] gap-6 animate-in zoom-in-95 duration-500">
               <div class="relative group">
                  <div class="absolute inset-0 bg-[var(--win-accent)] blur-[60px] opacity-20 rounded-full animate-pulse-slow group-hover:opacity-30 transition-opacity"></div>
                  <UIcon name="i-heroicons-table-cells" class="w-32 h-32 opacity-10 relative z-10" />
               </div>
               <div class="text-center space-y-2 relative z-10">
                   <h3 class="text-xl font-bold text-[var(--win-text-primary)]">Select a Table</h3>
                   <p class="text-sm max-w-xs mx-auto opacity-60 font-light">Choose a database table from the sidebar to inspect its contents.</p>
               </div>
           </div>
        </div>

        <!-- Footer / Pagination -->
        <div class="p-4 border-t border-white/5 bg-[var(--glass-level-2-bg)] flex items-center justify-between shrink-0" v-if="currentTable">
           <span class="text-xs text-[var(--win-text-muted)] font-mono">
               Showing {{ offset + 1 }}-{{ Math.min(offset + limit, totalRows || 0) }} of {{ totalRows }}
           </span>
           
           <div class="flex gap-2">
               <button 
                   @click="prevPage" 
                   :disabled="offset <= 0 || loading"
                   class="px-4 py-2 rounded-xl bg-[var(--glass-level-3-bg)] border border-white/5 hover:bg-[var(--win-accent)]/10 hover:text-[var(--win-accent)] hover:border-[var(--win-accent)]/20 disabled:opacity-30 disabled:hover:bg-[var(--glass-level-3-bg)] disabled:hover:text-inherit disabled:cursor-not-allowed transition-all text-xs font-bold uppercase tracking-wider flex items-center gap-2"
               >
                   <UIcon name="i-heroicons-arrow-left" class="w-3 h-3" />
                   Prev
               </button>
               <button 
                   @click="nextPage" 
                   :disabled="!hasMore || loading"
                   class="px-4 py-2 rounded-xl bg-[var(--glass-level-3-bg)] border border-white/5 hover:bg-[var(--win-accent)]/10 hover:text-[var(--win-accent)] hover:border-[var(--win-accent)]/20 disabled:opacity-30 disabled:hover:bg-[var(--glass-level-3-bg)] disabled:hover:text-inherit disabled:cursor-not-allowed transition-all text-xs font-bold uppercase tracking-wider flex items-center gap-2"
               >
                   Next
                   <UIcon name="i-heroicons-arrow-right" class="w-3 h-3" />
               </button>
           </div>
        </div>
        
        <!-- Hover Media Preview -->
        <div 
            v-if="hoverPreview.show" 
            class="fixed z-[100] pointer-events-none rounded-2xl overflow-hidden shadow-2xl border border-white/10 p-1 bg-[var(--glass-level-4-bg)] backdrop-blur-xl animate-scale-in"
            :style="{ left: hoverPreview.x + 20 + 'px', top: hoverPreview.y - 100 + 'px' }"
        >
            <img :src="hoverPreview.url" class="max-w-[150px] max-h-[220px] rounded-xl object-cover" />
        </div>
        
        <!-- Context Menu -->
         <div 
             v-if="contextMenu.show" 
             class="fixed z-[100] bg-[var(--glass-level-4-bg)] border border-white/10 rounded-xl shadow-2xl backdrop-blur-xl min-w-[160px] py-1 animate-fade-in-up origin-top-left overflow-hidden"
             :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
             @click.stop
         >
             <button @click="copyToClipboard(contextMenu.row[contextMenu.col] || JSON.stringify(contextMenu.row))" class="w-full text-left px-4 py-2.5 text-xs hover:bg-white/10 text-[var(--win-text-primary)] transition-colors flex items-center gap-2">
                 <UIcon name="i-heroicons-clipboard" class="w-3 h-3" /> Copy Value
             </button>
             <button @click="copyToClipboard(JSON.stringify(contextMenu.row, null, 2))" class="w-full text-left px-4 py-2.5 text-xs hover:bg-white/10 text-[var(--win-text-primary)] transition-colors flex items-center gap-2">
                 <UIcon name="i-heroicons-code-bracket" class="w-3 h-3" /> Copy Row JSON
             </button>
             <div class="h-px bg-white/10 my-1"></div>
             <button @click="closeContextMenu" class="w-full text-left px-4 py-2.5 text-xs hover:bg-white/10 text-[var(--status-error)] transition-colors">
                 Close
             </button>
         </div>

      </div>
      
      <!-- Side Detail Panel (Slide-Over) -->
      <div 
          class="fixed inset-y-0 right-0 w-[400px] bg-[var(--glass-level-3-bg)] backdrop-blur-3xl border-l border-white/10 shadow-2xl z-40 transform transition-transform duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]"
          :class="showSidePanel ? 'translate-x-0' : 'translate-x-full'"
      >
          <div class="h-full flex flex-col" v-if="selectedRow">
              <div class="p-6 border-b border-white/5 flex items-center justify-between">
                  <h3 class="text-xl font-bold text-[var(--win-text-primary)]">Row Details</h3>
                  <button @click="closeSidePanel" class="p-2 rounded-full hover:bg-white/5 transition-colors">
                      <UIcon name="i-heroicons-x-mark" class="w-5 h-5 text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)]" />
                  </button>
              </div>
              
              <div class="flex-1 overflow-y-auto p-6 space-y-6">
                  <!-- Image Header if valid image found -->
                  <div v-if="selectedRowPoster" class="flex justify-center mb-6">
                      <div class="relative w-40 h-60 rounded-2xl overflow-hidden shadow-2xl border border-white/10 group">
                           <img :src="selectedRowPoster" class="w-full h-full object-cover" />
                           <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                               <a :href="selectedRowPoster" target="_blank" class="p-2 bg-white/20 rounded-full backdrop-blur-md hover:bg-white/40 transition-colors">
                                   <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-5 h-5 text-white" />
                               </a>
                           </div>
                      </div>
                  </div>
                  
                  <div class="space-y-4">
                      <div v-for="key in Object.keys(selectedRow)" :key="key" class="group">
                          <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] block mb-1 group-hover:text-[var(--win-accent)] transition-colors">{{ key }}</label>
                          <div class="text-sm text-[var(--win-text-primary)] font-mono break-all bg-[var(--glass-level-1-bg)] p-3 rounded-xl border border-white/5 group-hover:border-[var(--win-accent)]/20 transition-colors">
                              {{ formatValue(selectedRow[key]) }}
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn, useIntervalFn, useClipboard } from '@vueuse/core'

const { getDbTables, queryDbTable } = useApi()
const { copy } = useClipboard()
const toast = useToast()

const tables = ref<string[]>([])
const currentTable = ref<string | null>(null)
const allColumns = ref<string[]>([])
const hiddenColumns = reactive(new Set<string>())
const rows = ref<any[]>([])
const loading = ref(false)

// Pagination
const offset = ref(0)
const limit = ref(50)
const totalRows = ref(0) 

// Sort & Search
const sortBy = ref<string | undefined>(undefined)
const sortOrder = ref<'asc' | 'desc'>('asc')
const searchQuery = ref('')
const lastSql = ref('')
const showSql = ref(false)

// Feature States
const showColumnMenu = ref(false)
const autoRefreshActive = ref(false)
const showSidePanel = ref(false)
const selectedRow = ref<any>(null)
const hoverPreview = reactive({ show: false, x: 0, y: 0, url: '' })
const contextMenu = reactive({ show: false, x: 0, y: 0, row: {} as any, col: '' })

// Auto Refresh Logic
const { pause, resume, isActive } = useIntervalFn(() => {
    if (currentTable.value) fetchData(true)
}, 5000, { immediate: false })

const toggleAutoRefresh = () => {
    autoRefreshActive.value = !autoRefreshActive.value
    if (autoRefreshActive.value) {
        resume()
        toast.add({ title: 'Live Mode Active', description: 'Refreshing every 5 seconds', color: 'green' })
    } else {
        pause()
        toast.add({ title: 'Live Mode Paused', color: 'gray' })
    }
}

onMounted(async () => {
    try {
        const res = await getDbTables()
        tables.value = res.tables
    } catch (e) {
        console.error("Failed to load tables", e)
    }
})

const selectTable = (table: string) => {
    currentTable.value = table
    // Reset state
    offset.value = 0
    sortBy.value = undefined
    sortOrder.value = 'asc'
    searchQuery.value = ''
    hiddenColumns.clear()
    lastSql.value = ''
    closeSidePanel()
    fetchData()
}

const fetchData = async (silent = false) => {
    if (!currentTable.value) return
    if (!silent) loading.value = true
    
    try {
        // Optimistic clear if aggressive
        // rows.value = [] 
        const res = await queryDbTable(
            currentTable.value, 
            limit.value, 
            offset.value,
            sortBy.value,
            sortOrder.value,
            searchQuery.value
        )
        allColumns.value = res.columns
        rows.value = res.rows
        totalRows.value = res.total as any
        
        // Backend returns the SQL now?
        if ((res as any).sql_query) {
             lastSql.value = (res as any).sql_query
        }
    } catch (e) {
        console.error("Failed to fetch data", e)
        if (isActive.value) toggleAutoRefresh() // Stop on error
    } finally {
        loading.value = false
    }
}

const visibleColumns = computed(() => {
    return allColumns.value.filter(c => !hiddenColumns.has(c))
})

const toggleColumnMenu = () => {
    showColumnMenu.value = !showColumnMenu.value
}

const toggleColumn = (col: string) => {
    if (hiddenColumns.has(col)) {
        hiddenColumns.delete(col)
    } else {
        hiddenColumns.add(col)
    }
}

// Side Panel
const openSidePanel = (row: any) => {
    selectedRow.value = row
    showSidePanel.value = true
}

const closeSidePanel = () => {
    showSidePanel.value = false
    selectedRow.value = null
}

const selectedRowPoster = computed(() => {
    if (!selectedRow.value) return null
    // Try to find a poster or image URL
    for (const key of Object.keys(selectedRow.value)) {
        const val = String(selectedRow.value[key] || '')
        if ((key.includes('poster') || key.includes('url')) && (val.endsWith('.jpg') || val.endsWith('.png') || val.endsWith('.webp'))) {
            return val
        }
    }
    return null
})

// Validation for preview hover
const isImageUrl = (val: any, key: string) => {
    if (typeof val !== 'string') return false
    const k = key.toLowerCase()
    const v = val.toLowerCase()
    return (k.includes('poster') || k.includes('url') || k.includes('path')) && 
           (v.startsWith('http') || v.startsWith('/')) &&
           (v.match(/\.(jpeg|jpg|gif|png|webp)$/) != null)
}

const handleCellHover = (e: MouseEvent, val: any, key: string) => {
    if (isImageUrl(val, key)) {
        hoverPreview.url = val
        hoverPreview.x = e.clientX
        hoverPreview.y = e.clientY
        hoverPreview.show = true
    }
}

const handleCellLeave = () => {
    hoverPreview.show = false
}

// Context Menu
const showContextMenu = (e: MouseEvent, row: any) => {
    contextMenu.x = e.clientX
    contextMenu.y = e.clientY
    contextMenu.row = row
    contextMenu.show = true
}

const closeContextMenu = () => {
    contextMenu.show = false
    showColumnMenu.value = false
}

const copyToClipboard = async (text: string) => {
    await copy(text)
    toast.add({ title: 'Copied', description: 'Copied to clipboard', color: 'green', timeout: 2000 })
    closeContextMenu()
}


// Search Handling
const handleSearch = useDebounceFn(() => {
    offset.value = 0 // Reset pagination on search
    fetchData()
}, 500)

const clearSearch = () => {
    searchQuery.value = ''
    handleSearch()
}

// Sort Handling
const handleSort = (column: string) => {
    if (sortBy.value === column) {
        // Toggle order
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
        // New column
        sortBy.value = column
        sortOrder.value = 'asc'
    }
    fetchData()
}

// Pagination
const hasMore = computed(() => {
    if (totalRows.value > -1) {
        return offset.value + limit.value < totalRows.value
    }
    return rows.value.length === limit.value 
})

const nextPage = () => {
    if (!hasMore.value) return
    offset.value += limit.value
    fetchData()
}

const prevPage = () => {
    if (offset.value >= limit.value) {
        offset.value -= limit.value
        fetchData()
    }
}

const refresh = () => fetchData()

const formatValue = (val: any) => {
    if (val === null) return 'NULL'
    if (val === undefined) return ''
    if (typeof val === 'boolean') return val ? 'TRUE' : 'FALSE'
    if (typeof val === 'object') return JSON.stringify(val)
    return String(val)
}
</script>

<style scoped>
/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--win-text-muted);
  border-radius: 99px;
  opacity: 0.2;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background: var(--win-text-secondary);
}

.animate-pulse-slow {
    animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 0.2; }
    50% { opacity: 0.1; }
}

.animate-scale-in {
    animation: scaleIn 0.2s ease-out forwards;
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}
</style>
