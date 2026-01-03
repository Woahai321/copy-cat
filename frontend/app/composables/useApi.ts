interface FileItem {
  name: string
  path: string
  is_directory: boolean
  size: number
  size_formatted: string
  modified: number
}

interface BrowseResponse {
  items: FileItem[]
  total: number
  has_more: boolean
}

interface FolderInfo {
  path: string
  size: number
  size_formatted: string
  exists: boolean
  item_count: number
}

interface CopyJob {
  id: number
  source_path: string
  destination_path: string
  status: string
  progress_percent: number
  total_size_bytes: number
  copied_size_bytes: number
  error_message: string | null
  created_at: string
  completed_at: string | null
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const { getAuthHeaders } = useAuth()
  const authHeaders = getAuthHeaders() as Record<string, string>

  // Add timeout wrapper for all API calls
  const fetchWithTimeout = async <T>(url: string, options: any = {}, timeout: number = 30000): Promise<T> => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const response = await $fetch<T>(url, {
        ...options,
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      return response
    } catch (error: any) {
      clearTimeout(timeoutId)

      // Handle 401 Unauthorized globally
      if (error.response?.status === 401) {
        console.warn('[useApi] 401 Unauthorized - logging out')
        const { logout } = useAuth()
        logout()
        navigateTo('/login')
        throw new Error('Session expired. Please login again.')
      }

      if (error.name === 'AbortError') {
        throw new Error('Request timed out after 30 seconds')
      }
      throw error
    }
  }

  const browseDirectory = async (
    source: 'zurg' | '16tb',
    path: string = '',
    limit?: number,
    offset: number = 0,
    sortBy: string = 'name',
    order: string = 'asc'
  ): Promise<BrowseResponse> => {
    try {
      const params: any = { source, path, offset, sort_by: sortBy, order }
      if (limit !== undefined) {
        params.limit = limit
      }

      return await fetchWithTimeout<BrowseResponse>(
        `${config.public.apiBase}/api/browse`,
        {
          params,
          headers: authHeaders,
        },
        60000 // 60 second timeout for directory browsing
      )
    } catch (error) {
      console.error('Failed to browse directory:', error)
      throw error
    }
  }

  const getFolderInfo = async (
    source: 'zurg' | '16tb',
    path: string,
    calculateSize: boolean = false
  ): Promise<FolderInfo> => {
    try {
      return await $fetch<FolderInfo>(
        `${config.public.apiBase}/api/folder-info`,
        {
          params: { source, path, calculate_size: calculateSize },
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get folder info:', error)
      throw error
    }
  }

  const startCopy = async (sourcePath: string, destinationPath: string): Promise<CopyJob> => {
    try {
      return await $fetch<CopyJob>(
        `${config.public.apiBase}/api/copy/start`,
        {
          method: 'POST',
          body: { source_path: sourcePath, destination_path: destinationPath },
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to start copy:', error)
      throw error
    }
  }

  const getQueue = async (): Promise<CopyJob[]> => {
    try {
      return await $fetch<CopyJob[]>(
        `${config.public.apiBase}/api/copy/queue`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get queue:', error)
      throw error
    }
  }

  const getJob = async (jobId: number): Promise<CopyJob> => {
    try {
      return await $fetch<CopyJob>(
        `${config.public.apiBase}/api/copy/${jobId}`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error(`Failed to get job ${jobId}:`, error)
      throw error
    }
  }

  const getHistory = async (limit: number = 50, offset: number = 0): Promise<CopyJob[]> => {
    try {
      return await $fetch<CopyJob[]>(
        `${config.public.apiBase}/api/copy/history`,
        {
          params: { limit, offset },
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get history:', error)
      throw error
    }
  }

  const cancelJob = async (jobId: number): Promise<void> => {
    try {
      await $fetch(
        `${config.public.apiBase}/api/copy/${jobId}`,
        {
          method: 'DELETE',
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to cancel job:', error)
      throw error
    }
  }

  const clearQueue = async (): Promise<{ message: string }> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/copy/queue`,
        {
          method: 'DELETE',
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to clear queue:', error)
      throw error
    }
  }

  const retryJob = async (jobId: number): Promise<CopyJob> => {
    try {
      return await $fetch<CopyJob>(
        `${config.public.apiBase}/api/copy/${jobId}/retry`,
        {
          method: 'POST',
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to retry job:', error)
      throw error
    }
  }

  const createFolder = async (source: string, path: string, folderName: string): Promise<{ success: boolean; message: string; path: string }> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/create-folder`,
        {
          method: 'POST',
          headers: authHeaders,
          params: {
            source,
            path,
            folder_name: folderName
          }
        }
      )
    } catch (error) {
      console.error('Failed to create folder:', error)
      throw error
    }
  }

  const deleteItem = async (source: string, path: string): Promise<{ success: boolean; message: string }> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/files/delete`,
        {
          method: 'DELETE',
          headers: authHeaders,
          params: { source, path }
        }
      )
    } catch (error) {
      console.error('Failed to delete item:', error)
      throw error
    }
  }


  const getUserInfo = async (): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/users/me`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get user info:', error)
      throw error
    }
  }

  const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
    try {
      await $fetch(
        `${config.public.apiBase}/api/users/change-password`,
        {
          method: 'POST',
          headers: authHeaders,
          body: {
            current_password: currentPassword,
            new_password: newPassword
          }
        }
      )
    } catch (error) {
      console.error('Failed to change password:', error)
      throw error
    }
  }

  const createUser = async (username: string, password: string, isAdmin: boolean = false): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/users/create`,
        {
          method: 'POST',
          headers: authHeaders,
          body: {
            username,
            password,
            is_admin: isAdmin
          }
        }
      )
    } catch (error) {
      console.error('Failed to create user:', error)
      throw error
    }
  }

  const listUsers = async (): Promise<any[]> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/users/list`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to list users:', error)
      throw error
    }
  }

  const getSystemStatus = async (): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/system/status`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get system status:', error)
      return null
    }
  }

  const getDiskUsage = async (): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/system/disk`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get disk usage:', error)
      return null
    }
  }

