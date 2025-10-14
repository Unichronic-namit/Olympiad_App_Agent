import json
from agent import analyze_question, analyze_questions_by_grade

def main():
    print("\n" + "="*60)
    print("🎨 QUESTION VISUAL ANALYSIS AGENT")
    print("="*60)
    
    print("\nChoose an option:")
    print("1. Analyze a single question by ID")
    print("2. Analyze all questions for a specific grade")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-2): ").strip()
    
    if choice == "1":
        # Single question analysis
        question_id = int(input("Enter question ID: "))
        result = analyze_question(question_id)
        
        print("\n" + "="*60)
        print("📊 FINAL RESULT")
        print("="*60)
        print(json.dumps(result, indent=2))
    
    elif choice == "2":
        # Grade-based batch analysis
        grade = int(input("Enter grade (1-12): "))
        
        if grade < 1 or grade > 12:
            print("❌ Invalid grade! Must be between 1 and 12.")
            return
        
        max_workers = input("Enter number of parallel workers (default 5): ").strip()
        max_workers = int(max_workers) if max_workers else 5
        
        results = analyze_questions_by_grade(grade, max_workers)
        
    elif choice == "0":
        print("\n👋 Goodbye!")
    
    else:
        print("\n❌ Invalid choice!")

if __name__ == "__main__":
    main()