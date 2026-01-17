import time
import random
import json
import pandas as pd
import os
import re
from typing import Generator, List, Dict

class MockTokenizer:
    def __init__(self, target_lang: str):
        self.target_lang = target_lang
        self.vocab = [" ", "the", "engine", "clutch", "brake", "is", "working", "fine", "repair", "needed"]
    
    def tokenize(self, text: str) -> List[str]:
        tokens = []
        for word in text.lower().split():
            tokens.append(f" {word}")
        return tokens

    def convert_tokens_to_ids(self, tokens: List[str]) -> List[int]:
        return [hash(t) % 1000 for t in tokens]

class IndicTransEngine:
    def __init__(self):
        self.is_ready = True
        self.is_mock = True  # Simulation flag
        self.glossary_path = " Technical Terms for transliteration_10 Languages _4 Dec 25.xlsx"
        self.glossary = self._load_glossary()
        
        # Enhanced dictionary for natural sentence simulation
        self.common_vocab = {
            "marathi": {
                "before": "पूर्वी", "starting": "सुरू करण्यापूर्वी", "vehicle": "वाहन", "driver": "चालक", "must": "पाहिजे", 
                "ensure": "खात्री करणे", "all": "सर्व", "safety": "सुरक्षा", "checks": "तपासणी", "completed": "पूर्ण झाले",
                "this": "हे", "includes": "समाविष्ट आहे", "verifying": "पडताळणी", "inspecting": "तपासणी", "system": "प्रणाली",
                "confirming": "पुष्टी करणे", "that": "की", "fuel": "इंधन", "tank": "टाकी", "sufficiently": "पुरेशा प्रमाणात",
                "filled": "भरले", "if": "जर", "any": "कोणतेही", "warning": "चेतावनी", "indicators": "दर्शक", "appear": "दिसतात",
                "on": "वर", "dashboard": "डॅशबोर्ड", "they": "ते", "should": "पाहिजे", "not": "नाही", "ignored": "दुर्लक्षीत",
                "as": "कारण", "often": "नेहमी", "signal": "संकेत", "potential": "संभाव्य", "mechanical": "यांत्रिक",
                "issues": "समस्या", "once": "एकदा", "allowed": "परवानगी", "idle": "आयडल", "for": "साठी", "few": "काही",
                "minutes": "मिनिटे", "so": "जेणेकरून", "internal": "अंतर्गत", "components": "घटक", "reach": "पोहोचतात",
                "optimal": "इष्टतम", "operating": "ऑपरेटिंग", "temperature": "तापमान", "during": "दरम्यान", "time": "वेळ",
                "sudden": "अचानक", "acceleration": "वेगवर्धक", "avoided": "टाळले", "prevent": "रोखण्यासाठी", "unnecessary": "अनावश्यक",
                "strain": "ताण", "by": "द्वारे", "following": "खालील", "steps": "पायऱ्या", "consistently": "सातत्याने",
                "overall": "एकूण", "lifespan": "आयुर्मान", "extended": "वाढवले", "and": "आणि", "unexpected": "अनपेक्षित",
                "breakdowns": "बिघाड", "minimized": "कमी केले"
            },
            "tamil": {
                "before": "முன்", "starting": "தொடங்கும்", "vehicle": "வாகனம்", "driver": "ஓட்டுநர்", "must": "வேண்டும்",
                "ensure": "உறுதிப்படுத்த", "all": "அனைத்து", "safety": "பாதுகாப்பு", "checks": "சோதனைகள்", "completed": "முடிந்தன",
                "this": "இது", "includes": "உள்ளடங்கும்", "verifying": "சரிபார்ப்பது", "inspecting": "ஆய்வு செய்வது", "system": "அமைப்பு",
                "confirming": "உறுதி செய்வது", "that": "என்று", "fuel": "எரிபொருள்", "tank": "தொட்டி", "sufficiently": "போதுமான அளவு",
                "filled": "நிரப்பப்பட்டது", "if": "என்றால்", "any": "ஏதேனும்", "warning": "எச்சரிக்கை", "indicators": "காட்டிகள்", "appear": "தோன்றினால்",
                "on": "இல்", "dashboard": "டாஷ்போர்டு", "they": "அவை", "should": "வேண்டும்", "not": "கூடாது", "ignored": "புறக்கணிக்கப்பட",
                "as": "ஏனென்றால்", "often": "அடிக்கடி", "signal": "சமிக்ஞை", "potential": "சாத்தியமான", "mechanical": "இயந்திர",
                "issues": "சிக்கல்கள்", "once": "ஒருமுறை", "allowed": "அனுமதிக்கப்பட", "idle": "செயலற்ற", "for": "க்கு", "few": "சில",
                "minutes": "நிமிடங்கள்", "so": "அதனால்", "internal": "உள்", "components": "உதிரிபாகங்கள்", "reach": "அடைய",
                "optimal": "உகந்த", "operating": "இயக்க", "temperature": "வெப்பநிலை", "during": "போது", "time": "நேரம்",
                "sudden": "திடீர்", "acceleration": "முடுக்கம்", "avoided": "தவிர்க்கப்பட", "prevent": "தடுக்க", "unnecessary": "தேவையற்ற",
                "strain": "திரிபு", "by": "மூலம்", "following": "பின்வரும்", "steps": "படிகள்", "consistently": "தொடர்ந்து",
                "overall": "ஒட்டுமொத்த", "lifespan": "ஆயுட்காலம்", "extended": "நீட்டிக்கப்படும்", "and": "மற்றும்", "unexpected": "எதிர்பாராத",
                "breakdowns": "முறிவுகள்", "minimized": "குறைக்கப்படும்"
            },
            "telugu": {
                "before": "ముందు", "starting": "ప్రారంభించే", "vehicle": "వాహనం", "driver": "డ్రైవర్", "must": "తప్పనిసరిగా",
                "ensure": "నిశ్చయించుకోవాలి", "all": "అన్ని", "safety": "భద్రతా", "checks": "తనిఖీలు", "completed": "పూర్తయినట్లు",
                "this": "ఇది", "includes": "కలిగి ఉంటుంది", "verifying": "ధృవీకరించడం", "inspecting": "తనిఖీ చేయడం", "system": "వ్యవస్థ",
                "confirming": "నిర్ధారించడం", "that": "అని", "fuel": "ఇంధనం", "tank": "ట్యాంక్", "sufficiently": "తగినంతగా",
                "filled": "నిండిన", "if": "ఒకవేళ", "any": "ఏదైనా", "warning": "హెచ్చరిక", "indicators": "సూచికలు", "appear": "కనిపిస్తే",
                "on": "పై", "dashboard": "డాష్‌బోర్డ్", "they": "అవి", "should": "చేయాలి", "not": "కూడదు", "ignored": "నిర్లక్ష్యం",
                "as": "ఎందుకంటే", "often": "తరచుగా", "signal": "संकेत", "potential": "संभाव्य", "mechanical": "మెకానికల్",
                "issues": "సమస్యలు", "once": "ఒకసారి", "allowed": "అనుమతించాలి", "idle": "ఐడిల్", "for": "కోసం", "few": "కొన్ని",
                "minutes": "నిమిషాలు", "so": "తద్వారా", "internal": "అంతర్గత", "components": "భాగాలు", "reach": "చేరుకుంటాయి",
                "optimal": "సరైన", "operating": "నిర్వహణ", "temperature": "ఉష్णోగ్రత", "during": "సమయంలో", "time": "సమయం",
                "sudden": "అకస్మాత్తుగా", "acceleration": "త్వరణం", "avoided": "తప్పించాలి", "prevent": "నిరోధించడానికి", "unnecessary": "അനவసరమైన",
                "strain": "ఒత్తిడి", "by": "ద్వారా", "following": "క్రింది", "steps": "దశలు", "consistently": "నిరంతరం",
                "overall": "మొత్తం", "lifespan": "జీవితకాలం", "extended": "పొడిగించబడుతుంది", "and": "మరియు", "unexpected": "అనుకోని",
                "breakdowns": "వైఫల్యాలు", "minimized": "తగ్గించబడతాయి"
            },
            "hindi": {
                "before": "पहले", "starting": "शुरू करने से पहले", "vehicle": "वाहन", "driver": "चालक", "must": "चाहिए",
                "ensure": "सुनिश्चित", "all": "सभी", "safety": "सुरक्षा", "checks": "जांच", "completed": "पूरा",
                "this": "यह", "includes": "शामिल", "verifying": "सत्यापित", "inspecting": "निरीक्षण", "system": "प्रणाली",
                "confirming": "पुष्टि", "that": "कि", "fuel": "ईंधन", "tank": "टंकी", "sufficiently": "पर्याप्त",
                "filled": "भरा", "if": "यदि", "any": "कोई", "warning": "चेतावनी", "indicators": "संकेतक", "appear": "दिखाई",
                "on": "पर", "dashboard": "डैशबोर्ड", "they": "वे", "should": "चाहिए", "not": "नहीं", "ignored": "अनदेखा",
                "as": "क्योंकि", "often": "अक्सर", "signal": "संकेत", "potential": "संभावित", "mechanical": "यांत्रिक",
                "issues": "समस्याएं", "once": "एक बार", "allowed": "अनुमति", "idle": "आइडल", "for": "लिए", "few": "कुछ",
                "minutes": "मिनट", "so": "ताकि", "internal": "आंतरिक", "components": "घटक", "reach": "पहुंच",
                "optimal": "इष्टतम", "operating": "ऑपरेटिंग", "temperature": "तापमान", "during": "दौरान", "time": "समय",
                "sudden": "अचानक", "acceleration": "त्वरण", "avoided": "बचना", "prevent": "रोकने", "unnecessary": "अनावश्यक",
                "strain": "तनाव", "by": "द्वारा", "following": "निम्नलिखित", "steps": "कदम", "consistently": "लगातार",
                "overall": "कुल", "lifespan": "जीवनकाल", "extended": "बढ़ाया", "and": "और", "unexpected": "अप्रत्यक्ष",
                "breakdowns": "खराबी", "minimized": "कम"
            }
        }

    def _mock_transliterate(self, text: str, lang: str) -> str:
        mappings = {
            "marathi": {"a": "अ", "b": "ब", "c": "क", "d": "ड", "e": "ए", "f": "फ", "g": "ग", "h": "ह", "i": "इ", "j": "ज", "k": "क", "l": "ल", "m": "म", "n": "न", "o": "ओ", "p": "प", "q": "क", "r": "र", "s": "स", "t": "ट", "u": "उ", "v": "व", "w": "व", "x": "क्ष", "y": "य", "z": "झ"},
            "tamil": {"a": "அ", "b": "ப", "c": "க", "d": "ட", "e": "எ", "f": "ப", "g": "க", "h": "ஹ", "i": "இ", "j": "ஜ", "k": "க", "l": "ல", "m": "ம", "n": "ந", "o": "ஒ", "p": "ப", "q": "க", "r": "ர", "s": "ஸ", "t": "ட", "u": "உ", "v": "வ", "w": "வ", "x": "க", "y": "ய", "z": "ஸ"},
            "telugu": {"a": "అ", "b": "బ", "c": "క", "d": "డ", "e": "ఎ", "f": "ఫ", "g": "గ", "h": "హ", "i": "ఇ", "j": "జ", "k": "క", "l": "ల", "m": "మ", "n": "న", "o": "ఒ", "p": "ప", "q": "క", "r": "ర", "s": "स", "t": "ట", "u": "ఉ", "v": "వ", "w": "వ", "x": "క", "y": "య", "z": "స"},
            "hindi": {"a": "अ", "b": "ब", "c": "क", "d": "ड", "e": "ए", "f": "फ", "g": "ग", "h": "ह", "i": "इ", "j": "ज", "k": "क", "l": "ल", "m": "म", "n": "न", "o": "ओ", "p": "प", "q": "क", "r": "र", "s": "स", "t": "ट", "u": "उ", "v": "व", "w": "व", "x": "क्ष", "y": "य", "z": "ज़"}
        }
        target_map = mappings.get(lang.lower(), mappings["marathi"])
        return "".join([target_map.get(c, "") for c in text.lower() if c.isalpha()])

    def _load_glossary(self) -> Dict[str, Dict[str, str]]:
        glossary = {"marathi": {}, "tamil": {}, "telugu": {}, "hindi": {}}
        if not os.path.exists(self.glossary_path):
            return glossary
        
        try:
            df = pd.read_excel(self.glossary_path)
            cols = df.columns.tolist()
            marathi_col = next((c for c in cols if 'Marathi' in c), None)
            tamil_col = next((c for c in cols if 'Tamil' in c), None)
            telugu_col = next((c for c in cols if 'Telugu' in c), None)
            hindi_col = next((c for c in cols if 'Hindi' in c), None)
            term_col = next((c for c in cols if 'Terms' in c), 'Technical Terms')

            for _, row in df.iterrows():
                term = str(row[term_col]).lower().strip()
                if marathi_col:
                    glossary['marathi'][term] = str(row[marathi_col]).split('(')[0].strip()
                if tamil_col:
                    glossary['tamil'][term] = str(row[tamil_col]).split('(')[0].strip()
                if telugu_col:
                    glossary['telugu'][term] = str(row[telugu_col]).split('(')[0].strip()
                if hindi_col:
                    glossary['hindi'][term] = str(row[hindi_col]).split('(')[0].strip()
        except Exception:
            pass
        return glossary

    def get_tokenization_steps(self, text: str) -> Dict:
        raw_tokens = text.lower().split()
        sp_tokens = [f" {t}" for t in raw_tokens]
        token_ids = [hash(t) % 32000 for t in sp_tokens]
        return {
            "input_text": text,
            "pre_processing": "Normalization -> Unicode NFKC -> Lowercase",
            "tokens": sp_tokens,
            "token_ids": token_ids,
            "vocabulary_size": 32000,
            "is_mock": self.is_mock
        }

    def calculate_confidence(self, source: str, target_tokens: List[str]) -> float:
        score = 0.85 + random.uniform(-0.05, 0.05)
        return round(max(0.4, min(0.98, score)), 4)

    def generate_translation_stream(self, text: str, target_lang: str) -> Generator[str, None, None]:
        target_lang = target_lang.lower()
        target_glossary = self.glossary.get(target_lang, {})
        target_vocab = self.common_vocab.get(target_lang, self.common_vocab["marathi"])
        
        # Split text into words and punctuation
        words = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
        
        yield json.dumps({"type": "status", "content": "Analyzing paragraph structure..."}) + "\n"
        time.sleep(0.4)
        
        yield json.dumps({"type": "status", "content": f"Prioritizing technical glossary for {target_lang}..."}) + "\n"
        time.sleep(0.3)

        tokens = []
        # Greedy matching for glossary terms (max 3 words)
        i = 0
        while i < len(words):
            matched = False
            # Try 3-word, then 2-word, then 1-word phrases from glossary
            for length in [3, 2, 1]:
                if i + length <= len(words):
                    phrase = " ".join(words[i:i+length]).lower().strip()
                    if phrase in target_glossary:
                        tokens.append(f" {target_glossary[phrase]}")
                        i += length
                        matched = True
                        break
            
            if not matched:
                word = words[i]
                word_lower = word.lower()
                if word_lower in target_vocab:
                    tokens.append(f" {target_vocab[word_lower]}")
                elif not word[0].isalnum():
                    tokens.append(word)
                else:
                    # Fallback transliteration for unknown words
                    tokens.append(f" {self._mock_transliterate(word, target_lang)}")
                i += 1

        for token in tokens:
            time.sleep(0.1)  # Faster for long text
            yield json.dumps({
                "type": "token", 
                "content": token,
                "confidence_chunk": random.uniform(0.9, 0.99)
            }) + "\n"

        final_score = self.calculate_confidence(text, tokens)
        yield json.dumps({"type": "final_score", "content": final_score}) + "\n"

engine = IndicTransEngine()
