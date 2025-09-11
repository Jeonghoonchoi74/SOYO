<template>
  <div class="bookmark-page">
    <div class="bookmark-container">
      <div class="bookmark-header">
        <h2 class="title">{{ $t('bookmark_title') }}</h2>
      </div>
      <div class="bookmark-list">
      <template v-if="bookmarked.length > 0">
        <div v-for="(place, idx) in bookmarked" :key="idx" class="bookmark-card">
          <button class="delete-btn" @click="deleteBookmark(idx, place)">🗑️</button>
          <img :src="place.image" class="place-img" :alt="$t('bookmark_place_img_alt')" @click="showPlaceDetail(place)" />
          <div class="place-info">
            <div class="place-name">{{ place.name }}</div>
            <div class="place-desc">{{ place.desc }}</div>

            <!-- 통합된 리뷰 카드 -->
            <div class="unified-review-card">
              <!-- 읽기 모드 -->
              <div v-if="!place.isEditing" class="read-mode">
                <!-- 평점 표시 -->
                <div class="rating-display">
                  <span class="info-label">{{ $t('bookmark_rating') }}</span>
                  <div class="star-rating readonly">
                    <span v-for="star in 5" :key="star" class="star" :class="{ active: star <= (place.rating || 0) }">
                      ★
                    </span>
                  </div>
                  <span class="rating-text">{{ place.rating || 0 }}/5</span>
                </div>

                <!-- 공개여부 표시 -->
                <div class="visibility-display">
                  <span class="info-label">{{ $t('bookmark_visibility') }}</span>
                  <span class="visibility-status" :class="{ public: place.isPublic }">
                    {{ place.isPublic ? $t('bookmark_public') : $t('bookmark_private') }}
                  </span>
                </div>

                <!-- 리뷰 표시 -->
                <div v-if="place.review" class="review-display">
                  <span class="info-label">{{ $t('bookmark_review') }}</span>
                  <div class="review-content">
                    <p>{{ place.review }}</p>
                  </div>
                </div>

                <!-- 액션 버튼들 -->
                <div class="action-buttons">
                  <!-- 리뷰가 있는 경우: 수정 버튼 -->
                  <button v-if="place.review" class="edit-btn" @click="editReview(idx, place)">
                    {{ $t('bookmark_edit') }}
                  </button>
                  <!-- 리뷰가 없는 경우: 리뷰 작성 버튼 -->
                  <button v-else class="write-review-btn" @click="editReview(idx, place)">
                    {{ $t('bookmark_write_review') }}
                  </button>
                </div>
              </div>

              <!-- 편집 모드 -->
              <div v-else class="edit-mode" :data-mode="place.review ? $t('review_edit_mode') : $t('review_write_mode')">
                <!-- 평점 편집 -->
                <div class="rating-edit">
                  <div class="edit-label">{{ $t('bookmark_rating') }}</div>
                  <div class="star-rating editable">
                    <span v-for="star in 5" :key="star" class="star"
                      :class="{ active: star <= (place.tempRating || 0) }" @click="setTempRating(place, star)">
                      ★
                    </span>
                  </div>
                  <span class="rating-text">{{ place.tempRating || 0 }}/5</span>
                </div>

                <!-- 공개여부 편집 -->
                <div class="visibility-edit">
                  <div class="edit-label">{{ $t('bookmark_visibility') }}</div>
                  <label class="visibility-toggle">
                    <input type="checkbox" v-model="place.tempIsPublic" />
                    <span class="toggle-slider"></span>
                    <span class="toggle-label">{{ place.tempIsPublic ? $t('bookmark_public') : $t('bookmark_private') }}</span>
                  </label>
                </div>

                <!-- 리뷰 편집 -->
                <div class="review-edit">
                  <div class="edit-label">{{ $t('review_label') }}</div>
                  <textarea v-model="place.reviewText" class="review-input"
                    :placeholder="place.review ? $t('review_placeholder') : $t('review_placeholder_text')" rows="3" />
                </div>

                <!-- 편집 버튼들 -->
                <div class="edit-buttons">
                  <button class="save-btn" @click="submitReview(idx, place)">
                    {{ place.review ? $t('save_button') : $t('register_review_button') }}
                  </button>
                  <button class="cancel-btn" @click="cancelEdit(idx, place)">
                    {{ $t('cancel_button') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="empty-state">
          <p>{{ $t('bookmark_empty') }}</p>
        </div>
      </template>
      </div>
    </div>

    <div v-if="showModal" class="custom-modal">{{ modalMessage }}</div>

    <!-- 장소 상세 정보 모달 -->
    <div v-if="showDetailModal" class="detail-modal-overlay" @click="closeDetailModal">
      <div class="detail-modal-content" @click.stop>
        <div class="detail-modal-header">
          <h3 class="detail-modal-title">{{ selectedPlace?.name }}</h3>
          <button class="detail-modal-close" @click="closeDetailModal">×</button>
        </div>
        <div class="detail-modal-body">
          <div class="detail-image-container">
            <img :src="selectedPlace?.image" :alt="selectedPlace?.name" class="detail-image" />
          </div>
          <div class="detail-info">
            <div class="detail-section">
              <h4 class="detail-section-title">📝 {{ $t('detail_description') }}</h4>
              <p class="detail-description">{{ selectedPlace?.desc }}</p>
            </div>
            
            <div v-if="selectedPlace?.address" class="detail-section">
              <h4 class="detail-section-title">📍 {{ $t('detail_address') }}</h4>
              <p class="detail-address">{{ selectedPlace?.address }}</p>
            </div>
            
            <div v-if="selectedPlace?.detailAddress" class="detail-section">
              <h4 class="detail-section-title">📍 {{ $t('detail_detail_address') }}</h4>
              <p class="detail-address">{{ selectedPlace?.detailAddress }}</p>
            </div>
            
            <div v-if="selectedPlace?.contact" class="detail-section">
              <h4 class="detail-section-title">📞 {{ $t('detail_contact') }}</h4>
              <p class="detail-contact">{{ selectedPlace?.contact }}</p>
            </div>
            
            <div v-if="selectedPlace?.openingHours" class="detail-section">
              <h4 class="detail-section-title">🕒 {{ $t('detail_opening_hours') }}</h4>
              <p class="detail-hours">{{ selectedPlace?.openingHours }}</p>
            </div>
            
            <div v-if="selectedPlace?.restDay" class="detail-section">
              <h4 class="detail-section-title">📅 {{ $t('detail_rest_day') }}</h4>
              <p class="detail-rest-day">{{ selectedPlace?.restDay }}</p>
            </div>
            
            <div v-if="selectedPlace?.representativeMenu" class="detail-section">
              <h4 class="detail-section-title">🍽️ {{ $t('detail_representative_menu') }}</h4>
              <p class="detail-menu">{{ selectedPlace?.representativeMenu }}</p>
            </div>
            
            <div v-if="selectedPlace?.menu" class="detail-section">
              <h4 class="detail-section-title">🍽️ {{ $t('detail_menu') }}</h4>
              <p class="detail-menu">{{ selectedPlace?.menu }}</p>
            </div>
            
            <div v-if="selectedPlace?.eventStartDate && selectedPlace?.eventEndDate" class="detail-section">
              <h4 class="detail-section-title">📅 {{ $t('detail_event_period') }}</h4>
              <p class="detail-period">{{ selectedPlace?.eventStartDate }} ~ {{ selectedPlace?.eventEndDate }}</p>
            </div>
            
            <div v-if="selectedPlace?.eventIntro" class="detail-section">
              <h4 class="detail-section-title">🎪 {{ $t('detail_event_intro') }}</h4>
              <p class="detail-intro">{{ selectedPlace?.eventIntro }}</p>
            </div>
            
            <div v-if="selectedPlace?.eventContent" class="detail-section">
              <h4 class="detail-section-title">📋 {{ $t('detail_event_content') }}</h4>
              <p class="detail-content">{{ selectedPlace?.eventContent }}</p>
            </div>
            
            <div v-if="selectedPlace?.inquiry" class="detail-section">
              <h4 class="detail-section-title">📞 {{ $t('detail_inquiry') }}</h4>
              <p class="detail-inquiry">{{ selectedPlace?.inquiry }}</p>
            </div>
            
            <div v-if="selectedPlace?.usageTime" class="detail-section">
              <h4 class="detail-section-title">⏰ {{ $t('detail_usage_time') }}</h4>
              <p class="detail-usage-time">{{ selectedPlace?.usageTime }}</p>
            </div>
            
            <div v-if="selectedPlace?.performanceTime" class="detail-section">
              <h4 class="detail-section-title">🎭 {{ $t('detail_performance_time') }}</h4>
              <p class="detail-performance-time">{{ selectedPlace?.performanceTime }}</p>
            </div>
            
            <div v-if="selectedPlace?.duration" class="detail-section">
              <h4 class="detail-section-title">⏱️ {{ $t('detail_duration') }}</h4>
              <p class="detail-duration">{{ selectedPlace?.duration }}</p>
            </div>
            
            <div v-if="selectedPlace?.ageLimit" class="detail-section">
              <h4 class="detail-section-title">👥 {{ $t('detail_age_limit') }}</h4>
              <p class="detail-age-limit">{{ selectedPlace?.ageLimit }}</p>
            </div>
            
            <div v-if="selectedPlace?.bookingPlace" class="detail-section">
              <h4 class="detail-section-title">📋 {{ $t('detail_booking_place') }}</h4>
              <p class="detail-booking-place">{{ selectedPlace?.bookingPlace }}</p>
            </div>
            
            <div v-if="selectedPlace?.discountInfo" class="detail-section">
              <h4 class="detail-section-title">💰 {{ $t('detail_discount_info') }}</h4>
              <p class="detail-discount">{{ selectedPlace?.discountInfo }}</p>
            </div>
            
            <div v-if="selectedPlace?.eventGrade" class="detail-section">
              <h4 class="detail-section-title">⭐ {{ $t('detail_event_grade') }}</h4>
              <p class="detail-grade">{{ selectedPlace?.eventGrade }}</p>
            </div>
            
            <div v-if="selectedPlace?.status" class="detail-section">
              <h4 class="detail-section-title">📊 {{ $t('detail_status') }}</h4>
              <p class="detail-status">{{ selectedPlace?.status }}</p>
            </div>
          </div>
        </div>
        <div class="detail-modal-footer">
          <button class="detail-modal-btn" @click="closeDetailModal">{{ $t('close_button') }}</button>
        </div>
      </div>
    </div>
    
    <!-- 뒤로가기 버튼 (왼쪽 하단) -->
    <button class="back-btn" @click="goBack">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
    </button>
  </div>
</template>

<script>
import { i18nState, $t } from '../i18n';
import { getAuth } from 'firebase/auth';
export default {
  name: 'BookmarkList',
  data() {
    return {
      bookmarked: [],
      showModal: false,
      modalMessage: '',
      showDetailModal: false,
      selectedPlace: null,
    };
  },
  async mounted() {
    const auth = getAuth();
    const user = auth.currentUser;
    if (!user) return;

    const res = await fetch('/api/get_user_bookmarks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid: user.uid })
    });
    const result = await res.json();
    if (result.success && result.bookmarks) {
      this.bookmarked = result.bookmarks;
      // 각 북마크에 필요한 필드들 추가
      this.bookmarked.forEach(place => {
        if (!place.reviewText) {
          place.reviewText = '';
        }
        place.isEditing = false;
        // rating과 isPublic 기본값 설정
        if (place.rating === undefined) {
          place.rating = 0;
        }
        if (place.isPublic === undefined) {
          place.isPublic = false;
        }
        // 임시 편집값들 초기화
        place.tempRating = place.rating;
        place.tempIsPublic = place.isPublic;
      });
    }

    // 사용자 리뷰 로드
    const reviewsRes = await fetch('/api/get_user_reviews', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid: user.uid })
    });
    const reviewsResult = await reviewsRes.json();
    if (reviewsResult.success && reviewsResult.reviews) {
      // 북마크에 리뷰 매칭
      reviewsResult.reviews.forEach(review => {
        const bookmark = this.bookmarked.find(place => place.name === review.placeId);
        if (bookmark) {
          bookmark.review = review.review;
        }
      });
    }
  },
  computed: {
    $t() { return $t; },
  },
  methods: {
    goBack() {
      this.$router.push('/main');
    },
    editReview(idx, place) {
      place.reviewText = place.review || '';
      place.tempRating = place.rating;
      place.tempIsPublic = place.isPublic;
      place.isEditing = true;
    },
    cancelEdit(idx, place) {
      place.isEditing = false;
      place.reviewText = '';
      place.tempRating = place.rating;
      place.tempIsPublic = place.isPublic;
    },
    async submitReview(idx, place) {
      const auth = getAuth();
      const user = auth.currentUser;
      if (!user) return;

      try {
        // 평점과 공개여부 업데이트
        if (place.isEditing && (place.tempRating !== place.rating || place.tempIsPublic !== place.isPublic)) {
          // 평점 업데이트
          if (place.tempRating !== place.rating) {
            const ratingResponse = await fetch('/api/update_bookmark_rating', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                uid: user.uid,
                contentId: place.contentId, // contentId 사용
                rating: place.tempRating
              })
            });

            const ratingResult = await ratingResponse.json();
            if (!ratingResult.success) {
              throw new Error(ratingResult.error || this.$t('rating_save_error'));
            }
            place.rating = place.tempRating;
          }

          // 공개여부 업데이트
          if (place.tempIsPublic !== place.isPublic) {
            const visibilityResponse = await fetch('/api/update_bookmark_visibility', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                uid: user.uid,
                contentId: place.contentId, // contentId 사용
                isPublic: place.tempIsPublic
              })
            });

            const visibilityResult = await visibilityResponse.json();
            if (!visibilityResult.success) {
              throw new Error(visibilityResult.error || this.$t('visibility_save_error'));
            }
            place.isPublic = place.tempIsPublic;
          }
        }

        // 리뷰 저장 (리뷰가 있는 경우에만)
        if (place.reviewText && place.reviewText.trim()) {
          // 사용자 선호도에서 region 가져오기
          let userRegion = this.$t('nationwide_default'); // 기본값
          try {
            const preferencesResponse = await fetch('/api/get_user_preferences', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ uid: user.uid })
            });
            
            const preferencesResult = await preferencesResponse.json();
            if (preferencesResult.success && preferencesResult.preferences && preferencesResult.preferences.region) {
              userRegion = preferencesResult.preferences.region;
            }
          } catch (error) {
            console.warn(this.$t('user_preference_error'), error);
          }

          const response = await fetch('/api/save_review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              uid: user.uid,
              contentId: place.contentId, // contentId 사용
              placeName: place.name,
              placeDesc: place.desc,
              placeImage: place.image,
              review: place.reviewText.trim(),
              rating: place.rating || 0,
              isPublic: place.isPublic || false,
              region: userRegion, // 사용자 선호도에서 가져온 region 사용
              userName: user.displayName || user.email
            })
          });

          if (!response.ok) {
            const result = await response.json();
            throw new Error(result.error || `HTTP error! status: ${response.status}`);
          }

          const result = await response.json();

          if (result.success) {
            place.review = place.reviewText.trim();
          } else {
            throw new Error(result.error || this.$t('server_error'));
          }
        }

        // 편집 모드 종료
        place.reviewText = '';
        place.isEditing = false;
        this.showModalMessage(this.$t('saved_successfully'));

      } catch (error) {
        console.error('저장 오류:', error);
        this.showModalMessage(`${this.$t('save_error')} ${error.message}`);
      }
    },
    async deleteBookmark(idx, place) {
      const auth = getAuth();
      const user = auth.currentUser;
      if (!user) return;

      console.log(this.$t('bookmark_delete_info'), place);
      console.log(this.$t('bookmark_place_id'), place.name);

      const response = await fetch('/api/delete_user_bookmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid: user.uid, contentId: place.contentId }) // contentId 사용
      });

      const result = await response.json();
      if (result.success) {
        this.bookmarked.splice(idx, 1);
        this.showModalMessage(this.$t('delete_bookmark_alert'));
      } else {
        console.error('북마크 삭제 실패:', result.error);
        this.showModalMessage(this.$t('bookmark_delete_failed'));
      }
    },
    showModalMessage(msg) {
      this.modalMessage = msg;
      this.showModal = true;
      setTimeout(() => {
        this.showModal = false;
      }, 1500);
    },
    setTempRating(place, rating) {
      place.tempRating = rating;
    },
    showPlaceDetail(place) {
      this.selectedPlace = place;
      this.showDetailModal = true;
    },
    closeDetailModal() {
      this.showDetailModal = false;
      this.selectedPlace = null;
    },
  },
};
</script>

