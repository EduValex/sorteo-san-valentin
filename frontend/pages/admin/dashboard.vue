<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Panel Administrador
            </h1>
            <p class="text-gray-600">Sorteo San Valentín - CTS Turismo</p>
          </div>
          <button
            @click="handleLogout"
            class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
          >
            Cerrar Sesión
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-1">
              <p class="text-sm text-gray-600">Total Participantes</p>
              <p class="text-3xl font-bold text-gray-900">{{ stats.total_participants || 0 }}</p>
            </div>
            <div class="bg-blue-100 rounded-full p-3">
              <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-1">
              <p class="text-sm text-gray-600">Verificados</p>
              <p class="text-3xl font-bold text-green-600">{{ stats.verified || 0 }}</p>
            </div>
            <div class="bg-green-100 rounded-full p-3">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-1">
              <p class="text-sm text-gray-600">Pendientes</p>
              <p class="text-3xl font-bold text-yellow-600">{{ stats.pending || 0 }}</p>
            </div>
            <div class="bg-yellow-100 rounded-full p-3">
              <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Raffle Section -->
      <div class="bg-white rounded-lg shadow mb-8 p-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Realizar Sorteo</h2>
        <p class="text-gray-600 mb-4">
          Participantes elegibles: <span class="font-semibold">{{ stats.eligible_for_draw || 0 }}</span>
        </p>

        <!-- Success Message -->
        <div v-if="winnerMessage" class="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          {{ winnerMessage }}
        </div>

        <!-- Error Message -->
        <div v-if="drawError" class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {{ drawError }}
        </div>

        <!-- Winner Info -->
        <div v-if="latestWinner" class="mb-4 p-4 bg-purple-50 border border-purple-200 rounded">
          <h3 class="font-semibold text-purple-900 mb-2">Ganador Seleccionado:</h3>
          <p class="text-purple-800"><strong>Nombre:</strong> {{ latestWinner.participant_name }}</p>
          <p class="text-purple-800"><strong>Email:</strong> {{ latestWinner.participant_email }}</p>
          <p class="text-purple-800"><strong>Teléfono:</strong> {{ latestWinner.participant_phone }}</p>
        </div>

        <button
          @click="handleDraw"
          :disabled="drawLoading || (stats.eligible_for_draw || 0) === 0"
          class="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ drawLoading ? 'Sorteando...' : 'Sortear Ganador' }}
        </button>
      </div>

      <!-- Tabs Navigation -->
      <div class="bg-white rounded-lg shadow mb-8">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px">
            <button
              @click="activeTab = 'participants'"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'participants'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              👥 Participantes
            </button>
            <button
              @click="activeTab = 'winners'"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'winners'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              🏆 Historial de Ganadores
            </button>
          </nav>
        </div>

        <!-- Participants Tab Content -->
        <div v-show="activeTab === 'participants'">
          <div class="p-6 border-b border-gray-200">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <h2 class="text-2xl font-bold text-gray-900">Lista de Participantes</h2>

              <!-- Search and Filter -->
              <div class="flex gap-2">
                <input
                  v-model="searchQuery"
                  @input="handleSearch"
                  type="text"
                  placeholder="Buscar..."
                  class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <select
                  v-model="filterVerified"
                  @change="loadParticipants"
                  class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Todos</option>
                  <option value="true">Verificados</option>
                  <option value="false">Pendientes</option>
                </select>
              </div>
            </div>
          </div>

        <!-- Loading State -->
        <div v-if="participantsLoading" class="p-8 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p class="mt-2 text-gray-600">Cargando participantes...</p>
        </div>

        <!-- Participants Table -->
        <div v-else-if="participants.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nombre
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Teléfono
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha Registro
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="participant in participants" :key="participant.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ participant.full_name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ participant.email }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ participant.phone }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    v-if="participant.is_verified"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"
                  >
                    Verificado
                  </span>
                  <span
                    v-else
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800"
                  >
                    Pendiente
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(participant.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

          <!-- Empty State -->
          <div v-else class="p-8 text-center text-gray-500">
            No hay participantes registrados
          </div>
        </div>

        <!-- Winners History Tab Content -->
        <div v-show="activeTab === 'winners'">
          <div class="p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Historial de Sorteos</h2>
            <p class="text-gray-600 mb-6">
              Lista completa de todos los sorteos realizados
            </p>

            <!-- Loading State -->
            <div v-if="winnersLoading" class="p-8 text-center">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
              <p class="mt-2 text-gray-600">Cargando ganadores...</p>
            </div>

            <!-- Winners Grid -->
            <div v-else-if="winners.length > 0" class="space-y-4">
              <div
                v-for="winner in winners"
                :key="winner.id"
                class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200 hover:shadow-lg transition-shadow"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-3">
                      <div class="text-4xl">🏆</div>
                      <div>
                        <h3 class="text-xl font-bold text-purple-900">{{ winner.participant_name }}</h3>
                        <p class="text-sm text-purple-600">
                          Sorteado el {{ formatDate(winner.drawn_at) }}
                        </p>
                      </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                      <div class="flex items-center gap-2 text-gray-700">
                        <span class="text-lg">📧</span>
                        <span class="text-sm">{{ winner.participant_email }}</span>
                      </div>
                      <div class="flex items-center gap-2 text-gray-700">
                        <span class="text-lg">📱</span>
                        <span class="text-sm">{{ winner.participant_phone }}</span>
                      </div>
                      <div class="flex items-center gap-2 text-gray-700">
                        <span class="text-lg">👤</span>
                        <span class="text-sm">Sorteado por: {{ winner.drawn_by_name }}</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span
                          v-if="winner.notified"
                          class="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full flex items-center gap-1"
                        >
                          <span>✅</span>
                          Notificado
                        </span>
                        <span
                          v-else
                          class="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full flex items-center gap-1"
                        >
                          <span>⏳</span>
                          Pendiente notificación
                        </span>
                      </div>
                    </div>

                    <div class="mt-4 pt-4 border-t border-purple-200">
                      <p class="text-sm text-gray-600">
                        <strong>Premio:</strong> {{ winner.prize_description || 'Estadía de 2 noches para pareja en hotel todo incluido' }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="p-12 text-center">
              <div class="text-6xl mb-4">🎲</div>
              <h3 class="text-xl font-semibold text-gray-700 mb-2">
                No hay sorteos realizados aún
              </h3>
              <p class="text-gray-500">
                Realiza tu primer sorteo para ver el historial de ganadores aquí
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import Swal from 'sweetalert2'
import confetti from 'canvas-confetti'

const api = useApi()
const router = useRouter()

// Check authentication
onMounted(() => {
  if (typeof window !== 'undefined' && !localStorage.getItem('access_token')) {
    router.push('/admin/login')
  } else {
    loadStats()
    loadParticipants()
    loadWinners()
  }
})

// Watch tab changes to load data
watch(activeTab, (newTab) => {
  if (newTab === 'winners' && winners.value.length === 0) {
    loadWinners()
  }
})

const stats = ref({
  total_participants: 0,
  verified: 0,
  pending: 0,
  eligible_for_draw: 0
})

const participants = ref<any[]>([])
const participantsLoading = ref(false)
const searchQuery = ref('')
const filterVerified = ref('')

const drawLoading = ref(false)
const drawError = ref('')
const winnerMessage = ref('')
const latestWinner = ref<any>(null)

// Tab management
const activeTab = ref('participants')

// Winners history
const winners = ref<any[]>([])
const winnersLoading = ref(false)

// Load statistics
const loadStats = async () => {
  try {
    const data: any = await api.getStats()
    stats.value = data
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

// Load participants
const loadParticipants = async () => {
  participantsLoading.value = true
  try {
    const params: any = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (filterVerified.value) params.is_verified = filterVerified.value === 'true'

    const data: any = await api.getParticipants(params)
    participants.value = data.results || data
  } catch (error) {
    console.error('Error loading participants:', error)
  } finally {
    participantsLoading.value = false
  }
}

// Search handler with debounce
let searchTimeout: any = null
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadParticipants()
  }, 500)
}

// Load winners history
const loadWinners = async () => {
  winnersLoading.value = true
  try {
    const data: any = await api.getWinners()
    winners.value = data.results || data
  } catch (error) {
    console.error('Error loading winners:', error)
  } finally {
    winnersLoading.value = false
  }
}

// Draw winner with EPIC animation
const handleDraw = async () => {
  // Mostrar confirmación hermosa con SweetAlert2
  const result = await Swal.fire({
    title: '🎲 Realizar Sorteo',
    html: `
      <p class="text-lg mb-2">¿Estás seguro de realizar el sorteo?</p>
      <p class="text-sm text-gray-600">Se seleccionará un ganador aleatorio entre los <strong>${stats.value.eligible_for_draw}</strong> participantes elegibles.</p>
    `,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#9333ea',
    cancelButtonColor: '#6b7280',
    confirmButtonText: '¡Sí, sortear!',
    cancelButtonText: 'Cancelar',
    customClass: {
      popup: 'rounded-xl'
    }
  })

  if (!result.isConfirmed) return

  drawError.value = ''
  winnerMessage.value = ''
  latestWinner.value = null

  // Mostrar animación de sorteo
  let timerInterval: any
  Swal.fire({
    title: '🎰 Sorteando...',
    html: `
      <div class="py-8">
        <div class="text-6xl mb-4 animate-bounce">🎲</div>
        <div class="text-xl font-bold text-purple-600 mb-2">Girando el tambor...</div>
        <div class="text-gray-600">Seleccionando ganador aleatorio</div>
        <div class="mt-4">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-4 border-purple-600"></div>
        </div>
      </div>
    `,
    showConfirmButton: false,
    allowOutsideClick: false,
    didOpen: () => {
      // Agregar animación de pulso a los iconos
      const icon = Swal.getPopup()?.querySelector('.text-6xl')
      if (icon) {
        icon.classList.add('animate-pulse')
      }
    },
    willClose: () => {
      clearInterval(timerInterval)
    }
  })

  try {
    const response: any = await api.drawWinner()

    // Cerrar animación de sorteo
    Swal.close()

    // Lanzar confetti
    const duration = 5 * 1000
    const animationEnd = Date.now() + duration
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 10000 }

    function randomInRange(min: number, max: number) {
      return Math.random() * (max - min) + min
    }

    const interval: any = setInterval(function() {
      const timeLeft = animationEnd - Date.now()

      if (timeLeft <= 0) {
        return clearInterval(interval)
      }

      const particleCount = 50 * (timeLeft / duration)

      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
      })
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
      })
    }, 250)

    // Mostrar ganador con estilo
    await Swal.fire({
      title: '🎉 ¡Tenemos Ganador!',
      html: `
        <div class="py-6">
          <div class="text-7xl mb-6">🏆</div>
          <div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-6 mb-4">
            <h3 class="text-2xl font-bold text-purple-900 mb-4">${response.winner.participant_name}</h3>
            <div class="space-y-2 text-left">
              <p class="text-gray-700"><strong>📧 Email:</strong> ${response.winner.participant_email}</p>
              <p class="text-gray-700"><strong>📱 Teléfono:</strong> ${response.winner.participant_phone}</p>
            </div>
          </div>
          <p class="text-sm text-gray-600 italic">
            Ganador de: ${response.winner.prize_description || 'Estadía de 2 noches para pareja'}
          </p>
        </div>
      `,
      icon: 'success',
      confirmButtonColor: '#9333ea',
      confirmButtonText: '¡Genial!',
      customClass: {
        popup: 'rounded-xl',
        title: 'text-3xl'
      }
    })

    winnerMessage.value = response.message
    latestWinner.value = response.winner
    await loadStats()
    await loadParticipants()
    await loadWinners() // Reload winners history
  } catch (error: any) {
    Swal.close()
    await Swal.fire({
      title: '❌ Error',
      text: error.message || 'Error al realizar el sorteo',
      icon: 'error',
      confirmButtonColor: '#ef4444',
      confirmButtonText: 'Entendido'
    })
    drawError.value = error.message || 'Error al realizar el sorteo'
  }
}

// Logout
const handleLogout = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }
  router.push('/admin/login')
}

// Format date
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('es-CL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
