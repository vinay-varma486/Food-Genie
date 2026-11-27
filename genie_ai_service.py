import json
import logging
import re
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from language_detector import language_detector
from nutrition_service import nutrition_rag
from crud_chat import record_chat_message, get_chat_history
from crud_diet import record_recommendation
from model_user import User
from schema_recommendation import (
    RecommendationResponse, RecommendedFoodItem, AvoidFoodItem, FoodRestrictionItem
)
from restriction_service import restriction_service
from openrouter_service import openrouter_service
from gemini_service import gemini_service
from config import settings

logger = logging.getLogger("genie_ai")

# Friendly localized fallback responses & labels when Gemini API is unreachable
GENIE_PERSONA = {
    "en": {
        "friend": "Friend",
        "greeting_template": "Hi {name}! 😊 How are you doing today? I'm Genie, your FoodGenie assistant. How can I help you?",
        "status": "I'm doing great, thank you for asking! How can I help you with your food and nutrition today?",
        "activity": "I'm here to help you with healthy food choices and nutrition! What would you like to know?",
        "thanks": "You're very welcome! 😊 Let me know anytime you need help with meals or nutrition.",
        "goodbye": "Take care! Have a wonderful and healthy day! 👋",
        "identity": "Hi {name}! I'm Genie, your personal FoodGenie nutrition assistant. Ask me about healthy meals, nutrients, budget plans, or foods tailored to your goals!",
        "goal_gain_missing": "That's great! Let's create a healthy weight-gain plan. Could you tell me your age, current weight, and height?",
        "goal_loss_missing": "That's a great decision! Let's create a balanced, filling weight-loss plan. Could you tell me your age, current weight, and height?",
        "goal_maintain_missing": "Maintaining your weight is a great goal! To personalize your daily balance, could you share your age, current weight, and height?",
        "goal_gain_ready": "Here is a healthy, calorie- and protein-dense weight-gain meal plan tailored to your details with estimated nutritional values and costs.",
        "goal_loss_ready": "Here is a satisfying, high-fiber, protein-rich weight-loss meal plan tailored to your details with estimated nutritional values and costs.",
        "goal_maintain_ready": "Here is a balanced weight-maintenance meal plan organized across all five daily meals with estimated nutritional values.",
        "breakfast_intro": "Here are some healthy breakfast options with their estimated nutritional benefits, quantities, and approximate costs:",
        "budget_advice": "Eating nutritious meals on a budget is totally doable! Would you like me to build a daily, weekly, or monthly plan? Just tell me your budget in ₹ (for example, ₹1,000 per week) and your dietary preference.",
        "doctor_advice": "For clinical diagnosis or medical care, consulting a qualified specialist is always best. You can open Nearby Doctors from the More menu to view clinics and directions.",
        "unrelated": "I'm Genie, your FoodGenie nutrition assistant! I'm best at helping with healthy foods, meal ideas, nutrition breakdowns, and budget meal plans. What food or health goal can I help you with?",
        "hair_intro": "I can help you explore nutrition that supports healthy hair—focusing on protein, iron, zinc, biotin, and omega-3 fatty acids.",
        "skin_intro": "Here are wholesome foods rich in Vitamin C, Vitamin E, zinc, and antioxidants that support healthy skin:",
        "iron_intro": "Here are iron-rich foods along with their estimated nutritional values and preparation tips to boost absorption:",
        "b12_intro": "Vitamin B12 supports nerve function and red blood cell production. Here are reliable dietary sources:",
        "vitaminc_intro": "Vitamin C supports immunity, collagen formation, and plant iron absorption. Here are top wholefood sources:",
        "vitamina_intro": "Vitamin A and beta-carotene support vision and skin renewal. Here are top wholefood sources:",
        "protein_intro": "Here are wholesome protein-rich foods with estimated quantities, nutritional breakdown, and approximate prices:",
        "calcium_intro": "Calcium supports strong bones and teeth. Here are nutrient-dense wholefood sources:",
        "budget_intro": "Here are affordable, locally available nutritious foods with estimated costs and nutritional profiles:",
        "general_intro": "Here are nutritious wholefood options benchmarked against ICMR-NIN and USDA data (values and prices are estimates):",
    },
    "te": {
        "friend": "మిత్రమా",
        "greeting_template": "హాయ్ {name}! 😊 ఈ రోజు మీరు ఎలా ఉన్నారు? నేను జీనీ (Genie), మీ FoodGenie సహాయకుడిని. మీకు ఎలా సహాయం చేయగలను?",
        "status": "నేను చాలా బాగున్నాను! ఈ రోజు మీ ఆరోగ్యం మరియు ఆహారం విషయంలో నేను ఎలా సహాయపడగలను?",
        "activity": "ఆరోగ్యకరమైన ఆహార ఎంపికలు మరియు పోషకాహారంతో మీకు సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను! మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
        "thanks": "మీకు ఎల్లప్పుడూ స్వాగతం! 😊 భోజనం లేదా పోషకాహారం గురించి ఎప్పుడైనా అడగండి.",
        "goodbye": "జాగ్రత్తగా ఉండండి! మీకు శుభదినం కావాలి! 👋",
        "identity": "హలో {name}! నేను జీనీ, మీ వ్యక్తిగత FoodGenie పోషకాహార సహాయకుడిని.",
        "goal_gain_missing": "చాలా మంచి నిర్ణయం! ఆరోగ్యకరమైన బరువు పెరుగుదల ప్రణాళిక తయారు చేద్దాం. దయచేసి మీ వయస్సు, ప్రస్తుత బరువు మరియు ఎత్తు చెప్పగలరా?",
        "goal_loss_missing": "ఆరోగ్యకరమైన బరువు తగ్గించే ప్రణాళిక చేద్దాం! మీ వయస్సు, ప్రస్తుత బరువు మరియు ఎత్తు చెప్పగలరా?",
        "goal_maintain_missing": "బరువును స్థిరంగా ఉంచుకోవడం గొప్ప లక్ష్యం! దయచేసి మీ వయస్సు, ప్రస్తుత బరువు మరియు ఎత్తు తెలియజేయగలరా?",
        "goal_gain_ready": "మీ వివరాల ఆధారంగా ఆరోగ్యకరమైన బరువు పెరుగుదల ఆహార ప్రణాళిక మరియు అంచనా పోషక విలువలు ఇవిగో:",
        "goal_loss_ready": "మీ వివరాల ఆధారంగా అధిక ప్రోటీన్ మరియు పీచు పదార్థాలతో కూడిన బరువు తగ్గే ఆహార ప్రణాళిక ఇవిగో:",
        "goal_maintain_ready": "మీ కోసం సమతుల్య బరువు నిర్వహణ ఆహార ప్రణాళిక మరియు అంచనా పోషక విలువలు ఇవిగో:",
        "breakfast_intro": "ఆరోగ్యకరమైన అల్పాహార (Breakfast) ఎంపికలు మరియు వాటి అంచనా పోషక ప్రయోజనాలు ఇవిగో:",
        "budget_advice": "తక్కువ బడ్జెట్‌లో ఆరోగ్యకరమైన భోజనం సులభంగా ప్లాన్ చేయవచ్చు! మీ రోజువారీ, వారపు లేదా నెలవారీ బడ్జెట్ (₹) చెప్పండి.",
        "doctor_advice": "వైద్య సలహా కోసం More మెనూలోని 'Nearby Doctors' ద్వారా సమీప వైద్యులను చూడవచ్చు.",
        "unrelated": "నేను మీ FoodGenie పోషకాహార సహాయకుడిని! ఆరోగ్యకరమైన ఆహారం, డైట్ ప్లాన్ మరియు బడ్జెట్ భోజనం గురించి అడగండి.",
        "hair_intro": "జుట్టు ఆరోగ్యానికి ప్రోటీన్, ఐరన్, జింక్ మరియు ఒమేగా-3 ఉన్న ఆహారాలు సహాయపడతాయి:",
        "skin_intro": "ఆరోగ్యకరమైన చర్మానికి విటమిన్ సి, విటమిన్ ఇ మరియు యాంటీఆక్సిడెంట్లు ఉండే ఆహారాలు ఇవిగో:",
        "iron_intro": "ఐరన్ సమృద్ధిగా ఉండే ఆహారాలు మరియు వాటి అంచనా పోషక విలువలు ఇవిగో:",
        "b12_intro": "విటమిన్ B12 నరాల ఆరోగ్యం మరియు రక్త కణాలకు చాలా అవసరం. సహజ వనరులు ఇవిగో:",
        "vitaminc_intro": "విటమిన్ సి రోగనిరోధక శక్తికి మరియు ఐరన్ శోషణకు ఎంతో సహాయపడుతుంది:",
        "vitamina_intro": "కంటి చూపు మరియు చర్మ ఆరోగ్యానికి విటమిన్ ఎ ఆహారాలు ఇవిగో:",
        "protein_intro": "శరీర బలానికి మరియు కండరాల ఆరోగ్యానికి మంచి ప్రోటీన్ ఆహారాలు ఇవిగో:",
        "calcium_intro": "ఎముకలు మరియు దంతాల దృఢత్వానికి క్యాల్షియం ఆహారాలు ఇవిగో:",
        "budget_intro": "తక్కువ ఖర్చులో పోషక విలువలున్న స్థానిక ఆహారాలు ఇవిగో:",
        "general_intro": "ICMR-NIN మరియు USDA ప్రమాణాల ఆధారంగా ఆరోగ్యకరమైన ఆహారాలు (అంచనా విలువలు):",
    },
    "hi": {
        "friend": "दोस्त",
        "greeting_template": "नमस्ते {name}! 😊 आप आज कैसे हैं? मैं जिनी (Genie) हूँ, आपका FoodGenie सहायक। मैं आपकी क्या मदद कर सकता हूँ?",
        "status": "मैं बिल्कुल ठीक हूँ, पूछने के लिए धन्यवाद! आज मैं आपके खान-पान और सेहत में क्या मदद कर सकता हूँ?",
        "activity": "मैं यहाँ आपकी स्वस्थ भोजन और पोषण चुनने में मदद करने के लिए हूँ! आप क्या जानना चाहेंगे?",
        "thanks": "आपका हमेशा स्वागत है! 😊 भोजन या पोषण से जुड़ा कोई भी सवाल कभी भी पूछें।",
        "goodbye": "अपना ध्यान रखें! आपका दिन शुभ और स्वस्थ हो! 👋",
        "identity": "नमस्ते {name}! मैं जिनी हूँ, आपका FoodGenie पोषण सहायक।",
        "goal_gain_missing": "बहुत बढ़िया! आइए स्वस्थ तरीके से वजन बढ़ाने की योजना बनाते हैं। कृपया अपनी उम्र, वर्तमान वजन और लंबाई बताएं?",
        "goal_loss_missing": "बहुत अच्छा लक्ष्य है! आइए संतुलित वजन घटाने की योजना बनाते हैं। कृपया अपनी उम्र, वर्तमान वजन और लंबाई बताएं?",
        "goal_maintain_missing": "वजन संतुलित रखना शानदार लक्ष्य है! कृपया अपनी उम्र, वर्तमान वजन और लंबाई बताएं?",
        "goal_gain_ready": "आपकी जानकारी के आधार पर स्वस्थ वजन बढ़ाने का संतुलित आहार चार्ट और अनुमानित पोषण मूल्य यहाँ हैं:",
        "goal_loss_ready": "आपकी जानकारी के आधार पर हाई-फाइबर और प्रोटीन युक्त वजन घटाने का आहार चार्ट यहाँ है:",
        "goal_maintain_ready": "आपके लिए संतुलित वजन बनाए रखने का दैनिक आहार चार्ट और अनुमानित पोषण मूल्य यहाँ हैं:",
        "breakfast_intro": "यहाँ कुछ स्वस्थ नाश्ते (Breakfast) के विकल्प और उनके अनुमानित पोषण लाभ दिए गए हैं:",
        "budget_advice": "कम बजट में पौष्टिक भोजन आसानी से बन सकता है! कृपया अपना दैनिक, साप्ताहिक या मासिक बजट (₹ में) बताएं।",
        "doctor_advice": "विस्तृत चिकित्सीय सलाह के लिए आप More मेनू में 'Nearby Doctors' देख सकते हैं।",
        "unrelated": "मैं जिनी हूँ, आपका FoodGenie पोषण सहायक! आप मुझसे स्वस्थ भोजन, डाइट प्लान या बजट प्लान के बारे में पूछ सकते हैं।",
        "hair_intro": "बालों के स्वास्थ्य के लिए प्रोटीन, आयरन, जिंक और ओमेगा-3 युक्त खाद्य पदार्थ लाभकारी हैं:",
        "skin_intro": "स्वस्थ त्वचा के लिए विटामिन सी, विटामिन ई और एंटीऑक्सीडेंट युक्त खाद्य पदार्थ यहाँ हैं:",
        "iron_intro": "आयरन से भरपूर खाद्य पदार्थ और उनके अनुमानित पोषण मूल्य यहाँ दिए गए हैं:",
        "b12_intro": "विटामिन बी12 नसों और रक्त निर्माण के लिए जरूरी है। मुख्य स्रोत यहाँ हैं:",
        "vitaminc_intro": "विटामिन सी रोग प्रतिरोधक क्षमता और आयरन अवशोषण में मदद करता है:",
        "vitamina_intro": "आंखों और त्वचा के लिए विटामिन ए युक्त खाद्य पदार्थ यहाँ हैं:",
        "protein_intro": "मांसपेशियों और ताकत के लिए प्रोटीन युक्त खाद्य पदार्थ यहाँ दिए गए हैं:",
        "calcium_intro": "हड्डियों की मजबूती के लिए कैल्शियम युक्त खाद्य पदार्थ यहाँ हैं:",
        "budget_intro": "किफायती और पौष्टिक स्थानीय खाद्य पदार्थों की सूची यहाँ है:",
        "general_intro": "ICMR-NIN और USDA मानकों पर आधारित स्वस्थ खाद्य पदार्थ (अनुमानित मूल्य):",
    },
    "ta": {
        "friend": "நண்பரே",
        "greeting_template": "வணக்கம் {name}! 😊 இன்று நீங்கள் எப்படி இருக்கிறீர்கள்? நான் உங்கள் FoodGenie உதவியாளர் ஜீனி. எப்படி உதவலாம்?",
        "status": "நான் நன்றாக இருக்கிறேன்! இன்று உங்கள் உணவு மற்றும் ஆரோக்கியத்திற்கு எப்படி உதவலாம்?",
        "activity": "ஆரோக்கியமான உணவுத் தேர்வுகள் மற்றும் ஊட்டச்சத்து வழிகாட்டலில் உங்களுக்கு உதவ இங்கே இருக்கிறேன்!",
        "thanks": "நல்வரவு! 😊 உணவு அல்லது ஊட்டச்சத்து பற்றி எப்போது வேண்டுமானாலும் கேளுங்கள்.",
        "goodbye": "கவனமாக இருங்கள்! இனிய ஆரோக்கியமான நாளாக அமையட்டும்! 👋",
        "identity": "வணக்கம் {name}! நான் உங்கள் FoodGenie ஊட்டச்சத்து உதவியாளர் ஜீனி.",
        "goal_gain_missing": "சிறந்த முடிவு! ஆரோக்கியமான எடை அதிகரிப்புத் திட்டத்தை உருவாக்குவோம். உங்கள் வயது, தற்போதைய எடை மற்றும் உயரத்தைக் கூற முடியுமா?",
        "goal_loss_missing": "நல்ல குறிக்கோள்! உங்கள் வயது, தற்போதைய எடை மற்றும் உயரத்தைக் கூற முடியுமா?",
        "goal_maintain_missing": "எடையைச் சமநிலையில் வைத்திருப்பது சிறந்தது! உங்கள் வயது, எடை மற்றும் உயரத்தைக் கூற முடியுமா?",
        "goal_gain_ready": "உங்கள் விவரங்களின் அடிப்படையில் ஆரோக்கியமான எடை அதிகரிப்பு உணவுத் திட்டம்:",
        "goal_loss_ready": "உங்கள் விவரங்களின் அடிப்படையில் சத்தான எடை குறைப்பு உணவுத் திட்டம்:",
        "goal_maintain_ready": "உங்கள் எடையைப் பராமரிக்க சமச்சீர் உணவுத் திட்டம்:",
        "breakfast_intro": "ஆரோக்கியமான காலை உணவு விருப்பங்கள் மற்றும் அவற்றின் ஊட்டச்சத்து நன்மைகள்:",
        "budget_advice": "உங்கள் தினசரி, வாராந்திர அல்லது மாதாந்திர பட்ஜெட்டை (₹) கூறுங்கள், சத்தான திட்டத்தை உருவாக்குகிறேன்!",
        "doctor_advice": "மருத்துவ ஆலோசனைக்கு More மெனுவில் 'Nearby Doctors' பகுதியைப் பார்க்கவும்.",
        "unrelated": "நான் உங்கள் FoodGenie ஊட்டச்சத்து உதவியாளர் ஜீனி! ஆரோக்கிய உணவு மற்றும் திட்டங்களைப் பற்றி கேளுங்கள்.",
        "hair_intro": "கூந்தல் ஆரோக்கியத்திற்கு புரதம், இரும்புச்சத்து மற்றும் துத்தநாகம் நிறைந்த உணவுகள்:",
        "skin_intro": "ஆரோக்கியமான சருமத்திற்கு வைட்டமின் சி மற்றும் ஆன்டிஆக்ஸிடன்ட்கள் நிறைந்த உணவுகள்:",
        "iron_intro": "இரும்புச்சத்து நிறைந்த உணவுகள் மற்றும் ஊட்டச்சத்து விவரங்கள்:",
        "b12_intro": "வைட்டமின் B12 நிறைந்த உணவுகள்:",
        "vitaminc_intro": "வைட்டமின் சி நிறைந்த உணவுகள்:",
        "vitamina_intro": "வைட்டமின் ஏ நிறைந்த உணவுகள்:",
        "protein_intro": "புரதச்சத்து நிறைந்த உணவுகள்:",
        "calcium_intro": "கால்சியம் நிறைந்த உணவுகள்:",
        "budget_intro": "குறைந்த பட்ஜெட்டில் சத்தான உள்ளூர் உணவுகள்:",
        "general_intro": "ICMR-NIN / USDA தரவுகளின் அடிப்படையில் சத்தான உணவுகள் (மதிப்பீடுகள்):",
    },
    "kn": {
        "friend": "ಸ್ನೇಹಿತರೆ",
        "greeting_template": "ನಮಸ್ಕಾರ {name}! 😊 ನೀವು ಇಂದು ಹೇಗಿದ್ದೀರಿ? ನಾನು ನಿಮ್ಮ FoodGenie ಸಹಾಯಕ ಜೀನಿ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
        "status": "ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ! ಇಂದು ನಿಮ್ಮ ಆಹಾರ ಮತ್ತು ಪೌಷ್ಟಿಕಾಂಶದ ಬಗ್ಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        "activity": "ಆರೋಗ್ಯಕರ ಆಹಾರ ಆಯ್ಕೆಗಳು ಮತ್ತು ಪೌಷ್ಟಿಕಾಂಶದ ಮಾಹಿತಿಯೊಂದಿಗೆ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ!",
        "thanks": "ನಿಮಗೆ ಸ್ವಾಗತ! 😊 ಆಹಾರ ಮತ್ತು ಆರೋಗ್ಯದ ಬಗ್ಗೆ ಯಾವಾಗ ಬೇಕಾದರೂ ಕೇಳಿ.",
        "goodbye": "ಕಾಳಜಿ ವಹಿಸಿ! ಶುಭ ಮತ್ತು ಆರೋಗ್ಯಕರ ದಿನವಾಗಲಿ! 👋",
        "identity": "ನಮಸ್ಕಾರ {name}! ನಾನು ನಿಮ್ಮ FoodGenie ಪೌಷ್ಟಿಕಾಂಶ ಸಹಾಯಕ ಜೀನಿ.",
        "goal_gain_missing": "ಅದ್ಭುತ ಗುರಿ! ಆರೋಗ್ಯಕರ ತೂಕ ಹೆಚ್ಚಳ ಯೋಜನೆ ರೂಪಿಸೋಣ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಯಸ್ಸು, ಪ್ರಸ್ತುತ ತೂಕ ಮತ್ತು ಎತ್ತರವನ್ನು ತಿಳಿಸಬಹುದೇ?",
        "goal_loss_missing": "ಒಳ್ಳೆಯ ನಿರ್ಧಾರ! ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಯಸ್ಸು, ಪ್ರಸ್ತುತ ತೂಕ ಮತ್ತು ಎತ್ತರವನ್ನು ತಿಳಿಸಬಹುದೇ?",
        "goal_maintain_missing": "ತೂಕವನ್ನು ಸಮತೋಲನದಲ್ಲಿಡುವುದು ಉತ್ತಮ ಗುರಿ! ನಿಮ್ಮ ವಯಸ್ಸು, ತೂಕ ಮತ್ತು ಎತ್ತರವನ್ನು ತಿಳಿಸಿ.",
        "goal_gain_ready": "ನಿಮ್ಮ ವಿವರಗಳ ಆಧಾರದ ಮೇಲೆ ತೂಕ ಹೆಚ್ಚಳ ಆಹಾರ ಯೋಜನೆ:",
        "goal_loss_ready": "ನಿಮ್ಮ ವಿವರಗಳ ಆಧಾರದ ಮೇಲೆ ತೂಕ ಇಳಿಕೆ ಆಹಾರ ಯೋಜನೆ:",
        "goal_maintain_ready": "ನಿಮ್ಮ ತೂಕ ನಿರ್ವಹಣಾ ಆಹಾರ ಯೋಜನೆ:",
        "breakfast_intro": "ಆರೋಗ್ಯಕರ ಬೆಳಗಿನ ಉಪಾಹಾರ ಆಯ್ಕೆಗಳು ಮತ್ತು ಪೌಷ್ಟಿಕಾಂಶದ ವಿವರಗಳು:",
        "budget_advice": "ನಿಮ್ಮ ದಿನದ, ವಾರದ ಅಥವಾ ತಿಂಗಳ ಬಜೆಟ್ (₹) ತಿಳಿಸಿ, ಪೌಷ್ಟಿಕ ಯೋಜನೆ ತಯಾರಿಸುತ್ತೇನೆ!",
        "doctor_advice": "ವೈದ್ಯಕೀಯ ಸಲಹೆಗಾಗಿ More ಮೆನುವಿನಲ್ಲಿ 'Nearby Doctors' ನೋಡಿ.",
        "unrelated": "ನಾನು ನಿಮ್ಮ FoodGenie ಪೌಷ್ಟಿಕಾಂಶ ಸಹಾಯಕ ಜೀನಿ! ಆರೋಗ್ಯಕರ ಆಹಾರ ಮತ್ತು ಡಯಟ್ ಬಗ್ಗೆ ಕೇಳಿ.",
        "hair_intro": "ಕೂದಲಿನ ಆರೋಗ್ಯಕ್ಕೆ ಪ್ರೋಟೀನ್, ಕಬ್ಬಿಣ ಮತ್ತು ಜಿಂಕ್ ಸಮೃದ್ಧ ಆಹಾರಗಳು:",
        "skin_intro": "ಚರ್ಮದ ಆರೋಗ್ಯಕ್ಕೆ ವಿಟಮಿನ್ ಸಿ ಮತ್ತು ಉತ್ಕರ್ಷಣ ನಿರೋಧಕ ಆಹಾರಗಳು:",
        "iron_intro": "ಕಬ್ಬಿಣಾಂಶ ಭರಿತ ಆಹಾರಗಳು ಮತ್ತು ಅಂದಾಜು ಪೌಷ್ಟಿಕಾಂಶ ಮೌಲ್ಯಗಳು:",
        "b12_intro": "ವಿಟಮಿನ್ B12 ಆಹಾರ ಮೂಲಗಳು:",
        "vitaminc_intro": "ವಿಟಮಿನ್ ಸಿ ಆಹಾರ ಮೂಲಗಳು:",
        "vitamina_intro": "ವಿಟಮಿನ್ ಎ ಆಹಾರ ಮೂಲಗಳು:",
        "protein_intro": "ಪ್ರೋಟೀನ್ ಸಮೃದ್ಧ ಆಹಾರಗಳು:",
        "calcium_intro": "ಕ್ಯಾಲ್ಸಿಯಂ ಸಮೃದ್ಧ ಆಹಾರಗಳು:",
        "budget_intro": "ಕಡಿಮೆ ಬಜೆಟ್‌ನ ಪೌಷ್ಟಿಕ ಆಹಾರಗಳು:",
        "general_intro": "ICMR-NIN / USDA ಆಧಾರಿತ ಆರೋಗ್ಯಕರ ಆಹಾರಗಳು (ಅಂದಾಜು ಮೌಲ್ಯಗಳು):",
    },
}


