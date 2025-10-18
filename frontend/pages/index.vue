<template>
  <div class="min-h-screen bg-gradient-to-br from-pink-100 via-red-100 to-pink-200 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md mx-auto">
      <!-- Logo/Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-red-600 mb-2">
          Sorteo San Valentín
        </h1>
        <p class="text-xl text-gray-700">CTS Turismo</p>
        <p class="mt-4 text-gray-600">
          Gana una estadía romántica de 2 noches para una pareja
        </p>
      </div>

      <!-- Registration Form -->
      <div class="bg-white shadow-lg rounded-lg p-8">
        <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">
          Regístrate para Participar
        </h2>

        <!-- Success Message -->
        <div v-if="successMessage" class="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          {{ successMessage }}
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleSubmit" v-if="!successMessage">
          <div class="mb-4">
            <label for="full_name" class="block text-sm font-medium text-gray-700 mb-2">
              Nombre Completo *
            </label>
            <input
              id="full_name"
              v-model="form.full_name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="Juan Pérez"
            />
          </div>

          <div class="mb-4">
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Correo Electrónico *
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="correo@ejemplo.com"
            />
          </div>

          <div class="mb-6">
            <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
              Teléfono *
            </label>
            <input
              id="phone"
              v-model="form.phone"
              type="tel"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="+56912345678"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-red-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-red-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Registrando...' : 'Registrarme' }}
          </button>
        </form>

        <!-- Link to Admin Login -->
        <div class="mt-6 text-center">
          <NuxtLink to="/admin/login" class="text-sm text-red-600 hover:text-red-700">
            Acceso Administrador
          </NuxtLink>
        </div>
      </div>

      <!-- Info Section -->
      <div class="mt-8 bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">
          ¿Cómo participar?
        </h3>
        <ol class="list-decimal list-inside space-y-2 text-gray-600">
          <li>Completa el formulario de registro</li>
          <li>Revisa tu correo electrónico y verifica tu cuenta</li>
          <li>Crea tu contraseña para confirmar tu participación</li>
          <li>¡Listo! Ya estás participando por el premio</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()

const form = ref({
  full_name: '',
  email: '',
  phone: ''
})

const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response: any = await api.registerParticipant(form.value)
    successMessage.value = response.message
    form.value = { full_name: '', email: '', phone: '' }
  } catch (error: any) {
    errorMessage.value = error.message || 'Error al registrarse. Intenta nuevamente.'
  } finally {
    loading.value = false
  }
}
</script>
