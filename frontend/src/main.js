import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

import { createRouter, createWebHistory } from 'vue-router'
import Home from './components/Home.vue'
import DestinationCategory from './components/DestinationCategory.vue'
import PreferenceInput from './components/PreferenceInput.vue'
import AuthPage from './components/AuthPage.vue'
import Test from './components/test.vue'

const routes = [
  { path: '/auth', component: AuthPage },
  { path: '/', component: Home },
  { path: '/destination', component: DestinationCategory },
  { path: '/preference', component: PreferenceInput },
  { path: '/recommend', component: () => import('./components/RecommendResult.vue') }, // 추후 구현
  { path: '/bookmarks', component: () => import('./components/BookmarkList.vue') }, // 북마크 페이지
  { path: '/community', component: () => import('./components/Community.vue') }, // 커뮤니티 페이지
  { path: '/management', component: () => import('./components/Management.vue') }, // 관리자 페이지
  { path: '/present', component: () => import('./components/PresentFestivals.vue') }, // 현재 진행중인 서울 행사
  { path: '/test', component: Test }, // 위치 정보 테스트 페이지
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
