"""
Master script: Run the full pipeline (capture -> OCR -> DeepSeek cleanup).
Usage:
  python run.py -k YOUR_DEEPSEEK_API_KEY
  python run.py -k YOUR_DEEPSEEK_API_KEY -w "Zoom,Teams" --fullscreen -i 3
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_step(name, cmd):
    print(f"\n{'='*60}")
    print(f"  STEP: {name}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=SCRIPT_DIR, shell=True)
    if result.returncode != 0:
        print(f"\n[FAIL] {name} exited with code {result.returncode}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Code Capture Tool - Full Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py -k sk-xxx
  python run.py -k sk-xxx -w "腾讯会议,Zoom" -i 3
  python run.py -k sk-xxx --fullscreen --model gpt-4o --base-url https://api.openai.com/v1
        """
    )
    parser.add_argument("-k", required=True, help="API key for the LLM (DeepSeek or OpenAI)")
    parser.add_argument("-w", default="腾讯会议,会议室,TencentMeeting,wemeet,Voov,Teams,Zoom",
                        help="Window title keywords to match")
    parser.add_argument("-i", type=int, default=5, help="Screenshot check interval in seconds")
    parser.add_argument("--fullscreen", action="store_true", help="Capture full screen instead of a window")
    parser.add_argument("--tesseract", default=None, help="Path to tesseract.exe")
    parser.add_argument("--base-url", default="https://api.deepseek.com", help="LLM API base URL")
    parser.add_argument("--model", default="deepseek-chat", help="LLM model name")
    parser.add_argument("-o", default=None, help="Output directory name (auto-generated if not set)")
    args = parser.parse_args()

    ts = datetime.now().strftime('%Y%m%d_%H%M')
    base = args.o or f"session_{ts}"

    screenshots_dir = f"{base}_screenshots"
    ocr_dir = f"{base}_ocr"
    final_dir = f"{base}_final"

    # Step 1: Capture
    cmd1 = f'python "{SCRIPT_DIR}/step1_capture.py" -o "{screenshots_dir}" -i {args.i}'
    if args.fullscreen:
        cmd1 += " --fullscreen"
    else:
        cmd1 += f' -w "{args.w}"'
    run_step("1/3 - Capture Screen", cmd1)

    # Step 2: OCR
    cmd2 = f'python "{SCRIPT_DIR}/step2_ocr.py" -i "{screenshots_dir}" -o "{ocr_dir}"'
    if args.tesseract:
        cmd2 += f' --tesseract "{args.tesseract}"'
    run_step("2/3 - OCR Code", cmd2)

    # Step 3: DeepSeek cleanup
    cmd3 = (
        f'python "{SCRIPT_DIR}/step3_deepseek.py"'
        f' -i "{ocr_dir}" -o "{final_dir}"'
        f' -k {args.k}'
        f' --base-url {args.base_url}'
        f' --model {args.model}'
    )
    run_step("3/3 - AI Cleanup", cmd3)

    print(f"\n{'='*60}")
    print(f"  ALL DONE - Final code in: {final_dir}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