<style scoped>
/* 네이버 지식iN 스타일 - Community.vue 베이스 */
.bookmark-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  padding: 20px;
  display: flex;
  justify-content: center;
}

.bookmark-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.bookmark-header {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.back-btn {
  position: fixed;
  bottom: 20px;
  left: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: none;
  background: #4A69E2;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 1000;
}

.back-btn:hover {
  background: #3B5BC7;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #212529;
  margin: 0;
  text-align: center;
  flex: 1;
}

.section {
  width: 100%;
  max-width: 480px;
  margin: 0 auto 3rem auto;
}

.bookmark-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bookmark-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  border: 1px solid #e9ecef;
  transition: all 0.2s ease;
  position: relative;
}

.bookmark-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #4A69E2;
}

.place-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.place-img:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.place-info {
  flex: 1;
  text-align: left;
  min-width: 0;
}

.place-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #ff6b35;
  text-align: left;
  line-height: 1.3;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.place-desc {
  font-size: 1rem;
  color: #64748b;
  text-align: left;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.empty-state {
  text-align: left;
  padding: 2rem;
  background-color: #f8fafc;
  border-radius: 12px;
  color: #64748b;
  width: 100%;
}

.back-home-btn {
  display: block;
  margin: 0 auto 2.5rem auto;
  background: #2563eb;
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
  background: #1d4ed8;
}

.delete-btn {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  font-size: 1.2rem;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s ease;
  border-radius: 12px;
  padding: 0.8rem;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
}

.delete-btn:hover {
  background: #fef2f2;
  border-color: #fecaca;
  color: #ef4444;
  transform: scale(1.05);
}

.delete-btn:active {
  transform: scale(0.95);
}

.custom-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #fff;
  color: #2563eb;
  font-size: 1.2rem;
  font-weight: 700;
  padding: 1.5rem 2.5rem;
  border-radius: 18px;
  box-shadow: 0 8px 32px rgba(37, 99, 235, 0.18);
  z-index: 3000;
  animation: fadeInOut 1.5s;
}

