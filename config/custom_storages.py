# custom_storages.py
from whitenoise.storage import CompressedManifestStaticFilesStorage

class MyStaticFilesStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
