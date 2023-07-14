#!/usr/bin/env bash
set -euo pipefail

cd lambdas/transcribe
pip install --requirement requirements.txt --target ./modules --no-cache-dir
cd modules
rm -r *.dist-info __pycache__ *tests*
zip -r ../lambda.zip .
cd ..
zip lambda.zip lambda.py
# rm -r ./modules

