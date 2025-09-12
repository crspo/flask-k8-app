import os
import sys

# Ensure repo root is on sys.path so 'backend' can be imported when running
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.utils.encoder import encode_text_to_qr, generate_qr_pdf


def main():
    s = encode_text_to_qr('TEST123', scale=25)
    print('ENCODED START:', s[:30])
    pdf = generate_qr_pdf('TEST123', scale=25)
    print('PDF bytes len:', len(pdf))


if __name__ == '__main__':
    main()
