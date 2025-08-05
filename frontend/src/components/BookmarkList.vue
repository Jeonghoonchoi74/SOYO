<template>
  <div class="bookmark-container">
    <button class="back-home-btn" @click="goHome">{{ $t('bookmark_back_home') }}</button>
    <h2 class="title">{{ $t('bookmark_title') }}</h2>
    <div class="bookmark-list">
      <template v-if="bookmarked.length > 0">
        <div v-for="(place, idx) in bookmarked" :key="idx" class="bookmark-card">
          <img :src="place.image" class="place-img" :alt="$t('bookmark_place_img_alt')" />
          <div class="place-info">
            <div class="place-name">{{ place.name }}</div>
            <div class="place-desc">{{ place.desc }}</div>

            <!-- 통합된 리뷰 카드 -->
            <div class="unified-review-card">
              <!-- 읽기 모드 -->
              <div v-if="!place.isEditing" class="read-mode">
                <!-- 평점 표시 -->
                <div class="rating-display">
                  <span class="info-label">평점:</span>
                  <div class="star-rating readonly">
                    <span v-for="star in 5" :key="star" class="star" :class="{ active: star <= (place.rating || 0) }">
                      ★
                    </span>
                  </div>
                  <span class="rating-text">{{ place.rating || 0 }}/5</span>
                </div>

                <!-- 공개여부 표시 -->
                <div class="visibility-display">
                  <span class="info-label">공개여부:</span>
                  <span class="visibility-status" :class="{ public: place.isPublic }">
                    {{ place.isPublic ? '공개' : '비공개' }}
                  </span>
                </div>

                <!-- 리뷰 표시 -->
                <div v-if="place.review" class="review-display">
                  <span class="info-label">리뷰:</span>
                  <div class="review-content">
                    <p>{{ place.review }}</p>
                  </div>
                </div>

                <!-- 액션 버튼들 -->
                <div class="action-buttons">
                  <!-- 리뷰가 있는 경우: 수정 버튼 -->
                  <button v-if="place.review" class="edit-btn" @click="editReview(idx, place)">
                    수정
                  </button>
                  <!-- 리뷰가 없는 경우: 리뷰 작성 버튼 -->
                  <button v-else class="write-review-btn" @click="editReview(idx, place)">
                    리뷰 작성
                  </button>
                </div>
              </div>

              <!-- 편집 모드 -->
              <div v-else class="edit-mode" :data-mode="place.review ? '리뷰 수정' : '리뷰 작성'">
                <!-- 평점 편집 -->
                <div class="rating-edit">
                  <div class="edit-label">평점:</div>
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
                  <div class="edit-label">공개여부:</div>
                  <label class="visibility-toggle">
                    <input type="checkbox" v-model="place.tempIsPublic" />
                    <span class="toggle-slider"></span>
                    <span class="toggle-label">{{ place.tempIsPublic ? '공개' : '비공개' }}</span>
                  </label>
                </div>

                <!-- 리뷰 편집 -->
                <div class="review-edit">
                  <div class="edit-label">리뷰:</div>
                  <textarea v-model="place.reviewText" class="review-input"
                    :placeholder="place.review ? $t('review_placeholder') : '이 장소에 대한 리뷰를 작성해주세요...'" rows="3" />
                </div>

                <!-- 편집 버튼들 -->
                <div class="edit-buttons">
                  <button class="save-btn" @click="submitReview(idx, place)">
                    {{ place.review ? '저장' : '리뷰 등록' }}
                  </button>
                  <button class="cancel-btn" @click="cancelEdit(idx, place)">
                    취소
                  </button>
                </div>
              </div>
            </div>
          </div>
          <button class="delete-btn" @click="deleteBookmark(idx, place)">🗑️</button>
        </div>
      </template>
      <template v-else>
        <div class="empty-state">
          <p>{{ $t('bookmark_empty') }}</p>
        </div>
      </template>
    </div>

    <!-- 관리자 버튼 (admin@gmail.com인 경우만 표시) -->
    <div class="section">
      <button class="delete-account-btn" @click="showDeleteAccountConfirm">
        {{ $t('delete_account_btn') }}
      </button>
    </div>

    <!-- 회원탈퇴 확인 모달 -->
    <div v-if="showDeleteConfirm" class="delete-confirm-modal">
      <div class="delete-confirm-content">
        <h3>{{ $t('delete_account_btn') }}</h3>
        <p>{{ $t('delete_account_confirm') }}</p>
        <div class="delete-confirm-buttons">
          <button class="cancel-btn" @click="cancelDeleteAccount">
            {{ $t('delete_account_cancel') }}
          </button>
          <button class="confirm-delete-btn" @click="confirmDeleteAccount">
            {{ $t('delete_account_btn') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="custom-modal">{{ modalMessage }}</div>
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
      showDeleteConfirm: false,
    };
  },
  async mounted() {
    const auth = getAuth();
    const user = auth.currentUser;
    if (!user) return;

    const res = await fetch('http://localhost:5000/api/get_user_bookmarks', {
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
    const reviewsRes = await fetch('http://localhost:5000/api/get_user_reviews', {
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
    goHome() {
      this.$router.push('/');
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
            const ratingResponse = await fetch('http://localhost:5000/api/update_bookmark_rating', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                uid: user.uid,
                contentId: place.contentId, // placeId를 contentId로 변경
                rating: place.tempRating
              })
            });

            const ratingResult = await ratingResponse.json();
            if (!ratingResult.success) {
              throw new Error(ratingResult.error || '평점 저장에 실패했습니다.');
            }
            place.rating = place.tempRating;
          }

          // 공개여부 업데이트
          if (place.tempIsPublic !== place.isPublic) {
            const visibilityResponse = await fetch('http://localhost:5000/api/update_bookmark_visibility', {
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
              throw new Error(visibilityResult.error || '공개여부 저장에 실패했습니다.');
            }
            place.isPublic = place.tempIsPublic;
          }
        }

        // 리뷰 저장 (리뷰가 있는 경우에만)
        if (place.reviewText && place.reviewText.trim()) {
          const response = await fetch('http://localhost:5000/api/save_review', {
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
              region: '부산', // 기본값으로 부산 설정 나중에는 가져올예정
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
            throw new Error(result.error || '서버에서 오류가 발생했습니다.');
          }
        }

        // 편집 모드 종료
        place.reviewText = '';
        place.isEditing = false;
        this.showModalMessage('저장되었습니다.');

      } catch (error) {
        console.error('저장 오류:', error);
        this.showModalMessage(`저장 중 오류가 발생했습니다: ${error.message}`);
      }
    },
    async deleteBookmark(idx, place) {
      const auth = getAuth();
      const user = auth.currentUser;
      if (!user) return;

      console.log('삭제할 북마크 정보:', place);
      console.log('전송할 placeId:', place.name);

      const response = await fetch('http://localhost:5000/api/delete_user_bookmark', {
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
        this.showModalMessage('북마크 삭제에 실패했습니다.');
      }
    },
    showModalMessage(msg) {
      this.modalMessage = msg;
      this.showModal = true;
      setTimeout(() => {
        this.showModal = false;
      }, 1500);
    },
    showDeleteAccountConfirm() {
      this.showDeleteConfirm = true;
    },
    cancelDeleteAccount() {
      this.showDeleteConfirm = false;
    },
    async confirmDeleteAccount() {
      const auth = getAuth();
      const user = auth.currentUser;
      if (!user) return;

      try {
        // 백엔드 API 호출하여 사용자 데이터 삭제
        await fetch('http://localhost:5000/api/delete_user_account', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: user.uid })
        });

        // Firebase Auth에서 사용자 삭제
        await user.delete();

        this.showDeleteConfirm = false;
        this.showModalMessage(this.$t('delete_account_success'));

        // 홈페이지로 리다이렉트
        setTimeout(() => {
          this.$router.push('/');
        }, 2000);

      } catch (error) {
        console.error('회원탈퇴 오류:', error);
        this.showModalMessage('회원탈퇴 중 오류가 발생했습니다.');
      }
    },
    setTempRating(place, rating) {
      place.tempRating = rating;
    },
  },
};
</script>

