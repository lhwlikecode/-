"""
Step 3: Use DeepSeek (or any OpenAI-compatible API) to clean up OCR code.
Usage:
  python step3_deepseek.py -i ./ocr_output -o ./final_code -k YOUR_API_KEY
  python step3_deepseek.py -i ./ocr_output -o ./final_code -k YOUR_API_KEY --base-url https://api.openai.com/v1 --model gpt-4o
"""

import os
import re
import sys
import json
import argparse
from openai import OpenAI


def read_all_txt(txt_dir):
    """Read all .txt files from a directory."""
    files = {}
    for fname in sorted(os.listdir(txt_dir)):
        if fname.endswith('.txt'):
            path = os.path.join(txt_dir, fname)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.strip():
                files[fname] = content
    return files


def build_prompt(files):
    """Build the prompt for the LLM."""
    files_section = ""
    for fname, content in files.items():
        files_section += f"\n### Source: {fname}\n```\n{content}\n```\n"

    return f"""You are a professional code restoration engineer. The following code snippets
were extracted from a programming tutorial video via OCR. They have these issues:
1. OCR character errors (e.g., 1/l confusion, symbol errors)
2. The same file's code may be split across multiple snippets
3. File names may not match the actual file names in the video

Your tasks:
- Fix all OCR syntax errors
- Merge code snippets that belong to the same file
- Infer the correct file name from the code content (class name, package name, etc.)
- Output complete, runnable code for each file

{files_section}

Output strictly in the following JSON format, nothing else:
```json
[
  {{
    "filename": "ExactFileName.java",
    "code": "the complete, fixed code"
  }},
  ...
]
```

Notes:
- filename must match what the video shows (use class name to infer, e.g., public class UserService -> UserService.java)
- code should be the full, compilable source file
- If you can't determine a file name, use the main class or function name
"""


def parse_response(text):
    """Extract JSON from the LLM response."""
    m = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if m:
        text = m.group(1)
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(
        description="Use LLM to clean up OCR-extracted code"
    )
    parser.add_argument("-i", required=True, help="Directory containing OCR txt files")
    parser.add_argument("-o", default="./final_code", help="Output directory for cleaned code")
    parser.add_argument("-k", required=True, help="API key")
    parser.add_argument("--base-url", default="https://api.deepseek.com", help="API base URL")
    parser.add_argument("--model", default="deepseek-chat", help="Model name")
    args = parser.parse_args()

    if not os.path.isdir(args.i):
        print(f"[FAIL] Input directory not found: {args.i}")
        sys.exit(1)

    files = read_all_txt(args.i)
    if not files:
        print(f"[FAIL] No .txt files found in: {args.i}")
        sys.exit(1)

    print(f"[OK] Found {len(files)} code snippet files:")
    for fname, content in files.items():
        print(f"  {fname}: {len(content)} chars")

    client = OpenAI(api_key=args.k, base_url=args.base_url)
    prompt = build_prompt(files)

    print(f"\n[AI] Sending to {args.model} at {args.base_url} ...")
    try:
        resp = client.chat.completions.create(
            model=args.model,
            messages=[
                {"role": "system", "content": "You are a strict code repair tool. Output only the specified JSON format, nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=8000,
        )
        reply = resp.choices[0].message.content
    except Exception as e:
        print(f"[FAIL] API call failed: {e}")
        sys.exit(1)

    try:
        file_list = parse_response(reply)
    except Exception as e:
        print(f"[FAIL] Failed to parse AI response: {e}")
        print("--- Raw response (first 800 chars) ---")
        print(reply[:800])
        sys.exit(1)

    os.makedirs(args.o, exist_ok=True)
    for item in file_list:
        fname = item.get('filename', 'unknown.txt')
        code = item.get('code', '')
        out_path = os.path.join(args.o, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"  [OK] {fname} ({len(code)} chars)")

    print(f"\n[DONE] {len(file_list)} files -> {args.o}")


if __name__ == "__main__":
    main()
