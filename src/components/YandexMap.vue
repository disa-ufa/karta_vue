<template>
  <div>
    <!-- Левая панель -->
    <LeftPanel :visibleLayers="visibleLayers" />

    <!-- Карта -->
    <div id="map" ref="mapRef" style="width: 100vw; height: 100vh; position: relative;"></div>

    <!-- Sidebar справа -->
    <transition name="sidebar">
      <SidebarCard v-if="selectedOrg" :org="selectedOrg" @close="selectedOrg = null" />
    </transition>

    <!-- Preview-карточка при наведении -->
    <div
      v-if="hoveredOrg"
      :style="previewCardStyle"
      class="preview-card"
      @mouseenter="isPreviewHovered = true"
      @mouseleave="handlePreviewLeave"
    >
      <div>
        <b>{{ hoveredOrg.name }}</b>
      </div>
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
import { ref, reactive, onMounted, watch, computed } from 'vue'
import LeftPanel from './LeftPanel.vue'
import SidebarCard from './SidebarCard.vue'

// === Цвета меток для каждого слоя ===
const layerPresets = {
  layer1: 'islands#redIcon',    // например, красный
  layer2: 'islands#blueIcon',   // синий
  layer3: 'islands#greenIcon'   // зелёный
}

const mapRef = ref(null)
const selectedOrg = ref(null)
const hoveredOrg = ref(null)
const previewCoords = ref({ x: 0, y: 0 })
const isPreviewHovered = ref(false)

const visibleLayers = reactive({
  layer1: true,
  layer2: true,
  layer3: true
})

const objectManagers = {}
const layerFiles = {
  layer1: '/objects.json',
  layer2: '/objects2.json',
  layer3: '/objects3.json'
}

let mapInstance = null

onMounted(() => {
  const script = document.createElement('script')
  script.src = 'https://api-maps.yandex.ru/2.1/?apikey=ВАШ_API_КЛЮЧ&lang=ru_RU'
  script.onload = initMap
  document.head.appendChild(script)
})

function handlePreviewLeave() {
  isPreviewHovered.value = false
  setTimeout(() => {
    if (!isPreviewHovered.value) hoveredOrg.value = null
  }, 150)
}

const previewCardStyle = computed(() => ({
  position: 'fixed',
  top: previewCoords.value.y + 10 + 'px',
  left: previewCoords.value.x + 10 + 'px',
  zIndex: 20000,
  minWidth: '280px',
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

function closePreviewCard() {
  hoveredOrg.value = null
}

function initMap() {
  window.ymaps.ready(() => {
    mapInstance = new window.ymaps.Map(mapRef.value, {
      center: [54.7, 56.0],
      zoom: 9
    })

    for (const layerId in layerFiles) {
      objectManagers[layerId] = new window.ymaps.ObjectManager({ clusterize: true })

      fetch(layerFiles[layerId])
        .then(r => r.json())
        .then(data => {
          objectManagers[layerId].add(data)

          // === ВАЖНО: назначаем цвет меток для этого слоя! ===
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

          objectManagers[layerId].objects.events.add('mouseleave', (e) => {
            setTimeout(() => {
              if (!isPreviewHovered.value) hoveredOrg.value = null
            }, 150)
          })

          objectManagers[layerId].objects.events.add('click', (e) => {
            const objectId = e.get('objectId')
            const props = objectManagers[layerId].objects.getById(objectId).properties
            selectedOrg.value = {
              name: props.name,
              subtitle: props.subtitle || "",
              address: props.address,
              website: props.website,
              phone: props.phone,
              description: props.description,
              rating: props.rating,
              ratingCount: props.ratingCount,
              status: props.status,
              image: props.image,
              rehab_form: props.rehab_form,
              age_group: props.age_group,
              accessibility: props.accessibility,
              profile: props.profile,
              services: props.services,
              specialists: props.specialists
            }
          })

          if (visibleLayers[layerId]) {
            mapInstance.geoObjects.add(objectManagers[layerId])
          }
        })
    }

    watch(visibleLayers, (newValues) => {
      for (const id in newValues) {
        if (newValues[id]) {
          mapInstance.geoObjects.add(objectManagers[id])
        } else {
          mapInstance.geoObjects.remove(objectManagers[id])
        }
      }
    }, { deep: true })
  })
}
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
.preview-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
  padding: 15px 20px 15px 20px;
  font-size: 16px;
  font-family: sans-serif;
  border: 1px solid #eee;
  min-width: 280px;
}
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
.sidebar-subtitle {
  font-size: 1em;
  color: #888;
  margin-bottom: 9px;
}
.sidebar-rating {
  margin-bottom: 9px;
  font-size: 1.1em;
  color: #222;
}
.sidebar-star {
  color: #ff9900;
  margin-right: 2px;
  font-size: 1.15em;
}
.sidebar-rating-value {
  font-weight: bold;
  margin-right: 4px;
}
.sidebar-rating-count {
  color: #888;
}
.sidebar-status {
  font-size: 1.05em;
  color: #1aaf5d;
  margin-bottom: 9px;
}
.sidebar-status.closed {
  color: #e64827;
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
