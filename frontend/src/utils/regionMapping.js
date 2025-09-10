// DB에 저장되는 지역명과 다국어 키 매핑
export const regionMapping = {
  '전국': 'region_nationwide',
  '강원특별자치도': 'region_gangwon',
  '경기도': 'region_gyeonggi',
  '경상남도': 'region_gyeongnam',
  '경상북도': 'region_gyeongbuk',
  '광주': 'region_gwangju',
  '대구': 'region_daegu',
  '대전': 'region_daejeon',
  '부산': 'region_busan',
  '서울': 'region_seoul',
  '세종특별자치시': 'region_sejong',
  '울산': 'region_ulsan',
  '인천': 'region_incheon',
  '전라남도': 'region_jeonnam',
  '전북특별자치도': 'region_jeonbuk',
  '제주도': 'region_jeju',
  '충청남도': 'region_chungnam',
  '충청북도': 'region_chungbuk'
};

// 지역별 사용 가능한 카테고리
export const regionCategories = {
  '전국': ['events', 'foods', 'tourist attraction'],
  '강원특별자치도': ['events', 'tourist attraction'],
  '경기도': ['events'],
  '경상남도': ['events', 'foods', 'tourist attraction'],
  '경상북도': ['events', 'foods', 'tourist attraction'],
  '광주': ['events', 'foods', 'tourist attraction'],
  '대구': ['events', 'foods', 'tourist attraction'],
  '대전': ['events', 'foods', 'tourist attraction'],
  '부산': ['events', 'foods', 'tourist attraction'],
  '서울': ['events'],
  '세종특별자치시': ['events', 'foods', 'tourist attraction'],
  '울산': ['events', 'foods', 'tourist attraction'],
  '인천': ['events', 'foods', 'tourist attraction'],
  '전라남도': ['events', 'foods', 'tourist attraction'],
  '전북특별자치도': ['events', 'foods', 'tourist attraction'],
  '제주도': ['events'],
  '충청남도': ['events', 'foods', 'tourist attraction'],
  '충청북도': ['events', 'foods', 'tourist attraction']
};

// 카테고리 표시명 매핑 (다국어 키)
export const categoryLabels = {
  'events': 'category_events',
  'foods': 'category_foods',
  'tourist attraction': 'category_tourist_attraction'
};

// DB 지역명을 다국어 키로 변환
export function getDisplayName(dbRegionName) {
  return regionMapping[dbRegionName] || dbRegionName;
}

// 사용자 표시명을 DB 지역명으로 변환
export function getDbRegionName(displayName) {
  const entries = Object.entries(regionMapping);
  const entry = entries.find(([dbName, display]) => display === displayName);
  return entry ? entry[0] : displayName;
}

// 지역별 이미지 경로 매핑
export const regionImages = {
  '전국': '/src/assets/regions/전국.png', // 전국 이미지가 없으므로 서울 이미지 사용
  '강원특별자치도': '/src/assets/regions/강원도.jpg',
  '경기도': '/src/assets/regions/경기도.jpg',
  '경상남도': '/src/assets/regions/경상남도.jpg',
  '경상북도': '/src/assets/regions/경상북도.jpg',
  '광주': '/src/assets/regions/광주.jpg',
  '대구': '/src/assets/regions/대구.jpg',
  '대전': '/src/assets/regions/대전.jpg',
  '부산': '/src/assets/regions/부산.jpg',
  '서울': '/src/assets/regions/서울.jpg',
  '세종특별자치시': '/src/assets/regions/세종특별자치시.jpg',
  '울산': '/src/assets/regions/울산.jpg',
  '인천': '/src/assets/regions/인천.jpg',
  '전라남도': '/src/assets/regions/전라남도.jpg',
  '전북특별자치도': '/src/assets/regions/전라북도.jpg',
  '제주도': '/src/assets/regions/제주도.jpg',
  '충청남도': '/src/assets/regions/충청남도.jpg',
  '충청북도': '/src/assets/regions/충청북도.jpg'
};

// 지역별 설명 데이터 (i18n 키)
export const regionDescriptions = {
  '전국': 'region_desc_nationwide',
  '강원특별자치도': 'region_desc_gangwon',
  '경기도': 'region_desc_gyeonggi',
  '경상남도': 'region_desc_gyeongnam',
  '경상북도': 'region_desc_gyeongbuk',
  '광주': 'region_desc_gwangju',
  '대구': 'region_desc_daegu',
  '대전': 'region_desc_daejeon',
  '부산': 'region_desc_busan',
  '서울': 'region_desc_seoul',
  '세종특별자치시': 'region_desc_sejong',
  '울산': 'region_desc_ulsan',
  '인천': 'region_desc_incheon',
  '전라남도': 'region_desc_jeonnam',
  '전북특별자치도': 'region_desc_jeonbuk',
  '제주도': 'region_desc_jeju',
  '충청남도': 'region_desc_chungnam',
  '충청북도': 'region_desc_chungbuk'
};

// 지역 옵션 배열 생성 (다국어 키 사용)
export function getRegionOptions() {
  // 전국을 제외한 지역들만 처리
  const regions = Object.entries(regionMapping)
    .filter(([value]) => value !== '전국')
    .map(([value, label]) => ({
      value,
      label,
      image: regionImages[value] || '/src/assets/regions/default.jpg'
    })).sort((a, b) => a.label.localeCompare(b.label, 'ko'));
  
  // 전국 옵션을 맨 앞에 추가
  return [
    { 
      value: '전국', 
      label: 'region_nationwide',
      image: regionImages['전국'] || '/src/assets/regions/nationwide.jpg'
    },
    ...regions
  ];
}

// 지역별 사용 가능한 카테고리 가져오기
export function getAvailableCategories(region) {
  return regionCategories[region] || [];
}

// 카테고리 표시명 가져오기
export function getCategoryLabel(category) {
  return categoryLabels[category] || category;
}

// 지역 설명 가져오기 (i18n 키 반환)
export function getRegionDescription(region) {
  return regionDescriptions[region] || '';
}
