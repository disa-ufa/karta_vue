<template>
  <div class="sidebar-card">
    <button class="sidebar-close" @click="$emit('close')">×</button>
    <div class="sidebar-scroll">
      <img v-if="org.image" :src="org.image" alt="" class="sidebar-image" />
      <h2 class="sidebar-title">{{ org.name }}</h2>
      <div class="sidebar-subtitle">{{ org.subtitle }}</div>
      <div class="sidebar-rating">
        <span v-if="org.rating" class="sidebar-star">★</span>
        <span v-if="org.rating" class="sidebar-rating-value">{{ org.rating }}</span>
        <span v-if="org.ratingCount" class="sidebar-rating-count">({{ org.ratingCount }} оценок)</span>
      </div>
      <div class="sidebar-status" :class="{ closed: org.status && org.status.includes('Закрыто') }">
        {{ org.status }}
      </div>
      <div class="sidebar-section"><b>Адрес:</b> {{ org.address }}</div>
      <div class="sidebar-section"><b>Телефон:</b> {{ org.phone }}</div>
      <div class="sidebar-section"><b>Сайт:</b> <a :href="org.website" target="_blank">{{ org.website }}</a></div>

      <!-- КОНКРЕТНЫЕ ПОЛЯ -->
      <div class="sidebar-section"><b>Форма:</b> {{ org.rehab_form }}</div>
      <div class="sidebar-section"><b>Возрастная группа:</b> {{ org.age_group }}</div>
      <div class="sidebar-section"><b>Доступная среда:</b> {{ org.accessibility }}</div>
      <div class="sidebar-section"><b>Профиль:</b> {{ org.profile }}</div>
      <div class="sidebar-section"><b>Перечень услуг:</b>
        <ul v-if="org.services">
          <li v-for="(service, i) in org.services.split('\n')" :key="i">{{ service }}</li>
        </ul>
      </div>
      <div class="sidebar-section"><b>Перечень специалистов:</b>
        <ul v-if="org.specialists">
          <li v-for="(spec, i) in org.specialists.split('\n')" :key="i">{{ spec }}</li>
        </ul>
      </div>

      
    </div>
  </div>
</template>

<script setup>
defineProps(['org'])
defineEmits(['close'])
</script>

<style scoped>
/* Стили из предыдущей версии (sidebar-card, .sidebar-section и т.д.) */
.sidebar-card {
  position: fixed;
  top: 0;
  right: 0;
  width: 420px;
  height: 100vh;
  background: #fff;
  box-shadow: -3px 0 16px 0 rgba(60,65,94,.14), -2px 0 6px 0 rgba(60,65,94,.04);
  z-index: 20000;
  display: flex;
  flex-direction: column;
  animation: slideInSidebar .23s cubic-bezier(.4,0,.2,1);
  overflow: hidden;
}
@keyframes slideInSidebar {
  from { right: -420px; opacity: 0; }
  to { right: 0; opacity: 1; }
}
.sidebar-close {
  position: absolute;
  top: 14px;
  right: 16px;
  font-size: 28px;
  border: none;
  background: none;
  color: #888;
  cursor: pointer;
  z-index: 2;
}
.sidebar-scroll {
  overflow-y: auto;
  padding: 38px 28px 24px 28px;
  flex: 1 1 auto;
  font-family: sans-serif;
}
.sidebar-image {
  width: 100%;
  border-radius: 7px;
  margin-bottom: 16px;
  max-height: 185px;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0,0,0,0.11);
}
.sidebar-title {
  font-size: 1.3em;
  font-weight: 600;
  margin-bottom: 7px;
}
.sidebar-section {
  margin-bottom: 9px;
  font-size: 1em;
}
.btn-green {
  background: #36c900;
  border: none;
  padding: 12px 19px;
  color: white;
  font-weight: bold;
  margin-top: 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.08em;
  width: 100%;
}
</style>
