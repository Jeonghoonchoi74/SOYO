// DB에 저장되는 지역명과 사용자에게 표시되는 지역명 매핑
export const regionMapping = {
  '강원특별자치도': '강원도',
  '경기도': '경기도',
  '경상남도': '경상남도',
  '경상북도': '경상북도',
  '광주': '광주',
  '대구': '대구',
  '대전': '대전',
  '부산': '부산',
  '서울': '서울',
  '세종특별자치시': '세종',
  '울산': '울산',
  '인천': '인천',
  '전라남도': '전라남도',
  '전북특별자치도': '전라북도',
  '제주도': '제주도',
  '충청남도': '충청남도',
  '충청북도': '충청북도'
};

// 지역별 사용 가능한 카테고리
export const regionCategories = {
  '강원특별자치도': ['events', 'tourist_attraction'],
  '경기도': ['events'],
  '경상남도': ['events', 'foods', 'tourist_attraction'],
  '경상북도': ['events', 'foods', 'tourist_attraction'],
  '광주': ['events', 'foods', 'tourist_attraction'],
  '대구': ['events', 'foods', 'tourist_attraction'],
  '대전': ['events', 'foods', 'tourist_attraction'],
  '부산': ['events', 'foods', 'tourist_attraction'],
  '서울': ['events'],
  '세종특별자치시': ['events', 'foods', 'tourist_attraction'],
  '울산': ['events', 'foods', 'tourist_attraction'],
  '인천': ['events', 'foods', 'tourist_attraction'],
  '전라남도': ['events', 'foods', 'tourist_attraction'],
  '전북특별자치도': ['events', 'foods', 'tourist_attraction'],
  '제주도': ['events'],
  '충청남도': ['events', 'foods', 'tourist_attraction'],
  '충청북도': ['events', 'foods', 'tourist_attraction']
};

// 카테고리 표시명 매핑
export const categoryLabels = {
  'events': '행사/축제',
  'foods': '맛집',
  'tourist_attraction': '관광지'
};

// DB 지역명을 사용자 표시명으로 변환
export function getDisplayName(dbRegionName) {
  return regionMapping[dbRegionName] || dbRegionName;
}

// 사용자 표시명을 DB 지역명으로 변환
export function getDbRegionName(displayName) {
  const entries = Object.entries(regionMapping);
  const entry = entries.find(([dbName, display]) => display === displayName);
  return entry ? entry[0] : displayName;
}

// 지역 옵션 배열 생성
export function getRegionOptions() {
  return Object.entries(regionMapping).map(([value, label]) => ({
    value,
    label
  })).sort((a, b) => a.label.localeCompare(b.label, 'ko'));
}

// 지역별 사용 가능한 카테고리 가져오기
export function getAvailableCategories(region) {
  return regionCategories[region] || [];
}

// 카테고리 표시명 가져오기
export function getCategoryLabel(category) {
  return categoryLabels[category] || category;
}
