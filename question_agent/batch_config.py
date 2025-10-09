"""
Configuration for Batch Pipeline Processing

This file contains configuration options for the batch pipeline processing.
"""

from typing import Optional, List
from dataclasses import dataclass

@dataclass
class BatchConfig:
    """Configuration for batch processing"""
    
    # Processing options
    skip_existing: bool = False  # Skip exams that already have questions
    max_exams: Optional[int] = None  # Limit number of exams to process (None = all)
    delay_between_exams: float = 1.0  # Delay in seconds between exam processing
    
    # Filtering options
    exam_filter: Optional[List[str]] = None  # Only process specific exams (e.g., ["IMO", "IEO"])
    grade_filter: Optional[List[int]] = None  # Only process specific grades (e.g., [6, 7, 8])
    level_filter: Optional[List[int]] = None  # Only process specific levels (e.g., [1, 2])
    
    # Error handling
    max_retries: int = 3  # Maximum retries for failed exams
    continue_on_error: bool = True  # Continue processing if one exam fails
    
    # Logging
    verbose: bool = True  # Enable verbose logging
    log_to_file: bool = False  # Log to file instead of console
    log_file_path: str = "batch_pipeline.log"
    
    # Performance
    batch_size: int = 1  # Process exams in batches (currently sequential)
    parallel_processing: bool = False  # Enable parallel processing (experimental)

# Default configuration
DEFAULT_CONFIG = BatchConfig()

# Example configurations for different use cases
TEST_CONFIG = BatchConfig(
    max_exams=3,
    skip_existing=False,
    verbose=True
)

PRODUCTION_CONFIG = BatchConfig(
    skip_existing=False,
    delay_between_exams=2.0,
    max_retries=3,
    continue_on_error=True,
    verbose=True
)

IMO_ONLY_CONFIG = BatchConfig(
    exam_filter=["IMO"],
    skip_existing=False,
    verbose=True
)

GRADE_6_ONLY_CONFIG = BatchConfig(
    grade_filter=[12],
    skip_existing=False,
    verbose=True
)
