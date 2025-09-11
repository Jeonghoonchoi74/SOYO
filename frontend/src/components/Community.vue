<template>
  <div class="community-page">
    <!-- 헤더 -->
    <div class="header-nav">
      <h1 class="page-title">{{ $t('community_title') }}</h1>
    </div>

    <!-- 지역 선택 스크롤 -->
    <div class="region-scroll">
      <div class="region-list">
        <button v-for="region in regions" :key="region" class="region-item"
          :class="{ active: selectedRegion === region }" @click="selectRegion(region)">
          {{ region }}
        </button>
      </div>
    </div>

    <!-- 메인 컨텐츠 -->
    <div class="main-content">
      <!-- 리뷰 목록 -->
      <div class="review-list">
        <!-- 로딩 상태 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>{{ $t('community_loading_reviews') }}</p>
        </div>
        
        <div v-else-if="filteredReviews.length > 0">
          <div v-for="review in filteredReviews" :key="review.id" class="review-item fade-in">
            <div class="review-content">
              <div class="review-image" v-if="review.placeImage">
                <img :src="review.placeImage" :alt="review.placeName" />
              </div>
              <div class="review-text">
                <div class="place-title">{{ review.placeName }}</div>
                <div class="review-description">{{ review.review }}</div>
              </div>
            </div>

            <div class="review-meta">
              <div class="author-info">
                <span class="author">{{ review.userName }}</span>
                <span class="time">{{ formatTimeAgo(review.createdAt) }}</span>
              </div>
              <div class="rating">
                <span class="star">★</span>
                <span>{{ review.rating || 0 }}</span>
              </div>
            </div>

            <div class="review-actions">
              <button class="action-btn" :class="{ active: review.isLiked }" @click="toggleLike(review)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path
                    d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                </svg>
                {{ $t('community_empathy') }} {{ review.likes || 0 }}
              </button>
              <button class="action-btn" @click="toggleComments(review)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                {{ $t('community_comments') }} {{ review.comments ? review.comments.length : 0 }}
              </button>
              <!-- 본인 리뷰인 경우에만 삭제 버튼 표시 -->
              <button v-if="review.uid === currentUser.uid" class="action-btn delete-btn" @click="deleteReview(review)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                </svg>
                {{ $t('community_delete') }}
              </button>
            </div>

            <!-- 댓글 섹션 -->
            <div v-if="review.showComments" class="comments-section">
              <div v-if="review.comments && review.comments.length > 0" class="comments-list">
                <div v-for="comment in review.comments" :key="comment.id" class="comment-item">
                  <div class="comment-content">
                    <strong>{{ comment.userName }}</strong>
                    <span>{{ comment.text }}</span>
                    <span class="comment-time">{{ formatTimeAgo(comment.createdAt) }}</span>
                  </div>
                  <button v-if="comment.uid === currentUser.uid" class="delete-comment-btn"
                    @click="deleteComment(review, comment)" :title="$t('community_comment_delete')">
                    ×
                  </button>
                </div>
              </div>

              <div class="comment-input">
                <textarea v-model="review.newComment" :placeholder="$t('community_comment_placeholder')" rows="2" />
                <button class="comment-submit" @click="submitComment(review)"
                  :disabled="!review.newComment || !review.newComment.trim()">
                  {{ $t('community_register') }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">📝</div>
          <p>{{ $t('community_no_reviews') }}</p>
          <p class="empty-subtitle">{{ $t('community_first_review') }}</p>
        </div>
      </div>
    </div>

    <!-- 플로팅 뒤로가기 버튼 -->
    <button class="floating-back-btn" @click="goBack">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
    </button>

    <!-- 플로팅 작성 버튼 -->
    <button class="floating-btn" @click="toggleWriteMode">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
      </svg>
    </button>

    <!-- 작성 모달 -->
    <div v-if="showWriteModal" class="write-modal-overlay" @click="closeWriteModal">
      <div class="write-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('community_write_review') }}</h3>
          <button class="close-btn" @click="closeWriteModal">×</button>
        </div>

        <div class="modal-body">
          <div v-if="availablePlaces.length > 0" class="place-selector">
            <label>{{ $t('community_place_select') }}</label>
            <select v-model="selectedPlace" class="place-select">
              <option value="">{{ $t('community_place_select_placeholder') }}</option>
              <option v-for="place in availablePlaces" :key="place.name" :value="place">
                {{ place.name }}
              </option>
            </select>
          </div>

          <div v-else class="no-places-message">
            <p>{{ $t('community_no_places') }}</p>
            <p>{{ $t('community_add_bookmark_first') }}</p>
          </div>

          <div v-if="selectedPlace" class="review-form">
            <div class="rating-input">
              <label>{{ $t('community_rating') }}</label>
              <div class="star-input">
                <button v-for="star in 5" :key="star" class="star-btn" :class="{ active: star <= newReview.rating }"
                  @click="setNewRating(star)">
                  ★
                </button>
              </div>
            </div>

            <div class="visibility-input">
              <label>
                <input type="checkbox" v-model="newReview.isPublic" />
                {{ $t('community_public') }}
              </label>
            </div>

            <div class="text-input">
              <label>{{ $t('community_review_content') }}</label>
              <textarea v-model="newReview.text" :placeholder="$t('community_review_placeholder')" rows="4" />
            </div>

            <div class="modal-actions">
              <button class="cancel-btn" @click="cancelNewReview">{{ $t('community_cancel') }}</button>
              <button class="submit-btn" @click="submitNewReview" :disabled="!newReview.text.trim()">
                {{ $t('community_submit') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 토스트 메시지 -->
    <div v-if="showModal" class="toast">{{ modalMessage }}</div>
  </div>
</template>

<script>
import { i18nState, $t } from '../i18n';
import { getAuth } from 'firebase/auth';
import { getRegionOptions, getDisplayName } from '../utils/regionMapping';

export default {
  name: 'Community',
  data() {
    return {
      publicReviews: [],
      availablePlaces: [],
      selectedPlace: '',
      newReview: {
        rating: 0,
        isPublic: true,
        text: ''
      },
      showModal: false,
      modalMessage: '',
      currentUser: null,
      showWriteModal: false,
      showPlaceDropdown: false,
      regions: [],
      selectedRegion: '',
      isLoading: false,
      streamingDelay: 300, // 스트리밍 지연 시간 (ms)

      sortBy: 'recent'
    };
  },
  computed: {
    filteredReviews() {
      let filtered = this.publicReviews;

      // 지역 필터링 ('전국'이 선택되면 모든 리뷰 표시)
      if (this.selectedRegion && this.selectedRegion !== this.$t('region_nationwide')) {
        filtered = filtered.filter(review =>
          review.region === this.selectedRegion
        );
      }

      // 정렬
      if (this.sortBy === 'rating') {
        return filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      } else {
        return filtered.sort((a, b) => {
          const dateA = new Date(a.createdAt?.seconds * 1000 || 0);
          const dateB = new Date(b.createdAt?.seconds * 1000 || 0);
          return dateB - dateA;
        });
      }
    }
  },
  async mounted() {
    const auth = getAuth();
    this.currentUser = auth.currentUser;
    if (!this.currentUser) {
      this.$router.push('/main');
      return;
    }

    await this.loadPublicReviews();
    await this.loadAvailablePlaces();
    await this.loadRegions();

    // 외부 클릭 시 드롭다운 닫기
    document.addEventListener('click', this.handleOutsideClick);
  },

  beforeUnmount() {
    document.removeEventListener('click', this.handleOutsideClick);
  },
  methods: {
    $t,
    goBack() {
      this.$router.push('/main');
    },

    toggleWriteMode() {
      this.showWriteModal = true;
    },

    closeWriteModal() {
      this.showWriteModal = false;
      this.showPlaceDropdown = false;
      this.cancelNewReview();
    },

    selectPlace(place) {
      this.selectedPlace = place;
      this.showPlaceDropdown = false;

      // 장소 선택 시 지역 정보 확인
      let region = place.region;

      // region이 없으면 장소 설명에서 추출
      if (!region && place.desc) {
        const desc = place.desc;
        if (desc.includes('부산')) region = '부산';
        else if (desc.includes('서울')) region = '서울';
        else if (desc.includes('대구')) region = '대구';
        else if (desc.includes('인천')) region = '인천';
        else if (desc.includes('광주')) region = '광주';
        else if (desc.includes('대전')) region = '대전';
        else if (desc.includes('울산')) region = '울산';
        else if (desc.includes('세종')) region = '세종';
        else if (desc.includes('경기')) region = '경기';
        else if (desc.includes('강원')) region = '강원';
        else if (desc.includes('충북')) region = '충북';
        else if (desc.includes('충남')) region = '충남';
        else if (desc.includes('전북')) region = '전북';
        else if (desc.includes('전남')) region = '전남';
        else if (desc.includes('경북')) region = '경북';
        else if (desc.includes('경남')) region = '경남';
        else if (desc.includes('제주')) region = '제주';
        else region = this.$t('region_nationwide');
      }

      // console.log('선택된 장소:', place);
      // console.log('저장될 지역:', region);
    },

    async loadPublicReviews() {
      try {
        this.isLoading = true;
        this.publicReviews = []; // 기존 리뷰 초기화
        
        const response = await fetch('/api/get_public_reviews');
        const result = await response.json();

        if (result.success && result.reviews.length > 0) {
          // 리뷰를 하나씩 스트리밍으로 표시 (비동기로 실행)
          this.streamReviews(result.reviews);
        }
      } catch (error) {
        console.error('공개 리뷰 로드 오류:', error);
        this.showModalMessage(this.$t('community_public_review_error'));
      } finally {
        this.isLoading = false;
      }
    },

    streamReviews(reviews) {
      reviews.forEach((review, index) => {
        // 각 리뷰를 지연 시간 후에 표시
        setTimeout(() => {
          const reviewItem = {
            ...review,
            showComments: false,
            newComment: '',
            isLiked: false,
            likes: 0,
            comments: []
          };
          
          this.publicReviews.push(reviewItem);
          
          // 백그라운드에서 좋아요 정보 로드
          this.loadReviewLikes(reviewItem);
        }, index * this.streamingDelay);
      });
    },

    async loadReviewLikes(review) {
      try {
        const likesResponse = await fetch(`/api/get_review_likes/${review.contentId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: this.currentUser.uid })
        });

        const likesResult = await likesResponse.json();
        if (likesResult.success) {
          review.likes = likesResult.likes;
          review.isLiked = likesResult.userLiked;
        }
      } catch (error) {
        console.error(`리뷰 ${review.contentId} 좋아요 로드 오류:`, error);
      }
    },

    async loadAvailablePlaces() {
      try {
        // Backend API를 통해 북마크와 리뷰 정보 가져오기
        const [bookmarksRes, reviewsRes] = await Promise.all([
          fetch('/api/get_user_bookmarks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid: this.currentUser.uid })
          }),
          fetch('/api/get_user_reviews', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid: this.currentUser.uid })
          })
        ]);

        const bookmarksResult = await bookmarksRes.json();
        const reviewsResult = await reviewsRes.json();

        if (bookmarksResult.success && reviewsResult.success) {
          const bookmarks = bookmarksResult.bookmarks || [];
          const reviews = reviewsResult.reviews || [];

          // 리뷰된 장소 이름들 Set으로 변환
          const reviewedPlaces = new Set(reviews.map(review => review.placeName));

          // 리뷰가 없는 북마크만 필터링
          this.availablePlaces = bookmarks.filter(bookmark =>
            !reviewedPlaces.has(bookmark.name)
          );

          console.log('Firebase에서 직접 가져온 북마크:', bookmarks);
          console.log('사용자가 작성한 리뷰들:', reviews);
          console.log('리뷰된 장소 이름들:', Array.from(reviewedPlaces));
          console.log('리뷰 작성 가능한 장소:', this.availablePlaces);
        }
      } catch (error) {
        console.error('사용 가능한 장소 로드 오류:', error);
      }
    },


    async loadReviewInteractions(review) {
      try {
        const likesResponse = await fetch(`/api/get_review_likes/${review.contentId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: this.currentUser.uid })
        });
        const likesResult = await likesResponse.json();
        if (likesResult.success) {
          review.likes = likesResult.likes;
          review.isLiked = likesResult.userLiked;
        }

        const commentsResponse = await fetch(`/api/get_review_comments/${review.contentId}`);
        const commentsResult = await commentsResponse.json();
        if (commentsResult.success) {
          review.comments = commentsResult.comments;
        }
      } catch (error) {
        console.error('리뷰 상호작용 로드 오류:', error);
      }
    },

    setNewRating(rating) {
      this.newReview.rating = rating;
    },

    async submitNewReview() {
      if (!this.selectedPlace || !this.newReview.text.trim()) {
        this.showModalMessage(this.$t('community_place_and_content_required'));
        return;
      }

      // 사용자 선호도에서 region 우선 가져오기
      let region = this.$t('region_nationwide'); // 기본값
      try {
        const preferencesResponse = await fetch('/api/get_user_preferences', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: this.currentUser.uid })
        });
        
        const preferencesResult = await preferencesResponse.json();
        if (preferencesResult.success && preferencesResult.preferences && preferencesResult.preferences.region) {
          region = preferencesResult.preferences.region;
        }
      } catch (error) {
        console.warn(this.$t('community_user_preference_error'), error);
        
        // 사용자 선호도가 없으면 장소 정보에서 region 사용
        region = this.selectedPlace.region;
        
        // region이 없으면 장소 설명에서 추출 (regionMapping.js 매핑에 맞게 수정)
        if (!region && this.selectedPlace.desc) {
          const desc = this.selectedPlace.desc;
          if (desc.includes('부산')) region = '부산';
          else if (desc.includes('서울')) region = '서울';
          else if (desc.includes('대구')) region = '대구';
          else if (desc.includes('인천')) region = '인천';
          else if (desc.includes('광주')) region = '광주';
          else if (desc.includes('대전')) region = '대전';
          else if (desc.includes('울산')) region = '울산';
          else if (desc.includes('세종')) region = '세종특별자치시';
          else if (desc.includes('경기')) region = '경기도';
          else if (desc.includes('강원')) region = '강원특별자치도';
          else if (desc.includes('충북')) region = '충청북도';
          else if (desc.includes('충남')) region = '충청남도';
          else if (desc.includes('전북')) region = '전북특별자치도';
          else if (desc.includes('전남')) region = '전라남도';
          else if (desc.includes('경북')) region = '경상북도';
          else if (desc.includes('경남')) region = '경상남도';
          else if (desc.includes('제주')) region = '제주도';
          else region = this.$t('region_nationwide');
        }
      }

      console.log('선택된 장소:', this.selectedPlace);
      console.log('사용할 지역:', region);

      try {
        const response = await fetch('/api/save_review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            uid: this.currentUser.uid,
            contentId: this.selectedPlace.contentId, // placeId를 contentId로 변경
            placeName: this.selectedPlace.name,
            placeDesc: this.selectedPlace.desc,
            placeImage: this.selectedPlace.image,
            review: this.newReview.text.trim(),
            rating: this.newReview.rating,
            isPublic: this.newReview.isPublic,
            region: region,
            userName: this.currentUser.displayName || this.currentUser.email
          })
        });

        const result = await response.json();
        if (result.success) {
          this.showModalMessage(this.$t('community_review_success'));
          this.closeWriteModal();
          await this.loadPublicReviews();
          await this.loadAvailablePlaces();
        } else {
          throw new Error(result.error || this.$t('community_review_failed'));
        }
      } catch (error) {
        console.error('리뷰 등록 오류:', error);
        this.showModalMessage(this.$t('community_review_error'));
      }
    },

    cancelNewReview() {
      this.selectedPlace = '';
      this.newReview = {
        rating: 0,
        isPublic: true,
        text: ''
      };
    },

    async toggleLike(review) {
      try {
        // console.log('좋아요 토글 - 리뷰 데이터:', review);
        const requestData = {
          contentId: review.contentId, // placeId를 contentId로 변경
          uid: this.currentUser.uid,
          userName: this.currentUser.displayName || this.currentUser.email
        };
        // console.log('좋아요 토글 - 전송 데이터:', requestData);

        const response = await fetch('/api/toggle_review_like', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData)
        });

        const result = await response.json();
        if (result.success) {
          review.isLiked = result.isLiked;
          review.likes = result.totalLikes;
        }
      } catch (error) {
        console.error('좋아요 토글 오류:', error);
        this.showModalMessage(this.$t('community_like_error'));
      }
    },

    async toggleComments(review) {
      review.showComments = !review.showComments;
      
      // 댓글 섹션이 열릴 때만 댓글 로드 (지연 로딩)
      if (review.showComments && (!review.comments || review.comments.length === 0)) {
        try {
          const commentsResponse = await fetch(`/api/get_review_comments/${review.contentId}`);
          const commentsResult = await commentsResponse.json();
          if (commentsResult.success) {
            review.comments = commentsResult.comments;
          }
        } catch (error) {
          console.error('댓글 로드 오류:', error);
        }
      }
    },

    async submitComment(review) {
      if (!review.newComment || !review.newComment.trim()) {
        return;
      }

      try {
        // console.log('댓글 추가 - 리뷰 데이터:', review);
        const requestData = {
          contentId: review.contentId, // placeId를 contentId로 변경
          uid: this.currentUser.uid,
          userName: this.currentUser.displayName || this.currentUser.email,
          comment: review.newComment.trim()
        };
        // console.log('댓글 추가 - 전송 데이터:', requestData);

        const response = await fetch('/api/add_review_comment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData)
        });

        const result = await response.json();
        if (result.success) {
          review.comments = review.comments || [];
          review.comments.push(result.comment);
          review.newComment = '';
          this.showModalMessage(this.$t('community_comment_success'));
        }
      } catch (error) {
        console.error('댓글 등록 오류:', error);
        this.showModalMessage(this.$t('community_comment_error'));
      }
    },

    formatDate(timestamp) {
      if (!timestamp) return '';
      const date = new Date(timestamp.seconds * 1000);
      return date.toLocaleDateString('ko-KR') + ' ' + date.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    formatTimeAgo(timestamp) {
      if (!timestamp) return this.$t('community_just_now');

      let date;
      if (timestamp.seconds) {
        // Firestore Timestamp 객체
        date = new Date(timestamp.seconds * 1000);
      } else if (timestamp.toDate) {
        // Firestore Timestamp 객체의 toDate() 메서드
        date = timestamp.toDate();
      } else if (timestamp instanceof Date) {
        // Date 객체
        date = timestamp;
      } else {
        // 문자열이나 숫자
        date = new Date(timestamp);
      }

      // 유효하지 않은 날짜인 경우
      if (isNaN(date.getTime())) {
        return this.$t('community_just_now');
      }

      const now = new Date();
      const diffInMinutes = Math.floor((now - date) / (1000 * 60));

      if (diffInMinutes < 1) return this.$t('community_just_now');
      if (diffInMinutes < 60) return `${diffInMinutes}${this.$t('community_minutes_ago')}`;

      const diffInHours = Math.floor(diffInMinutes / 60);
      if (diffInHours < 24) return `${diffInHours}${this.$t('community_hours_ago')}`;

      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays < 7) return `${diffInDays}${this.$t('community_days_ago')}`;

      const diffInWeeks = Math.floor(diffInDays / 7);
      if (diffInWeeks < 4) return `${diffInWeeks}${this.$t('community_weeks_ago')}`;

      const diffInMonths = Math.floor(diffInDays / 30);
      if (diffInMonths < 12) return `${diffInMonths}${this.$t('community_months_ago')}`;

      return date.toLocaleDateString('ko-KR');
    },

    showModalMessage(msg) {
      this.modalMessage = msg;
      this.showModal = true;
      setTimeout(() => {
        this.showModal = false;
      }, 2000);
    },

    async deleteComment(review, comment) {
      if (!confirm(this.$t('community_comment_delete_confirm'))) {
        return;
      }

      try {
        const requestData = {
          contentId: review.placeId || review.contentId,  // placeId 또는 contentId 사용
          commentId: comment.id,
          uid: this.currentUser.uid
        };
        
        // console.log('댓글 삭제 - 리뷰 데이터:', review);
        // console.log('댓글 삭제 - 댓글 데이터:', comment);
        // console.log('댓글 삭제 - 전송 데이터:', requestData);

        const response = await fetch('/api/delete_review_comment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData)
        });

        const result = await response.json();
        if (result.success) {
          // 댓글 목록에서 삭제된 댓글 제거
          const commentIndex = review.comments.findIndex(c => c.id === comment.id);
          if (commentIndex > -1) {
            review.comments.splice(commentIndex, 1);
          }
          this.showModalMessage(this.$t('community_comment_delete_success'));
        } else {
          throw new Error(result.error || this.$t('community_comment_delete_failed'));
        }
      } catch (error) {
        console.error('댓글 삭제 오류:', error);
        this.showModalMessage(this.$t('community_comment_delete_error'));
      }
    },

    async loadRegions() {
      try {
        // regionMapping.js에서 지역 목록 가져오기
        const regionOptions = getRegionOptions();
        this.regions = regionOptions.map(option => this.$t(getDisplayName(option.value)));
        this.selectedRegion = this.$t('region_nationwide');
      } catch (error) {
        console.error(this.$t('community_region_load_error'), error);
        // 오류 시 기본 지역 목록 사용
        this.regions = [this.$t('region_nationwide'), this.$t('region_seoul'), this.$t('region_busan'), this.$t('region_daegu'), this.$t('region_incheon'), this.$t('region_gwangju'), this.$t('region_daejeon'), this.$t('region_ulsan'), this.$t('region_sejong'), this.$t('region_gyeonggi'), this.$t('region_gangwon'), this.$t('region_chungbuk'), this.$t('region_chungnam'), this.$t('region_jeonbuk'), this.$t('region_jeonnam'), this.$t('region_gyeongbuk'), this.$t('region_gyeongnam'), this.$t('region_jeju')];
        this.selectedRegion = this.$t('region_nationwide');
      }
    },

    selectRegion(region) {
      this.selectedRegion = region;
    },

    setSortBy(sortType) {
      this.sortBy = sortType;
    },

    async deleteReview(review) {
      if (!confirm(this.$t('community_review_delete_confirm'))) {
        return;
      }

      try {
        const response = await fetch('/api/delete_review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            uid: this.currentUser.uid,
            contentId: review.contentId
          })
        });

        const result = await response.json();
        if (result.success) {
          this.showModalMessage(this.$t('community_review_delete_success'));
          // 리뷰 목록 새로고침
          await this.loadPublicReviews();
          // 사용 가능한 장소 목록도 새로고침 (삭제된 리뷰가 다시 작성 가능해짐)
          await this.loadAvailablePlaces();
        } else {
          throw new Error(result.error || this.$t('community_review_delete_failed'));
        }
      } catch (error) {
        console.error('리뷰 삭제 오류:', error);
        this.showModalMessage(this.$t('community_review_delete_error'));
      }
    }
  }
};
</script>
<style scoped>
/* 모던 세련된 스타일 */
.community-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  position: relative;
}

