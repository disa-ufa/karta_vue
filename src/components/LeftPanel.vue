<script setup>
import { ref, watch, computed } from 'vue'
import AuthModal from './AuthModal.vue'

const props = defineProps({
  visibleLayers: { type: Object, required: false, default: () => ({}) },
  ageGroups: { type: [Array, Object], default: () => [] },
  accessibility: { type: [Array, Object], default: () => [] },
  allAgeGroups: { type: Array, default: () => [] },
  allOrganizations: { type: Array, default: () => [] },
  ministries: { type: Array, default: () => [] }, // <- теперь как prop
})

const emit = defineEmits([
  'update:ageGroups',
  'update:accessibility',
  'search',
  'selectOrg',
  'open-auth'
])

const LAYER_LABELS = {
  layer1: 'Министерство просвещения Р.Б.',
  layer2: 'Министерство спорта Р.Б.',
  layer3: 'Министерство культуры Р.Б.',
  layer4: 'Министерство здравоохранения Р.Б.',
  layer5: 'Министерство труда и социальной защиты Р.Б.'
}

const localAgeGroups = ref([...props.ageGroups])
const localAccessibilityEnabled = ref(props.accessibility.includes('Да'))

// --- AUTH MODAL (если хочешь, можно убрать этот AuthModal и оставить только открытие из App.vue)
const showAuthModal = ref(false)
const isLoginTab = ref(true)
const authError = ref('')
const authLoading = ref(false)

function openAuth() {
  emit('open-auth') // теперь только эмитим вверх!
}

function closeAuth() {
  showAuthModal.value = false
  authError.value = ''
}

// --- SEARCH ---
const searchInput = ref('')
const showDropdown = ref(false)
const searchResults = computed(() => {
  if (!searchInput.value.trim()) return []
  const query = searchInput.value.trim().toLowerCase()
  return props.allOrganizations.filter(
    org =>
      (org.name || '').toLowerCase().includes(query) ||
      (org.address || '').toLowerCase().includes(query)
  ).slice(0, 12)
})

function handleSearchInput(e) {
  searchInput.value = e.target.value
  emit('search', searchInput.value)
  showDropdown.value = !!searchInput.value.trim()
}
function clearSearch() {
  searchInput.value = ''
  emit('search', '')
  showDropdown.value = false
}
function onFocusSearch() {
  if (searchInput.value.trim()) showDropdown.value = true
}
function selectOrgFromDropdown(org) {
  emit('selectOrg', org)
  showDropdown.value = false
  searchInput.value = org.name
}

// --- FILTERS ---
const hasChanges = computed(() => {
  const originalAge = [...props.ageGroups].sort().join(',')
  const localAge = [...localAgeGroups.value].sort().join(',')
  const originalAcc = props.accessibility.includes('Да')
  const localAcc = localAccessibilityEnabled.value
  return originalAge !== localAge || originalAcc !== localAcc
})

watch(() => props.ageGroups, val => {
  localAgeGroups.value = [...val]
})
watch(() => props.accessibility, val => {
  localAccessibilityEnabled.value = val.includes('Да')
})

function toggleLocalAgeGroup(val) {
  const arr = [...localAgeGroups.value]
  if (arr.includes(val)) {
    arr.splice(arr.indexOf(val), 1)
  } else {
    arr.push(val)
  }
  if (arr.length === 0) {
    localAgeGroups.value = [...props.allAgeGroups]
  } else {
    localAgeGroups.value = arr
  }
}
function toggleAccessibility() {
  localAccessibilityEnabled.value = !localAccessibilityEnabled.value
}
function applyFilters() {
  if (localAgeGroups.value.length === 0) {
    localAgeGroups.value = [...props.allAgeGroups]
  }
  emit('update:ageGroups', localAgeGroups.value)
  emit('update:accessibility', localAccessibilityEnabled.value ? ['Да'] : [])
}
function cancelFilters() {
  localAgeGroups.value = [...props.ageGroups]
  localAccessibilityEnabled.value = props.accessibility.includes('Да')
}
function resetFilters() {
  localAgeGroups.value = [...props.allAgeGroups]
  localAccessibilityEnabled.value = false
  applyFilters()
}
</script>

