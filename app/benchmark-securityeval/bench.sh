#!/usr/bin/env bash
set -euo pipefail

git clone https://github.com/S2E-Lab/SecurityEval.git bench


export REPO_DIR="../../bench"
export OUT_DIR_NAME="Testcases_securecoder"
./gradlew -Dorg.gradle.java.home=/Users/mac112/Library/Java/JavaVirtualMachines/corretto-23.0.2/Contents/Home --no-daemon :app:benchmark-securityeval:run

