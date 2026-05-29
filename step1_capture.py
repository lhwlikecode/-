"""
Step 1: Capture screenshots when screen content changes.
Usage:
  python step1_capture.py -o ./screenshots -i 3
  python step1_capture.py -o ./screenshots -i 3 -w "腾讯会议,Teams,Zoom"
"""

import os
import time
import sys
import ctypes
import argparse
from ctypes import wintypes
from datetime import datetime

import cv2
import numpy as np
from mss import MSS


def find_window_by_keywords(keywords_str="腾讯会议,会议室,TencentMeeting,wemeet,Voov,Teams,Zoom"):
    """Find windows whose titles contain any of the given keywords."""
    keywords = [k.strip() for k in keywords_str.split(",")]
    user32 = ctypes.windll.user32
    results = []

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def enum_callback(hwnd, lParam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value
        if not title:
            return True
        if not any(k.lower() in title.lower() for k in keywords):
            return True
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w > 200 and h > 200:
            results.append((rect.left, rect.top, w, h, title))
        return True

    proc = WNDENUMPROC(enum_callback)
    user32.EnumWindows(proc, 0)

    if results:
        return results[0]
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Capture screenshots when screen content changes"
    )
    parser.add_argument(
        "-o", default=f"./screenshots_{datetime.now().strftime('%Y%m%d_%H%M')}",
        help="Output directory for screenshots"
    )
    parser.add_argument(
        "-i", type=int, default=5,
        help="Detection interval in seconds (default: 5)"
    )
    parser.add_argument(
        "-w", default="腾讯会议,会议室,TencentMeeting,wemeet,Voov,Teams,Zoom",
        help="Comma-separated window title keywords to match"
    )
    parser.add_argument(
        "--fullscreen", action="store_true",
        help="Capture entire primary monitor instead of a specific window"
    )
    args = parser.parse_args()

    os.makedirs(args.o, exist_ok=True)
    print(f"[OK] Output directory: {args.o}")

    with MSS() as sct:
        if args.fullscreen:
            monitor = sct.monitors[0]
            print(f"[OK] Fullscreen mode: {monitor['width']}x{monitor['height']}")
        else:
            result = find_window_by_keywords(args.w)
            if result:
                monitor = {"top": result[1], "left": result[0],
                           "width": result[2], "height": result[3]}
                print(f"[OK] Found window: \"{result[4]}\" ({result[2]}x{result[3]})")
            else:
                print(f"[FAIL] No window found matching: {args.w}")
                print("       Try --fullscreen or adjust -w keywords.")
                sys.exit(1)

        prev_gray = None
        count = 0
        next_check = time.time()

        print(f"[RUN] Checking every {args.i}s for changes. Press Ctrl+C to stop.")
        try:
            while True:
                now = time.time()
                if now < next_check:
                    time.sleep(0.3)
                    continue
                next_check = now + args.i

                frame = np.array(sct.grab(monitor))
                gray = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2GRAY)

                changed = (prev_gray is None)
                if prev_gray is not None:
                    diff = cv2.absdiff(prev_gray, gray)
                    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                    ratio = np.sum(thresh > 0) / thresh.size
                    if ratio > 0.01:
                        changed = True

                if changed:
                    count += 1
                    ts = datetime.now().strftime("%H:%M:%S")
                    fname = f"shot_{count:04d}.png"
                    cv2.imwrite(os.path.join(args.o, fname), frame)
                    print(f"[{ts}] #{count} -> {fname}")
                    prev_gray = gray

        except KeyboardInterrupt:
            print(f"\n[DONE] {count} screenshots saved -> {args.o}")


if __name__ == "__main__":
    main()
