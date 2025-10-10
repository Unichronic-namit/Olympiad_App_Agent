import json
from agent import analyze_question

# Run the agent
if __name__ == "__main__":
    question_id = int(input("Enter question ID: "))
    result = analyze_question(question_id)
    
    print("\n" + "="*60)
    print("📊 FINAL RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))