import { createRouter, createWebHistory } from 'vue-router'
import YandexMap from '../components/YandexMap.vue'
import Profile from '../components/Profile.vue'

const routes = [
  { path: '/', component: YandexMap },
  { path: '/profile', component: Profile }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
