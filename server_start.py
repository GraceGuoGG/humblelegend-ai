#!/usr/bin/env python3
"""直接启动服务器"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.simple_server import start_server

print("Starting HumbleLegend API Server...")
print("Host: 0.0.0.0")
print("Port: 8000")
print("Press Ctrl+C to stop")
print("-" * 40)

start_server('0.0.0.0', 8000)
