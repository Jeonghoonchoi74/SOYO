<template>
  <div class="recommend-page">
    <div class="recommend-content">
      <div class="recommend-header">
        <h2 class="title">{{ $t('recommend_title') }}</h2>
        <p class="region-info">{{ $t(getDisplayName(region)) }} 지역 {{ $t(getCategoryLabel(category)) }} 추천</p>
      </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('recommend_loading') }}</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="places.length === 0" class="no-data">
      <p>{{ $t('recommend_no_data') }}</p>
    </div>
    
    <div v-else class="places-grid">
      <div 
        v-for="(place, idx) in places" 
        :key="place.contentid || idx" 
        class="place-card"
        @click="openModal(place)"
      >
        <div class="card-actions">
          <button class="action-btn" @click.stop="toggleBookmark(idx)">
            <span :class="{ active: place.bookmarked }">❤️</span>
          </button>
        </div>
        
        <div class="place-image">
          <img 
            v-if="place.firstimage" 
            :src="place.firstimage" 
            :alt="place.title"
            @error="handleImageError"
          />
          <div v-else class="no-image">
            <span>{{ $t('recommend_no_image') }}</span>
          </div>
        </div>
        
        <div class="place-content">
          <h3 class="place-title">{{ place.displayTitle || place.title }}</h3>
          
          <div class="place-info">
            <div class="info-item">
              <span class="label">{{ $t('recommend_address') }}</span>
              <span class="value">{{ place.displayAddress || place.addr1 }}</span>
            </div>
            
            <div v-if="category === 'events' && place.eventstartdate && place.eventenddate" class="info-item">
              <span class="label">{{ $t('recommend_period') }}</span>
              <span class="value">
                {{ formatDate(place.eventstartdate) }} ~ {{ formatDate(place.eventenddate) }}
              </span>
            </div>
            
            <div v-if="place.tel" class="info-item">
              <span class="label">{{ $t('recommend_contact') }}</span>
              <span class="value">{{ formatTelForCard(place.tel) }}</span>
            </div>
            
            <!-- foods 카테고리 추가 정보 -->
            <div v-if="category === 'foods' && place.firstmenu" class="info-item">
              <span class="label">{{ $t('recommend_representative_menu') }}</span>
              <span class="value">{{ place.firstmenu }}</span>
            </div>
            
                    <!-- tourist attraction 카테고리 추가 정보 -->
        <div v-if="category === 'tourist attraction' && place.infocenter" class="info-item">
              <span class="label">{{ $t('recommend_inquiry') }}</span>
              <span class="value">{{ place.infocenter }}</span>
            </div>
          </div>
          
          <div v-if="category === 'events'" class="place-status">
            <span :class="getStatusClass(place)" class="status-badge">
              {{ getStatusText(place) }}
            </span>
          </div>
          
          <!-- 키워드 섹션 -->
          <div v-if="place.keywords && place.keywords.length > 0" class="place-keywords">
            <div class="keywords-container">
              <span 
                v-for="(keyword, keywordIdx) in place.keywords.slice(0, 3)" 
                :key="keywordIdx" 
                class="keyword-tag"
              >
                #{{ keyword }}
              </span>
              <span v-if="place.keywords.length > 3" class="more-keywords">
                +{{ place.keywords.length - 3 }}
              </span>
            </div>
          </div>
          
          <!-- DB 참조 정보 섹션 -->
          <div v-if="place.dbReference" class="db-reference">
            <div class="db-reference-container">
              <span class="db-label">📊 DB:</span>
              <span class="db-path">{{ place.dbReference }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="summary">
      <p>{{ $t('recommend_summary').replace('{count}', places.length) }}</p>
    </div>
    
    
    <button class="bookmark-list-btn" @click="goBookmark">{{ $t('recommend_bookmark_btn') }}</button>
    
    <!-- Floating 버튼 -->
    <button class="floating-back-btn" @click="goHome">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
      </svg>
      {{ $t('recommend_back_main') }}
    </button>
    
    <!-- 상세 모달 -->
    <div v-if="selectedPlace" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ selectedPlace.displayTitle || selectedPlace.title }}</h2>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="modal-image">
            <img 
              v-if="selectedPlace.firstimage" 
              :src="selectedPlace.firstimage" 
              :alt="selectedPlace.title"
            />
            <div v-else class="no-image">
              <span>{{ $t('recommend_no_image') }}</span>
            </div>
          </div>
          
          <div class="modal-info">
            <div class="info-section">
              <h3>{{ $t('recommend_detail_info') }}</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">{{ $t('recommend_address') }}</span>
                  <span class="value">{{ selectedPlace.displayAddress || selectedPlace.addr1 }}</span>
                </div>
                <div v-if="selectedPlace.addr2" class="info-item">
                  <span class="label">{{ $t('recommend_detail_address') }}</span>
                  <span class="value">{{ selectedPlace.addr2 }}</span>
                </div>

                <div v-if="category === 'events' && selectedPlace.eventstartdate && selectedPlace.eventenddate" class="info-item">
                  <span class="label">{{ $t('recommend_period') }}</span>
                  <span class="value">
                    {{ formatDate(selectedPlace.eventstartdate) }} ~ {{ formatDate(selectedPlace.eventenddate) }}
                  </span>
                </div>
                <div v-if="selectedPlace.tel" class="info-item">
                  <span class="label">{{ $t('recommend_contact') }}</span>
                  <span class="value" v-html="formatTelForDetail(selectedPlace.tel)"></span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.usetimefestival" class="info-item">
                  <span class="label">{{ $t('recommend_usage_time') }}</span>
                  <span class="value" v-html="formatPlaytime(selectedPlace.detail_intro2.usetimefestival)"></span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.playtime" class="info-item">
                  <span class="label">{{ $t('recommend_performance_time') }}</span>
                  <span class="value" v-html="formatPlaytime(selectedPlace.detail_intro2.playtime)"></span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.spendtimefestival" class="info-item">
                  <span class="label">{{ $t('recommend_duration') }}</span>
                  <span class="value">{{ selectedPlace.detail_intro2.spendtimefestival }}</span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.agelimit" class="info-item">
                  <span class="label">{{ $t('recommend_age_limit') }}</span>
                  <span class="value" v-html="formatPlaytime(selectedPlace.detail_intro2.agelimit)"></span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.bookingplace" class="info-item">
                  <span class="label">{{ $t('recommend_booking_place') }}</span>
                  <span class="value">{{ selectedPlace.detail_intro2.bookingplace }}</span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.discountinfofestival" class="info-item">
                  <span class="label">{{ $t('recommend_discount_info') }}</span>
                  <span class="value">{{ selectedPlace.detail_intro2.discountinfofestival }}</span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.festivalgrade" class="info-item">
                  <span class="label">{{ $t('recommend_event_grade') }}</span>
                  <span class="value">{{ selectedPlace.detail_intro2.festivalgrade }}</span>
                </div>
                
                <!-- foods 카테고리 추가 정보 -->
                <div v-if="category === 'foods' && selectedPlace.firstmenu" class="info-item">
                  <span class="label">{{ $t('recommend_representative_menu') }}</span>
                  <span class="value">{{ selectedPlace.firstmenu }}</span>
                </div>
                
                <div v-if="category === 'foods' && selectedPlace.treatmenu" class="info-item">
                  <span class="label">{{ $t('recommend_menu') }}</span>
                  <span class="value">{{ selectedPlace.treatmenu }}</span>
                </div>
                
                <div v-if="category === 'foods' && selectedPlace.opentimefood" class="info-item">
                  <span class="label">{{ $t('recommend_opening_hours') }}</span>
                  <span class="value">{{ selectedPlace.opentimefood }}</span>
                </div>
                
                <div v-if="category === 'foods' && selectedPlace.restdatefood" class="info-item">
                  <span class="label">{{ $t('recommend_rest_day') }}</span>
                  <span class="value">{{ selectedPlace.restdatefood }}</span>
                </div>
                
                <!-- tourist attraction 카테고리 추가 정보 -->
                <div v-if="category === 'tourist attraction' && selectedPlace.infocenter" class="info-item">
                  <span class="label">{{ $t('recommend_inquiry') }}</span>
                  <span class="value">{{ selectedPlace.infocenter }}</span>
                </div>
                
                <div v-if="category === 'tourist attraction' && selectedPlace.usetime" class="info-item">
                  <span class="label">{{ $t('recommend_usage_time') }}</span>
                  <span class="value">{{ selectedPlace.usetime }}</span>
                </div>
                
                <div v-if="category === 'tourist attraction' && selectedPlace.restdate" class="info-item">
                  <span class="label">{{ $t('recommend_rest_day') }}</span>
                  <span class="value">{{ selectedPlace.restdate }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">{{ $t('recommend_status') }}</span>
                  <span class="value">
                    <span :class="getStatusClass(selectedPlace)" class="status-badge">
                      {{ getStatusText(selectedPlace) }}
                    </span>
                  </span>
                </div>
              </div>
            </div>
            
            <!-- overview(개요) 섹션: 제목 없이 overview만 -->
            <div v-if="selectedPlace.displaySummary || selectedPlace.overview" class="info-section">
              <p v-html="selectedPlace.displaySummary || selectedPlace.overview" style="margin-top: 12px; color: #222; font-size: 1.13rem; line-height: 1.7; text-align: left;"></p>
            </div>
            
            <!-- 지도 섹션 -->
            <div v-if="selectedPlace.addr1" class="info-section">
              <h3>{{ $t('recommend_location') }}</h3>
              <GoogleMap 
                :address="selectedPlace.addr1" 
                :title="selectedPlace.title"
                :zoom="16"
              />
            </div>
            
            <!-- 상세정보 섹션 -->
            <div v-if="selectedPlace.detail_intro2?.eventintro || selectedPlace.detail_intro2?.eventtext" class="info-section">
              <h3>{{ $t('recommend_detail_info') }}</h3>
              <div class="detail-content">
                <div v-if="selectedPlace.detail_intro2.eventintro" class="detail-item">
                  <h4>행사 소개</h4>
                  <p>{{ selectedPlace.detail_intro2.eventintro }}</p>
                </div>
                
                <div v-if="selectedPlace.detail_intro2.eventtext" class="detail-item">
                  <h4>행사 내용</h4>
                  <p>{{ selectedPlace.detail_intro2.eventtext }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
      <div v-if="showModal" class="custom-modal">{{ modalMessage }}</div>
    </div>
  </div>
</template>

<script>
import { i18nState, $t } from '../i18n';
import { getAuth } from 'firebase/auth';
import { collection, getDocs, query, where } from 'firebase/firestore';
import { db } from '../firebase.js';
import { getDisplayName } from '../utils/regionMapping';
import GoogleMap from './GoogleMap.vue';

export default {
  name: 'RecommendResult',
  components: {
    GoogleMap
  },
  data() {
    return {
      region: '서울', // 기본값, 쿼리 파라미터에서 업데이트됨
      category: 'events', // 기본값, 쿼리 파라미터에서 업데이트됨
      places: [],
      loading: true,
      error: null,
      selectedPlace: null,
      showModal: false,
      modalMessage: '',
      bookmarkDisabled: [],
    };
  },
  computed: {
    // $t는 methods에서만 정의
  },
      async mounted() {
        // 쿼리 파라미터에서 지역 정보 가져오기
        const regionFromQuery = this.$route.query.region;
        const categoryFromQuery = this.$route.query.category;
        const searchQueryFromQuery = this.$route.query.searchQuery;
        
        if (regionFromQuery) {
          this.region = regionFromQuery;
        }
        if (categoryFromQuery) {
          this.category = categoryFromQuery;
        }
        
        // localStorage에서 검색 결과 확인
        const tempSearchResults = localStorage.getItem('tempSearchResults');
        let searchResultsFromStorage = null;
        
        if (tempSearchResults) {
          try {
            searchResultsFromStorage = JSON.parse(tempSearchResults);
            // 사용 후 삭제
            localStorage.removeItem('tempSearchResults');
          } catch (error) {
            console.error('검색 결과 파싱 오류:', error);
          }
        }
        
        if (searchResultsFromStorage && Array.isArray(searchResultsFromStorage)) {
          // localStorage에서 전달된 검색 결과가 있으면 처리
          await this.processSearchResults(searchResultsFromStorage);
        } else if (searchQueryFromQuery && searchQueryFromQuery.trim()) {
          // 검색 쿼리가 있으면 추천 API 사용
          await this.searchWithRecommendAPI(searchQueryFromQuery);
        } else {
          // 기존 방식으로 데이터 가져오기
          await this.fetchRecommendPlaces();
        }
        
        await this.loadUserBookmarks();
      },
      
      beforeUnmount() {
        // 컴포넌트 언마운트 시 정리 작업
      },
  methods: {
    $t,
    // 지역명 표시 함수
    getDisplayName(dbRegionName) {
      return getDisplayName(dbRegionName);
    },
    
    // 카테고리 라벨 표시 함수
    getCategoryLabel(category) {
      switch (category) {
        case 'events':
          return this.$t('category_events');
        case 'foods':
          return this.$t('category_foods');
        case 'tourist attraction':
          return this.$t('category_tourist_attraction');
        default:
          return category;
      }
    },

    // 현재 날짜를 YYYYMMDD 형식으로 변환
    getCurrentDate() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      return `${year}${month}${day}`;
    },

    // 날짜 형식 변환 (YYYYMMDD -> YYYY-MM-DD)
    formatDate(dateString) {
      if (!dateString || dateString.length !== 8) return this.$t('recommend_date_info_missing');
      return `${dateString.substring(0, 4)}-${dateString.substring(4, 6)}-${dateString.substring(6, 8)}`;
    },

    // 연락처 포맷팅 (카드용 - 첫 번째 <br> 이전까지만)
    formatTelForCard(telString) {
      if (!telString) return '';
      const brIndex = telString.indexOf('<br>');
      if (brIndex !== -1) {
        return telString.substring(0, brIndex);
      }
      return telString;
    },

    // 연락처 포맷팅 (상세용 - <br> 태그를 실제 줄바꿈으로 변환)
    formatTelForDetail(telString) {
      if (!telString) return '';
      return telString.replace(/<br>/gi, '<br>');
    },

    // 공연 시간 포맷팅 (<br> 태그를 실제 줄바꿈으로 변환)
    formatPlaytime(playtimeString) {
      if (!playtimeString) return '';
      return playtimeString.replace(/<br>/gi, '<br>');
    },

    // 이미지 로드 에러 처리
    handleImageError(event) {
      event.target.style.display = 'none';
      event.target.nextElementSibling.style.display = 'flex';
    },

    // 카테고리별 필터링 로직
    isInTargetPeriod(place) {
      // events 카테고리인 경우 날짜 필터링 적용
      if (this.category === 'events') {
        const startDate = place.eventstartdate;
        const endDate = place.eventenddate;
        const currentDate = this.getCurrentDate();
        
        // 날짜 정보가 없는 경우는 제외
        if (!startDate || !endDate) {
          console.log(`날짜 정보 없음 제외: ${place.title || place.displayTitle}`);
          return false;
        }
        
        // 종료일이 현재 날짜보다 이전인 경우 제외 (이미 끝난 행사)
        if (endDate < currentDate) {
          console.log(`종료된 행사 제외: ${place.title || place.displayTitle} (종료일: ${endDate})`);
          return false;
        }
        
        // 시작일이 너무 먼 미래인 경우 제외 (2025년 이후)
        const maxStartDate = '20251231';
        if (startDate > maxStartDate) {
          console.log(`너무 먼 미래 행사 제외: ${place.title || place.displayTitle} (시작일: ${startDate})`);
          return false;
        }
        
        return true;
      }
      
      // foods, tourist attraction 카테고리는 모든 데이터 표시
      return true;
    },

    // 행사 상태 텍스트 반환
    getStatusText(place) {
      // events 카테고리인 경우 날짜 기반 상태 표시
      if (this.category === 'events') {
        const currentDate = this.getCurrentDate();
        const startDate = place.eventstartdate;
        const endDate = place.eventenddate;
        
        if (!startDate || !endDate) return this.$t('recommend_status_unknown');
        
        if (currentDate < startDate) {
          return this.$t('recommend_status_upcoming');
        } else if (currentDate >= startDate && currentDate <= endDate) {
          return this.$t('recommend_status_ongoing');
        } else {
          return this.$t('recommend_status_ended');
        }
      }
      
      // foods, tourist attraction 카테고리는 상시 운영 표시
      return this.$t('recommend_status_always_open');
    },

    // 행사 상태에 따른 CSS 클래스 반환
    getStatusClass(place) {
      // events 카테고리인 경우 날짜 기반 상태 표시
      if (this.category === 'events') {
        const currentDate = this.getCurrentDate();
        const startDate = place.eventstartdate;
        const endDate = place.eventenddate;
        
        if (!startDate || !endDate) return 'unknown';
        
        if (currentDate < startDate) {
          return 'upcoming';
        } else if (currentDate >= startDate && currentDate <= endDate) {
          return 'ongoing';
        } else {
          return 'ended';
        }
      }
      
      // foods, tourist attraction 카테고리는 상시 운영 표시
      return 'always-open';
    },

    // 사용자 언어 감지 함수
    async getUserLanguage() {
      try {
        const auth = getAuth();
        const user = auth.currentUser;
        if (!user) return 'ko';
        
        // Firestore에서 사용자 언어 설정 조회
        const { getFirestore, doc, getDoc } = await import('firebase/firestore');
        const db = getFirestore();
        const userDoc = await getDoc(doc(db, 'users', user.uid));
        
        if (userDoc.exists()) {
          const userData = userDoc.data();
          const userLanguage = userData.lang;
          console.log('사용자 언어 설정:', userLanguage);
          return userLanguage || 'ko';
        } else {
          console.log('Firestore에 사용자 데이터가 없음');
          return 'ko';
        }
      } catch (error) {
        console.error('사용자 언어 감지 오류:', error);
        return 'ko';
      }
    },

    // 번역 API 호출 함수
    async translateText(text, targetLang = 'ko') {
      try {
        const response = await fetch('http://localhost:5001/translate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: text,
            target_language: targetLang
          }),
        });

        if (response.ok) {
          const result = await response.json();
          return result.translated_text;
        } else {
          console.error('번역 API 오류:', response.status);
          return text; // 번역 실패시 원본 반환
        }
      } catch (error) {
        console.error('번역 중 오류:', error);
        return text; // 오류시 원본 반환
      }
    },

    // 추천 API를 통한 검색
    async searchWithRecommendAPI(searchQuery) {
      try {
        this.loading = true;
        this.error = null;
        
        // 사용자 로그인 상태 확인
        const auth = getAuth();
        const user = auth.currentUser;
        
        if (!user) {
          this.error = this.$t('recommend_login_required');
          this.loading = false;
          return;
        }
        
        // 사용자 언어 확인 및 번역
        const userLanguage = await this.getUserLanguage();
        let finalQuery = searchQuery;
        
        if (userLanguage !== 'ko') {
          console.log('사용자 언어가 한국어가 아니므로 번역을 진행합니다.');
          finalQuery = await this.translateText(searchQuery, 'ko');
          console.log(`번역 결과: ${searchQuery} → ${finalQuery}`);
        }
        
        console.log('추천 API 검색 시작:', finalQuery);
        
        // 5002번 포트 추천 API 호출
        const response = await fetch('http://localhost:5002/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            uid: user.uid,
            query: finalQuery
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('추천 API 결과:', result);
        
        if (result && Array.isArray(result)) {
          // 사용자 설정 region과 category와 일치하는 결과만 필터링
          const filteredResults = result.filter(item => 
            item.region === this.region && item.category === this.category
          );
          
          console.log(`전체 결과: ${result.length}개, 지역 및 카테고리 필터링 후: ${filteredResults.length}개`);
          
          // Firebase에서 상세 정보 가져오기 (실시간 로딩)
          this.places = []; // 초기화
          this.bookmarkDisabled = []; // 초기화
          console.log(`필터링된 결과 ${filteredResults.length}개 처리 시작`);
          
          // 각 항목을 병렬로 처리하되, 완료되는 대로 즉시 표시
          const processItem = async (item) => {
            console.log(`Firebase 조회 중: ${item.id}, ${item.region}, ${item.category}`);
            const firebaseData = await this.getFirebaseData(
              item.id, 
              item.region, 
              item.category
            );
            if (firebaseData) {
              console.log(`Firebase 데이터 추가: ${item.id}`, firebaseData);
              
              // 날짜 필터링 적용 (events 카테고리인 경우)
              if (this.category === 'events' && !this.isInTargetPeriod(firebaseData)) {
                console.log(`날짜 필터링으로 제외: ${item.id}`);
                return;
              }
              
              // 즉시 추가하여 바로 표시
              this.places.push({
                ...firebaseData,
                bookmarked: false
              });
              this.bookmarkDisabled.push(false);
              
              console.log(`장소 추가됨: ${item.id}, 총 ${this.places.length}개`);
            } else {
              console.log(`Firebase 데이터 없음: ${item.id}`);
            }
          };
          
          // 모든 항목을 병렬로 시작 (완료되는 대로 즉시 표시)
          const promises = filteredResults.map(processItem);
          await Promise.allSettled(promises);
          
          console.log(`최종 상세 장소 ${this.places.length}개`, this.places);
          
        } else {
          console.error('추천 API 응답 형식 오류:', result);
          this.error = '검색 결과를 처리할 수 없습니다.';
        }
        
      } catch (err) {
        console.error('추천 API 검색 오류:', err);
        this.error = '검색 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.';
      } finally {
        this.loading = false;
      }
    },

    // 라우터 state에서 전달된 검색 결과 처리
    async processSearchResults(searchResults) {
      try {
        this.loading = true;
        this.error = null;
        
        console.log('라우터 state에서 전달된 검색 결과 처리:', searchResults);
        
        // 사용자 설정 region과 category와 일치하는 결과만 필터링
        const filteredResults = searchResults.filter(item => 
          item.region === this.region && item.category === this.category
        );
        
        console.log(`전체 결과: ${searchResults.length}개, 지역 및 카테고리 필터링 후: ${filteredResults.length}개`);
        
        // Firebase에서 상세 정보 가져오기 (실시간 로딩)
        this.places = []; // 초기화
        this.bookmarkDisabled = []; // 초기화
        console.log(`필터링된 결과 ${filteredResults.length}개 처리 시작`);
        
        // 각 항목을 병렬로 처리하되, 완료되는 대로 즉시 표시
        const processItem = async (item) => {
          console.log(`Firebase 조회 중: ${item.id}, ${item.region}, ${item.category}`);
          const firebaseData = await this.getFirebaseData(
            item.id, 
            item.region, 
            item.category
          );
          if (firebaseData) {
            console.log(`Firebase 데이터 추가: ${item.id}`, firebaseData);
            
            // 날짜 필터링 적용 (events 카테고리인 경우)
            if (this.category === 'events' && !this.isInTargetPeriod(firebaseData)) {
              console.log(`날짜 필터링으로 제외: ${item.id}`);
              return;
            }
            
            // 즉시 추가하여 바로 표시
            this.places.push({
              ...firebaseData,
              bookmarked: false
            });
            this.bookmarkDisabled.push(false);
            
            console.log(`장소 추가됨: ${item.id}, 총 ${this.places.length}개`);
          } else {
            console.log(`Firebase 데이터 없음: ${item.id}`);
          }
        };
        
        // 모든 항목을 병렬로 시작 (완료되는 대로 즉시 표시)
        const promises = filteredResults.map(processItem);
        await Promise.allSettled(promises);
        
        console.log(`최종 상세 장소 ${this.places.length}개`, this.places);
        
      } catch (err) {
        console.error('검색 결과 처리 오류:', err);
        this.error = '검색 결과를 처리하는 중 오류가 발생했습니다.';
      } finally {
        this.loading = false;
      }
    },

    // Firebase에서 상세 데이터 가져오기 (언어별 라우팅 + 폴백 + 크로스 카테고리 검색)
    async getFirebaseData(contentId, region, category) {
      try {
        // 사용자 언어 확인
        const userLanguage = await this.getUserLanguage();
        const lang = userLanguage || 'ko';
        
        console.log(`Firebase 데이터 조회 - 언어: ${lang}, 지역: ${region}, 카테고리: ${category}, ID: ${contentId}`);
        
        // events 카테고리가 아닌 경우 한국어로 조회
        const searchLang = (category === 'events') ? lang : 'ko';
        
        // 1. 적절한 언어로 먼저 시도
        let docRef = collection(db, 'api_data', searchLang, region, category, 'items');
        let q = query(docRef, where('contentid', '==', contentId));
        let querySnapshot = await getDocs(q);
        
        if (!querySnapshot.empty) {
          const doc = querySnapshot.docs[0];
          const data = doc.data();
          
          console.log(`Firebase 데이터 조회 성공 (${searchLang}) - ID: ${contentId}`, data);
          
          // DB 경로 생성
          const dbPath = `api_data/${searchLang}/${region}/${category}/items/${contentId}`;
          
          // 언어별 필드 매핑 (사용자 언어 기준)
          const mappedData = this.mapLanguageFields(data, lang, dbPath);
          console.log(`매핑된 데이터 - ID: ${contentId}`, mappedData);
          
          return mappedData;
        } else {
          console.log(`Firebase 데이터 없음 (${searchLang}) - ID: ${contentId}, 지역: ${region}, 카테고리: ${category}`);
          
          // 2. 한국어로 폴백 시도 (events 카테고리가 아니거나 사용자 언어가 한국어가 아닌 경우)
          if (searchLang !== 'ko') {
            console.log(`한국어 폴백 시도 - ID: ${contentId}`);
            
            docRef = collection(db, 'api_data', 'ko', region, category, 'items');
            q = query(docRef, where('contentid', '==', contentId));
            querySnapshot = await getDocs(q);
            
            if (!querySnapshot.empty) {
              const doc = querySnapshot.docs[0];
              const data = doc.data();
              
              console.log(`Firebase 데이터 조회 성공 (ko 폴백) - ID: ${contentId}`, data);
              
              // DB 경로 생성
              const dbPath = `api_data/ko/${region}/${category}/items/${contentId}`;
              
              // 한국어 필드 매핑
              const mappedData = this.mapLanguageFields(data, 'ko', dbPath);
              console.log(`매핑된 데이터 (ko 폴백) - ID: ${contentId}`, mappedData);
              
              return mappedData;
            } else {
              console.log(`한국어 폴백도 실패 - ID: ${contentId}`);
            }
          }
          
          // 3. 크로스 카테고리 검색 (다른 카테고리에서 찾기)
          console.log(`크로스 카테고리 검색 시도 - ID: ${contentId}`);
          const allCategories = ['foods', 'events', 'tourist attraction'];
          
          for (const searchCategory of allCategories) {
            if (searchCategory === category) continue; // 이미 시도한 카테고리는 건너뛰기
            
            // events 카테고리가 아닌 경우 한국어로 조회
            const crossSearchLang = (searchCategory === 'events') ? lang : 'ko';
            
            try {
              docRef = collection(db, 'api_data', crossSearchLang, region, searchCategory, 'items');
              q = query(docRef, where('contentid', '==', contentId));
              querySnapshot = await getDocs(q);
              
              if (!querySnapshot.empty) {
                const doc = querySnapshot.docs[0];
                const data = doc.data();
                
                console.log(`Firebase 데이터 조회 성공 (크로스 카테고리: ${searchCategory}, 언어: ${crossSearchLang}) - ID: ${contentId}`, data);
                
                // DB 경로 생성
                const dbPath = `api_data/${crossSearchLang}/${region}/${searchCategory}/items/${contentId}`;
                
                // 언어별 필드 매핑 (사용자 언어 기준)
                const mappedData = this.mapLanguageFields(data, lang, dbPath);
                console.log(`매핑된 데이터 (크로스 카테고리) - ID: ${contentId}`, mappedData);
                
                return mappedData;
              }
            } catch (error) {
              console.log(`크로스 카테고리 검색 오류 (${searchCategory}):`, error);
            }
          }
          
          // 4. 한국어 크로스 카테고리 검색 (사용자 언어가 한국어가 아닌 경우)
          if (lang !== 'ko') {
            console.log(`한국어 크로스 카테고리 검색 시도 - ID: ${contentId}`);
            
            for (const searchCategory of allCategories) {
              if (searchCategory === category) continue;
              
              try {
                docRef = collection(db, 'api_data', 'ko', region, searchCategory, 'items');
                q = query(docRef, where('contentid', '==', contentId));
                querySnapshot = await getDocs(q);
                
                if (!querySnapshot.empty) {
                  const doc = querySnapshot.docs[0];
                  const data = doc.data();
                  
                  console.log(`Firebase 데이터 조회 성공 (한국어 크로스 카테고리: ${searchCategory}) - ID: ${contentId}`, data);
                  
                  // DB 경로 생성
                  const dbPath = `api_data/ko/${region}/${searchCategory}/items/${contentId}`;
                  
                  // 한국어 필드 매핑
                  const mappedData = this.mapLanguageFields(data, 'ko', dbPath);
                  console.log(`매핑된 데이터 (한국어 크로스 카테고리) - ID: ${contentId}`, mappedData);
                  
                  return mappedData;
                }
              } catch (error) {
                console.log(`한국어 크로스 카테고리 검색 오류 (${searchCategory}):`, error);
              }
            }
          }
          
          console.log(`모든 검색 시도 실패 - ID: ${contentId}`);
          
          // 5. 데이터가 없는 경우 기본 정보 반환
          console.log(`기본 정보 생성 - ID: ${contentId}`);
          return {
            contentid: contentId,
            displayTitle: `장소 ${contentId}`,
            displayAddress: `${region} ${category}`,
            displaySummary: '상세 정보를 불러올 수 없습니다.',
            title: `장소 ${contentId}`,
            addr1: `${region} ${category}`,
            overview: '상세 정보를 불러올 수 없습니다.'
          };
        }
        return null;
      } catch (error) {
        console.error('Firebase 데이터 조회 오류:', error);
        return null;
      }
    },

    // 언어별 필드 매핑 함수
    mapLanguageFields(data, lang, dbPath = '') {
      if (lang === 'ko') {
        // 한국어: 기본 필드 사용 (overview 우선, 없으면 빈 문자열)
        return {
          ...data,
          displayTitle: data.title || '',
          displayAddress: data.addr1 || '',
          displaySummary: data.overview || '',
          keywords: data.keywords || [],
          dbReference: dbPath
        };
      } else {
        // 다국어: 번역된 필드 사용 (summary 우선, overview 대체)
        return {
          ...data,
          displayTitle: data.translated_eventtitle || data.title || '',
          displayAddress: data.translated_addr || data.addr1 || '',
          displaySummary: data.summary || data.overview || '',
          keywords: data.keywords || [],
          dbReference: dbPath
        };
      }
    },

    // Firebase에서 서울 행사 데이터 가져오기
    async fetchRecommendPlaces() {
      try {
        this.loading = true;
        this.error = null;
        
        // 사용자 로그인 상태 확인
        const auth = getAuth();
        const user = auth.currentUser;
        
        if (!user) {
          this.error = this.$t('recommend_login_required');
          this.loading = false;
          return;
        }
        
        // 사용자 언어 확인
        const userLanguage = await this.getUserLanguage();
        const lang = userLanguage || 'ko';
        
        // events 카테고리가 아닌 경우 한국어로 조회
        const searchLang = (this.category === 'events') ? lang : 'ko';
        
        console.log(`기존 방식 데이터 조회 - 언어: ${lang}, 조회 언어: ${searchLang}, 지역: ${this.region}, 카테고리: ${this.category}`);
        
        // Firebase에서 해당 지역의 데이터 가져오기 (하나씩 로딩)
        const seoulCollectionRef = collection(db, 'api_data', searchLang, this.region, this.category, 'items');
        const querySnapshot = await getDocs(seoulCollectionRef);
        
        // 초기화
        this.places = [];
        this.bookmarkDisabled = [];
        
        // 모든 문서를 배열로 변환
        const allPlaces = [];
        querySnapshot.forEach((doc) => {
          const data = doc.data();
          // DB 경로 생성
          const dbPath = `api_data/${searchLang}/${this.region}/${this.category}/items/${doc.id}`;
          // 언어별 필드 매핑 적용
          const mappedData = this.mapLanguageFields(data, lang, dbPath);
          allPlaces.push(mappedData);
        });
        
        // 카테고리별 필터링
        const targetPlaces = allPlaces.filter(this.isInTargetPeriod);
        
        // 정렬
        let sortedPlaces;
        if (this.category === 'events') {
          // events 카테고리: 상태별로 정렬 (진행중 → 예정 → 종료)
          sortedPlaces = targetPlaces.sort((a, b) => {
            const statusA = this.getStatusClass(a);
            const statusB = this.getStatusClass(b);
            
            // 상태 우선순위: ongoing(진행중) > upcoming(예정) > ended(종료)
            const statusOrder = { 'ongoing': 0, 'upcoming': 1, 'ended': 2, 'unknown': 3 };
            
            if (statusOrder[statusA] !== statusOrder[statusB]) {
              return statusOrder[statusA] - statusOrder[statusB];
            }
            
            // 같은 상태 내에서는 시작일순으로 정렬
            return (a.eventstartdate || '') - (b.eventstartdate || '');
          });
        } else {
          // foods, tourist attraction 카테고리: 제목순으로 정렬
          sortedPlaces = targetPlaces.sort((a, b) => {
            return (a.title || '').localeCompare(b.title || '', 'ko');
          });
        }
        
        // 하나씩 추가하여 바로 표시 (실시간 로딩)
        const addPlace = async (place) => {
          this.places.push({
            ...place,
            bookmarked: false
          });
          this.bookmarkDisabled.push(false);
          
          console.log(`장소 추가됨: ${place.title || place.displayTitle}, 총 ${this.places.length}개`);
          
          // 부드러운 로딩을 위한 약간의 지연
          await new Promise(resolve => setTimeout(resolve, 150));
        };
        
        // 각 장소를 순차적으로 추가 (하나씩 표시)
        for (const place of sortedPlaces) {
          await addPlace(place);
        }
        
      } catch (err) {
        console.error('추천 장소 데이터 가져오기 오류:', err);
        
        // Firebase 권한 에러인지 확인
        if (err.code === 'permission-denied') {
          this.error = '데이터 접근 권한이 없습니다. 관리자에게 문의해주세요.';
        } else if (err.code === 'not-found') {
          this.error = `${this.$t(this.getDisplayName(this.region))} 지역의 데이터를 찾을 수 없습니다.`;
        } else {
          this.error = '추천 장소 정보를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        }
      } finally {
        this.loading = false;
      }
    },


    async loadUserBookmarks() {
      const auth = getAuth();
      const user = auth.currentUser;
      if (!user) return;
      
      try {
        const res = await fetch('http://localhost:5000/api/get_user_bookmarks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: user.uid })
        });
        const result = await res.json();
        
        if (result.success && result.bookmarks) {
          // 사용자의 북마크 상태를 업데이트
          const bookmarkedPlaces = result.bookmarks.map(bookmark => bookmark.name);
          
          // 각 장소의 북마크 상태를 실제 데이터로 업데이트
          this.places.forEach((place, idx) => {
            const placeTitle = place.displayTitle || place.title;
            this.places[idx].bookmarked = bookmarkedPlaces.includes(placeTitle);
          });
          
        }
      } catch (error) {
        console.error('북마크 로드 오류:', error);
      }
    },

    async toggleBookmark(idx) {
      if (this.bookmarkDisabled[idx]) return;
      this.bookmarkDisabled[idx] = true;
      const wasBookmarked = this.places[idx].bookmarked;
      this.places[idx].bookmarked = !this.places[idx].bookmarked;
      const isNowBookmarked = this.places[idx].bookmarked;
      const result = await this.saveBookmark(idx, isNowBookmarked);
      if (result && result.success) {
        if (isNowBookmarked) {
          this.showModalMessage(this.$t('add_bookmark_alert'));
        } else {
          this.showModalMessage(this.$t('delete_bookmark_alert'));
        }
      } else {
        // 실패 시 롤백
        this.places[idx].bookmarked = wasBookmarked;
        this.showModalMessage(this.$t('recommend_bookmark_error'));
      }
      setTimeout(() => {
        this.bookmarkDisabled[idx] = false;
      }, 2000);
    },

    async saveBookmark(idx, value) {
      const auth = getAuth();
      const user = auth.currentUser;
      if (!user) return { success: false };
      try {
        if (value) {
          const params = {
            uid: user.uid,
            contentId: this.places[idx].contentid, // contentId 사용
            bookmark: value,
            name: this.places[idx].displayTitle || this.places[idx].title,
            desc: this.places[idx].displayAddress || this.places[idx].addr1,
            image: this.places[idx].firstimage,
            region: this.region,
          };
          
          console.log('북마크 저장 파라미터:', params);
          console.log('장소 정보:', this.places[idx]);
          console.log('contentId 타입:', typeof this.places[idx].contentid);
          const res = await fetch('http://localhost:5000/api/save_bookmark', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params),
          });
          const result = await res.json();
          return result;
        } else {
          // 북마크 삭제
          const params = {
            uid: user.uid,
            contentId: this.places[idx].contentid, // contentId 사용
          };
          
          console.log('북마크 삭제 파라미터:', params);
          const res = await fetch('http://localhost:5000/api/delete_user_bookmark', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params),
          });
          const result = await res.json();
          return result;
        }
      } catch (e) {
        console.error('북마크 처리 오류:', e);
        return { success: false, error: e.message };
      }
    },

    showModalMessage(msg) {
      this.modalMessage = msg;
      this.showModal = true;
      setTimeout(() => {
        this.showModal = false;
      }, 1500);
    },

    // 모달 열기
    openModal(place) {
      this.selectedPlace = place;
    },

    // 모달 닫기
    closeModal() {
      this.selectedPlace = null;
    },

    goBookmark() {
      this.$router.push('/bookmarks');
    },

    goHome() {
      this.$router.push('/');
    },
  },
};
</script>

