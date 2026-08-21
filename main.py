#!/usr/bin/env python3
"""
KernossAI - Lanzador Principal
Permite la ejecución directa del proyecto mediante: python main.py
"""

import sys
import os

# Asegurar que el directorio raíz esté en el PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from KernossAI.main import main

if __name__ == "__main__":
    main()
