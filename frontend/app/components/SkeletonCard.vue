<template>
  <div class="glass-panel overflow-hidden h-full flex items-stretch">
      <!-- Media Poster Skeleton -->
      <div class="w-20 sm:w-28 bg-white/5 flex-shrink-0 shimmer-bg border-r border-white/5"></div>
      
      <!-- Content Skeleton -->
      <div class="flex-1 p-4 flex flex-col justify-between py-5 gap-3">
          <!-- Top Section -->
          <div class="space-y-2">
              <div class="h-5 w-3/4 bg-white/5 rounded shimmer-bg"></div>
              <div class="flex gap-2">
                  <div class="h-4 w-12 bg-white/5 rounded shimmer-bg"></div>
                  <div class="h-4 w-20 bg-white/5 rounded shimmer-bg"></div>
              </div>
          </div>
          
          <!-- Bottom Section -->
          <div class="space-y-2">
              <div class="h-3 w-1/2 bg-white/5 rounded shimmer-bg"></div>
              <div class="h-3 w-2/3 bg-white/5 rounded shimmer-bg"></div>
          </div>
      </div>
  </div>
</template>
