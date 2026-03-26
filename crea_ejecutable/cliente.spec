# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Usar ruta absoluta del proyecto
PROJECT_ROOT = r"C:\gestion_oficios"

# Lista de módulos ocultos necesarios
hiddenimports = [
    'psycopg2',
    'psycopg2.extras',
    'psycopg2._psycopg',
    'psycopg2.extensions',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'fitz',
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.reader.excel',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'dotenv',
    'dotenv.main',
    'dotenv.parser',
    'mimetypes',
    'tempfile',
    'platform',
    'subprocess',
    'secrets',
    'hashlib',
    'threading',
    'json',
    'logging',
    'datetime',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
]

a = Analysis(
    ['run_cliente.py'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_ROOT, '.env'), '.'),
        (os.path.join(PROJECT_ROOT, 'cliente'), 'cliente'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestionOficios_Cliente',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)