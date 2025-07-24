<template>
  <div class="panel">
    <h3>Ведомства</h3>
    <label><input type="checkbox" v-model="visibleLayers.layer1"> Министерство образования Р.Б.</label><br>
    <label><input type="checkbox" v-model="visibleLayers.layer2"> Министерство здравоохранения Р.Б.</label><br>
    <label><input type="checkbox" v-model="visibleLayers.layer3"> Министерство культуры Р.Б.</label><br>
    <!-- Можно добавить фильтры, поиск и т.п. -->
  </div>
</template>

<script setup>
defineProps(['visibleLayers'])
</script>

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
