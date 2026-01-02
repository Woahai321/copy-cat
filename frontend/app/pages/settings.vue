<template>
  <div class="h-full flex flex-col p-6 space-y-8 max-w-7xl mx-auto w-full animate-fade-in">
    
    <!-- Cinematic Header -->
    <div class="flex items-center justify-between pb-6 border-b border-white/5 relative overflow-hidden group">
      <div class="absolute top-0 right-0 w-64 h-64 bg-[var(--win-accent)]/5 blur-[80px] rounded-full -translate-y-1/2 translate-x-1/2 group-hover:bg-[var(--win-accent)]/10 transition-colors"></div>
      
      <div class="flex items-center gap-5 relative z-10">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--glass-level-2-bg)] to-[var(--glass-level-1-bg)] flex items-center justify-center border border-white/10 shadow-2xl">
          <UIcon name="i-heroicons-cog-6-tooth" class="w-8 h-8 text-[var(--win-accent)] animate-spin-slow" />
        </div>
        <div>
          <h1 class="text-3xl font-bold text-[var(--win-text-primary)] tracking-tight">Settings</h1>
          <p class="text-sm text-[var(--win-text-muted)] font-light">System preferences, security, and user management</p>
        </div>
      </div>
    </div>

    <div class="flex flex-col lg:flex-row gap-8 flex-1 min-h-0">
      
      <!-- Sidebar Navigation -->
      <div class="lg:w-64 flex-shrink-0 flex flex-row lg:flex-col gap-1 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="currentTab = tab.id"
          class="flex items-center gap-3 px-5 py-3.5 rounded-2xl text-sm transition-all duration-300 group relative flex-shrink-0"
          :class="currentTab === tab.id 
            ? 'bg-[var(--glass-level-2-bg)] text-[var(--win-text-primary)] font-bold shadow-xl border border-white/10 marquee-border' 
            : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-[var(--glass-level-1-bg)] border border-transparent'"
        >
          <div v-if="currentTab === tab.id" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-[var(--win-accent)] rounded-full hidden lg:block"></div>
          <UIcon :name="getTabIcon(tab.id)" class="w-5 h-5" :class="currentTab === tab.id ? 'text-[var(--win-accent)]' : 'text-[var(--win-text-muted)] group-hover:text-[var(--win-text-secondary)]'" />
          <span class="tracking-wide">{{ tab.label }}</span>
        </button>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 min-w-0 bg-[var(--glass-level-1-bg)] glass-panel !rounded-[2rem] border-white/5 shadow-2xl overflow-hidden flex flex-col backdrop-blur-3xl">
        <div class="flex-1 overflow-y-auto p-8 relative">
          
          <!-- Appearance Tab -->
          <div v-show="currentTab === 'appearance'" class="animate-fade-in-up space-y-8">
            <div class="space-y-2">
              <h2 class="text-xl font-bold text-[var(--win-text-primary)] flex items-center gap-3">
                <UIcon name="i-heroicons-swatch" class="w-6 h-6 text-[var(--win-accent)]" />
                Theme & Appearance
              </h2>
              <p class="text-sm text-[var(--win-text-muted)] font-light leading-relaxed">Customize the look and feel of your CopyCat interface.</p>
            </div>
            
            <SettingsThemeSelector />
          </div>

          <!-- Security Tab -->
          <div v-if="currentTab === 'security'" class="max-w-xl animate-fade-in-up space-y-8">
            <div class="space-y-2">
              <h2 class="text-xl font-bold text-[var(--win-text-primary)] flex items-center gap-3">
                <UIcon name="i-heroicons-lock-closed" class="w-6 h-6 text-[var(--win-accent)]" />
                Change Password
              </h2>
              <p class="text-sm text-[var(--win-text-muted)] font-light leading-relaxed">Ensure your account remains secure by regularly updating your password. Use at least 8 characters with a mix of symbols.</p>
            </div>
            
            <form @submit.prevent="handleChangePassword" class="space-y-6">
              <div class="space-y-4">
                <div class="relative group">
                  <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">Current Password</label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <UIcon name="i-heroicons-key" class="w-4 h-4 text-[var(--win-text-secondary)] group-focus-within:text-[var(--win-accent)] transition-colors" />
                    </div>
                    <input v-model="pwdForm.current" type="password" required class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-[var(--win-text-primary)] outline-none focus:border-[var(--win-accent)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all text-sm shadow-inner" placeholder="Enter current password" />
                  </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="relative group">
                    <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">New Password</label>
                    <div class="relative">
                      <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <UIcon name="i-heroicons-shield-check" class="w-4 h-4 text-[var(--win-text-secondary)] group-focus-within:text-[var(--win-accent)] transition-colors" />
                      </div>
                      <input v-model="pwdForm.new" type="password" required class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-[var(--win-text-primary)] outline-none focus:border-[var(--win-accent)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all text-sm shadow-inner" placeholder="New password" />
                    </div>
                  </div>
                  
                  <div class="relative group">
                    <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">Confirm New</label>
                    <div class="relative">
                      <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <UIcon name="i-heroicons-check-circle" class="w-4 h-4 text-[var(--win-text-secondary)] group-focus-within:text-[var(--win-accent)] transition-colors" />
                      </div>
                      <input v-model="pwdForm.confirm" type="password" required class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-[var(--win-text-primary)] outline-none focus:border-[var(--win-accent)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all text-sm shadow-inner" placeholder="Confirm password" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="pt-4 flex justify-end">
                <button type="submit" class="min-w-[180px] bg-[var(--win-text-primary)] text-[var(--win-bg-base)] hover:bg-[var(--win-text-primary)]/90 disabled:opacity-50 rounded-2xl py-4 px-8 text-xs font-bold uppercase tracking-widest transition-all shadow-xl flex items-center justify-center gap-2 active:scale-95" :disabled="loading">
                  <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <span>Update Password</span>
                </button>
              </div>
            </form>
          </div>

          <!-- Users Tab (Admin Only) -->
          <div v-show="currentTab === 'users'" class="animate-fade-in-up space-y-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h2 class="text-xl font-bold text-[var(--win-text-primary)] flex items-center gap-3">
                  <UIcon name="i-heroicons-user-group" class="w-6 h-6 text-[var(--win-accent)]" />
                  User Management
                </h2>
                <p class="text-sm text-[var(--win-text-muted)] font-light">Add or remove users and manage access privileges.</p>
              </div>
              <button @click="showAddUserModal = true" class="px-6 py-3.5 bg-[var(--win-accent)]/10 text-[var(--win-accent)] border border-[var(--win-accent)]/30 hover:bg-[var(--win-accent)]/20 rounded-2xl text-xs font-bold uppercase tracking-widest transition-all flex items-center gap-2">
                <UIcon name="i-heroicons-user-plus" class="w-4 h-4" />
                <span>Add User</span>
              </button>
            </div>

            <div class="bg-[var(--glass-level-1-bg)] border border-white/5 rounded-[2rem] overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-left text-sm">
                  <thead class="bg-[var(--glass-level-1-bg)] text-[10px] uppercase tracking-[0.2em] font-bold text-[var(--win-text-muted)] border-b border-white/5">
                    <tr>
                      <th class="px-8 py-5 font-bold">Member</th>
                      <th class="px-8 py-5 font-bold">Role</th>
                      <th class="px-8 py-5 font-bold">Created</th>
                      <th class="px-8 py-5 font-bold text-right">ID</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-white/[0.03]">
                    <tr v-for="user in users" :key="user.id" class="hover:bg-[var(--glass-level-1-bg)] transition-colors group">
                      <td class="px-8 py-5">
                        <div class="flex items-center gap-3">
                          <div class="w-8 h-8 rounded-lg bg-[var(--glass-level-1-bg)] border border-white/5 flex items-center justify-center text-[10px] font-bold text-[var(--win-accent)] uppercase">
                            {{ user.username.substring(0, 1) }}
                          </div>
                          <span class="font-medium text-[var(--win-text-primary)]">{{ user.username }}</span>
                        </div>
                      </td>
                      <td class="px-8 py-5">
                        <span 
                          class="px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-widest border"
                          :class="user.is_admin ? 'bg-[var(--brand-1)]/10 text-[var(--brand-1)] border-[var(--brand-1)]/20 shadow-[0_0_10px_rgba(96,205,255,0.1)]' : 'bg-[var(--glass-level-1-bg)] text-[var(--win-text-muted)] border-white/10'"
                        >
                          {{ user.is_admin ? 'Admin' : 'User' }}
                        </span>
                      </td>
                      <td class="px-8 py-5 text-[var(--win-text-muted)] font-light">{{ formatDate(user.created_at) }}</td>
                      <td class="px-8 py-5 text-right font-mono text-[var(--win-accent)]/50 group-hover:text-[var(--win-accent)] transition-colors">#0{{ user.id }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- System Tab (Settings) -->
          <div v-show="currentTab === 'system'" class="animate-fade-in-up max-w-3xl space-y-10">
             <div>
                <h2 class="text-xl font-bold text-[var(--win-text-primary)] flex items-center gap-3">
                  <UIcon name="i-heroicons-cpu-chip" class="w-6 h-6 text-[var(--win-accent)]" />
                  System Configuration
                </h2>
                <p class="text-sm text-[var(--win-text-muted)] font-light">Configure application settings and paths.</p>
             </div>
             
             <form @submit.prevent="handleUpdateSystemSettings" class="space-y-10">
                <!-- Trakt Section -->
                <div class="space-y-6 relative">
                   <div class="flex items-center gap-4 text-[var(--win-text-primary)] font-bold text-xs uppercase tracking-[0.2em]">
                      <div class="w-8 h-8 rounded-lg bg-[var(--brand-1)]/10 border border-[var(--brand-1)]/20 flex items-center justify-center">
                        <UIcon name="i-heroicons-sparkles" class="w-4 h-4 text-[var(--brand-1)]" />
                      </div>
                      <span>Trakt Integration</span>
                   </div>
                   
                   <div class="relative group">
                      <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">Trakt API Key (Masked)</label>
                      <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <UIcon name="i-heroicons-finger-print" class="w-4 h-4 text-[var(--win-text-secondary)] group-focus-within:text-[var(--brand-1)] transition-colors" />
                        </div>
                        <input v-model="systemForm.trakt_client_id" type="password" class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-[var(--win-text-primary)] outline-none focus:border-[var(--brand-1)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all font-mono text-sm shadow-inner" placeholder="Leave empty to maintain existing key" />
                      </div>
                      <p class="text-[10px] text-[var(--win-text-secondary)] mt-2 ml-1 italic font-light">Fetch posters and ratings from your Trakt application dashboard.</p>
                   </div>
                </div>

                <!-- Library Paths -->
                <div class="space-y-6">
                   <div class="flex items-center gap-4 text-[var(--win-text-primary)] font-bold text-xs uppercase tracking-[0.2em]">
                      <div class="w-8 h-8 rounded-lg bg-[var(--brand-10)]/10 border border-[var(--brand-10)]/20 flex items-center justify-center">
                        <UIcon name="i-heroicons-rectangle-stack" class="w-4 h-4 text-[var(--brand-10)]" />
                      </div>
                      <span>Library Paths</span>
                   </div>
    
                   <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div class="relative group">
                        <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">Movies Path</label>
                        <div class="relative">
                          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <UIcon name="i-heroicons-film" class="w-4 h-4 text-[var(--win-text-secondary)] group-focus-within:text-[var(--brand-10)] transition-colors" />
                          </div>
                          <input v-model="systemForm.default_movies_path" type="text" class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-[var(--win-text-primary)] outline-none focus:border-[var(--brand-10)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all font-mono text-sm shadow-inner" placeholder="/mnt/destination/movies" />
                        </div>
                      </div>
                      <div class="relative group">
                        <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">TV Shows Path</label>
                        <div class="relative">
                          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <UIcon name="i-heroicons-tv" class="w-4 h-4 text-[var(--win-text-secondary)] group-focus-within:text-[var(--brand-10)] transition-colors" />
                          </div>
                          <input v-model="systemForm.default_series_path" type="text" class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-[var(--win-text-primary)] outline-none focus:border-[var(--brand-10)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all font-mono text-sm shadow-inner" placeholder="/mnt/destination/shows" />
                        </div>
                      </div>
                   </div>
                </div>

                <!-- Automated Scanning -->
                <div class="space-y-6">
                   <div class="flex items-center gap-4 text-[var(--win-text-primary)] font-bold text-xs uppercase tracking-[0.2em]">
                      <div class="w-8 h-8 rounded-lg bg-[var(--glass-level-2-bg)] border border-[var(--status-success)]/20 flex items-center justify-center">
                        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 text-[var(--status-success)]" />
                      </div>
                      <span>Automated Scanning</span>
                   </div>

                   <div class="relative group">
                      <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">Scan Interval (Seconds)</label>
                      <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <UIcon name="i-heroicons-clock" class="w-4 h-4 text-[var(--win-text-secondary)] group-focus-within:text-[var(--status-success)] transition-colors" />
                        </div>
                        <input v-model.number="systemForm.scan_interval_seconds" type="number" min="30" max="86400" class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-[var(--win-text-primary)] outline-none focus:border-[var(--status-success)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all font-mono text-sm shadow-inner" placeholder="300" />
                      </div>
                      <p class="text-[10px] text-[var(--win-text-secondary)] mt-2 ml-1 italic font-light">How often to scan for new media files (minimum 30 seconds, maximum 24 hours).</p>
                   </div>
                </div>

                <!-- Discord Notifications -->
                <div class="space-y-6">
                   <div class="flex items-center gap-4 text-[var(--win-text-primary)] font-bold text-xs uppercase tracking-[0.2em]">
                      <div class="w-8 h-8 rounded-lg bg-[var(--brand-8)]/10 border border-[var(--brand-8)]/20 flex items-center justify-center">
                        <UIcon name="i-heroicons-bell-alert" class="w-4 h-4 text-[var(--brand-8)]" />
                      </div>
                      <span>Discord Notifications</span>
                      <span v-if="discordConfigured" class="ml-auto text-[10px] bg-[var(--glass-level-2-bg)] text-[var(--status-success)] px-2 py-1 rounded-lg border border-[var(--status-success)]/20">Connected</span>
                   </div>

                   <div class="relative group">
                      <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">Webhook URL</label>
                      <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <UIcon name="i-heroicons-link" class="w-4 h-4 text-[var(--win-text-secondary)] group-focus-within:text-[var(--brand-8)] transition-colors" />
                        </div>
                        <input v-model="systemForm.discord_webhook_url" type="password" class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-[var(--win-text-primary)] outline-none focus:border-[var(--brand-8)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all font-mono text-sm shadow-inner" placeholder="https://discord.com/api/webhooks/..." />
                      </div>
                      <p class="text-[10px] text-[var(--win-text-secondary)] mt-2 ml-1 italic font-light">Paste your Discord channel webhook URL to receive notifications.</p>
                   </div>

                   <div class="flex flex-col gap-4 p-4 rounded-2xl bg-[var(--glass-level-1-bg)] border border-white/5">
                      <label class="flex items-center gap-3 cursor-pointer group">
                        <div class="relative flex items-center">
                          <input v-model="systemForm.discord_notify_success" type="checkbox" class="sr-only peer" />
                          <div class="w-10 h-5 bg-[var(--glass-level-3-bg)] rounded-full peer-checked:bg-[var(--win-text-primary)] transition-all"></div>
                          <div class="absolute left-1 top-1 w-3 h-3 bg-[var(--win-text-primary)]/50 rounded-full transition-all peer-checked:left-6 peer-checked:bg-[var(--win-bg-base)]"></div>
                        </div>
                        <div class="flex flex-col">
                          <span class="text-xs font-bold text-[var(--win-text-primary)]">Notify on Success</span>
                          <span class="text-[10px] text-[var(--win-text-muted)] font-light">Send notification when copy jobs complete.</span>
                        </div>
                      </label>
                      
                      <label class="flex items-center gap-3 cursor-pointer group">
                        <div class="relative flex items-center">
                          <input v-model="systemForm.discord_notify_failure" type="checkbox" class="sr-only peer" />
                          <div class="w-10 h-5 bg-[var(--glass-level-3-bg)] rounded-full peer-checked:bg-[var(--win-text-primary)] transition-all"></div>
                          <div class="absolute left-1 top-1 w-3 h-3 bg-[var(--win-text-primary)]/50 rounded-full transition-all peer-checked:left-6 peer-checked:bg-[var(--win-bg-base)]"></div>
                        </div>
                        <div class="flex flex-col">
                          <span class="text-xs font-bold text-[var(--win-text-primary)]">Notify on Failure</span>
                          <span class="text-[10px] text-[var(--win-text-muted)] font-light">Send notification when copy jobs fail or are cancelled.</span>
                        </div>
                      </label>
                   </div>

                   <button 
                     type="button"
                     @click="handleTestDiscord"
                     :disabled="!discordConfigured || testingDiscord"
                     class="px-5 py-3 bg-[var(--brand-8)]/10 text-[var(--brand-8)] border border-[var(--brand-8)]/30 hover:bg-[var(--brand-8)]/20 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-xs font-bold uppercase tracking-widest transition-all flex items-center gap-2"
                   >
                     <UIcon v-if="testingDiscord" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                     <UIcon v-else name="i-heroicons-paper-airplane" class="w-4 h-4" />
                     <span>{{ testingDiscord ? 'Sending...' : 'Test Webhook' }}</span>
                   </button>
                </div>

                <div class="pt-4 flex justify-end">
                   <button type="submit" class="min-w-[180px] bg-[var(--win-text-primary)] text-[var(--win-bg-base)] hover:bg-[var(--win-text-primary)]/90 disabled:opacity-50 rounded-2xl py-4 px-8 text-xs font-bold uppercase tracking-widest transition-all shadow-xl flex items-center justify-center gap-3 active:scale-95" :disabled="loading">
                      <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                      <span>Save Changes</span>
                   </button>
                </div>
             </form>
          </div>

          <!-- About Tab -->
          <div v-show="currentTab === 'about'" class="animate-fade-in-up space-y-10 max-w-2xl">
              <div class="flex items-center gap-6 p-8 rounded-[2.5rem] bg-[var(--glass-level-1-bg)] border border-white/5 shadow-2xl relative overflow-hidden group">
                <div class="absolute -top-12 -left-12 w-48 h-48 bg-[var(--win-accent)]/10 blur-[60px] rounded-full animate-pulse-slow"></div>
                
                <div class="w-24 h-24 rounded-[2rem] bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center border border-white/10 shadow-inner flex-shrink-0 relative z-10">
                  <UIcon name="i-heroicons-cube-transparent" class="w-12 h-12 text-[var(--win-accent)]" />
                </div>
                <div class="relative z-10">
                  <h3 class="text-3xl font-bold text-[var(--win-text-primary)] tracking-tighter mb-1">CopyCat OS</h3>
                  <div class="flex items-center gap-3">
                    <span class="px-3 py-1 bg-[var(--win-accent)]/20 text-[var(--win-accent)] rounded-full text-[10px] font-bold tracking-[0.2em] uppercase">v0.0.1 Stable</span>
                    <span class="text-[var(--win-text-secondary)] text-xs font-light tracking-wide italic">"Perfect synchronization"</span>
                  </div>
                </div>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Status Cards -->
                <div v-for="stat in systemStats" :key="stat.label" class="p-6 rounded-3xl bg-[var(--glass-level-1-bg)] border border-white/5 hover:bg-[var(--glass-level-2-bg)] transition-colors group">
                  <div class="flex items-center justify-between mb-4">
                    <div class="w-10 h-10 rounded-xl bg-[var(--glass-level-1-bg)] flex items-center justify-center border border-white/5 text-[var(--win-text-muted)] group-hover:text-[var(--win-text-primary)] transition-colors">
                      <UIcon :name="stat.icon" class="w-5 h-5" />
                    </div>
                    <span :class="stat.colorClass" class="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded bg-[var(--glass-level-2-bg)]">
                      {{ stat.status }}
                    </span>
                  </div>
                  <div class="text-[10px] uppercase tracking-[0.2em] text-[var(--win-text-muted)] font-bold">{{ stat.label }}</div>
                  <div class="text-[var(--win-text-primary)] font-medium mt-1">{{ stat.value }}</div>
                </div>
              </div>
              
              <div class="p-5 rounded-2xl bg-[var(--glass-level-3-bg)] border border-white/5 text-[10px] text-center text-[var(--win-text-secondary)] font-mono tracking-widest uppercase">
                System Online • Authorized Access Only
              </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Add User Modal (Enhanced Glass) -->
    <div v-if="showAddUserModal" class="fixed inset-0 z-50 flex items-center justify-center px-4 backdrop-blur-md bg-[var(--glass-level-4-bg)]" @click.self="showAddUserModal = false">
      <div class="glass-panel w-full max-w-md p-10 !rounded-[2.5rem] border-white/10 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.6)] animate-zoom-in relative overflow-hidden">
        <div class="absolute -top-24 -right-24 w-48 h-48 bg-[var(--win-accent)]/10 blur-3xl rounded-full"></div>
        
        <div class="relative z-10">
          <div class="flex items-center gap-4 mb-8">
            <div class="w-12 h-12 rounded-xl bg-[var(--win-accent)]/10 border border-[var(--win-accent)]/20 flex items-center justify-center">
              <UIcon name="i-heroicons-user-plus" class="w-6 h-6 text-[var(--win-accent)]" />
            </div>
            <div>
              <h3 class="text-2xl font-bold text-[var(--win-text-primary)] tracking-tight">Add New User</h3>
              <p class="text-xs text-[var(--win-text-muted)] font-light">Create a new user account.</p>
            </div>
          </div>
          
          <form @submit.prevent="handleAddUser" class="space-y-6">
            <div class="space-y-4">
              <div class="relative group">
                <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">Username</label>
                <input v-model="newUserForm.username" type="text" required class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 px-5 text-[var(--win-text-primary)] outline-none focus:border-[var(--win-accent)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all text-sm" placeholder="Member name" />
              </div>

              <div class="relative group">
                <label class="text-[10px] uppercase font-bold tracking-[0.2em] text-[var(--win-text-muted)] mb-2 block ml-1">Password</label>
                <input v-model="newUserForm.password" type="password" required class="w-full bg-[var(--glass-level-2-bg)] border border-white/10 rounded-2xl py-4 px-5 text-[var(--win-text-primary)] outline-none focus:border-[var(--win-accent)]/50 focus:bg-[var(--glass-level-3-bg)] transition-all text-sm" placeholder="Secret key" />
              </div>

              <label class="flex items-center gap-3 p-4 rounded-2xl bg-[var(--glass-level-1-bg)] border border-white/5 hover:bg-[var(--glass-level-2-bg)] transition-all cursor-pointer group">
                <div class="relative flex items-center">
                  <input v-model="newUserForm.isAdmin" type="checkbox" class="sr-only peer" />
                  <div class="w-10 h-5 bg-[var(--glass-level-3-bg)] rounded-full peer-checked:bg-[var(--win-accent)] transition-all"></div>
                  <div class="absolute left-1 top-1 w-3 h-3 bg-[var(--glass-level-2-bg)] rounded-full transition-all peer-checked:left-6 peer-checked:bg-[var(--win-bg-base)]"></div>
                </div>
                <div class="flex flex-col">
                  <span class="text-xs font-bold text-[var(--win-text-primary)] uppercase tracking-wider">Admin Access</span>
                  <span class="text-[10px] text-[var(--win-text-muted)] font-light">Grant administrative privileges.</span>
                </div>
              </label>
            </div>

            <div class="flex flex-col gap-3 pt-2">
              <button type="submit" class="w-full bg-[var(--win-text-primary)] text-[var(--win-bg-base)] hover:bg-[var(--win-text-primary)]/90 disabled:opacity-50 rounded-2xl py-4 text-xs font-bold uppercase tracking-widest transition-all shadow-xl flex items-center justify-center gap-2" :disabled="loading">
                <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <span>Create User</span>
              </button>
              <button type="button" @click="showAddUserModal = false" class="w-full py-4 text-[10px] text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] uppercase tracking-[0.3em] font-bold transition-colors">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'

definePageMeta({
  middleware: 'auth'
})

const { changePassword, listUsers, createUser, getUserInfo, getSettings, updateSettings, testDiscordWebhook } = useApi()
const toast = useToast()

// Discord state
const discordConfigured = ref(false)
const testingDiscord = ref(false)

const tabs = reactive([
  { id: 'appearance', label: 'Appearance' },
  { id: 'security', label: 'Security' },
  { id: 'system', label: 'System' },
  { id: 'users', label: 'Users' },
  { id: 'about', label: 'About' }
])

const getTabIcon = (id: string) => {
  switch(id) {
    case 'appearance': return 'i-heroicons-swatch'
    case 'security': return 'i-heroicons-shield-check'
    case 'system': return 'i-heroicons-cpu-chip'
    case 'users': return 'i-heroicons-user-group'
    case 'about': return 'i-heroicons-information-circle'
    default: return 'i-heroicons-cog'
  }
}

const systemStats = reactive([
  { label: 'System Status', icon: 'i-heroicons-cpu-chip', value: 'CopyCat Engine v2', status: 'Optimal', colorClass: 'text-[var(--status-success)]' },
  { label: 'Trakt Status', icon: 'i-heroicons-sparkles', value: 'Trakt Protocol', status: 'Linked', colorClass: 'text-[var(--brand-1)]' },
  { label: 'Total Users', icon: 'i-heroicons-user-group', value: 'Loading...', status: 'Active', colorClass: 'text-[var(--brand-10)]' },
  { label: 'Security', icon: 'i-heroicons-shield-exclamation', value: 'JWT Encrypted', status: 'Secured', colorClass: 'text-[var(--status-success)]' }
])

const currentTab = ref('appearance')
const loading = ref(false)
const users = ref<any[]>([])
const currentUser = ref<any>(null)

// Forms
const pwdForm = reactive({
  current: '',
  new: '',
  confirm: ''
})

const systemForm = reactive({
    trakt_client_id: '',
    default_movies_path: '',
    default_series_path: '',
    scan_interval_seconds: 300,
    discord_webhook_url: '',
    discord_notify_success: true,
    discord_notify_failure: true
})

const showAddUserModal = ref(false)
const newUserForm = reactive({
  username: '',
  password: '',
  isAdmin: false
})

// Handlers
const loadSystemSettings = async () => {
    try {
        const data = await getSettings()
        systemForm.default_movies_path = data.default_movies_path || ''
        systemForm.default_series_path = data.default_series_path || ''
        systemForm.scan_interval_seconds = data.scan_interval_seconds || 300
        // Clear trakt client id as it's masked or sensitive
        systemForm.trakt_client_id = ''
        // Discord settings
        systemForm.discord_webhook_url = ''  // Masked, don't show
        systemForm.discord_notify_success = data.discord_notify_success ?? true
        systemForm.discord_notify_failure = data.discord_notify_failure ?? true
        discordConfigured.value = data.discord_webhook_configured || false
        
        systemStats[1].status = data.trakt_configured ? 'Linked' : 'Offline'
        systemStats[1].colorClass = data.trakt_configured ? 'text-[var(--brand-1)]' : 'text-[var(--status-error)]'
    } catch (e) {
        console.error("Failed to load settings", e)
    }
}

const handleUpdateSystemSettings = async () => {
    loading.value = true
    try {
        await updateSettings({
            trakt_client_id: systemForm.trakt_client_id || undefined,
            default_movies_path: systemForm.default_movies_path || undefined,
            default_series_path: systemForm.default_series_path || undefined,
            scan_interval_seconds: systemForm.scan_interval_seconds || undefined,
            discord_webhook_url: systemForm.discord_webhook_url || undefined,
            discord_notify_success: systemForm.discord_notify_success,
            discord_notify_failure: systemForm.discord_notify_failure
        })
        toast.add({ title: 'Settings Saved', description: 'Settings updated successfully', color: 'green' })
        // Clear sensitive fields
        systemForm.trakt_client_id = ''
        systemForm.discord_webhook_url = ''
        loadSystemSettings()
    } catch (e: any) {
        toast.add({ title: 'Error', description: e.data?.detail || e.message, color: 'red' })
    } finally {
        loading.value = false
    }
}

const handleTestDiscord = async () => {
    testingDiscord.value = true
    try {
        await testDiscordWebhook()
        toast.add({ title: 'Test Sent', description: 'Check your Discord channel for the test message', color: 'green' })
    } catch (e: any) {
        toast.add({ title: 'Test Failed', description: e.data?.detail || e.message, color: 'red' })
    } finally {
        testingDiscord.value = false
    }
}
const handleChangePassword = async () => {
  if (pwdForm.new !== pwdForm.confirm) {
    toast.add({ title: 'Synchronization Error', description: 'Passwords do not match', color: 'red' })
    return
  }

  loading.value = true
  try {
    await changePassword(pwdForm.current, pwdForm.new)
    toast.add({ title: 'Password Updated', description: 'Security profile updated successfully', color: 'green' })
    pwdForm.current = ''
    pwdForm.new = ''
    pwdForm.confirm = ''
  } catch (error: any) {
    toast.add({ title: 'Update Failed', description: error.message || 'Failed to update credentials', color: 'red' })
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    // Only load if admin
    if (currentUser.value?.is_admin) {
      const data = await listUsers()
      users.value = data
      systemStats[2].value = `${data.length} Personnel`
    }
  } catch (error) {
    console.error('Failed to load users', error)
  }
}

const handleAddUser = async () => {
  loading.value = true
  try {
    await createUser(newUserForm.username, newUserForm.password, newUserForm.isAdmin)
    toast.add({ title: 'User Created', description: `${newUserForm.username} added successfully`, color: 'green' })
    showAddUserModal.value = false
    newUserForm.username = ''
    newUserForm.password = ''
    newUserForm.isAdmin = false
    loadUsers()
  } catch (error: any) {
    toast.add({ title: 'Creation Failed', description: error.data?.detail || error.message, color: 'red' })
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

// Logic to check admin status
const init = async () => {
  try {
    currentUser.value = await getUserInfo()
    if (currentUser.value?.is_admin) {
       loadUsers()
       loadSystemSettings()
    } else {
       // If not admin and on sensitive tab, switch away
       if (currentTab.value === 'users' || currentTab.value === 'system') {
           currentTab.value = 'security'
       }
       
       // Remove sensitive tabs for non-admins
       const toRemove = ['users', 'system']
       toRemove.forEach(id => {
           const idx = tabs.findIndex(t => t.id === id)
           if (idx > -1) tabs.splice(idx, 1)
       })
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(init)

watch(currentTab, (newTab) => {
  if (newTab === 'users') loadUsers()
  if (newTab === 'system') loadSystemSettings()
})
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.marquee-border::after {
  content: '';
  position: absolute;
  inset: -1px;
  background: linear-gradient(90deg, transparent, var(--win-accent), transparent);
  background-size: 200% 100%;
  animation: marquee 3s linear infinite;
  border-radius: inherit;
  z-index: -1;
  opacity: 0.3;
}

@keyframes marquee {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

input::placeholder {
  color: var(--win-text-muted);
  opacity: 0.5;
  font-weight: 300;
}
</style>
