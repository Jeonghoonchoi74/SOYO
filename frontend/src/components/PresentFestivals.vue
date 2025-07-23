<template>
  <div class="present-festivals">
    <div class="container">
      <h1 class="page-title">현재~12월 서울 행사</h1>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>행사 정보를 불러오는 중...</p>
      </div>
      
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
      </div>
      
      <div v-else-if="festivals.length === 0" class="no-data">
        <p>현재부터 12월까지의 행사가 없습니다.</p>
      </div>
      
      <div v-else class="festivals-grid">
        <div 
          v-for="festival in festivals" 
          :key="festival.contentid" 
          class="festival-card"
          @click="openModal(festival)"
        >
          <div class="festival-image">
            <img 
              v-if="festival.firstimage" 
              :src="festival.firstimage" 
              :alt="festival.title"
              @error="handleImageError"
            />
            <div v-else class="no-image">
              <span>이미지 없음</span>
            </div>
          </div>
          
          <div class="festival-content">
            <h3 class="festival-title">{{ festival.title }}</h3>
            
            <div class="festival-info">
              <div class="info-item">
                <span class="label">주소:</span>
                <span class="value">{{ festival.addr1 }}</span>
              </div>
              
              <div class="info-item">
                <span class="label">기간:</span>
                <span class="value">
                  {{ formatDate(festival.eventstartdate) }} ~ {{ formatDate(festival.eventenddate) }}
                </span>
              </div>
              
              <div v-if="festival.tel" class="info-item">
                <span class="label">연락처:</span>
                <span class="value">{{ formatTelForCard(festival.tel) }}</span>
              </div>
            </div>
            
            <div class="festival-status">
              <span :class="getStatusClass(festival)" class="status-badge">
                {{ getStatusText(festival) }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="summary">
        <p>현재부터 12월까지의 총 {{ festivals.length }}개 행사가 있습니다.</p>
      </div>
    </div>
    
    <!-- 상세 모달 -->
    <div v-if="selectedFestival" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ selectedFestival.title }}</h2>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="modal-image">
            <img 
              v-if="selectedFestival.firstimage" 
              :src="selectedFestival.firstimage" 
              :alt="selectedFestival.title"
            />
            <div v-else class="no-image">
              <span>이미지 없음</span>
            </div>
          </div>
          
          <div class="modal-info">
            <div class="info-section">
              <h3>행사 정보</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">주소:</span>
                  <span class="value">{{ selectedFestival.addr1 }}</span>
                </div>
                <div v-if="selectedFestival.addr2" class="info-item">
                  <span class="label">상세주소:</span>
                  <span class="value">{{ selectedFestival.addr2 }}</span>
                </div>

                <div class="info-item">
                  <span class="label">기간:</span>
                  <span class="value">
                    {{ formatDate(selectedFestival.eventstartdate) }} ~ {{ formatDate(selectedFestival.eventenddate) }}
                  </span>
                </div>
                <div v-if="selectedFestival.tel" class="info-item">
                  <span class="label">연락처:</span>
                  <span class="value" v-html="formatTelForDetail(selectedFestival.tel)"></span>
                </div>
                
                <div v-if="selectedFestival.detail_intro2?.usetimefestival" class="info-item">
                  <span class="label">이용 시간:</span>
                  <span class="value" v-html="formatPlaytime(selectedFestival.detail_intro2.usetimefestival)"></span>
                </div>
                
                <div v-if="selectedFestival.detail_intro2?.playtime" class="info-item">
                  <span class="label">공연 시간:</span>
                  <span class="value" v-html="formatPlaytime(selectedFestival.detail_intro2.playtime)"></span>
                </div>
                
                <div v-if="selectedFestival.detail_intro2?.spendtimefestival" class="info-item">
                  <span class="label">소요 시간:</span>
                  <span class="value">{{ selectedFestival.detail_intro2.spendtimefestival }}</span>
                </div>
                
                <div v-if="selectedFestival.detail_intro2?.agelimit" class="info-item">
                  <span class="label">연령 제한:</span>
                  <span class="value" v-html="formatPlaytime(selectedFestival.detail_intro2.agelimit)"></span>
                </div>
                
                <div v-if="selectedFestival.detail_intro2?.bookingplace" class="info-item">
                  <span class="label">예약 장소:</span>
                  <span class="value">{{ selectedFestival.detail_intro2.bookingplace }}</span>
                </div>
                
                <div v-if="selectedFestival.detail_intro2?.discountinfofestival" class="info-item">
                  <span class="label">할인 정보:</span>
                  <span class="value">{{ selectedFestival.detail_intro2.discountinfofestival }}</span>
                </div>
                
                <div v-if="selectedFestival.detail_intro2?.festivalgrade" class="info-item">
                  <span class="label">행사 등급:</span>
                  <span class="value">{{ selectedFestival.detail_intro2.festivalgrade }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">상태:</span>
                  <span class="value">
                    <span :class="getStatusClass(selectedFestival)" class="status-badge">
                      {{ getStatusText(selectedFestival) }}
                    </span>
                  </span>
                </div>
              </div>
            </div>
            
            <!-- 상세정보 섹션 -->
            <div v-if="selectedFestival.detail_intro2?.eventintro || selectedFestival.detail_intro2?.eventtext" class="info-section">
              <h3>상세 정보</h3>
              <div class="detail-content">
                <div v-if="selectedFestival.detail_intro2.eventintro" class="detail-item">
                  <h4>행사 소개</h4>
                  <p>{{ selectedFestival.detail_intro2.eventintro }}</p>
                </div>
                
                <div v-if="selectedFestival.detail_intro2.eventtext" class="detail-item">
                  <h4>행사 내용</h4>
                  <p>{{ selectedFestival.detail_intro2.eventtext }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { collection, query, where, limit, getDocs } from 'firebase/firestore';
import { db } from '../firebase.js';

const festivals = ref([]);
const loading = ref(true);
const error = ref(null);
const selectedFestival = ref(null);

// 현재 날짜를 YYYYMMDD 형식으로 변환
const getCurrentDate = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
};

// 날짜 형식 변환 (YYYYMMDD -> YYYY-MM-DD)
const formatDate = (dateString) => {
  if (!dateString || dateString.length !== 8) return '날짜 정보 없음';
  return `${dateString.substring(0, 4)}-${dateString.substring(4, 6)}-${dateString.substring(6, 8)}`;
};

// 연락처 포맷팅 (카드용 - 첫 번째 <br> 이전까지만)
const formatTelForCard = (telString) => {
  if (!telString) return '';
  
  // 첫 번째 <br> 태그의 위치 찾기
  const brIndex = telString.indexOf('<br>');
  
  if (brIndex !== -1) {
    // 첫 번째 <br> 태그까지만 반환
    return telString.substring(0, brIndex);
  }
  
  // <br> 태그가 없으면 전체 반환
  return telString;
};

// 연락처 포맷팅 (상세용 - <br> 태그를 실제 줄바꿈으로 변환)
const formatTelForDetail = (telString) => {
  if (!telString) return '';
  
  // <br> 태그를 <br> HTML 태그로 변환
  return telString.replace(/<br>/gi, '<br>');
};

// 공연 시간 포맷팅 (<br> 태그를 실제 줄바꿈으로 변환)
const formatPlaytime = (playtimeString) => {
  if (!playtimeString) return '';
  
  // <br> 태그를 <br> HTML 태그로 변환
  return playtimeString.replace(/<br>/gi, '<br>');
};

// 이미지 로드 에러 처리
const handleImageError = (event) => {
  event.target.style.display = 'none';
  event.target.nextElementSibling.style.display = 'flex';
};

// 현재부터 12월 31일까지의 행사 필터링
const isInTargetPeriod = (festival) => {
  const startDate = festival.eventstartdate;
  const endDate = festival.eventenddate;
  
  // 현재 날짜부터 12월 31일까지
  const currentDate = getCurrentDate();
  const targetEndDate = '20251231';
  
  return startDate && endDate && 
         startDate <= targetEndDate && 
         endDate >= currentDate;
};

// 행사 상태 텍스트 반환
const getStatusText = (festival) => {
  const currentDate = getCurrentDate();
  const startDate = festival.eventstartdate;
  const endDate = festival.eventenddate;
  
  if (!startDate || !endDate) return '날짜 정보 없음';
  
  if (currentDate < startDate) {
    return '예정';
  } else if (currentDate >= startDate && currentDate <= endDate) {
    return '진행중';
  } else {
    return '종료';
  }
};

// 행사 상태에 따른 CSS 클래스 반환
const getStatusClass = (festival) => {
  const currentDate = getCurrentDate();
  const startDate = festival.eventstartdate;
  const endDate = festival.eventenddate;
  
  if (!startDate || !endDate) return 'unknown';
  
  if (currentDate < startDate) {
    return 'upcoming';
  } else if (currentDate >= startDate && currentDate <= endDate) {
    return 'ongoing';
  } else {
    return 'ended';
  }
};

// Firebase에서 서울 행사 데이터 가져오기
const fetchPresentFestivals = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // Firebase에서 서울 행사 데이터 가져오기
    const seoulCollectionRef = collection(db, 'api_data', 'ko', '부산', 'events', 'items'); // 나중에는 Prefercen Input 에서 받아온 값으로 변경 예정정
    const querySnapshot = await getDocs(seoulCollectionRef);
    
    const allFestivals = [];
    querySnapshot.forEach((doc) => {
      const data = doc.data();
      allFestivals.push(data);
    });
    
    // 2025년 4월부터 12월까지의 행사만 필터링
    const targetFestivals = allFestivals.filter(isInTargetPeriod);
    
    // 상태별로 정렬 (진행중 → 예정 → 종료)
    const sortedFestivals = targetFestivals.sort((a, b) => {
      const statusA = getStatusClass(a);
      const statusB = getStatusClass(b);
      
      // 상태 우선순위: ongoing(진행중) > upcoming(예정) > ended(종료)
      const statusOrder = { 'ongoing': 0, 'upcoming': 1, 'ended': 2, 'unknown': 3 };
      
      if (statusOrder[statusA] !== statusOrder[statusB]) {
        return statusOrder[statusA] - statusOrder[statusB];
      }
      
      // 같은 상태 내에서는 시작일순으로 정렬
      return (a.eventstartdate || '') - (b.eventstartdate || '');
    });
    
    festivals.value = sortedFestivals;
    
  } catch (err) {
    console.error('행사 데이터 가져오기 오류:', err);
    error.value = '행사 정보를 불러오는 중 오류가 발생했습니다.';
  } finally {
    loading.value = false;
  }
};

