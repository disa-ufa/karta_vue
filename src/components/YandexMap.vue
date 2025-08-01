<template>
  <div>
<LeftPanel
  v-show="!isPanelCollapsed" 
  class="map-panel"
  :visibleLayers="visibleLayers"
  :ageGroups="ageGroups"
  :accessibility="accessibility"
  :allAgeGroups="allAgeGroups"
  :allOrganizations="allOrganizations"
  @update:ageGroups="val => ageGroups.splice(0, ageGroups.length, ...val)"
  @update:accessibility="val => accessibility.splice(0, accessibility.length, ...val)"
  @selectOrg="handleSelectOrganization"
  @collapse="isPanelCollapsed = true"
/>

<!-- Кнопка для раскрытия панели -->
<button
  v-if="isPanelCollapsed"
  class="panel-toggle-btn"
  @click="isPanelCollapsed = false"
  title="Показать панель"
>
  <svg width="22" height="22" viewBox="0 0 20 20">
    <path d="M7 5l6 5-6 5" stroke="#666" stroke-width="2.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</button>

    <div id="map" ref="mapRef" style="width: 100vw; height: 100vh; position: relative;"></div>
    <transition name="sidebar">
      <SidebarCard v-if="selectedOrg" :org="selectedOrg" @close="selectedOrg = null" />
    </transition>
    <div
      v-if="hoveredOrg"
      :style="previewCardStyle"
      class="preview-card"
      @mouseenter="isPreviewHovered = true"
      @mouseleave="handlePreviewLeave"
    >
      <div><b>{{ hoveredOrg.name }}</b></div>
      <div>Адрес: {{ hoveredOrg.address }}</div>
      <div>Телефон: {{ hoveredOrg.phone }}</div>
      <div>
        Сайт:
        <a :href="hoveredOrg.website" target="_blank" style="color: #1aaf5d;">
          {{ hoveredOrg.website }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed, nextTick } from 'vue'
import LeftPanel from './LeftPanel.vue'
import SidebarCard from './SidebarCard.vue'

const isPanelCollapsed = ref(false)
const allAgeGroups = ['0-18', '18+', 'СВО']
const allAccessibility = ['Да', 'Нет']
const ageGroups = reactive([...allAgeGroups])
const accessibility = reactive([])

const visibleLayers = reactive({
  
  layer1_1: true,
  layer1_2: true,
  layer1_3: true,
  layer2: true,
  layer3: true,
  layer4: true,
  layer5: true
})

const layerFiles = {
  layer1_1: '/objects1-1.json',
  layer1_2: '/objects1-2.json',
  layer1_3: '/objects1-3.json',
  layer2: '/objects2.json',
  layer3: '/objects3.json',
  layer4: '/objects4.json',
  layer5: '/objects5.json'
}

const layerPresets = {
  layer1_1: 'islands#redIcon',        // Муниципальные ОО
  layer1_2: 'islands#orangeIcon',     // Коррекционные ОО
  layer1_3: 'islands#brownIcon',      // ПМПК
  layer2: 'islands#blueIcon',
  layer3: 'islands#greenIcon',
  layer4: 'islands#violetIcon',
  layer5: 'islands#yellowIcon'
}

const mapRef = ref(null)
const objectManagers = {}
let mapInstance = null

const selectedOrg = ref(null)
const hoveredOrg = ref(null)
const previewCoords = ref({ x: 0, y: 0 })
const isPreviewHovered = ref(false)
const allOrganizations = ref([])

function filterFeature(obj) {
  const accVal = (obj.properties.accessibility || '').toLowerCase().trim()
  const ageVal = (obj.properties.age_group || '').toLowerCase().trim()
  let ageOk = true, accOk = true
  const accFilter = Array.isArray(accessibility) ? [...accessibility] : []
  const ageFilter = Array.isArray(ageGroups) ? [...ageGroups] : []
  if (ageFilter.length > 0) ageOk = ageFilter.some(group => ageVal.includes(group.toLowerCase().trim()))
  if (accFilter.length > 0) accOk = accFilter.some(val => accVal === val.toLowerCase().trim())
  return ageOk && accOk
}

function applyFiltersToAllLayers() {
  for (const layerId in objectManagers) {
    const manager = objectManagers[layerId]
    if (manager?.objects?.getLength && manager.objects.getLength() > 0) {
      manager.setFilter(obj => filterFeature(obj))
    }
  }
}
function addLayerWithFilter(layerId) {
  if (objectManagers[layerId]) {
    objectManagers[layerId].setFilter(obj => filterFeature(obj))
    mapInstance.geoObjects.add(objectManagers[layerId])
  }
}
function removeLayer(layerId) {
  if (objectManagers[layerId]) {
    mapInstance.geoObjects.remove(objectManagers[layerId])
  }
}
watch([ageGroups, accessibility], applyFiltersToAllLayers, { deep: true })

function handlePreviewLeave() {
  isPreviewHovered.value = false
  setTimeout(() => { if (!isPreviewHovered.value) hoveredOrg.value = null }, 150)
}
const previewCardStyle = computed(() => ({
  position: 'fixed',
  top: previewCoords.value.y + 10 + 'px',
  left: previewCoords.value.x + 10 + 'px',
  zIndex: 20000,
  minWidth: '280px'
}))
function openPreviewCard(props, coords) {
  hoveredOrg.value = {
    name: props.name,
    address: props.address,
    website: props.website,
    phone: props.phone
  }
  previewCoords.value = coords
}
function handleSelectOrganization(org) {
  let foundFeature = null, foundLayer = null
  for (const layerId in objectManagers) {
    const om = objectManagers[layerId]
    const feats = om.objects.getAll()
    foundFeature = feats.find(f =>
      f.properties.name === org.name && f.properties.address === org.address
    )
    if (foundFeature) { foundLayer = om; break }
  }
  if (foundFeature && foundLayer && mapInstance) {
    const coords = foundFeature.geometry.coordinates
    mapInstance.setCenter(coords, 17, { duration: 400 })
    selectedOrg.value = { ...foundFeature.properties }
  }
}

