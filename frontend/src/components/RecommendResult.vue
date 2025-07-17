<template>
    <div class="recommend-container">
      <button class="back-home-btn" @click="goHome">{{ $t('recommend_back_home') }}</button>
      <h2 class="title">{{ $t('recommend_title') }}</h2>
      <div class="card-list">
        <div v-for="(place, idx) in places" :key="idx" class="place-card">
          <div class="card-actions">
            <button class="action-btn">🗺️</button>
            <button class="action-btn" :class="{ active: place.bookmarked }" :disabled="bookmarkDisabled[idx]" @click="toggleBookmark(idx)">❤️</button>
            <button class="action-btn">🔈</button>
          </div>
          <img :src="place.image" class="place-img" :alt="$t('recommend_card_img_alt')" />
          <div class="place-info">
            <div class="place-name">{{ place.name }}</div>
            <div class="place-desc">{{ place.desc }}</div>
            <div class="place-review">
              <span class="review-badge">{{ $t('recommend_review_badge') }}</span>
              "{{ place.review }}"
            </div>
          </div>
        </div>
      </div>
      <button class="bookmark-list-btn" @click="goBookmark">{{ $t('recommend_bookmark_btn') }}</button>
      <div v-if="showModal" class="custom-modal">{{ modalMessage }}</div>
    </div>
  </template>
  
  <script>
  import { i18nState, $t } from '../i18n';
  import { getAuth } from 'firebase/auth';
  export default {
    name: 'RecommendResult',
    data() {
      return {
        bookmarkArr: [false, false], // 초기값을 모두 false로 설정
        showModal: false,
        modalMessage: '',
        bookmarkDisabled: [],
      };
    },
    computed: {
      $t() { return $t; },
      places() {
        return [
          {
            image: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80',
            name: this.$t('place_jinmi'),
            desc: this.$t('place_jinmi_desc'),
            review: this.$t('place_jinmi_review'),
            bookmarked: this.bookmarkArr[0],
          },
          {
            image: 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80',
            name: this.$t('place_haeundae'),
            desc: this.$t('place_haeundae_desc'),
            review: this.$t('place_haeundae_review'),
            bookmarked: this.bookmarkArr[1],
          },
        ];
      },
    },
    async mounted() {
      this.bookmarkDisabled = Array(this.places.length).fill(false);
      await this.loadUserBookmarks();
    },
    methods: {
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
              this.bookmarkArr[idx] = bookmarkedPlaces.includes(place.name);
            });
          }
        } catch (error) {
          console.error('북마크 로드 오류:', error);
        }
      },
      async toggleBookmark(idx) {
        if (this.bookmarkDisabled[idx]) return;
        this.bookmarkDisabled[idx] = true;
        const wasBookmarked = this.bookmarkArr[idx];
        this.bookmarkArr[idx] = !this.bookmarkArr[idx];
        const isNowBookmarked = this.bookmarkArr[idx];
        const result = await this.saveBookmark(idx, isNowBookmarked);
        if (result && result.success) {
          if (isNowBookmarked) {
            this.showModalMessage(this.$t('add_bookmark_alert'));
          } else {
            this.showModalMessage(this.$t('delete_bookmark_alert'));
          }
        } else {
          // 실패 시 롤백
          this.bookmarkArr[idx] = wasBookmarked;
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
            // 북마크 추가
            const params = {
              uid: user.uid,
              placeId: this.places[idx].name,
              bookmark: value,
              name: this.places[idx].name,
              desc: this.places[idx].desc,
              image: this.places[idx].image,
            };
            console.log('북마크 추가 요청 파라미터:', params);
            const res = await fetch('http://localhost:5000/api/save_bookmark', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(params),
            });
            console.log('북마크 응답 status:', res.status);
            const result = await res.json();
            console.log('북마크 응답 결과:', result);
            return result;
          } else {
            // 북마크 삭제
            const params = {
              uid: user.uid,
              placeId: this.places[idx].name,
            };
            console.log('북마크 삭제 요청 파라미터:', params);
            const res = await fetch('http://localhost:5000/api/delete_user_bookmark', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(params),
            });
            console.log('북마크 삭제 응답 status:', res.status);
            const result = await res.json();
            console.log('북마크 삭제 응답 결과:', result);
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
  .title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 3rem;
    text-align: center;
    color: #1e293b;
  }
  .card-list {
    width: 100%;
    max-width: 900px;
    display: flex;
    flex-direction: column;
    gap: 2.2rem;
    margin-bottom: 3.5rem;
  }
  .place-card {
    background: #f1f5f9;
    border-radius: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
  .place-img {
    width: 100%;
    height: 260px;
    object-fit: cover;
    border-radius: 16px;
    margin-bottom: 1.5rem;
  }
  .place-info {
    margin-bottom: 1rem;
  }
  .place-name {
    font-size: 1.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    color: #1e293b;
  }
  .place-desc {
    font-size: 1.15rem;
    color: #334155;
    margin-bottom: 0.3rem;
  }
  .place-review {
    font-size: 1.05rem;
    color: #64748b;
  }
  .card-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
  }
  .card-actions button {
    border: none;
    background: #e2e8f0;
    border-radius: 10px;
    padding: 0.7rem 1.2rem;
    font-size: 1.3rem;
    cursor: pointer;
    transition: background 0.2s;
  }
  .card-actions .like-btn.active,
  .card-actions .save-btn.active {
    background: #2563eb;
    color: #fff;
  }
  .subtitle {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #1e293b;
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
  </style>