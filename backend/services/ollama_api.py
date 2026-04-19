import ollama
import json
import re
from typing import List, Dict, AsyncGenerator


# -------------------------------
# 0. Text Cleaning
# -------------------------------
def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespaces and normalizing line breaks.
    """
    if not text:
        return ""
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


# -------------------------------
# 1. Prompt Generator
# -------------------------------
def build_prompt(resume_skill_dict: dict = None, jd_skill_dict: dict = None, comparison: dict = None) -> str:
    prompt = f"""Generate ONLY valid JSON array. No explanations, markdown, or comments.

[{{"skill_in_jd": "skill", "matched_in_resume": "Yes or No", "evidence": "brief"}}]

Resume: {json.dumps(resume_skill_dict or {})}
JD: {json.dumps(jd_skill_dict or {})}
Comparison: {json.dumps(comparison or {})}

For each JD skill, check if in resume. Output Yes or No. JSON array only."""
    return prompt


# -------------------------------
# 2. Call Ollama (Blocking)
# -------------------------------
def call_ollama(prompt: str, model: str = "phi3") -> str:
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0,
                "top_p": 0.9,
                "repeat_penalty": 1.2,
                "num_predict": 500,
            }
        )
        return response["message"]["content"]
    except Exception as e:
        # If Ollama fails, return a default JSON response
        print(f"Ollama error: {e}")
        return '[{"skill_in_jd": "Error", "matched_in_resume": "No", "evidence": "Ollama service unavailable"}]'


# -------------------------------
# 3. Call Ollama (Streaming)
# -------------------------------
async def stream_ollama(prompt: str, model: str = "phi3") -> AsyncGenerator[str, None]:
    """
    Async generator that yields chunks of text from Ollama.
    """
    stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        options={
            "temperature": 0,
            "top_p": 0.9,
            "repeat_penalty": 1.2,
        }
    )
    for chunk in stream:
        if "message" in chunk and "content" in chunk["message"]:
            yield chunk["message"]["content"]


# -------------------------------
# 4. Safe JSON Parsing
# -------------------------------

def _strip_js_comments(text: str) -> str:
    """Remove JavaScript-style single and multi-line comments."""
    text = re.sub(r'//.*?(?=[\n,}\]])', '', text)  # Remove // comments but keep delimiters
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)  # Remove /* */ comments
    return text


def _remove_trailing_commas(text: str) -> str:
    """Remove trailing commas before closing brackets/braces."""
    text = re.sub(r',\s*}', '}', text)  # Remove trailing comma before }
    text = re.sub(r',\s*]', ']', text)  # Remove trailing comma before ]
    text = re.sub(r',(\s*[,}\]])', r'\1', text)  # Remove multiple consecutive commas
    return text


def _normalize_evidence(text: str) -> str:
    """Convert empty or problematic evidence fields to valid strings."""
    # Replace empty evidence: "evidence": "" with "evidence": "Not specified"
    text = re.sub(r'"evidence"\s*:\s*""', '"evidence": "Not specified"', text)
    # Fix evidence with only comments/whitespace
    text = re.sub(r'"evidence"\s*:\s*[^,}]*//[^,}]*', '"evidence": "Not specified"', text)
    return text


def _normalize_matched_status(text: str) -> str:
    """Ensure matched_in_resume is always 'Yes' or 'No'."""
    # Handle any malformed values and default to "No" if unclear
    text = re.sub(r'"matched_in_resume"\s*:\s*""', '"matched_in_resume": "No"', text)
    text = re.sub(r'"matched_in_resume"\s*:\s*(?!["Yes|"No)[^,}]*', '"matched_in_resume": "No"', text)
    return text


def _clean_skill_names(text: str) -> str:
    """Remove trailing incomplete skill names and empty entries."""
    # Find all skill_in_jd values and remove empty ones
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines with empty skill_in_jd
        if '"skill_in_jd"' in line and '""' in line:
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def extract_json(text: str) -> List[Dict]:
    """
    Robustly parse malformed JSON from LLM with comments, trailing commas, and incomplete fields.
    """
    # Aggressive cleaning
    text = _strip_js_comments(text)
    text = _normalize_evidence(text)
    text = _normalize_matched_status(text)
    text = _remove_trailing_commas(text)
    text = _clean_skill_names(text)
    
    # Try standard parsing first
    try:
        data = json.loads(text)
        if isinstance(data, list):
            valid_data = [
                item for item in data
                if item.get('skill_in_jd') and item.get('skill_in_jd').strip()
                and item.get('matched_in_resume') in ['Yes', 'No']
            ]
            if valid_data:
                return valid_data
    except json.JSONDecodeError:
        pass
    
    # Fallback: manual parsing
    try:
        # Extract array content
        start = text.find('[')
        end = text.rfind(']')
        if start >= 0 and end > start:
            content = text[start + 1:end]
            
            # Split by objects manually
            objects = []
            depth = 0
            current_obj = ''
            in_string = False
            escape = False
            
            for char in content:
                if char == '"' and not escape:
                    in_string = not in_string
                escape = char == '\\' and not escape
                
                if not in_string:
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        current_obj += char
                        if depth == 0:
                            objects.append(current_obj.strip())
                            current_obj = ''
                            continue
                
                current_obj += char
            
            # Parse each object
            valid_data = []
            for obj_str in objects:
                if not obj_str.strip():
                    continue
                obj_str = '{' + obj_str if not obj_str.startswith('{') else obj_str
                try:
                    item = json.loads(obj_str)
                    # Validate and fix
                    if item.get('skill_in_jd') and item.get('skill_in_jd').strip():
                        if item.get('matched_in_resume') not in ['Yes', 'No']:
                            item['matched_in_resume'] = 'No'
                        if not item.get('evidence'):
                            item['evidence'] = 'Not specified'
                        valid_data.append(item)
                except json.JSONDecodeError:
                    pass
            
            if valid_data:
                return valid_data
    except Exception as e:
        print(f"Fallback parsing error: {e}")
    
    # Last resort: return error object
    raise ValueError(f"Could not parse JSON after aggressive cleaning. Last attempt:\n{text[:500]}")


# -------------------------------
# 5. Convert JSON → Markdown Table
# -------------------------------
def json_to_markdown(data: List[Dict]) -> str:
    table = "| Skill in JD | Matched in Resume | Evidence/Insight |\n"
    table += "| :--- | :--- | :--- |\n"
    for item in data:
        table += f"| {item.get('skill_in_jd','')} | {item.get('matched_in_resume','')} | {item.get('evidence','')} |\n"
    return table


# -------------------------------
# 6. Compute Match Score
# -------------------------------
def compute_match_score(data: List[Dict]) -> Dict:
    total = len(data)
    matched = sum(1 for d in data if d.get("matched_in_resume") == "Yes")
    missing_skills = [d.get("skill_in_jd") for d in data if d.get("matched_in_resume") == "No"]
    score = (matched / total) * 100 if total > 0 else 0
    return {"match_percentage": round(score, 2), "missing_skills": missing_skills}


# -------------------------------
# 7. Main Pipeline Function (Blocking)
# -------------------------------
def match_job(resume_skill_dict: dict = None, jd_skill_dict: dict = None, comparison: dict = None) -> Dict:
    parsed_json = generate_skill_analysis_json(resume_skill_dict, jd_skill_dict, comparison)
    markdown_table = json_to_markdown(parsed_json)
    score_data = compute_match_score(parsed_json)
    return {
        "table": markdown_table,
        "match_percentage": score_data["match_percentage"],
        "missing_skills": score_data["missing_skills"],
        "raw_json": parsed_json
    }


# -------------------------------
# 8. Fast JSON Generator (No LLM)
# -------------------------------
def generate_skill_analysis_json(resume_skill_dict: dict = None, jd_skill_dict: dict = None, comparison: dict = None) -> List[Dict]:
    """Generate skill analysis JSON instantly from comparison data without LLM."""
    resume_skill_dict = resume_skill_dict or {}
    jd_skill_dict = jd_skill_dict or {}
    comparison = comparison or {}
    
    result = []
    
    # For each skill in JD, determine if matched in resume
    for skill in jd_skill_dict.keys():
        matched = "Yes" if skill in resume_skill_dict else "No"
        
        # Generate evidence
        if matched == "Yes":
            resume_count = resume_skill_dict.get(skill, 0)
            jd_count = jd_skill_dict.get(skill, 0)
            evidence = f"Resume: {resume_count}x, JD: {jd_count}x"
        else:
            evidence = "Not found in resume"
        
        result.append({
            "skill_in_jd": skill,
            "matched_in_resume": matched,
            "evidence": evidence
        })
    
    return result


# -------------------------------
# 9. Streaming Pipeline Function
# -------------------------------
async def stream_resume_analysis(resume_skill_dict: dict = None, jd_skill_dict: dict = None, comparison: dict = None):
    """Stream skill analysis instantly without LLM call."""
    try:
        # Generate JSON directly (no LLM call)
        analysis_data = generate_skill_analysis_json(resume_skill_dict, jd_skill_dict, comparison)
        
        # Yield as formatted JSON
        yield "["
        for i, item in enumerate(analysis_data):
            if i > 0:
                yield ","
            yield json.dumps(item)
        yield "]"
        
        print(f"✓ Generated {len(analysis_data)} skills in analysis (no LLM call)")
    except Exception as e:
        print(f"Error in stream_resume_analysis: {str(e)}")
        yield json.dumps([{"skill_in_jd": "Error", "matched_in_resume": "No", "evidence": str(e)}])
