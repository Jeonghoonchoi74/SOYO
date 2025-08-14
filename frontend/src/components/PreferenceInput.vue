<template>
    <div class="pref-container">
      <h2 class="title">{{ $t('pref_title') }}</h2>
      <p class="subtitle">{{ $t('pref_subtitle') }}</p>
      
      <div class="section">
        <div class="section-label">{{ $t('pref_section_region') }}</div>
        <div class="region-selector">
          <select v-model="selectedRegion" class="region-dropdown" @change="onRegionChange">
            <option value="" disabled>{{ $t('pref_region_placeholder') }}</option>
            <option v-for="region in regionOptions" :key="region.value" :value="region.value">
              {{ region.label }}
            </option>
          </select>
        </div>
      </div>
      
      <div v-if="selectedRegion" class="section">
        <div class="section-label">{{ $t('pref_section_category') }}</div>
        <div class="category-selector">
          <button 
            v-for="category in availableCategories" 
            :key="category" 
            :class="['category-btn', { active: selectedCategory === category }]" 
            @click="selectCategory(category)"
          >
            {{ getCategoryDisplayName(category) }}
          </button>
        </div>
      </div>
      
      <!-- 카테고리별 선호도 섹션들 -->
      <div v-if="selectedCategory === 'events'" class="section">
        <div class="section-label">{{ $t('pref_section_purpose') }}</div>
        <div class="toggle-list">
          <button v-for="item in purposeOptions" :key="item" :class="['toggle-btn', { active: selectedPurpose === item }]" @click="selectPurpose(item)">
            {{ $t(item) }}
          </button>
        </div>
      </div>
      
      <div v-if="selectedCategory === 'foods'" class="section">
        <div class="section-label">{{ $t('pref_section_food') }}</div>
        <div class="toggle-list">
          <button v-for="item in foodOptions" :key="item" :class="['toggle-btn', { active: selectedFood === item }]" @click="selectFood(item)">
            {{ $t(item) }}
          </button>
        </div>
      </div>
      
      <div v-if="selectedCategory === 'tourist_attraction'" class="section">
        <div class="section-label">{{ $t('pref_section_attraction') }}</div>
        <div class="toggle-list">
          <button v-for="item in attractionOptions" :key="item" :class="['toggle-btn', { active: selectedAttraction === item }]" @click="selectAttraction(item)">
            {{ $t(item) }}
          </button>
        </div>
      </div>
      
      <!-- 공통 섹션들 -->
      <div v-if="selectedCategory" class="section">
        <div class="section-label">{{ $t('pref_section_sns') }}</div>
        <div class="toggle-list">
          <button v-for="item in snsOptions" :key="item" :class="['toggle-btn', { active: selectedSNS === item }]" @click="selectSNS(item)">
            {{ $t(item) }}
          </button>
        </div>
      </div>

      <div v-if="selectedCategory" class="section">
        <div class="section-label">{{ $t('pref_section_shopping') }}</div>
        <div class="toggle-list">
          <button v-for="item in shoppingOptions" :key="item" :class="['toggle-btn', { active: selectedShopping === item }]" @click="selectShopping(item)">
            {{ $t(item) }}
          </button>
        </div>
      </div>

      <div v-if="selectedCategory" class="section">
        <div class="section-label">{{ $t('pref_section_free') }}</div>
        <textarea
          v-model="freeText"
          class="free-input"
          :placeholder="$t('pref_free_placeholder')"
          rows="3"
        />
      </div>
  
      <button class="recommend-btn" :disabled="!canProceed || isSaving" @click="recommend">
        {{ isSaving ? '저장 중...' : $t('pref_recommend_btn') }}
      </button>
    </div>
  </template>
  
  <script>
  import { i18nState, $t } from '../i18n';
  import { getAuth } from 'firebase/auth';
  import { getRegionOptions, getAvailableCategories, getCategoryLabel } from '../utils/regionMapping';
  export default {
    name: 'PreferenceInput',
    data() {
      return {
        regionOptions: getRegionOptions(),
        selectedRegion: '',
        selectedCategory: '',
        availableCategories: [],
        foodOptions: ['pref_food_mild', 'pref_food_seafood', 'pref_food_vegan'],
        shoppingOptions: ['pref_shop_dutyfree', 'pref_shop_souvenir', 'pref_shop_local'],
        attractionOptions: ['pref_attraction_nature', 'pref_attraction_city', 'pref_attraction_culture'],
        snsOptions: ['pref_sns_life_shot', 'pref_sns_casual', 'pref_sns_artistic'],
        purposeOptions: ['pref_purpose_healing', 'pref_purpose_food', 'pref_purpose_culture', 'pref_purpose_activity'],
        selectedFood: '',
        selectedShopping: '',
        selectedAttraction: '',
        selectedSNS: '',
        selectedPurpose: '',
        freeText: '',
        isSaving: false,
      };
    },
    computed: {
      canProceed() {
        // 지역 선택과 카테고리 선택이 필요함
        return this.selectedRegion && this.selectedCategory;
      },
      $t() { return $t; },
    },

    mounted() {
      this.selectedRegion = '';
      this.selectedCategory = '';
      this.availableCategories = [];
      this.selectedFood = '';
      this.selectedShopping = '';
      this.selectedAttraction = '';
      this.selectedSNS = '';
      this.selectedPurpose = '';
      this.freeText = '';
    },

      methods: {
    selectFood(item) {
      this.selectedFood = item;
    },
    selectShopping(item) {
      this.selectedShopping = item;
    },
    selectAttraction(item) {
      this.selectedAttraction = item;
    },
    selectSNS(item) {
      this.selectedSNS = item;
    },
    selectPurpose(item) {
      this.selectedPurpose = item;
    },
    onRegionChange() {
      this.selectedCategory = ''; // 지역 변경 시 카테고리 초기화
      this.availableCategories = getAvailableCategories(this.selectedRegion);
    },
    selectCategory(category) {
      this.selectedCategory = category;
    },
    getCategoryDisplayName(category) {
      return getCategoryLabel(category);
    },
      async savePreferences() {
        const auth = getAuth();
        const user = auth.currentUser;
        
        if (!user) {
          console.error('사용자가 로그인되지 않았습니다.');
          return false;
        }

        const preferences = {
          region: this.selectedRegion,
          category: this.selectedCategory,
          food: this.selectedFood,
          shopping: this.selectedShopping,
          attraction: this.selectedAttraction,
          sns: this.selectedSNS,
          purpose: this.selectedPurpose,
          freeText: this.freeText,
        };

        try {
          this.isSaving = true;
          
          const response = await fetch('http://localhost:5000/api/save_user_preferences', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              uid: user.uid,
              preferences: preferences
            }),
          });

          const result = await response.json();
          
          if (result.success) {
            console.log('사용자 선호도가 성공적으로 저장되었습니다.');
            return true;
          } else {
            console.error('선호도 저장 실패:', result.error);
            return false;
          }
        } catch (error) {
          console.error('선호도 저장 중 오류 발생:', error);
          return false;
        } finally {
          this.isSaving = false;
        }
      },

      async recommend() {
        if (this.isSaving) return;
        
        const saved = await this.savePreferences();
        if (saved) {
          this.$router.push({
            path: '/recommend',
            query: { 
              region: this.selectedRegion,
              category: this.selectedCategory
            }
          });
        } else {
          // 저장 실패 시에도 추천 페이지로 이동 (선택사항)
          this.$router.push({
            path: '/recommend',
            query: { 
              region: this.selectedRegion,
              category: this.selectedCategory
            }
          });
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .pref-container {
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
  
  .subtitle {
    font-size: 1rem;
    color: #64748b;
    margin-bottom: 2.5rem;
    text-align: center;
  }
  
  .section {
    width: 100%;
    max-width: 500px;
    margin-bottom: 2rem;
  }
  
  .section-label {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #1e293b;
  }
  
  .toggle-list {
    display: flex;
    gap: 1.2rem;
  }
  
  .toggle-btn {
    flex: 1;
    padding: 1rem 0.8rem;
    border: none;
    border-radius: 24px;
    background: #e2e8f0;
    color: #222;
    font-size: 1.2rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .toggle-btn:hover {
    border-color: #a5b4fc;
    color: #1e3a8a;
  }
  
  .toggle-btn.active {
    background: #2563eb;
    color: #fff;
  }
  
  .region-selector {
    width: 100%;
  }
  
  .region-dropdown {
    width: 100%;
    padding: 1rem 1.5rem;
    font-size: 1.2rem;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    background: #fff;
    color: #1e293b;
    cursor: pointer;
    transition: border-color 0.2s;
  }
  
  .region-dropdown:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .region-dropdown option {
    padding: 0.5rem;
    font-size: 1.1rem;
  }

  .category-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
  }

  .category-btn {
    flex: 1;
    padding: 0.8rem 1.2rem;
    border: none;
    border-radius: 24px;
    background: #e2e8f0;
    color: #222;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.2s;
  }

  .category-btn:hover {
    border-color: #a5b4fc;
    color: #1e3a8a;
  }

  .category-btn.active {
    background: #2563eb;
    color: #fff;
  }
  
  .free-input {
    width: 100%;
    max-width: 500px;
    padding: 1.2rem 1.5rem;
    font-size: 1.2rem;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    margin-bottom: 1rem;
    background: #fff;
    box-sizing: border-box;
    resize: none;
    color: #1e293b;
  }
  
  .free-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .recommend-btn {
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
  
  .recommend-btn:hover {
    background: #1d4ed8;
    transform: translateY(-2px);
  }
  .recommend-btn:active {
    background: #1e40af;
    transform: translateY(0);
  }
  .recommend-btn:disabled {
    background: #cbd5e1;
    color: #fff;
    cursor: not-allowed;
  }
  
  /* 모바일 반응형 */
  @media (max-width: 768px) {
    .pref-container {
      width: 100%;
      margin: 20px auto;
      padding: 40px 20px 60px 20px;
      border-radius: 20px;
    }
    
    .title {
      font-size: 1.5rem;
      margin-bottom: 2rem;
    }
    
    .subtitle {
      font-size: 0.9rem;
      margin-bottom: 2rem;
    }
    
    .section {
      max-width: 100%;
      margin-bottom: 1.5rem;
    }
    
    .section-label {
      font-size: 1.1rem;
      margin-bottom: 0.8rem;
    }
    
    .toggle-list {
      flex-direction: column;
      gap: 0.8rem;
    }
    
    .toggle-btn {
      padding: 0.8rem 0.6rem;
      font-size: 1rem;
    }
    
    .region-dropdown {
      padding: 0.8rem 1.2rem;
      font-size: 1rem;
    }

    .category-btn {
      padding: 0.6rem 1rem;
      font-size: 0.9rem;
    }
    
    .free-input {
      padding: 1rem 1.2rem;
      font-size: 1rem;
    }
    
    .recommend-btn {
      padding: 1.2rem 0;
      font-size: 1.1rem;
    }
  }
  </style>