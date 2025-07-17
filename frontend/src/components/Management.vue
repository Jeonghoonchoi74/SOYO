<template>
  <div class="management-container">
    <button class="back-btn" @click="goBack">{{ $t('management_back') }}</button>
    <h2 class="title">{{ $t('management_title') }}</h2>
    
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
      </div>
    </div>
    
    <!-- 리뷰 섹션 -->
    <div class="reviews-section">
      <h3 class="section-title">{{ $t('management_reviews') }}</h3>
      <div class="reviews-list">
        <template v-if="reviews.length > 0">
          <div v-for="(review, idx) in reviews" :key="idx" class="review-card">
            <div class="review-header">
              <img :src="review.placeImage" class="place-img" :alt="review.placeName" />
              <div class="review-info">
                <div class="place-name">{{ review.placeName }}</div>
                <div class="user-name">{{ review.userName }}</div>
                <div class="review-date">{{ formatDate(review.createdAt) }}</div>
              </div>
            </div>
            <div class="review-content">
              <p>{{ review.review }}</p>
            </div>
          </div>
        </template>
        <div v-else class="empty-state">
          <p>아직 리뷰가 없습니다.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { i18nState, $t } from '../i18n';
import { getAuth } from 'firebase/auth';
import { db } from '../firebase';
import { collection, onSnapshot, query, orderBy, getDocs } from 'firebase/firestore';

export default {
  name: 'Management',
  data() {
    return {
      reviews: [],
      statistics: {},
      isAdmin: false,
      unsubscribeReviews: null,
      unsubscribeUsers: null,
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
    // 실시간 리뷰 구독
    const reviewsQuery = query(collection(db, 'all_reviews'), orderBy('createdAt', 'desc'));
    this.unsubscribeReviews = onSnapshot(reviewsQuery, (snapshot) => {
      this.reviews = snapshot.docs.map(doc => doc.data());
      this.updateStatistics();
    });
    // 실시간 사용자 구독 (통계용)
    this.unsubscribeUsers = onSnapshot(collection(db, 'users'), (snapshot) => {
      this.updateStatistics();
    });
  },
  beforeUnmount() {
    if (this.unsubscribeReviews) this.unsubscribeReviews();
    if (this.unsubscribeUsers) this.unsubscribeUsers();
  },
  computed: {
    $t() { return $t; },
  },
  methods: {
    goBack() {
      this.$router.push('/bookmarks');
    },
    async updateStatistics() {
      // 전체 사용자 수
      const userSnap = await getDocs(collection(db, 'users'));
      const total_users = userSnap.size;
      // 전체 북마크 수
      let total_bookmarks = 0;
      for (const userDoc of userSnap.docs) {
        const bookmarksSnap = await getDocs(collection(db, 'users', userDoc.id, 'bookmarks'));
        total_bookmarks += bookmarksSnap.size;
      }
      // 전체 리뷰 수
      const total_reviews = this.reviews.length;
      // 장소별 통계
      const place_stats = {};
      this.reviews.forEach(review => {
        const place = review.placeName || 'Unknown';
        if (place_stats[place]) place_stats[place] += 1;
        else place_stats[place] = 1;
      });
      this.statistics = {
        total_users,
        total_reviews,
        total_bookmarks,
        place_stats
      };
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
.management-container {
  width: 800px;
  margin: 60px auto;
  padding: 64px 80px 96px 80px;
  border-radius: 32px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.back-btn {
  display: block;
  margin: 0 auto 2.5rem auto;
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

.back-btn:hover {
  background: #475569;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 3rem;
  text-align: center;
  color: #1e293b;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #334155;
  margin-bottom: 2rem;
  border-left: 4px solid #7c3aed;
  padding-left: 1rem;
}

.stats-section {
  width: 100%;
  max-width: 900px;
  margin-bottom: 4rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border: 1px solid #e2e8f0;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  color: #7c3aed;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  color: #64748b;
  font-weight: 600;
}

.place-stats {
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border: 1px solid #e2e8f0;
}

.place-stats h4 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #334155;
  margin-bottom: 1.5rem;
}

.place-stats-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.place-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.place-name {
  font-weight: 600;
  color: #475569;
}

.place-count {
  background: #7c3aed;
  color: #fff;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.reviews-section {
  width: 100%;
  max-width: 900px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.review-card {
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border: 1px solid #e2e8f0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.place-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 12px;
}

.review-info {
  flex: 1;
}

.review-info .place-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.3rem;
}

.review-info .user-name {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 0.2rem;
}

.review-info .review-date {
  font-size: 0.9rem;
  color: #94a3b8;
}

.review-content p {
  font-size: 1rem;
  color: #475569;
  line-height: 1.6;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background: #fff;
  border-radius: 16px;
  color: #64748b;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border: 1px solid #e2e8f0;
}

@media (max-width: 768px) {
  .management-container {
    width: 95%;
    margin: 20px auto;
    padding: 32px 20px 64px 20px;
    border-radius: 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .review-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .place-img {
    width: 120px;
    height: 120px;
  }
}
</style> 