@keyframes fadeInOut {
  0% {
    opacity: 0;
    transform: translate(-50%, -60%);
  }

  10% {
    opacity: 1;
    transform: translate(-50%, -50%);
  }

  90% {
    opacity: 1;
    transform: translate(-50%, -50%);
  }

  100% {
    opacity: 0;
    transform: translate(-50%, -40%);
  }
}


/*
 통합된 리뷰 카드 스타일 */
.unified-review-card {
  margin-top: 1rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
}

.unified-review-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 읽기 모드 스타일 */
.read-mode {
  padding: 1.5rem;
}

.rating-display,
.visibility-display,
.review-display {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.review-display {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.info-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: #374151;
  min-width: 80px;
  flex-shrink: 0;
}

.review-content {
  flex: 1;
  padding: 0;
}

.review-content p {
  font-size: 0.95rem;
  color: #374151;
  margin: 0;
  line-height: 1.6;
  font-style: italic;
}



.action-buttons {
  display: flex;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.edit-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.8rem 2rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.edit-btn:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.write-review-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.8rem 2rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.write-review-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* 편집 모드 스타일 */
.edit-mode {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 1.5rem;
  position: relative;
}

.edit-mode::before {
  content: attr(data-mode);
  display: block;
  background: #3b82f6;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.4rem 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  margin-bottom: 1rem;
  width: fit-content;
}

.rating-edit,
.visibility-edit,
.review-edit {
  margin-bottom: 1.5rem;
}

.edit-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: #374151;
  margin-bottom: 0.8rem;
  display: block;
}

.star-rating {
  display: flex;
  gap: 0.2rem;
  align-items: center;
}

.star-rating.readonly .star {
  cursor: default;
}

.star-rating.editable .star {
  cursor: pointer;
  transform: scale(1);
  transition: all 0.2s ease;
}

.star-rating.editable .star:hover {
  color: #f59e0b;
  transform: scale(1.1);
}

.star {
  font-size: 1.4rem;
  color: #d1d5db;
  transition: all 0.2s ease;
  user-select: none;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.star.active {
  color: #fbbf24;
  filter: drop-shadow(0 0 4px rgba(251, 191, 36, 0.3));
}

.rating-text {
  font-size: 0.9rem;
  color: #6b7280;
  margin-left: 0.5rem;
  font-weight: 600;
  background: #f1f5f9;
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
}

.visibility-status {
  display: inline-flex;
  align-items: center;
  font-size: 0.85rem;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  background: #f1f5f9;
  color: #64748b;
  font-weight: 600;
  border: 1px solid #e2e8f0;
}

.visibility-status.public {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #15803d;
  border-color: #bbf7d0;
}



/* 공개여부 토글 스타일 */
.visibility-toggle {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  cursor: pointer;
  user-select: none;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background 0.2s;
}

.visibility-toggle:hover {
  background: rgba(59, 130, 246, 0.05);
}

.visibility-toggle input[type="checkbox"] {
  display: none;
}

.toggle-slider {
  position: relative;
  width: 52px;
  height: 28px;
  background: #cbd5e1;
  border-radius: 14px;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 24px;
  height: 24px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.visibility-toggle input:checked+.toggle-slider {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.visibility-toggle input:checked+.toggle-slider::before {
  transform: translateX(24px);
}

.toggle-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
}

.review-input {
  width: 100%;
  padding: 1rem;
  font-size: 0.95rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
  box-sizing: border-box;
  resize: vertical;
  color: #1e293b;
  transition: all 0.2s ease;
  font-family: inherit;
  line-height: 1.5;
  min-height: 80px;
}

.review-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background: #fefefe;
}

.review-input::placeholder {
  color: #9ca3af;
}

.edit-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.save-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.8rem 2rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.save-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.cancel-btn {
  background: #f8fafc;
  color: #64748b;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.8rem 2rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
}

/* 반응형 */
@media (max-width: 768px) {
  .bookmark-page {
    padding: 12px;
  }
  
  .bookmark-container {
    max-width: 100%;
  }
  
  .bookmark-header {
    padding: 16px 20px;
    margin-bottom: 12px;
  }
  
  .back-btn {
    width: 50px;
    height: 50px;
  }
  
  .title {
    font-size: 18px;
    text-align: center;
  }
  
  .bookmark-list {
    gap: 6px;
  }
  
  .bookmark-card {
    padding: 16px;
    gap: 12px;
    flex-direction: column;
  }
  
  .place-info {
    width: 100%;
  }
  
  .place-img {
    width: 60px;
    height: 60px;
  }
  
  .place-name {
    font-size: 15px;
  }
  
  .place-desc {
    font-size: 13px;
  }
  
  /* 리뷰 입력란 모바일 최적화 */
  .review-input {
    padding: 12px;
    font-size: 16px; /* 모바일에서 더 큰 폰트 */
    min-height: 100px; /* 더 높은 최소 높이 */
    line-height: 1.6;
  }
  
  .review-edit {
    margin-bottom: 1rem;
  }
  
  .edit-label {
    font-size: 14px;
    margin-bottom: 6px;
  }
  
  .edit-buttons {
    flex-direction: column;
    gap: 8px;
  }
  
  .save-btn,
  .cancel-btn {
    width: 100%;
    padding: 12px;
    font-size: 14px;
  }
  
  /* 모바일에서 쓰레기통 버튼 크기 조정 */
  .delete-btn {
    width: 40px;
    height: 40px;
    padding: 0.6rem;
    font-size: 1rem;
    top: 8px;
    right: 8px;
  }
}

/* 장소 상세 정보 모달 스타일 */
.detail-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 5000;
  padding: 20px;
  box-sizing: border-box;
}

.detail-modal-content {
  background: white;
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.detail-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px 24px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.detail-modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  line-height: 1.3;
}

.detail-modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.detail-modal-close:hover {
  background: #f1f5f9;
  color: #374151;
}

.detail-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.detail-image-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
  position: relative;
}