<style scoped>
/* 네이버 지식iN 스타일 - Community.vue 베이스 */
.recommend-page {
  min-height: 100vh;
  background: #F7F8FA;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  padding: 20px;
}

.recommend-content {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
  margin: 0 auto;
}

.recommend-header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #212529;
}

.region-info {
  font-size: 16px;
  color: #6c757d;
  margin-top: 0;
  font-weight: 500;
}

.floating-back-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: #4A69E2;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(74, 105, 226, 0.3);
  transition: all 0.3s ease;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
}

.floating-back-btn:hover {
  background: #3B5BC7;
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(74, 105, 226, 0.4);
}

.floating-back-btn:active {
  transform: translateY(0);
}

.loading {
  text-align: center;
  color: #64748b;
  padding: 60px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  color: #ff6b6b;
  background: white;
  padding: 20px;
  border-radius: 10px;
  margin: 20px;
}

.no-data {
  text-align: center;
  color: #64748b;
  padding: 60px 0;
  font-size: 1.2rem;
}

.places-grid {
  width: 100%;
  max-width: 900px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.place-card {
  background: #f1f5f9;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  cursor: pointer;
  position: relative;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.place-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.card-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
}

.action-btn {
  border: none;
  background: #e2e8f0;
  border-radius: 10px;
  padding: 0.7rem 1.2rem;
  font-size: 1.3rem;
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #cbd5e1;
}

.action-btn .active {
  background: #2563eb;
  color: #fff;
}

.place-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 16px;
  margin-bottom: 1rem;
}

