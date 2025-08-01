<template>
      <div class="recommend-container">
      <div class="header">
        <h2 class="title">{{ $t('recommend_title') }}</h2>
      </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>추천 장소를 불러오는 중...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="places.length === 0" class="no-data">
      <p>추천할 장소가 없습니다.</p>
    </div>
    
    <div v-else class="places-grid">
      <div 
        v-for="(place, idx) in displayedPlaces" 
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
            <span>이미지 없음</span>
          </div>
        </div>
        
        <div class="place-content">
          <h3 class="place-title">{{ place.title }}</h3>
          
          <div class="place-info">
            <div class="info-item">
              <span class="label">주소:</span>
              <span class="value">{{ place.addr1 }}</span>
            </div>
            
            <div class="info-item">
              <span class="label">기간:</span>
              <span class="value">
                {{ formatDate(place.eventstartdate) }} ~ {{ formatDate(place.eventenddate) }}
              </span>
            </div>
            
            <div v-if="place.tel" class="info-item">
              <span class="label">연락처:</span>
              <span class="value">{{ formatTelForCard(place.tel) }}</span>
            </div>
          </div>
          
          <div class="place-status">
            <span :class="getStatusClass(place)" class="status-badge">
              {{ getStatusText(place) }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="summary">
      <p>총 {{ places.length }}개의 추천 장소 중 {{ displayedPlaces.length }}개를 보여주고 있습니다.</p>
    </div>
    
    <div v-if="hasMoreItems" class="load-more-container">
      <button class="load-more-btn" @click="loadMore" :disabled="loading">
        {{ loading ? '로딩 중...' : '더 보기' }}
      </button>
    </div>
    
    <button class="bookmark-list-btn" @click="goBookmark">{{ $t('recommend_bookmark_btn') }}</button>
    
    <button class="back-home-btn" @click="goHome">{{ $t('recommend_back_home') }}</button>
    
    <!-- 상세 모달 -->
    <div v-if="selectedPlace" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ selectedPlace.title }}</h2>
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
              <span>이미지 없음</span>
            </div>
          </div>
          
          <div class="modal-info">
            <div class="info-section">
              <h3>장소 정보</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">주소:</span>
                  <span class="value">{{ selectedPlace.addr1 }}</span>
                </div>
                <div v-if="selectedPlace.addr2" class="info-item">
                  <span class="label">상세주소:</span>
                  <span class="value">{{ selectedPlace.addr2 }}</span>
                </div>

                <div class="info-item">
                  <span class="label">기간:</span>
                  <span class="value">
                    {{ formatDate(selectedPlace.eventstartdate) }} ~ {{ formatDate(selectedPlace.eventenddate) }}
                  </span>
                </div>
                <div v-if="selectedPlace.tel" class="info-item">
                  <span class="label">연락처:</span>
                  <span class="value" v-html="formatTelForDetail(selectedPlace.tel)"></span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.usetimefestival" class="info-item">
                  <span class="label">이용 시간:</span>
                  <span class="value" v-html="formatPlaytime(selectedPlace.detail_intro2.usetimefestival)"></span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.playtime" class="info-item">
                  <span class="label">공연 시간:</span>
                  <span class="value" v-html="formatPlaytime(selectedPlace.detail_intro2.playtime)"></span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.spendtimefestival" class="info-item">
                  <span class="label">소요 시간:</span>
                  <span class="value">{{ selectedPlace.detail_intro2.spendtimefestival }}</span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.agelimit" class="info-item">
                  <span class="label">연령 제한:</span>
                  <span class="value" v-html="formatPlaytime(selectedPlace.detail_intro2.agelimit)"></span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.bookingplace" class="info-item">
                  <span class="label">예약 장소:</span>
                  <span class="value">{{ selectedPlace.detail_intro2.bookingplace }}</span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.discountinfofestival" class="info-item">
                  <span class="label">할인 정보:</span>
                  <span class="value">{{ selectedPlace.detail_intro2.discountinfofestival }}</span>
                </div>
                
                <div v-if="selectedPlace.detail_intro2?.festivalgrade" class="info-item">
                  <span class="label">행사 등급:</span>
                  <span class="value">{{ selectedPlace.detail_intro2.festivalgrade }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">상태:</span>
                  <span class="value">
                    <span :class="getStatusClass(selectedPlace)" class="status-badge">
                      {{ getStatusText(selectedPlace) }}
                    </span>
                  </span>
                </div>
              </div>
            </div>
            
            <!-- overview(개요) 섹션: 제목 없이 overview만 -->
            <div v-if="selectedPlace.overview" class="info-section">
              <p v-html="selectedPlace.overview" style="margin-top: 12px; color: #222; font-size: 1.13rem; line-height: 1.7; text-align: left;"></p>
            </div>
            <!-- 상세정보 섹션 -->
            <div v-if="selectedPlace.detail_intro2?.eventintro || selectedPlace.detail_intro2?.eventtext" class="info-section">
              <h3>상세 정보</h3>
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
</template>

<script>
import { i18nState, $t } from '../i18n';
import { getAuth } from 'firebase/auth';
import { collection, getDocs } from 'firebase/firestore';
import { db } from '../firebase.js';

let region = '부산';

export default {
  name: 'RecommendResult',
  data() {
    return {
      places: [],
      displayedPlaces: [],
      loading: true,
      error: null,
      selectedPlace: null,
      showModal: false,
      modalMessage: '',
      bookmarkDisabled: [],
      itemsPerPage: 6,
      currentPage: 1,
      hasMoreItems: true,
    };
  },
  computed: {
    $t() { return $t; },
  },
      async mounted() {
      await this.fetchRecommendPlaces();
      await this.loadUserBookmarks();
    },
  methods: {
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
      if (!dateString || dateString.length !== 8) return '날짜 정보 없음';
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

    // 현재부터 12월 31일까지의 행사 필터링
    isInTargetPeriod(place) {
      const startDate = place.eventstartdate;
      const endDate = place.eventenddate;
      const currentDate = this.getCurrentDate();
      const targetEndDate = '20251231';
      
      return startDate && endDate && 
             startDate <= targetEndDate && 
             endDate >= currentDate;
    },

    // 행사 상태 텍스트 반환
    getStatusText(place) {
      const currentDate = this.getCurrentDate();
      const startDate = place.eventstartdate;
      const endDate = place.eventenddate;
      
      if (!startDate || !endDate) return '날짜 정보 없음';
      
      if (currentDate < startDate) {
        return '예정';
      } else if (currentDate >= startDate && currentDate <= endDate) {
        return '진행중';
      } else {
        return '종료';
      }
    },

    // 행사 상태에 따른 CSS 클래스 반환
    getStatusClass(place) {
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
    },

    // Firebase에서 서울 행사 데이터 가져오기
    async fetchRecommendPlaces() {
      try {
        this.loading = true;
        this.error = null;
        
        // Firebase에서 서울 행사 데이터 가져오기
        const seoulCollectionRef = collection(db, 'api_data', 'ko', region, 'events', 'items');
        const querySnapshot = await getDocs(seoulCollectionRef);
        
        const allPlaces = [];
        querySnapshot.forEach((doc) => {
          const data = doc.data();
          allPlaces.push(data);
        });
        
        // 2025년 4월부터 12월까지의 행사만 필터링
        const targetPlaces = allPlaces.filter(this.isInTargetPeriod);
        
        // 상태별로 정렬 (진행중 → 예정 → 종료)
        const sortedPlaces = targetPlaces.sort((a, b) => {
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
        
        // 북마크 상태 초기화
        this.places = sortedPlaces.map(place => ({
          ...place,
          bookmarked: false
        }));
        
        // 초기 6개 항목 표시
        this.loadInitialItems();
        
      } catch (err) {
        console.error('추천 장소 데이터 가져오기 오류:', err);
        this.error = '추천 장소 정보를 불러오는 중 오류가 발생했습니다.';
      } finally {
        this.loading = false;
      }
    },

    // 초기 항목 로드
    loadInitialItems() {
      this.currentPage = 1;
      this.displayedPlaces = this.places.slice(0, this.itemsPerPage);
      this.hasMoreItems = this.places.length > this.itemsPerPage;
      this.bookmarkDisabled = Array(this.displayedPlaces.length).fill(false);
    },

    // 더 많은 항목 로드
    loadMore() {
      if (this.loading || !this.hasMoreItems) return;
      
      this.loading = true;
      
      // 현재 스크롤 위치 저장
      const scrollPosition = window.scrollY;
      
      setTimeout(() => {
        const startIndex = this.currentPage * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const newItems = this.places.slice(startIndex, endIndex);
        
        this.displayedPlaces = [...this.displayedPlaces, ...newItems];
        this.currentPage += 1;
        this.hasMoreItems = endIndex < this.places.length;
        
        // 북마크 비활성화 배열 업데이트
        this.bookmarkDisabled = Array(this.displayedPlaces.length).fill(false);
        
        this.loading = false;
        
        // 스크롤 위치 복원
        this.$nextTick(() => {
          window.scrollTo(0, scrollPosition);
        });
      }, 500); // 로딩 효과를 위한 지연
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
            this.places[idx].bookmarked = bookmarkedPlaces.includes(place.title);
          });
          
          // displayedPlaces도 업데이트
          this.displayedPlaces.forEach((place, idx) => {
            this.displayedPlaces[idx].bookmarked = bookmarkedPlaces.includes(place.title);
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
        this.showModalMessage('북마크 처리 중 오류가 발생했습니다.');
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
            name: this.places[idx].title,
            desc: this.places[idx].addr1,
            image: this.places[idx].firstimage,
            region: region,
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
.recommend-container {
  width: 800px;
  margin: 60px auto;
  padding: 64px 80px 96px 80px;
  border-radius: 32px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header {
  width: 100%;
  margin-bottom: 30px;
  text-align: center;
}

.back-home-btn {
  display: block;
  margin: 2rem auto 0 auto;
  background: #64748b;
  color: #fff;
  border: none;
  border-radius: 14px;
  padding: 1.1rem 0;
  width: 100%;
  max-width: 420px;
  font-size: 1.2rem;
  font-weight: 800;
  cursor: pointer;
  transition: background 0.2s;
}

.back-home-btn:hover {
  background: #475569;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 3rem;
  text-align: center;
  color: #1e293b;
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

.summary {
  text-align: center;
  color: #64748b;
  font-size: 1rem;
  margin-bottom: 2rem;
}

.bookmark-list-btn {
  width: 100%;
  max-width: 420px;
  padding: 1.4rem 0;
  background: #2563eb;
  color: #fff;
  font-size: 1.3rem;
  font-weight: 800;
  border: none;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(37,99,235,0.12);
  cursor: pointer;
  transition: all 0.2s;
}

.bookmark-list-btn:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}

.bookmark-list-btn:active {
  background: #1e40af;
  transform: translateY(0);
}

.load-more-container {
  text-align: center;
  margin: 2rem 0;
}

.load-more-btn {
  background: #e2e8f0;
  color: #475569;
  border: none;
  border-radius: 12px;
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background: #cbd5e1;
  transform: translateY(-2px);
}

.load-more-btn:disabled {
  background: #f1f5f9;
  color: #94a3b8;
  cursor: not-allowed;
  transform: none;
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

/* 모바일 반응형 */
@media (max-width: 768px) {
  .recommend-container {
    width: 100%;
    margin: 20px auto;
    padding: 40px 20px 60px 20px;
    border-radius: 20px;
  }
  
  .title {
    font-size: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .places-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .place-card {
    padding: 1rem;
  }
  
  .place-title {
    font-size: 1.1rem;
  }
  
  .modal-content {
    margin: 10px;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 15px 20px;
  }
  
  .modal-title {
    font-size: 1.1rem;
  }
  
  .modal-body {
    padding: 15px;
  }
  
  .modal-image {
    height: 200px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  .overview-item {
    font-size: 0.97rem;
    padding: 12px 6px;
  }
  .info-title {
    font-size: 1rem;
  }
}
</style>