.detail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-info {
  padding: 24px;
}

.detail-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}

.detail-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.detail-section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #374151;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-description,
.detail-address,
.detail-contact,
.detail-hours,
.detail-rest-day,
.detail-menu,
.detail-period,
.detail-intro,
.detail-content,
.detail-inquiry,
.detail-usage-time,
.detail-performance-time,
.detail-duration,
.detail-age-limit,
.detail-booking-place,
.detail-discount,
.detail-grade,
.detail-status {
  font-size: 0.95rem;
  color: #4b5563;
  line-height: 1.6;
  margin: 0;
  word-break: break-word;
}

.detail-modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
}

.detail-modal-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.detail-modal-btn:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .detail-modal-overlay {
    padding: 12px;
  }
  
  .detail-modal-content {
    max-height: 95vh;
  }
  
  .detail-modal-header {
    padding: 20px 20px 16px 20px;
  }
  
  .detail-modal-title {
    font-size: 1.3rem;
  }
  
  .detail-info {
    padding: 20px;
  }
  
  .detail-section {
    margin-bottom: 20px;
    padding-bottom: 16px;
  }
  
  .detail-section-title {
    font-size: 0.95rem;
    margin-bottom: 10px;
  }
  
  .detail-description,
  .detail-address,
  .detail-contact,
  .detail-hours,
  .detail-rest-day,
  .detail-menu,
  .detail-period,
  .detail-intro,
  .detail-content,
  .detail-inquiry,
  .detail-usage-time,
  .detail-performance-time,
  .detail-duration,
  .detail-age-limit,
  .detail-booking-place,
  .detail-discount,
  .detail-grade,
  .detail-status {
    font-size: 0.9rem;
  }
  
  .detail-modal-footer {
    padding: 16px 20px;
  }
  
  .detail-modal-btn {
    padding: 10px 20px;
    font-size: 0.95rem;
  }
}
</style>