<template>
  <div class="h-full flex flex-col relative">
    
    <!-- Full Page Loading Overlay for Resets -->
    <div v-if="isLoadingMore && items.length === 0" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-300">
        <div class="relative">
            <div class="w-16 h-16 rounded-full border-4 border-white/5 border-t-[var(--win-accent)] animate-spin"></div>
            <UIcon name="i-heroicons-film" class="w-6 h-6 text-[var(--win-accent)] absolute inset-0 m-auto animate-pulse" />
        </div>
        <p class="mt-4 text-xs font-mono uppercase tracking-widest text-[var(--win-text-muted)] animate-pulse">Loading Library</p>
    </div>

    <!-- Header -->
    <div class="p-4 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-4 sticky top-0 z-20 bg-[var(--glass-level-4-bg)] backdrop-blur-xl">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-[var(--win-text-primary)] mb-1 flex items-center gap-3">
          <UIcon name="i-heroicons-film" class="w-6 h-6 md:w-8 md:h-8 text-[var(--win-accent)]" />
          Media Library
        </h1>
        <p class="text-xs md:text-sm text-[var(--win-text-muted)]">Browse your media collection with rich metadata</p>
      </div>

        <!-- Search & Sort Row -->
        <div class="flex flex-wrap items-center gap-2 md:gap-3 w-full md:w-auto mt-2 md:mt-0">
          <!-- Search -->
          <div class="relative group flex-1 md:flex-none">
            <UIcon name="i-heroicons-magnifying-glass" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--win-text-muted)] group-focus-within:text-[var(--win-accent)] transition-colors" />
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Search library..." 
              class="bg-[var(--glass-level-2-bg)] border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-[var(--win-text-primary)] focus:border-[var(--win-accent)] outline-none w-full md:w-64 transition-all md:focus:w-80 placeholder-[var(--win-text-muted)] focus:bg-[var(--glass-level-3-bg)]"
            />
          </div>

          <!-- Sort Dropdown -->
          <div class="relative group">
            <select 
              v-model="sortOption"
              class="bg-[var(--glass-level-3-bg)] border border-white/10 rounded-lg pl-3 pr-8 py-2 text-sm text-[var(--win-text-primary)] focus:border-[var(--win-accent)] outline-none appearance-none cursor-pointer hover:bg-white/5 transition-colors font-bold"
            >
              <option value="created_at:desc">Most Recent</option>
              <option value="created_at:asc">Oldest First</option>
              <option value="title:asc">Title (A-Z)</option>
              <option value="title:desc">Title (Z-A)</option>
              <option value="release_date:desc">Newest Release</option>
              <option value="release_date:asc">Oldest Release</option>
              <option value="rating:desc">Top Rated</option>
            </select>
            <UIcon name="i-heroicons-chevron-down" class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--win-text-muted)] pointer-events-none" />
          </div>
        </div>

        <!-- Controls Row -->
        <div class="flex items-center gap-2 w-full md:w-auto mt-2 md:mt-0 xl:ml-auto">
             <!-- View Mode Toggle -->
             <div class="flex bg-[var(--glass-level-3-bg)] p-1 rounded-lg border border-white/10">
                <button 
                  @click="viewMode = 'grid'"
                  class="p-2 rounded-md transition-all duration-300"
                  :class="viewMode === 'grid' ? 'bg-[var(--win-accent)] text-black shadow-lg' : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-white/5'"
                  title="Grid View"
                >
                  <UIcon name="i-heroicons-squares-2x2" class="w-5 h-5" />
                </button>
                <button 
                  @click="viewMode = 'list'"
                  class="p-2 rounded-md transition-all duration-300"
                  :class="viewMode === 'list' ? 'bg-[var(--win-accent)] text-black shadow-lg' : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-white/5'"
                  title="List View"
                >
                  <UIcon name="i-heroicons-list-bullet" class="w-5 h-5" />
                </button>
             </div>

             <!-- Selection Mode Toggle -->
             <button 
               @click="toggleSelectionMode"
               class="btn-ghost !rounded-lg flex items-center justify-center gap-2"
               :class="{ '!bg-[var(--win-accent)] !text-black': selectionMode }"
             >
               <UIcon :name="selectionMode ? 'i-heroicons-check-circle' : 'i-heroicons-squares-2x2'" class="w-5 h-5" />
               <span class="sr-only md:not-sr-only md:inline">{{ selectionMode ? 'Exit Select' : 'Select' }}</span>
             </button>

             <!-- Tabs -->
            <div class="flex flex-1 md:flex-none bg-[var(--glass-level-3-bg)] p-1 rounded-lg border border-white/10">
               <button 
                 @click="filterType = 'movie'"
                 class="flex-1 md:flex-none px-4 md:px-6 py-2 text-xs md:text-sm font-bold rounded-md transition-all duration-300 flex justify-center"
                 :class="filterType === 'movie' ? 'bg-[var(--win-accent)] text-black shadow-[0_0_15px_var(--win-accent)]' : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-white/5'"
               >
                 <div class="flex items-center gap-2">
                    <UIcon name="i-heroicons-film" class="w-4 h-4" />
                    <span>Movies</span>
                 </div>
               </button>
               <button 
                 @click="filterType = 'tv'"
                 class="flex-1 md:flex-none px-4 md:px-6 py-2 text-xs md:text-sm font-bold rounded-md transition-all duration-300 flex justify-center"
                 :class="filterType === 'tv' ? 'bg-[var(--win-accent)] text-black shadow-[0_0_15px_var(--win-accent)]' : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-white/5'"
               >
                 <div class="flex items-center gap-2">
                    <UIcon name="i-heroicons-tv" class="w-4 h-4" />
                    <span>Shows</span>
                 </div>
               </button>
            </div>

            <!-- Scan Button -->
            <button 
              @click="triggerScan"
              :disabled="scanning"
              class="btn-secondary !rounded-lg flex items-center justify-center gap-2"
            >
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5" :class="{ 'animate-spin': scanning }" />
              <span class="sr-only md:not-sr-only md:inline">{{ scanning ? 'Scanning...' : 'Scan' }}</span>
            </button>
        </div>
      </div>

    <!-- Content Area -->
    <div ref="scrollEl" class="flex-1 min-h-0 overflow-y-auto custom-scrollbar pr-2 -mr-2">
       
        <!-- Selection Actions Bar -->
        <div v-if="selectionMode && selectedItems.size > 0" class="sticky top-0 z-20 mb-4 glass-panel p-3 flex items-center justify-between gap-3 animate-fade-in-down">
          <div class="flex items-center gap-3">
            <span class="text-sm text-[var(--win-text-primary)] font-bold">{{ selectedItems.size }} selected</span>
            <button @click="selectAllVisible" class="text-xs text-[var(--win-accent)] hover:underline">Select All</button>
            <button @click="clearSelection" class="text-xs text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)]">Clear</button>
          </div>
          <button 
            @click="handleBulkCopy"
            class="btn-primary flex items-center gap-2"
          >
            <UIcon name="i-heroicons-document-duplicate" class="w-4 h-4" />
            Copy Selected
          </button>
        </div>

        <!-- Grid View -->
        <div v-if="viewMode === 'grid'">
            <!-- Loading Skeleton Grid -->
            <div v-if="isLoading" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 md:gap-6">
                <div v-for="n in 12" :key="n" class="aspect-[2/3]">
                    <SkeletonCard />
                </div>
            </div>

            <div v-else-if="filteredItems.length > 0" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 md:gap-6 pb-20 animate-fade-in-up min-h-[500px]">
                <!-- ... Grid Item Content is inside here ... -->
                <div 
                  v-for="item in filteredItems" 
                  :key="item.id"
                  @click="handleItemClick(item)"
                  class="group relative aspect-[2/3] bg-[var(--glass-level-2-bg)] rounded-lg md:rounded-xl overflow-hidden border transition-all duration-300 hover:-translate-y-1 cursor-pointer"
                  :class="[
                    isSelected(item.id) 
                      ? 'border-[var(--win-accent)] shadow-[0_0_20px_rgba(96,205,255,0.3)] ring-2 ring-[var(--win-accent)]/50' 
                      : 'border-white/5 hover:border-[var(--win-accent)] hover:shadow-[0_0_20px_rgba(96,205,255,0.2)]'
                  ]"
                >
                   <!-- Selection Checkbox (visible in selection mode) -->
                   <div 
                     v-if="selectionMode"
                     class="absolute top-2 left-2 z-20"
                     @click.stop="toggleSelection(item.id)"
                   >
                     <div 
                       class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all cursor-pointer"
                       :class="isSelected(item.id) 
                         ? 'bg-[var(--win-accent)] border-[var(--win-accent)]' 
                         : 'bg-black/50 border-white/30 hover:border-[var(--win-accent)]'"
                     >
                       <UIcon v-if="isSelected(item.id)" name="i-heroicons-check" class="w-4 h-4 text-black" />
                     </div>
                   </div>

                   <!-- Poster Image -->
                   <img 
                     v-if="item.poster_url" 
                     :src="item.poster_url.startsWith('http') ? item.poster_url : `${apiBase}${item.poster_url}`" 
                     class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                     loading="lazy"
                   />
                   <!-- Fallback Poster -->
                   <div v-else class="w-full h-full flex flex-col items-center justify-center p-4 bg-gradient-to-br from-white/5 to-black">
                      <UIcon :name="item.media_type === 'movie' ? 'i-heroicons-film' : 'i-heroicons-tv'" class="w-12 h-12 text-[var(--win-text-muted)] mb-2" />
                      <span class="text-sm text-center font-bold text-[var(--win-text-secondary)] line-clamp-2">{{ item.title }}</span>
                   </div>

                   <!-- Overlay Gradient (only when not in selection mode) -->
                   <div 
                     v-if="!selectionMode"
                     class="absolute inset-0 bg-gradient-to-t from-black/95 via-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-3 md:p-4"
                   >
                       <div class="flex-shrink-0">
                         <h3 class="font-bold text-[var(--win-text-primary)] leading-tight line-clamp-2 text-sm md:text-base">{{ item.title }}</h3>
                         
                         <!-- Metadata Row -->
                         <div class="flex items-center gap-2 mt-1 md:mt-2 text-[10px] md:text-xs">
                            <span class="text-[var(--win-accent)] font-mono">{{ item.year || 'Unknown' }}</span>
                            <span v-if="item.rating" class="text-amber-400 flex items-center gap-1 font-bold">
                               <UIcon name="i-heroicons-star" class="w-3 h-3" />
                               {{ parseFloat(item.rating).toFixed(1) }}
                            </span>
                         </div>

                         <!-- Technical Tags -->
                         <div v-if="getTechTags(item).length" class="flex flex-wrap gap-1 md:gap-1.5 mt-1 md:mt-2">
                             <span 
                               v-for="tag in getTechTags(item)" 
                               :key="tag.label"
                               :class="[
                                   'text-[9px] md:text-[10px] font-bold px-1 py-0.5 rounded uppercase tracking-wider',
                                   tag.color
                               ]"
                             >
                               {{ tag.label }}
                             </span>
                         </div>

                         <!-- Enriched Metadata (Genres / Overview) -->
                         <div v-if="item.genres && item.genres.length" class="hidden md:flex flex-wrap gap-1 mt-2">
                             <span v-for="g in item.genres.slice(0, 2)" :key="g" class="text-[10px] uppercase tracking-wider text-[var(--win-text-muted)] bg-white/10 px-1.5 py-0.5 rounded">
                                 {{ g }}
                             </span>
                         </div>
                         
                         <!-- Overview - Limited to 5 lines -->
                         <p v-if="item.overview" class="hidden md:block text-[10px] text-[var(--win-text-muted)] mt-2 leading-relaxed opacity-90 overflow-hidden" style="display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical;">
                             {{ item.overview }}
                         </p>
                       </div>
                       
                       <!-- Copy Button - Always visible at bottom -->
                       <button 
                          @click.stop="handleCopy(item)"
                          class="mt-2 md:mt-3 w-full py-1.5 md:py-2 bg-[var(--win-accent)] text-black text-[10px] md:text-xs font-bold rounded hover:bg-white transition-colors flex items-center justify-center gap-1 md:gap-2 flex-shrink-0"
                       >
                          <UIcon name="i-heroicons-document-duplicate" class="w-3 h-3 md:w-4 md:h-4" />
                          Copy
                       </button>
                   </div>
                </div>
            </div>
            
            <!-- Empty State for Grid -->
            <div v-else class="h-full flex flex-col items-center justify-center text-gray-500 opacity-60">
                <template v-if="scanning">
                   <UIcon name="i-heroicons-arrow-path" class="w-16 h-16 animate-spin mb-4" />
                   <p>Scanning your Zurg drive for media...</p>
                </template>
                <template v-else>
                   <UIcon name="i-heroicons-circle-stack" class="w-16 h-16 mb-4" />
                   <p v-if="items.length === 0">Your library is empty. Click "Scan Library" to start.</p>
                   <p v-else>No matches found for "{{ searchQuery }}"</p>
                </template>
            </div>
        </div>

        <!-- List View -->
        <div v-else-if="viewMode === 'list'" class="pb-20 space-y-2">
            <!-- Loading Skeleton List -->
             <div v-if="isLoading" class="space-y-3">
                 <div v-for="n in 8" :key="n" class="h-32 bg-[var(--glass-level-1-bg)] rounded-xl animate-pulse"></div>
             </div>

             <div v-else-if="filteredItems.length > 0" class="space-y-2 animate-fade-in-up min-h-[500px]">
                <div 
                   v-for="item in filteredItems" 
                   :key="item.id"
                   @click="handleItemClick(item)"
                   class="group flex items-center gap-2 md:gap-4 p-2 md:p-3 bg-[var(--glass-level-1-bg)] hover:bg-[var(--glass-level-2-bg)] rounded-xl border border-white/5 hover:border-[var(--win-accent)]/30 transition-all cursor-pointer relative"
                   :class="{ 'border-[var(--win-accent)] bg-[var(--glass-level-2-bg)]': isSelected(item.id) }"
                >
                   <!-- Selection Checkbox (List) -->
                   <div 
                     v-if="selectionMode"
                     class="flex-shrink-0"
                     @click.stop="toggleSelection(item.id)"
                   >
                     <div 
                       class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all cursor-pointer"
                       :class="isSelected(item.id) 
                         ? 'bg-[var(--win-accent)] border-[var(--win-accent)]' 
                         : 'border-[var(--win-text-muted)] hover:border-[var(--win-text-primary)]'"
                     >
                       <UIcon v-if="isSelected(item.id)" name="i-heroicons-check" class="w-3.5 h-3.5 text-black" />
                     </div>
                   </div>

                   <!-- Poster Thumbnail (Left) -->
                   <div class="flex-shrink-0 h-20 w-[3.5rem] md:h-32 md:w-24 rounded-lg overflow-hidden bg-black/50 relative shadow-md">
                      <img 
                        v-if="item.poster_url" 
                        :src="item.poster_url.startsWith('http') ? item.poster_url : `${apiBase}${item.poster_url}`" 
                        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        loading="lazy"
                      />
                      <div v-else class="w-full h-full flex items-center justify-center bg-white/5">
                         <UIcon :name="item.media_type === 'movie' ? 'i-heroicons-film' : 'i-heroicons-tv'" class="w-8 h-8 text-white/20" />
                      </div>
                   </div>

                   <!-- Info Block (Middle) -->
                   <div class="flex-1 min-w-0 flex flex-col justify-center gap-1.5">
                       <div class="flex items-center gap-3">
                           <h3 class="text-base md:text-lg font-bold text-[var(--win-text-primary)] truncate">{{ item.title }}</h3>
                           <span class="text-xs font-mono text-[var(--win-accent)] bg-[var(--win-accent)]/10 px-1.5 py-0.5 rounded">{{ item.year || '----' }}</span>
                           <span v-if="item.rating" class="text-amber-400 text-xs flex items-center gap-1 font-bold bg-amber-400/10 px-1.5 py-0.5 rounded">
                               <UIcon name="i-heroicons-star" class="w-3 h-3" />
                               {{ parseFloat(item.rating).toFixed(1) }}
                           </span>
                       </div>

                       <!-- Tag Row -->
                       <div class="flex flex-wrap items-center gap-2">
                           <!-- Tech Tags -->
                            <span 
                              v-for="tag in getTechTags(item)" 
                              :key="tag.label"
                              :class="[
                                  'text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider',
                                  tag.color
                              ]"
                            >
                              {{ tag.label }}
                            </span>
                            
                            <!-- Divider -->
                            <div v-if="getTechTags(item).length && item.genres?.length" class="h-3 w-px bg-white/10 mx-1"></div>

                            <!-- Genres -->
                            <span v-for="g in (item.genres || []).slice(0, 3)" :key="g" class="text-[10px] text-[var(--win-text-muted)] uppercase tracking-wider">
                                {{ g }}
                            </span>
                       </div>
                       
                       <!-- Path Info (Subtle) -->
                       <div class="flex items-center gap-2 mt-1 opacity-50 group-hover:opacity-100 transition-opacity">
                            <UIcon name="i-heroicons-folder" class="w-3 h-3 text-[var(--win-text-muted)]" />
                            <span class="text-[10px] font-mono text-[var(--win-text-muted)] truncate">{{ item.full_path }}</span>
                       </div>
                   </div>

                   <!-- Action (Right) -->
                   <div class="flex-shrink-0 flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity px-4">
                       <button 
                          @click.stop="handleCopy(item)"
                          class="btn-ghost !p-2 rounded-lg text-[var(--win-accent)] bg-[var(--win-accent)]/10 hover:bg-[var(--win-accent)] hover:text-black transition-colors"
                          title="Copy to Library"
                       >
                          <UIcon name="i-heroicons-document-duplicate" class="w-5 h-5" />
                       </button>
                       <button 
                         class="btn-ghost !p-2 rounded-lg text-[var(--win-text-muted)] hover:text-white"
                         title="View Details"
                       >
                          <UIcon name="i-heroicons-chevron-right" class="w-5 h-5" />
                       </button>
                   </div>
                </div>
             </div>
             
             <!-- Empty State for List -->
            <div v-else class="h-full flex flex-col items-center justify-center text-gray-500 opacity-60 py-20">
                <template v-if="scanning">
                   <UIcon name="i-heroicons-arrow-path" class="w-16 h-16 animate-spin mb-4" />
                   <p>Scanning your Zurg drive for media...</p>
                </template>
                <template v-else>
                   <UIcon name="i-heroicons-queue-list" class="w-16 h-16 mb-4" />
                   <p v-if="items.length === 0">Your library is empty. Click "Scan Library" to start.</p>
                   <p v-else>No matches found for "{{ searchQuery }}"</p>
                </template>
            </div>
        </div>
    </div>


    <!-- Loading State for Scroll -->
    <div v-if="isLoadingMore && items.length > 0" class="py-10 flex justify-center">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-[var(--win-accent)]" />
    </div>

    <!-- No more items indicator -->
    <div v-if="!hasMore && items.length > 0" class="py-10 text-center text-gray-500 text-xs font-mono uppercase tracking-widest opacity-40">
        End of Library
    </div>
    
    <!-- Infinite Scroll Trigger (Invisible) -->
    <div
      ref="infiniteScrollTrigger"
      class="h-4 w-full mt-8"
    />

    <!-- Details Modal -->
    <MediaDetailModal 
        v-if="selectedItem"
        :show="!!selectedItem"
        :item="selectedItem"
        @close="selectedItem = null"
        @copy="handleCopy"
        @view-trakt="openInTrakt"
    />

    <!-- Trakt Setup Modal -->
    <div v-if="showTraktModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
        <div class="glass-panel w-full max-w-md p-6 !rounded-xl !border-[var(--win-accent)] shadow-[0_0_50px_rgba(96,205,255,0.2)] animate-in">
            <h2 class="text-xl font-bold text-white mb-2 flex items-center gap-2">
               <UIcon name="i-heroicons-key" class="w-5 h-5 text-[var(--win-accent)]" />
               Setup Trakt Integration
            </h2>
            <p class="text-sm text-gray-400 mb-6">
               To fetch posters and metadata, we need your Trakt Client ID.
            </p>

            <form @submit.prevent="saveTraktKey" class="space-y-4">
                <div>
                   <label class="text-xs font-bold text-gray-500 uppercase">Trakt Client ID</label>
                   <input 
                     v-model="traktKeyInput"
                     type="text" 
                     required
                     placeholder="Enter your Client ID"
                     class="w-full mt-1 bg-black/40 border border-white/10 rounded px-3 py-2 text-[var(--win-text-primary)] focus:border-[var(--win-accent)] outline-none font-mono text-sm"
                   />
                </div>
                
                <div class="flex justify-end gap-3 mt-6">
                   <button type="button" @click="showTraktModal = false" class="text-gray-400 hover:text-white text-sm">Cancel</button>
                   <button 
                     type="submit" 
                     class="px-4 py-2 bg-[var(--win-accent)] text-black font-bold rounded text-sm hover:bg-white transition-colors"
                     :disabled="savingKey"
                   >
                     {{ savingKey ? 'Saving...' : 'Save & Enable' }}
                   </button>
                </div>
            </form>
        </div>
    </div>


  </div>