.community-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(74, 105, 226, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(59, 91, 199, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}





/* 지역 선택 스크롤 */
.region-scroll {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 16px 0;
  width: 100vw;
  max-width: 100vw;
  box-sizing: border-box;
  position: relative;
  z-index: 10;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.region-list {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 0 16px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.region-list::-webkit-scrollbar {
  display: none;
}

.region-item {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(74, 105, 226, 0.2);
  border-radius: 25px;
  padding: 10px 20px;
  font-size: 14px;
  color: #6c757d;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.region-item:hover {
  background: rgba(74, 105, 226, 0.1);
  color: #4A69E2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 105, 226, 0.15);
}

.region-item.active {
  background: linear-gradient(135deg, #4A69E2 0%, #3B5BC7 100%);
  color: white;
  font-weight: 600;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 105, 226, 0.3);
}







/* 헤더 네비게이션 */
.header-nav {
  background: linear-gradient(135deg, #4A69E2 0%, #3B5BC7 100%);
  border-bottom: none;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100vw;
  max-width: 100vw;
  margin: 0;
  padding: 20px 12px;
  box-sizing: border-box;
  position: relative;
  z-index: 10;
  box-shadow: 0 4px 20px rgba(74, 105, 226, 0.15);
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: -0.5px;
}

/* 플로팅 뒤로가기 버튼 */
.floating-back-btn {
  position: fixed;
  bottom: 30px;
  left: 20px;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #4A69E2 0%, #3B5BC7 100%);
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(74, 105, 226, 0.3);
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.floating-back-btn:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 12px 32px rgba(74, 105, 226, 0.4);
}

.floating-back-btn:active {
  transform: translateY(-2px) scale(1.02);
}

/* 메인 컨텐츠 */
.main-content {
  width: 100vw;
  max-width: 100vw;
  margin: 0;
  padding: 0 12px;
  box-sizing: border-box;
}

/* 리뷰 목록 */
.review-list {
  margin-top: 8px;
}

.review-item {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin-bottom: 12px;
  padding: 20px;
  border-radius: 16px;
  width: 100%;
  box-sizing: border-box;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.review-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.fade-in {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}



.review-content {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.review-image {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
}

.review-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.review-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.place-title {
  font-weight: 600;
  color: #4A69E2;
  font-size: 16px;
  line-height: 1.4;
}

.review-description {
  line-height: 1.5;
  color: #495057;
  font-size: 14px;
}

.review-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
  color: #6c757d;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author {
  font-weight: 500;
  color: #495057;
}

.time {
  color: #adb5bd;
}

.rating {
  display: flex;
  align-items: center;
  gap: 2px;
  font-weight: 500;
}

.star {
  color: #ffc107;
}

.review-actions {
  display: flex;
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(74, 105, 226, 0.2);
  border-radius: 25px;
  padding: 8px 16px;
  font-size: 13px;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.action-btn:hover {
  background: rgba(74, 105, 226, 0.1);
  color: #4A69E2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 105, 226, 0.15);
}

.action-btn.active {
  background: linear-gradient(135deg, #4A69E2 0%, #3B5BC7 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 16px rgba(74, 105, 226, 0.3);
}

.action-btn.delete-btn {
  color: #dc3545;
  border-color: rgba(220, 53, 69, 0.3);
  background: rgba(220, 53, 69, 0.05);
}

.action-btn.delete-btn:hover {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

/* 댓글 섹션 */
.comments-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f3f4;
}

.comments-list {
  margin-bottom: 12px;
}

.comment-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 8px 0;
  font-size: 14px;
  line-height: 1.4;
  color: #495057;
}

.comment-content {
  flex: 1;
}

.comment-content strong {
  color: #212529;
  margin-right: 8px;
}

.delete-comment-btn {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
  margin-left: 8px;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.delete-comment-btn:hover {
  background: #dc3545;
  color: white;
}

.comment-time {
  color: #adb5bd;
  font-size: 12px;
  margin-left: 8px;
}

.comment-input {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.comment-input textarea {
  flex: 1;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.comment-input textarea:focus {
  outline: none;
  border-color: #4A69E2;
}

.comment-submit {
  background: #4A69E2;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}

.comment-submit:disabled {
  background: #adb5bd;
  cursor: not-allowed;
}

/* 플로팅 버튼 */
.floating-btn {
  position: fixed;
  bottom: 30px;
  right: 20px;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #4A69E2 0%, #3B5BC7 100%);
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(74, 105, 226, 0.3);
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.floating-btn:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 12px 32px rgba(74, 105, 226, 0.4);
}

.floating-btn:active {
  transform: translateY(-2px) scale(1.02);
}

/* 작성 모달 */
.write-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 20px;
  color: #212529;
}

.write-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  overflow-y: auto;
  color: #212529;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 3001;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 20px 24px;
  border-bottom: 1px solid #f1f3f4;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #212529;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #adb5bd;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 20px 24px 24px 24px;
}

.place-selector {
  margin-bottom: 16px;
}

.place-selector label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #212529;
}

.place-select {
  width: 100%;
  padding: 14px;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  font-size: 14px;
  background: #f8f9fa;
  color: #212529;
  transition: all 0.2s ease;
}

.place-select:focus {
  outline: none;
  border-color: #ff6b35;
  background: white;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.review-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rating-input label,
.visibility-input label,
.text-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #212529;
}

.star-input {
  display: flex;
  gap: 4px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #e9ecef;
  cursor: pointer;
  transition: color 0.2s;
}

.star-btn.active,
.star-btn:hover {
  color: #ffc107;
}

.visibility-input label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #212529;
}

.text-input textarea {
  width: 100%;
  padding: 14px;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  line-height: 1.6;
  color: #212529;
  background: #f8f9fa;
  transition: all 0.2s ease;
  min-height: 100px;
  max-height: 200px;
  box-sizing: border-box;
}

.text-input textarea:focus {
  outline: none;
  border-color: #ff6b35;
  background: white;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}



.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn,
.submit-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: none;
}

.cancel-btn {
  background: #f8f9fa;
  color: #495057;
}

.submit-btn {
  background: #4A69E2;
  color: white;
}

.submit-btn:disabled {
  background: #adb5bd;
  cursor: not-allowed;
}

/* 로딩 상태 */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4A69E2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-subtitle {
  font-size: 14px;
  color: #adb5bd;
  margin-top: 8px;
}

.no-places-message {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.no-places-message p {
  margin: 8px 0;
  font-size: 14px;
}

/* 토스트 */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 4000;
  animation: fadeInOut 2s;
}

@keyframes fadeInOut {

  0%,
  100% {
    opacity: 0;
  }

  10%,
  90% {
    opacity: 1;
  }
}

/* 반응형 */
@media (max-width: 768px) {
  .main-content {
    padding: 0 8px;
    width: 100vw;
    max-width: 100vw;
  }

  .review-item {
    margin-bottom: 4px;
    padding: 12px;
    width: 100%;
    box-sizing: border-box;
  }

  .review-content {
    gap: 8px;
  }

  .review-image {
    width: 60px;
    height: 60px;
  }

  .place-title {
    font-size: 15px;
  }

  .review-description {
    font-size: 13px;
  }

  /* 모바일에서 리뷰 작성 모달을 더 크게 */
  .write-modal-overlay {
    padding: 8px;
    align-items: flex-start;
    padding-top: 20px;
  }

  .write-modal {
    max-width: 100%;
    width: calc(100% - 16px);
    max-height: calc(100vh - 40px);
    border-radius: 12px;
    margin: 0;
  }

  .modal-header {
    padding: 20px 20px 16px 20px;
  }

  .modal-header h3 {
    font-size: 20px;
  }

  .modal-body {
    padding: 16px 20px 20px 20px;
  }

  .place-selector label,
  .rating-input label,
  .text-input label {
    font-size: 16px;
    margin-bottom: 10px;
  }

  .place-select {
    padding: 16px;
    font-size: 16px;
    border-radius: 12px;
  }

  .star-btn {
    font-size: 28px;
    padding: 4px;
    margin: 0 2px;
  }

  .visibility-input label {
    font-size: 16px;
  }

  .text-input textarea {
    padding: 16px;
    font-size: 16px;
    border-radius: 12px;
    min-height: 120px;
    line-height: 1.6;
  }

  .modal-actions {
    gap: 16px;
    margin-top: 20px;
  }

  .cancel-btn,
  .submit-btn {
    padding: 14px 24px;
    font-size: 16px;
    border-radius: 8px;
    flex: 1;
  }
}

/* 더 작은 모바일 화면 (480px 이하) */
@media (max-width: 480px) {
  .write-modal-overlay {
    padding: 4px;
    padding-top: 10px;
  }

  .write-modal {
    width: calc(100% - 8px);
    max-height: calc(100vh - 20px);
    border-radius: 8px;
  }

  .modal-header {
    padding: 16px 16px 12px 16px;
  }

  .modal-header h3 {
    font-size: 18px;
  }

  .modal-body {
    padding: 12px 16px 16px 16px;
  }

  .place-selector label,
  .rating-input label,
  .text-input label {
    font-size: 15px;
    margin-bottom: 8px;
  }

  .place-select {
    padding: 14px;
    font-size: 15px;
  }

  .star-btn {
    font-size: 26px;
    margin: 0 2px;
  }

  .text-input textarea {
    padding: 14px;
    font-size: 15px;
    min-height: 100px;
  }

  .modal-actions {
    gap: 12px;
    margin-top: 16px;
  }

  .cancel-btn,
  .submit-btn {
    padding: 12px 20px;
    font-size: 15px;
  }
}
</style>