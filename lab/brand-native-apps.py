"""Compatibility entry point for the current NSIPA brand."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('brand-native-nsipa.py')),run_name="__main__")
