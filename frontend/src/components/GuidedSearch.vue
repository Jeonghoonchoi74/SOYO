<template>
  <div class="preference-page">

    <button class="page-back-btn" @click="goToSearch">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path d="M19 12H5M12 19l-7-7 7-7" />
      </svg>
    </button>
    <div class="preference-content">
      <div class="progress-bar" v-if="currentStep > 0 && !isConfirmationStep">
        <div
          class="progress"
          :style="{ width: progressPercentage + '%' }"
        ></div>
      </div>

      <!-- Step Title -->
      <div class="step-header" v-if="!isConfirmationStep">
        <button v-if="history.length > 0" @click="goBack" class="back-btn">
          ←
        </button>
        <h2 class="title">{{ $t(currentQuestion.text) }}</h2>
      </div>

      <!-- Options -->
      <div
        class="options-container"
        v-if="!currentQuestion.isRegion && !isConfirmationStep"
      >
        <div
          v-for="(option, index) in currentQuestion.options"
          :key="index"
          class="option-card-guided"
          :class="{ active: isSelected(option.value) }"
          @click="selectOption(option)"
        >
          <div class="option-icon-guided" v-if="option.icon">
            {{ option.icon }}
          </div>
          <div class="option-text-guided">{{ $t(option.text) }}</div>
          <div v-if="option.description" class="option-description-guided">
            {{ option.description }}
          </div>
        </div>
      </div>

      <!-- Region Modal Trigger -->
      <div v-if="currentQuestion.isRegion && !isConfirmationStep">
        <div class="form-group">
          <label class="section-label">{{ $t(currentQuestion.text) }}</label>
          <button
            type="button"
            class="region-selector-btn"
            @click="openRegionModal"
            :class="{ 'has-selection': userSelections.region }"
          >
            <span v-if="userSelections.region">
              {{ getSelectedRegionDisplayName() }}
            </span>
            <span v-else class="placeholder">
              {{ $t('guided_search_region_placeholder') }}
            </span>
            <span class="dropdown-icon">▼</span>
          </button>
        </div>
        
        <!-- Region Description -->
        <div v-if="userSelections.region" class="form-group">
          <div class="region-description">
            <p class="description-text">{{ $t(getRegionDescription(userSelections.region.value)) }}</p>
          </div>
        </div>
      </div>

      <!-- Confirmation Step -->
      <div v-if="isConfirmationStep" class="confirmation-container">
        <div class="step-header">
          <h2 class="title">{{ $t('guided_search_confirm_title') }}</h2>
        </div>
        <div class="final-query">
          <p><strong>{{ $t('guided_search_final_query') }}</strong></p>
          <p>{{ finalQuery }}</p>
        </div>
        <div class="confirmation-buttons">
          <button @click="goBack" class="recommend-btn secondary">
            {{ $t('guided_search_retry') }}
          </button>
          <button @click="startRecommendation" class="recommend-btn">
            {{ $t('guided_search_recommend') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Region Select Modal -->
    <div v-if="showRegionModal" class="modal-overlay" @click="closeRegionModal">
      <div class="modal-content region-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('guided_search_region_select') }}</h3>
          <button class="close-btn" @click="closeRegionModal">×</button>
        </div>
        <div class="modal-body">
          <div class="region-grid">
            <button
              v-for="region in regionOptions"
              :key="region.value"
              :class="[
                'region-option',
                { active: tempSelectedRegion === region.value },
              ]"
              @click="selectRegionAndClose(region.value)"
              :title="$t(region.label)"
            >
              <div class="region-image">
                <img :src="region.image" :alt="$t(region.label)" />
              </div>
              <span class="region-name">{{ $t(region.label) }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 검색 중 모달 -->
    <div v-if="showSearchingModal" class="modal-overlay">
      <div class="modal-content searching-modal">
        <div class="searching-container">
          <div class="searching-image">
            <img :src="currentSearchingImage" alt="Searching" />
          </div>
          <h3 class="searching-title">{{ $t('searching_title') }}</h3>
          <p class="searching-message">{{ $t('searching_message') }}</p>
        </div>
      </div>
    </div>

    <!-- 튜토리얼 모달 -->
    <div v-if="showTutorialModal" class="modal-overlay" @click="closeTutorial">
      <div class="modal-box tutorial-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('tutorial_title') }}</h3>
          <button class="close-btn" @click="closeTutorial">×</button>
        </div>
        <div class="tutorial-content">
          <div class="tutorial-step" v-for="(step, index) in tutorialSteps" :key="index">
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h4>{{ $t(step.title) }}</h4>
              <p>{{ $t(step.description) }}</p>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="modal-btn primary" @click="closeTutorial">{{ $t('tutorial_got_it') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAuth } from "firebase/auth";
import { getRegionOptions, getRegionDescription } from "../utils/regionMapping";
import questions from "../utils/guidedSearchQuestions";
import { $t, i18nState } from "../i18n";
import trying1 from "../assets/trying1.jpg";
import trying2 from "../assets/trying2.png";

export default {
  name: "GuidedSearch",
  data() {
    return {
      questions: questions,
      currentStep: 1,
      userSelections: {},
      history: [],
      currentPath: "",
      currentSubPath: "",
      regionOptions: getRegionOptions(),
      showRegionModal: false,
      showSearchingModal: false,
      tempSelectedRegion: "",
      isSaving: false,
      trying1: trying1,
      trying2: trying2,
      searchingImages: [trying1, trying2],
      currentSearchingImageIndex: 0,
      searchingImageInterval: null,
      showTutorialModal: false,
      tutorialSteps: [
        {
          title: 'tutorial_step1_title',
          description: 'tutorial_step1_desc'
        },
        {
          title: 'tutorial_step2_title',
          description: 'tutorial_step2_desc'
        },
        {
          title: 'tutorial_step3_title',
          description: 'tutorial_step3_desc'
        },
        {
          title: 'tutorial_step4_title',
          description: 'tutorial_step4_desc'
        },
        {
          title: 'tutorial_step5_title',
          description: 'tutorial_step5_desc'
        },
        {
          title: 'tutorial_step6_title',
          description: 'tutorial_step6_desc'
        },
        {
          title: 'tutorial_step7_title',
          description: 'tutorial_step7_desc'
        }
      ]
    };
  },
  computed: {
    currentQuestion() {
      return this.questions.steps[this.currentStep] || {};
    },
    isConfirmationStep() {
      return this.currentQuestion.isConfirmation;
    },
    progressPercentage() {
      const pathKey = this.currentPath + this.currentSubPath;
      const totalSteps = this.questions.pathConfig[pathKey] || 10; // Default to a higher number
      const completedSteps = this.history.length;
      if (totalSteps === 0) return 0;
      return (completedSteps / totalSteps) * 100;
    },
    currentSearchingImage() {
      return this.searchingImages[this.currentSearchingImageIndex];
    },
    finalQuery() {
      const queryConfig = this.questions.queryConfig;
      let queryParts = [];
      const selections = { ...this.userSelections };

      // Handle redundancy
      for (const child in queryConfig.redundancyMap) {
        if (selections[child]) {
          const parent = queryConfig.redundancyMap[child];
          delete selections[parent];
        }
      }

      // Build query with suffixes (exclude region selection)
      for (const id in selections) {
        if (
          selections[id] &&
          selections[id].text &&
          selections[id].value !== "any" &&
          id !== "region" // 지역 선택은 쿼리에서 제외
        ) {
          const suffixRule = queryConfig.suffixes?.[id];
          let text = this.$t(selections[id].text); // 기본 텍스트를 먼저 할당

          if (suffixRule && selections[id].value !== "alone") {
            let specificSuffix = "";
            // 규칙이 객체인지 확인
            if (typeof suffixRule === "object" && suffixRule !== null) {
              specificSuffix = suffixRule[selections[id].value];
            } else {
              specificSuffix = suffixRule;
            }

            if (specificSuffix) {
              // suffix가 '*'로 시작하는지 확인
              if (specificSuffix.startsWith("*")) {
                // '*'를 제외한 나머지 문자열로 text 전체를 교체
                text = this.$t(specificSuffix.substring(1));
              } else {
                // 기존 방식대로 뒤에 덧붙임
                text += this.$t(specificSuffix);
              }
            }
          }
          queryParts.push(text);
        }
      }
      return queryParts.join(", ");
    },
  },
  watch: {
    currentStep(newStep) {
      if (this.questions.steps[newStep]?.isRegion) {
        this.openRegionModal();
      }
    },
  },
  methods: {
    $t(key) {
      return $t(key);
    },
    goToSearch() {
      this.$router.push("/search");
    },
    selectOption(option) {
      // Set path for progress bar
      if (option.path) {
        this.currentPath = option.path;
      }
      if (option.subPath) {
        this.currentSubPath = option.subPath;
      }

      this.history.push(this.currentStep);
      this.userSelections[this.currentQuestion.id] = {
        text: option.text,
        value: option.value,
      };
      this.currentStep = option.nextStep;
    },
    goBack() {
      if (this.history.length > 0) {
        const previousStep = this.history.pop();
        const stepToClear = this.questions.steps[this.currentStep];
        if (stepToClear && stepToClear.id) {
          delete this.userSelections[stepToClear.id];
        }
        // Reset path if we go back to a path-defining question
        const prevQuestion = this.questions.steps[previousStep];
        if (prevQuestion.options.some((o) => o.path)) {
          this.currentPath = "";
        }
        if (prevQuestion.options.some((o) => o.subPath)) {
          this.currentSubPath = "";
        }

        this.currentStep = previousStep;
      }
    },
    isSelected(value) {
      const selection = this.userSelections[this.currentQuestion.id];
      return selection && selection.value === value;
    },
    // Region Modal Methods
    openRegionModal() {
      this.tempSelectedRegion = this.userSelections.region
        ? this.userSelections.region.value
        : "";
      this.showRegionModal = true;
    },
    closeRegionModal() {
      this.showRegionModal = false;
    },
    selectRegion(regionValue) {
      this.tempSelectedRegion = regionValue;
    },
    selectRegionAndClose(regionValue) {
      const region = this.regionOptions.find(
        (r) => r.value === regionValue
      );
      if (region) {
        this.userSelections.region = {
          text: this.$t(region.label),
          value: region.value,
        };
      }
      this.closeRegionModal();
      console.log('지역 선택 완료, 다음 단계로 이동:', this.currentQuestion.nextStep);
      console.log('현재 사용자 선택:', this.userSelections);
      this.currentStep = this.currentQuestion.nextStep;
    },
    confirmRegionSelection() {
      const region = this.regionOptions.find(
        (r) => r.value === this.tempSelectedRegion
      );
      if (region) {
        this.userSelections.region = {
          text: this.$t(region.label),
          value: region.value,
        };
      } else {
        // Handle case where no region is selected but confirmed
        this.userSelections.region = { text: "전국", value: "all" };
      }
      this.history.push(this.currentStep);
      this.currentStep = this.currentQuestion.nextStep;
      this.showRegionModal = false;
    },
    getSelectedRegionDisplayName() {
      const region = this.userSelections.region;
      return region ? region.text : "";
    },
    getRegionDescription(region) {
      return getRegionDescription(region);
    },
    startRecommendation() {
      this.recommend();
    },

    // 번역 API 호출 함수
    async translateQuery(query, targetLang = 'ko', sourceLang = 'auto') {
      const auth = getAuth();
      const user = auth.currentUser;
      
      if (!user) {
        console.error('사용자가 로그인되지 않았습니다.');
        return query;
      }

      try {
        console.log('번역 요청 시작:', query);
        console.log('소스 언어:', sourceLang, '→ 타겟 언어:', targetLang);
        
        const response = await fetch('/api/translate/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: query,
            source_lang: sourceLang,
            target_language: targetLang,
            uid: user.uid
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.translated_text) {
          console.log('원본 텍스트:', query);
          console.log('번역된 텍스트 (한국어):', result.translated_text);
          return result.translated_text;
        } else {
          console.error('번역 결과가 없습니다:', result);
          return query;
        }
        
      } catch (error) {
        console.error('번역 API 호출 중 오류 발생:', error);
        return query; // 오류 시 원본 쿼리 반환
      }
    },

    async recommend() {
      if (this.isSaving) return;

      const auth = getAuth();
      const user = auth.currentUser;

      if (!user) {
        console.error("사용자가 로그인되지 않았습니다.");
        return;
      }

      // 검색 중 모달 표시
      this.showSearchingModal = true;
      this.isSaving = true;
      this.startSearchingImageRotation();

      try {
        let finalQuery = this.finalQuery;
        const region = this.userSelections.region
          ? this.userSelections.region.value
          : "";
        const category = this.userSelections.category
          ? this.userSelections.category.value
          : "";

        // 현재 언어가 한국어가 아닌 경우 번역 수행
        if (i18nState.lang !== 'ko') {
          console.log("현재 언어가 한국어가 아님, 번역 API 호출 중...");
          console.log("원본 쿼리:", finalQuery);
          finalQuery = await this.translateQuery(finalQuery, 'ko', i18nState.lang);
          console.log("번역된 쿼리:", finalQuery);
        }

        // 상세한 파라미터 로그
        console.log("=== 추천 API 요청 파라미터 ===");
        console.log("사용자 UID:", user.uid);
        console.log("최종 검색어:", finalQuery);
        console.log("선택된 지역:", region);
        console.log("선택된 카테고리:", category);
        console.log("전체 사용자 선택:", this.userSelections);
        console.log("요청 URL:", "/api/recommend/search");

        const requestData = {
          uid: user.uid,
          query: finalQuery,
          region: region,
          category: category,
        };

        console.log("전송할 데이터:", requestData);

        const response = await fetch("/api/recommend/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            uid: user.uid,
            query: finalQuery,
            region: region,
            category: category,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        const searchResults = result.data;

        console.log("=== 추천 API 응답 ===");
        console.log("응답 상태:", response.status);
        console.log("응답 헤더:", response.headers);
        console.log("전체 응답:", result);
        console.log("검색 결과 데이터:", searchResults);
        console.log("결과 개수:", searchResults ? searchResults.length : 0);

        localStorage.setItem(
          "tempSearchResults",
          JSON.stringify(searchResults)
        );

        // 검색 중 모달 숨기기
        this.showSearchingModal = false;
        this.stopSearchingImageRotation();

        this.$router.push({
          path: "/recommend",
          query: {
            region: region,
            category: category,
            searchQuery: finalQuery,
          },
        });
      } catch (error) {
        console.error("=== 추천 API 오류 ===");
        console.error("오류 메시지:", error.message);
        console.error("오류 스택:", error.stack);
        console.error("전체 오류 객체:", error);
        
        // 검색 중 모달 숨기기
        this.showSearchingModal = false;
        this.stopSearchingImageRotation();
        
        this.$router.push({
          path: "/recommend",
          query: {
            region: this.userSelections.region
              ? this.userSelections.region.value
              : "",
            category: this.userSelections.category
              ? this.userSelections.category.value
              : "",
            searchQuery: this.finalQuery,
          },
        });
      } finally {
        this.isSaving = false;
      }
    },
    
    goHome() {
      this.$router.push('/main');
    },

    // 검색 중 이미지 교체 관련 메서드들
    startSearchingImageRotation() {
      this.currentSearchingImageIndex = 0;
      this.searchingImageInterval = setInterval(() => {
        this.currentSearchingImageIndex = (this.currentSearchingImageIndex + 1) % this.searchingImages.length;
      }, 500); // 0.5초마다 이미지 변경
    },

    stopSearchingImageRotation() {
      if (this.searchingImageInterval) {
        clearInterval(this.searchingImageInterval);
        this.searchingImageInterval = null;
      }
    },
    showTutorial() {
      this.showTutorialModal = true;
    },
    closeTutorial() {
      this.showTutorialModal = false;
    }
  },

  beforeUnmount() {
    // 컴포넌트 언마운트 시 interval 정리
    this.stopSearchingImageRotation();
  },
};
</script>

<style scoped>
/* 메인페이지와 일치하는 파란색 배경 */
.preference-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  position: relative;
}
.page-back-btn {
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
.page-back-btn:hover {
  background: #3B5BC7;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}
.preference-content {
  width: 100%;
  max-width: 720px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  margin-top: 20px;
  position: relative;
  z-index: 10;
}
.progress-bar {
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  margin-bottom: 24px;
  overflow: hidden;
}
.progress {
  height: 100%;
  background-color: #4a69e2;
  transition: width 0.3s ease;
}
.step-header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 32px;
}
.back-btn {
  position: absolute;
  left: 0;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #495057;
  padding: 0 10px;
}
.title {
  font-size: 24px;
  font-weight: 700;
  color: #212529;
  text-align: center;
  margin: 0;
}
.options-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.option-card-guided {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid #e9ecef;
  text-align: center;
}
.option-card-guided:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}
.option-card-guided.active {
  border-color: #4a69e2;
  background-color: #f1f4fe;
  box-shadow: 0 6px 16px rgba(74, 105, 226, 0.2);
}
.option-icon-guided {
  font-size: 36px;
  margin-bottom: 12px;
}
.option-text-guided {
  font-size: 16px;
  font-weight: 600;
  color: #343a40;
}
.option-description-guided {
  font-size: 13px;
  color: #6c757d;
  margin-top: 8px;
}
.confirmation-container {
  margin-top: 32px;
  text-align: center;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
}
.final-query {
  margin-bottom: 24px;
  font-size: 16px;
  color: #495057;
}
.recommend-btn {
  width: 48%;
  padding: 16px;
  background: #4a69e2;
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.recommend-btn:hover {
  background: #3b5bc7;
}
.recommend-btn.secondary {
  background: #6c757d;
}
.recommend-btn.secondary:hover {
  background: #5a6268;
}
.confirmation-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* Region Modal Styles */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.section-label {
  font-size: 16px;
  font-weight: 600;
  color: #212529;
  text-align: left;
}
.region-selector-btn {
  width: 100%;
  padding: 14px 16px;
  font-size: 14px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #ffffff;
  color: #212529;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: left;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}
.region-selector-btn:hover {
  border-color: #4A69E2;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(74, 105, 226, 0.12);
}
.region-selector-btn.has-selection {
  background: #ffffff;
  border-color: #4A69E2;
  color: #4A69E2;
}
.region-selector-btn .placeholder {
  color: #adb5bd;
}

.region-description {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 8px;
}

.description-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #495057;
  text-align: left;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  color: #212529;
  width: 100vw;
  height: 100vh;
  box-sizing: border-box;
}
.modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  width: 100%;
  max-width: 900px;
  max-height: 95vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 10000;
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
}
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #adb5bd;
  cursor: pointer;
}
.modal-body {
  padding: 20px 24px;
}
.region-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 4px;
  max-height: 900px;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}
.region-grid::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}
.region-option {
  padding: 0;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #495057;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  min-height: 100px;
  position: relative;
  overflow: hidden;
}
.region-option:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 10;
}
.region-option.active {
  box-shadow: 0 4px 12px rgba(74, 105, 226, 0.5);
  transform: scale(1.02);
  z-index: 10;
}
.region-image {
  width: 100%;
  height: 100%;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  position: absolute;
  top: 0;
  left: 0;
}
.region-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.region-name {
  font-size: 11px;
  font-weight: 600;
  line-height: 1.2;
  text-align: center;
  word-break: keep-all;
  opacity: 1;
  transform: translateX(-50%) translateY(0);
  transition: all 0.2s ease;
  position: absolute;
  bottom: 6px;
  left: 50%;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 10;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.modal-footer {
  padding: 20px 24px;
  display: flex;
  justify-content: flex-end;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
.btn-primary {
  background: #4A69E2;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

/* 반응형 */
@media (max-width: 768px) {
  .region-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: auto;
    gap: 4px;
  }
  .region-option {
    padding: 0;
    min-height: 70px;
  }
  .region-image {
    width: 100%;
    height: 100%;
  }
  .region-name {
    font-size: 10px;
    bottom: 2px;
  }
}

/* 플로팅 버튼 스타일 */
.float-btn {
  position: fixed;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.float-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.home-float-btn {
  bottom: 20px;
  right: 20px;
  background: #28a745;
  color: white;
}

.home-float-btn:hover {
  background: #218838;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

/* 검색 중 모달 스타일 */
.searching-modal {
  max-width: 400px;
  text-align: center;
  z-index: 10000;
  position: relative;
}

.searching-container {
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.searching-image {
  width: 200px;
  height: 200px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.searching-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.searching-title {
  font-size: 20px;
  font-weight: 600;
  color: #212529;
  margin: 0;
}

.searching-message {
  font-size: 16px;
  color: #6c757d;
  margin: 0;
  line-height: 1.5;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .float-btn {
    width: 50px;
    height: 50px;
  }
  
  .home-float-btn {
    right: 20px;
  }

  /* 도움말 버튼 */
  .help-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: rgba(255, 255, 255, 0.9);
    color: #333;
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    width: 45px;
    height: 45px;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .help-btn:hover {
    background: rgba(255, 255, 255, 1);
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  /* 모달 박스 스타일 */
  .modal-box {
    background: white;
    border-radius: 16px;
    width: 100%;
    max-width: 480px;
    max-height: 85vh;
    overflow-y: auto;
    color: #212529;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    position: relative;
    z-index: 10000;
  }

  /* 튜토리얼 모달 */
  .tutorial-modal {
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
  }

  .tutorial-content {
    max-height: 60vh;
    overflow-y: auto;
    padding: 20px 24px;
  }

  .tutorial-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e9ecef;
  }

  .tutorial-step:last-child {
    border-bottom: none;
    margin-bottom: 0;
  }

  .step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #4A69E2;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 14px;
    flex-shrink: 0;
  }

  .step-content h4 {
    margin: 0 0 8px 0;
    color: #212529;
    font-size: 16px;
    font-weight: 600;
  }

  .step-content p {
    margin: 0;
    color: #495057;
    line-height: 1.6;
    font-size: 14px;
  }

  .modal-actions {
    display: flex;
    justify-content: center;
    padding: 20px 24px 24px 24px;
  }

  .modal-btn {
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    border: none;
    font-weight: 500;
    transition: all 0.2s ease;
    min-width: 120px;
  }

  .modal-btn.primary {
    background: #4A69E2;
    color: white;
  }

  .modal-btn.primary:hover {
    background: #3B5BC7;
  }
  
  .modal-overlay {
    padding: 10px;
    z-index: 9999;
  }

  /* 모바일 반응형 */
  @media (max-width: 768px) {
    .help-btn {
      width: 40px;
      height: 40px;
      bottom: 15px;
      right: 15px;
      font-size: 16px;
    }

    .tutorial-modal {
      max-width: 95vw;
      max-height: 85vh;
    }

    .tutorial-content {
      max-height: 65vh;
      padding: 16px 20px;
    }

    .tutorial-step {
      gap: 12px;
      margin-bottom: 20px;
      padding-bottom: 16px;
    }

    .step-number {
      width: 28px;
      height: 28px;
      font-size: 12px;
    }

    .step-content h4 {
      font-size: 15px;
    }

    .step-content p {
      font-size: 13px;
    }
  }
  
  .modal-content {
    max-width: 95vw;
    max-height: 90vh;
    z-index: 10000;
  }
  
  .searching-modal {
    max-width: 350px;
    z-index: 10000;
  }
  
  .searching-container {
    padding: 32px 20px;
    gap: 16px;
  }
  
  .searching-image {
    width: 160px;
    height: 160px;
  }
  
  .searching-title {
    font-size: 18px;
  }
  
  .searching-message {
    font-size: 14px;
  }
}
</style>