</template>

<script setup lang="ts">
import SkeletonCard from '~/components/SkeletonCard.vue'
import MediaDetailModal from '~/components/MediaDetailModal.vue'

const toast = useToast()
const { getSettings } = useApi()
const { setSource, setDestination, goToStep, reset: resetWizard } = useCopyWizard()

// State
const scrollEl = ref<HTMLElement | null>(null)
const items = ref<any[]>([])
const scanning = ref(false)
const searchQuery = ref('')
const filterType = ref<string>('movie')
const viewMode = ref<'grid' | 'list'>('grid')

// Pagination State
const page = ref(1)
const INITIAL_LIMIT = 48
const SUBSEQUENT_LIMIT = 48
const totalItems = ref(0)
const hasMore = ref(true)
const isLoadingMore = ref(false)
const finished = ref(false)
const sortOption = ref('created_at:desc') // Format: "field:order"

// Modal State
const showTraktModal = ref(false)
const traktKeyInput = ref('')
const savingKey = ref(false)
const selectedItem = ref<any>(null)

// Selection Mode State
const selectionMode = ref(false)
const selectedItems = ref<Set<number>>(new Set())

// Loading state for skeleton
const isLoading = ref(true)


// Selection Methods
const toggleSelectionMode = () => {
  selectionMode.value = !selectionMode.value
  if (!selectionMode.value) {
    selectedItems.value.clear()
  }
}

