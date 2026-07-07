from dotenv import load_dotenv
import os
from pathlib import Path

env_file = Path('.env')
print(f'File exists: {env_file.exists()}')
if env_file.exists():
    content = env_file.read_text(encoding='utf-8')
    print(f'Content: {repr(content)}')
    
load_dotenv(dotenv_path=str(env_file))
print(f'DB_HOST after load: {os.environ.get(\"DB_HOST\")}')
print(f'DB_PORT after load: {os.environ.get(\"DB_PORT\")}')
