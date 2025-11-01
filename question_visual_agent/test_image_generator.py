from image_generator import generate_image

# Simple test
if __name__ == "__main__":
    print("🧪 Testing Image Generator\n")
    
    # Test prompt
    test_prompt = """A cartoon-style illustration of a pizza showing 2 out of 8 slices remaining, designed for teaching grade 3 students about fractions. Flat vector illustration style with bold outlines. Pizza centered in frame, occupying 70% of image space, shown from a top-down angle. Pizza crust in golden brown (#D2B48C) with red tomato sauce (#FF6347) and green bell pepper (#32CD32) toppings. Solid white background (#FFFFFF) with no shadows. Bright colors to enhance engagement. Soft even lighting from directly above, creating a flat appearance. Child-friendly and inviting. No text, labels, branding, or logos visible. Clean professional educational illustration suitable for young learners. 8K resolution, sharp clean edges, vector-style quality with no gradients."""
    
    # Generate test image
    result = generate_image(
        prompt=test_prompt,
        question_id=2066,
        image_type="option",
        option="d"
    )
    
    if result['success']:
        print(f"\n✅ Test successful!")
        print(f"📁 Image saved at: {result['file_path']}")
    else:
        print(f"\n❌ Test failed!")
        print(f"Error: {result['error']}")