import sys
from pathlib import Path

CANDIDATES = Path(__file__).parent / "candidates"
# logs_quadratic imports from logs_good, and graded files are loaded by path in a fresh process.
sys.path.insert(0, str(CANDIDATES))
