import time
import random
import json
from typing import Generator, List, Dict

# Standard SentencePiece dummy behavior for visualization if SP is not installed or model is missing
class MockTokenizer:
    def __init__(self, target_lang: str):
        self.target_lang = target_lang
        self.vocab = [" ", "the", "engine", "clutch", "brake", "is", "working", "fine", "repair", "needed"]
    
    def tokenize(self, text: str) -> List[str]:
        # Simple split with " " prefix to simulate SentencePiece
        tokens = []
        for word in text.lower().split():
            tokens.append(f" {word}")
        return tokens

    def convert_tokens_to_ids(self, tokens: List[str]) -> List[int]:
        return [hash(t) % 1000 for t in tokens]

class IndicTransEngine:
    def __init__(self):
        # In a real scenario, we would load:
        # self.tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-en-m2m-200mb", trust_remote_code=True)
        # self.model = AutoModelForSeq2SeqLM.from_pretrained("ai4bharat/indic-en-m2m-200mb", trust_remote_code=True)
        self.is_ready = True
        
        # Mapping for mock translations (Automotive snippets)
        self.mock_repo = {
            "marathi": {
                "engine clutch brake": ["इंजिन", " क्लच", " आणि", " ब्रेक"],
                "repair the engine": ["इंजिन", " दुरुस्त", " करा"],
                "check the brakes": ["ब्रेक", " तपासा"],
                "default": ["अनुवाद", " प्रक्रिया", " सुरू", " आहे"]
            },
            "tamil": {
                "engine clutch brake": ["இயந்திரம்", " கிளட்ச்", " மற்றும்", " பிரேக்"],
                "repair the engine": ["இயந்திரத்தை", " பழுதுபார்க்கவும்"],
                "check the brakes": ["பிரேக்குகளை", " சரிபார்க்கவும்"],
                "default": ["மொழிபெயர்ப்பு", " நடந்து", " கொண்டிருக்கிறது"]
            },
            "telugu": {
                "engine clutch brake": ["ఇంజిన్", " క్లచ్", " మరియు", " బ్రేక్"],
                "repair the engine": ["ఇంజిన్", " మరమ్మతు", " చేయండి"],
                "check the brakes": ["బ్రేక్లను", " తనిఖీ", " చేయండి"],
                "default": ["అనువాదం", " జరుగుతోంది"]
            }
        }

    def get_tokenization_steps(self, text: str) -> Dict:
        """Simulates the SentencePiece tokenization flow."""
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
        """Simulated COMET-QE score."""
        # Simple heuristic: heavily penalized for very short or very long outputs relative to source
        # or if suspicious tokens are missing.
        src_len = len(source.split())
        tgt_len = len(target_tokens)
        
        base_score = 0.85
        length_penalty = abs(src_len - tgt_len) * 0.05
        random_noise = random.uniform(-0.05, 0.05)
        
        score = base_score - length_penalty + random_noise
        return round(max(0.4, min(0.98, score)), 4)

    def generate_translation_stream(self, text: str, target_lang: str) -> Generator[str, None, None]:
        """Generates tokens one-by-one to simulate NMT decoding."""
        lang_repo = self.mock_repo.get(target_lang.lower(), self.mock_repo["marathi"])
        
        # Try to find a match in mock repo or use dynamic fallback
        clean_text = text.lower().strip()
        if clean_text in lang_repo:
            tokens = lang_repo[clean_text]
        else:
            # Dynamic fallback to show it "works" with any input
            # Prefix with a generic phrase and echo a bit of the input (mocking a model's attempt)
            prefix = lang_repo["default"]
            tokens = prefix + [f" ({text[:15]}...)"]

        # Debug: Start encoding phase
        yield json.dumps({"type": "status", "content": "Encoding source sequence..."}) + "\n"
        time.sleep(0.5)
        
        yield json.dumps({"type": "status", "content": f"Initializing decoder for {target_lang}..."}) + "\n"
        time.sleep(0.3)

        generated_so_far = []
        for token in tokens:
            time.sleep(0.2) # Simulate compute time per token
            generated_so_far.append(token)
            yield json.dumps({
                "type": "token", 
                "content": token,
                "confidence_chunk": random.uniform(0.8, 0.99)
            }) + "\n"

        # Final QE Score
        final_score = self.calculate_confidence(text, generated_so_far)
        yield json.dumps({"type": "final_score", "content": final_score}) + "\n"

engine = IndicTransEngine()
