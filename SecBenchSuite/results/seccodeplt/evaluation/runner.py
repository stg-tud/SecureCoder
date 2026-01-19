
import glob
import subprocess
import json
import os
import sys
import shutil

def run_cmd(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

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

def run_codeql():
    print("Starting CodeQL analysis...")
    src_root = "/app/source"
    db_path = "/app/codeql_db"
    output_sarif = "/app/codeql_results.sarif"
    
    if not os.path.exists(src_root):
        print(f"Source root {src_root} not found")
        return

    # Create DB
    # Assuming codeql in PATH
    cmd_create = ["codeql", "database", "create", db_path, "--language=python", f"--source-root={src_root}", "--overwrite"]
    res = run_cmd(cmd_create)
    if res.returncode != 0:
        print(f"CodeQL DB Create Failed: {res.stderr}")
        return

    # Analyze
    # Using the pre-downloaded pack codeql/python-queries or specific suite
    # In Dockerfile we did: 'codeql pack download codeql/python-queries'
    # So we can reference the suite by name or path.
    # Standard suite: codeql/python-queries:codeql-suites/python-security-extended.qls
    
    cmd_analyze = [
        "codeql", "database", "analyze", db_path,
        "codeql/python-queries:codeql-suites/python-security-extended.qls",
        "--format=sarif-latest",
        f"--output={output_sarif}"
    ]
    res = run_cmd(cmd_analyze)
    if res.returncode != 0:
        print(f"CodeQL Analyze Failed: {res.stderr}")
        # Try finding standard library path if pack fails?
        # But 'codeql/python-queries' should resolve if downloaded.
    else:
        print("CodeQL analysis successful.")

if __name__ == "__main__":
    # Install dependencies first (pip install -r requirements.txt is done in command string)
    run_tests()
    run_codeql()
