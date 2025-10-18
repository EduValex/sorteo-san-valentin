/**
 * Composable para manejar las llamadas a la API del backend
 */
export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  /**
   * Realiza una petición a la API
   */
  const apiCall = async <T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    const url = `${apiBase}${endpoint}`

    // Obtener token de localStorage si existe
    const token = (typeof window !== 'undefined') ? localStorage.getItem('access_token') : null

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          error: 'Error en la petición'
        }))
        throw new Error(error.error || error.detail || 'Error desconocido')
      }

      return await response.json()
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  return {
    // Registro de participante
    registerParticipant: (data: {
      email: string
      full_name: string
      phone: string
    }) => apiCall('/participants/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

    // Verificar email
    verifyEmail: (token: string) => apiCall('/participants/verify-email/', {
      method: 'POST',
      body: JSON.stringify({ token }),
    }),

    // Establecer contraseña
    setPassword: (data: {
      verification_token: string
      password: string
      password_confirm: string
    }) => apiCall('/participants/set-password/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

    // Login de administrador
    loginAdmin: (email: string, password: string) => apiCall('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

    // Listar participantes (admin)
    getParticipants: (params?: {
      search?: string
      is_verified?: boolean
      page?: number
    }) => {
      const queryParams = new URLSearchParams()
      if (params?.search) queryParams.append('search', params.search)
      if (params?.is_verified !== undefined) {
        queryParams.append('is_verified', params.is_verified.toString())
      }
      if (params?.page) queryParams.append('page', params.page.toString())

      const query = queryParams.toString()
      return apiCall(`/admin/participants/${query ? '?' + query : ''}`)
    },

    // Obtener estadísticas (admin)
    getStats: () => apiCall('/admin/participants/stats/'),

    // Realizar sorteo (admin)
    drawWinner: () => apiCall('/admin/winners/draw/', {
      method: 'POST',
    }),

    // Listar ganadores (admin)
    getWinners: () => apiCall('/admin/winners/'),
  }
}
