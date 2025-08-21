import whisper
from transformers import BartTokenizer, BartForConditionalGeneration
from transformers import MarianMTModel, MarianTokenizer

# -------------------------------
# Load Whisper for transcription
# -------------------------------
whisper_model = whisper.load_model("base")

# -------------------------------
# Load BART for summarization
# -------------------------------
bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

# -------------------------------
# Load MarianMT for translation
# -------------------------------
SUPPORTED_LANG_PAIRS = {
    ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    # Add more as needed
}

translation_models = {}
translation_tokenizers = {}

for (src_lang, tgt_lang), model_name in SUPPORTED_LANG_PAIRS.items():
    try:
        print(f"Loading translation model: {model_name}")
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)

        translation_tokenizers[(src_lang, tgt_lang)] = tokenizer
        translation_models[(src_lang, tgt_lang)] = model
    except Exception as e:
        print(f"[!] Failed to load model {model_name}: {e}")
