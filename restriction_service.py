import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from schema_recommendation import FoodRestrictionItem, RestrictionAnalysisResponse

logger = logging.getLogger("restriction_service")

# Comprehensive Knowledge Base of Clinically Verified Food Restrictions
# Categorized into:
# 1. Allergies (IgE-mediated & severe hypersensitivities)
# 2. Intolerances (Enzymatic / digestive malabsorption)
# 3. Dietary Preferences (Vegetarian, Vegan, Flexitarian)
# 4. Medical Conditions (Diabetes, Hypertension, Thyroid, PCOS, Kidney Stones, GERD, Anemia)
# 5. Medication-Food Interactions (Warfarin, Statins, Levothyroxine, Metformin, MAOIs, ACE Inhibitors)

RESTRICTION_DATABASE = {
    # ------------------ ALLERGIES (Medically Necessary / Critical) ------------------
    "allergy_peanuts": {
        "id": "allergy_peanuts",
        "category": "allergy",
        "restriction_type": "medically_necessary",
        "severity": "critical",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Peanuts, Peanut Butter & Peanut Oils",
                "reason": "Peanut proteins (Ara h 1-8) trigger severe IgE-mediated immune reactions, potentially causing airway constriction, facial swelling, or anaphylaxis.",
                "safe_alternatives": ["Sunflower seed butter", "Roasted pumpkin seeds", "Roasted watermelon seeds", "Roasted chana (Bengal gram)"],
                "clinical_note": "Strict lifelong avoidance is medically necessary. Always inspect food packaging for peanut traces and carry an emergency auto-injector if prescribed."
            },
            "te": {
                "food_name": "వేరుశనగలు, పల్లీ నూనె & పల్లీ వెన్న",
                "reason": "వేరుశనగలోని ప్రోటీన్లు తీవ్రమైన అలెర్జీ ప్రతిచర్యలను ప్రేరేపించి శ్వాస తీసుకోవడంలో ఇబ్బంది లేదా అనాఫిలాక్సిస్ వంటి ప్రమాదాన్ని కలిగిస్తాయి.",
                "safe_alternatives": ["పొద్దుతిరుగుడు గింజలు", "గుమ్మడి గింజలు", "వేయించిన పుచ్చకాయ గింజలు", "వేయించిన పుట్నాలు (శనగలు)"],
                "clinical_note": "వేరుశనగ అలెర్జీ ఉన్నవారు వీటిని పూర్తిగా నివారించాలి. వైద్యుల సూచనలను తప్పక పాటించండి."
            },
            "hi": {
                "food_name": "मूंगफली, पीनट बटर और मूंगफली का तेल",
                "reason": "मूंगफली के प्रोटीन गंभीर एलर्जी और सांस लेने में कठिनाई जैसी गंभीर समस्याएं पैदा कर सकते हैं।",
                "safe_alternatives": ["सूरजमुखी के बीज", "कद्दू के बीज", "तरबूज के बीज", "भुने हुए चने"],
                "clinical_note": "मूंगफली की एलर्जी में इसे पूरी तरह टालना चिकित्सीय रूप से अनिवार्य है।"
            },
            "ta": {
                "food_name": "வேர்க்கடலை மற்றும் வேர்க்கடலை எண்ணெய்",
                "reason": "வேர்க்கடலை புரதங்கள் கடுமையான ஒவ்வாமையை ஏற்படுத்தி மூச்சுத்திணறல் உருவாக்கக்கூடும்.",
                "safe_alternatives": ["சூரியகாந்தி விதைகள்", "பூசணி விதைகள்", "பொட்டுக்கடலை"],
                "clinical_note": "ஒவ்வாமை உள்ளவர்கள் இதைத் தவிர்ப்பது கட்டாயமாகும்."
            },
            "kn": {
                "food_name": "ಕಡಲೆಕಾಯಿ ಮತ್ತು ಕಡಲೆಕಾಯಿ ಎಣ್ಣೆ",
                "reason": "ಕಡಲೆಕಾಯಿ ಪ್ರೋಟೀನ್ಗಳು ತೀವ್ರ ಅಲರ್ಜಿಯನ್ನು ಉಂಟುಮಾಡಬಹುದು.",
                "safe_alternatives": ["ಸೂರ್ಯಕಾಂತಿ ಬೀಜಗಳು", "ಕುಂಬಳಕಾಯಿ ಬೀಜಗಳು", "ಹುರಿಗಡಲೆ"],
                "clinical_note": "ಅಲರ್ಜಿ ಇರುವವರು ಕಡ್ಡಾಯವಾಗಿ ಇದನ್ನು ತ್ಯಜಿಸಬೇಕು."
            }
        }
    },
    "allergy_gluten": {
        "id": "allergy_gluten",
        "category": "allergy",
        "restriction_type": "medically_necessary",
        "severity": "critical",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Wheat, Maida, Semolina (Sooji), Barley & Rye",
                "reason": "Gluten peptides trigger autoimmune-mediated destruction of intestinal villi in Celiac disease, leading to severe chronic malabsorption and gut inflammation.",
                "safe_alternatives": ["Ragi (Finger Millet)", "Jowar (Sorghum)", "Bajra (Pearl Millet)", "Brown Rice", "Quinoa", "Buckwheat (Kuttu)"],
                "clinical_note": "A strict zero-gluten diet is clinically mandatory for Celiac disease. Consult a gastroenterologist for gut mucosal health monitoring."
            },
            "te": {
                "food_name": "గోధుమలు, మైదా, ఉప్మా రవ్వ (నూక), బార్లీ",
                "reason": "గ్లూటెన్ ఉన్న గోధుమలు సెలియాక్ వ్యాధి ఉన్నవారిలో పేగుల గోడలను దెబ్బతీసి పోషకాల లోపానికి కారణమవుతాయి.",
                "safe_alternatives": ["రాగులు", "జొన్నలు", "సజ్జలు", "ముడి బియ్యం (బ్రౌన్ రైస్)", "కొర్రలు"],
                "clinical_note": "సెలియాక్ సమస్య ఉన్నవారు గ్లూటెన్ లేని ఆహారాన్ని మాత్రమే తీసుకోవాలి."
            },
            "hi": {
                "food_name": "गेहूं, मैदा, सूजी, जौ और राई",
                "reason": "ग्लूटेन सीलिएक रोग में आंतों की परत को नुकसान पहुंचाता है और पाचन तंत्र को गंभीर रूप से प्रभावित करता है।",
                "safe_alternatives": ["रागी", "ज्वार", "बाजरा", "ब्राउन राइस", "कुट्टू का आटा"],
                "clinical_note": "सीलिएक रोग में 100% ग्लूटेन-मुक्त आहार चिकित्सकीय रूप से अनिवार्य है।"
            },
            "ta": {
                "food_name": "கோதுமை, மைதா மற்றும் ரவை",
                "reason": "செலியாக் நோய் உள்ளவர்களுக்கு குடல் சுவர்களைப் பாதித்து ஊட்டச்சத்து குறைபாட்டை உண்டாக்கும்.",
                "safe_alternatives": ["கேழ்வரகு (ராகி)", "சோளம்", "கம்பு", "கைக்குத்தல் அரிசி"],
                "clinical_note": "முழுமையாக பசையம் (Gluten) அற்ற உணவுகளை மட்டுமே தேர்ந்தெடுக்கவும்."
            },
            "kn": {
                "food_name": "ಗೋಧಿ, ಮೈದಾ ಮತ್ತು ರವೆ",
                "reason": "ಗ್ಲುಟನ್ ಅಲರ್ಜಿ ಇರುವವರಲ್ಲಿ ಕರುಳಿನ ತೊಂದರೆಗೆ ಕಾರಣವಾಗುತ್ತದೆ.",
                "safe_alternatives": ["ರಾಗಿ", "ಜೋಳ", "ಸಜ್ಜೆ", "ಕುಚುಲಕ್ಕಿ"],
                "clinical_note": "ಗ್ಲುಟನ್ ರಹಿತ ಪರ್ಯಾಯ ಧಾನ್ಯಗಳನ್ನು ಬಳಸುವುದು ಸೂಕ್ತ."
            }
        }
    },
    "allergy_dairy": {
        "id": "allergy_dairy",
        "category": "allergy",
        "restriction_type": "medically_necessary",
        "severity": "high",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Cow's Milk, Casein, Whey, Paneer & Butter",
                "reason": "Casein and beta-lactoglobulin proteins elicit immunological mast cell activation, resulting in hives, facial eczema, or gastrointestinal bleeding.",
                "safe_alternatives": ["Almond milk", "Oat milk", "Coconut milk", "Calcium-set tofu", "Fortified soy beverage"],
                "clinical_note": "True dairy allergy is distinct from lactose intolerance and requires complete elimination of milk proteins from all meals."
            },
            "te": {
                "food_name": "ఆవు పాలు, పనీర్, చీజ్ మరియు పాల ఉత్పత్తులు",
                "reason": "పాలలో ఉండే కేసిన్ ప్రోటీన్ వల్ల రోగనిరోధక వ్యవస్థ ప్రతికూలంగా స్పందించి దురదలు, దద్దుర్లు కలిగిస్తుంది.",
                "safe_alternatives": ["బాదం పాలు", "కొబ్బరి పాలు", "ఓట్స్ పాలు", "టోఫు (సోయా పనీర్)"],
                "clinical_note": "పాల ప్రోటీన్ అలెర్జీ ఉన్నవారు పాల పదార్థాలను పూర్తిగా దూరంగా ఉంచాలి."
            },
            "hi": {
                "food_name": "गाय का दूध, पनीर, मक्खन और सभी दुग्ध उत्पाद",
                "reason": "दूध के प्रोटीन (केसीन) से गंभीर एलर्जी, खुजली और पेट की समस्याएं हो सकती हैं।",
                "safe_alternatives": ["बादाम का दूध", "नारियल का दूध", "ओट्स का दूध", "टोफू"],
                "clinical_note": "दूध की एलर्जी होने पर सभी डेयरी उत्पादों से परहेज करना अनिवार्य है।"
            },
            "ta": {
                "food_name": "பால், பன்னீர் மற்றும் பால் பொருட்கள்",
                "reason": "பால் புரதங்கள் தோல் அலர்ஜி மற்றும் செரிமானக் கோளாறுகளை உண்டாக்கும்.",
                "safe_alternatives": ["பாதாம் பால்", "தேங்காய்ப்பால்", "டோஃபு"],
                "clinical_note": "பால் ஒவ்வாமை உள்ளவர்கள் தாவர அடிப்படையிலான பாலைப் பயன்படுத்தலாம்."
            },
            "kn": {
                "food_name": "ಹಾಲು, ಪನೀರ್ ಮತ್ತು ಹಾಲಿನ ಉತ್ಪನ್ನಗಳು",
                "reason": "ಹಾಲಿನಲ್ಲಿರುವ ಪ್ರೋಟೀನ್ ಅಲರ್ಜಿ ಮತ್ತು ಚರ್ಮದ ತುರಿಕೆಗೆ ಕಾರಣವಾಗುತ್ತದೆ.",
                "safe_alternatives": ["ಬಾದಾಮಿ ಹಾಲು", "ತೆಂಗಿನ ಹಾಲು", "ಟೋಫು"],
                "clinical_note": "ಹಾಲಿನ ಉತ್ಪನ್ನಗಳ ಬದಲಿಗೆ ಸಸ್ಯಜನ್ಯ ಹಾಲು ಬಳಸುವುದು ಉತ್ತಮ."
            }
        }
    },
    "allergy_shellfish": {
        "id": "allergy_shellfish",
        "category": "allergy",
        "restriction_type": "medically_necessary",
        "severity": "critical",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Prawns, Shrimps, Crabs, Lobsters & Oysters",
                "reason": "Tropomyosin muscle proteins in shellfish cause immediate high-affinity IgE antibody binding, triggering severe bronchospasms and anaphylactic shock.",
                "safe_alternatives": ["Flaxseeds, chia seeds, and walnuts for Omega-3 fatty acids", "Algal DHA oils"],
                "clinical_note": "Medical emergency risk. If accidental ingestion causes difficulty breathing, contact emergency medical services immediately."
            },
            "te": {
                "food_name": "రొయ్యలు, పీతలు మరియు సముద్రపు గుల్లలు",
                "reason": "వీటిలోని ట్రోపోమయోసిన్ ప్రోటీన్ అత్యంత వేగంగా అలెర్జీ ప్రతిచర్యను మరియు శ్వాస నిరోధాన్ని కలిగిస్తుంది.",
                "safe_alternatives": ["అవిసె గింజలు", "చియా గింజలు", "వాల్ నట్స్ (ఒమేగా-3 కోసం)"],
                "clinical_note": "సముద్రపు రొయ్యలు, పీతల అలెర్జీ ఉన్నవారు వీటిని పూర్తిగా విసర్జించాలి."
            },
            "hi": {
                "food_name": "झींगा, केकड़ा और समुद्री सीप",
                "reason": "इनमें मौजूद प्रोटीन से तेजी से सांस लेने में तकलीफ और गंभीर एलर्जी हो सकती है।",
                "safe_alternatives": ["अलसी के बीज", "चिया के बीज", "अखरोट"],
                "clinical_note": "शेलफिश एलर्जी बहुत गंभीर होती है, तुरंत डॉक्टर से संपर्क करें।"
            },
            "ta": {
                "food_name": "இறால், நண்டு மற்றும் கடல் உணவுகள்",
                "reason": "கடுமையான ஒவ்வாமை மற்றும் மூச்சுத்திணறலை உடனடியாக உண்டாக்கும் அபாயம் உள்ளது.",
                "safe_alternatives": ["ஆளி விதைகள்", "சியா விதைகள்", "அக்ரூட் பருப்பு"],
                "clinical_note": "இதை முழுமையாகத் தவிர்ப்பது உயிர் காக்கும் நடவடிக்கையாகும்."
            },
            "kn": {
                "food_name": "ಸೀಗಡಿ, ಏಡಿ ಮತ್ತು ಕಡಲ ಚಿಪ್ಪುಗಳು",
                "reason": "ತೀವ್ರ ಅಲರ್ಜಿ ಮತ್ತು ಉಸಿರಾಟದ ಸಮಸ್ಯೆಯನ್ನು ತರಬಹುದು.",
                "safe_alternatives": ["ಅಗಸೆ ಬೀಜಗಳು", "ಚಿಯಾ ಬೀಜಗಳು", "ಅಕ್ರೋಟು"],
                "clinical_note": "ಇದರಿಂದ ಸಂಪೂರ್ಣ ದೂರವಿರುವುದು ಅವಶ್ಯಕ."
            }
        }
    },
    "allergy_soy": {
        "id": "allergy_soy",
        "category": "allergy",
        "restriction_type": "medically_necessary",
        "severity": "high",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Soybeans, Soy Chunks, Edamame, Tofu & Soy Sauce",
                "reason": "Soy storage globulins (Gly m 5, Gly m 6) induce cross-reactive mast cell degranulation, triggering atopic dermatitis and gut inflammation.",
                "safe_alternatives": ["Moong dal (Green gram)", "Chana dal (Chickpea lentils)", "Sprouted pulses", "Hemp seeds"],
                "clinical_note": "Check ingredient lists for hidden soy derivatives including hydrolyzed vegetable protein (HVP) and soy lecithin."
            },
            "te": {
                "food_name": "సోయాబీన్స్, సోయా చంక్స్, టోఫు మరియు సోయా సాస్",
                "reason": "సోయాలోని గ్లోబులిన్ ప్రోటీన్లు రోగనిరోధక వ్యవస్థను ప్రేరేపించి చర్మ సమస్యలు, జీర్ణ సమస్యలకు దారితీస్తాయి.",
                "safe_alternatives": ["పెసరపప్పు", "శనగపప్పు", "మొలకెత్తిన గింజలు", "కందిపప్పు"],
                "clinical_note": "ప్యాక్ చేసిన ఆహారాల్లో సోయా ఉత్పత్తులు లేకుండా చూసుకోండి."
            },
            "hi": {
                "food_name": "सोयाबीन, सोया चंक्स, टोफू और सोया सॉस",
                "reason": "सोया प्रोटीन से त्वचा पर लाल चकत्ते और पेट में सूजन हो सकती है।",
                "safe_alternatives": ["मूंग की दाल", "चना दाल", "अंकुरित दालें"],
                "clinical_note": "पैकेटबंद खाद्य पदार्थों में सोया के अंश की जांच अवश्य करें।"
            },
            "ta": {
                "food_name": "சோயாபீன்ஸ், டோஃபு மற்றும் சோயா பொருட்கள்",
                "reason": "தோல் வெடிப்புகள் மற்றும் குடல் அலர்ஜியை ஏற்படுத்தக்கூடும்.",
                "safe_alternatives": ["பாசிப்பருப்பு", "கடலைப்பருப்பு", "முளைகட்டிய பயிர்கள்"],
                "clinical_note": "சோயா பொருட்கள் இல்லாத உணவுகளைத் தேர்ந்தெடுக்கவும்."
            },
            "kn": {
                "food_name": "ಸೋಯಾಬೀನ್, ಸೋಯಾ ಚಂಕ್ಸ್ ಮತ್ತು ಟೋಫು",
                "reason": "ಚರ್ಮದ ತೊಂದರೆ ಮತ್ತು ಅಲರ್ಜಿಗೆ ಕಾರಣವಾಗಬಹುದು.",
                "safe_alternatives": ["ಹೆಸರುಬೇಳೆ", "ಕಡಲೆಬೇಳೆ", "ಮೊಳಕೆ ಕಾಳುಗಳು"],
                "clinical_note": "ಪರ್ಯಾಯ ಕಾಳುಗಳನ್ನು ಸೇವಿಸುವುದು ಉತ್ತಮ."
            }
        }
    },
    "allergy_eggs": {
        "id": "allergy_eggs",
        "category": "allergy",
        "restriction_type": "medically_necessary",
        "severity": "high",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Whole Eggs, Egg Whites (Ovalbumin) & Mayonnaise",
                "reason": "Ovalbumin and ovomucoid proteins are resistant to heat and digestion, causing mucosal antibody synthesis and respiratory or dermatological symptoms.",
                "safe_alternatives": ["Aquafaba (Chickpea water)", "Soaked chia seeds gel", "Mashed ripe bananas for baking", "Paneer (if dairy tolerated) or Tofu"],
                "clinical_note": "Medically indicated restriction. Ensure baked goods and confectioneries do not contain hidden egg albumins."
            },
            "te": {
                "food_name": "కోడిగుడ్లు, ఎగ్ వైట్ మరియు మయోనైజ్",
                "reason": "గుడ్డులోని ఓవల్బుమిన్ ప్రోటీన్ చర్మంపై దద్దుర్లు, కడుపు నొప్పి మరియు శ్వాసకోశ అలెర్జీలను రేకెత్తిస్తుంది.",
                "safe_alternatives": ["నానబెట్టిన చియా విత్తనాలు", "అరటిపండు గుజ్జు", "పనీర్ లేదా టోఫు"],
                "clinical_note": "గుడ్డు అలెర్జీ ఉన్నవారు బేకరీ ఉత్పత్తులను తీసుకునేటప్పుడు జాగ్రత్త వహించాలి."
            },
            "hi": {
                "food_name": "अंडे, अंडे की सफेदी और मेयोनेज़",
                "reason": "अंडे के प्रोटीन से त्वचा पर पित्ती और पेट दर्द जैसी एलर्जी हो सकती है।",
                "safe_alternatives": ["भीगे हुए चिया बीज", "पका हुआ केला", "पनीर या टोफू"],
                "clinical_note": "अंडे की एलर्जी होने पर बेकरी उत्पादों की सामग्री ध्यान से पढ़ें।"
            },
            "ta": {
                "food_name": "முட்டை மற்றும் மயோனைஸ்",
                "reason": "முட்டை புரதங்கள் வயிற்று வலி மற்றும் ஒவ்வாமை தோல் தடிப்புகளை உண்டாக்கும்.",
                "safe_alternatives": ["சியா விதைகள்", "வாழைப்பழக் கூழ்", "பன்னீர்"],
                "clinical_note": "முட்டை ஒவ்வாமை உள்ளவர்கள் இதைத் தவிர்க்கவும்."
            },
            "kn": {
                "food_name": "ಮೊಟ್ಟೆ ಮತ್ತು ಮಯೋನೈಸ್",
                "reason": "ಮೊಟ್ಟೆಯ ಪ್ರೋಟೀನ್ ಹೊಟ್ಟೆ ನೋವು ಮತ್ತು ಅಲರ್ಜಿಗೆ ಕಾರಣವಾಗಬಹುದು.",
                "safe_alternatives": ["ಚಿಯಾ ಬೀಜಗಳು", "ಬಾಳೆಹಣ್ಣು", "ಪನೀರ್"],
                "clinical_note": "ಮೊಟ್ಟೆ ಅಲರ್ಜಿ ಇದ್ದರೆ ಪರ್ಯಾಯ ಆಹಾರ ಆರಿಸಿಕೊಳ್ಳಿ."
            }
        }
    },

    # ------------------ INTOLERANCES (Enzymatic / Digestive) ------------------
    "intolerance_lactose": {
        "id": "intolerance_lactose",
        "category": "intolerance",
        "restriction_type": "general_suggestion",
        "severity": "moderate",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Liquid Cow/Buffalo Milk, Ice Cream & Soft Cheeses",
                "reason": "Low intestinal lactase enzyme prevents lactose breakdown; unabsorbed sugar ferments in the colon, producing gas, bloating, and osmotic cramps.",
                "safe_alternatives": ["Traditional cultured curd / dahi (probiotics pre-digest lactose)", "Lactose-free milk", "Ghee (virtually lactose-free)", "Almond/oat milk"],
                "clinical_note": "Lactose intolerance is not life-threatening. Cultured fermented curd and aged cheeses are generally well tolerated by most individuals."
            },
            "te": {
                "food_name": "పచ్చి ఆవు/గేదె పాలు, ఐస్ క్రీం మరియు మెత్తని చీజ్",
                "reason": "లాక్టేజ్ ఎంజైమ్ లోపం వల్ల పాలలోని చక్కెర సరిగ్గా జీర్ణం కాక కడుపుబ్బరం, గ్యాస్ మరియు అజీర్తిని కలిగిస్తుంది.",
                "safe_alternatives": ["సహజంగా తోడుపెట్టిన పెరుగు (లాక్టోస్ ముందే జీర్ణమవుతుంది)", "లాక్టోస్-ఫ్రీ పాలు", "స్వచ్ఛమైన నెయ్యి", "బాదం పాలు"],
                "clinical_note": "ఇది ప్రాణాంతకమైన అలెర్జీ కాదు. పెరుగు మరియు నెయ్యి సాధారణంగా సమస్య లేకుండా పడతాయి."
            },
            "hi": {
                "food_name": "ताजा दूध, आइसक्रीम और सॉफ्ट चीज",
                "reason": "लैक्टेज एंजाइम की कमी के कारण दूध की शर्करा पच नहीं पाती, जिससे पेट फूलना और गैस की समस्या होती है।",
                "safe_alternatives": ["पारंपरिक दही (जिसमें लैक्टोज पहले से पच जाता है)", "लैक्टोज-मुक्त दूध", "देसी घी", "बादाम का दूध"],
                "clinical_note": "यह कोई खतरनाक एलर्जी नहीं है। अधिकांश लोग आसानी से दही और घी पचा लेते हैं।"
            },
            "ta": {
                "food_name": "பசும்பால் மற்றும் ஐஸ்கிரீம்",
                "reason": "லாக்டோஸ் சர்க்கரையை ஜீரணிக்க முடியாததால் வயிறு உப்பசம் மற்றும் வாயு தொல்லை ஏற்படும்.",
                "safe_alternatives": ["பாரம்பரிய தயிர்", "லாக்டோஸ் இல்லாத பால்", "நெய்"],
                "clinical_note": "தயிர் மற்றும் நெய் பெரும்பாலும் செரிமானத்திற்கு உகந்தவை."
            },
            "kn": {
                "food_name": "ಹಸಿ ಹಾಲು ಮತ್ತು ಐಸ್ ಕ್ರೀಮ್",
                "reason": "ಲ್ಯಾಕ್ಟೋಸ್ ಜೀರ್ಣವಾಗದೆ ಹೊಟ್ಟೆ ಉಬ್ಬರ ಮತ್ತು ಗ್ಯಾಸ್ ಉಂಟಾಗುತ್ತದೆ.",
                "safe_alternatives": ["ಮಜ್ಜಿಗೆ ಮತ್ತು ಮೊಸರು", "ಲ್ಯಾಕ್ಟೋಸ್ ರಹಿತ ಹಾಲು", "ತುಪ್ಪ"],
                "clinical_note": "ಮೊಸರು ಮತ್ತು ತುಪ್ಪ ಸುಲಭವಾಗಿ ಜೀರ್ಣವಾಗುತ್ತವೆ."
            }
        }
    },
    "intolerance_histamine": {
        "id": "intolerance_histamine",
        "category": "intolerance",
        "restriction_type": "general_suggestion",
        "severity": "moderate",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Aged Cheeses, Fermented Pickles, Cured Meats & Wine",
                "reason": "Impaired diamine oxidase (DAO) enzyme activity delays degradation of dietary histamines, triggering sudden facial flushing, headaches, and gut motility issues.",
                "safe_alternatives": ["Freshly cooked whole foods", "Fresh green leafy vegetables", "Freshly cooked dal", "Unfermented fresh milk/curd"],
                "clinical_note": "Cook meals fresh daily and avoid repeatedly reheating high-protein leftovers."
            },
            "te": {
                "food_name": "నిల్వ ఉంచిన ఊరగాయలు, పులియబెట్టిన ఆహారాలు & నిల్వ చేసిన మాంసం",
                "reason": "హిస్టామైన్ నిర్విషీకరణ ఎంజైమ్ తక్కువగా ఉండటం వల్ల తలనొప్పి, చర్మం ఎర్రబడటం మరియు అజీర్తి వస్తాయి.",
                "safe_alternatives": ["రోజూ తాజాగా వండిన ఆహారాలు", "తాజా కూరగాయలు", "తాజా పప్పుధాన్యాలు"],
                "clinical_note": "ఎప్పటికప్పుడు తాజాగా వండిన ఆహారాన్ని మాత్రమే తీసుకోవడం మంచిది."
            },
            "hi": {
                "food_name": "पुराना अचार, बहुत दिनों का रखा पनीर और बासी भोजन",
                "reason": "हिस्टामाइन पचाने वाले एंजाइम की कमी से सिरदर्द, त्वचा का लाल होना और बेचैनी हो सकती है।",
                "safe_alternatives": ["रोज ताजा बना भोजन", "ताजी हरी सब्जियां", "ताजा दाल"],
                "clinical_note": "हमेशा ताजा पका हुआ भोजन खाएं और बासी खाने से बचें।"
            },
            "ta": {
                "food_name": "பழைய ஊறுகாய் மற்றும் நொதிக்க வைக்கப்பட்ட உணவுகள்",
                "reason": "ஹிஸ்டமைன் அதிகரிப்பால் தலைவலி மற்றும் செரிமானக் கோளாறுகள் வரலாம்.",
                "safe_alternatives": ["தினமும் சமைக்கும் புதிய உணவுகள்", "புதிய காய்கறிகள்"],
                "clinical_note": "புதிய சமைத்த உணவுகளை மட்டுமே உண்பது நல்லது."
            },
            "kn": {
                "food_name": "ಹಳಸಿದ ಉಪ್ಪಿನಕಾಯಿ ಮತ್ತು ಹಳೆಯ ಆಹಾರಗಳು",
                "reason": "ಹಿಸ್ಟಮೈನ್ ಹೆಚ್ಚಳದಿಂದ ತಲೆನೋವು ಮತ್ತು ಹೊಟ್ಟೆಯ ತೊಂದರೆ ಉಂಟಾಗುತ್ತದೆ.",
                "safe_alternatives": ["ತಾಜಾ ಅಡುಗೆ", "ತಾಜಾ ತರಕಾರಿಗಳು ಮತ್ತು ಬೇಳೆಕಾಳುಗಳು"],
                "clinical_note": "ಯಾವಾಗಲೂ ತಾಜಾ ಆಹಾರ ಸೇವಿಸುವುದು ಸೂಕ್ತ."
            }
        }
    },

    # ------------------ DIETARY PREFERENCES ------------------
    "preference_vegetarian": {
        "id": "preference_vegetarian",
        "category": "dietary_preference",
        "restriction_type": "general_suggestion",
        "severity": "mild",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Meat, Poultry, Seafood, Animal Gelatin & Animal Rennet",
                "reason": "Excluded in alignment with your personal and cultural vegetarian nutritional principles.",
                "safe_alternatives": ["Moong dal, Chana dal & Rajma", "Fresh Paneer", "Sprouted legumes", "Almonds and Walnuts for healthy fats"],
                "clinical_note": "A balanced vegetarian diet is highly cardio-protective. Ensure regular intake of Vitamin B12 and iron through legumes and dairy."
            },
            "te": {
                "food_name": "మాంసం, చికెన్, చేపలు, గుడ్లు మరియు సీఫుడ్",
                "reason": "మీ శాకాహార జీవన విధానం మరియు ప్రాధాన్యతలకు అనుగుణంగా వీటిని మినహాయించడమైనది.",
                "safe_alternatives": ["పెసరపప్పు, శనగలు, రాజ్మా", "తాజా పనీర్", "మొలకెత్తిన గింజలు", "బాదం మరియు వాల్ నట్స్"],
                "clinical_note": "శాకాహారం ఎంతో ఆరోగ్యకరమైనది. పప్పుధాన్యాల ద్వారా తగినంత ప్రోటీన్ మరియు విటమిన్ బి12 పొందేలా చూసుకోండి."
            },
            "hi": {
                "food_name": "मांस, चिकन, मछली और समुद्री भोजन",
                "reason": "आपकी व्यक्तिगत शाकाहारी जीवनशैली और प्राथमिकताओं के अनुसार इन्हें हटाया गया है।",
                "safe_alternatives": ["दालें, छोले और राजमा", "ताजा पनीर", "अंकुरित अनाज", "मेवे"],
                "clinical_note": "शाकाहारी भोजन दिल के लिए बेहतरीन है। दालों और डेयरी से पर्याप्त प्रोटीन लेते रहें।"
            },
            "ta": {
                "food_name": "அசைவ உணவுகள், இறைச்சி மற்றும் மீன்",
                "reason": "உங்கள் சைவ உணவு விருப்பத்திற்கு ஏற்ப பரிந்துரைக்கப்படுகிறது.",
                "safe_alternatives": ["பருப்பு வகைகள், கொண்டைக்கடலை", "பன்னீர்", "முளைகட்டிய பயிர்கள்"],
                "clinical_note": "சைவ உணவில் போதுமான புரதச்சத்தை பருப்பு வகைகள் மூலம் பெறலாம்."
            },
            "kn": {
                "food_name": "ಮಾಂಸಾಹಾರ, ಚಿಕನ್ ಮತ್ತು ಮೀನು",
                "reason": "ನಿಮ್ಮ ಸಸ್ಯಾಹಾರಿ ಆಯ್ಕೆಗೆ ಅನುಗುಣವಾಗಿ ಇವುಗಳನ್ನು ಹೊರತುಪಡಿಸಲಾಗಿದೆ.",
                "safe_alternatives": ["ಬೇಳೆಕಾಳುಗಳು, ಕಡಲೆ", "ಪನೀರ್", "ಮೊಳಕೆ ಕಾಳುಗಳು"],
                "clinical_note": "ಸಸ್ಯಾಹಾರವು ಉತ್ತಮ ಆರೋಗ್ಯ ನೀಡುತ್ತದೆ. ಬೇಳೆಕಾಳುಗಳ ಮೂಲಕ ಪ್ರೋಟೀನ್ ಪಡೆಯಿರಿ."
            }
        }
    },
    "preference_vegan": {
        "id": "preference_vegan",
        "category": "dietary_preference",
        "restriction_type": "general_suggestion",
        "severity": "mild",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "All Animal Products: Dairy, Paneer, Ghee, Honey & Eggs",
                "reason": "Excluded in strict adherence to a plant-based vegan lifestyle free of animal exploitation.",
                "safe_alternatives": ["Fortified Soy Milk & Tofu", "Nutritional Yeast (for B-vitamins)", "Lentils, Chickpeas & Ragi", "Chia & Flaxseed gel"],
                "clinical_note": "A 100% plant-based diet benefits from periodic Vitamin B12 and Vitamin D testing under medical guidance."
            },
            "te": {
                "food_name": "జంతు సంబంధిత ఆహారాలు: పాలు, పనీర్, నెయ్యి, తేనె మరియు గుడ్లు",
                "reason": "మీ సంపూర్ణ మొక్కల ఆధారిత వీగన్ (Vegan) జీవనశైలికి అనుగుణంగా వీటిని నివారించడమైనది.",
                "safe_alternatives": ["టోఫు మరియు సోయా పాలు", "పప్పుధాన్యాలు, రాగులు", "చియా మరియు అవిసె గింజలు"],
                "clinical_note": "వీగన్ ఆహారంలో విటమిన్ B12 తగినంతగా ఉండేలా వైద్యుల సలహా తీసుకోవడం శ్రేయస్కరం."
            },
            "hi": {
                "food_name": "दूध, दही, पनीर, घी, शहद और अंडे",
                "reason": "आपकी वीगन (पूर्णतः पादप-आधारित) जीवनशैली के अनुसार इन्हें शामिल नहीं किया गया है।",
                "safe_alternatives": ["टोफू और सोया दूध", "दालें और रागी", "चिया और अलसी के बीज"],
                "clinical_note": "वीगन आहार में विटामिन बी12 की नियमित जांच जरूर करवाएं।"
            },
            "ta": {
                "food_name": "பால், நெய், தேன் மற்றும் முட்டை",
                "reason": "உங்கள் தாவர அடிப்படையிலான வீகன் வாழ்க்கை முறைக்கு ஏற்ப தவிர்க்கப்படுகிறது.",
                "safe_alternatives": ["சோயா பால், டோஃபு", "பருப்பு வகைகள்", "ஆளி விதைகள்"],
                "clinical_note": "வைட்டமின் பி12 அளவை சீராகப் பராமரிக்க மருத்துவர் ஆலோசனை பெறவும்."
            },
            "kn": {
                "food_name": "ಹಾಲು, ತುಪ್ಪ, ಜೇನುತುಪ್ಪ ಮತ್ತು ಮೊಟ್ಟೆ",
                "reason": "ನಿಮ್ಮ ಸಸ್ಯಜನ್ಯ ವೀಗನ್ ಆಹಾರ ಪದ್ಧತಿಗೆ ಅನುಗುಣವಾಗಿ ಇವುಗಳನ್ನು ಹೊರಗಿಡಲಾಗಿದೆ.",
                "safe_alternatives": ["ಸೋಯಾ ಹಾಲು, ಟೋಫು", "ಕಾಳುಗಳು ಮತ್ತು ರಾಗಿ", "ಅಗಸೆ ಬೀಜಗಳು"],
                "clinical_note": "ವಿಟಮಿನ್ ಬಿ12 ಮಟ್ಟವನ್ನು ಪರೀಕ್ಷಿಸಿಕೊಳ್ಳುವುದು ಸೂಕ್ತ."
            }
        }
    },

    # ------------------ MEDICAL CONDITIONS ------------------
    "condition_diabetes": {
        "id": "condition_diabetes",
        "category": "medical_condition",
        "restriction_type": "medically_necessary",
        "severity": "high",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Refined Sugars, Maida, White Bread, Packaged Fruit Juices & Sweets",
                "reason": "High-glycemic simple carbohydrates digest rapidly, precipitating sharp postprandial glucose excursions and pancreatic beta-cell strain.",
                "safe_alternatives": ["Whole sprouted moong", "Finger millet (Ragi in moderate portions)", "Foxtail millet", "Methi seeds & Karela (Bitter gourd)", "Roasted chana"],
                "clinical_note": "Dietary adjustments must be coordinated with blood sugar monitoring and physician guidance to avoid hypoglycemia."
            },
            "te": {
                "food_name": "తెల్ల చక్కెర, మైదా, వైట్ బ్రెడ్, తియ్యటి పండ్ల రసాలు & స్వీట్లు",
                "reason": "ఇవి రక్తంలో గ్లూకోజ్ స్థాయిలను అత్యంత వేగంగా పెంచి ఇన్సులిన్ నిరోధకతను మరింత తీవ్రతరం చేస్తాయి.",
                "safe_alternatives": ["మొలకెత్తిన పెసలు", "రాగులు (పరిమితంగా)", "కొర్రలు", "మెంతులు & కాకరకాయ", "వేయించిన శనగలు"],
                "clinical_note": "షుగర్ ఉన్నవారు రక్తంలో చక్కెర స్థాయిలను క్రమం తప్పకుండా పర్యవేక్షించుకుంటూ వైద్యుల సలహా తీసుకోవాలి."
            },
            "hi": {
                "food_name": "सफेद चीनी, मैदा, सफेद ब्रेड, पैकेटबंद जूस और मिठाइयां",
                "reason": "हाई ग्लाइसेमिक इंडेक्स वाले ये खाद्य पदार्थ रक्त शर्करा को अचानक बहुत तेज बढ़ा देते हैं।",
                "safe_alternatives": ["अंकुरित मूंग", "रागी (सीमित मात्रा में)", "बाजरा व ज्वार", "मेथी दाना और करेला", "भुना चना"],
                "clinical_note": "मधुमेह के रोगियों को अपने शर्करा स्तर की नियमित जांच करनी चाहिए।"
            },
            "ta": {
                "food_name": "சர்க்கரை, மைதா, வெள்ளை ரொட்டி மற்றும் இனிப்புகள்",
                "reason": "இரத்தத்தில் சர்க்கரை அளவை உடனடியாக உயர்த்தி நீரிழிவை மோசமாக்கும்.",
                "safe_alternatives": ["முளைகட்டிய பயிறு", "கேழ்வரகு", "திணை", "வெந்தயம் மற்றும் பாகற்காய்"],
                "clinical_note": "இரத்த சர்க்கரை அளவை சீராகப் பரிசோதித்துக் கொள்ளவும்."
            },
            "kn": {
                "food_name": "ಬಿಳಿ ಸಕ್ಕರೆ, ಮೈದಾ, ಬಿಳಿ ಬ್ರೆಡ್ ಮತ್ತು ಸಿಹಿತಿಂಡಿಗಳು",
                "reason": "ರಕ್ತದಲ್ಲಿನ ಸಕ್ಕರೆ ಮಟ್ಟವನ್ನು ಕ್ಷಿಪ್ರವಾಗಿ ಹೆಚ್ಚಿಸುತ್ತವೆ.",
                "safe_alternatives": ["ಮೊಳಕೆ ಹೆಸರುಕಾಳು", "ರಾಗಿ", "ನವಣೆ ಧಾನ್ಯ", "ಮೆಂತ್ಯ ಮತ್ತು ಹಾಗಲಕಾಯಿ"],
                "clinical_note": "ಮಧುಮೇಹಿಗಳು ಸಕ್ಕರೆ ಪ್ರಮಾಣವನ್ನು ಆಗಾಗ ಪರೀಕ್ಷಿಸಿಕೊಳ್ಳಬೇಕು."
            }
        }
    },
    "condition_hypertension": {
        "id": "condition_hypertension",
        "category": "medical_condition",
        "restriction_type": "medically_necessary",
        "severity": "high",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "High-Sodium Foods: Commercial Pickles (Achar), Papad, Salty Snacks & Canned Soups",
                "reason": "Excess sodium increases plasma osmolarity, expanding intravascular volume and elevating peripheral arterial resistance.",
                "safe_alternatives": ["Lemon juice, fresh amla, and roasted garlic for flavor", "Potassium-rich tender coconut water (if renal function normal)", "Unsalted roasted nuts"],
                "clinical_note": "Maintain daily dietary sodium under 2,000 mg (under 1 level teaspoon of salt). Adhere to DASH dietary principles under doctor supervision."
            },
            "te": {
                "food_name": "అధిక ఉప్పు ఉన్న ఊరగాయలు (ఆవకాయ), అప్పడాలు, ప్యాకేజ్డ్ ఉప్పు స్నాక్స్",
                "reason": "అధిక ఉప్పు రక్త నాళాలపై ఒత్తిడిని పెంచి రక్తపోటు (బీపీ) మరింత పెరిగేలా చేస్తుంది.",
                "safe_alternatives": ["నిమ్మరసం, తాజా ఉసిరి మరియు వేయించిన వెల్లుల్లి", "కొబ్బరి నీళ్లు (పొటాషియం సమృద్ధిగా)", "ఉప్పు లేని నట్స్"],
                "clinical_note": "రోజూ ఉప్పు వాడకాన్ని ఒక చిన్న చెంచా కంటే తక్కువకు పరిమితం చేసి, బీపీని క్రమం తప్పకుండా పరీక్షించుకోండి."
            },
            "hi": {
                "food_name": "अचार, पापड़, नमकीन और पैकेटबंद नमकीन स्नैक्स",
                "reason": "अत्यधिक सोडियम रक्त वाहिकाओं पर दबाव बढ़ाता है और उच्च रक्तचाप का कारण बनता है।",
                "safe_alternatives": ["नींबू का रस, ताजा आंवला और लहसुन", "नारियल पानी", "बिना नमक वाले भुने मेवे"],
                "clinical_note": "रोजाना नमक की मात्रा 1 चम्मच से कम रखें और बीपी की नियमित जांच करें।"
            },
            "ta": {
                "food_name": "ஊறுகாய், அப்பளம் மற்றும் அதிக உப்புள்ள நொறுக்குத் தீனிகள்",
                "reason": "அதிக சோடியம் இரத்த அழுத்தத்தை தீவிரமாக அதிகரிக்கும்.",
                "safe_alternatives": ["எலுமிச்சை சாறு, நெல்லிக்காய் மற்றும் பூண்டு", "இளநீர்", "உப்பில்லாத நட்ஸ்"],
                "clinical_note": "உணவில் உப்பைக் குறைத்து இரத்த அழுத்தத்தைக் கண்காணிக்கவும்."
            },
            "kn": {
                "food_name": "ಉಪ್ಪಿನಕಾಯಿ, ಹಪ್ಪಳ ಮತ್ತು ಅತಿಯಾದ ಉಪ್ಪಿರುವ ಕುರುಕಲು ತಿಂಡಿಗಳು",
                "reason": "ಅಧಿಕ ಸೋಡಿಯಂ ರಕ್ತದೊತ್ತಡವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.",
                "safe_alternatives": ["ನಿಂಬೆರಸ, ಬೆಟ್ಟದ ನೆಲ್ಲಿಕಾಯಿ ಮತ್ತು ಬೆಳ್ಳುಳ್ಳಿ", "ಎಳನೀರು", "ಉಪ್ಪಿಲ್ಲದ ಬೀಜಗಳು"],
                "clinical_note": "ದೈನಂದಿನ ಉಪ್ಪಿನ ಪ್ರಮಾಣವನ್ನು ಕಡಿಮೆ ಮಾಡುವುದು ರಕ್ತದೊತ್ತಡಕ್ಕೆ ಮುಖ್ಯ."
            }
        }
    },
    "condition_thyroid": {
        "id": "condition_thyroid",
        "category": "medical_condition",
        "restriction_type": "general_suggestion",
        "severity": "moderate",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Excessive Raw Cruciferous Greens (Raw Cabbage, Raw Cauliflower, Raw Broccoli)",
                "reason": "Raw glucosinolates produce goitrin metabolites that can competitively inhibit iodine uptake into thyroid follicles (thorough cooking deactivates goitrogens).",
                "safe_alternatives": ["Thoroughly cooked or steamed greens and vegetables", "Brazil nuts (selenium-dense)", "Iodized salt in moderation", "Pumpkin seeds (zinc)"],
                "clinical_note": "You do not need to eliminate vegetables completely. Boiling, steaming, or sautéing safely neutralizes goitrogenic enzymes."
            },
            "te": {
                "food_name": "పచ్చి క్యాబేజీ, పచ్చి క్యాలీఫ్లవర్ మరియు పచ్చి బ్రకోలీ",
                "reason": "పచ్చిగా తిన్నప్పుడు వీటిలోని గాయిట్రోజెన్లు థైరాయిడ్ గ్రంథి అయోడిన్ గ్రహించకుండా అడ్డుకుంటాయి (బాగా ఉడికిస్తే ఈ సమస్య ఉండదు).",
                "safe_alternatives": ["బాగా ఉడికించిన ఆకుకూరలు మరియు కూరగాయలు", "సెలీనియం ఉన్న గింజలు", "అయోడైజ్డ్ ఉప్పు", "గుమ్మడి గింజలు"],
                "clinical_note": "కూరగాయలను బాగా ఉడికించి తింటే థైరాయిడ్‌కు ఎటువంటి ఇబ్బంది ఉండదు."
            },
            "hi": {
                "food_name": "कच्चा पत्तागोभी, कच्चा फूलगोभी और कच्ची ब्रोकली",
                "reason": "कच्ची अवस्था में इनमें मौजूद तत्व थायरॉइड ग्रंथि द्वारा आयोडीन के अवशोषण में बाधा डालते हैं।",
                "safe_alternatives": ["अच्छी तरह पकाई या उबली हुई सब्जियां", "कद्दू के बीज", "आयोडीन युक्त नमक"],
                "clinical_note": "सब्जियों को अच्छी तरह पकाकर खाने से थायरॉइड पर कोई बुरा असर नहीं पड़ता।"
            },
            "ta": {
                "food_name": "பச்சை முட்டைகோஸ் மற்றும் காலிஃபிளவர்",
                "reason": "பச்சையாக சாப்பிடும்போது தைராய்டு சுரப்பியின் அயோடின் உறிஞ்சும் திறனைப் பாதிக்கலாம்.",
                "safe_alternatives": ["நன்றாக வேகவைத்த காய்கறிகள்", "பூசணி விதைகள்", "அயோடின் கலந்த உப்பு"],
                "clinical_note": "காய்கறிகளை நன்றாக சமைத்து உண்பது பாதுகாப்பானது."
            },
            "kn": {
                "food_name": "ಹಸಿ ಎಲೆಕೋಸು ಮತ್ತು ಹೂಕೋಸು",
                "reason": "ಹಸಿಯಾಗಿ ಸೇವಿಸಿದರೆ ಥೈರಾಯ್ಡ್ ಗ್ರಂಥಿಯ ಮೇಲೆ ಪರಿಣಾಮ ಬೀರಬಹುದು.",
                "safe_alternatives": ["ಚೆನ್ನಾಗಿ ಬೇಯಿಸಿದ ತರಕಾರಿಗಳು", "ಕುಂಬಳಕಾಯಿ ಬೀಜಗಳು", "ಅಯೋಡಿನ್ ಯುಕ್ತ ಉಪ್ಪು"],
                "clinical_note": "ತರಕಾರಿಗಳನ್ನು ಚೆನ್ನಾಗಿ ಬೇಯಿಸಿ ತಿನ್ನುವುದು ಸುರಕ್ಷಿತ."
            }
        }
    },
    "condition_pcos": {
        "id": "condition_pcos",
        "category": "medical_condition",
        "restriction_type": "general_suggestion",
        "severity": "moderate",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Ultra-Processed Sugary Desserts, Trans-Fat Fried Snacks & Excess Dairy Drinks",
                "reason": "Sustained insulin spikes stimulate ovarian theca cells to overproduce androgens, driving hormonal imbalance, hirsutism, and ovulatory irregularities.",
                "safe_alternatives": ["Spearmint tea (anti-androgenic properties)", "Flaxseed meal and Chia seeds", "Cinnamon water", "High-fiber whole lentils and leafy greens"],
                "clinical_note": "A low-glycemic, anti-inflammatory wholefood pattern is clinically proven to restore ovulatory regularity in PCOS."
            },
            "te": {
                "food_name": "స్వీట్లు, మైదాతో చేసిన బేకరీ పదార్థాలు మరియు వేపుళ్లు",
                "reason": "ఇవి ఇన్సులిన్ స్థాయిలను వేగంగా పెంచి అండాశయాలలో పురుష హార్మోన్ల (ఆండ్రోజెన్స్) విడుదలను పెంచుతాయి, దీనివల్ల పీరియడ్స్ క్రమం తప్పుతాయి.",
                "safe_alternatives": ["పుదీనా టీ (Spearmint tea)", "అవిసె గింజల పొడి & చియా గింజలు", "దాల్చిన చెక్క కషాయం", "పీచు పదార్థాలు పుష్కలంగా ఉన్న పప్పులు"],
                "clinical_note": "పీసీఓఎస్ ఉన్నవారు తక్కువ గ్లైసెమిక్ ఆహారాలను తీసుకుంటే హార్మోన్ల సమతుల్యత మెరుగవుతుంది."
            },
            "hi": {
                "food_name": "ज्यादा मीठा, तली-भुनी चीजें और मैदे के स्नैक्स",
                "reason": "ये इंसुलिन बढ़ाते हैं, जिससे एंड्रोजन हार्मोन का स्तर बढ़कर हार्मोनल असंतुलन और पीसीओएस की समस्या बढ़ती है।",
                "safe_alternatives": ["पुदीने की चाय", "अलसी और चिया के बीज", "दालचीनी का पानी", "फाइबर युक्त दालें"],
                "clinical_note": "कम चीनी और अधिक फाइबर वाला संतुलित आहार पीसीओएस में अत्यंत लाभकारी है।"
            },
            "ta": {
                "food_name": "அதிக சர்க்கரை உள்ள இனிப்புகள் மற்றும் பொரித்த உணவுகள்",
                "reason": "இன்சுலின் அளவை உயர்த்தி ஹார்மோன் சமநிலையின்மை மற்றும் ஒழுங்கற்ற மாதவிடாயை ஏற்படுத்தும்.",
                "safe_alternatives": ["புதினா தேநீர்", "ஆளி விதைகள்", "இலவங்கப்பட்டை நீர்", "நார்ச்சத்து உணவுகள்"],
                "clinical_note": "குறைந்த சர்க்கரை மற்றும் அதிக நார்ச்சத்து உள்ள உணவுகளை உட்கொள்ளவும்."
            },
            "kn": {
                "food_name": "ಸಿಹಿ ತಿನಿಸುಗಳು ಮತ್ತು ಎಣ್ಣೆಯಲ್ಲಿ ಕರಿದ ತಿಂಡಿಗಳು",
                "reason": "ಇನ್ಸುಲಿನ್ ಹೆಚ್ಚಿಸಿ ಹಾರ್ಮೋನ್ ಅಸಮತೋಲನ ಉಂಟುಮಾಡುತ್ತವೆ.",
                "safe_alternatives": ["ಪುದೀನಾ ಚಹಾ", "ಅಗಸೆ ಬೀಜಗಳು", "ದಾಲ್ಚಿನ್ನಿ ನೀರು", "ನಾರಿನಂಶವಿರುವ ಕಾಳುಗಳು"],
                "clinical_note": "ನಾರಿನಂಶವಿರುವ ಆಹಾರ ಪದ್ಧತಿ ಪಿಸಿಓಎಸ್ ನಿಯಂತ್ರಣಕ್ಕೆ ಸಹಕಾರಿ."
            }
        }
    },
    "condition_kidney_stones": {
        "id": "condition_kidney_stones",
        "category": "medical_condition",
        "restriction_type": "medically_necessary",
        "severity": "high",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Excessive Raw Spinach (Palak), Beetroots, Starfruit & High-Purine Organ Meats",
                "reason": "High dietary oxalates bind to urinary calcium, precipitating insoluble calcium oxalate crystals and recurrent renal lithiasis.",
                "safe_alternatives": ["Bottle gourd (Sorakaya / Lauki)", "Cucumber, Zucchini, and Pumpkin", "Adequate water with lemon juice (citrate inhibits stone nucleation)"],
                "clinical_note": "Ensure 3+ liters of fluid intake daily. Boiling spinach and discarding the cooking water removes up to 60% of soluble oxalates."
            },
            "te": {
                "food_name": "పచ్చి పాలకూర (అధికంగా), బీట్‌రూట్ మరియు అధిక ప్యూరిన్లు ఉండే ఆహారాలు",
                "reason": "వీటిలోని అధిక ఆక్సలేట్లు మూత్రంలోని క్యాల్షియంతో కలిసి మూత్రపిండాలలో రాళ్లు (కిడ్నీ స్టోన్స్) ఏర్పడేలా చేస్తాయి.",
                "safe_alternatives": ["సొరకాయ", "దోసకాయ మరియు గుమ్మడికాయ", "నిమ్మరసం కలిపిన తగినంత మంచినీరు"],
                "clinical_note": "రోజూ కనీసం 3 లీటర్ల నీరు తాగాలి. పాలకూరను ఉడికించి ఆ నీటిని ఒంపేసి వాడటం మంచిది."
            },
            "hi": {
                "food_name": "कच्चा पालक (अधिक मात्रा में), चुकंदर और अत्यधिक मांसाहार",
                "reason": "इनमें मौजूद ऑक्सालेट मूत्र में कैल्शियम के साथ मिलकर पथरी (किडनी स्टोन) बनाते हैं।",
                "safe_alternatives": ["लौकी", "खीरा और कद्दू", "नींबू पानी और भरपूर मात्रा में सादा पानी"],
                "clinical_note": "प्रतिदिन 3 लीटर से अधिक पानी पिएं। पालक को उबालकर पानी फेंकने से ऑक्सालेट कम हो जाते हैं।"
            },
            "ta": {
                "food_name": "அதிக பசலைக்கீரை, பீட்ரூட் மற்றும் அதிக புரத அசைவம்",
                "reason": "இதில் உள்ள ஆக்சலேட்டுகள் சிறுநீரகத்தில் கற்கள் உருவாகக் காரணமாகின்றன.",
                "safe_alternatives": ["சுரைக்காய்", "வெள்ளரிக்காய் மற்றும் பூசணிக்காய்", "எலுமிச்சை கலந்த தண்ணீர்"],
                "clinical_note": "தினமும் 3 லிட்டருக்கும் அதிகமாக தண்ணீர் அருந்தவும்."
            },
            "kn": {
                "food_name": "ಹಸಿ ಪಾಲಕ್ ಸೊಪ್ಪು ಮತ್ತು ಬೀಟ್ರೂಟ್",
                "reason": "ಆಕ್ಸಲೇಟ್ ಅಂಶಗಳು ಮೂತ್ರಪಿಂಡದಲ್ಲಿ ಕಲ್ಲುಗಳು ಉಂಟಾಗಲು ಕಾರಣವಾಗುತ್ತವೆ.",
                "safe_alternatives": ["ಸೋರೆಕಾಯಿ", "ಸೌತೆಕಾಯಿ ಮತ್ತು ಕುಂಬಳಕಾಯಿ", "ಸಾಕಷ್ಟು ನೀರು ಮತ್ತು ನಿಂಬೆರಸ"],
                "clinical_note": "ದಿನಕ್ಕೆ ಕನಿಷ್ಠ 3 ಲೀಟರ್ ನೀರು ಕುಡಿಯುವುದು ಕಿಡ್ನಿ ಕಲ್ಲುಗಳನ್ನು ತಡೆಯುತ್ತದೆ."
            }
        }
    },
    "condition_gerd": {
        "id": "condition_gerd",
        "category": "medical_condition",
        "restriction_type": "general_suggestion",
        "severity": "moderate",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Deep-Fried Heavy Foods, Raw Onions, Fiery Red Chilies & Late-Night Carbonated Drinks",
                "reason": "Excess fats delay gastric emptying and trigger cholecystokinin release, reducing lower esophageal sphincter (LES) tone and permitting acid backflow.",
                "safe_alternatives": ["Oatmeal porridge", "Tender coconut water", "Ripe bananas", "Fennel seed (Saunf) infusion", "Steamed gourd vegetables"],
                "clinical_note": "Avoid lying down for 2-3 hours following dinner. Elevate the head of your bed if nocturnal reflux disturbs sleep."
            },
            "te": {
                "food_name": "ఎక్కువ నూనెలో వేయించిన ఆహారాలు, ఘాటైన పచ్చిమిర్చి, నిద్రపోయే ముందు కూల్ డ్రింక్స్",
                "reason": "ఇవి కడుపులో ఆమ్లాల ఉత్పత్తిని పెంచి, అన్నవాహిక కవాటాన్ని సడలించి గుండెల్లో మంట (ఎసిడిటీ) కలిగిస్తాయి.",
                "safe_alternatives": ["ఓట్స్ గంజి", "కొబ్బరి నీళ్లు", "బాగా పండిన అరటిపండ్లు", "సోంపు నీళ్లు (సౌంఫ్)", "ఉడికించిన కూరగాయలు"],
                "clinical_note": "రాత్రి భోజనం చేసిన వెంటనే పడుకోకుండా కనీసం 2 గంటల సమయం ఇవ్వండి."
            },
            "hi": {
                "food_name": "तली-भुनी भारी चीजें, अत्यधिक तीखी लाल मिर्च और कोल्ड ड्रिंक्स",
                "reason": "ये पेट में एसिड को बढ़ाकर सीने में जलन और खट्टी डकारें पैदा करते हैं।",
                "safe_alternatives": ["ओट्स दलिया", "नारियल पानी", "पका हुआ केला", "सौंफ का पानी", "उबली सब्जियां"],
                "clinical_note": "रात के खाने के तुरंत बाद न सोएं, कम से कम 2 घंटे का अंतर रखें।"
            },
            "ta": {
                "food_name": "அதிக எண்ணெய் பலகாரங்கள், காரமான மிளகாய் மற்றும் குளிர் பானங்கள்",
                "reason": "வயிற்றில் அமிலத்தன்மையை அதிகரித்து நெஞ்செரிச்சலை உண்டாக்கும்.",
                "safe_alternatives": ["ஓட்ஸ் கஞ்சி", "இளநீர்", "வாழைப்பழம்", "சோம்பு தண்ணீர்"],
                "clinical_note": "இரவு உணவிற்குப் பின் உடனே படுக்கைக்குச் செல்வதைத் தவிர்க்கவும்."
            },
            "kn": {
                "food_name": "ಕರಿದ ತಿಂಡಿಗಳು, ಅತಿಯಾದ ಖಾರ ಮತ್ತು ತಂಪು ಪಾನೀಯಗಳು",
                "reason": "ಹೊಟ್ಟೆಯಲ್ಲಿ ಆಮ್ಲೀಯತೆ ಹೆಚ್ಚಿಸಿ ಎದೆಯುರಿಗೆ ಕಾರಣವಾಗುತ್ತವೆ.",
                "safe_alternatives": ["ಓಟ್ಸ್ ಗಂಜಿ", "ಎಳನೀರು", "ಬಾಳೆಹಣ್ಣು", "ಸೋಂಪು ಕಾಳಿನ ನೀರು"],
                "clinical_note": "ಊಟದ ನಂತರ ತಕ್ಷಣ ಮಲಗದೆ 2 ಗಂಟೆಗಳ ಕಾಲಾವಕಾಶ ಕೊಡಿ."
            }
        }
    },
    "condition_anemia": {
        "id": "condition_anemia",
        "category": "medical_condition",
        "restriction_type": "general_suggestion",
        "severity": "moderate",
        "action_type": "time_separate",
        "translations": {
            "en": {
                "food_name": "Strong Black Tea, Coffee & Calcium Supplements With Main Meals",
                "reason": "Tannins, polyphenols, and divalent calcium ions chelate non-heme plant iron in the gut lumen, reducing intestinal iron uptake by up to 60%.",
                "safe_alternatives": ["Enjoy tea or coffee 1.5 to 2 hours away from meals", "Pair iron sources with Vitamin C (Lemon juice, Amla) to triple absorption"],
                "clinical_note": "Confirm the etiology of anemia with a complete blood count and serum ferritin under your physician's supervision."
            },
            "te": {
                "food_name": "భోజనం చేసే సమయంలో టీ, కాఫీ మరియు క్యాల్షియం మాత్రలు",
                "reason": "టీ మరియు కాఫీలోని టానిన్లు ఆహారంలోని ఐరన్ శరీరానికి అందకుండా అడ్డుకుంటాయి (ఐరన్ శోషణను 60% తగ్గిస్తాయి).",
                "safe_alternatives": ["భోజనానికి 2 గంటల ముందు లేదా తర్వాత మాత్రమే టీ/కాఫీ తాగండి", "ఐరన్ ఉన్న ఆహారంతో పాటు నిమ్మరసం లేదా ఉసిరి తీసుకోండి"],
                "clinical_note": "రక్తహీనత ఉన్నవారు ఐరన్ ఆహారంతో పాటు విటమిన్ సి కలిపి తీసుకుంటే వేగంగా హిమోగ్లోబిన్ పెరుగుతుంది."
            },
            "hi": {
                "food_name": "भोजन के तुरंत साथ चाय, कॉफी या कैल्शियम की गोलियां",
                "reason": "चाय-कॉफी में मौजूद टैनिन भोजन के आयरन को शरीर में अवशोषित होने से रोकते हैं।",
                "safe_alternatives": ["भोजन के 2 घंटे पहले या बाद में चाय/कॉफी पिएं", "आयरन युक्त भोजन के साथ नींबू या आंवला लें"],
                "clinical_note": "विटामिन सी युक्त नींबू के साथ आयरन लेने से उसका अवशोषण कई गुना बढ़ जाता है।"
            },
            "ta": {
                "food_name": "உணவுடன் உடனே தேநீர் மற்றும் காபி குடிப்பது",
                "reason": "தேநீரில் உள்ள டானின் சத்து உணவில் உள்ள இரும்புச்சத்தை உடல் உறிஞ்சுவதைத் தடுக்கிறது.",
                "safe_alternatives": ["உணவுக்கு 2 மணி நேர இடைவெளியில் தேநீர் குடிக்கவும்", "எலுமிச்சை சாற்றுடன் இரும்புச்சத்து உணவை உட்கொள்ளவும்"],
                "clinical_note": "வைட்டமின் சி சத்துடன் இரும்புச்சத்தை எடுக்கும்போது சிறந்த பலன் கிடைக்கும்."
            },
            "kn": {
                "food_name": "ಊಟದ ತಕ್ಷಣ ಟೀ ಅಥವಾ ಕಾಫಿ ಸೇವಿಸುವುದು",
                "reason": "ಟೀಯಲ್ಲಿರುವ ಟ್ಯಾನಿನ್ ಅಂಶವು ಕಬ್ಬಿಣಾಂಶ ದೇಹಕ್ಕೆ ಸೇರದಂತೆ ತಡೆಯುತ್ತದೆ.",
                "safe_alternatives": ["ಊಟವಾದ 2 ಗಂಟೆಗಳ ನಂತರ ಟೀ/ಕಾಫಿ ಕುಡಿಯಿರಿ", "ಕಬ್ಬಿಣಾಂಶದ ಜೊತೆಗೆ ನಿಂಬೆರಸ ಬಳಸಿ"],
                "clinical_note": "ವಿಟಮಿನ್ ಸಿ ಜೊತೆ ಕಬ್ಬಿಣಾಂಶ ಸೇವಿಸುವುದು ರಕ್ತಹೀನತೆಗೆ ಅತ್ಯುತ್ತಮ."
            }
        }
    },

    # ------------------ MEDICATION-FOOD INTERACTIONS ------------------
    "med_warfarin": {
        "id": "med_warfarin",
        "category": "medication_interaction",
        "restriction_type": "medically_necessary",
        "severity": "critical",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Erratic or Abrupt Surges in Vitamin K Greens (Sudden large intake of Kale, Spinach)",
                "reason": "Vitamin K is an essential cofactor for clotting factors II, VII, IX, and X, directly neutralizing the anticoagulant efficacy of Warfarin and disrupting INR.",
                "safe_alternatives": ["Maintain steady, consistent week-to-week green intake rather than erratic bingeing", "Lower-K vegetables: Cucumber, Bottle gourd, Carrots, Tomatoes"],
                "clinical_note": "Clinically critical interaction. Never make drastic shifts in leafy green consumption without consulting your prescribing physician and checking PT/INR."
            },
            "te": {
                "food_name": "అకస్మాత్తుగా అధిక పరిమాణంలో విటమిన్ కె ఉన్న ఆకుకూరలు (పాలకూర, కాలే) తినడం",
                "reason": "విటమిన్ కె రక్తాన్ని గడ్డకట్టేలా చేస్తుంది, ఇది వార్ఫరిన్ వంటి రక్తాన్ని పలుచబరిచే మందుల ప్రభావాన్ని దెబ్బతీసి ప్రాణాంతకమవుతుంది.",
                "safe_alternatives": ["ఆకుకూరలను రోజూ ఒకే నిర్ణీత పరిమాణంలో క్రమబద్ధంగా తీసుకోవాలి", "దోసకాయ, సొరకాయ, టమాటాలు"],
                "clinical_note": "రక్తం పలుచబడే మందులు వాడేవారు ఆకుకూరల విషయంలో వైద్యుల సలహాను మరియు INR పరీక్షలను తప్పక అనుసరించాలి."
            },
            "hi": {
                "food_name": "अचानक बहुत अधिक मात्रा में पालक और हरी पत्तेदार सब्जियां खाना",
                "reason": "विटामिन के खून को थक्का बनाता है, जिससे वारफारिन जैसी रक्त पतला करने वाली दवाइयों का असर खत्म हो जाता है।",
                "safe_alternatives": ["हरी सब्जियों की मात्रा रोज एक समान रखें", "खीरा, लौकी, गाजर और टमाटर"],
                "clinical_note": "वारफारिन लेते समय अपने डॉक्टर की सलाह के बिना खानपान में बड़ा बदलाव न करें।"
            },
            "ta": {
                "food_name": "திடீரென அதிக அளவில் கீரைகள் மற்றும் வைட்டமின் கே உணவுகள் உண்பது",
                "reason": "வார்ஃபரின் போன்ற இரத்தத்தை நீர்க்கச் செய்யும் மருந்துகளின் செயல்திறனை வைட்டமின் கே முடக்கும்.",
                "safe_alternatives": ["கீரைகளை திடீரென கூட்டவோ குறைக்கவோ செய்யாமல் சீராக எடுக்கவும்", "வெள்ளரிக்காய், சுரைக்காய்"],
                "clinical_note": "மருத்துவரின் ஆலோசனை மற்றும் INR பரிசோதனையின்றி கீரைகளின் அளவை மாற்றாதீர்கள்."
            },
            "kn": {
                "food_name": "ಏಕಾಏಕಿ ಅಧಿಕ ಪ್ರಮಾಣದಲ್ಲಿ ಪಾಲಕ್ ಮತ್ತು ಹಸಿರು ಸೊಪ್ಪುಗಳನ್ನು ತಿನ್ನುವುದು",
                "reason": "ರಕ್ತ ತೆಳುವಾಗಿಸುವ ವಾರ್ಫರಿನ್ ಮಾತ್ರೆಗಳ ಪ್ರಭಾವವನ್ನು ವಿಟಮಿನ್ ಕೆ ಕಡಿಮೆ ಮಾಡುತ್ತದೆ.",
                "safe_alternatives": ["ಸೊಪ್ಪಿನ ಸೇವನೆಯನ್ನು ನಿಗದಿತ ಪ್ರಮಾಣದಲ್ಲಿ ಸಮತೋಲನವಾಗಿಡಿ", "ಸೌತೆಕಾಯಿ, ಸೋರೆಕಾಯಿ"],
                "clinical_note": "ವೈದ್ಯರ ಸಲಹೆಯಿಲ್ಲದೆ ಆಹಾರದಲ್ಲಿ ದಿಢೀರ್ ಬದಲಾವಣೆ ಮಾಡಬೇಡಿ."
            }
        }
    },
    "med_statins": {
        "id": "med_statins",
        "category": "medication_interaction",
        "restriction_type": "medically_necessary",
        "severity": "critical",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Grapefruit, Fresh Grapefruit Juice & Seville Oranges",
                "reason": "Furanocoumarins irreversibly inhibit intestinal CYP3A4 enzymes, skyrocketing statin blood levels and significantly elevating the risk of severe muscle breakdown (rhabdomyolysis).",
                "safe_alternatives": ["Sweet Oranges (Santra)", "Mosambi (Sweet Lime)", "Indian Gooseberry (Amla)", "Apples, Guava & Papaya"],
                "clinical_note": "Clinically mandatory restriction when taking Atorvastatin, Simvastatin, or Lovastatin. If grapefruit is desired, consult your physician for non-CYP3A4 statins."
            },
            "te": {
                "food_name": "గ్రేప్‌ఫ్రూట్ (పంపరపనస) మరియు గ్రేప్‌ఫ్రూట్ జ్యూస్",
                "reason": "గ్రేప్‌ఫ్రూట్‌లోని రసాయనాలు కొలెస్ట్రాల్ మందులైన స్టాటిన్స్ శోషణను ప్రమాదకరంగా పెంచి కండరాల క్షీణతకు (రాబ్డోమయోలిసిస్) కారణమవుతాయి.",
                "safe_alternatives": ["కమలాపండ్లు", "బత్తాయి (మోసంబి)", "ఉసిరికాయ", "యాపిల్ మరియు జామకాయ"],
                "clinical_note": "స్టాటిన్ మందులు వాడేవారు గ్రేప్‌ఫ్రూట్‌ను ఎట్టి పరిస్థితుల్లోనూ తీసుకోకూడదు."
            },
            "hi": {
                "food_name": "ग्रेपफ्रूट (चकोतरा) और उसका ताजा रस",
                "reason": "यह कोलेस्ट्रॉल की स्टेटिन दवाओं के स्तर को खून में खतरनाक रूप से बढ़ा देता है, जिससे मांसपेशियों को गंभीर नुकसान पहुंच सकता है।",
                "safe_alternatives": ["संतरा", "मौसमी", "आंवला", "सेब और अमरूद"],
                "clinical_note": "स्टेटिन दवा लेने वालों के लिए चकोतरे से पूर्ण परहेज अनिवार्य है।"
            },
            "ta": {
                "food_name": "கிரேப்ஃப்ரூட் (பப்ளிமாஸ்) மற்றும் அதன் சாறு",
                "reason": "கொலஸ்ட்ரால் ஸ்டேடின் மருந்துகளின் நச்சுத்தன்மையை அதிகரித்து தசைச் சிதைவை உண்டாக்கும்.",
                "safe_alternatives": ["ஆரஞ்சு", "சாத்துக்குடி", "நெல்லிக்காய்", "ஆப்பிள்"],
                "clinical_note": "ஸ்டேடின் மருந்து உட்கொள்பவர்கள் பப்ளிமாஸ் பழத்தைத் தவிர்க்க வேண்டும்."
            },
            "kn": {
                "food_name": "ಚಕೋತ ಹಣ್ಣು ಮತ್ತು ಅದರ ರಸ",
                "reason": "ಕೊಲೆಸ್ಟ್ರಾಲ್ ಸ್ಟ್ಯಾಟಿನ್ ಔಷಧಿಗಳ ತೀವ್ರತೆಯನ್ನು ಹೆಚ್ಚಿಸಿ ಸ್ನಾಯುಗಳಿಗೆ ಹಾನಿ ಮಾಡುತ್ತದೆ.",
                "safe_alternatives": ["ಕಿತ್ತಳೆ", "ಮೋಸಂಬಿ", "ನೆಲ್ಲಿಕಾಯಿ", "ಸೇಬು"],
                "clinical_note": "ಸ್ಟ್ಯಾಟಿನ್ ಮಾತ್ರೆ ತೆಗೆದುಕೊಳ್ಳುವಾಗ ಚಕೋತ ಹಣ್ಣನ್ನು ತಿನ್ನಬಾರದು."
            }
        }
    },
    "med_levothyroxine": {
        "id": "med_levothyroxine",
        "category": "medication_interaction",
        "restriction_type": "medically_necessary",
        "severity": "high",
        "action_type": "time_separate",
        "translations": {
            "en": {
                "food_name": "High-Calcium Milk/Paneer, Soy Products & Iron Supplements Within 4 Hours of Dosing",
                "reason": "Polyvalent cations (Calcium, Iron) and soy phytoestrogens chelate levothyroxine sodium in the stomach lumen, slashing drug bioavailability by up to 50%.",
                "safe_alternatives": ["Take Levothyroxine with plain water 30-60 minutes before breakfast", "Schedule tea, milk, paneer, and calcium supplements 4 hours later in the day"],
                "clinical_note": "A 4-hour window between your thyroid hormone dose and calcium/iron/soy ensures stable systemic TSH levels."
            },
            "te": {
                "food_name": "థైరాయిడ్ మాత్ర వేసుకున్న వెంటనే పాలు, పనీర్, సోయా లేదా ఐరన్/క్యాల్షియం మాత్రలు",
                "reason": "క్యాల్షియం మరియు ఐరన్ థైరాయిడ్ మందుతో కలిసిపోయి అది శరీరానికి సరిగ్గా అందకుండా చేస్తాయి (50% శోషణ తగ్గిపోతుంది).",
                "safe_alternatives": ["ఉదయం ఖాళీ కడుపుతో మంచినీటితో మాత్రమే థైరాయిడ్ మాత్ర వేసుకోండి", "పాలు, కాఫీ లేదా ఇతర మాత్రలను 4 గంటల తర్వాత మాత్రమే తీసుకోండి"],
                "clinical_note": "మందు వేసుకున్న 4 గంటల తర్వాతే పాల ఉత్పత్తులు తీసుకోవడం వల్ల థైరాయిడ్ హార్మోన్ స్థిరంగా పనిచేస్తుంది."
            },
            "hi": {
                "food_name": "थायरॉइड की दवा के साथ या तुरंत बाद दूध, पनीर, सोयाबीन या कैल्शियम की गोलियां",
                "reason": "कैल्शियम और सोया थायरॉइड दवा के अवशोषण को 50% तक कम कर देते हैं, जिससे दवा बेअसर हो जाती है।",
                "safe_alternatives": ["सुबह खाली पेट केवल सादे पानी से थायरॉइड की गोली लें", "दूध, चाय या कैल्शियम की चीजें 4 घंटे बाद लें"],
                "clinical_note": "दवा और डेयरी उत्पादों के बीच 4 घंटे का अंतर रखना बहुत जरूरी है।"
            },
            "ta": {
                "food_name": "தைராய்டு மருந்துடன் பால், பன்னீர், சோயா அல்லது கால்சியம் மாத்திரைகள்",
                "reason": "கால்சியம் தைராய்டு மருந்தை உடல் உறிஞ்சுவதை பாதியாகக் குறைத்துவிடும்.",
                "safe_alternatives": ["வெறும் வயிற்றில் தண்ணீருடன் தைராய்டு மாத்திரை எடுக்கவும்", "பால் மற்றும் கால்சியம் உணவுகளை 4 மணி நேரம் கழித்து எடுக்கவும்"],
                "clinical_note": "தைராய்டு மாத்திரைக்கும் பாலுக்கும் 4 மணி நேர இடைவெளி அவசியம்."
            },
            "kn": {
                "food_name": "ಥೈರಾಯ್ಡ್ ಮಾತ್ರೆ ಜೊತೆಗೆ ಹಾಲು, ಪನೀರ್, ಸೋಯಾ ಅಥವಾ ಕ್ಯಾಲ್ಸಿಯಂ ಮಾತ್ರೆಗಳು",
                "reason": "ಕ್ಯಾಲ್ಸಿಯಂ ಥೈರಾಯ್ಡ್ ಔಷಧಿಯ ಪರಿಣಾಮವನ್ನು ಅರ್ಧದಷ್ಟು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ.",
                "safe_alternatives": ["ಬೆಳಿಗ್ಗೆ ಬರೀ ನೀರಿನ ಜೊತೆ ಖಾಲಿ ಹೊಟ್ಟೆಯಲ್ಲಿ ಮಾತ್ರೆ ಸೇವಿಸಿ", "ಹಾಲು ಮತ್ತು ಕಾಫಿಯನ್ನು 4 ಗಂಟೆಗಳ ನಂತರ ಸೇವಿಸಿ"],
                "clinical_note": "ಔಷಧಿ ಮತ್ತು ಹಾಲಿನ ನಡುವೆ 4 ಗಂಟೆಗಳ ಅಂತರ ಕಾಪಾಡಿಕೊಳ್ಳಿ."
            }
        }
    },
    "med_metformin": {
        "id": "med_metformin",
        "category": "medication_interaction",
        "restriction_type": "medically_necessary",
        "severity": "high",
        "action_type": "limit",
        "translations": {
            "en": {
                "food_name": "Excessive Alcohol Consumption & Chronic Low Vitamin B12 Intake",
                "reason": "Alcohol combined with Metformin increases the risk of dangerous lactic acidosis. Long-term Metformin also impairs ileal absorption of Vitamin B12.",
                "safe_alternatives": ["Tender coconut water, buttermilk, herbal infusions", "Vitamin B12-rich foods or supplements under physician oversight"],
                "clinical_note": "Have your physician test serum Vitamin B12 levels annually if on long-term Metformin therapy."
            },
            "te": {
                "food_name": "మెట్‌ఫార్మిన్ మందు వాడుతున్నప్పుడు ఆల్కహాల్ తీసుకోవడం",
                "reason": "ఆల్కహాల్ మరియు మెట్‌ఫార్మిన్ కలయిక వల్ల లాక్టిక్ అసిడోసిస్ అనే ప్రమాదకరమైన పరిస్థితి వచ్చే అవకాశం ఉంది. అలాగే విటమిన్ B12 తగ్గుతుంది.",
                "safe_alternatives": ["మజ్జిగ, కొబ్బరి నీళ్లు, మూలికా కషాయాలు", "విటమిన్ B12 ఉన్న ఆహారాలు"],
                "clinical_note": "మెట్‌ఫార్మిన్ దీర్ఘకాలంగా వాడేవారు ఏటా విటమిన్ B12 పరీక్ష చేయించుకోవాలి."
            },
            "hi": {
                "food_name": "मेटफॉर्मिन के साथ शराब का अत्यधिक सेवन",
                "reason": "शराब से लैक्टिक एसिडोसिस का गंभीर खतरा बढ़ जाता है और शरीर में विटामिन बी12 की कमी हो सकती है।",
                "safe_alternatives": ["छाछ, नारियल पानी और ताजा नींबू पानी", "विटामिन बी12 युक्त पौष्टिक आहार"],
                "clinical_note": "मेटफॉर्मिन लेने वाले हर साल विटामिन बी12 की जांच अवश्य कराएं।"
            },
            "ta": {
                "food_name": "மெட்ஃபோர்மின் மருந்துடன் மது அருந்துதல்",
                "reason": "லாக்டிக் அமிலத்தன்மை அபாயத்தை அதிகரித்து வைட்டமின் பி12 குறைபாட்டை உண்டாக்கும்.",
                "safe_alternatives": ["மோர், இளநீர் மற்றும் பழச்சாறுகள்", "வைட்டமின் பி12 உணவுகள்"],
                "clinical_note": "ஆண்டுதோறும் வைட்டமின் பி12 அளவை மருத்துவரிடம் பரிசோதிக்கவும்."
            },
            "kn": {
                "food_name": "ಮೆಟ್ಫಾರ್ಮಿನ್ ಜೊತೆ ಮದ್ಯಪಾನ",
                "reason": "ಲ್ಯಾಕ್ಟಿಕ್ ಆಸಿಡೋಸಿಸ್ ಅಪಾಯವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ ಮತ್ತು ವಿಟಮಿನ್ ಬಿ12 ಕೊರತೆ ತರುತ್ತದೆ.",
                "safe_alternatives": ["ಮಜ್ಜಿಗೆ, ಎಳನೀರು", "ವಿಟಮಿನ್ ಬಿ12 ಸಮೃದ್ಧ ಆಹಾರ"],
                "clinical_note": "ಪ್ರತಿ ವರ್ಷ ವಿಟಮಿನ್ ಬಿ12 ಮಟ್ಟವನ್ನು ಪರೀಕ್ಷಿಸಿಕೊಳ್ಳಿ."
            }
        }
    },
    "med_maois": {
        "id": "med_maois",
        "category": "medication_interaction",
        "restriction_type": "medically_necessary",
        "severity": "critical",
        "action_type": "avoid",
        "translations": {
            "en": {
                "food_name": "Aged Cheeses (Parmesan, Cheddar), Cured/Fermented Meats, Draft Beers & Yeast Extracts",
                "reason": "MAO inhibitors prevent tyramine enzymatic breakdown. Accumulated tyramine displaces norepinephrine, triggering severe, potentially fatal hypertensive crises.",
                "safe_alternatives": ["Fresh unaged paneer", "Freshly pasteurized milk", "Freshly cooked whole legumes and vegetables"],
                "clinical_note": "Medically critical restriction. Carry a medication alert card and consult your prescribing psychiatrist before consuming any aged foods."
            },
            "te": {
                "food_name": "నిల్వ ఉంచిన చీజ్, నిల్వ చేసిన మాంసం, ఈస్ట్ ఉత్పత్తులు మరియు బీర్",
                "reason": "MAO ఇన్హిబిటర్లు టైరమైన్ ను జీర్ణం చేయలేవు, దీనివల్ల రక్తపోటు ప్రాణాంతకమైన రీతిలో అకస్మాత్తుగా పెరిగిపోతుంది.",
                "safe_alternatives": ["తాజా పనీర్", "తాజా పాలు", "తాజాగా వండిన పప్పుధాన్యాలు"],
                "clinical_note": "MAOI మందులు వాడేవారు నిల్వ చేసిన ఆహారాలను కచ్చితంగా నివారించాలి."
            },
            "hi": {
                "food_name": "पुराना चीज (पनीर), प्रसंस्कृत मांस और बीयर",
                "reason": "टायरामाइन न पचने के कारण अचानक जानलेवा उच्च रक्तचाप (हाइपरटेंसिव क्राइसिस) हो सकता है।",
                "safe_alternatives": ["ताजा पनीर", "ताजा दूध", "ताजी बनी दालें"],
                "clinical_note": "इस दवा के दौरान पुराने और किण्वित खाद्य पदार्थों से पूरी तरह बचें।"
            },
            "ta": {
                "food_name": "பழைய பாலாடைக்கட்டி (Cheese) மற்றும் பதப்படுத்தப்பட்ட இறைச்சி",
                "reason": "இரத்த அழுத்தத்தை அபாயகரமான அளவிற்கு உயர்த்தி பக்கவாத அபாயத்தை உண்டாக்கும்.",
                "safe_alternatives": ["புதிய பன்னீர்", "புதிய காய்கறிகள்"],
                "clinical_note": "பழைய மற்றும் நொதித்த உணவுகளை முழுமையாகத் தவிர்க்கவும்."
            },
            "kn": {
                "food_name": "ಹಳೆಯ ಚೀಸ್ ಮತ್ತು ಸಂಸ್ಕರಿಸಿದ ಮಾಂಸ",
                "reason": "ರಕ್ತದೊತ್ತಡವನ್ನು ಅಪಾಯಕಾರಿ ಮಟ್ಟಕ್ಕೆ ಹೆಚ್ಚಿಸಬಹುದು.",
                "safe_alternatives": ["ತಾಜಾ ಪನೀರ್", "ತಾಜಾ ಬೇಳೆಕಾಳುಗಳು"],
                "clinical_note": "ಹಳೆಯ ಮತ್ತು ಸಂಸ್ಕರಿಸಿದ ಆಹಾರಗಳಿಂದ ದೂರವಿರಿ."
            }
        }
    }
}

