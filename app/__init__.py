"""Compatibility package for legacy `app.*` imports.

The source lives under `backend/app`, but older tests and modules import from
`app.*`. Point this package at the backend app path so both styles resolve.
"""
from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "backend" / "app")]