def classify_user_intent(query: str) -> str:
    """
    Classifies user query intent cleanly across casual conversation,
    health goals, specific meal requests, restrictions, budget, and nutrition Q&A.
    """
    q = query.lower().strip()
    clean_words = set(re.findall(r'\b\w+\b', q))

    # 1. Casual Greeting (only when not combined with food/health questions)
    greetings = {"hi", "hello", "hey", "yo", "namaste", "namaskar", "vanakkam", "namaskaram", "hai", "hii"}
    nutrition_keywords = [
        "iron", "vitamin", "protein", "calcium", "food", "foods", "diet", "meal", "breakfast",
        "lunch", "dinner", "snack", "hair", "skin", "weight", "gain", "loss", "budget", "avoid",
        "allergy", "diabetes", "thyroid", "cart", "cheaper", "alternative", "calories", "cost",
        "రుచి", "ఆహార", "జుట్టు", "బరువు", "खाना", "बाल", "वजन", "ஆகாரம்", "உணவு", "ಆಹಾರ"
    ]
    if (clean_words & greetings or any(q.startswith(g) for g in ["good morning", "good afternoon", "good evening", "హాయ్", "నమస్కారం", "नमस्ते", "வணக்கம்", "ನಮಸ್ಕಾರ"])):
        if not any(k in q for k in nutrition_keywords):
            return "casual_greeting"

    # 2. Casual Status ("How are you?")
    if any(phrase in q for phrase in [
        "how are you", "how r u", "how do you do", "ela unnavu", "bagunnara", "ela unnar",
        "kya haal hai", "kaisa hai", "kaise ho", "eppadi irukkeenga", "hegiddira",
        "బాగున్నారా", "ఎలా ఉన్నారు", "कैसे हैं", "कैसे हो", "எப்படி இருக்கீங்க", "ಹೇಗಿದ್ದೀರಾ"
    ]) and not any(k in q for k in nutrition_keywords):
        return "casual_status"

    # 3. Casual Activity ("What are you doing?")
    if any(phrase in q for phrase in [
        "what are you doing", "what r u doing", "what doing", "em chestunnavu", "em chestunnav", "em chesthunav",
        "kya kar rahe ho", "kya kar rahe", "enna panreenga", "enna seigirai", "enu maadthiddira",
        "ఏం చేస్తున్నావు", "ఏం చేస్తున్నావ్", "क्या कर रहे हो", "என்ன செய்கிறீர்கள்", "ಏನು ಮಾಡುತ್ತಿದ್ದೀರಿ"
    ]):
        return "casual_activity"

    # 4. Casual Thanks
    if any(phrase in q for phrase in [
        "thank you", "thanks", "thx", "thank u", "dhanyavadamulu", "dhanyavadalu", "shukriya", "dhanyawad", "nandri",
        "ధన్యవాదాలు", "ధన్యవాదములు", "शुक्रिया", "धन्यवाद", "நன்றி", "ಧನ್ಯವಾದಗಳು"
    ]):
        return "casual_thanks"

    # 5. Casual Goodbye
    if any(phrase in q for phrase in [
        "bye", "goodbye", "cya", "see you", "tata", "alvida", "velthanu", "poitu varen", "hogi barthini",
        "బై", "వెళ్తాను", "अलविदा", "போய் வருகிறேன்", "ಹೋಗಿ ಬರುತ್ತೇನೆ"
    ]):
        return "casual_goodbye"

    # 6. Identity / Purpose
    if any(phrase in q for phrase in [
        "who are you", "what are you", "what can you do", "your name", "who made you",
        "nuvvu evaru", "meeru evaru", "tum kaun ho", "neenu yaaru",
        "నువ్వు ఎవరు", "మీరు ఎవరు", "तुम कौन हो"
    ]):
        return "casual_identity"

    # 7. Health Goals (Gain / Loss / Maintain)
    gain_markers = [
        "gain weight", "weight gain", "bulk up", "baruvu peragali", "లావు అవ్వ", "బరువు పెరగ",
        "वजन बढ़ाना", "vajan badhana", "mote hona", "edai athikarikka", "எடை கூட", "thooka hechhisalu", "ತೂಕ ಹೆಚ್ಚಳ", "లావు కావాలి"
    ]
    if any(m in q for m in gain_markers):
        return "health_goal_gain"

    loss_markers = [
        "lose weight", "weight loss", "fat loss", "slim down", "baruvu thaggali", "బరువు తగ్గ", "సన్నబడాలి",
        "वजन घटाना", "vajan kam", "patle hona", "edai kuraikka", "எடை குறைய", "thooka ilike", "ತೂಕ ಇಳಿಕೆ", "fat burn"
    ]
    if any(m in q for m in loss_markers):
        return "health_goal_loss"

    maintain_markers = [
        "maintain weight", "weight maintenance", "బరువు స్థిరంగా", "वजन संतुलित",
        "same weight", "edai paramarippu", "thooka samatholana"
    ]
    if any(m in q for m in maintain_markers):
        return "health_goal_maintain"

    # 8. Budget Planning (only if pure budget inquiry without specific food search)
    if any(phrase in q for phrase in [
        "budget diet", "cost per day", "monthly budget", "weekly budget", "affordable diet",
        "takkuva karchu", "తక్కువ ఖర్చు డైట్", "బजट डाइट", "बजट डाइट", "kam kharch", "kam budget"
    ]):
        return "budget_planning"

    # 9. Doctor Search
    if any(phrase in q for phrase in [
        "find doctor", "nearby doctor", "dermatologist near", "dietitian near", "doctor search",
        "డాక్టర్ కావాలి", "వైద్యుడు", "डॉक्टर खोजें", "चिकित्सक"
    ]):
        return "doctor_search"

    # 10. Unrelated non-food queries
    if any(phrase in q for phrase in [
        "write code", "python code", "solve math", "who won", "cricket score", "movie review",
        "write an essay", "capital of france", "programming in", "javascript code"
    ]):
        return "general_unrelated"

    return "nutrition_question"


