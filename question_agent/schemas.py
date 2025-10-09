from typing import List, Literal
from pydantic import BaseModel, Field, model_validator

Difficulty = Literal["easy", "medium", "hard"]
CorrectKey = Literal["A", "B", "C", "D"]

class QuestionItem(BaseModel):
    syllabus_id: int
    difficulty: Difficulty
    question_text: str = Field(..., min_length=10)
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: CorrectKey
    solution: str = Field(..., min_length=10)
    is_active: bool = True
    _valid: bool = True  # internal flag

    @model_validator(mode="after")
    def validate_options(self):
        opts = [self.option_a.strip(), self.option_b.strip(), self.option_c.strip(), self.option_d.strip()]
        banned = {"All of the above", "None of the above", "All of these", "None of these"}

        if len(set(opts)) != 4 or any(o in banned for o in opts):
            self._valid = False
        return self

class QuestionBatch(BaseModel):
    questions: List[QuestionItem] = Field(..., min_length=1)
    skipped_count: int = 0  # just a counter

    @model_validator(mode="after")
    def filter_invalid_questions(self):
        valid = []
        skipped = 0
        for q in self.questions:
            if getattr(q, "_valid", True):
                valid.append(q)
            else:
                skipped += 1
        self.questions = valid
        self.skipped_count = skipped
        if skipped > 0:
            print(f"LOG: {skipped} question(s) skipped due to duplicate/banned options")
        return self
