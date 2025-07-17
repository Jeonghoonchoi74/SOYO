<template>
  <div class="destcat-container">
    <button class="bookmark-btn" @click="goBookmark">좋아요/북마크</button>
    <h2 class="title">{{ $t('dest_title') }}</h2>
    <p class="subtitle">{{ $t('dest_subtitle') }}</p>
    <input
      v-model="destination"
      class="destination-input"
      type="text"
      :placeholder="$t('dest_input_placeholder')"
    />
    <div class="category-grid">
      <label v-for="cat in categories" :key="cat.value" class="category-item" :class="{ active: selectedCategories.includes(cat.value) }">
        <input type="checkbox" v-model="selectedCategories" :value="cat.value" class="hidden-checkbox" />
        <span class="icon">{{ cat.icon }}</span>
        <span>{{ cat.label }}</span>
      </label>
    </div>
    <button class="next-btn" :disabled="!canProceed" @click="next">{{ $t('dest_next_btn') }}</button>
  </div>
</template>

<script>
import { i18nState, $t } from '../i18n';
export default {
  name: 'DestinationCategory',
  data() {
    return {
      destination: '',
      categories: [
        { value: 'food', label: $t('dest_category_food'), icon: '🍔' },
        { value: 'shopping', label: $t('dest_category_shopping'), icon: '🛍️' },
        { value: 'culture', label: $t('dest_category_culture'), icon: '🏛️' },
        { value: 'transport', label: $t('dest_category_transport'), icon: '🚌' },
      ],
      selectedCategories: [],
    };
  },
  computed: {
    canProceed() {
      return this.destination.trim() && this.selectedCategories.length > 0;
    },
    $t() { return $t; },
  },
  methods: {
      goBookmark() {
    this.$router.push('/bookmarks');
  },
    next() {
      this.$router.push('/preference');
    },
  },
};
</script>

<style scoped>
.destcat-container {
  width: 800px;
  margin: 60px auto;
  padding: 64px 80px 96px 80px;
  border-radius: 32px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.bookmark-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #fff;
  color: #2563eb;
  border: 2px solid #2563eb;
  border-radius: 10px;
  padding: 0.7rem 1.5rem;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  z-index: 10;
}
.bookmark-btn:hover {
  background: #2563eb;
  color: #fff;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 3rem;
  text-align: center;
  color: #1e293b;
}

.subtitle {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 2.5rem;
}

/* 목적지 입력창 */
.destination-input {
  width: 100%;
  max-width: 500px;
  padding: 1.2rem 1.5rem;
  font-size: 1.2rem;
  border: 2px solid #cbd5e1;
  border-radius: 14px;
  margin-bottom: 2.5rem;
  background: #fff;
  box-sizing: border-box;
  color: #1e293b;
}

.destination-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.destination-input::placeholder {
  color: #64748b;
  opacity: 1;
}

/* 카테고리 선택 영역 */
.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
  max-width: 360px;
  margin-bottom: 3rem;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease-in-out;
}

.category-item:hover {
  border-color: #a5b4fc;
  transform: translateY(-2px);
}

.category-item.active {
  background-color: #e0e7ff; /* 연한 파란색 배경 */
  border-color: #3b82f6; /* 파란색 테두리 */
  color: #1e3a8a; /* 진한 파란색 텍스트 */
}

.icon {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
}

.hidden-checkbox {
  display: none; /* 실제 체크박스는 숨김 */
}

/* 다음 버튼 */
.next-btn {
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

.next-btn:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}
.next-btn:active {
  background: #1e40af;
  transform: translateY(0);
}
.next-btn:disabled {
  background: #cbd5e1;
  color: #fff;
  cursor: not-allowed;
}
</style>