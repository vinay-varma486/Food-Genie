export const LANGUAGES = [
  { code: 'en', label: 'English', native: 'English', flag: '🇬🇧' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు', flag: '🇮🇳' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்', flag: '🇮🇳' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' }
];

export const translations = {
  en: {
    brandName: "FoodGenie",
    tagline: "Your friendly AI nutrition companion",
    assistantName: "Genie",
    nav: {
      features: "Features",
      dietPlans: "Diet Plans",
      nearbyDoctors: "Nearby Doctors",
      dashboard: "Dashboard",
      signIn: "Sign In",
      profile: "Profile"
    },
    hero: {
      badge: "AI-Powered Nutrition Intelligence",
      heading: "Your health, your food, your way.",
      subtitle: "Meet Genie, your personal AI nutrition companion. Talk or type to discover personalized nutrition, meal plans, and expert food guidance.",
      tapToSpeak: "Tap orb or mic to talk with Genie",
      listening: "Genie is listening...",
      thinking: "Genie is preparing your recommendation...",
      speaking: "Genie is speaking...",
      stopListening: "Tap to stop listening",
      stopSpeaking: "Tap to stop audio"
    },
    queryBox: {
      placeholder: "Ask Genie anything about food and nutrition...",
      send: "Send",
      micTooltip: "Use Voice",
      clearTooltip: "Clear"
    },
    suggested: {
      title: "Popular Genie Prompts",
      items: [
        { label: "Foods for hair health", query: "What are the best foods for hair health and growth?" },
        { label: "Iron-rich foods", query: "Give me a list of vegetarian and non-vegetarian iron-rich foods." },
        { label: "Vitamin B12 foods", query: "Which foods provide high Vitamin B12, especially for vegetarians?" },
        { label: "Protein-rich foods", query: "What are the best high-protein food options for daily meals?" },
        { label: "Budget-friendly diet", query: "Can you create an affordable, healthy weekly meal plan on a budget?" },
        { label: "Foods to avoid & allergies", query: "What foods should I avoid with diabetes, thyroid, or medication interactions?" }
      ]
    },
    features: {
      sectionTitle: "Explore Intelligent Food Assistance",
      sectionSubtitle: "Designed to help you make smarter, budget-conscious and healthier culinary choices every day.",
      foodBenefits: {
        title: "Food Benefits",
        tag: "Nutritional Science",
        desc: "Instant breakdown of vitamins, minerals, antioxidants, and health impacts for any dish, vegetable, or ingredient."
      },
      foodRestrictions: {
        title: "Food Restrictions",
        tag: "Safety & Clinical",
        desc: "Personalized safeguards for food allergies, medical conditions (Diabetes, BP, Thyroid), and drug-food interactions with safe swaps."
      },
      budgetDiet: {
        title: "Budget Diet Planner",
        tag: "Cost-Optimized",
        desc: "Personalized daily, weekly, and monthly diet charts mapped to your exact budget and affordable local grocery markets."
      },
      nearbyDoctors: {
        title: "Find Nearby Doctors",
        tag: "Verified Directory",
        desc: "Locate certified nutritionists, dietitians, and wellness clinics around your location with live interactive mapping."
      },
      actionExplore: "Explore with Genie"
    },
    voiceStates: {
      idle: "Genie is ready. Click the orb or mic to speak.",
      listening: "Listening to your voice...",
      thinking: "Analyzing nutritional data...",
      speaking: "Sharing recommendation..."
    },
    footer: {
      disclaimer: "FoodGenie provides AI-assisted dietary suggestions. For medical advice, consult certified healthcare professionals.",
      copyright: "© 2026 FoodGenie. All rights reserved."
    }
  },
  te: {
    brandName: "FoodGenie",
    tagline: "మీ స్నేహపూర్వక AI పోషకాహార సహచరుడు",
    assistantName: "జీనీ (Genie)",
    nav: {
      features: "లక్షణాలు",
      dietPlans: "డైట్ ప్లాన్స్",
      nearbyDoctors: "సమీప వైద్యులు",
      dashboard: "డ్యాష్‌బోర్డ్",
      signIn: "లాగిన్",
      profile: "ప్రొఫైల్"
    },
    hero: {
      badge: "AI-ఆధారిత పోషకాహార మేధస్సు",
      heading: "మీ ఆరోగ్యం, మీ ఆహారం, మీ పద్ధతి.",
      subtitle: "మీ వ్యక్తిగత AI పోషకాహార సహచరుడైన జీనీని కలవండి. వ్యక్తిగతీకరించిన పోషకాహారం, భోజన ప్రణాళికలు మరియు ఆహార సలహాల కోసం మాట్లాడండి లేదా టైప్ చేయండి.",
      tapToSpeak: "జీనీతో మాట్లాడటానికి ఆర్బ్ లేదా మైక్‌ని నొక్కండి",
      listening: "జీనీ వింటోంది...",
      thinking: "జీనీ సమాధానం సిద్ధం చేస్తోంది...",
      speaking: "జీనీ మాట్లాడుతోంది...",
      stopListening: "ఆపడానికి నొక్కండి",
      stopSpeaking: "వాయిస్ ఆపడానికి నొక్కండి"
    },
    queryBox: {
      placeholder: "ఆహారం మరియు పోషకాల గురించి జీనీని ఏదైనా అడగండి...",
      send: "పంపండి",
      micTooltip: "వాయిస్ ఉపయోగించండి",
      clearTooltip: "క్లియర్ చేయండి"
    },
    suggested: {
      title: "తరచుగా అడిగే ప్రశ్నలు",
      items: [
        { label: "జుట్టు ఆరోగ్యానికి ఆహారాలు", query: "జుట్టు ఆరోగ్యానికి, ఒత్తుగా పెరగడానికి ఉత్తమ ఆహారాలు ఏమిటి?" },
        { label: "ఐరన్ సమృద్ధిగా ఉండే ఆహారాలు", query: "ఐరన్ ఎక్కువగా లభించే శాకాహార మరియు మాంసాహార ఆహారాల వివరాలు చెప్పండి." },
        { label: "విటమిన్ B12 ఆహారాలు", query: "విటమిన్ B12 అధికంగా లభించే ఆహారాలు ఏమిటి?" },
        { label: "ప్రోటీన్ సమృద్ధిగా ఉండే ఆహారాలు", query: "రోజూ సులభంగా తినదగిన అధిక ప్రోటీన్ ఆహారాలు ఏమిటి?" },
        { label: "బడ్జెట్-స్నేహపూర్వక డైట్", query: "తక్కువ ఖర్చుతో కూడిన ఆరోగ్యకరమైన వారపు భోజన ప్రణాళికను తయారు చేయండి." }
      ]
    },
    features: {
      sectionTitle: "మేధోపరమైన ఆహార సేవలను అన్వేషించండి",
      sectionSubtitle: "మీరు ప్రతిరోజూ బడ్జెట్ మరియు ఆరోగ్యాన్ని సమతుల్యం చేస్తూ ఉత్తమ ఆహారాన్ని ఎంచుకోవడంలో సహాయపడుతుంది.",
      foodBenefits: {
        title: "ఆహార ప్రయోజనాలు",
        tag: "పోషక విజ్ఞానం",
        desc: "ఏదైనా వంటకం లేదా కూరగాయలలోని విటమిన్లు, ఖనిజాలు మరియు ఆరోగ్య ప్రయోజనాలను తక్షణమే తెలుసుకోండి."
      },
      foodRestrictions: {
        title: "ఆహార పరిమితులు & రక్షణ",
        tag: "క్లినికల్ భద్రత",
        desc: "అలెర్జీలు, షుగర్, బీపీ, థైరాయిడ్ మరియు మందుల పరస్పర చర్యల కోసం వ్యక్తిగత ఆహార నియమాలు."
      },
      budgetDiet: {
        title: "బడ్జెట్ డైట్ ప్లానర్",
        tag: "ధర ఆదా",
        desc: "మీ నెలవారీ బడ్జెట్ మరియు స్థానిక కిరాణా ధరలకు సరిపోయే వ్యక్తిగత డైట్ చార్టులు."
      },
      nearbyDoctors: {
        title: "సమీప వైద్యులను కనుగొనండి",
        tag: "ధృవీకరించబడిన డైరెక్టరీ",
        desc: "మీ సమీపంలోని అర్హత కలిగిన డైటీషియన్లు మరియు న్యూట్రిషన్ క్లినిక్‌లను సులభంగా గుర్తించండి."
      },
      actionExplore: "జీనీతో ప్రారంభించండి"
    },
    voiceStates: {
      idle: "జీనీ సిద్ధంగా ఉంది. మాట్లాడటానికి మైక్ నొక్కండి.",
      listening: "మీ వాయిస్ వింటోంది...",
      thinking: "సమాచారాన్ని విశ్లేషిస్తోంది...",
      speaking: "సమాధానం చెబుతోంది..."
    },
    footer: {
      disclaimer: "ఫుడ్ జీనీ AI సలహాలు మాత్రమే ఇస్తుంది. వైద్య సలహా కోసం డాక్టర్లను సంప్రదించండి.",
      copyright: "© 2026 FoodGenie. సర్వహక్కులు ప్రత్యేకించబడ్డాయి."
    }
  },
  hi: {
    brandName: "FoodGenie",
    tagline: "आपका अपना AI पोषण साथी",
    assistantName: "जिनी (Genie)",
    nav: {
      features: "विशेषताएं",
      dietPlans: "डाइट प्लान",
      nearbyDoctors: "नजदीकी डॉक्टर्स",
      dashboard: "डैशबोर्ड",
      signIn: "लॉग इन",
      profile: "प्रोफाइल"
    },
    hero: {
      badge: "AI-संचालित पोषण बुद्धिमत्ता",
      heading: "आपकी सेहत, आपका खाना, आपकी पसंद।",
      subtitle: "मिलिए जिनी से, आपका व्यक्तिगत AI पोषण साथी। अपनी पसंदीदा भाषा में बोलकर या लिखकर पोषण, डाइट चार्ट और भोजन के लाभ जानें।",
      tapToSpeak: "जिनी से बात करने के लिए ऑर्ब या माइक छुएं",
      listening: "जिनी सुन रहा है...",
      thinking: "जिनी विश्लेषण कर रहा है...",
      speaking: "जिनी बोल रहा है...",
      stopListening: "रोकने के लिए टैप करें",
      stopSpeaking: "ऑडियो बंद करें"
    },
    queryBox: {
      placeholder: "खान-पान और पोषण के बारे में जिनी से कुछ भी पूछें...",
      send: "भेजें",
      micTooltip: "वॉइस का प्रयोग करें",
      clearTooltip: "साफ़ करें"
    },
    suggested: {
      title: "सुझाए गए प्रश्न",
      items: [
        { label: "बालों के स्वास्थ्य के लिए भोजन", query: "बालों को स्वस्थ और मजबूत रखने के लिए कौन से खाद्य पदार्थ अच्छे हैं?" },
        { label: "आयरन से भरपूर खाद्य पदार्थ", query: "आयरन से भरपूर शाकाहारी और मांसाहारी खाद्य पदार्थों की सूची दें।" },
        { label: "विटामिन बी12 वाले खाद्य पदार्थ", query: "विटामिन बी12 की कमी पूरी करने वाले मुख्य भोजन कौन से हैं?" },
        { label: "प्रोटीन युक्त आहार", query: "दैनिक आहार में उच्च प्रोटीन के सस्ते और आसान विकल्प क्या हैं?" },
        { label: "बजट-अनुकूल संतुलित आहार", query: "कम बजट में संपूर्ण और स्वस्थ साप्ताहिक डाइट प्लान बनाएं।" }
      ]
    },
    features: {
      sectionTitle: "स्मार्ट पोषण सुविधाओं को जानें",
      sectionSubtitle: "हर दिन स्वस्थ और बजट-अनुकूल भोजन विकल्प चुनने में जिनी आपकी मदद करता है।",
      foodBenefits: {
        title: "भोजन के लाभ",
        tag: "पोषण विज्ञान",
        desc: "किसी भी व्यंजन, फल या सब्जी में मौजूद विटामिन, मिनरल्स और स्वास्थ्य लाभों का तुरंत विश्लेषण।"
      },
      foodRestrictions: {
        title: "आहार प्रतिबंध और सुरक्षा",
        tag: "क्लिनिकल सुरक्षा",
        desc: "एलर्जी, मधुमेह, बीपी, थायराइड और दवाओं के साथ भोजन के सुरक्षित विकल्प और सख्त नियम।"
      },
      budgetDiet: {
        title: "बजट डाइट प्लानर",
        tag: "लागत-अनुकूलित",
        desc: "आपके मासिक बजट और नजदीकी किफायती किराना सामान के अनुसार तैयार किए गए डाइट चार्ट।"
      },
      nearbyDoctors: {
        title: "नजदीकी डॉक्टर खोजें",
        tag: "सत्यापित डायरेक्टरी",
        desc: "अपने आसपास प्रमाणित डाइटिशियन, न्यूट्रिशनिस्ट और क्लिनिक तुरंत खोजें।"
      },
      actionExplore: "जिनी के साथ देखें"
    },
    voiceStates: {
      idle: "जिनी तैयार है। बोलने के लिए ऑर्ब या माइक दबाएं।",
      listening: "आपकी आवाज़ सुनी जा रही है...",
      thinking: "पोषण डेटा का विश्लेषण जारी है...",
      speaking: "जिनी जानकारी दे रहा है..."
    },
    footer: {
      disclaimer: "FoodGenie केवल AI-आधारित पोषण मार्गदर्शन देता है। चिकित्सकीय सलाह के लिए डॉक्टर से संपर्क करें।",
      copyright: "© 2026 FoodGenie. सर्वाधिकार सुरक्षित।"
    }
  },
  ta: {
    brandName: "FoodGenie",
    tagline: "உங்கள் அன்பான AI ஊட்டச்சத்து தோழன்",
    assistantName: "ஜீனி (Genie)",
    nav: {
      features: "அம்சங்கள்",
      dietPlans: "உணவு திட்டங்கள்",
      nearbyDoctors: "அருகிலுள்ள மருத்துவர்கள்",
      dashboard: "டாஷ்போர்டு",
      signIn: "உள்நுழை",
      profile: "சுயவிவரம்"
    },
    hero: {
      badge: "AI-இயங்கும் ஊட்டச்சத்து நுண்ணறிவு",
      heading: "உங்கள் ஆரோக்கியம், உங்கள் உணவு, உங்கள் விருப்பம்.",
      subtitle: "ஜீனியை சந்திக்கவும். உங்களின் தனிப்பயனாக்கப்பட்ட ஊட்டச்சத்து ஆலோசகர்.",
      tapToSpeak: "பேச மைக் அல்லது ஆர்ப் அழுத்தவும்",
      listening: "ஜீனி கேட்கிறது...",
      thinking: "பதிலை தயாரிக்கிறது...",
      speaking: "ஜீனி பேசுகிறது...",
      stopListening: "நிறுத்த தட்டவும்",
      stopSpeaking: "ஆடியோவை நிறுத்தவும்"
    },
    queryBox: {
      placeholder: "உணவு மற்றும் சத்துக்கள் பற்றி ஜீனியிடம் கேளுங்கள்...",
      send: "அனுப்பு",
      micTooltip: "குரல் பயன்படுத்தவும்",
      clearTooltip: "அழிக்க"
    },
    suggested: {
      title: "பிரபலமான கேள்விகள்",
      items: [
        { label: "கூந்தல் ஆரோக்கியத்திற்கான உணவு", query: "கூந்தல் வளர்ச்சிக்கு சிறந்த உணவுகள் எவை?" },
        { label: "இரும்புச்சத்து நிறைந்த உணவுகள்", query: "இரும்புச்சத்து அதிகம் உள்ள உணவுகள் எவை?" },
        { label: "வைட்டமின் B12 உணவுகள்", query: "வைட்டமின் B12 நிறைந்த உணவுகள் பட்டியல் கொடுங்கள்." },
        { label: "புரதம் நிறைந்த உணவுகள்", query: "அதிக புரதம் கொண்ட உணவுகள் எவை?" },
        { label: "குறைந்த பட்ஜெட் உணவு திட்டம்", query: "குறைந்த பட்ஜெட்டில் ஆரோக்கியமான உணவு அட்டவணை தாருங்கள்." }
      ]
    },
    features: {
      sectionTitle: "சிறந்த ஊட்டச்சத்து சேவைகள்",
      sectionSubtitle: "ஒவ்வொரு நாளும் ஆரோக்கியமான மற்றும் பட்ஜெட் உணவுகளைத் தேர்ந்தெடுக்க ஜீனி உதவும்.",
      foodBenefits: {
        title: "உணவு நன்மைகள்",
        tag: "ஊட்டச்சத்து அறிவியல்",
        desc: "உணவுகளில் உள்ள வைட்டமின்கள் மற்றும் ஊட்டச்சத்து பலன்களை உடனே அறியுங்கள்."
      },
      budgetDiet: {
        title: "பட்ஜெட் டயட் திட்டம்",
        tag: "விலை சிக்கனம்",
        desc: "உங்கள் பட்ஜெட்டுக்கு ஏற்றவாறு ஆரோக்கியமான உணவு அட்டவணைகள்."
      },
      nearbyDoctors: {
        title: "அருகிலுள்ள மருத்துவர்கள்",
        tag: "சரிபார்க்கப்பட்ட பட்டியல்",
        desc: "உங்களுக்கு அருகிலுள்ள சிறந்த ஊட்டச்சத்து மருத்துவர்களை கண்டறியுங்கள்."
      },
      actionExplore: "ஆராயுங்கள்"
    },
    voiceStates: {
      idle: "ஜீனி தயாராக உள்ளது.",
      listening: "கேட்கிறது...",
      thinking: "சிந்திக்கிறது...",
      speaking: "பேசுகிறது..."
    },
    footer: {
      disclaimer: "மருத்துவ ஆலோசனைக்கு உங்கள் மருத்துவரை அணுகவும்.",
      copyright: "© 2026 FoodGenie. அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை."
    }
  },
  kn: {
    brandName: "FoodGenie",
    tagline: "ನಿಮ್ಮ AI ಪೋಷಕಾಂಶ ಒಡನಾಡಿ",
    assistantName: "ಜೀನಿ (Genie)",
    nav: {
      features: "ವೈಶಿಷ್ಟ್ಯಗಳು",
      dietPlans: "ಡಯಟ್ ಪ್ಲಾನ್",
      nearbyDoctors: "ಹತ್ತಿರದ ವೈದ್ಯರು",
      dashboard: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
      signIn: "ಸೈನ್ ಇನ್",
      profile: "ಪ್ರೊಫೈಲ್"
    },
    hero: {
      badge: "AI-ಆಧಾರಿತ ಪೋಷಕಾಂಶ ಮಾರ್ಗದರ್ಶಿ",
      heading: "ನಿಮ್ಮ ಆರೋಗ್ಯ, ನಿಮ್ಮ ಆಹಾರ, ನಿಮ್ಮ ದಾರಿ.",
      subtitle: "ನಿಮ್ಮ ವೈಯಕ್ತಿಕ AI ಪೌಷ್ಟಿಕಾಂಶ ಸಹಾಯಕ ಜೀನಿಯನ್ನು ಭೇಟಿ ಮಾಡಿ.",
      tapToSpeak: "ಮಾತನಾಡಲು ಮೈಕ್ ಒತ್ತಿರಿ",
      listening: "ಜೀನಿ ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದೆ...",
      thinking: "ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ...",
      speaking: "ಜೀನಿ ಮಾತನಾಡುತ್ತಿದೆ...",
      stopListening: "ನಿಲ್ಲಿಸಲು ಒತ್ತಿರಿ",
      stopSpeaking: "ಧ್ವನಿಯನ್ನು ನಿಲ್ಲಿಸಿ"
    },
    queryBox: {
      placeholder: "ಆಹಾರ ಮತ್ತು ಪೌಷ್ಟಿಕಾಂಶದ ಬಗ್ಗೆ ಜೀನಿಯನ್ನು ಏನಾದರೂ ಕೇಳಿ...",
      send: "ಕಳುಹಿಸಿ",
      micTooltip: "ಧ್ವನಿ ಬಳಸಿ",
      clearTooltip: "ತೆರವುಗೊಳಿಸಿ"
    },
    suggested: {
      title: "ಜನಪ್ರಿಯ ಪ್ರಶ್ನೆಗಳು",
      items: [
        { label: "ಕೂದಲಿನ ಆರೋಗ್ಯಕ್ಕಾಗಿ ಆಹಾರಗಳು", query: "ಕೂದಲಿನ ಬೆಳವಣಿಗೆಗೆ ಉತ್ತಮ ಆಹಾರಗಳು ಯಾವುವು?" },
        { label: "ಕಬ್ಬಿಣಾಂಶ ಭರಿತ ಆಹಾರಗಳು", query: "ಹೆಚ್ಚು ಕಬ್ಬಿಣಾಂಶ ಹೊಂದಿರುವ ಆಹಾರಗಳ ಪಟ್ಟಿ ನೀಡಿ." },
        { label: "ವಿಟಮಿನ್ B12 ಆಹಾರಗಳು", query: "ವಿಟಮಿನ್ B12 ಸಮೃದ್ಧವಾಗಿರುವ ಆಹಾರಗಳು ಯಾವುವು?" },
        { label: "ಪ್ರೋಟೀನ್ ಭರಿತ ಆಹಾರ", query: "ದೈನಂದಿನ ಅಧಿಕ ಪ್ರೋಟೀನ್ ಆಹಾರ ಆಯ್ಕೆಗಳು ಯಾವುವು?" },
        { label: "ಬಜೆಟ್ ಸ್ನೇಹಿ ಆಹಾರ ಯೋಜನೆ", query: "ಕಡಿಮೆ ವೆಚ್ಚದ ಆರೋಗ್ಯಕರ ಸಾಪ್ತಾಹಿಕ ಊಟದ ಯೋಜನೆಯನ್ನು ಮಾಡಿ." }
      ]
    },
    features: {
      sectionTitle: "ಬುದ್ಧಿವಂತ ಆಹಾರ ಸೇವೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",
      sectionSubtitle: "ಪ್ರತಿದಿನ ಬಜೆಟ್ ಮತ್ತು ಆರೋಗ್ಯವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಲು ಜೀನಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
      foodBenefits: {
        title: "ಆಹಾರದ ಪ್ರಯೋಜನಗಳು",
        tag: "ಪೌಷ್ಟಿಕಾಂಶ ವಿಜ್ಞಾನ",
        desc: "ಆಹಾರದಲ್ಲಿರುವ ವಿಟಮಿನ್ ಮತ್ತು ಖನಿಜಗಳ ವಿವರಗಳನ್ನು ತಕ್ಷಣ ತಿಳಿಯಿರಿ."
      },
      budgetDiet: {
        title: "ಬಜೆಟ್ ಡಯಟ್ ಪ್ಲಾನರ್",
        tag: "ವೆಚ್ಚ ಉಳಿತಾಯ",
        desc: "ನಿಮ್ಮ ಬಜೆಟ್‌ಗೆ ತಕ್ಕಂತೆ ಆರೋಗ್ಯಕರ ಡಯಟ್ ಚಾರ್ಟ್‌ಗಳು."
      },
      nearbyDoctors: {
        title: "ಹತ್ತಿರದ ವೈದ್ಯರನ್ನು ಹುಡುಕಿ",
        tag: "ಪರಿಶೀಲಿಸಿದ ಪಟ್ಟಿ",
        desc: "ನಿಮ್ಮ ಹತ್ತಿರದ ಪರಿಣಿತ ಪೌಷ್ಟಿಕತಜ್ಞರನ್ನು ಸುಲಭವಾಗಿ ಪತ್ತೆಹಚ್ಚಿ."
      },
      actionExplore: "ಪ್ರಾರಂಭಿಸಿ"
    },
    voiceStates: {
      idle: "ಜೀನಿ ಸಿದ್ಧವಾಗಿದೆ.",
      listening: "ಕೇಳುತ್ತಿದೆ...",
      thinking: "ಯೋಚಿಸುತ್ತಿದೆ...",
      speaking: "ಮಾತನಾಡುತ್ತಿದೆ..."
    },
    footer: {
      disclaimer: "ವೈದ್ಯಕೀಯ ಸಲಹೆಗಾಗಿ ದಯವಿಟ್ಟು ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
      copyright: "© 2026 FoodGenie. ಎಲ್ಲ ಹಕ್ಕುಗಳನ್ನು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ."
    }
  }
};

