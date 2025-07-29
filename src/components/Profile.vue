<template>
  <div class="profile-wrapper">
    <div class="profile-card">
      <h2>Личный кабинет</h2>
      <form @submit.prevent="saveProfile">
        <div class="form-group">
          <label>Наименование организации</label>
          <input v-model="profile.name" required />
        </div>
        <div class="form-group">
          <label>Юридический адрес</label>
          <textarea v-model="profile.address" rows="2" />
        </div>
        <div class="form-group">
          <label>Официальный сайт</label>
          <input v-model="profile.website" type="url" placeholder="https://example.com" />
        </div>
        <div class="form-group">
          <label>Телефон</label>
          <input v-model="profile.phone" type="tel" placeholder="+7 (___) ___-__-__" />
        </div>
        <div class="form-group">
          <label>Координаты</label>
          <input v-model="coordsInput" placeholder="55.12345, 54.12345" />
        </div>
        <!-- Остальные поля по аналогии -->
        <button class="save-btn" :disabled="loading">{{ loading ? 'Сохраняю...' : 'Сохранить' }}</button>
        <button type="button" class="logout-btn" @click="$emit('logout')">Выйти</button>
        <div v-if="success" class="success-msg">Изменения сохранены!</div>
        <div v-if="error" class="error-msg">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const profile = ref({})
const success = ref(false)
const error = ref('')
const loading = ref(false)
const coordsInput = ref('')

function parseCoords(str) {
  if (!str) return []
  const arr = str.split(',').map(x => parseFloat(x.trim()))
  return arr.length === 2 && arr.every(Number.isFinite) ? arr : []
}
function coordsToStr(arr) {
  return Array.isArray(arr) && arr.length === 2 ? arr.join(', ') : ''
}

onMounted(async () => {
  const token = localStorage.getItem('user_token')
  const res = await fetch('http://136.169.171.150:8888/api/profile', {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.ok) {
    const data = await res.json()
    profile.value = data
    coordsInput.value = coordsToStr(data.coords)
  } else {
    error.value = 'Ошибка загрузки профиля'
  }
})

watch(coordsInput, val => {
  profile.value.coords = parseCoords(val)
})

async function saveProfile() {
  loading.value = true
  success.value = false
  error.value = ''
  const token = localStorage.getItem('user_token')
  // Корректно передаём координаты
  profile.value.coords = parseCoords(coordsInput.value)
  const res = await fetch('http://136.169.171.150:8888/api/profile', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(profile.value)
  })
  loading.value = false
  if (res.ok) {
    success.value = true
    error.value = ''
  } else {
    error.value = 'Ошибка сохранения'
    success.value = false
  }
}
</script>

<style scoped>
.profile-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f9fa;
}
.profile-card {
  background: #fff;
  padding: 36px 32px 28px 32px;
  border-radius: 16px;
  box-shadow: 0 8px 48px rgba(60,80,100,0.09);
  width: 430px;
  max-width: 98vw;
}
h2 {
  text-align: center;
  margin-bottom: 26px;
  font-size: 23px;
  color: #222;
  font-weight: 600;
}
.form-group {
  margin-bottom: 19px;
}
label {
  display: block;
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 7px;
  color: #384358;
}
input,
textarea {
  width: 100%;
  padding: 9px 12px;
  border: 1.3px solid #e5e5e5;
  border-radius: 7px;
  font-size: 15px;
  background: #f9fbfc;
  box-sizing: border-box;
  outline: none;
  transition: border 0.14s;
}
input:focus,
textarea:focus {
  border-color: #36c900;
}
.save-btn {
  width: 100%;
  padding: 12px 0;
  background: #36c900;
  color: #fff;
  border: none;
  border-radius: 9px;
  font-size: 16px;
  font-weight: bold;
  margin-top: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background 0.17s;
}
.save-btn:disabled {
  background: #b9e4b1;
  cursor: not-allowed;
}
.logout-btn {
  width: 100%;
  padding: 10px 0;
  background: #eee;
  color: #888;
  border: none;
  border-radius: 9px;
  font-size: 15px;
  font-weight: 500;
  margin-top: 4px;
  cursor: pointer;
  transition: background 0.17s;
}
.logout-btn:hover {
  background: #ffeaea;
  color: #e24c4c;
}
.success-msg {
  margin-top: 13px;
  color: #36c900;
  font-size: 15px;
  text-align: center;
}
.error-msg {
  margin-top: 13px;
  color: #d9292a;
  font-size: 15px;
  text-align: center;
}
</style>
