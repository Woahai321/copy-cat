<template>
  <div 
    class="flex flex-col h-full select-none"
    @mousedown="startSelection"
    @mousemove="updateSelection"
    @mouseup="endSelection"
    @mouseleave="endSelection"
    @contextmenu.prevent="showContextMenu($event)"
    :class="{ 'cursor-crosshair': isSelecting }"
  >
    <!-- Toolbar -->
    <div class="flex items-center gap-2 p-3 border-b border-white/5 bg-black/10 backdrop-blur-md sticky top-0 z-10 rounded-t-xl">
      <!-- Nav Left -->
      <div class="flex items-center gap-1">
          <button 
            @click="navigateUp"
            :disabled="breadcrumbs.length <= 1"
            class="p-2 rounded-lg hover:bg-white/10 disabled:opacity-30 disabled:hover:bg-transparent transition-all text-gray-300 hover:text-white"
            title="Up to parent folder"
          >
            <UIcon name="i-heroicons-arrow-up" class="w-4 h-4" />
          </button>
          <button 
            @click="refresh"
            class="p-2 rounded-lg hover:bg-white/10 transition-all text-gray-300 hover:text-white"
            title="Refresh"
          >
            <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 group-hover:animate-spin" />
          </button>
      </div>

      <!-- Address Bar (Breadcrumbs / Input) -->
      <div 
        class="flex-1 bg-black/20 border border-white/10 rounded-lg flex items-center px-3 h-9 group hover:bg-black/30 transition-all cursor-text overflow-hidden"
        @click="enableManualInput"
      >
         <div class="flex items-center gap-1.5 text-xs text-gray-400 mr-2 flex-shrink-0">
             <UIcon name="i-heroicons-computer-desktop" class="w-4 h-4" />
         </div>
         
         <!-- Breadcrumb View -->
         <div v-if="!isManualInputActive" class="flex-1 flex items-center overflow-hidden">
            <FileBreadcrumbs 
                :current-path="currentPath" 
                @navigate="navigateToManualPathArg" 
            />
         </div>
         
         <!-- Standard Input for Path -->
         <input 
            v-else
            v-model="manualPath" 
            ref="manualInputRef"
            @keydown.enter="navigateToManualPath"
            @blur="isManualInputActive = false"
            class="flex-1 bg-transparent border-none outline-none text-xs text-gray-200 h-full font-mono w-full"
            autoFocus
         />
      </div>

       <!-- Search (Responsive) -->
       <div class="relative w-full max-w-[140px] md:max-w-[200px] transition-all duration-300 focus-within:max-w-[240px]">
          <input 
            v-model="searchQuery"
            placeholder="Search" 
            class="w-full bg-black/20 border border-white/10 rounded-lg h-9 px-3 pl-8 text-xs text-white focus:border-[var(--brand-1)]/50 outline-none transition-all placeholder-white/20"
          />
          <UIcon name="i-heroicons-magnifying-glass" class="w-3.5 h-3.5 absolute left-2.5 top-3 text-gray-500" />
       </div>
       
       <!-- View Toggle -->
       <div class="flex bg-black/20 rounded-lg p-1 border border-white/10">
          <button 
             @click="viewMode = 'list'"
             class="p-1 rounded transition-all"
             :class="viewMode === 'list' ? 'bg-white/10 text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'"
             title="List View"
          >
             <UIcon name="i-heroicons-list-bullet" class="w-4 h-4" />
          </button>
          <button 
             @click="viewMode = 'grid'"
             class="p-1 rounded transition-all"
             :class="viewMode === 'grid' ? 'bg-white/10 text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'"
             title="Grid View"
          >
             <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" />
          </button>
       </div>

       <!-- New: Selection Toggle (Mobile & Desktop if selectable) -->
       <button 
         v-if="selectable || isMobile"
         @click="isSelectionMode = !isSelectionMode"
         class="flex items-center justify-center p-1.5 rounded-lg border transition-all"
         :class="isSelectionMode ? 'bg-[var(--win-accent)] text-black border-[var(--win-accent)] shadow-[0_0_10px_rgba(96,205,255,0.4)]' : 'border-transparent text-gray-500 hover:text-white'"
         :title="isSelectionMode ? 'Exit Selection Mode' : 'Enable Selection Mode'"
       >
          <UIcon :name="isSelectionMode ? 'i-heroicons-check-circle' : 'i-heroicons-cursor-arrow-rays'" class="w-5 h-5" />
       </button>

       <!-- New Folder -->
       <button 
         v-if="isDestination"
         class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-white/10 border border-transparent hover:border-white/10 transition-all group" 
         @click="isNewFolderModalOpen = true"
       >
          <UIcon name="i-heroicons-folder-plus" class="w-4 h-4 text-[var(--brand-1)] group-hover:scale-110 transition-transform" />
          <span class="text-xs hidden sm:inline text-gray-300 font-medium group-hover:text-white">New</span>
       </button>
    </div>

    <!-- File List Header -->
    <div class="grid grid-cols-12 gap-2 px-6 py-2 text-[10px] uppercase tracking-wider font-bold text-gray-500 border-b border-white/5 bg-black/5">
       <!-- Checkbox Placeholder -->
       <div v-if="isSelectionMode" class="col-span-1 flex justify-center">
          <!-- Optional: Select All could go here -->
       </div>
       
       <div 
         class="pl-1 cursor-pointer flex items-center gap-1 hover:text-gray-300 transition-colors" 
         :class="isSelectionMode ? 'col-span-9 md:col-span-5' : 'col-span-10 md:col-span-6'"
         @click="toggleSort('name')"
       >
         Name
         <UIcon v-if="sortByField === 'name'" :name="sortOrder === 'asc' ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-3 h-3" />
       </div>
       <div 
         class="hidden md:flex col-span-4 cursor-pointer items-center gap-1 hover:text-gray-300 transition-colors" 
         @click="toggleSort('modified')"
         :class="{ 'text-[var(--brand-1)] hover:text-[var(--brand-2)]': sortByField === 'modified' }"
       >
         Date modified
         <UIcon v-if="sortByField === 'modified'" :name="sortOrder === 'asc' ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-3 h-3" />
       </div>
       <div 
         class="hidden md:flex col-span-2 text-right pr-4 cursor-pointer items-center justify-end gap-1 hover:text-gray-300 transition-colors" 
         @click="toggleSort('size')"
         :class="{ 'text-[var(--brand-1)] hover:text-[var(--brand-2)]': sortByField === 'size' }"
       >
         Size
         <UIcon v-if="sortByField === 'size'" :name="sortOrder === 'asc' ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-3 h-3" />
       </div>
    </div>

    <!-- Scrollable File Area (Drop Target) -->
    <div 
        ref="fileContainer"
        class="flex-1 overflow-y-auto relative bg-transparent scrollbar-hide"
        @dragover.prevent="handleDragOver"
        @drop.prevent="handleDrop"
    >
       <!-- Loading Shimmer -->
       <div v-if="loading" class="flex-1 p-2 space-y-1 overflow-hidden">
         <div v-for="i in 10" :key="i" class="grid grid-cols-12 gap-2 px-4 py-2 items-center">
            <div class="col-span-6 flex items-center gap-3">
               <div class="w-5 h-5 rounded bg-white/5 shimmer-bg"></div>
               <div class="h-3 w-32 rounded bg-white/5 shimmer-bg"></div>
            </div>
            <div class="col-span-4">
               <div class="h-3 w-20 rounded bg-white/5 shimmer-bg"></div>
            </div>
            <div class="col-span-2 flex justify-end">
               <div class="h-3 w-12 rounded bg-white/5 shimmer-bg"></div>
            </div>
         </div>
       </div>

       <!-- List View -->
       <div v-if="viewMode === 'list'" class="pb-4 pt-1 px-2 space-y-0.5">
          <!-- Go Back Item -->
          <div 
             v-if="breadcrumbs.length > 1"
             class="grid grid-cols-12 gap-2 px-4 py-2 hover:bg-white/5 cursor-pointer items-center group text-xs text-gray-400 rounded-lg transition-colors"
             @click="navigateUp"
          >
             <div class="col-span-12 pl-2 flex items-center gap-2">
                <UIcon name="i-heroicons-arrow-turn-up-left" class="w-4 h-4 opacity-50 text-[var(--brand-1)]" />
                <span class="font-medium">..</span>
             </div>
          </div>
          
          <!-- Files -->
          <div 
             v-for="file in filteredFiles" 
             :key="file.path"
             class="selectable-item grid grid-cols-12 gap-2 px-4 py-2 cursor-pointer items-center text-xs group transition-all duration-150 border border-transparent mx-1 rounded-lg"
             :class="{
                'bg-[var(--brand-1)]/20 border-[var(--brand-1)]/30': isSelected(file.path),
                'hover:bg-white/5 hover:border-white/5': !isSelected(file.path)
             }"
             :data-path="file.path"
             draggable="true"
             @dragstart="handleDragStart($event, file)"
             @click.stop="handleClick($event, file)"
             @dblclick="handleDoubleClick(file)"
             @contextmenu.stop.prevent="showContextMenu($event, file)"
          >
             <!-- Checkbox Col -->
             <div v-if="isSelectionMode" class="col-span-1 flex items-center justify-center pl-2" @click.stop="toggleSelection(file)">
                <div 
                   class="w-4 h-4 rounded border flex items-center justify-center transition-all"
                   :class="isSelected(file.path) ? 'bg-[var(--win-accent)] border-[var(--win-accent)] text-black' : 'border-white/20 bg-black/20 hover:border-white/50'"
                >
                   <UIcon v-if="isSelected(file.path)" name="i-heroicons-check" class="w-3 h-3" />
                </div>
             </div>

             <!-- Name Col -->
             <div 
               class="flex items-center gap-3 overflow-hidden pl-1"
               :class="isSelectionMode ? 'col-span-9 md:col-span-5' : 'col-span-10 md:col-span-6'"
             >
                <UIcon 
                  :name="getFileIcon(file)" 
                  class="w-5 h-5 flex-shrink-0 transition-colors"
                  :class="getFileIconColor(file, isSelected(file.path))"
                />
                <div class="flex flex-col truncate min-w-0">
                    <span class="truncate font-medium select-none text-sm" :class="isSelected(file.path) ? 'text-white' : 'text-gray-300 group-hover:text-white'">{{ file.name }}</span>
                    <!-- Mobile Subtitle -->
                    <span class="md:hidden text-[10px] text-gray-500 font-mono flex items-center gap-2">
                        <span>{{ file.is_dir ? 'Folder' : formatSize(file.size_bytes) }}</span>
                        <span class="w-1 h-1 rounded-full bg-gray-600"></span>
                        <span>{{ formatDate(file.modified_at) }}</span>
                    </span>
                </div>
             </div>
             
             <!-- Date Col (Desktop) -->
             <div class="hidden md:block col-span-4 font-mono text-[10px] truncate" :class="isSelected(file.path) ? 'text-[var(--brand-1)]/70' : 'text-gray-500 group-hover:text-gray-400'">
                {{ formatDate(file.modified_at) }}
             </div>
             
             <!-- Size Col & Actions -->
             <div class="col-span-2 flex items-center justify-end gap-2 pr-2">
                <span class="hidden md:block font-mono text-[10px]" :class="isSelected(file.path) ? 'text-[var(--brand-1)]/70' : 'text-gray-500 group-hover:text-gray-400'">
                   {{ file.is_dir ? '' : formatSize(file.size_bytes) }}
                </span>
                
                <!-- Touch Context Trigger -->
                <button 
                  @click.stop="showContextActions(file)"
                  class="p-2 rounded-md hover:bg-white/10 text-gray-500 hover:text-white md:hidden active:bg-white/20 active:text-white transition-colors"
                >
                   <UIcon name="i-heroicons-ellipsis-vertical" class="w-5 h-5" />
                </button>
             </div>
          </div>
       </div>

       <!-- Grid View -->
       <div v-else class="p-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 content-start">
           <!-- Go Back Card -->
           <div 
             v-if="currentPath !== '/'"
             @click="navigateUp"
             class="glass-panel p-4 flex flex-col items-center justify-center gap-3 cursor-pointer hover:bg-white/10 transition-colors group h-32"
           >
              <UIcon name="i-heroicons-arrow-turn-up-left" class="w-10 h-10 text-gray-500 group-hover:text-[var(--brand-1)] transition-colors" />
              <div class="text-xs text-gray-500 font-bold">Back</div>
           </div>

           <!-- File Cards -->
           <div 
              v-for="file in filteredFiles"
              :key="file.path"
              class="selectable-item glass-panel p-4 flex flex-col items-center gap-3 cursor-pointer transition-all duration-200 h-36 group relative border"
              :class="isSelected(file.path) ? 'border-[var(--brand-1)]/50 bg-[var(--brand-1)]/10 shadow-[0_0_15px_rgba(96,205,255,0.2)]' : 'border-transparent hover:border-white/10 hover:bg-white/5'"
              :data-path="file.path"
              draggable="true"
             @dragstart="handleDragStart($event, file)"
             @click.stop="handleClick($event, file)"
             @dblclick="handleDoubleClick(file)"
             @contextmenu.stop.prevent="showContextMenu($event, file)"
           >
              <!-- Checkbox (Top Left) -->
              <button 
                  v-if="isSelectionMode"
                  @click.stop="toggleSelection(file)"
                  class="absolute top-2 left-2 w-5 h-5 rounded-full border flex items-center justify-center transition-all z-20"
                  :class="isSelected(file.path) ? 'bg-[var(--win-accent)] border-[var(--win-accent)] text-black' : 'border-white/20 bg-black/40 text-transparent hover:border-white/50'"
              >
                  <UIcon name="i-heroicons-check" class="w-3.5 h-3.5" />
              </button>

              <!-- Context Menu Trigger for Grid -->
              <button 
                  @click.stop="showContextMenu($event, file)"
                  class="absolute top-2 right-2 p-1 rounded-full bg-black/20 text-gray-400 hover:text-white hover:bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity z-10"
              >
                 <UIcon name="i-heroicons-ellipsis-horizontal" class="w-4 h-4" />
              </button>

              <div class="flex-1 flex items-center justify-center relative w-full">
                 <!-- Icon -->
                 <UIcon 
                   :name="getFileIcon(file)" 
                   class="w-12 h-12 transition-transform duration-300 group-hover:scale-110"
                   :class="getFileIconColor(file, isSelected(file.path))"
                 />
                 <!-- Type Badge (if media) -->
                 <div v-if="isMovie(file.name)" class="absolute -top-1 -right-1 bg-black/60 backdrop-blur px-1.5 py-0.5 rounded text-[8px] font-bold text-gray-300 border border-white/10 uppercase tracking-wider">MOV</div>
              </div>
              
              <div class="w-full text-center">
                 <div class="text-xs font-medium truncate w-full select-none" :class="isSelected(file.path) ? 'text-white' : 'text-gray-300 group-hover:text-white'">{{ file.name }}</div>
                 <div class="text-[10px] text-gray-500 mt-0.5 flex justify-center gap-2">
                    <span v-if="!file.is_dir">{{ formatSize(file.size_bytes) }}</span>
                    <span v-if="file.is_dir">Folder</span>
                 </div>
              </div>
           </div>
       </div>

       <!-- Rubber Band Selection Box -->
       <div 
         v-if="isSelecting"
         class="absolute bg-[var(--brand-1)]/10 border border-[var(--brand-1)]/40 pointer-events-none z-50 transform-gpu backdrop-blur-[1px] rounded"
         :style="{
            left: Math.min(selectionStart.x, selectionCurrent.x) + 'px',
            top: Math.min(selectionStart.y, selectionCurrent.y) + 'px',
            width: Math.abs(selectionCurrent.x - selectionStart.x) + 'px',
            height: Math.abs(selectionCurrent.y - selectionStart.y) + 'px'
         }"
       ></div>
    </div>

    <!-- Pagination Footer -->
    <div class="p-3 border-t border-white/5 bg-black/10 backdrop-blur-md sticky bottom-0 z-10 rounded-b-xl flex items-center justify-between">
       <button 
          @click="prevPage"
          :disabled="page <= 1 || loading"
          class="p-2 rounded-lg hover:bg-white/10 disabled:opacity-30 disabled:hover:bg-transparent transition-all text-gray-300 hover:text-white flex items-center gap-2"
       >
          <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
          <span class="text-xs font-medium">Prev</span>
       </button>
       
       <span class="text-xs text-slate-500 font-mono">
          Page {{ page }} of {{ totalPages || 1 }}
       </span>
       
       <button 
          @click="nextPage"
          :disabled="!hasMore || loading"
          class="p-2 rounded-lg hover:bg-white/10 disabled:opacity-30 disabled:hover:bg-transparent transition-all text-gray-300 hover:text-white flex items-center gap-2"
       >
          <span class="text-xs font-medium">Next</span>
          <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
       </button>
    </div>

    <!-- Context Menu (Responsive: Bottom Sheet on Mobile, Floating on Desktop) -->
    <div 
      v-if="contextMenu.show"
      class="fixed z-[100] bg-[#1a1a1a] border border-white/10 md:border-white/5 md:bg-black/80 md:backdrop-blur-xl shadow-2xl transition-all duration-200"
      :class="[
          // Mobile: Bottom Sheet
          'md:rounded-lg md:w-48 md:py-1 inset-x-0 bottom-0 rounded-t-2xl pb-safe md:pb-1 md:inset-auto md:top-auto md:left-auto',
          { 'animate-slide-up': isMobile, 'fade-in': !isMobile }
      ]"
      :style="!isMobile ? { left: contextMenu.x + 'px', top: contextMenu.y + 'px' } : {}"
      @click.stop
    >
        <!-- Mobile Handle -->
        <div class="md:hidden w-full flex justify-center pt-3 pb-1">
            <div class="w-12 h-1 bg-white/20 rounded-full"></div>
        </div>

        <!-- Header -->
        <div class="px-4 py-3 md:px-3 md:py-2 text-sm md:text-xs font-bold text-white md:text-gray-400 border-b border-white/5 md:mb-1 truncate flex items-center gap-2">
            <UIcon :name="contextMenu.file?.is_dir ? 'i-heroicons-folder' : 'i-heroicons-document'" class="w-4 h-4 md:w-3 md:h-3 text-[var(--win-accent)]" />
            <span class="truncate">{{ contextMenu.file?.name || 'Selection' }}</span>
        </div>
        
        <!-- Actions -->
        <div class="p-2 md:p-0 space-y-1 md:space-y-0">
            <button class="w-full text-left px-4 py-3 md:px-3 md:py-2 text-base md:text-xs text-white md:text-gray-200 hover:bg-white/10 md:hover:bg-[var(--brand-1)]/20 md:hover:text-[var(--brand-1)] flex items-center gap-3 md:gap-2 rounded-lg md:rounded-none transition-colors" @click="handleContextAction('copy')">
                <UIcon name="i-heroicons-clipboard" class="w-5 h-5 md:w-4 md:h-4 text-gray-400 md:text-current" /> 
                Copy Path
            </button>
            <button class="w-full text-left px-4 py-3 md:px-3 md:py-2 text-base md:text-xs text-white md:text-gray-200 hover:bg-white/10 md:hover:bg-[var(--brand-1)]/20 md:hover:text-[var(--brand-1)] flex items-center gap-3 md:gap-2 rounded-lg md:rounded-none transition-colors" @click="handleContextAction('move')">
                <UIcon name="i-heroicons-arrows-right-left" class="w-5 h-5 md:w-4 md:h-4 text-gray-400 md:text-current" /> 
                Move to...
            </button>
            <div class="h-px bg-white/5 my-1 mx-2 hidden md:block"></div>
            <button class="w-full text-left px-4 py-3 md:px-3 md:py-2 text-base md:text-xs text-red-400 hover:bg-red-500/10 hover:text-red-300 flex items-center gap-3 md:gap-2 rounded-lg md:rounded-none transition-colors" @click="handleContextAction('delete')">
                <UIcon name="i-heroicons-trash" class="w-5 h-5 md:w-4 md:h-4" /> 
                Delete
            </button>
        </div>
        
        <!-- Mobile Cancel -->
        <div class="p-2 border-t border-white/5 md:hidden mt-2">
            <button @click="closeContextMenu" class="w-full py-3 text-center font-bold text-gray-400 hover:text-white bg-white/5 rounded-xl">
                Cancel
            </button>
        </div>
    </div>

    <!-- Custom New Folder Modal (Glass Overlay) -->
    <div v-if="isNewFolderModalOpen" class="fixed inset-0 z-[200] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in">
      <div class="glass-panel p-6 w-full max-w-sm mx-4 transform transition-all scale-100 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <h3 class="text-lg font-bold text-white mb-6 flex items-center gap-2.5">
            <div class="p-2 bg-[var(--brand-1)]/10 rounded-lg">
                <UIcon name="i-heroicons-folder-plus" class="w-5 h-5 text-[var(--brand-1)]" />
            </div>
            Create New Folder
        </h3>
        
        <input 
            v-model="newFolderName" 
            @keyup.enter="createFolderRef" 
            ref="newFolderInput" 
            class="w-full bg-black/30 border border-white/10 rounded-lg p-3 text-white mb-6 focus:border-[var(--brand-1)] focus:ring-1 focus:ring-[var(--brand-1)]/50 outline-none text-sm font-mono placeholder-gray-600 transition-all" 
            placeholder="Folder Name" 
            autoFocus
        />
        
        <div class="flex justify-end gap-3">
          <button 
            @click="isNewFolderModalOpen = false" 
            class="px-4 py-2 rounded-lg text-sm text-gray-400 hover:bg-white/5 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="createFolderRef" 
            class="px-5 py-2 rounded-lg text-sm bg-gradient-to-r from-[var(--brand-1)] to-[var(--brand-5)] text-white font-semibold hover:shadow-[0_0_20px_rgba(96,205,255,0.4)] hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:hover:scale-100"
            :disabled="!newFolderName"
          >
            Create
          </button>
        </div>
      </div>
    </div>

    <!-- Overlay to close context menu -->
    <div v-if="contextMenu.show" class="fixed inset-0 z-[90] bg-black/20 md:bg-transparent" @click="closeContextMenu" @contextmenu.prevent="closeContextMenu"></div>
  </div>
