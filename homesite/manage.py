#!/usr/bin/env python
from pathlib import Path
import os
import sys

if __name__ == '__main__':
    sys.path.pop(0)

    BASE_DIR = Path(__file__).resolve().parent.parent
    if str(BASE_DIR) not in sys.path:
        sys.path.append(str(BASE_DIR))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homesite.settings')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