def _extract_context_from_history_and_query(
    query: str,
    chat_history: List[Dict[str, str]],
    profile_ctx: Dict[str, Any]
) -> Dict[str, Any]:
    """Extracts user attributes (age, weight, height, diet, goal) from history + current query + profile."""
    combined = " ".join([t.get("text", "") for t in chat_history if t.get("sender") == "user"] + [query]).lower()

    age = profile_ctx.get("age")
    weight = profile_ctx.get("weight_kg")
    height = profile_ctx.get("height_cm")
    diet = profile_ctx.get("dietary_preference")
    goal = profile_ctx.get("health_goals")

    if not age:
        m = re.search(r'\b(?:age|i am|im|i\'m)?\s*(\d{2})\s*(?:years?\s*old|yrs?|yo)\b', combined)
        if m:
            age = int(m.group(1))

    if not weight:
        m = re.search(r'(\d{2,3}(?:\.\d+)?)\s*(?:kg|kgs|kilograms?)\b', combined)
        if m:
            weight = float(m.group(1))

    if not height:
        m = re.search(r'(\d{3}(?:\.\d+)?)\s*(?:cm|centimeters?)\b', combined)
        if m:
            height = float(m.group(1))

    if any(w in combined for w in ["vegan"]):
        diet = "vegan"
    elif any(w in combined for w in ["non-veg", "non veg", "non vegetarian", "chicken", "fish", "eggs"]):
        diet = "non-vegetarian"
    elif any(w in combined for w in ["vegetarian", "veg ", "veg.", "శాకాహార", "शाकाहारी"]):
        diet = "vegetarian"

    return {
        "age": age,
        "weight_kg": weight,
        "height_cm": height,
        "dietary_preference": diet,
        "health_goals": goal,
        "has_baseline_metrics": bool(age and weight and height),
    }