  const getTransferStats = async (): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/stats`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get transfer stats:', error)
      return null
    }
  }

  const setJobPriority = async (jobId: number, priority: number): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/copy/${jobId}/priority`,
        {
          method: 'POST',
          headers: authHeaders,
          body: { priority }
        }
      )
    } catch (error) {
      console.error('Failed to set job priority:', error)
      throw error
    }
  }

  const reorderQueue = async (jobIds: number[]): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/copy/reorder`,
        {
          method: 'POST',
          headers: authHeaders,
          body: { job_ids: jobIds }
        }
      )
    } catch (error) {
      console.error('Failed to reorder queue:', error)
      throw error
    }
  }

  const batchCopyItems = async (itemIds: number[], destinationPath: string): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/library/batch-copy`,
        {
          method: 'POST',
          headers: authHeaders,
          body: { item_ids: itemIds, destination_path: destinationPath }
        }
      )
    } catch (error) {
      console.error('Failed to batch copy:', error)
      throw error
    }
  }

  const testDiscordWebhook = async (): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/settings/test-discord`,
        {
          method: 'POST',
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to test Discord webhook:', error)
      throw error
    }
  }

  const getSettings = async (): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/settings`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get settings:', error)
      throw error
    }
  }

  const updateSettings = async (settings: any): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/settings`,
        {
          method: 'POST',
          headers: authHeaders,
          body: settings
        }
      )
    } catch (error) {
      console.error('Failed to update settings:', error)
      throw error
    }
  }

  const validateSettings = async (settings: any): Promise<{ valid: boolean }> => {
    try {
      return await $fetch<{ valid: boolean }>(
        `${config.public.apiBase}/api/settings/validate`,
        {
          method: 'POST',
          headers: authHeaders,
          body: settings
        }
      )
    } catch (error) {
      console.error('Failed to validate settings:', error)
      throw error
    }
  }

  const getSettingsStatus = async (): Promise<any> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/settings/status`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get settings status:', error)
      return null
    }
  }

  const getDbTables = async (): Promise<{ tables: string[] }> => {
    try {
      return await $fetch(
        `${config.public.apiBase}/api/db/tables`,
        {
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to get db tables:', error)
      throw error
    }
  }

  const queryDbTable = async (
    table: string,
    limit: number = 50,
    offset: number = 0,
    sortBy?: string,
    order: 'asc' | 'desc' = 'asc',
    search?: string
  ): Promise<{ columns: string[], rows: any[], total: number }> => {
    try {
      const params: any = { table, limit, offset }
      if (sortBy) {
        params.sort_by = sortBy
        params.order = order
      }
      if (search) {
        params.search = search
      }

      return await $fetch(
        `${config.public.apiBase}/api/db/query`,
        {
          params,
          headers: authHeaders,
        }
      )
    } catch (error) {
      console.error('Failed to query db table:', error)
      throw error
    }
  }

  return {
    browseDirectory,
    getFolderInfo,
    startCopy,
    getQueue,
    getJob,
    getHistory,
    cancelJob,
    clearQueue,
    retryJob,
    createFolder,
    deleteItem,
    getUserInfo,
    changePassword,
    createUser,
    listUsers,
    getSystemStatus,
    getDiskUsage,
    getTransferStats,
    setJobPriority,
    reorderQueue,
    batchCopyItems,
    testDiscordWebhook,
    getSettings,
    updateSettings,
    validateSettings,
    getSettingsStatus,
    getDbTables,
    queryDbTable
  }
}
