<script setup>
import { computed } from 'vue'
const props = defineProps({
  visibleLayers: { type: Object, required: true },
  ageGroups: { type: [Array, Object], default: () => [] },
  accessibility: { type: [Array, Object], default: () => [] },
  allAgeGroups: { type: Array, required: true },
  allAccessibility: { type: Array, required: true }
})
const emit = defineEmits(['update:ageGroups', 'update:accessibility'])

const ageGroupsArray = computed(() => Array.isArray(props.ageGroups) ? props.ageGroups : props.ageGroups.value)
const accessibilityArray = computed(() => Array.isArray(props.accessibility) ? props.accessibility : props.accessibility.value)

function toggleAgeGroup(val) {
  const arr = [...ageGroupsArray.value]
  if (arr.includes(val)) {
    const next = arr.filter(v => v !== val)
    console.log('[LeftPanel] toggleAgeGroup:', val, '->', next)
    emit('update:ageGroups', next)
  } else {
    arr.push(val)
    console.log('[LeftPanel] toggleAgeGroup:', val, '->', arr)
    emit('update:ageGroups', arr)
  }
}
function toggleAccessibility(val) {
  const arr = [...accessibilityArray.value]
  if (arr.includes(val)) {
    const next = arr.filter(v => v !== val)
    console.log('[LeftPanel] toggleAccessibility:', val, '->', next)
    emit('update:accessibility', next)
  } else {
    arr.push(val)
    console.log('[LeftPanel] toggleAccessibility:', val, '->', arr)
    emit('update:accessibility', arr)
  }
}
</script>

<template>
  <div class="panel">
    <h3>Ведомства</h3>
    <label><input type="checkbox" v-model="visibleLayers.layer1"> Министерство образования Р.Б.</label><br>
    <label><input type="checkbox" v-model="visibleLayers.layer2"> Министерство здравоохранения Р.Б.</label><br>
    <label><input type="checkbox" v-model="visibleLayers.layer3"> Министерство культуры Р.Б.</label><br>
    <hr>
    <h4>Возрастная группа</h4>
    <div>
      <label v-for="val in allAgeGroups" :key="val">
        <input type="checkbox"
               :value="val"
               :checked="ageGroupsArray.includes(val)"
               @change="toggleAgeGroup(val)">
        {{ val }}
      </label>
    </div>
    <h4>Доступная среда</h4>
    <div>
      <label v-for="val in allAccessibility" :key="val" style="margin-right: 8px;">
        <input type="checkbox"
               :value="val"
               :checked="accessibilityArray.includes(val)"
               @change="toggleAccessibility(val)">
        {{ val }}
      </label>
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
</style>
