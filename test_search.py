#!/usr/bin/env python3
import os
import json
from ddgs import DDGS

# 测试不使用代理
print("Testing without proxy...")
try:
    results = list(DDGS().text("Python", max_results=2))
    print(json.dumps(results, indent=2))
except Exception as e:
    print(f"Error: {e}")
