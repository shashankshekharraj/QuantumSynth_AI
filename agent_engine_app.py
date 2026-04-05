import os
import sys

# Add current directory to path so imports work correctly in Reasoning Engine
sys.path.append(os.path.dirname(__file__))

from agent import root_agent
from vertexai.preview.reasoning_engines import AdkApp

# Create the AdkApp wrapper
adk_app = AdkApp(
    agent=root_agent,
    enable_tracing=False,
)
