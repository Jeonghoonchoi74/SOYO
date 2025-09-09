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
      뒤로가기
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
        <h2 class="title">{{ currentQuestion.text }}</h2>
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
          <div class="option-text-guided">{{ option.text }}</div>
          <div v-if="option.description" class="option-description-guided">
            {{ option.description }}
          </div>
        </div>
      </div>

      <!-- Region Modal Trigger -->
      <div v-if="currentQuestion.isRegion && !isConfirmationStep">
        <div class="form-group">
          <label class="section-label">{{ currentQuestion.text }}</label>
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
              전국 또는 특정 지역을 선택하세요
            </span>
            <span class="dropdown-icon">▼</span>
          </button>
        </div>
      </div>

      <!-- Confirmation Step -->
      <div v-if="isConfirmationStep" class="confirmation-container">
        <div class="step-header">
          <h2 class="title">이대로 추천을 받을까요?</h2>
        </div>
        <div class="final-query">
          <p><strong>완성된 검색어:</strong></p>
          <p>{{ finalQuery }}</p>
        </div>
        <div class="confirmation-buttons">
          <button @click="goBack" class="recommend-btn secondary">
            다시 선택
          </button>
          <button @click="startRecommendation" class="recommend-btn">
            추천 받기
          </button>
        </div>
      </div>
    </div>

    <!-- Region Select Modal -->
    <div v-if="showRegionModal" class="modal-overlay" @click="closeRegionModal">
      <div class="modal-content region-modal" @click.stop>
        <div class="modal-header">
          <h3>지역 선택</h3>
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
              @click="selectRegion(region.value)"
            >
              {{ $t(region.label) }}
            </button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="confirmRegionSelection">
            확인
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAuth } from "firebase/auth";
import { getRegionOptions } from "../utils/regionMapping";
import questions from "../utils/guidedSearchQuestions";
import { $t } from "../i18n";

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
      tempSelectedRegion: "",
      isSaving: false,
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

      // Build query with suffixes
      for (const id in selections) {
        if (
          selections[id] &&
          selections[id].text &&
          selections[id].value !== "any"
        ) {
          const suffixRule = queryConfig.suffixes?.[id];
          let text = selections[id].text; // 기본 텍스트를 먼저 할당

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
                text = specificSuffix.substring(1);
              } else {
                // 기존 방식대로 뒤에 덧붙임
                text += specificSuffix;
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
    startRecommendation() {
      this.recommend();
    },

    async recommend() {
      if (this.isSaving) return;

      const auth = getAuth();
      const user = auth.currentUser;

      if (!user) {
        console.error("사용자가 로그인되지 않았습니다.");
        return;
      }

      try {
        this.isSaving = true;
        const finalQuery = this.finalQuery;
        const region = this.userSelections.region
          ? this.userSelections.region.value
          : "";
        const category = this.userSelections.category
          ? this.userSelections.category.value
          : "";

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
  },
};
</script>

<style scoped>
/* Using styles from PreferenceInput.vue and SearchChooser.vue for consistency */
.preference-page {
  min-height: 100vh;
  background: #f7f8fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  position: relative;
}
.page-back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  background: white;
  color: #4a69e2;
  border: 1px solid #4a69e2;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  z-index: 1000;
}
.page-back-btn:hover {
  background: #4a69e2;
  color: white;
}
.preference-content {
  width: 100%;
  max-width: 720px;
  background: white;
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-top: 20px;
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
  background: #f7f8fa;
  color: #212529;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: left;
}
.region-selector-btn:hover {
  border-color: #4a69e2;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 105, 226, 0.1);
}
.region-selector-btn.has-selection {
  background: white;
  border-color: #4a69e2;
  color: #4a69e2;
}
.region-selector-btn .placeholder {
  color: #adb5bd;
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
  z-index: 3000;
  padding: 20px;
  color: #212529;
}
.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
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
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}
.region-option {
  padding: 16px 20px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #f8f9fa;
  color: #495057;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}
.region-option:hover {
  background: #e9ecef;
}
.region-option.active {
  background: #4a69e2;
  border-color: #4a69e2;
  color: white;
}
.modal-footer {
  padding: 20px 24px;
  display: flex;
  justify-content: flex-end;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
.btn-primary {
  background: #4a69e2;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}
</style>
