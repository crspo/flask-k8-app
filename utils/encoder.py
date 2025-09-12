"""Compatibility re-export for encoder functions.

Many modules import `utils.encoder`. The real implementation lives in
`backend.utils.encoder` for this project layout; re-export the functions here
so both import paths work.
"""
from backend.utils.encoder import encode_text_to_qr, generate_qr_pdf

__all__ = ["encode_text_to_qr", "generate_qr_pdf"]