.place-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.place-card:hover .place-image img {
  transform: scale(1.05);
}

.no-image {
  width: 100%;
  height: 100%;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-size: 0.9rem;
}

.place-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.place-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.8rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.place-info {
  margin-bottom: 1rem;
  flex: 1;
}

.info-item {
  display: flex;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #64748b;
  min-width: 60px;
  margin-right: 0.5rem;
}

.value {
  color: #334155;
  flex: 1;
  word-break: break-all;
}

.place-status {
  display: flex;
  justify-content: flex-end;
}

.place-keywords {
  margin-top: 0.8rem;
  padding-top: 0.8rem;
  border-top: 1px solid #e2e8f0;
}

.keywords-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}

.keyword-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
  transition: all 0.2s ease;
}

.keyword-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
}

.more-keywords {
  background: #f1f5f9;
  color: #64748b;
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid #e2e8f0;
}

.db-reference {
  margin-top: 0.6rem;
  padding-top: 0.6rem;
  border-top: 1px solid #e2e8f0;
}

.db-reference-container {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.7rem;
}

.db-label {
  color: #64748b;
  font-weight: 600;
  white-space: nowrap;
}

.db-path {
  color: #475569;
  font-family: 'Courier New', monospace;
  background: #f8fafc;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  font-size: 0.65rem;
  word-break: break-all;
  flex: 1;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.ongoing {
  background: #28a745;
  color: white;
}

.status-badge.upcoming {
  background: #007bff;
  color: white;
}

.status-badge.ended {
  background: #6c757d;
  color: white;
}

.status-badge.unknown {
  background: #ffc107;
  color: #212529;
}

.status-badge.always-open {
  background: #17a2b8;
  color: white;
}

.summary {
  text-align: center;
  color: #64748b;
  font-size: 1rem;
  margin-bottom: 2rem;
}

.bookmark-list-btn {
  width: 100%;
  padding: 16px;
  background: #4A69E2;
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 12px;
}

.bookmark-list-btn:hover {
  background: #3B5BC7;
  transform: translateY(-1px);
}

.bookmark-list-btn:active {
  transform: translateY(0);
}



/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 15px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #e9ecef;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.modal-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  flex: 1;
  padding-right: 20px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.modal-close:hover {
  background: #f8f9fa;
  color: #495057;
}

.modal-body {
  padding: 20px;
}

.modal-image {
  width: 100%;
  height: 250px;
  overflow: hidden;
  border-radius: 10px;
  margin-bottom: 20px;
}

.modal-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 15px;
}

