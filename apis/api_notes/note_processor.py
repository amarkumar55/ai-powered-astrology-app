# note_processor.py

import tempfile
import os
import pytesseract
from PIL import Image
from .model_loader import (
    whisper_model, bart_tokenizer, bart_model,
    translation_models, translation_tokenizers
)

# ------------------------------
# Helper: Translation
# ------------------------------
def translate_text(text, src_lang, tgt_lang):
    key = (src_lang, tgt_lang)
    if key not in translation_models:
        raise ValueError(f"Unsupported translation: {src_lang} → {tgt_lang}")

    tokenizer = translation_tokenizers[key]
    model = translation_models[key]

    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    output = model.generate(**inputs, num_beams=4, do_sample=False)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# ------------------------------
# Helper: Tag Extraction
# ------------------------------
def extract_tags(text, max_tags=5):
    """
    Very basic keyword/tag extraction.
    Could be replaced with spaCy, KeyBERT, or another NLP library later.
    """
    words = text.split()
    keywords = list({w.strip(".,!?").lower() for w in words if len(w) > 4})
    return keywords[:max_tags]

# ------------------------------
# Helper: Summarization + Title
# ------------------------------
def summarize_text(text, target_language="en", detected_lang="en"):
    # Summarize
    inputs = bart_tokenizer(text, max_length=1024, return_tensors="pt", truncation=True)
    summary_ids = bart_model.generate(
        inputs["input_ids"], num_beams=4, do_sample=False,
        max_length=150, early_stopping=True
    )
    summary_en = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # Translate if needed
    final_summary = summary_en
    if target_language and detected_lang != target_language:
        try:
            final_summary = translate_text(summary_en, src_lang="en", tgt_lang=target_language)
        except Exception as e:
            print(f"Translation failed: {e}")

    # Title generation
    title_ids = bart_model.generate(
        inputs["input_ids"], num_beams=4, max_length=15, min_length=3, early_stopping=True
    )
    title = bart_tokenizer.decode(title_ids[0], skip_special_tokens=True)

    # Tag extraction
    tags = extract_tags(final_summary)

    return {"summary": final_summary, "title": title, "tags": tags}

# ------------------------------
# Process Manual Text
# ------------------------------
def process_text_and_generate_note(text, target_language="en"):
    detected_lang = "en"  # TODO: Add language detection if needed
    return summarize_text(text, target_language, detected_lang)

# ------------------------------
# Process Audio
# ------------------------------
def process_audio_and_generate_note(audio_file, target_language="en"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        for chunk in audio_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        result = whisper_model.transcribe(tmp_path, fp16=False, temperature=0.0)
        transcript = result["text"].strip()
        detected_lang = result.get("language", "en")
        return summarize_text(transcript, target_language, detected_lang)
    finally:
        os.unlink(tmp_path)

# ------------------------------
# Process Image
# ------------------------------
def process_image_and_generate_note(image_file, target_language="en"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        for chunk in image_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        img = Image.open(tmp_path)
        extracted_text = pytesseract.image_to_string(img)
        detected_lang = "en"  # TODO: Add lang detection if OCR output is multi-lingual
        return summarize_text(extracted_text, target_language, detected_lang)
    finally:
        os.unlink(tmp_path)



def ask_ai_with_note(note_content, user_message, max_chunk_size=2000, chat_history=None):
    """
    Uses the note content as context for AI chat.
    Splits long notes into manageable chunks to avoid token overflow.
    Includes previous chat history in order.
    """
    if not note_content.strip():
        note_content = "No content available in the note."

    # Split note into chunks if it's too long
    words = note_content.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start = end

    # Concatenate chunks (could also summarize each chunk if needed)
    context = "\n\n".join(chunks)

    # Build prompt with chat history first, then user message
    prompt = f"You are an AI assistant. Use the following note as context:\n\n{context}\n\n"
    
    if chat_history:
        for chat in chat_history:
            prompt += f"User: {chat['user']}\nAI: {chat['ai']}\n"
    
    prompt += f"User: {user_message}\nAI:"

    # Call AI model
    response = ai_model.generate(prompt)
    return response


def summarize_chunks(note_content, max_chunk_size=2000):
    words = note_content.split()
    summaries = []

    start = 0
    while start < len(words):
        end = min(start + max_chunk_size, len(words))
        chunk_text = " ".join(words[start:end])
        summary = ai_model.generate(f"Summarize this note chunk:\n\n{chunk_text}")
        summaries.append(summary)
        start = end

    return " ".join(summaries)