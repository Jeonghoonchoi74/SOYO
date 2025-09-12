const questions = {
  pathConfig: {
    // Define total steps for each major path for the progress bar
    food_meal: 9,
    food_cafe: 8,
    food_pub: 8,
    event: 6,
    tourist_nature: 6,
    tourist_exhibition: 6,
    tourist_leports: 5,
    tourist_themepark: 7,
  },
  queryConfig: {
    // Config for making the query more natural
    suffixes: {
      who: {
        two: "guided_with_two",
        "3-4": "guided_with_group",
        group: "guided_group_suffix",
      },
      two_relation: {
        couple: "guided_with_couple",
        friend: "guided_with_friend",
        child: "guided_with_child",
        // '비즈니스'를 선택하면, 텍스트 전체를 '*비즈니스 파트너와'로 교체
        business: "*guided_business_partner",
      },
      small_group_relation: {
        family: "guided_with_family",
        friends: "guided_with_friends",
        // '비즈니스'를 선택하면, 텍스트 전체를 '*직장 동료와'로 교체
        business: "*guided_colleague",
      },
    },
    // If a key exists, its value (parent) should be excluded from the query
    redundancyMap: {
      two_relation: "who",
      small_group_relation: "who",
      group_type: "who",
    },
  },
  steps: {
    1: {
      id: "who",
      text: "guided_who",
      options: [
        { value: "alone", text: "guided_alone", icon: "👤", nextStep: 2 },
        { value: "two", text: "guided_two", icon: "🧑‍🤝‍🧑", nextStep: "1a" },
        { value: "3-4", text: "guided_3_4", icon: "👨‍👩‍👧", nextStep: "1b" },
        { value: "group", text: "guided_group", icon: "🏢", nextStep: "1c" },
      ],
    },
    "1a": {
      id: "two_relation",
      text: "guided_relation",
      options: [
        { value: "couple", text: "guided_couple", icon: "❤️", nextStep: 2 },
        { value: "friend", text: "guided_friend", icon: "😊", nextStep: 2 },
        { value: "child", text: "guided_child", icon: "👶", nextStep: 2 },
        { value: "business", text: "guided_business", icon: "💼", nextStep: 2 },
      ],
    },
    "1b": {
      id: "small_group_relation",
      text: "guided_relation",
      options: [
        { value: "family", text: "guided_family", icon: "👨‍👩‍👧‍👦", nextStep: 2 },
        { value: "friends", text: "guided_friend", icon: "😊", nextStep: 2 },
        { value: "business", text: "guided_business", icon: "💼", nextStep: 2 },
      ],
    },
    "1c": {
      id: "group_type",
      text: "guided_group_type",
      options: [
        { value: "club", text: "guided_club", icon: "🎨", nextStep: 2 },
        {
          value: "friends_gathering",
          text: "guided_friends_gathering",
          icon: "🎉",
          nextStep: 2,
        },
        { value: "field_trip", text: "guided_field_trip", icon: "🚌", nextStep: 2 },
        {
          value: "business_group",
          text: "guided_business_group",
          icon: "💼",
          nextStep: 2,
        },
      ],
    },
    2: {
      id: "category",
      text: "guided_what",
      options: [
        { value: "foods", text: "guided_foods", icon: "🍔", nextStep: 3, path: "food" },
        {
          value: "events",
          text: "guided_events",
          icon: "🎉",
          nextStep: 100,
          path: "event",
        },
        {
          value: "tourist attraction",
          text: "guided_tourist_attraction",
          icon: "🏞️",
          nextStep: 200,
          path: "tourist",
        },
      ],
    },
    3: {
      id: "food_consideration",
      text: "guided_food_consideration",
      options: [
        {
          value: "value_for_money",
          text: "guided_value_for_money",
          icon: "💰",
          nextStep: 4,
        },
        {
          value: "guaranteed_taste",
          text: "guided_guaranteed_taste",
          icon: "👍",
          nextStep: 4,
        },
        {
          value: "unique_menu",
          text: "guided_unique_menu",
          icon: "✨",
          nextStep: 4,
        },
      ],
    },
    4: {
      id: "food_type",
      text: "guided_food_type",
      options: [
        {
          value: "meal",
          text: "guided_meal",
          icon: "🍚",
          nextStep: 5,
          subPath: "_meal",
        },
        {
          value: "cafe",
          text: "guided_cafe",
          icon: "☕",
          nextStep: 20,
          subPath: "_cafe",
        },
        {
          value: "pub",
          text: "guided_pub",
          icon: "🍻",
          nextStep: 30,
          subPath: "_pub",
        },
      ],
    },
    5: {
      id: "meal_cuisine",
      text: "guided_meal_cuisine",
      options: [
        { value: "korean", text: "guided_korean", nextStep: 6 },
        { value: "japanese", text: "guided_japanese", nextStep: 6 },
        { value: "chinese", text: "guided_chinese", nextStep: 6 },
        { value: "western", text: "guided_western", nextStep: 6 },
        { value: "asian", text: "guided_asian", nextStep: 6 },
        { value: "other_cuisine", text: "guided_other_cuisine", nextStep: 6 },
      ],
    },
    6: {
      id: "meal_dish_type",
      text: "guided_meal_dish_type",
      options: [
        { value: "meat", text: "guided_meat", nextStep: 7 },
        { value: "seafood", text: "guided_seafood", nextStep: 7 },
        { value: "soup", text: "guided_soup", nextStep: 7 },
        { value: "noodles", text: "guided_noodles", nextStep: 7 },
        { value: "vegetarian", text: "guided_vegetarian", nextStep: 7 },
      ],
    },
    7: {
      id: "meal_time",
      text: "guided_meal_time",
      options: [
        { value: "breakfast", text: "guided_breakfast", nextStep: 998 },
        { value: "lunch", text: "guided_lunch", nextStep: 998 },
        { value: "dinner", text: "guided_dinner", nextStep: 998 },
        { value: "late_night", text: "guided_late_night", nextStep: 998 },
      ],
    },
    8: {
      id: "meal_atmosphere",
      text: "guided_meal_atmosphere",
      options: [
        { value: "value", text: "guided_value", nextStep: 998 },
        { value: "tasty", text: "guided_tasty", nextStep: 998 },
        { value: "unique", text: "guided_unique", nextStep: 998 },
      ],
    },
    20: {
      id: "cafe_type",
      text: "guided_cafe_type",
      options: [
        { value: "coffee_specialist", text: "guided_coffee_specialist", nextStep: 22 },
        { value: "dessert_specialist", text: "guided_dessert_specialist", nextStep: 22 },
        { value: "bakery_cafe", text: "guided_bakery_cafe", nextStep: 22 },
        { value: "tea_house", text: "guided_tea_house", nextStep: 22 },
      ],
    },
    22: {
      id: "cafe_atmosphere",
      text: "guided_cafe_atmosphere",
      options: [
        { value: "photo_worthy", text: "guided_photo_worthy", nextStep: 998 },
        { value: "good_view", text: "guided_good_view", nextStep: 998 },
        { value: "good_music", text: "guided_good_music", nextStep: 998 },
        { value: "quiet", text: "guided_quiet", nextStep: 998 },
        { value: "themed", text: "guided_themed", nextStep: 998 },
        { value: "large", text: "guided_large", nextStep: 998 },
      ],
    },
    30: {
      id: "pub_type",
      text: "guided_pub_type",
      options: [
        { value: "traditional_pub", text: "guided_traditional_pub", nextStep: 31 },
        { value: "craft_beer", text: "guided_craft_beer", nextStep: 31 },
        { value: "wine_bar", text: "guided_wine_bar", nextStep: 31 },
        { value: "cocktail_bar", text: "guided_cocktail_bar", nextStep: 31 },
        { value: "izakaya", text: "guided_izakaya", nextStep: 31 },
        { value: "hof_soju", text: "guided_hof_soju", nextStep: 31 },
      ],
    },
    31: {
      id: "pub_food",
      text: "guided_pub_food",
      options: [
        { value: "western_food", text: "guided_western_food", nextStep: 32 },
        { value: "korean_food", text: "guided_korean_food", nextStep: 32 },
        { value: "japanese_food", text: "guided_japanese_food", nextStep: 32 },
        { value: "simple_anju", text: "guided_simple_anju", nextStep: 32 },
        { value: "fusion_anju", text: "guided_fusion_anju", nextStep: 32 },
      ],
    },
    32: {
      id: "pub_atmosphere",
      text: "guided_pub_atmosphere",
      options: [
        {
          value: "photo_worthy",
          text: "guided_pub_photo_worthy",
          nextStep: 998,
        },
        { value: "good_view", text: "guided_pub_good_view", nextStep: 998 },
        { value: "good_music", text: "guided_good_music", nextStep: 998 },
        {
          value: "private_room",
          text: "guided_private_room",
          nextStep: 998,
        },
      ],
    },
    100: {
      id: "event_location",
      text: "guided_event_location",
      options: [
        { value: "indoor", text: "guided_indoor", nextStep: 101 },
        { value: "outdoor", text: "guided_outdoor", nextStep: 101 },
      ],
    },
    101: {
      id: "event_type",
      text: "guided_event_type",
      options: [
        { value: "performance", text: "guided_performance", nextStep: 102 },
        { value: "festival", text: "guided_festival", nextStep: 102 },
        { value: "exhibition", text: "guided_exhibition", nextStep: 102 },
        { value: "tour", text: "guided_tour", nextStep: 102 },
        { value: "class", text: "guided_class", nextStep: 102 },
      ],
    },
    102: {
      id: "event_atmosphere",
      text: "guided_event_atmosphere",
      options: [
        { value: "crowded", text: "guided_crowded", nextStep: 998 },
        { value: "calm", text: "guided_calm", nextStep: 998 },
        { value: "photo_worthy", text: "guided_photo_worthy", nextStep: 998 },
        { value: "any", text: "guided_any", nextStep: 998 },
      ],
    },
    200: {
      id: "spot_type",
      text: "guided_spot_type",
      options: [
        {
          value: "nature",
          text: "guided_nature",
          nextStep: 201,
          subPath: "_nature",
        },
        {
          value: "exhibition",
          text: "guided_exhibition",
          nextStep: 210,
          subPath: "_exhibition",
        },
        {
          value: "leports",
          text: "guided_leports",
          nextStep: 220,
          subPath: "_leports",
        },
        {
          value: "themepark",
          text: "guided_themepark",
          nextStep: 230,
          subPath: "_themepark",
        },
      ],
    },
    201: {
      id: "nature_type",
      text: "guided_nature_type",
      options: [
        { value: "mountain", text: "guided_mountain", nextStep: 202 },
        { value: "sea", text: "guided_sea", nextStep: 203 },
        { value: "camping", text: "guided_camping", nextStep: 204 },
        { value: "river", text: "guided_river", nextStep: 205 },
      ],
    },
    202: {
      id: "mountain_activity",
      text: "guided_mountain_activity",
      options: [
        { value: "hiking", text: "guided_hiking", nextStep: 998 },
        { value: "park_viewing", text: "guided_park_viewing", nextStep: 998 },
        { value: "city_park", text: "guided_city_park", nextStep: 998 },
        { value: "valley", text: "guided_valley", nextStep: 998 },
      ],
    },
    203: {
      id: "sea_activity",
      text: "guided_sea_activity",
      options: [
        { value: "walk_drive", text: "guided_walk_drive", nextStep: 998 },
        {
          value: "marine_sports",
          text: "guided_marine_sports",
          nextStep: 998,
        },
        { value: "sunrise_night", text: "guided_sunrise_night", nextStep: 998 },
      ],
    },
    204: {
      id: "camping_style",
      text: "guided_camping_style",
      options: [
        { value: "campground", text: "guided_campground", nextStep: 998 },
        { value: "glamping", text: "guided_glamping", nextStep: 998 },
      ],
    },
    205: {
      id: "river_activity",
      text: "guided_river_activity",
      options: [
        { value: "water_play", text: "guided_water_play", nextStep: 998 },
        { value: "walk_bike", text: "guided_walk_bike", nextStep: 998 },
        { value: "scenery", text: "guided_scenery", nextStep: 998 },
      ],
    },
    210: {
      id: "exhibition_type",
      text: "guided_exhibition_type",
      options: [
        { value: "museum", text: "guided_museum", nextStep: 211 },
        { value: "art_gallery", text: "guided_art_gallery", nextStep: 212 },
        { value: "palace", text: "guided_palace", nextStep: 998 },
        { value: "hanok_village", text: "guided_hanok_village", nextStep: 998 },
      ],
    },
    211: {
      id: "museum_subject",
      text: "guided_museum_subject",
      options: [
        { value: "history", text: "guided_history", nextStep: 998 },
        { value: "science", text: "guided_science", nextStep: 998 },
        { value: "person", text: "guided_person", nextStep: 998 },
        { value: "art_culture", text: "guided_art_culture", nextStep: 998 },
      ],
    },
    212: {
      id: "gallery_type",
      text: "guided_gallery_type",
      options: [
        { value: "classic_art", text: "guided_classic_art", nextStep: 998 },
        { value: "modern_art", text: "guided_modern_art", nextStep: 998 },
        { value: "photo_design", text: "guided_photo_design", nextStep: 998 },
      ],
    },
    220: {
      id: "leports_type",
      text: "guided_leports_type",
      options: [
        { value: "water", text: "guided_water", nextStep: 998 },
        { value: "land", text: "guided_land", nextStep: 998 },
        { value: "winter", text: "guided_winter", nextStep: 998 },
        { value: "air", text: "guided_air", nextStep: 998 },
      ],
    },
    230: {
      id: "themepark_location",
      text: "guided_themepark_location",
      options: [
        { value: "indoor", text: "guided_indoor", nextStep: 231 },
        { value: "outdoor", text: "guided_outdoor", nextStep: 231 },
      ],
    },
    231: {
      id: "themepark_type",
      text: "guided_themepark_type",
      options: [
        {
          value: "themepark_amusement",
          text: "guided_themepark_amusement",
          nextStep: 998,
        },
        { value: "aquarium_zoo", text: "guided_aquarium_zoo", nextStep: 998 },
        { value: "observatory", text: "guided_observatory", nextStep: 998 },
        {
          value: "shopping_mall",
          text: "guided_shopping_mall",
          nextStep: 232,
        },
        { value: "waterpark", text: "guided_waterpark", nextStep: 998 },
      ],
    },
    232: {
      id: "mall_purpose",
      text: "guided_mall_purpose",
      options: [
        { value: "shopping", text: "guided_shopping", nextStep: 998 },
        { value: "food", text: "guided_food", nextStep: 998 },
        { value: "events", text: "guided_events", nextStep: 998 },
      ],
    },
    998: {
      id: "region",
      text: "guided_region",
      isRegion: true,
      nextStep: 999,
    },
    999: {
      id: "confirmation",
      text: "guided_final_confirm",
      isConfirmation: true,
    },
  },
};
export default questions;
