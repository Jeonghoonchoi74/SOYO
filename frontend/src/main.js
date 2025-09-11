import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

import { createRouter, createWebHistory } from 'vue-router'
import Home from './components/Home.vue'
import Main from './components/Main.vue'
import DestinationCategory from './components/DestinationCategory.vue'
import PreferenceInput from './components/PreferenceInput.vue'
import AuthPage from './components/AuthPage.vue'
import Test from './components/test.vue'
import SearchChooser from './components/SearchChooser.vue'
import GuidedSearch from './components/GuidedSearch.vue'
import Mypage from './components/Mypage.vue'

const routes = [
  { path: '/auth', component: AuthPage },
  { path: '/', component: Home },
  { path: '/main', component: Main },
  { path: '/destination', redirect: '/search' }, // Redirect to the new chooser page
  { path: '/search', component: SearchChooser }, // New search chooser page
  { path: '/preference', component: PreferenceInput }, // Existing free search
  { path: '/search/guided', component: GuidedSearch }, // New guided search
  { path: '/mypage', component: Mypage }, // 마이페이지
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