const isSelected = (id: number) => selectedItems.value.has(id)

const toggleSelection = (id: number) => {
  if (selectedItems.value.has(id)) {
    selectedItems.value.delete(id)
  } else {
    selectedItems.value.add(id)
  }
  // Force reactivity
  selectedItems.value = new Set(selectedItems.value)
}

const selectAllVisible = () => {
  filteredItems.value.forEach(item => selectedItems.value.add(item.id))
  selectedItems.value = new Set(selectedItems.value)
}

const clearSelection = () => {
  selectedItems.value.clear()
  selectedItems.value = new Set(selectedItems.value)
}

const handleItemClick = (item: any) => {
  if (selectionMode.value) {
    toggleSelection(item.id)
  } else {
    selectedItem.value = item
    
    // Prioritize enrichment if missing data
    if ((!item.poster_url || !item.tmdb_id) && token.value) {
        $fetch(`${apiBase}/api/library/prioritize`, {
            method: 'POST',
            body: { item_id: item.id },
            headers: { 'Authorization': `Bearer ${token.value}` }
        }).catch(e => console.error("Failed to prioritize item", e))
    }
  }
}

const handleBulkCopy = async () => {
    if (selectedItems.value.size === 0) return
    
    resetWizard()
    
    // Prepare items info
    const itemsToCopy = items.value.filter(i => selectedItems.value.has(i.id)).map(i => ({
        id: i.id,
        name: i.title,
        path: i.full_path,
        size: i.size_bytes || 0,
        size_formatted: i.size_formatted || ''
    }))
    
    setSource(itemsToCopy.map(i => i.path), itemsToCopy)
    
    // Auto-select destination from settings
    try {
        const settings = await getSettings()
        const defaultPath = filterType.value === 'movie' ? settings.default_movies_path : settings.default_series_path
        if (defaultPath) {
            setDestination(defaultPath)
        }
    } catch (e) {
        console.error("Failed to load settings for defaults", e)
    }
    
    goToStep(3)
    navigateTo('/copy-wizard')
}