def _detect_meal_filter(query: str) -> Optional[str]:
    q = query.lower()
    if any(w in q for w in ["breakfast", "morning meal", "అల్పాహారం", "नाश्ता", "காலை உணவு", "ಉಪಾಹಾರ"]):
        return "Breakfast"
    if any(w in q for w in ["morning snack", "mid-morning", "mid morning"]):
        return "Morning Snack"
    if any(w in q for w in ["lunch", "afternoon meal", "మధ్యాహ్న భోజనం", "दोपहर का भोजन"]):
        return "Lunch"
    if any(w in q for w in ["evening snack", "snacks", "snack", "సాయంత్రం", "शाम का नाश्ता"]):
        return "Evening Snack"
    if any(w in q for w in ["dinner", "night meal", "supper", "రాత్రి భోజనం", "रात का खाना"]):
        return "Dinner"
    return None


def _build_five_meal_plan_markdown(
    intro: str,
    foods: List[RecommendedFoodItem],
    language: str = "en",
    restrictions: Optional[List[FoodRestrictionItem]] = None,
) -> str:
    """Constructs a structured 5-category daily diet recommendation table with real DB values."""
    lines = [intro, ""]
    categories = ["Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"]

    used_names = set()
    selected_rows = []
    for cat in categories:
        match = next(
            (f for f in foods if f.meal_category == cat and f.name not in used_names),
            None,
        )
        if not match:
            match = next((f for f in foods if f.name not in used_names), None)
        if match:
            used_names.add(match.name)
            selected_rows.append((cat, match))

    lines.append("| Meal | Food | Quantity | Calories (est.) | Protein (est.) | Est. Price |")
    lines.append("|:---|:---|:---|---:|---:|---:|")
    for cat, food in selected_rows:
        macros = food.nutrients_per_serving or food.nutrients_per_100g
        cals = f"{macros.calories_kcal:.0f} kcal" if macros else "N/A"
        prot = f"{macros.protein_g:.1f}g" if macros else "N/A"
        lines.append(
            f"| **{cat}** | {food.name} | {food.serving_size} | {cals} | {prot} | ₹{food.estimated_price_inr:.0f} |"
        )

    lines.append("")
    lines.append("### Detailed Meal Breakdown (ICMR-NIN / USDA Estimated Values)")
    for cat, food in selected_rows:
        macros = food.nutrients_per_serving or food.nutrients_per_100g
        cals = f"{macros.calories_kcal:.0f} kcal" if macros else "N/A"
        prot = f"{macros.protein_g:.1f}g" if macros else "N/A"
        carbs = f"{macros.carbs_g:.1f}g" if macros else "N/A"
        fat = f"{macros.fat_g:.1f}g" if macros else "N/A"
        vits = ", ".join([f"{v.name} ({v.amount_per_serving}{v.unit})" for v in food.vitamins[:3]]) or "Verified food record"
        mins = ", ".join([f"{m.name} ({m.amount_per_serving}{m.unit})" for m in food.minerals[:3]]) or "Verified food record"
        lines.append(f"- **{cat} — {food.name}** ({food.serving_size}, est. ₹{food.estimated_price_inr:.0f}): {cals} | Protein {prot} | Carbs {carbs} | Fats {fat} | Vitamins: {vits} | Minerals: {mins}. *{food.benefit}* Prep: {food.how_to_consume}")

    if restrictions:
        lines.append("")
        lines.append("### Foods to Limit or Avoid")
        for r in restrictions[:4]:
            alts = ", ".join(r.safe_alternatives[:3]) if r.safe_alternatives else "Consult a dietitian"
            lines.append(f"- **{r.food_name}**: {r.reason} **Alternatives:** {alts}.")

    return "\n".join(lines)


