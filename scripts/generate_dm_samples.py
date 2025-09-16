import os
import sys

# Ensure repo root is on sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.utils.encoder import encode_text_to_qr

samples = {
    'small': 6,
    'medium': 8,
    'large': 12,
}

text = '80ce01234005409ea0\n80ce0424345114c425'  # sample from user's attachment

for name, module_size in samples.items():
    uri = encode_text_to_qr(text, module_size=module_size)
    # strip data: prefix
    if uri.startswith('data:'):
        b64 = uri.split(',', 1)[1]
    else:
        b64 = uri
    out_path = f'backend/static/dm_{name}.png'
    with open(out_path, 'wb') as f:
        f.write(__import__('base64').b64decode(b64))
    print('Wrote', out_path)
