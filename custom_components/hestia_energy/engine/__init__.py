"""Hestia Energy's brain, in plain Python.

Nothing here imports Home Assistant (tests/test_engine_pure.py): every module is tested alone, by replaying real
statistics (the rule of Hestia Comfort). The integration around it only reads Home Assistant and hands the facts over.
"""
