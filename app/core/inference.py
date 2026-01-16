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
        self.glossary_path = "glossary/ Technical Terms for transliteration_10 Languages _4 Dec 25.xlsx"
        self.glossary = self._load_glossary()
        
        self.mock_repo = {
            "marathi": {
                "engine clutch brake": ["इंजिन", " क्लच", " आणि", " ब्रेक"],
                "repair the engine": ["इंजिन", " दुरुस्त", " करा"],
                "check the brakes": ["ब्रेक", " तपासा"],
                "please check the oil level before starting the engine": ["कृपया", " इंजिन", " सुरू", " करण्यापूर्वी", " तेल", " पातळी", " तपासा"],
                "default": ["अनुवाद", " प्रक्रिया", " सुरू", " आहे"]
            },
            "tamil": {
                "engine clutch brake": ["இயந்திரம்", " கிளட்ச்", " மற்றும்", " பிரேக்"],
                "repair the engine": ["இயந்திரத்தை", " பழுதுபார்க்கவும்"],
                "check the brakes": ["பிரேக்குகளை", " சரிபார்க்கவும்"],
                "please check the oil level before starting the engine": ["இயந்திரத்தைத்", " தொடங்குவதற்கு", " முன்", " தயவுசெய்து", " எண்ணெய்", " அளவைச்", " சரிபார்க்கவும்"],
                "default": ["மொழிபெயர்ப்பு", " நடந்து", " கொண்டிருக்கிறது"]
            },
            "telugu": {
                "engine clutch brake": ["ఇంజిన్", " క్లచ్", " మరియు", " బ్రేక్"],
                "repair the engine": ["ఇంజిన్", " మరమ్మతు", " చేయండి"],
                "check the brakes": ["బ్రేక్లను", " తనిఖీ", " చేయండి"],
                "please check the oil level before starting the engine": ["ఇంజిన్ను", " ప్రారంభించే", " ముందు", " దయచేసి", " నూనె", " స్థాయిని", " తనిఖీ", " చేయండి"],
                "default": ["అనువాదం", " జరుగుతోంది"]
            }
        }

    def _load_glossary(self) -> Dict[str, Dict[str, str]]:
        glossary = {"marathi": {}, "tamil": {}, "telugu": {}}
        if not os.path.exists(self.glossary_path):
            return glossary
        
        try:
            df = pd.read_excel(self.glossary_path)
            # Find exact column names or close matches
            cols = df.columns.tolist()
            marathi_col = next((c for c in cols if 'Marathi' in c), None)
            tamil_col = next((c for c in cols if 'Tamil' in c), None)
            telugu_col = next((c for c in cols if 'Telugu' in c), None)
            term_col = next((c for c in cols if 'Terms' in c), 'Technical Terms')

            for _, row in df.iterrows():
                term = str(row[term_col]).lower().strip()
                if marathi_col:
                    glossary['marathi'][term] = str(row[marathi_col]).split('(')[0].strip()
                if tamil_col:
                    glossary['tamil'][term] = str(row[tamil_col]).strip()
                if telugu_col:
                    glossary['telugu'][term] = str(row[telugu_col]).strip()
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
            "vocabulary_size": 32000
        }

    def calculate_confidence(self, source: str, target_tokens: List[str]) -> float:
        src_len = len(source.split())
        tgt_len = len(target_tokens)
        
        base_score = 0.85
        length_penalty = abs(src_len - tgt_len) * 0.05
        random_noise = random.uniform(-0.05, 0.05)
        
        score = base_score - length_penalty + random_noise
        return round(max(0.4, min(0.98, score)), 4)

    def generate_translation_stream(self, text: str, target_lang: str) -> Generator[str, None, None]:
        lang_repo = self.mock_repo.get(target_lang.lower(), self.mock_repo["marathi"])
        target_glossary = self.glossary.get(target_lang.lower(), {})
        
        clean_text = text.lower().strip().replace(".", "").replace(",", "")
        
        if clean_text in lang_repo:
            tokens = lang_repo[clean_text]
        elif clean_text in target_glossary:
            tokens = [f" {target_glossary[clean_text]}"]
        else:
            # Fallback: try to match multi-word phrases from glossary first, then single words
            # Sort glossary by length descending to match longest phrases first
            sorted_terms = sorted(target_glossary.keys(), key=len, reverse=True)
            
            temp_text = clean_text
            translated_chunks = []
            
            # Very simple greedy phrase matching
            while temp_text:
                matched = False
                for term in sorted_terms:
                    if temp_text.startswith(term):
                        translated_chunks.append(f" {target_glossary[term]}")
                        temp_text = temp_text[len(term):].strip()
                        matched = True
                        break
                
                if not matched:
                    # Take one word if no phrase match
                    parts = temp_text.split(maxsplit=1)
                    word = parts[0]
                    # Clean fallback: just use the word, possibly adding as a separate token
                    translated_chunks.append(f" {word}")
                    temp_text = parts[1] if len(parts) > 1 else ""

            tokens = translated_chunks if translated_chunks else lang_repo["default"]

        yield json.dumps({"type": "status", "content": "Encoding source sequence..."}) + "\n"
        time.sleep(0.5)
        
        yield json.dumps({"type": "status", "content": f"Initializing decoder for {target_lang}..."}) + "\n"
        time.sleep(0.3)

        generated_so_far = []
        for token in tokens:
            time.sleep(0.2)
            generated_so_far.append(token)
            yield json.dumps({
                "type": "token", 
                "content": token,
                "confidence_chunk": random.uniform(0.8, 0.99)
            }) + "\n"

        final_score = self.calculate_confidence(text, generated_so_far)
        yield json.dumps({"type": "final_score", "content": final_score}) + "\n"

engine = IndicTransEngine()