// 모달 열기
const openModal = (festival) => {
  selectedFestival.value = festival;
};

// 모달 닫기
const closeModal = () => {
  selectedFestival.value = null;
};

onMounted(() => {
  fetchPresentFestivals();
});
</script>

<style scoped>
.present-festivals {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  text-align: center;
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 40px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.loading {
  text-align: center;
  color: white;
  padding: 60px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
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
  margin: 20px 0;
}

.no-data {
  text-align: center;
  color: white;
  padding: 60px 0;
  font-size: 1.2rem;
}

.festivals-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  margin-bottom: 40px;
  justify-content: center;
}

.festival-card {
  background: white;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  width: 350px;
  min-height: 500px;
  cursor: pointer;
}

.festival-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.festival-image {
  position: relative;
  height: 300px;
  overflow: hidden;
  flex-shrink: 0;
}

.festival-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.festival-card:hover .festival-image img {
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

.festival-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.festival-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.festival-info {
  margin-bottom: 15px;
  flex: 1;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #6c757d;
  min-width: 60px;
  margin-right: 10px;
}

.value {
  color: #495057;
  flex: 1;
  word-break: break-all;
}

.festival-status {
  display: flex;
  justify-content: flex-end;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
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
  color: white;
  font-size: 1.1rem;
  margin-top: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(10px);
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
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  flex: 1;
  padding-right: 20px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
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
  padding: 30px;
}

.modal-image {
  width: 100%;
  height: 300px;
  overflow: hidden;
  border-radius: 10px;
  margin-bottom: 30px;
}

.modal-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-info {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.info-section {
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 20px;
}

.info-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-section h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.status-display {
  display: flex;
  justify-content: flex-start;
}

/* 상세정보 스타일 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-item {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  background: #f8f9fa;
}

.detail-item h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
  border-bottom: 2px solid #dee2e6;
  padding-bottom: 5px;
}

.detail-item p {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #6c757d;
  margin: 0;
  white-space: pre-line;
}

.no-detail {
  color: #6c757d;
  font-style: italic;
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #dee2e6;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .container {
    padding: 0 15px;
  }
  
  .page-title {
    font-size: 2rem;
    margin-bottom: 30px;
  }
  
  .festivals-grid {
    flex-direction: column;
    gap: 20px;
  }
  
  .festival-card {
    margin-bottom: 20px;
  }
  
  .festival-content {
    padding: 15px;
  }
  
  .festival-title {
    font-size: 1.1rem;
  }
}
</style> 