// Computed
const filteredItems = computed(() => {
    // We now rely entirely on server-side filtering
    return items.value
})

const totalPages = computed(() => {
    if (totalItems.value <= INITIAL_LIMIT) return 1
    return 1 + Math.ceil((totalItems.value - INITIAL_LIMIT) / SUBSEQUENT_LIMIT)
})

// Methods
const { token } = useAuth()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const setup = async () => {
    try {
        if (!token.value) return 

        await $fetch(`${apiBase}/api/settings/status`, {
            headers: { 'Authorization': `Bearer ${token.value}` }
        }).then(res => {
            if (!res.has_trakt_key) showTraktModal.value = true
        })

        // Initial load is now managed purely by resetAndLoad to avoid race conditions
        await resetAndLoad()
    } catch (e) {
        console.error(e)
    }
}

const resetAndLoad = async () => {
    if (isLoadingMore.value && items.value.length === 0) return // Already resetting

    isLoadingMore.value = true
    page.value = 1
    items.value = []
    hasMore.value = true
    finished.value = false
    
    // Immediate scroll reset to prevent infinite scroll trigger
    if (scrollEl.value) {
        scrollEl.value.scrollTop = 0
    }
    
    await loadPage(false)
}

// State for Infinite Scroll
const infiniteScrollTrigger = ref<HTMLElement | null>(null)
let infiniteScrollObserver: IntersectionObserver | null = null