def format_recommendations_markdown(
    intro: str,
    foods: List[RecommendedFoodItem],
    language: str = "en",
    query: str = "",
    restrictions: Optional[List[FoodRestrictionItem]] = None,
) -> str:
    """
    Constructs a clean structured food recommendation response with:
    - Natural intro
    - Markdown Table: | Food | Meal | Quantity | Price (Est.) | Protein | Calories |
    - Detailed 12-point breakdown grounded in real DB values (never fabricated)
    """
    output_lines = [intro, ""]

    col_food = "Food"
    col_meal = "Meal Category"
    col_qty = "Quantity"
    col_price = "Est. Price"
    col_protein = "Protein"
    col_calories = "Calories"

    if language == "te":
        col_food = "ఆహారం (Food)"
        col_meal = "భోజన సమయం"
        col_qty = "పరిమాణం"
        col_price = "అంచనా ధర"
        col_protein = "ప్రోటీన్"
        col_calories = "కేలరీలు"
    elif language == "hi":
        col_food = "भोजन (Food)"
        col_meal = "भोजन श्रेणी"
        col_qty = "मात्रा"
        col_price = "अनुमानित कीमत"
        col_protein = "प्रोटीन"
        col_calories = "कैलोरी"

    output_lines.append(f"| {col_food} | {col_meal} | {col_qty} | {col_price} | {col_protein} | {col_calories} |")
    output_lines.append("|:---|:---|:---|---:|---:|---:|")

    for food in foods[:8]:
        macros = food.nutrients_per_serving or food.nutrients_per_100g
        cal = f"{int(macros.calories_kcal)} kcal" if macros else "Est."
        prot = f"{macros.protein_g:.1f}g" if macros else "Est."
        meal_cat = food.meal_category or "Any meal"
        output_lines.append(
            f"| **{food.name}** | {meal_cat} | {food.serving_size} | ₹{food.estimated_price_inr:.0f} | {prot} | {cal} |"
        )

    output_lines.append("\n### Nutritional Details & Preparation (Estimated per Serving)\n")

    for idx, food in enumerate(foods[:6], 1):
        macros = food.nutrients_per_serving or food.nutrients_per_100g
        cals = f"{macros.calories_kcal:.0f} kcal" if macros else "N/A"
        prot = f"{macros.protein_g:.1f}g" if macros else "N/A"
        carbs = f"{macros.carbs_g:.1f}g" if macros else "N/A"
        fat = f"{macros.fat_g:.1f}g" if macros else "N/A"
        fiber = f"{macros.fiber_g:.1f}g" if macros else "N/A"

        vits = ", ".join([f"{v.name} ({v.amount_per_serving}{v.unit})" for v in food.vitamins[:3]]) or "See database profile"
        mins = ", ".join([f"{m.name} ({m.amount_per_serving}{m.unit})" for m in food.minerals[:3]]) or "See database profile"
        benefits = food.benefit or "Supports balanced daily nutrition."
        how_to = food.how_to_consume or "Prepare fresh using minimal oil."

        output_lines.append(f"#### {idx}. **{food.name}** ({food.meal_category or 'Daily Meal'})")
        output_lines.append(f"- **Recommended Quantity:** {food.serving_size}")
        output_lines.append(f"- **Macros (Estimated):** **{cals}** | **{prot} Protein** | {carbs} Carbs | {fat} Fats | {fiber} Fiber")
        output_lines.append(f"- **Vitamins:** {vits}")
        output_lines.append(f"- **Minerals:** {mins}")
        output_lines.append(f"- **Health Benefits:** {benefits}")
        output_lines.append(f"- **Estimated Price:** ₹{food.estimated_price_inr:.0f} (Estimated local retail)")
        output_lines.append(f"- **Preparation:** {how_to}\n")

    if restrictions:
        output_lines.append("### Foods to Limit or Avoid\n")
        for r in restrictions[:4]:
            alts = ", ".join(r.safe_alternatives[:3]) if r.safe_alternatives else "Whole-food alternatives"
            output_lines.append(f"- **{r.food_name}** ({r.category.replace('_', ' ')}): {r.reason} *Alternatives: {alts}*")

    disclaimer = {
        "en": "\n*Disclaimer: Nutritional values and retail prices are estimates based on ICMR-NIN and USDA reference data. This guidance supports general wellness and does not replace medical diagnosis or treatment.*",
        "te": "\n*గమనిక (Disclaimer): పోషక విలువలు మరియు ధరలు ICMR-NIN & USDA డేటా ఆధారిత అంచనాలు మాత్రమే. వైద్య సలహా కోసం నిపుణులను సంప్రదించండి.*",
        "hi": "\n*अस्वीकरण (Disclaimer): पोषण मूल्य और कीमतें ICMR-NIN और USDA डेटा पर आधारित अनुमान हैं। चिकित्सीय सलाह के लिए डॉक्टर से परामर्श लें।*",
        "ta": "\n*குறிப்பு (Disclaimer): ஊட்டச்சத்து மதிப்புகள் மற்றும் விலைகள் ICMR-NIN / USDA தரவுகளின் அடிப்படையிலான மதிப்பீடுகள் மட்டுமே.*",
        "kn": "\n*ಸೂಚನೆ (Disclaimer): ಪೌಷ್ಟಿಕಾಂಶ ಮೌಲ್ಯಗಳು ಮತ್ತು ಬೆಲೆಗಳು ICMR-NIN / USDA ಆಧಾರಿತ ಅಂದಾಜುಗಳಾಗಿವೆ.*",
    }
    output_lines.append(disclaimer.get(language, disclaimer["en"]))

    return "\n".join(output_lines)


