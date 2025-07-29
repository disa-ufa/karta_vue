<template>
  <div>
    <!-- Если пользователь авторизован, показываем личный кабинет -->
    <Profile v-if="isLoggedIn" @logout="handleLogout" />

    <!-- Если не авторизован — карта + панель + модалка входа/регистрации -->
    <template v-else>
      <YandexMap @open-auth="showAuth = true" />
      <LeftPanel
        :ministries="ministries"
        @open-auth="showAuth = true"
      />
      <AuthModal
        :show="showAuth"
        :isLogin="isLoginTab"
        :ministries="ministries"
        @close="showAuth = false"
        @login="handleLogin"
        @switchTab="val => isLoginTab = val"
      />
    </template>

    <!-- Скрытая ссылка для админки -->
    <div style="position: fixed; bottom: 8px; right: 16px; opacity: 0.5; z-index:12000;">
      <a href="#" @click.prevent="showAdmin = true">Админка</a>
    </div>

    <!-- Модальное окно для админки -->
    <div v-if="showAdmin" style="position: fixed; top:0; left:0; width:100vw; height:100vh; background:#fff; z-index:20000;">
      <button style="float:right; margin:8px;" @click="showAdmin = false">Закрыть</button>
      <AdminPanel />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import YandexMap from './components/YandexMap.vue'
import AuthModal from './components/AuthModal.vue'
import AdminPanel from './components/AdminPanel.vue'
import Profile from './components/Profile.vue'
import LeftPanel from './components/LeftPanel.vue'

// Единый список ведомств
const ministries = [
  'Министерство просвещения Р.Б.',
  'Министерство спорта Р.Б.',
  'Министерство культуры Р.Б.',
  'Министерство здравоохранения Р.Б.',
  'Министерство труда и социальной защиты Р.Б.'
]

const showAdmin = ref(false)
const showAuth = ref(false)
const isLoginTab = ref(true)
const isLoggedIn = ref(!!localStorage.getItem('user_token'))

function handleLogin({ email, password }) {
  // Тут должна быть логика обращения к API, пример:
  // fetch(...).then(...)
  // Пока просто эмулируем успешный вход:
  localStorage.setItem('user_token', 'test') // заменишь на свой токен
  isLoggedIn.value = true
  showAuth.value = false
}

function handleLogout() {
  isLoggedIn.value = false
  localStorage.removeItem('user_token')
}
</script>
