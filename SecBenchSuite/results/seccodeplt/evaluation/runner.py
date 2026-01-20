
import glob
import subprocess
import json
import os
import sys

def run_tests():
    results = {}
    test_files = glob.glob("test_*.py") # They are at root /app
    print(f"Found {len(test_files)} test files.")
    
    for i, test_file in enumerate(test_files):
        print(f"Running functional test {i+1}/{len(test_files)}: {test_file}")
        try:
            res = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            results[test_file] = {
                "return_code": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except subprocess.TimeoutExpired:
            results[test_file] = {"return_code": -1, "error": "Timeout"}
        except Exception as e:
            results[test_file] = {"return_code": -1, "error": str(e)}

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_tests()
