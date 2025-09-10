<template>
  <div class="management-page">
    <div class="management-content">
      <div class="management-header">
        <button class="back-btn" @click="goBack">{{ $t('management_back') }}</button>
        <h2 class="title">{{ $t('management_title') }}</h2>
      </div>
    
    <!-- 통계 섹션 -->
    <div class="stats-section">
      <h3 class="section-title">{{ $t('management_stats') }}</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ statistics.total_users || 0 }}</div>
          <div class="stat-label">전체 사용자</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ statistics.total_reviews || 0 }}</div>
          <div class="stat-label">전체 리뷰</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ statistics.total_bookmarks || 0 }}</div>
          <div class="stat-label">전체 북마크</div>
        </div>
      </div>
      
      <!-- 장소별 통계 -->
      <div class="place-stats">
        <h4>장소별 방문 통계</h4>
        <div class="place-stats-list">
          <div v-for="(count, place) in statistics.place_stats" :key="place" class="place-stat-item">
            <span class="place-name">{{ place }}</span>
            <span class="place-count">{{ count }}회</span>
          </div>
        </div>
        <div v-if="Object.keys(statistics.place_stats || {}).length === 0" class="no-data">
          <p>아직 방문한 장소가 없습니다.</p>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
import { $t } from '../i18n';
import { getAuth } from 'firebase/auth';

export default {
  name: 'Management',
  data() {
    return {
      statistics: {},
      isAdmin: false,
    };
  },
  async mounted() {
    const auth = getAuth();
    const user = auth.currentUser;
    if (!user || user.email !== 'admin@gmail.com') {
      this.$router.push('/');
      return;
    }
    this.isAdmin = true;
    await this.loadStatistics();
  },
  computed: {
    $t() { return $t; },
  },
  methods: {
    goBack() {
      this.$router.push('/bookmarks');
    },
    async loadStatistics() {
      try {
        const response = await fetch('/api/get_statistics');
        const result = await response.json();
        
        if (result.success) {
          this.statistics = result.statistics;
        } else {
          console.error('통계 로드 실패:', result.error);
        }
      } catch (error) {
        console.error('통계 로드 오류:', error);
      }
    },
    formatDate(timestamp) {
      if (!timestamp) return '';
      let date;
      if (timestamp.toDate) date = timestamp.toDate();
      else if (timestamp.seconds) date = new Date(timestamp.seconds * 1000);
      else date = new Date(timestamp);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
  },
};
</script>

<style scoped>
/* 네이버 지식iN 스타일 - Community.vue 베이스 */
.management-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  padding: 20px;
}

.management-content {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
  margin: 0 auto;
}

.management-header {
  text-align: center;
  margin-bottom: 32px;
}

.back-btn {
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
  margin-bottom: 16px;
}

.back-btn:hover {
  background: #3B5BC7;
}

.title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 0;
  color: #212529;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #212529;
  margin-bottom: 24px;
  border-left: 4px solid #4A69E2;
  padding-left: 16px;
}

.stats-section {
  width: 100%;
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 1px solid #e9ecef;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #4A69E2;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
}

.place-stats {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.place-stats h4 {
  font-size: 18px;
  font-weight: 600;
  color: #212529;
  margin-bottom: 16px;
}

.place-stats-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.place-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.place-name {
  font-weight: 500;
  color: #495057;
  font-size: 14px;
}

.place-count {
  background: #4A69E2;
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.no-data {
  text-align: center;
  padding: 24px;
  color: #6c757d;
  font-style: italic;
}

.no-data p {
  margin: 0;
  font-size: 14px;
}

/* 반응형 */
@media (max-width: 768px) {
  .management-page {
    padding: 12px;
  }
  
  .management-content {
    padding: 32px 20px;
  }
  
  .management-header {
    margin-bottom: 24px;
  }
  
  .title {
    font-size: 20px;
  }
  
  .back-btn {
    padding: 14px;
    font-size: 15px;
    margin-bottom: 12px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .stat-label {
    font-size: 13px;
  }
  
  .place-stats {
    padding: 16px;
  }
  
  .place-stats h4 {
    font-size: 16px;
    margin-bottom: 12px;
  }
  
  .place-stat-item {
    padding: 10px 12px;
  }
  
  .place-name {
    font-size: 13px;
  }
  
  .place-count {
    font-size: 11px;
    padding: 3px 8px;
  }
}
</style> 