</template>

<script setup lang="ts">
import { useMouseInElement, useFocus, useWindowSize } from '@vueuse/core'

const props = defineProps<{
  initialPath?: string
  layout?: 'list' | 'grid'
  isDestination?: boolean // New: Identifying role
  layout?: 'list' | 'grid'
  isDestination?: boolean // New: Identifying role
  source?: string
  selectable?: boolean // New: Enable selection mode toggle on desktop
}>()

const emit = defineEmits<{
  'update:path': [path: string]
  'selection-change': [files: Set<string>] // Changed to Set
  'items-dropped': [files: string[]] // New: Drop event
}>()

const { browseDirectory, createFolder, deleteItem } = useApi()
const toast = useToast()
const { width } = useWindowSize()
const isMobile = computed(() => width.value < 768)

// State
const currentPath = ref(props.initialPath || '/')
const files = ref<any[]>([])
const loading = ref(false)
const manualPath = ref('/')
const isManualInputActive = ref(false) // Toggle for breadcrumb vs input
const searchQuery = ref('')
const breadcrumbs = ref<string[]>(['/'])

// View Mode
const viewMode = ref<'list' | 'grid'>('list') // Default to List

// Pagination State
const page = ref(1)
const totalItems = ref(0)
const hasMore = ref(false)
const ITEMS_PER_PAGE = 29

