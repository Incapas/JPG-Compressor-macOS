import io
import json
from pathlib import Path
       
def read_data(file: str) -> str:
        """
        Lit et retourne les données JSON à partir d'un fichier.

        Cette fonction tente d'ouvrir et de lire un fichier JSON.
        Si la lecture réussit, elle retourne les données JSON décodées.
        En cas d'erreur (par exemple, si le fichier n'existe pas ou n'est pas un JSON valide),
        elle retourne une chaîne vide ("").

        Args:
            file (str): Le chemin du fichier JSON à lire.

        Returns:
            any: Les données JSON décodées si la lecture réussit, sinon une chaîne vide ("").
        """
        try:
            with io.open(file=file, mode="r") as f:
                return json.load(f)
        except:
            return "" 

def write_data(file: str, data: str) -> None:
    """
    Écrit des données sous forme JSON dans un fichier.

    Cette fonction prend des données et les écrit dans un fichier spécifié au format JSON.
    Elle utilise l'encodage UTF-8 pour gérer les caractères non-ASCII.

    Args:
        file (str): Le chemin du fichier dans lequel écrire les données JSON.
        data (str): Les données à écrire dans le fichier.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """
    with io.open(file=file, mode="w", encoding="utf-8") as f:
        json.dump(obj=data, fp=f, ensure_ascii=False)
    return None

def check_the_existence_of_an_export_directory() -> None:
        """
        Vérifie l'existence et la validité du dossier d'exportation configuré, et initialise un dossier par défaut si nécessaire.

        Cette fonction effectue les opérations suivantes :
        1.  Tente de lire le chemin du dossier d'exportation à partir du fichier 'export_directory.json'.
        2.  Si le fichier existe et contient une chaîne vide (""), cela signifie qu'aucun dossier n'a été configuré.
            Dans ce cas, le chemin du dossier utilisateur (Path.home()) est écrit dans 'export_directory.json' comme dossier par défaut.
        3.  Si le fichier existe mais contient un chemin valide, la fonction ne fait rien.
        4.  Si une exception JSONDecodeError se produit lors de la lecture du fichier (indiquant un fichier JSON invalide ou inexistant),
            le chemin du dossier utilisateur est écrit dans 'export_directory.json' comme dossier par défaut.

        La fonction garantit qu'un dossier d'exportation est toujours configuré, même si l'utilisateur ne l'a pas explicitement défini.

        Returns:
            None: La fonction ne retourne aucune valeur.
         """
        try:
            with io.open(file="export_directory.json", mode="r") as f:
                if json.load(f) == "":
                    write_data(file="export_directory.json", data=str(Path.home()))
                    return None
                else:
                    return None
        except json.decoder.JSONDecodeError as e:
            write_data(file="export_directory.json", data=str(Path.home()))
            return None