.info-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

/* 상세정보 스타일 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-item {
  background: #fff;
  color: #222;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 18px 16px;
  box-shadow: 0 1px 4px rgba(37,99,235,0.04);
  font-size: 1.13rem;
  line-height: 1.7;
  word-break: keep-all;
}
.detail-item p {
  color: #222;
  text-align: left;
  font-size: 1.13rem;
}

.detail-item h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 6px;
  border-bottom: 2px solid #dee2e6;
  padding-bottom: 4px;
}

.custom-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #fff;
  color: #2563eb;
  font-size: 1rem;
  font-weight: 600;
  padding: 15px 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(37,99,235,0.18);
  z-index: 3000;
  animation: fadeInOut 1.5s;
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translate(-50%, -60%); }
  10% { opacity: 1; transform: translate(-50%, -50%); }
  90% { opacity: 1; transform: translate(-50%, -50%); }
  100% { opacity: 0; transform: translate(-50%, -40%); }
}

/* overview 관련 커스텀 스타일 제거 (overview-item, info-title 등) */

/* 반응형 */
@media (max-width: 768px) {
  .recommend-page {
    padding: 12px;
  }
  
  .recommend-content {
    padding: 32px 20px;
  }
  
  .recommend-header {
    margin-bottom: 24px;
  }
  
  .title {
    font-size: 20px;
    margin-bottom: 6px;
  }
  
  .region-info {
    font-size: 14px;
  }
  
  .places-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .place-card {
    padding: 12px;
  }
  
  .place-title {
    font-size: 16px;
  }
  
  .keyword-tag {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }
  
  .more-keywords {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }
  
  .db-reference-container {
    font-size: 0.65rem;
  }
  
  .db-path {
    font-size: 0.6rem;
    padding: 0.15rem 0.3rem;
  }
  
  .modal-content {
    margin: 12px;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-title {
    font-size: 18px;
  }
  
  .modal-body {
    padding: 16px 20px;
  }
  
  .modal-image {
    height: 180px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .floating-back-btn {
    bottom: 20px;
    right: 20px;
    padding: 10px 16px;
    font-size: 13px;
  }
  
  /* 모바일에서 지도 높이 조정 */
  .google-map-container {
    height: 200px;
  }
}
</style>