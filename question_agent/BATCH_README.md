# 🤖 Automated Batch Processing for Olympiad Questions

This directory contains automated batch processing scripts that will run your question generation pipeline for ALL exam overviews in your database.

## 📁 Files Created

- `batch_pipeline.py` - Basic batch processing script
- `enhanced_batch_pipeline.py` - Advanced batch processing with configuration
- `batch_config.py` - Configuration options and presets
- `run_batch.py` - Command-line interface for easy execution

## 🚀 Quick Start

### 1. Basic Usage (Recommended)

```bash
# Process all exams (including those with existing questions)
python run_batch.py --mode production

# Test with only 3 exams
python run_batch.py --mode test

# Process only IMO exams
python run_batch.py --mode imo

# Process only Grade 6 exams
python run_batch.py --mode grade6
```

### 2. Advanced Usage

```bash
# Custom configuration
python run_batch.py --mode custom --exam IMO IEO --grade 6 7 --max-exams 10

# Skip exams that already have questions (if you want to avoid duplicates)
python run_batch.py --mode production --skip-existing

# Add delay between exams
python run_batch.py --mode production --delay 2.0

# Increase retry attempts
python run_batch.py --mode production --retries 5
```

### 3. Direct Script Usage

```python
# In Python
import asyncio
from enhanced_batch_pipeline import run_production_batch

# Run production batch
asyncio.run(run_production_batch())
```

## ⚙️ Configuration Options

### BatchConfig Parameters

- `skip_existing`: Skip exams that already have questions (default: False)
- `max_exams`: Limit number of exams to process (default: None = all)
- `delay_between_exams`: Delay in seconds between exams (default: 1.0)
- `exam_filter`: Only process specific exams (e.g., ["IMO", "IEO"])
- `grade_filter`: Only process specific grades (e.g., [6, 7, 8])
- `level_filter`: Only process specific levels (e.g., [1, 2])
- `max_retries`: Maximum retries for failed exams (default: 3)
- `continue_on_error`: Continue processing if one exam fails (default: True)

### Predefined Configurations

- `TEST_CONFIG`: Process 3 exams only
- `PRODUCTION_CONFIG`: Process all exams (including existing questions)
- `IMO_ONLY_CONFIG`: Process only IMO exams
- `GRADE_6_ONLY_CONFIG`: Process only Grade 6 exams

## 📊 What It Does

1. **Fetches all exam overviews** from your database
2. **Applies filters** based on your configuration
3. **Checks existing questions** (if skip_existing=True, but default is False)
4. **Processes each exam** using your existing pipeline
5. **Handles errors** with retry logic
6. **Tracks progress** and provides detailed reporting
7. **Generates summary** of all results

## 🔄 Processing Flow

```
Database → Filter Exams → Check Existing → Generate Questions → Save to DB → Next Exam
```

## 📈 Progress Tracking

The batch processor provides:
- Real-time progress updates
- Detailed logging
- Error tracking and retry attempts
- Final summary with statistics
- Individual exam results

## 🛡️ Safety Features

- **Processes All Exams**: Will generate questions for all exams by default
- **Error Recovery**: Retries failed exams up to 3 times
- **Graceful Handling**: Continues processing even if some exams fail
- **Progress Logging**: Detailed logs for monitoring and debugging

## 📝 Example Output

```
🤖 Olympiad Question Generator - Batch Processing
============================================================
Mode: production
Skip existing: False
Delay between exams: 1.0s
Max retries: 3
============================================================

Fetching exam overviews with filters applied...
Found 15 exam overviews matching filters:
  - IMO Grade 6 Level 1 (25 questions)
  - IMO Grade 6 Level 2 (30 questions)
  - IEO Grade 7 Level 1 (20 questions)
  ...

Processing 15 exam overviews...
Processing 1/15: IMO Grade 6 Level 1
✅ Completed IMO Grade 6 Level 1: 25 questions in 12.3s

Processing 2/15: IMO Grade 6 Level 2
✅ Completed IMO Grade 6 Level 2: 30 questions in 15.7s

...

================================================================================
ENHANCED BATCH PIPELINE COMPLETE!
================================================================================
Total Exams Processed: 15
  ✅ Completed: 12
  ⏭️  Skipped: 2
  ❌ Failed: 1
Total Questions Generated: 285
Total Processing Time: 180.5 seconds
Average Time per Exam: 12.0 seconds
================================================================================
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check your `DATABASE_URL` in `.env` file
   - Ensure database is accessible

2. **OpenAI API Error**
   - Check your `OPENAI_API_KEY` in `.env` file
   - Verify API key has sufficient credits

3. **Memory Issues**
   - Reduce `max_exams` to process fewer exams at once
   - Increase `delay_between_exams` to reduce load

4. **Timeout Errors**
   - Increase `max_retries` for more attempts
   - Check network connectivity

### Debug Mode

```bash
# Enable verbose logging
python run_batch.py --mode production --verbose

# Process only 1 exam for testing
python run_batch.py --mode custom --max-exams 1
```

## 🔧 Customization

You can create custom configurations by modifying `batch_config.py` or using the command-line options:

```python
# Custom configuration example
from batch_config import BatchConfig
from enhanced_batch_pipeline import run_enhanced_batch_pipeline

custom_config = BatchConfig(
    exam_filter=["IMO", "IEO"],
    grade_filter=[6, 7, 8],
    level_filter=[1, 2],
    skip_existing=True,
    max_exams=20,
    delay_between_exams=2.0,
    max_retries=5
)

asyncio.run(run_enhanced_batch_pipeline(custom_config))
```

## 📚 Next Steps

1. **Test the batch processor** with a small subset first
2. **Monitor the logs** to ensure everything works correctly
3. **Adjust configuration** based on your needs
4. **Schedule regular runs** to keep your question bank updated
5. **Set up monitoring** for production use

---

*Happy question generating! 🚀*
