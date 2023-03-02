from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent) not in path:
    path.append(str(Path(__file__).resolve().parent))
if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))