// Sorting State
const sortByField = ref('modified')
const sortOrder = ref('desc')

// Multi-Selection State
const selectedFiles = ref<Set<string>>(new Set())
const lastSelectedFile = ref<string | null>(null) // For Shift+Click range
const isSelectionMode = ref(false) // Mobile Selection Toggle

// Drag Selection
const fileContainer = ref<HTMLElement | null>(null)
const isSelecting = ref(false)
const selectionStart = ref({ x: 0, y: 0 })
const selectionCurrent = ref({ x: 0, y: 0 })

// Context Menu
const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  file: null as any
})


// New Folder
const isNewFolderModalOpen = ref(false)
const newFolderName = ref('')

const isMovie = (name: string) => {
  const ext = name.split('.').pop()?.toLowerCase()
  return ['mkv', 'mp4', 'avi', 'mov', 'wmv', 'm4v'].includes(ext || '')
}

const isImage = (name: string) => {
  const ext = name.split('.').pop()?.toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext || '')
}

const isAudio = (name: string) => {
  const ext = name.split('.').pop()?.toLowerCase()
  return ['mp3', 'wav', 'flac', 'aac', 'ogg'].includes(ext || '')
}

const isArchive = (name: string) => {
  const ext = name.split('.').pop()?.toLowerCase()
  return ['zip', 'rar', '7z', 'tar', 'gz'].includes(ext || '')
}