class GenieAIService:
    @staticmethod
    def _call_llm_provider(
        query: str,
        user_name: str,
        detected_language: str,
        health_goal: Optional[str] = None,
        dietary_preference: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        profile_summary: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        rag_context: Optional[List[Dict[str, Any]]] = None,
        restrictions_context: Optional[List[Dict[str, Any]]] = None,
        intent: Optional[str] = None,
        timeout: float = 20.0,
    ) -> Optional[str]:
        """Calls configured LLM provider (OpenRouter primary, Gemini fallback)."""
        provider = (settings.LLM_PROVIDER or "auto").lower().strip()
        kwargs = {
            "query": query,
            "user_name": user_name,
            "detected_language": detected_language,
            "health_goal": health_goal,
            "dietary_preference": dietary_preference,
            "allergies": allergies,
            "profile_summary": profile_summary,
            "chat_history": chat_history,
            "rag_context": rag_context,
            "restrictions_context": restrictions_context,
            "intent": intent,
            "timeout": timeout,
        }

        if provider == "gemini" and gemini_service.api_key:
            reply = gemini_service.generate_response_sync(**kwargs)
            if reply:
                return reply
            if openrouter_service.is_configured():
                return openrouter_service.generate_response_sync(**kwargs)
            return None

        if openrouter_service.is_configured():
            reply = openrouter_service.generate_response_sync(**kwargs)
            if reply:
                return reply

        if gemini_service.api_key:
            return gemini_service.generate_response_sync(**kwargs)

        return None

    @classmethod
    def generate_friendly_response(
        cls,
        db: Session,
        query: str,
        user_id: Optional[int] = None,
        preferred_language: str = "en",
        session_id: Optional[str] = None,
        is_voice: bool = False,
        selected_food: Optional[Dict[str, Any]] = None,
    ) -> RecommendationResponse:
        # 1. Auto-detect language from user's message (never require a dropdown)
        detected_lang, confidence, _ = language_detector.detect_language(query, preferred_language)
        active_lang = detected_lang if confidence >= 0.80 else (preferred_language or "en")
        if active_lang not in GENIE_PERSONA:
            active_lang = "en"

        persona = GENIE_PERSONA.get(active_lang, GENIE_PERSONA["en"])

        # 2. Load user profile context & localized fallback name
        user_name = persona["friend"]
        profile_ctx: Dict[str, Any] = {}
        user_allergies: List[str] = []
        user_conditions: List[str] = []

        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                if user.full_name and user.full_name.strip():
                    user_name = user.full_name.strip()
                elif user.email:
                    user_name = user.email.split("@")[0].replace(".", " ").title()
                if user.profile:
                    p = user.profile
                    profile_ctx = {
                        "age": p.age,
                        "gender": p.gender,
                        "weight_kg": p.weight_kg,
                        "target_weight_kg": getattr(p, "target_weight_kg", None),
                        "height_cm": p.height_cm,
                        "activity_level": p.activity_level,
                        "dietary_preference": p.dietary_preference,
                        "health_goals": p.health_goals,
                        "monthly_food_budget": p.monthly_food_budget,
                    }
                    if p.health_conditions:
                        try:
                            parsed = json.loads(p.health_conditions)
                            user_conditions = parsed if isinstance(parsed, list) else [str(parsed)]
                        except Exception:
                            user_conditions = [c.strip() for c in p.health_conditions.split(",") if c.strip()]
                    if p.allergies:
                        user_allergies = [a.allergen_name for a in p.allergies]

        # 3. Load recent conversation turns for memory & context continuity
        chat_history: List[Dict[str, str]] = []
        if session_id:
            past_rows = get_chat_history(db, user_id=user_id, session_id=session_id, limit=12, order="asc")
            for row in past_rows:
                if row.user_query:
                    chat_history.append({"sender": "user", "text": row.user_query})
                if row.genie_response:
                    chat_history.append({"sender": "genie", "text": row.genie_response})

        extracted = _extract_context_from_history_and_query(query, chat_history, profile_ctx)

        # Build concise profile summary string for Gemini
        summary_bits = []
        if extracted.get("age"):
            summary_bits.append(f"Age: {extracted['age']}")
        if profile_ctx.get("gender"):
            summary_bits.append(f"Gender: {profile_ctx['gender']}")
        if extracted.get("weight_kg"):
            summary_bits.append(f"Current Weight: {extracted['weight_kg']} kg")
        if profile_ctx.get("target_weight_kg"):
            summary_bits.append(f"Target Weight: {profile_ctx['target_weight_kg']} kg")
        if extracted.get("height_cm"):
            summary_bits.append(f"Height: {extracted['height_cm']} cm")
        if profile_ctx.get("activity_level"):
            summary_bits.append(f"Activity Level: {profile_ctx['activity_level']}")
        if profile_ctx.get("monthly_food_budget"):
            summary_bits.append(f"Monthly Food Budget: ₹{profile_ctx['monthly_food_budget']:.0f} (approx ₹{profile_ctx['monthly_food_budget']/30:.0f}/day)")

        cart_items_summary = []
        cart_total_cost = 0.0
        cart_total_kcal = 0.0
        cart_total_prot = 0.0
        if user_id:
            from model_cart import UserCart
            user_cart = db.query(UserCart).filter(UserCart.user_id == user_id).first()
            if user_cart and user_cart.items:
                for ci in user_cart.items:
                    q_mult = float(ci.quantity or 1.0)
                    c_kcal = round((ci.calories_per_unit or 0.0) * q_mult, 1)
                    c_prot = round((ci.protein_per_unit or 0.0) * q_mult, 1)
                    c_cost = round((ci.estimated_price_inr_per_unit or 0.0) * q_mult, 2)
                    cart_total_kcal += c_kcal
                    cart_total_prot += c_prot
                    cart_total_cost += c_cost
                    cart_items_summary.append(
                        f"{ci.food_name} ({ci.meal_category}, qty {q_mult:g}, {c_kcal:.0f} kcal, {c_prot:.1f}g P, est. ₹{c_cost:.0f})"
                    )
                summary_bits.append(
                    f"User Food Cart ({len(cart_items_summary)} items, Total {cart_total_kcal:.0f} kcal, {cart_total_prot:.1f}g Protein, Est. Total ₹{cart_total_cost:.0f}): "
                    + "; ".join(cart_items_summary[:8])
                )
            else:
                summary_bits.append("User Food Cart: empty (0 items saved)")

        if selected_food and isinstance(selected_food, dict):
            sf_name = selected_food.get("name") or selected_food.get("food_name")
            if sf_name:
                summary_bits.append(
                    f"Selected Food Focus: {sf_name} | Calories: {selected_food.get('calories_kcal', 'N/A')} kcal | "
                    f"Protein: {selected_food.get('protein_g', 'N/A')}g | Est. Price: ₹{selected_food.get('estimated_price_inr', 'N/A')}"
                )

        profile_summary_str = " | ".join(summary_bits) if summary_bits else None

        # 4. Classify intent
        intent = classify_user_intent(query)
        logger.info(f"Genie intent='{intent}' lang='{active_lang}' query='{query[:60]}'")

        # 5. Pure casual conversations (greetings, status, activity, thanks, goodbye, identity, unrelated)
        # Never generate meal plans or dump food tables here!
        casual_fallbacks = {
            "casual_greeting": persona["greeting_template"].format(name=user_name),
            "casual_status": persona["status"],
            "casual_activity": persona["activity"],
            "casual_thanks": persona["thanks"],
            "casual_goodbye": persona["goodbye"],
            "casual_identity": persona["identity"].format(name=user_name),
            "doctor_search": persona["doctor_advice"],
            "general_unrelated": persona["unrelated"],
        }

        if intent in casual_fallbacks:
            reply_text = None
            # Let LLM handle non-greeting conversational turns naturally with full history
            if intent not in ("casual_greeting", "casual_goodbye"):
                reply_text = cls._call_llm_provider(
                    query=query,
                    user_name=user_name,
                    detected_language=active_lang,
                    health_goal=extracted.get("health_goals"),
                    dietary_preference=extracted.get("dietary_preference"),
                    allergies=user_allergies,
                    profile_summary=profile_summary_str,
                    chat_history=chat_history,
                    intent=intent,
                    timeout=12.0,
                )
            if not reply_text:
                reply_text = casual_fallbacks[intent]

            record_chat_message(
                db=db,
                user_id=user_id,
                session_id=session_id,
                user_query=query,
                genie_response=reply_text,
                language_code=active_lang,
                is_voice_input=is_voice,
                is_voice_output=is_voice,
                detected_language=detected_lang,
                intent=intent,
            )
            return RecommendationResponse(
                id=1,
                query=query,
                language=active_lang,
                intent=intent,
                summary=reply_text,
                recommended_foods=[],
                foods_to_avoid=[],
                restrictions=[],
                cautions=None,
            )

        # 6. Health goal declaration without baseline metrics -> ask naturally for missing details!
        is_goal_intent = intent in ("health_goal_gain", "health_goal_loss", "health_goal_maintain")
        q_lower = query.lower()
        explicit_plan_or_foods = any(
            w in q_lower for w in ["food", "foods", "meal plan", "diet plan", "chart", "list", "eat", "ఆహార", "खाना"]
        )
        if is_goal_intent and not extracted["has_baseline_metrics"] and not explicit_plan_or_foods:
            missing_map = {
                "health_goal_gain": persona["goal_gain_missing"],
                "health_goal_loss": persona["goal_loss_missing"],
                "health_goal_maintain": persona["goal_maintain_missing"],
            }
            reply_text = cls._call_llm_provider(
                query=query,
                user_name=user_name,
                detected_language=active_lang,
                health_goal=intent.replace("health_goal_", "weight_"),
                dietary_preference=extracted.get("dietary_preference"),
                allergies=user_allergies,
                profile_summary=profile_summary_str,
                chat_history=chat_history,
                intent=intent,
                timeout=12.0,
            )
            if not reply_text:
                reply_text = missing_map[intent]

            record_chat_message(
                db=db,
                user_id=user_id,
                session_id=session_id,
                user_query=query,
                genie_response=reply_text,
                language_code=active_lang,
                is_voice_input=is_voice,
                is_voice_output=is_voice,
                detected_language=detected_lang,
                intent=intent,
            )
            return RecommendationResponse(
                id=1,
                query=query,
                language=active_lang,
                intent=intent,
                summary=reply_text,
                recommended_foods=[],
                foods_to_avoid=[],
                restrictions=[],
                cautions=None,
            )

        # 7. Food / Meal / Diet / Nutrition / Budget / Avoidance Query
        # Retrieve verified foods grounded from database
        all_foods = nutrition_rag.retrieve_verified_foods(db, query, language=active_lang, limit=25)
        topic = nutrition_rag.identify_topic(query)
        meal_filter = _detect_meal_filter(query)

        # Filter out allergies & vegetarian/vegan conflicts
        res_analysis = restriction_service.analyze_restrictions(
            query=query,
            allergies=user_allergies,
            medical_conditions=user_conditions,
            dietary_preference=extracted.get("dietary_preference"),
            language=active_lang,
        )
        restrictions: List[FoodRestrictionItem] = res_analysis.restrictions
        avoids: List[AvoidFoodItem] = [
            AvoidFoodItem(
                name=r.food_name,
                reason=r.reason,
                food_name=r.food_name,
                restriction_type=r.restriction_type,
                category=r.category,
                severity=r.severity,
                safe_alternatives=r.safe_alternatives,
                clinical_note=r.clinical_note,
                action_type=r.action_type,
            )
            for r in restrictions
        ]

        diet_pref = (extracted.get("dietary_preference") or "").lower()
        is_veg = diet_pref in ("vegetarian", "vegan") or any(
            w in q_lower for w in ["vegetarian", "veg", "vegan", "శాకాహార", "శాకాహారి", "शाकाहारी"]
        )

        safe_foods: List[RecommendedFoodItem] = []
        for food in all_foods:
            fname = food.name.lower()
            if is_veg and "egg" in fname:
                continue
            if diet_pref == "vegan" and any(d in fname for d in ["paneer", "curd", "yogurt", "milk", "egg"]):
                continue
            conflicted = False
            for r in restrictions:
                if r.restriction_type == "medically_necessary" and r.category == "allergy":
                    rid = (r.id or "").lower()
                    if "peanut" in rid and ("peanut" in fname or "groundnut" in fname):
                        conflicted = True
                        break
                    if "dairy" in rid and ("milk" in fname or "paneer" in fname or "curd" in fname):
                        conflicted = True
                        break
                    if "gluten" in rid and ("wheat" in fname or "maida" in fname or "sooji" in fname):
                        conflicted = True
                        break
                    if "soy" in rid and ("soya" in fname or "soy" in fname or "tofu" in fname):
                        conflicted = True
                        break
            if not conflicted:
                safe_foods.append(food)

        # Prioritize by meal filter or goal
        if meal_filter:
            meal_matched = [f for f in safe_foods if f.meal_category == meal_filter]
            if meal_matched:
                safe_foods = meal_matched + [f for f in safe_foods if f.meal_category != meal_filter]

        active_goal = (
            "weight_gain" if intent == "health_goal_gain"
            else "weight_loss" if intent == "health_goal_loss"
            else "weight_maintain" if intent == "health_goal_maintain"
            else (extracted.get("health_goals") or "")
        ).lower()
        if "gain" in active_goal:
            dense = ["Peanuts", "Paneer", "Eggs", "Ragi", "Sesame", "Sweet Potato", "Almonds", "Walnuts"]
            safe_foods.sort(key=lambda f: 0 if any(d.lower() in f.name.lower() for d in dense) else 1)
        elif "loss" in active_goal:
            lean = ["Moong", "Spinach", "Broccoli", "Guava", "Amla", "Moringa", "Papaya", "Carrots"]
            safe_foods.sort(key=lambda f: 0 if any(l.lower() in f.name.lower() for l in lean) else 1)

        # Prepare compact RAG dicts for Gemini
        rag_payload = []
        for f in safe_foods[:12]:
            m = f.nutrients_per_serving or f.nutrients_per_100g
            rag_payload.append({
                "name": f.name,
                "name_te": f.name_te,
                "name_hi": f.name_hi,
                "meal_category": f.meal_category,
                "serving_size": f.serving_size,
                "estimated_price_inr": f.estimated_price_inr,
                "calories_kcal": m.calories_kcal if m else 0,
                "protein_g": m.protein_g if m else 0,
                "carbs_g": m.carbs_g if m else 0,
                "fat_g": m.fat_g if m else 0,
                "fiber_g": m.fiber_g if m else 0,
                "vitamins_summary": [f"{v.name} {v.amount_per_serving}{v.unit}" for v in f.vitamins[:3]],
                "minerals_summary": [f"{mi.name} {mi.amount_per_serving}{mi.unit}" for mi in f.minerals[:3]],
                "benefit": f.benefit,
                "how_to_consume": f.how_to_consume,
            })

        restriction_payload = [
            {
                "food_name": r.food_name,
                "category": r.category,
                "reason": r.reason,
                "safe_alternatives": r.safe_alternatives,
            }
            for r in restrictions[:6]
        ]

        # Primary AI conversational response (OpenRouter primary, Gemini fallback)
        llm_reply = cls._call_llm_provider(
            query=query,
            user_name=user_name,
            detected_language=active_lang,
            health_goal=active_goal or None,
            dietary_preference=extracted.get("dietary_preference"),
            allergies=user_allergies,
            profile_summary=profile_summary_str,
            chat_history=chat_history,
            rag_context=rag_payload,
            restrictions_context=restriction_payload,
            intent=topic if not is_goal_intent else intent,
            timeout=14.0,
        )

        # Build fallback structured response if LLM is offline/unavailable
        intro_map = {
            "hair_health": persona["hair_intro"],
            "skin_nutrition": persona["skin_intro"],
            "iron_rich": persona["iron_intro"],
            "vitamin_b12": persona["b12_intro"],
            "vitamin_c": persona["vitaminc_intro"],
            "vitamin_a": persona["vitamina_intro"],
            "protein_rich": persona["protein_intro"],
            "calcium_rich": persona["calcium_intro"],
            "budget_diet": persona["budget_intro"],
            "general_nutrition": persona["general_intro"],
        }

        if llm_reply and len(llm_reply.strip()) > 15:
            final_summary = llm_reply.strip()
            # Append concise verified nutrition summary table if LLM omitted structured numbers/prices
            if "|" not in final_summary or "₹" not in final_summary:
                table_rows = [
                    "\n\n| Food | Meal Category | Quantity | Est. Price | Protein | Calories |",
                    "|:---|:---|:---|---:|---:|---:|",
                ]
                for f in safe_foods[:6]:
                    macros = f.nutrients_per_serving or f.nutrients_per_100g
                    cal_s = f"{int(macros.calories_kcal)} kcal" if macros else "Est."
                    prot_s = f"{macros.protein_g:.1f}g" if macros else "Est."
                    table_rows.append(
                        f"| **{f.name}** | {f.meal_category or 'Daily Meal'} | {f.serving_size} | ₹{f.estimated_price_inr:.0f} | {prot_s} | {cal_s} |"
                    )
                final_summary += "\n".join(table_rows)
            if "disclaimer" not in final_summary.lower():
                final_summary += "\n\n*Disclaimer: Nutritional values and prices are estimates based on ICMR-NIN and USDA reference data and do not replace medical advice.*"
        else:
            if "cart" in q_lower and user_id and cart_items_summary:
                cart_rows = "\n".join(f"- {line}" for line in cart_items_summary)
                final_summary = (
                    f"Here is a live summary of your saved **My Food Cart** ({len(cart_items_summary)} items):\n\n"
                    f"- **Estimated Cart Cost:** ₹{cart_total_cost:.0f} (estimated market rates)\n"
                    f"- **Total Cart Energy & Protein:** {cart_total_kcal:.0f} kcal | {cart_total_prot:.1f}g protein\n\n"
                    f"### Saved Cart Items\n{cart_rows}\n\n"
                    "*Tip: You can ask me to suggest cheaper local swaps (like Roasted Peanuts, Green Moong, or Ragi) or check if these fit your daily target.*"
                )
            elif any(w in q_lower for w in ["cheaper", "cheap", "budget swap", "alternative", "substitute"]):
                from model_grocery import GroceryItem
                heroes = db.query(GroceryItem).filter(GroceryItem.is_budget_hero.is_(True)).all()
                swap_lines = [
                    f"- **{h.name}** (~₹{h.avg_price_inr:.0f} per {h.standard_quantity}, verified benchmark): {h.affordable_substitute_for or h.nutritional_perks}"
                    for h in heroes[:5]
                ]
                intro_text = persona["budget_intro"] + ("\n\n" + "\n".join(swap_lines) if swap_lines else "")
                final_summary = format_recommendations_markdown(
                    intro=intro_text,
                    foods=safe_foods,
                    language=active_lang,
                    query=query,
                    restrictions=restrictions,
                )
            elif is_goal_intent or any(w in q_lower for w in ["diet plan", "meal plan", "full day", "5 meals"]):
                goal_intro = (
                    persona["goal_gain_ready"] if "gain" in active_goal
                    else persona["goal_loss_ready"] if "loss" in active_goal
                    else persona["goal_maintain_ready"]
                )
                final_summary = _build_five_meal_plan_markdown(
                    intro=goal_intro,
                    foods=safe_foods,
                    language=active_lang,
                    restrictions=restrictions,
                )
            elif meal_filter == "Breakfast":
                breakfast_foods = [f for f in safe_foods if f.meal_category == "Breakfast"] or safe_foods[:6]
                final_summary = format_recommendations_markdown(
                    intro=persona["breakfast_intro"],
                    foods=breakfast_foods,
                    language=active_lang,
                    query=query,
                    restrictions=restrictions,
                )
            else:
                final_summary = format_recommendations_markdown(
                    intro=intro_map.get(topic, persona["general_intro"]),
                    foods=safe_foods,
                    language=active_lang,
                    query=query,
                    restrictions=restrictions,
                )

        caution_text = None
        if topic == "iron_rich":
            caution_text = "Pair plant iron with Vitamin C (lemon or amla) to boost absorption, and keep tea/coffee 1-2 hours away from iron-rich meals."
        elif topic == "hair_health":
            caution_text = "Avoid crash dieting; inadequate protein or iron often worsens hair shedding."

        # Persist conversation and recommendation
        record_chat_message(
            db=db,
            user_id=user_id,
            session_id=session_id,
            user_query=query,
            genie_response=final_summary,
            language_code=active_lang,
            is_voice_input=is_voice,
            is_voice_output=is_voice,
            detected_language=detected_lang,
            intent=topic if not is_goal_intent else intent,
        )

        # Return top relevant cards (up to 20 for broad nutrition queries, 6 for focused meal queries)
        card_limit = 6 if meal_filter else 20
        cards = safe_foods[:card_limit]

        db_rec = record_recommendation(
            db=db,
            user_id=user_id,
            query=query,
            summary=final_summary,
            intent=topic if not is_goal_intent else intent,
            language=active_lang,
            recommended_foods=[r.model_dump() for r in cards],
            foods_to_avoid=[a.model_dump() for a in avoids],
            cautions=caution_text,
        )

        return RecommendationResponse(
            id=db_rec.id,
            query=query,
            language=active_lang,
            intent=topic if not is_goal_intent else intent,
            summary=final_summary,
            recommended_foods=cards,
            foods_to_avoid=avoids,
            restrictions=restrictions,
            cautions=caution_text,
            doctor_referral=res_analysis.doctor_referral,
            created_at=db_rec.created_at,
        )


genie_ai = GenieAIService()
