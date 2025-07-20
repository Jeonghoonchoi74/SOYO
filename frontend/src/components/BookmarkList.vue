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
              
              <!-- 리뷰 섹션 -->
              <div class="review-section">
                <div v-if="place.review && !place.isEditing" class="existing-review">
                  <p>{{ place.review }}</p>
                  <button class="edit-review-btn" @click="editReview(idx, place)">수정</button>
                </div>
                <div v-if="!place.review || place.isEditing" class="review-input-section">
                  <textarea 
                    v-model="place.reviewText" 
                    class="review-input-small" 
                    :placeholder="$t('review_placeholder')" 
                    rows="2"
                  />
                  <button 
                    class="review-submit-btn" 
                    :disabled="!place.reviewText || !place.reviewText.trim()" 
                    @click="submitReview(idx, place)"
                  >
                    {{ $t('review_submit') }}
                  </button>
                  <button
                    v-if="place.isEditing"
                    class="cancel-edit-btn"
                    @click="cancelEdit(idx, place)"
                  >
                    취소
                  </button>
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
        // 각 북마크에 reviewText 필드 추가
        this.bookmarked.forEach(place => {
          if (!place.reviewText) {
            place.reviewText = '';
          }
          place.isEditing = false;
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
        place.reviewText = place.review;
        place.isEditing = true;
      },
      cancelEdit(idx, place) {
        place.isEditing = false;
        place.reviewText = '';
      },
      async submitReview(idx, place) {
        const auth = getAuth();
        const user = auth.currentUser;
        if (!user || !place.reviewText.trim()) return;
        
        try {
          console.log('리뷰 저장 시도:', {
            uid: user.uid,
            placeId: place.name,
            placeName: place.name,
            placeDesc: place.desc,
            placeImage: place.image,
            review: place.reviewText.trim(),
            userName: user.displayName || user.email
          });
          
          const response = await fetch('http://localhost:5000/api/save_review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              uid: user.uid,
              placeId: place.name,
              placeName: place.name,
              placeDesc: place.desc,
              placeImage: place.image,
              review: place.reviewText.trim(),
              userName: user.displayName || user.email
            })
          });
          
          console.log('서버 응답 상태:', response.status);
          
          if (!response.ok) {
            const result = await response.json();
            throw new Error(result.error || `HTTP error! status: ${response.status}`);
          }
          
          const result = await response.json();
          console.log('서버 응답:', result);
          
          if (result.success) {
            // 북마크에 리뷰 추가
            place.review = place.reviewText.trim();
            place.reviewText = '';
            place.isEditing = false;
            this.showModalMessage(this.$t('review_success'));
          } else {
            throw new Error(result.error || '서버에서 오류가 발생했습니다.');
          }
        } catch (error) {
          console.error('리뷰 저장 오류:', error);
          this.showModalMessage(`리뷰 저장 중 오류가 발생했습니다: ${error.message}`);
        }
      },
      async deleteBookmark(idx, place) {
        const auth = getAuth();
        const user = auth.currentUser;
        if (!user) return;
        await fetch('http://localhost:5000/api/delete_user_bookmark', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: user.uid, placeId: place.name }) // place.name이 placeId 역할
        });
        this.bookmarked.splice(idx, 1);
        this.showModalMessage(this.$t('delete_bookmark_alert'));
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
  
  .header {
    text-align: left;
    margin-bottom: 2.5rem;
    width: 100%;
  }
  
  .title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 3rem;
    text-align: left;
    color: #1e293b;
  }
  
  .subtitle {
    font-size: 1rem;
    color: #64748b;
    margin-top: 0.5rem;
  }
  
  .section {
    width: 100%;
    max-width: 480px;
    margin: 0 auto 3rem auto;
  }
  
  .section-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #334155;
    margin-bottom: 1.5rem;
    border-left: 4px solid #3b82f6;
    padding-left: 0.8rem;
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
    background: #f1f5f9;
    border-radius: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    padding: 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
  }
  
  .bookmark-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border-color: #e2e8f0;
  }
  
  .place-img {
    width: 120px;
    height: 120px;
    object-fit: cover;
    border-radius: 16px;
  }
  
  .place-info {
    flex: 1;
    text-align: left;
  }
  
  .place-name {
    font-size: 1.3rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
    color: #1e293b;
    text-align: left;
  }
  
  .place-desc {
    font-size: 1.1rem;
    color: #334155;
    text-align: left;
    margin-bottom: 0.2rem;
  }
  
  .review-box {
    background-color: #f8fafc;
    border-radius: 12px;
    padding: 1rem;
  }
  
  .review-input {
    width: 100%;
    padding: 1.2rem 1.5rem;
    font-size: 1.2rem;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    margin-bottom: 1.2rem;
    background: #fff;
    box-sizing: border-box;
    resize: none;
    color: #1e293b;
  }
  .review-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .review-btn {
    width: 100%;
    padding: 1.2rem 0;
    background: #2563eb;
    color: #fff;
    font-size: 1.2rem;
    font-weight: 800;
    border: none;
    border-radius: 14px;
    box-shadow: 0 6px 24px rgba(37,99,235,0.12);
    cursor: pointer;
    transition: all 0.2s;
  }
  .review-btn:disabled {
    background-color: #94a3b8;
    cursor: not-allowed;
  }
  .review-btn:hover {
    background: #1d4ed8;
    transform: translateY(-2px);
  }
  .review-btn:active {
    background: #1e40af;
    transform: translateY(0);
  }
  
  .history-list {
    list-style: none;
    padding-left: 0;
    color: #475569;
    font-size: 0.98rem;
    border-left: 2px solid #e2e8f0;
  }
  
  .history-list li {
    padding: 0.6rem 1rem;
    transition: background-color 0.2s;
  }
  
  .history-list li:hover {
    background-color: #f8fafc;
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
    background: none;
    border: none;
    font-size: 1.6rem;
    cursor: pointer;
    margin-left: 1rem;
    color: #64748b;
    transition: color 0.2s;
  }
  .delete-btn:hover {
    color: #ef4444;
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

  .delete-account-btn {
    width: 100%;
    padding: 1.2rem 0;
    background: #dc2626;
    color: #fff;
    font-size: 1.2rem;
    font-weight: 800;
    border: none;
    border-radius: 14px;
    box-shadow: 0 6px 24px rgba(220,38,38,0.12);
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

  .cancel-btn {
    padding: 1rem 2rem;
    background: #f1f5f9;
    color: #64748b;
    border: none;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .cancel-btn:hover {
    background: #e2e8f0;
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
  .review-section {
    margin-top: 0.2rem;
    padding-top: 0.2rem;
  } */


  .existing-review p {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 0.5rem;
    line-height: 1.4;
    text-align: left;
  }

  .edit-review-btn {
    background: #3b82f6;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .edit-review-btn:hover {
    background: #2563eb;
  }

  .review-input-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .review-input-small {
    width: 100%;
    padding: 0.8rem;
    font-size: 0.9rem;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: #fff;
    box-sizing: border-box;
    resize: none;
    color: #1e293b;
  }

  .review-input-small:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }

  .review-submit-btn {
    background: #10b981;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    align-self: flex-start;
  }

  .review-submit-btn:disabled {
    background: #94a3b8;
    cursor: not-allowed;
  }

  .review-submit-btn:hover:not(:disabled) {
    background: #059669;
  }

  .management-btn {
    width: 100%;
    padding: 1.2rem 0;
    background: #7c3aed;
    color: #fff;
    font-size: 1.2rem;
    font-weight: 800;
    border: none;
    border-radius: 14px;
    box-shadow: 0 6px 24px rgba(124,58,237,0.12);
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .management-btn:hover {
    background: #6d28d9;
    transform: translateY(-2px);
  }
  
  .management-btn:active {
    background: #5b21b6;
    transform: translateY(0);
  }

  .cancel-edit-btn {
    background: #f1f5f9;
    color: #64748b;
    border: none;
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .cancel-edit-btn:hover {
    background: #e2e8f0;
  }

  @media (min-width: 600px) {
    .bookmark-container {
      max-width: 600px;
      margin: 40px auto;
      padding: 40px 32px 64px 32px;
      border-radius: 24px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }
  }
  @media (min-width: 900px) {
    .bookmark-container {
      max-width: 800px;
      padding: 48px 64px 80px 64px;
    }
  }
  </style>