from image_generator import generate_image

# Simple test
if __name__ == "__main__":
    print("🧪 Testing Image Generator\n")
    
    # Test prompt
    test_prompt = """A bright cartoon illustration of Earth with a thick layer of colorful gases surrounding it, designed for teaching grade 3 students about the atmosphere. Flat vector illustration style with bold outlines. Earth positioned in the center of the frame, occupying 60% of the image, shown from a 45-degree top-right angle. Earth colored in vibrant blue (#0000FF) with green (#008000) landmasses. The atmosphere depicted as a gradient of light blue (#ADD8E6) to white (#FFFFFF) surrounding the planet. Solid white background (#FFFFFF) with no shadows. Soft diffused lighting from directly above, creating a flat appearance. Child-friendly and engaging. No text, labels, branding, or logos visible. Clean professional educational illustration suitable for young learners. 8K resolution, sharp clean edges, vector-style quality with no gradients."""
    
    # Generate test image
    result = generate_image(
        prompt=test_prompt,
        question_id=1984,
        image_type="question",
        # option="d"
    )
    
    if result['success']:
        print(f"\n✅ Test successful!")
        print(f"📁 Image saved at: {result['file_path']}")
    else:
        print(f"\n❌ Test failed!")
        print(f"Error: {result['error']}")