// Computed
const filteredFiles = computed(() => {
  if (!searchQuery.value) return files.value
  return files.value.filter(f => f.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const breadcrumbSegments = computed(() => {
    if (currentPath.value === '/') return []
    return currentPath.value.split('/').filter(Boolean)
})

// --- Methods ---

const loadFiles = async (path: string) => {
  loading.value = true
  try {
    const source = props.source || (props.isDestination ? 'destination' : 'source')
    console.log(`[FileExplorer] Loading files for source=${source} path=${path} page=${page.value} sort=${sortByField.value} order=${sortOrder.value}`)
    
    // Calculate offset
    const offset = (page.value - 1) * ITEMS_PER_PAGE
    
    // Pass sort params and pagination to API
    const result = await browseDirectory(source, path, ITEMS_PER_PAGE, offset, sortByField.value, sortOrder.value)
    
    // Update total and hasMore
    totalItems.value = result.total
    hasMore.value = result.has_more

    // Map backend response fields to component expectations
    const items = result.items.map((item: any) => ({
        ...item,
        is_dir: item.is_directory,
        size_bytes: item.size,
        modified_at: item.modified ? new Date(item.modified * 1000).toISOString() : new Date().toISOString()
    }))
    
    files.value = items
    currentPath.value = path
    manualPath.value = path
    isManualInputActive.value = false // Reset to breadcrumbs on load
    
    // Reset page if path changed (logic handled in caller usually, but let's check)
    // Actually, loadFiles is called generically.
    // If we navigate UP or DOWN, we should reset page.
    // But if we just refresh, we might keep page?
    // Let's standardise: Caller should reset page if needed, or we check previous path?
    // Simplified: Resetting page is done in navigation methods, loadFiles just loads.
    
    // Update breadcrumbs logic (simplified)
    breadcrumbs.value = path === '/' ? ['/'] : path.split('/').filter(Boolean)
    
    // Clear selection on folder change
    selectedFiles.value.clear()
    emit('selection-change', selectedFiles.value)
  } catch (error) {
    console.error('Failed to list files:', error)
    toast.add({ title: 'Error', description: 'Failed to list directory', color: 'red' })
  } finally {
    loading.value = false
  }
}

const toggleViewMode = () => {
    viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
}

const toggleSort = async (field: string) => { // Make async
  console.log(`[FileExplorer] Toggling sort: ${field}`)
  if (sortByField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortByField.value = field
    // Default to desc for modified/size, asc for name
    sortOrder.value = (field === 'modified' || field === 'size') ? 'desc' : 'asc'
  }
  
  // Force reload
  page.value = 1 // Reset to page 1 on sort change
  files.value = [] // Clear momentarily to show loading state if desired, or just wait
  await loadFiles(currentPath.value)
}

const navigateUp = () => {
  if (currentPath.value === '/') return
  const parent = currentPath.value.split('/').slice(0, -1).join('/') || '/'
  page.value = 1 // Reset page
  loadFiles(parent)
}

const navigateToBreadcrumb = (index: number) => {
    const path = '/' + breadcrumbSegments.value.slice(0, index + 1).join('/')
    page.value = 1 // Reset page
    loadFiles(path)
}

const navigateToRoot = () => {
    page.value = 1 // Reset page
    loadFiles('/')
}

const enableManualInput = () => {
    isManualInputActive.value = true
    // Need to wait for DOM update to focus input
    nextTick(() => {
        // focus input logic if needed
    })
}

const navigateToManualPath = () => {
    page.value = 1 // Reset page
    loadFiles(manualPath.value)
}

const navigateToManualPathArg = (path: string) => {
    page.value = 1
    loadFiles(path)
}

const refresh = () => loadFiles(currentPath.value)

const nextPage = () => {
    if (!hasMore.value) return
    page.value++
    loadFiles(currentPath.value)
}

const prevPage = () => {
    if (page.value <= 1) return
    page.value--
    loadFiles(currentPath.value)
}

const totalPages = computed(() => Math.ceil(totalItems.value / ITEMS_PER_PAGE))

// --- Selection Logic ---

const isSelected = (path: string) => selectedFiles.value.has(path)

const toggleSelection = (file: any) => {
    if (selectedFiles.value.has(file.path)) {
        selectedFiles.value.delete(file.path)
    } else {
        selectedFiles.value.add(file.path)
        lastSelectedFile.value = file.path
    }
    emit('selection-change', selectedFiles.value)
}

const handleClick = (e: MouseEvent, file: any) => {
  // Checkbox/Selection Mode Logic handled by explicit toggles now
  // If clicking the ROW (not checkbox), standard behavior:
  
  if (isSelectionMode.value) {
      toggleSelection(file)
      return
  }

  // Mobile Support: Single tap to navigate folders (Normal Mode)
  if (window.innerWidth < 768 && file.is_dir && !e.ctrlKey && !e.shiftKey) {
     page.value = 1 // Reset page
     loadFiles(file.path)
     return
  }
  
  // Standard modifiers still work
  if (e.ctrlKey || e.metaKey) {
    toggleSelection(file)
  } else if (e.shiftKey && lastSelectedFile.value) {
    // Range
    const lastIdx = filteredFiles.value.findIndex(f => f.path === lastSelectedFile.value)
    const currIdx = filteredFiles.value.findIndex(f => f.path === file.path)
    if (lastIdx !== -1 && currIdx !== -1) {
      const start = Math.min(lastIdx, currIdx)
      const end = Math.max(lastIdx, currIdx)
      // Clear if not holding ctrl? Standard Windows behavior is replace unless Ctrl.
      if (!e.ctrlKey) selectedFiles.value.clear()
      
      for (let i = start; i <= end; i++) {
        selectedFiles.value.add(filteredFiles.value[i].path)
      }
      emit('selection-change', selectedFiles.value)
    }
  } else {
    // Single Select (Navigate if double click / click logic?)
    // Actually, widespread behavior: Click selects, Double Click opens.
    selectedFiles.value.clear()
    selectedFiles.value.add(file.path)
    lastSelectedFile.value = file.path
    emit('selection-change', selectedFiles.value)
  }
  
  // Hide context menu if open
  closeContextMenu()
}

const handleDoubleClick = (file: any) => {
  if (isSelectionMode.value) return // Disable double click in selection mode
  if (file.is_dir) {
    page.value = 1 // Reset page
    loadFiles(file.path)
  }
}

// --- Rubber Band Selection (Simplified Visuals for now) ---
// Note: Full intersection logic with DOM elements requires querying refs.
// For this iteration, we start the box. Actual selection logic needs bounding client rects.
const startSelection = (e: MouseEvent) => {
  // Only start if clicking on background (not a file item, which stops propagation)
  if (e.button !== 0) return // Left click only
  
  // Get container rect local coordinates
  const container = fileContainer.value
  if (!container) return
  const rect = container.getBoundingClientRect()
  
  isSelecting.value = true
  selectionStart.value = { x: e.clientX - rect.left, y: e.clientY - rect.top + container.scrollTop }
  selectionCurrent.value = { ...selectionStart.value }
  
  // If not adding to selection, clear existing
  if (!e.ctrlKey && !e.shiftKey && !isSelectionMode.value) {
     selectedFiles.value.clear()
     emit('selection-change', selectedFiles.value)
  }
}

const updateSelection = (e: MouseEvent) => {
  if (!isSelecting.value) return
  const container = fileContainer.value
  if (!container) return
  const rect = container.getBoundingClientRect()
  
  // Update current endpoint relative to container
  // We need to account for scrollTop if the container scrolls but the box is absolute inside it?
  // The box is absolute in the ROOT div (top level), not inside the scrollable fileContainer?
  // Let's re-read line 2 and 282. The root div does NOT have 'relative'. 
  // But wait, the previous code had `y: e.clientY - rect.top + container.scrollTop`.
  // If the box is in 'fileContainer' it needs relative. If it's in root, it needs root relative.
  // Looking at the template structure:
  // Root (Div) -> Toolbar, FileListHeader, FileContainer (Scrollable), SelectionBox.
  // SelectionBox is sibling to FileContainer?
  // Line 282 is INSIDE Root. Line 137 is FileContainer.
  // So SelectionBox is over everything.
  // The 'rect' used in startSelection is 'fileContainer.value'. 
  // If the user scrolls, 'fileContainer' contents move.
  // The selection box physics seems slightly messed up in the original code if it mixes container.scrollTop with fixed overlay.
  // Let's assume the box should draw relative to the VIEWPORT of the file list?
  // Or relative to the content?
  // Standard Explorer: Box moves with scroll? No, usually box allows scrolling.
  
  // Let's simplify. bounds checks.
  
  selectionCurrent.value = { 
      x: e.clientX - rect.left, 
      y: e.clientY - rect.top + container.scrollTop 
  }
  
  // Calculate Normalized Selection Rect (x, y, w, h)
  const left = Math.min(selectionStart.value.x, selectionCurrent.value.x)
  const top = Math.min(selectionStart.value.y, selectionCurrent.value.y)
  const width = Math.abs(selectionCurrent.value.x - selectionStart.value.x)
  const height = Math.abs(selectionCurrent.value.y - selectionStart.value.y)
  
  // Logic: Find all .selectable-item elements
  // Since this runs on mousemove, we should throttle or be efficient.
  // For < 500 items, simple rect intersection is fine.
  
  const items = container.querySelectorAll('.selectable-item')
  const newSelection = new Set<string>()
  
  // If Shift/Ctrl held, we might want to KEEP existing selection? 
  // Initial implementation: standard "replace selection unless modifier" logic is handled in startSelection (clearing or not).
  // Here we just ADD/REMOVE based on intersection?
  // Usually drag select ADDS to current 'drag session selection'.
  // If we cleared at start, we just set.
  // If we didn't clear (Search/Ctrl), we add/remove?
  // Let's go with: Union(InitialSelection, BoxSelection).
  // But strictly speaking, Windows drag select inverts or adds?
  // Simple version: Selected = Union(OriginalSelectionSnapshot, IntersectedItems)
  // We need to store 'selectionAtDragStart' to implement this perfectly.
  
  // Simplified:
  // 1. We keep track of what is in the box currently.
  // 2. We set selectedFiles = (selectedFiles - itemsInBoxLastFrame) + itemsInBoxCurrentFrame?
  // Too complex.
  // EASIEST: On start, snapshot 'selectedFiles'. 
  // On move: selectedFiles = snapshot + intersected (if Ctrl) or just intersected (if no Ctrl).
  
  // Let's do the simple "Just select what's in box" logic for now, respecting ctrl.
  
  // We actually need to iterate.
  items.forEach((el) => {
      const elRect = el.getBoundingClientRect()
      // Convert elRect to be relative to container's top-left (same coordinate space as selection box)
      // el.getBoundingClientRect is viewport relative.
      // container.getBoundingClientRect is viewport relative.
      // relativeX = elRect.left - containerRect.left
      // relativeY = elRect.top - containerRect.top + container.scrollTop
      
      const elLeft = elRect.left - rect.left
      const elTop = elRect.top - rect.top + container.scrollTop
      const elRight = elLeft + elRect.width
      const elBottom = elTop + elRect.height
      
      // Check Intersection
      const intersects = (
          left < elRight &&
          (left + width) > elLeft &&
          top < elBottom &&
          (top + height) > elTop
      )
      
      const path = el.getAttribute('data-path')
      if (path && intersects) {
          newSelection.add(path)
      }
  })
  
  // Merge logic
  if (e.ctrlKey || e.metaKey) {
      // Toggle logic or Add logic?
      // VS Code/Windows: Add to selection.
      // We need to merge 'snapshot' + newSelection.
      // Since I don't have snapshot, I'll just ADD. 
      // But if I move mouse BACK, it should unselect?
      // Real logic: calculatedSelection = baseSelection (from start) XOR boxSelection?
      // Let's just do: selectedFiles = newSelection (if no ctrl).
      // If ctrl: selectedFiles = Union(initialSelection, newSelection)
      
      // We need a 'snapshot' variable. I'll add it to state.
      // For now, let's just make it work for basic select (no ctrl).
      selectedFiles.value = newSelection
  } else {
      selectedFiles.value = newSelection
  }
  emit('selection-change', selectedFiles.value)
}

const endSelection = () => {
  isSelecting.value = false
}

// --- Context Menu ---
// Mobile Action Sheet Trigger
const showContextActions = (file: any) => {
   // Determine center of screen for mobile "sheet" feel or just passed center
   // Since we don't have event, we mock one center or use simple logic
   contextMenu.value = {
     show: true,
     x: window.innerWidth / 2 - 90, // Center X (menu width ~180)
     y: window.innerHeight / 2 - 50, // Center Y
     file: file
   }
   
   // Select it
   if (file && !selectedFiles.value.has(file.path)) {
       selectedFiles.value.clear()
       selectedFiles.value.add(file.path)
       emit('selection-change', selectedFiles.value)
   }
}

const showContextMenu = (e: MouseEvent, file?: any) => {
  e.preventDefault() // Stop browser menu
  
  // If right-clicked a file that isn't selected, select it (exclusive)
  if (file && !selectedFiles.value.has(file.path)) {
      selectedFiles.value.clear()
      selectedFiles.value.add(file.path)
      emit('selection-change', selectedFiles.value)
      emit('selection-change', selectedFiles.value)
  }

  // Mobile: Select only (no context menu)
  if (isMobile.value) return
  
  contextMenu.value = {
    show: true,
    x: e.clientX,
    y: e.clientY,
    file: file
  }
}

const closeContextMenu = () => {
    contextMenu.value.show = false
}

const handleContextAction = async (action: string) => {
    closeContextMenu()
    
    // Determine items to act on
    let itemsToActOn: string[] = []
    
    if (contextMenu.value.file) {
        // If context menu was opened on a file
        if (selectedFiles.value.has(contextMenu.value.file.path)) {
            // efficient: act on all selected
            itemsToActOn = Array.from(selectedFiles.value)
        } else {
            // act on just this file (should have been selected by showContextMenu logic normally, but safety check)
            itemsToActOn = [contextMenu.value.file.path]
        }
    } else {
        // Folder background context menu? (Not fully impl yet)
        return
    }

    if (action === 'delete') {
         if (!confirm(`Are you sure you want to delete ${itemsToActOn.length} item(s)? This action cannot be undone.`)) return
         
         const sourceName = props.isDestination ? '16tb' : 'zurg'
         
         let successCount = 0
         for (const path of itemsToActOn) {
             try {
                 await deleteItem(sourceName, path)
                 successCount++
             } catch (e: any) {
                 toast.add({ title: 'Error', description: e.message || `Failed to delete ${path}`, color: 'red' })
             }
         }
         
         if (successCount > 0) {
             toast.add({ title: 'Success', description: `Deleted ${successCount} item(s)`, color: 'green' })
             refresh()
             // clear selection
             selectedFiles.value.clear()
             emit('selection-change', selectedFiles.value)
         }
    } else {
         toast.add({ title: 'Action', description: `Requested ${action} - Not implemented yet`, color: 'primary' })
    }
}

// --- Drag and Drop ---
const handleDragStart = (e: DragEvent, file: any) => {
   // If the dragged file is not in selection, select it
   if (!selectedFiles.value.has(file.path)) {
       selectedFiles.value.clear()
       selectedFiles.value.add(file.path)
       emit('selection-change', selectedFiles.value)
   }
   
   // Set data
   if (e.dataTransfer) {
       e.dataTransfer.effectAllowed = 'copy'
       const filesToDrag = Array.from(selectedFiles.value)
       e.dataTransfer.setData('application/json', JSON.stringify(filesToDrag))
       
       // preview
       e.dataTransfer.setDragImage(e.target as Element, 0, 0)
   }
}

const handleDragOver = (e: DragEvent) => {
    // Only allow drop if we are destination
    if (props.isDestination) {
        e.preventDefault() // Necessary to allow dropping
        if(e.dataTransfer) e.dataTransfer.dropEffect = 'copy'
    }
}

const handleDrop = (e: DragEvent) => {
    if (!props.isDestination) return
    
    const data = e.dataTransfer?.getData('application/json')
    if (data) {
        try {
            const files = JSON.parse(data) as string[]
            emit('items-dropped', files)
        } catch (e) {
            console.error('Failed to parse dropped items', e)
        }
    }
}

// --- Utils ---
const createFolderRef = async () => {
    if(!newFolderName.value) return
    try {
        const source = props.isDestination ? '16tb' : 'zurg'
        // createFolder in useApi takes (source, path, folderName)
        await createFolder(source, currentPath.value, newFolderName.value)
        isNewFolderModalOpen.value = false
        newFolderName.value = ''
        refresh()
    } catch(e) {
        console.error(e)
    }
}

const formatDate = (d: string) => {
  const date = new Date(d)
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const getFileIcon = (file: any) => {
  if (file.is_dir) return 'i-heroicons-folder-20-solid'
  if (isMovie(file.name)) return 'i-heroicons-film'
  if (isImage(file.name)) return 'i-heroicons-photo'
  if (isAudio(file.name)) return 'i-heroicons-musical-note'
  if (isArchive(file.name)) return 'i-heroicons-archive-box'
  return 'i-heroicons-document'
}

const getFileIconColor = (file: any, isActive: boolean) => {
    if (isActive) return 'text-white' // Active always white/bright
    
    if (file.is_dir) return 'text-[var(--brand-1)] drop-shadow-md'
    if (isMovie(file.name)) return 'text-[var(--brand-10)]'
    if (isImage(file.name)) return 'text-[var(--brand-2)]'
    if (isAudio(file.name)) return 'text-[var(--brand-8)]'
    if (isArchive(file.name)) return 'text-[var(--brand-5)]'
    
    return 'text-gray-400'
}

watch(() => props.initialPath, (newP) => {
  if(newP) loadFiles(newP)
})

onMounted(() => {
  loadFiles(currentPath.value)
})

import FileBreadcrumbs from '~/components/FileBreadcrumbs.vue'

defineExpose({
    refresh,
    loadFiles,
    currentPath,
    selectedFiles // Expose for parent
})
</script>

<style scoped>
/* Scrollbar matching Windows style in main.css */
</style>
