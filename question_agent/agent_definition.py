"""
OpenAI Agent for Question Generation
"""

import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from schemas import QuestionBatch
from prompts import SYSTEM_PROMPT, make_user_prompt_for_section
from agents import Agent,Runner, RunConfig, ModelSettings, output_guardrail, GuardrailFunctionOutput, RunContextWrapper

# Load environment
load_dotenv()

@output_guardrail
async def structure_output_guardrail(ctx: RunContextWrapper[None], agent: Agent, output: QuestionBatch):
    try:
        # Force validation by re-parsing into QuestionBatch
        _ = QuestionBatch.model_validate(output)

        return GuardrailFunctionOutput(
            output_info={"ok": True, "message": "Valid QuestionBatch structure"},
            tripwire_triggered=False
        )
    except Exception as e:
        return GuardrailFunctionOutput(
            output_info={"error": f"Invalid structure: {str(e)}"},
            tripwire_triggered=True
        )
    
# @output_guardrail
# async def batch_output_guardrail(ctx: RunContextWrapper[None], agent: Agent, output: QuestionBatch):
#     try:
#         seen = set()
#         for item in output.questions:
#             stem = item.question_text.strip().lower()
#             if stem in seen:
#                 return GuardrailFunctionOutput(output_info={"error": "Duplicate stem in batch"}, tripwire_triggered=True)
#             seen.add(stem)
#         return GuardrailFunctionOutput(output_info={"ok": True}, tripwire_triggered=False)
#     except Exception as e:
#         return GuardrailFunctionOutput(output_info={"error": str(e)}, tripwire_triggered=True)

# Agent definition
question_agent = Agent(
    name="Question Generator",
    instructions=SYSTEM_PROMPT,
    output_type=QuestionBatch,
    output_guardrails=[structure_output_guardrail]
    # output_guardrails=[structure_output_guardrail,batch_output_guardrail],
)

async def generate_questions_with_agent(section_info: Dict[str, Any], topics: List[Dict[str, Any]], exam: str, grade: int, level: int) -> Dict[str, Any]:
    """Agent call - just run and return!"""

    if not topics:
        print(f"WARNING: No topics found for section {section_info['section_name']}")
        return {"questions": []}

    # Create user prompt
    user_prompt = make_user_prompt_for_section(
        section_name=section_info["section_name"],
        topics=topics,
        exam=exam,
        grade=grade,
        level=level
    )

    started = time.time()
    # print("started",started)
    try:
        # Run agent
        response = await Runner.run(
            starting_agent=question_agent,
            input=user_prompt,
            run_config=RunConfig(
                model="gpt-4o-2024-08-06",
                model_settings=ModelSettings(temperature=0.7)
            ),
        )

        q = response.final_output
        # print("response",response)
        # print("q",q)

        finished = time.time()

        # print("finished",finished)
        # print(f"Time taken for completion ({section_info["section_name"]}) - ",finished-started)

        payload = q.model_dump()

        print(f"SUCCESS: Generated {len(payload.get('questions', []))} questions for {section_info['section_name']}")
        return payload

    except Exception as e:
        print(f"ERROR: Failed to generate questions for {section_info['section_name']}: {e}")
        return {"questions": []}