// Cache
const itemsCache = useItemsCache()

const loadPage = async (append: boolean = false) => {
    // If not appending, we are doing a reset load which already set isLoadingMore to true
    // If appending, check if we are already loading or have no more items
    if (append && (isLoadingMore.value || !hasMore.value)) return
    
    // Explicitly lock before any async calls
    isLoadingMore.value = true
    
    if (append) {
        page.value++
    }

    try {
        if (!token.value) return

        let limit = SUBSEQUENT_LIMIT
        let offset = 0
        
        if (page.value === 1) {
            limit = INITIAL_LIMIT
            offset = 0
        } else {
            limit = SUBSEQUENT_LIMIT
            // Offset = Initial items + (previous subsequent pages * subsequent limit)
            offset = INITIAL_LIMIT + (page.value - 2) * SUBSEQUENT_LIMIT
        }

        const typeParam = filterType.value ? `&type=${filterType.value}` : ''
        const searchParam = searchQuery.value ? `&search=${encodeURIComponent(searchQuery.value)}` : ''
        
        // Dynamic Sort
        const [field, order] = sortOption.value.split(':')
        const sortParam = `&sort_by=${field}&order=${order}`
        
        // Construct cache key based on params
        const cacheFilters = `${typeParam}${searchParam}${sortParam}`
        
        // 1. Try Cache
        const cached = itemsCache.getCached(page.value, limit, cacheFilters)
        let dataToUse = null
        let needsFetch = true
        
        if (cached) {
            if (!cached.isStale) {
                // Fresh cache: Use immediately, skip fetch
                console.log(`✨ Using fresh cache for page ${page.value}`)
                dataToUse = cached.data
                needsFetch = false
            } else {
                // Stale cache: Use immediately, but trigger background fetch
                console.log(`⚡ Using stale cache for page ${page.value}, refreshing in background...`)
                dataToUse = cached.data
                needsFetch = true // Trigger fetch in background
            }
        }
        
        // Helper to process response data
        const processResponse = (response: any) => {
            const newItems = Array.isArray(response) ? response : (response.items || [])
            
            if (!Array.isArray(response) && response.total !== undefined) {
                 totalItems.value = response.total
                 hasMore.value = response.has_more
            } else {
                 hasMore.value = newItems.length >= limit
            }

            if (append) {
                // De-duplicate items based on ID to be safe
                const existingIds = new Set(items.value.map(i => i.id))
                const uniqueNewItems = newItems.filter((i: any) => !existingIds.has(i.id))
                items.value = [...items.value, ...uniqueNewItems]
            } else {
                items.value = newItems
                if (scrollEl.value) scrollEl.value.scrollTop = 0
            }

            if (newItems.length === 0) {
                hasMore.value = false
                finished.value = true
            }
        }

        // Apply cached data if available
        if (dataToUse) {
            processResponse(dataToUse)
            await nextTick() // Update DOM
            isLoadingMore.value = false // Release lock early for UI (background fetch continues)
            isLoading.value = false
        }
        
        // 2. Fetch from API (Foreground or Background)
        if (needsFetch) {
            const url = `${apiBase}/api/library/items?limit=${limit}&offset=${offset}${typeParam}${searchParam}${sortParam}`
            
            const fetchPromise = $fetch<any>(url, {
                headers: { 'Authorization': `Bearer ${token.value}` }
            }).then(response => {
                // Update Cache
                itemsCache.setCache(page.value, limit, cacheFilters, response)
                
                // If we didn't use cache, process this response now
                if (!dataToUse) {
                    processResponse(response)
                }
            })
            
            if (!dataToUse) {
                // Foreground fetch: wait for it
                await fetchPromise
            } else {
                // Background fetch: let it run, we already unlocked UI
            }
        }
        
    } catch (e) {
        console.error("Load Error", e)
    } finally {
        // Ensure lock is released if we did a foreground fetch or errored
        if (isLoadingMore.value) {
            await nextTick()
            isLoadingMore.value = false
            isLoading.value = false
        }
    }
}