class FoodRestrictionService:
    """
    Evaluates evidence-based personalized food restrictions across:
    - Food allergies
    - Food intolerances
    - Dietary preferences
    - Clinical medical conditions
    - Known medication-food interactions
    """

    @classmethod
    def get_restriction_item(cls, item_key: str, lang: str = "en") -> Optional[FoodRestrictionItem]:
        rule = RESTRICTION_DATABASE.get(item_key)
        if not rule:
            return None
        
        translations = rule.get("translations", {})
        item_trans = translations.get(lang) or translations.get("en")
        if not item_trans:
            return None

        return FoodRestrictionItem(
            id=rule["id"],
            food_name=item_trans["food_name"],
            reason=item_trans["reason"],
            restriction_type=rule["restriction_type"],
            category=rule["category"],
            severity=rule.get("severity", "moderate"),
            action_type=rule.get("action_type", "avoid"),
            safe_alternatives=item_trans.get("safe_alternatives", []),
            clinical_note=item_trans.get("clinical_note")
        )

    @classmethod
    def analyze_restrictions(
        cls,
        query: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        intolerances: Optional[List[str]] = None,
        medical_conditions: Optional[List[str]] = None,
        medications: Optional[List[str]] = None,
        dietary_preference: Optional[str] = None,
        language: str = "en"
    ) -> RestrictionAnalysisResponse:
        matched_keys = set()
        lang = language if language in ["en", "te", "hi", "ta", "kn"] else "en"

        # 1. Match from explicit user profile inputs
        # Allergies
        if allergies:
            for a in allergies:
                al_lower = a.lower()
                if "peanut" in al_lower or "groundnut" in al_lower or "వేరుశనగ" in al_lower or "मूंगफली" in al_lower:
                    matched_keys.add("allergy_peanuts")
                if "gluten" in al_lower or "celiac" in al_lower or "wheat" in al_lower or "గోధుమ" in al_lower or "गेहूं" in al_lower:
                    matched_keys.add("allergy_gluten")
                if "dairy" in al_lower or "milk" in al_lower or "పాలు" in al_lower or "दूध" in al_lower:
                    matched_keys.add("allergy_dairy")
                if "shellfish" in al_lower or "shrimp" in al_lower or "prawn" in al_lower or "రొయ్య" in al_lower or "झींगा" in al_lower:
                    matched_keys.add("allergy_shellfish")
                if "soy" in al_lower or "సోయా" in al_lower or "सोया" in al_lower:
                    matched_keys.add("allergy_soy")
                if "egg" in al_lower or "గుడ్డు" in al_lower or "अंडा" in al_lower:
                    matched_keys.add("allergy_eggs")

        # Intolerances
        if intolerances:
            for it in intolerances:
                it_lower = it.lower()
                if "lactose" in it_lower or "లాక్టోస్" in it_lower or "लैक्टोज" in it_lower:
                    matched_keys.add("intolerance_lactose")
                if "histamine" in it_lower or "హిస్టామైన్" in it_lower:
                    matched_keys.add("intolerance_histamine")

        # Dietary preference
        if dietary_preference:
            dp_lower = dietary_preference.lower()
            if "vegan" in dp_lower:
                matched_keys.add("preference_vegan")
            elif "veg" in dp_lower and "non" not in dp_lower:
                matched_keys.add("preference_vegetarian")

        # Medical conditions
        if medical_conditions:
            for mc in medical_conditions:
                mc_lower = mc.lower()
                if "diabet" in mc_lower or "sugar" in mc_lower or "షుగర్" in mc_lower or "मधुमेह" in mc_lower:
                    matched_keys.add("condition_diabetes")
                if "hyperten" in mc_lower or "bp" in mc_lower or "blood pressure" in mc_lower or "బీపీ" in mc_lower or "रक्तचाप" in mc_lower:
                    matched_keys.add("condition_hypertension")
                if "thyroid" in mc_lower or "hypothyroid" in mc_lower or "థైరాయిడ్" in mc_lower or "थायराइड" in mc_lower:
                    matched_keys.add("condition_thyroid")
                if "pcos" in mc_lower or "pcod" in mc_lower or "పీసీఓఎస్" in mc_lower:
                    matched_keys.add("condition_pcos")
                if "stone" in mc_lower or "uric" in mc_lower or "kidney" in mc_lower or "రాయి" in mc_lower or "पथरी" in mc_lower:
                    matched_keys.add("condition_kidney_stones")
                if "gerd" in mc_lower or "acid" in mc_lower or "reflux" in mc_lower or "ఎసిడిటీ" in mc_lower or "एसिडिटी" in mc_lower:
                    matched_keys.add("condition_gerd")
                if "anemia" in mc_lower or "anaemia" in mc_lower or "iron defic" in mc_lower or "రక్తహీనత" in mc_lower or "एनीमिया" in mc_lower:
                    matched_keys.add("condition_anemia")

        # Medications
        if medications:
            for med in medications:
                m_lower = med.lower()
                if "warfarin" in m_lower or "coumadin" in m_lower or "blood thinner" in m_lower:
                    matched_keys.add("med_warfarin")
                if "statin" in m_lower or "atorvastatin" in m_lower or "simvastatin" in m_lower or "cholesterol med" in m_lower:
                    matched_keys.add("med_statins")
                if "levothyroxine" in m_lower or "thyroxine" in m_lower or "synthroid" in m_lower or "eltroxin" in m_lower:
                    matched_keys.add("med_levothyroxine")
                if "metformin" in m_lower or "glycomet" in m_lower:
                    matched_keys.add("med_metformin")
                if "maoi" in m_lower or "monoamine" in m_lower:
                    matched_keys.add("med_maois")

        # 2. Extract from Query Text if provided
        if query:
            q_lower = query.lower()
            # Allergy keywords
            if any(w in q_lower for w in ["peanut", "groundnut", "వేరుశనగ", "मूंगफली"]):
                matched_keys.add("allergy_peanuts")
            if any(w in q_lower for w in ["gluten", "celiac", "wheat allergy", "గోధుమ", "गेहूं"]):
                matched_keys.add("allergy_gluten")
            if any(w in q_lower for w in ["dairy allergy", "milk allergy", "పాల అలెర్జీ", "दूध की एलर्जी"]):
                matched_keys.add("allergy_dairy")
            if any(w in q_lower for w in ["shellfish", "prawn", "shrimp", "రొయ్య", "झींगा"]):
                matched_keys.add("allergy_shellfish")
            if any(w in q_lower for w in ["soy allergy", "సోయా", "सोया"]):
                matched_keys.add("allergy_soy")
            if any(w in q_lower for w in ["egg allergy", "గుడ్డు అలెర్జీ", "अंडे की एलर्जी"]):
                matched_keys.add("allergy_eggs")

            # Intolerance keywords
            if any(w in q_lower for w in ["lactose", "ల్యాక్టోస్", "లాక్టోస్", "लैक्टोज"]):
                matched_keys.add("intolerance_lactose")
            if any(w in q_lower for w in ["histamine", "హిస్టామైన్"]):
                matched_keys.add("intolerance_histamine")

            # Conditions
            if any(w in q_lower for w in ["diabet", "sugar", "షుగర్", "డయాబెటిస్", "मधुमेह"]):
                matched_keys.add("condition_diabetes")
            if any(w in q_lower for w in ["hyperten", "bp", "blood pressure", "రక్తపోటు", "బీపీ", "बीपी", "रक्तचाप"]):
                matched_keys.add("condition_hypertension")
            if any(w in q_lower for w in ["thyroid", "hypothyroid", "థైరాయిడ్", "थायराइड"]):
                matched_keys.add("condition_thyroid")
            if any(w in q_lower for w in ["pcos", "pcod", "పీసీఓఎస్"]):
                matched_keys.add("condition_pcos")
            if any(w in q_lower for w in ["stone", "kidney stone", "uric", "gout", "కిడ్నీ రాళ్ళు", "पथरी"]):
                matched_keys.add("condition_kidney_stones")
            if any(w in q_lower for w in ["gerd", "acid reflux", "acidity", "ఎసిడిటీ", "గుండెల్లో మంట", "एसिडिटी"]):
                matched_keys.add("condition_gerd")
            if any(w in q_lower for w in ["anemia", "iron deficiency", "రక్తహీనత", "खून की कमी", "एनीमिया"]):
                matched_keys.add("condition_anemia")

            # Medications
            if any(w in q_lower for w in ["warfarin", "blood thinner", "coumadin"]):
                matched_keys.add("med_warfarin")
            if any(w in q_lower for w in ["grapefruit", "statin", "atorvastatin", "simvastatin"]):
                matched_keys.add("med_statins")
            if any(w in q_lower for w in ["levothyroxine", "thyroxine", "synthroid", "eltroxin"]):
                matched_keys.add("med_levothyroxine")
            if any(w in q_lower for w in ["metformin", "glycomet"]):
                matched_keys.add("med_metformin")
            if any(w in q_lower for w in ["maoi", "antidepressant aged"]):
                matched_keys.add("med_maois")

        # Build list of FoodRestrictionItem objects
        restrictions: List[FoodRestrictionItem] = []
        for key in matched_keys:
            item = cls.get_restriction_item(key, lang=lang)
            if item:
                restrictions.append(item)

        # Sort: medically_necessary first, then general_suggestion
        restrictions.sort(key=lambda x: (0 if x.restriction_type == "medically_necessary" else 1, 0 if x.severity == "critical" else 1))

        med_count = sum(1 for r in restrictions if r.restriction_type == "medically_necessary")
        gen_count = sum(1 for r in restrictions if r.restriction_type == "general_suggestion")

        disclaimers = {
            "en": "FoodGenie food restriction recommendations provide evidence-based nutritional guidance. FoodGenie does not diagnose medical conditions, prescribe pharmaceuticals, or replace clinical management.",
            "te": "ఫుడ్ జీనీ ఆహార పరిమితుల సూచనలు శాస్త్రీయ పోషకాహార సమాచారాన్ని మాత్రమే అందిస్తాయి. ఇది వైద్య నిర్ధారణను లేదా డాక్టర్ చికిత్సను భర్తీ చేయదు.",
            "hi": "फूडजिनी आहार प्रतिबंध सिफारिशें साक्ष्य-आधारित पोषण संबंधी मार्गदर्शन प्रदान करती हैं। यह किसी बीमारी का निदान या डॉक्टर के इलाज का विकल्प नहीं है।",
            "ta": "உணவுக் கட்டுப்பாட்டுப் பரிந்துரைகள் வழிகாட்டுதலுக்காக மட்டுமே. மருத்துவ ஆலோசனைக்கு மருத்துவரை அணுகவும்.",
            "kn": "ಆಹಾರ ನಿರ್ಬಂಧಗಳ ಶಿಫಾರಸುಗಳು ಪೌಷ್ಟಿಕಾಂಶದ ಮಾರ್ಗದರ್ಶನಕ್ಕಾಗಿ ಮಾತ್ರ. ವೈದ್ಯರ ಸಲಹೆಯನ್ನು ಪಡೆಯಿರಿ."
        }

        doctor_referrals = {
            "en": "Always consult a registered clinical dietitian, allergist, or licensed physician before making major dietary eliminations or managing chronic prescriptions.",
            "te": "ఆహారంలో పెద్ద మార్పులు చేసేముందు లేదా మందులు వాడుతున్నప్పుడు నిపుణులైన డాక్టర్ లేదా డైటీషియన్‌ను సంప్రదించండి.",
            "hi": "खान-पान में बड़ा बदलाव करने से पहले हमेशा प्रमाणित क्लिनिकल डाइटिशियन या डॉक्टर से सलाह लें।",
            "ta": "முக்கிய உணவுக் கட்டுப்பாடுகளுக்கு முன் பதிவுபெற்ற ஊட்டச்சத்து நிபுணரை அணுகவும்.",
            "kn": "ಆಹಾರ ಪದ್ಧತಿಯಲ್ಲಿ ಮಹತ್ವದ ಬದಲಾವಣೆ ಮಾಡುವ ಮುನ್ನ ನುರಿತ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ."
        }

        return RestrictionAnalysisResponse(
            total_restrictions=len(restrictions),
            medically_necessary_count=med_count,
            general_suggestions_count=gen_count,
            restrictions=restrictions,
            clinical_disclaimer=disclaimers.get(lang, disclaimers["en"]),
            doctor_referral=doctor_referrals.get(lang, doctor_referrals["en"]),
            language=lang
        )

restriction_service = FoodRestrictionService()

