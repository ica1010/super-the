# myapp/storage.py
import os
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

class AutoCreateManifestStaticFilesStorage(ManifestStaticFilesStorage):
    # Empêcher le comportement strict qui lève une erreur si un fichier est manquant
    manifest_strict = False

    def post_process(self, paths, dry_run=False, **options):
        # Exécuter le post-process habituel et récupérer les résultats
        processed_files = super().post_process(paths, dry_run, **options)
        if dry_run:
            # En mode dry run, ne rien faire de plus
            yield from processed_files
        else:
            for original_path, processed_path, processed in processed_files:
                # Si le traitement n'a pas eu lieu (processed est None), on crée un fichier vide
                if processed is None:
                    full_path = os.path.join(self.location, original_path)
                    # Créer le répertoire s'il n'existe pas
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    # Créer un fichier vide ou avec un contenu par défaut
                    with open(full_path, 'wb') as f:
                        f.write(b'')
                    # Vous pouvez éventuellement logger cette création
                    yield original_path, original_path, True
                else:
                    yield original_path, processed_path, processed