function offsetDuplicateCoords(features) {
  const coordGroups = new Map();
  const OFFSET = 0.0002; // ~6м

  // Группируем по строковому представлению координат
  features.forEach(feature => {
    const coordStr = JSON.stringify(feature.geometry.coordinates);
    if (!coordGroups.has(coordStr)) {
      coordGroups.set(coordStr, []);
    }
    coordGroups.get(coordStr).push(feature);
  });

  // Для каждой группы одинаковых координат смещаем кроме первой
  for (const group of coordGroups.values()) {
    if (group.length > 1) {
      const [lon, lat] = group[0].geometry.coordinates;
      for (let i = 1; i < group.length; i++) {
        const angle = (i * 30) * Math.PI / 180; // равномерно по кругу
        const dx = Math.cos(angle) * OFFSET;
        const dy = Math.sin(angle) * OFFSET;
        group[i].geometry.coordinates = [
          lon + dx,
          lat + dy
        ];
      }
    }
  }
  return features;
}


function initMap() {
  window.ymaps.ready(async () => {
    await nextTick()
    if (!mapRef.value) { console.error('mapRef ещё не готов!'); return }
    mapInstance = new window.ymaps.Map(mapRef.value, {
      center: [54.7, 56.0],
      zoom: 7,
      controls: ['zoomControl']
    })
    allOrganizations.value = []
    for (const layerId in layerFiles) {
      objectManagers[layerId] = new window.ymaps.ObjectManager({ clusterize: true })
      fetch(layerFiles[layerId])
        .then(r => r.json())
        .then(data => {
          // Перед добавлением смещаем дубликаты:
    if (data && data.features) {
      data.features = offsetDuplicateCoords(data.features);
      console.log('После смещения', data.features.map(f => f.geometry.coordinates));

    }
          objectManagers[layerId].add(data)
          objectManagers[layerId].objects.options.set('preset', layerPresets[layerId])
          objectManagers[layerId].objects.options.set('hasBalloon', false)
          objectManagers[layerId].objects.options.set('openBalloonOnClick', false)
          objectManagers[layerId].objects.options.set('hasHint', false)
          objectManagers[layerId].objects.events.add('mouseenter', (e) => {
            const objectId = e.get('objectId')
            const geoObject = objectManagers[layerId].objects.getById(objectId)
            const props = geoObject.properties
            const coords = geoObject.geometry.coordinates
            const pixel = mapInstance.options.get('projection').toGlobalPixels(coords, mapInstance.getZoom())
            const mapPx = mapInstance.converter.globalToPage(pixel)
            openPreviewCard(props, { x: mapPx[0], y: mapPx[1] })
          })
          objectManagers[layerId].objects.events.add('mouseleave', () => {
            setTimeout(() => { if (!isPreviewHovered.value) hoveredOrg.value = null }, 150)
          })
          objectManagers[layerId].objects.events.add('click', (e) => {
            const objectId = e.get('objectId')
            const props = objectManagers[layerId].objects.getById(objectId).properties
            selectedOrg.value = { ...props }
          })
          if (data && data.features) {
            allOrganizations.value.push(
              ...data.features.map(f => ({
                ...f.properties,
                coords: f.geometry.coordinates,
                layer: layerId
              }))
            )
          }
          if (visibleLayers[layerId]) addLayerWithFilter(layerId)
          applyFiltersToAllLayers()
        })
    }
    watch(visibleLayers, (newValues) => {
      for (const id in newValues) {
        removeLayer(id)
        if (newValues[id]) addLayerWithFilter(id)
      }
    }, { deep: true })
  })
}
onMounted(() => {
  const script = document.createElement('script')
  script.src = 'https://api-maps.yandex.ru/2.1/?apikey=9dda63a0-a400-4fa1-bed5-024c6ad2056d&lang=ru_RU'
  script.onload = initMap
  document.head.appendChild(script)
})
</script>

<style scoped>
.panel-toggle-btn {
  position: absolute;
  top: 22px;
  left: 12px;
  background: #fff;
  border-radius: 9px;
  border: 1px solid #ddd;
  width: 36px; height: 36px;
  z-index: 2001;
  box-shadow: 0 2px 12px #0001;
  display: flex;
  align-items: center; justify-content: center;
  cursor: pointer;
  transition: background 0.15s;
}
.panel-toggle-btn:hover { background: #f3f6ff; }

.LeftPanel {
  background: #fff;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  width: 280px;
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1000;
  font-family: 'Segoe UI', sans-serif;
}

/* Заголовок и сброс */
.LeftPanel h3 {
  font-size: 16px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.LeftPanel .reset-button {
  font-size: 13px;
  color: #888;
  cursor: pointer;
}
.LeftPanel .reset-button:hover {
  text-decoration: underline;
}

/* Чекбоксы и группы */
.LeftPanel label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 4px 0;
}

/* Кнопка Применить */
.apply-button {
  background-color: #04b;
  color: white;
  padding: 8px 16px;
  border: none;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
}
.apply-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Сайдбар */
.sidebar-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.15);
  width: 350px;
  max-height: 90vh;
  overflow-y: auto;
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1500;
}

/* Всплывающая карточка при наведении */
.preview-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  padding: 12px;
  font-size: 13px;
  pointer-events: auto;
}
</style>
