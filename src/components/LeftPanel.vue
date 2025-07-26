<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  visibleLayers: { type: Object, required: true },
  ageGroups: { type: [Array, Object], default: () => [] },
  accessibility: { type: [Array, Object], default: () => [] },
  allAgeGroups: { type: Array, required: true }
})

const emit = defineEmits(['update:ageGroups', 'update:accessibility'])

const localAgeGroups = ref([...props.ageGroups])
const localAccessibilityEnabled = ref(props.accessibility.includes('Да'))

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
  emit('update:ageGroups', localAgeGroups.value)
  emit('update:accessibility', [])
}
</script>

<template>
  <div class="panel">

    <h4>Ведомства</h4>
    <label><input type="checkbox" v-model="visibleLayers.layer1"> Министерство образования Р.Б.</label><br>
    <label><input type="checkbox" v-model="visibleLayers.layer2"> Министерство здравоохранения Р.Б.</label><br>
    <label><input type="checkbox" v-model="visibleLayers.layer3"> Министерство культуры Р.Б.</label><br>
    <hr>

    <div class="header">
      <h3>Фильтры</h3>
      <button class="reset-button" @click="resetFilters">Сбросить</button>
    </div>

    <h4>Возрастная группа</h4>
<div class="age-group-row">
  <label v-for="val in allAgeGroups" :key="val" class="age-checkbox">
    <input
      type="checkbox"
      :value="val"
      :checked="localAgeGroups.includes(val)"
      @change="toggleLocalAgeGroup(val)"
    />
    {{ val }}
  </label>
</div>


    <h4>Доступная среда</h4>
    <div>
      <button
        @click="toggleAccessibility"
        :class="{ 'selected': localAccessibilityEnabled }"
        class="accessibility-button"
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
  top: 10px;
  left: 10px;
  background: white;
  padding: 10px;
  z-index: 9999;
  border: 1px solid black;
  border-radius: 5px;
  font-family: sans-serif;
  width: 230px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.reset-button {
  background: none;
  border: none;
  color: #aaa;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}
.reset-button:hover {
  color: #000;
}

.age-group-list label {
  display: block;
  margin-bottom: 4px;
}

.accessibility-button {
  padding: 6px 12px;
  border: 1px solid #ccc;
  background: #f5f5f5;
  cursor: pointer;
  border-radius: 5px;
  font-size: 14px;
}
.accessibility-button.selected {
  background-color: #36c900;
  color: white;
  border-color: #36c900;
}

.actions {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
}
.btn-apply, .btn-cancel {
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;
  border: none;
}
.btn-apply {
  background-color: #36c900;
  color: white;
  opacity: 1;
  transition: opacity 0.2s;
}
.btn-apply.disabled {
  background-color: #ccc !important;
  cursor: not-allowed;
  opacity: 0.7;
}
.btn-cancel {
  background: none;
  color: #007bff;
}
</style>
