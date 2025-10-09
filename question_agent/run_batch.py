#!/usr/bin/env python3
"""
Simple script to run batch processing with different options

Usage:
    python run_batch.py --mode test          # Test with 3 exams
    python run_batch.py --mode production    # Process all exams
    python run_batch.py --mode imo           # Process only IMO exams
    python run_batch.py --mode grade6        # Process only Grade 6 exams
    python run_batch.py --mode custom        # Custom configuration
"""

import asyncio
import argparse
from enhanced_batch_pipeline import (
    run_test_batch,
    run_production_batch,
    run_imo_only_batch,
    run_grade_6_only_batch,
    run_enhanced_batch_pipeline
)
from batch_config import BatchConfig

async def main():
    parser = argparse.ArgumentParser(description='Run batch pipeline for question generation')
    parser.add_argument('--mode', choices=['test', 'production', 'imo', 'grade6', 'custom'], 
                       default='production', help='Processing mode')
    parser.add_argument('--max-exams', type=int, help='Maximum number of exams to process')
    parser.add_argument('--exam', nargs='+', help='Specific exams to process (e.g., IMO IEO)')
    parser.add_argument('--grade', type=int, nargs='+', help='Specific grades to process (e.g., 6 7 8)')
    parser.add_argument('--level', type=int, nargs='+', help='Specific levels to process (e.g., 1 2)')
    parser.add_argument('--skip-existing', action='store_true', default=False, 
                       help='Skip exams that already have questions')
    parser.add_argument('--no-skip-existing', action='store_false', dest='skip_existing',
                       help='Process all exams even if they have questions (default behavior)')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Delay between exams in seconds')
    parser.add_argument('--retries', type=int, default=3, 
                       help='Maximum retries for failed exams')
    parser.add_argument('--verbose', action='store_true', default=True, 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    print("🤖 Olympiad Question Generator - Batch Processing")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Skip existing: {args.skip_existing}")
    print(f"Delay between exams: {args.delay}s")
    print(f"Max retries: {args.retries}")
    print("=" * 60)
    
    try:
        if args.mode == 'test':
            await run_test_batch()
        elif args.mode == 'production':
            await run_production_batch()
        elif args.mode == 'imo':
            await run_imo_only_batch()
        elif args.mode == 'grade6':
            await run_grade_6_only_batch()
        elif args.mode == 'custom':
            # Build custom configuration
            config = BatchConfig(
                max_exams=args.max_exams,
                exam_filter=args.exam,
                grade_filter=args.grade,
                level_filter=args.level,
                skip_existing=args.skip_existing,
                delay_between_exams=args.delay,
                max_retries=args.retries,
                verbose=args.verbose
            )
            await run_enhanced_batch_pipeline(config)
        
        print("\n✅ Batch processing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Batch processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Batch processing failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
