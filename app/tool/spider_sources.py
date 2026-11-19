"""Compatibility entry point; Spider artwork generation has been retired.

All platform artwork is generated from docs/images/logo.png by app_icons.py.
Run from app/: python tool/app_icons.py
"""
from app_icons import main

if __name__ == '__main__':
    main()
