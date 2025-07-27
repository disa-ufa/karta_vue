<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  isLogin: Boolean,
  loading: Boolean,
  error: String,
  ministries: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'login', 'register', 'switchTab'])

const loginEmail = ref('')
const loginPassword = ref('')

const regEmail = ref('')
const regPassword = ref('')
const regPasswordRepeat = ref('')
const regName = ref('')
const regMinistry = ref('')
const regContactName = ref('')
const regContactPhone = ref('')

const localError = ref('')
const registrationSuccess = ref(false)

watch(() => props.show, show => {
  if (!show) {
    loginEmail.value = ''
    loginPassword.value = ''
    regEmail.value = ''
    regPassword.value = ''
    regPasswordRepeat.value = ''
    regName.value = ''
    regMinistry.value = ''
    regContactName.value = ''
    regContactPhone.value = ''
    localError.value = ''
    registrationSuccess.value = false
  }
})

// Маска телефона: +7 (___) ___-__-__
function onPhoneInput(e) {
  let value = e.target.value.replace(/\D/g, '')
  if (value.startsWith('7')) value = value.slice(1)
  if (value.length > 10) value = value.slice(0, 10)
  let masked = '+7 ('
  if (value.length) masked += value.substring(0, 3)
  if (value.length >= 3) masked += ') '
  if (value.length >= 4) masked += value.substring(3, 6)
  if (value.length >= 6) masked += '-' + value.substring(6, 8)
  if (value.length >= 8) masked += '-' + value.substring(8, 10)
  regContactPhone.value = masked
}

// Проверка сложности пароля
function isStrongPassword(password) {
  // минимум 6 символов, хотя бы 1 буква и 1 цифра
  return /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/.test(password)
}

function handleLogin() {
  emit('login', { email: loginEmail.value, password: loginPassword.value })
}

async function handleRegister() {
  localError.value = ''
  registrationSuccess.value = false

  if (regPassword.value !== regPasswordRepeat.value) {
    localError.value = 'Пароли не совпадают'
    return
  }
  if (!isStrongPassword(regPassword.value)) {
    localError.value = 'Пароль должен быть не менее 6 символов и содержать буквы и цифры'
    return
  }
  if (!regMinistry.value) {
    localError.value = 'Выберите ведомство'
    return
  }

  // Отправляем запрос на сервер
  try {
    const response = await fetch('http://136.169.171.150:7777/api/register-request', {

      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        orgName: regName.value,
        ministry: regMinistry.value,
        contactName: regContactName.value,
        contactPhone: regContactPhone.value,
        email: regEmail.value,
        password: regPassword.value
      })
    })

    if (response.ok) {
      registrationSuccess.value = true
      // Сброс формы
      regEmail.value = ''
      regPassword.value = ''
      regPasswordRepeat.value = ''
      regName.value = ''
      regMinistry.value = ''
      regContactName.value = ''
      regContactPhone.value = ''
    } else {
      const err = await response.json()
      localError.value = err?.error || 'Ошибка при отправке заявки'
    }
  } catch (e) {
    localError.value = 'Ошибка соединения с сервером'
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="auth-modal">
      <div class="tabs">
        <button :class="{active: isLogin}" @click="$emit('switchTab', true)">Вход</button>
        <button :class="{active: !isLogin}" @click="$emit('switchTab', false)">Регистрация</button>
      </div>
      <div class="modal-content">
        <!-- Вход -->
        <form v-if="isLogin" @submit.prevent="handleLogin" autocomplete="on">
          <input type="email" v-model="loginEmail" placeholder="E-mail" autocomplete="username" required />
          <input type="password" v-model="loginPassword" placeholder="Пароль" autocomplete="current-password" required />
          <button type="submit" class="modal-btn" :disabled="loading">Войти</button>
        </form>
        <!-- Регистрация -->
        <form v-else @submit.prevent="handleRegister" autocomplete="on" v-if="!registrationSuccess">
          <input type="text" v-model="regName" placeholder="Наименование организации" required />

          <select v-model="regMinistry" required>
            <option value="" disabled>Выберите ведомство</option>
            <option v-for="m in ministries" :key="m" :value="m">{{ m }}</option>
          </select>

          <input type="text" v-model="regContactName" placeholder="ФИО контактного лица" required />

          <input
            type="tel"
            v-model="regContactPhone"
            @input="onPhoneInput"
            maxlength="18"
            placeholder="+7 (___) ___-__-__"
            required
            autocomplete="tel"
          />

          <input type="email" v-model="regEmail" placeholder="E-mail" required autocomplete="username" />
          <input type="password" v-model="regPassword" placeholder="Пароль" required autocomplete="new-password" />
          <input type="password" v-model="regPasswordRepeat" placeholder="Повторите пароль" required autocomplete="new-password" />
          <button type="submit" class="modal-btn" :disabled="loading">Зарегистрироваться</button>
        </form>
        <div v-if="registrationSuccess" class="modal-success">
          Заявка принята и будет рассмотрена модератором.<br>
          Результат будет отправлен на email.
        </div>
        <div v-if="localError" class="modal-error">{{ localError }}</div>
        <div v-else-if="error" class="modal-error">{{ error }}</div>
      </div>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(51,61,81,0.20); z-index: 9999;
  display: flex; align-items: center; justify-content: center;
}
.auth-modal {
  background: #fff; border-radius: 14px; box-shadow: 0 8px 48px rgba(60,80,100,0.19);
  padding: 28px 28px 20px 28px; width: 370px; position: relative;
}
.tabs {
  display: flex; justify-content: center; margin-bottom: 18px; gap: 10px;
}
.tabs button {
  background: none; border: none; font-size: 16px; color: #999;
  padding: 5px 12px; border-radius: 7px; cursor: pointer;
  transition: background 0.17s, color 0.17s;
}
.tabs button.active {
  background: #f2faff; color: #2962ff; font-weight: bold;
}
.modal-content input,
.modal-content select {
  width: 100%; margin-bottom: 13px; padding: 8px 11px;
  border: 1.2px solid #e5e5e5; border-radius: 6px; font-size: 15px;
}
.modal-content select:invalid { color: #a7a7a7; }
.modal-btn {
  width: 100%; background: #36c900; color: #fff; border: none;
  padding: 10px 0; border-radius: 8px; font-size: 16px;
  font-weight: bold; cursor: pointer; margin-top: 2px;
  transition: background 0.17s;
}
.close-btn {
  position: absolute; top: 12px; right: 13px; font-size: 22px;
  border: none; background: none; color: #888; cursor: pointer; padding: 0;
}
.modal-error {
  color: #f33; font-size: 14px; margin-top: 8px; text-align: center;
}
.modal-success {
  color: #36c900;
  font-size: 16px;
  text-align: center;
  margin: 26px 0 12px 0;
  font-weight: 500;
  line-height: 1.5;
}
</style>
