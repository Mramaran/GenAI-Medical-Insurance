"""
CLI entry point for testing the OCR+NLP pipeline.
Usage: python main.py <file_path> [--policy POLICY_NUMBER] [--raw]
"""

import sys
import json
import argparse

from pipeline import process_document, process_multiple_documents


def main():
    parser = argparse.ArgumentParser(
        description="OCR+NLP Pipeline for Medical Insurance Documents"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Path(s) to document file(s) - images or PDFs",
    )
    parser.add_argument(
        "--policy",
        type=str,
        default=None,
        help="Insurance policy number",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Also print raw OCR text",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  Medical Document OCR+NLP Pipeline")
    print("=" * 60)

    try:
        if len(args.files) == 1:
            print(f"\nProcessing: {args.files[0]}")
            result = process_document(args.files[0], args.policy)
        else:
            print(f"\nProcessing {len(args.files)} documents...")
            result = process_multiple_documents(args.files, args.policy)

        # Print structured output
        exclude_set = {"raw_text"} if not args.raw else set()
        output = result.model_dump(exclude=exclude_set)
        print("\n" + json.dumps(output, indent=2, ensure_ascii=False))

        # Summary
        print(f"\nDocument Type: {result.document_type.value}")
        print(f"Confidence: {result.confidence_score}")
        print(f"Extraction Method: {result.extraction_method}")
        if result.missing_fields:
            print(f"Missing Fields: {', '.join(result.missing_fields)}")
        else:
            print("All key fields extracted successfully.")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