<style scoped>
.bookmark-container {
  width: 800px;
  margin: 60px auto;
  padding: 64px 80px 96px 80px;
  border-radius: 32px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 3rem;
  text-align: left;
  color: #1e293b;
}

.section {
  width: 100%;
  max-width: 480px;
  margin: 0 auto 3rem auto;
}

.bookmark-list {
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 3.5rem;
}

.bookmark-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.bookmark-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #10b981, #f59e0b);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.bookmark-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: #cbd5e1;
}

.bookmark-card:hover::before {
  opacity: 1;
}

.place-img {
  width: 140px;
  height: 140px;
  object-fit: cover;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.bookmark-card:hover .place-img {
  transform: scale(1.02);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.place-info {
  flex: 1;
  text-align: left;
  min-width: 0;
}

.place-name {
  font-size: 1.4rem;
  font-weight: 800;
  margin-bottom: 0.6rem;
  color: #1e293b;
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
  align-self: flex-start;
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

.delete-account-btn {
  width: 100%;
  padding: 1.2rem 0;
  background: #dc2626;
  color: #fff;
  font-size: 1.2rem;
  font-weight: 800;
  border: none;
  border-radius: 14px;
  box-shadow: 0 6px 24px rgba(220, 38, 38, 0.12);
  cursor: pointer;
  transition: all 0.2s;
}

.delete-account-btn:hover {
  background: #b91c1c;
  transform: translateY(-2px);
}

.delete-account-btn:active {
  background: #991b1b;
  transform: translateY(0);
}

.delete-confirm-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 4000;
}

.delete-confirm-content {
  background: #fff;
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.delete-confirm-content h3 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #dc2626;
  margin-bottom: 1rem;
}

.delete-confirm-content p {
  font-size: 1.1rem;
  color: #64748b;
  margin-bottom: 2rem;
  line-height: 1.6;
  white-space: pre-line;
}

.delete-confirm-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.confirm-delete-btn {
  padding: 1rem 2rem;
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-delete-btn:hover {
  background: #b91c1c;
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

@media (min-width: 600px) {
  .bookmark-container {
    max-width: 600px;
    margin: 40px auto;
    padding: 40px 32px 64px 32px;
    border-radius: 24px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  }
}

@media (min-width: 900px) {
  .bookmark-container {
    max-width: 800px;
    padding: 48px 64px 80px 64px;
  }
}
</style>