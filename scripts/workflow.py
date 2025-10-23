#!/usr/bin/env python3
"""
Complete Workflow Script
Generates descriptions and uploads to Shopify in one go
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main workflow function"""
    parser = argparse.ArgumentParser(description='Complete workflow: Generate descriptions and upload to Shopify')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--upload', action='store_true', help='Upload to Shopify after generating descriptions')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual upload)')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    print("🚀 SHOPIFY AUTOMATION WORKFLOW")
    print("="*60)
    print(f"Input file: {args.input_file}")
    print(f"Upload to Shopify: {'Yes' if args.upload else 'No'}")
    print(f"Dry run: {'Yes' if args.dry_run else 'No'}")
    print("="*60)
    
    # Step 1: Generate descriptions
    input_path = Path(args.input_file)
    output_file = input_path.parent / f"{input_path.stem}_with_descriptions{input_path.suffix}"
    
    generate_cmd = f"python generate_descriptions.py \"{args.input_file}\" -o \"{output_file}\""
    if args.config:
        generate_cmd += f" --config \"{args.config}\""
    if args.headless:
        generate_cmd += " --headless"
    
    if not run_command(generate_cmd, "Generating AI Descriptions"):
        print("❌ Failed to generate descriptions. Exiting.")
        sys.exit(1)
    
    print(f"✅ Descriptions generated and saved to: {output_file}")
    
    # Step 2: Upload to Shopify (if requested)
    if args.upload:
        upload_cmd = f"python upload_with_descriptions.py \"{output_file}\""
        if args.config:
            upload_cmd += f" --config \"{args.config}\""
        if args.dry_run:
            upload_cmd += " --dry-run"
        
        if not run_command(upload_cmd, "Uploading to Shopify"):
            print("❌ Failed to upload to Shopify.")
            sys.exit(1)
        
        print("✅ Upload to Shopify completed!")
    else:
        print("\n📝 Next steps:")
        print(f"1. Review the generated descriptions in: {output_file}")
        print("2. When ready to upload, run:")
        print(f"   python upload_with_descriptions.py \"{output_file}\"")
        if args.dry_run:
            print("   (Add --dry-run for testing)")
    
    print("\n🎉 Workflow completed successfully!")

if __name__ == "__main__":
    main()
