import json
import requests
import ollama

# OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # ya "gemma3:4b" — jo bhi pull kiya ho


def build_prompt(resume_text: str, job_description: str | None = None) -> str:
    jd_section = (
        f"\nJob Description:\n{job_description}\n"
        if job_description
        else "\nNo job description provided — do a general resume quality analysis.\n"
    )

    return f"""You are an expert resume reviewer and ATS system.
        Resume Text:
        {resume_text}
        {jd_section}
        Analyze the resume and respond with ONLY valid JSON (no markdown, no extra text) in this exact format:
        {{
        "match_score": <number 0-100>,
        "skills_found": ["skill1", "skill2"],
        "missing_skills": ["skill1", "skill2"],
        "strengths": ["point1", "point2"],
        "weaknesses": ["point1", "point2"],
        "suggestions": "short paragraph with improvement tips in bullet points "
        }}

        If no job description was given, set match_score based on general resume quality (clarity, structure, impact) and missing_skills as [].
        """



def call_ollama(prompt:str) -> str:
    response = ollama.generate(
        model="gemma3:4b",
        prompt=prompt,
        stream=False, 
        format="json"
    )

    return response["response"]


def analyze_resume(resume_text: str, job_description: str | None = None) -> dict:
    prompt = build_prompt(resume_text, job_description)
    raw_output = call_ollama(prompt)

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON: {raw_output[:200]}")

    return result