const loadMore = () => {
    if (!hasMore.value || isLoadingMore.value) return
    loadPage(true)
}

const triggerScan = async () => {
    scanning.value = true
    try {
        if (!token.value) return
        await $fetch(`${apiBase}/api/library/scan`, {
             method: 'POST',
             headers: { 'Authorization': `Bearer ${token.value}` }
        })
        
        toast.add({ title: 'Scan Started', description: 'Scanning items and fetching metadata in background.', color: 'green' })
        
        // Refresh current view
        setTimeout(() => resetAndLoad(), 2000)
    } catch(e) {
        toast.add({ title: 'Scan Failed', color: 'red' })
    } finally {
        scanning.value = false
    }
}

// Helpers
const openExternal = (url: string) => {
    if (url) window.open(url, '_blank')
}

const openInTrakt = (item: any) => {
  if (!item.tmdb_id) return
  
  // Trakt search URL using TMDB ID
  const mediaType = item.media_type === 'tv' ? 'show' : 'movie'
  const traktUrl = `https://trakt.tv/search/tmdb/${item.tmdb_id}?id_type=${mediaType}`
  
  window.open(traktUrl, '_blank')
}

const saveTraktKey = async () => {
    if (!traktKeyInput.value) return
    
    savingKey.value = true
    try {
        if (!token.value) return
        await $fetch(`${apiBase}/api/settings`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token.value}`,
                'Content-Type': 'application/json' 
            },
            body: { trakt_client_id: traktKeyInput.value }
        })
        
        showTraktModal.value = false
        toast.add({ title: 'Settings Saved', color: 'green' })
        triggerScan() 
    } catch (e) {
        toast.add({ title: 'Failed to save settings', color: 'red' })
    } finally {
        savingKey.value = false
    }
}

const handleCopy = async (item: any) => {
    resetWizard()
    
    setSource(item.full_path, {
        name: item.title,
        path: item.full_path,
        size: item.size_bytes || 0,
        size_formatted: item.size_formatted || ''
    })
    
    // Auto-select destination from settings
    try {
        const settings = await getSettings()
        const defaultPath = item.media_type === 'movie' ? settings.default_movies_path : settings.default_series_path
        if (defaultPath) {
            setDestination(defaultPath)
        }
    } catch (e) {
        console.error("Failed to load settings for defaults", e)
    }
    
    goToStep(3)
    navigateTo('/copy-wizard')
}

const getTechTags = (item: any) => {
    if (!item.source_metadata) return []
    try {
        const meta = typeof item.source_metadata === 'string' 
            ? JSON.parse(item.source_metadata) 
            : item.source_metadata
            
        const tags = []
        
        // --- NEW METADATA TAGS ---

        // 1. Season Info (TV Only - High Priority)
        // Check for Season Pack or Multi-Season
        if (meta.is_season_pack) {
             const s = meta.season_range || (meta.season ? `S${String(meta.season).padStart(2, '0')}` : 'Season Pack')
             tags.push({ label: s, color: 'bg-[var(--status-warning)]/20 text-[var(--status-warning)] border border-[var(--status-warning)]/30' })
        } else if (meta.is_multi_season) {
             const s = meta.season_range || `S${meta.season}-S${meta.season_end}`
             tags.push({ label: s, color: 'bg-[var(--status-warning)]/20 text-[var(--status-warning)] border border-[var(--status-warning)]/30' })
        } else if (item.media_type === 'tv') {
             if (meta.season && meta.episode) {
                 // Standard SxxExx
                 const s = `S${String(meta.season).padStart(2, '0')}E${String(meta.episode).padStart(2, '0')}`
                 tags.push({ label: s, color: 'bg-white/10 text-[var(--win-text-muted)] border border-white/10' })
             } else if (meta.episode) {
                 // Episode Only (e.g. E01)
                 const s = `E${String(meta.episode).padStart(2, '0')}`
                 tags.push({ label: s, color: 'bg-white/10 text-[var(--win-text-muted)] border border-white/10' })
             }
        }

        // 2. Streaming Service (Cyan/Blue)
        if (meta.streaming_service && meta.streaming_service.length) {
            tags.push({ label: meta.streaming_service[0], color: 'bg-[var(--brand-3)]/20 text-[var(--brand-3)] border border-[var(--brand-3)]/30' })
        }

        // 3. Resolution (Purple) - Existing
        if (meta.resolution && meta.resolution.length) {
            tags.push({ label: meta.resolution[0], color: 'bg-[var(--brand-5)]/20 text-[var(--brand-5)] border border-[var(--brand-5)]/30' })
        }
        
        // 4. Quality Modifier (Pink)
        if (meta.quality_modifier && meta.quality_modifier.length) {
            tags.push({ label: meta.quality_modifier[0], color: 'bg-[var(--brand-4)]/20 text-[var(--brand-4)] border border-[var(--brand-4)]/30' })
        }

        // 5. Audio Modifier (Orange)
        if (meta.audio_modifier && meta.audio_modifier.length) {
            tags.push({ label: meta.audio_modifier[0], color: 'bg-[var(--brand-2)]/20 text-[var(--brand-2)] border border-[var(--brand-2)]/30' })
        }

        // 6. Source (Blue) - Existing
        if (meta.source && meta.source.length) {
            tags.push({ label: meta.source[0], color: 'bg-[var(--brand-1)]/20 text-[var(--brand-1)] border border-[var(--brand-1)]/30' })
        }
        
        // 7. Codec (Gray) - Existing
        if (meta.codec && meta.codec.length) {
            tags.push({ label: meta.codec[0], color: 'bg-gray-500/20 text-gray-300 border border-gray-500/30' })
        }

        // 8. Release Group (Green) - Low Priority (End)
        if (meta.release_group) {
             tags.push({ label: meta.release_group, color: 'bg-green-500/20 text-green-300 border border-green-500/30' })
        }
        
        return tags
    } catch (e) {
        return []
    }
}

// Watchers
watch(filterType, (newVal, oldVal) => {
    if (newVal !== oldVal) {
        resetAndLoad()
    }
})

// Debounced search watcher
let searchTimeout: any = null
watch(searchQuery, () => {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
        resetAndLoad()
    }, 400) // 400ms debounce
})

// Sort option watcher
watch(sortOption, () => {
    resetAndLoad()
})

// Lifecycle
onMounted(() => {
    setup()
    
    // Setup manual IntersectionObserver for robustness
    if (process.client) {
        nextTick(() => {
            setupInfiniteScroll()
        })
    }
})

onUnmounted(() => {
    if (infiniteScrollObserver) {
        infiniteScrollObserver.disconnect()
    }
})

const setupInfiniteScroll = () => {
  if (!process.client || !infiniteScrollTrigger.value) return
  
  // Clean up existing observer
  if (infiniteScrollObserver) {
    infiniteScrollObserver.disconnect()
  }
  
  // Create new observer
  infiniteScrollObserver = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      // When trigger element becomes visible and we have more pages
      if (entry.isIntersecting && hasMore.value && !isLoadingMore.value && !isLoading.value) {
        console.log('🔄 Infinite scroll triggered, loading next page...')
        loadMore()
      }
    },
    {
      root: null,              // viewport
      rootMargin: '200px',     // Start loading 200px BEFORE reaching trigger
      threshold: 0.1           // Trigger when 10% visible
    }
  )
  
  infiniteScrollObserver.observe(infiniteScrollTrigger.value)
}
</script>