<template>
  <div class="panel">

    <!-- Вход/Регистрация -->
    <button class="reset-btn auth-link" @click="openAuth">Вход / Регистрация</button>
    
    <!-- Поиск -->
    <div class="search-bar" @click.stop>
      <span class="search-icon">&#128269;</span>
      <input
        class="search-input"
        type="text"
        :placeholder="'Поиск и выбор мест'"
        v-model="searchInput"
        @input="handleSearchInput"
        @focus="onFocusSearch"
        @keydown.esc="showDropdown=false"
      />
      <span class="search-clear" v-if="searchInput" @click="clearSearch">&#10005;</span>
      <div
        v-if="showDropdown && searchResults.length"
        class="search-dropdown"
      >
        <div
          v-for="org in searchResults"
          :key="org.id"
          class="search-item"
          @mousedown.prevent="selectOrgFromDropdown(org)"
        >
          <span class="search-item-title">{{ org.name }}</span>
          <span class="search-item-address">{{ org.address }}</span>
        </div>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="panel-section">
      <div class="section-title">Ведомства</div>
      <label v-for="key in Object.keys(visibleLayers)" :key="key" class="checkbox-row">
        <input type="checkbox" v-model="visibleLayers[key]"/>
        {{ LAYER_LABELS[key] || key }}
      </label>
    </div>
    <hr class="panel-divider"/>
    <div class="panel-section">
      <div class="panel-header">
        <span class="panel-title">Фильтры</span>
        <button class="reset-btn" @click="resetFilters">Сбросить</button>
      </div>
      <div class="section-title">Возрастная группа</div>
      <div class="age-checkbox-row">
        <label v-for="val in props.allAgeGroups" :key="val" class="checkbox-inline">
          <input type="checkbox"
                :value="val"
                :checked="localAgeGroups.includes(val)"
                @change="toggleLocalAgeGroup(val)">
          {{ val }}
        </label>
      </div>
    </div>
    <div class="panel-section">
      <div class="section-title">Доступная среда</div>
      <button
        @click="toggleAccessibility"
        :class="['accessibility-btn', { selected: localAccessibilityEnabled }]"
        type="button"
      >
        Да
      </button>
    </div>
    <div class="actions">
      <button
        class="btn-apply"
        :class="{ disabled: !hasChanges }"
        :disabled="!hasChanges"
        @click="applyFilters"
      >
        Применить
      </button>
      <button class="btn-cancel" @click="cancelFilters">Отмена</button>
    </div>
  </div>
</template>






<style scoped>
.panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 320px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(51, 61, 81, 0.07);
  padding: 22px 20px 20px 20px;
  font-family: 'Segoe UI', 'Arial', sans-serif;
  z-index: 20;
  border: 1px solid #e5e5e5;
}

.auth-link {
  font-size: 14px;
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  transition: color 0.18s;
  margin-bottom: 18px;
  padding: 0;
  /* float: right; <-- убрать эту строку */
  text-align: left;
  display: block; /* для корректного выравнивания на всю ширину */
}

.auth-link:hover {
  color: #36c900;
  text-decoration: underline;
}
.search-bar {
  display: flex;
  align-items: center;
  background: #f7f7f7;
  border-radius: 24px;
  padding: 0 12px;
  margin-bottom: 16px;
  height: 44px;
  box-shadow: 0 2px 8px 0 #24252912;
  position: relative;
}
.search-bar .search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  flex: 1;
  height: 40px;
  padding-left: 0;
}
.search-icon { font-size: 18px; color: #c4c4c4; margin-right: 5px; }
.search-clear { cursor: pointer; font-size: 18px; color: #bbb; margin-left: 3px; }
.search-clear:hover { color: #ff3b3b; }
.search-dropdown {
  position: absolute; left: 0; top: 44px; background: #fff; border-radius: 13px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.09); width: 100%; z-index: 30;
  max-height: 520px; overflow-y: auto;
}
.search-item { padding: 9px 14px; cursor: pointer; border-bottom: 1px solid #f1f1f1; }
.search-item:last-child { border-bottom: none; }
.search-item:hover { background: #f4f9fd; }
.search-item-title { font-weight: 500; display: block; color: #222; font-size: 15px; }
.search-item-address { display: block; font-size: 13px; color: #888; }
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.panel-title { font-weight: 600; font-size: 18px; }
.reset-btn {
  font-size: 14px;
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  transition: color 0.18s;
  margin-left: 8px;
  padding: 0;
}
.reset-btn:hover { color: #36c900; text-decoration: underline; }
.section-title { font-weight: 500; font-size: 15px; margin-bottom: 4px; }
.checkbox-row { display: block; margin-bottom: 3px; font-size: 15px; }
.age-checkbox-row { display: flex; gap: 16px; }
.checkbox-inline { display: flex; align-items: center; gap: 5px; font-size: 15px; }
.accessibility-btn {
  border: 1.5px solid #a1aeb8;
  border-radius: 8px;
  padding: 5px 16px;
  background: #f5f6fa;
  color: #333;
  font-size: 15px;
  cursor: pointer;
  margin-top: 6px;
  outline: none;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.accessibility-btn.selected {
  background: #e5ffe6;
  color: #36c900;
  border-color: #36c900;
  font-weight: bold;
}
.panel-divider {
  border: none;
  border-top: 1px solid #eaeaea;
  margin: 12px 0;
}
.actions {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
}
.btn-apply, .btn-cancel {
  padding: 8px 16px;
  font-size: 15px;
  cursor: pointer;
  border-radius: 8px;
  border: none;
}
.btn-apply {
  background-color: #36c900;
  color: white;
  opacity: 1;
  transition: opacity 0.2s, background 0.15s;
}
.btn-apply.disabled {
  background-color: #e5e5e5 !important;
  color: #aaa !important;
  cursor: not-allowed;
  opacity: 1;
}
.btn-cancel {
  background: none;
  color: #3d64ff;
}
.btn-cancel:hover { text-decoration: underline; }
</style>
