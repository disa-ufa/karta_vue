<template>
  <div>
    <LeftPanel
      :visibleLayers="visibleLayers"
      :ageGroups="ageGroups"
      :accessibility="accessibility"
      :allAgeGroups="allAgeGroups"
      :allAccessibility="allAccessibility"
      @update:ageGroups="val => {
        console.log('[YandexMap] parent set ageGroups:', val)
        ageGroups.splice(0, ageGroups.length, ...val)
      }"
      @update:accessibility="val => {
        console.log('[YandexMap] parent set accessibility:', val)
        accessibility.splice(0, accessibility.length, ...val)
      }"
    />
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

const allAgeGroups = ['0-18', '18+', 'СВО']
const allAccessibility = ['Да', 'Нет']

const ageGroups = reactive([...allAgeGroups])
const accessibility = reactive([])

const visibleLayers = reactive({
  layer1: true,
  layer2: true,
  layer3: true
})

const layerFiles = {
  layer1: '/objects.json',
  layer2: '/objects2.json',
  layer3: '/objects3.json'
}

const layerPresets = {
  layer1: 'islands#redIcon',
  layer2: 'islands#blueIcon',
  layer3: 'islands#greenIcon'
}

const mapRef = ref(null)
const objectManagers = {}
let mapInstance = null

const selectedOrg = ref(null)
const hoveredOrg = ref(null)
const previewCoords = ref({ x: 0, y: 0 })
const isPreviewHovered = ref(false)

function filterFeature(obj) {
  const accVal = (obj.properties.accessibility || '').toLowerCase().trim()
  const ageVal = (obj.properties.age_group || '').toLowerCase().trim()

  let ageOk = true, accOk = true

  const accFilter = Array.isArray(accessibility) ? [...accessibility] : []
  const ageFilter = Array.isArray(ageGroups) ? [...ageGroups] : []

  if (ageFilter.length > 0) {
    ageOk = ageFilter.some(group => ageVal.includes(group.toLowerCase().trim()))
  }

  if (accFilter.length > 0) {
    accOk = accFilter.some(val => accVal === val.toLowerCase().trim())
  }

  console.log(`[YandexMap] → ${obj.properties.name} | ageOk=${ageOk}, accOk=${accOk}`)
  console.log(`[YandexMap]    compare: accVal='${accVal}' vs`, accFilter)

  return ageOk && accOk
}

function applyFiltersToAllLayers() {
  console.log('[YandexMap] ✅ applyFiltersToAllLayers() triggered')
  for (const layerId in objectManagers) {
    const manager = objectManagers[layerId]
    if (manager?.objects?.getLength && manager.objects.getLength() > 0) {
      manager.setFilter(obj => filterFeature(obj))
      console.log(`[YandexMap] [${layerId}] setFilter applied`)
    } else {
      console.log(`[YandexMap] [${layerId}] ObjectManager пуст или не готов`)
    }
  }
}

function addLayerWithFilter(layerId) {
  if (objectManagers[layerId]) {
    objectManagers[layerId].setFilter(obj => filterFeature(obj))
    mapInstance.geoObjects.add(objectManagers[layerId])
    console.log(`[YandexMap] addLayerWithFilter: ${layerId} (setFilter + add)`)
  }
}

function removeLayer(layerId) {
  if (objectManagers[layerId]) {
    mapInstance.geoObjects.remove(objectManagers[layerId])
    console.log(`[YandexMap] removeLayer: ${layerId}`)
  }
}

watch([ageGroups, accessibility], () => {
  console.log('[YandexMap] 🔁 watch triggered: filters updated')
  applyFiltersToAllLayers()
}, { deep: true })

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

function initMap() {
  window.ymaps.ready(async () => {
    await nextTick()
    if (!mapRef.value) {
      console.error('mapRef ещё не готов!')
      return
    }

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
            setTimeout(() => {
              if (!isPreviewHovered.value) hoveredOrg.value = null
            }, 150)
          })

          objectManagers[layerId].objects.events.add('click', (e) => {
            const objectId = e.get('objectId')
            const props = objectManagers[layerId].objects.getById(objectId).properties
            selectedOrg.value = { ...props }
          })

          if (visibleLayers[layerId]) {
            addLayerWithFilter(layerId)
          }

          applyFiltersToAllLayers()
        })
    }

    watch(visibleLayers, (newValues) => {
      for (const id in newValues) {
        removeLayer(id)
        if (newValues[id]) {
          addLayerWithFilter(id)
        }
      }
    }, { deep: true })
  })
}

onMounted(() => {
  const script = document.createElement('script')
  script.src = 'https://api-maps.yandex.ru/2.1/?apikey=9dda63a0-a400-4fa1-bed5-024c6ad2056d&lang=ru_RU'
  script.onload = initMap
  document.head.appendChild(script)

  setTimeout(() => {
    console.log('[YandexMap] refs on mount:', {
      ageGroups: [...ageGroups],
      accessibility: [...accessibility]
    })
  }, 2000)
})
</script>
