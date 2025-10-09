import json
from typing import List, Dict, Any

SYSTEM_PROMPT = (
    "You are an expert Olympiad Question Creator specializing in given exam,grade and level.\n"
    "Generate multiple-choice questions. Ensure that all questions are unique, not repeated within this session, and not "
    "trivial rephrasings of earlier questions. Avoid very generic textbook-style questions. Ensure all four options are distinct, meaningful."
    "Each question should test a new concept or application, not duplicate previously asked material"
    "Generate unique multiple-choice questions (MCQs) and output only valid JSON conforming to the provided schema.\n"
    "Each question must include: question_text, 4 unique options (A–D), one correct_option (A|B|C|D), a detailed solution, "
    "difficulty in {easy, medium, hard}, and syllabus_id chosen from the provided list.\n\n"

    "STRICT REQUIREMENTS:\n"
    "- Questions must be appropriate for the given grade students\n"
    "- Use simple, clear language that given grade students can understand\n"
    "- Questions must be educational and follow academic standards\n"
    "- Ensure questions are unique and not repetitive\n"
    "- All questions must relate to the provided syllabus topics\n"
    "- Difficulty should be aligned\n\n"

    "GUARDRAILS:\n"
    "- NO inappropriate content\n"
    "- NO questions requiring advanced mathematical concepts\n"
    "- NO overly complex scientific terminology\n"
    "- Questions must be factually accurate\n"
    "- Solutions must be clear and educational\n\n"

    "QUALITY CHECKS:\n"
    "- Each question should have one clearly correct answer\n"
    "- Wrong options should be plausible but clearly incorrect\n"
    "- Solutions should explain WHY the answer is correct\n\n"

    "CRITICAL:\n"
    "- Output must be valid JSON only.\n"
    "- Ensure questions options are unique and not repetitive"
    "- Each question must have exactly four options [A, B, C, D]. All options must be unique and distinct, without "
    "repetition or overlap. Do not include banned options like All of the above or None of the above."
    "- Do not add any explanations, commentary, or formatting like ```json.\n"

    "Avoid template phrasing; ensure each question is novel with distinct numbers, objects, or contexts.\n"
    "Return ONLY the JSON object; no extra text or markdown.\n"
)

def _difficulty_for_level(level: int) -> str:
    # return "easy" if level <= 1 else ("medium" if level == 2 else "hard")
    return "easy"

def make_user_prompt_for_section(
    section_name: str,
    topics: List[Dict[str, Any]],
    exam: str,
    grade: int,
    level: int,
) -> str:
    difficulty = _difficulty_for_level(level)

    # Create topics preview
    topics_list = []
    syllabus_options = []
    for topic in topics:
        if topic.get("subtopic"):
            topics_list.append(f"{topic['topic']} → {topic['subtopic']}")
        else:
            topics_list.append(topic["topic"])
        syllabus_options.append({
            "syllabus_id": topic["syllabus_id"],
            "topic": topic["topic"],
            "subtopic": topic.get("subtopic", "")
        })

    topics_text = ", ".join(topics_list)
    pool_json = json.dumps(syllabus_options, ensure_ascii=False)

    return (
        f"""
            - The number of generated questions must be exactly equal to the number of items in syllabus_pool (one question per syllabus_id).
            - Each question must strictly reference its syllabus_id from syllabus_pool:
            * If both topic and subtopic are available, use both in framing the question.
            * If only topic is available, use the topic alone.
            - Do not invent extra topics or subtopics outside syllabus_pool.
            - Ensure every syllabus_id from the pool is used exactly once, mapped to a unique question.

            - Additionally, reference_topics is provided as a list of topics to cover:
            * Ensure that these reference_topics are incorporated into the questions where relevant.
            * Distribute them naturally across the questions so all reference_topics are covered at least once.
            * Priority is: follow syllabus_pool strictly for structure, and then align/reference with reference_topics.
        """
        # f"Task: Generate a QuestionBatch JSON with exactly 2 MCQs.\n"
        f"Section: {section_name}, Exam: {exam} Grade: {grade}, Level: {level}.\n"
        f"Difficulty: {difficulty}.\n"
        f"Topics to cover: {topics_text}\n"
        f"Available syllabus options (choose one syllabus_id per question): {pool_json}\n\n"

        "OUTPUT SCHEMA (strict JSON):\n"
            "{\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"syllabus_id\": <int>,\n"
        "      \"difficulty\": \"easy\" | \"medium\" | \"hard\",\n"
        "      \"question_text\": <string>,\n"
        "      \"option_a\": <string>,\n"
        "      \"option_b\": <string>,\n"
        "      \"option_c\": <string>,\n"
        "      \"option_d\": <string>,\n"
        "      \"correct_option\": \"A\" | \"B\" | \"C\" | \"D\",\n"
        "      \"solution\": <string>,\n"
        "      \"is_active\": true\n"
        "    }\n"
        "  ]\n"
        "}\n\n"

        "Rules:\n"
        f"- Return exactly told items in questions.\n"
        "- Use subtopic details in the question when provided.\n"
        "- Options must be unique and plausible; avoid 'All/None of the above'.\n"
        "- Do not repeat question stems; ensure varied contexts and numbers.\n"
        f"- Questions should be educational and age-appropriate for Grade {grade}.\n"
        "- Include clear explanations in solutions.\n"
        "- Return ONLY the JSON object; no markdown or commentary."
    )