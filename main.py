import io
import os
import json
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

import front
from tools import *

# Déclaration de la variable globale permettant de stocker les caractéristiques des images à compresser
data = {}       
       
def config_container(function):
    """
    Décorateur qui permet de configurer l'expansion du conteneur 'container' Tkinter.
    Il inverse l'état d'expansion du conteneur avant d'exécuter la fonction décorée.
    Si le conteneur est déjà configuré pour s'étendre (expand=True), il sera configuré pour ne pas s'étendre (expand=False) et vice-versa.

    Args:
        function (callable): La fonction à décorer, qui doit interagir avec le conteneur 'container'.

    Returns:
        callable: La fonction enveloppée, qui exécute la fonction d'origine après avoir modifié l'état d'expansion du conteneur.
    """
    def wrapper():   
        container.pack(expand=False) if container.pack_info().get("expand") == 1 else container.pack(expand=True)
        foo = function()
        return foo
    return wrapper

def reset_container(function):
    """
    Décorateur qui permet de réinitialiser le conteneur 'container' Tkinter en détruisant tous ses enfants.
    Il détruit tous les widgets enfants du conteneur avant d'exécuter la fonction décorée.

    Args:
        function (callable): La fonction à décorer, qui doit interagir avec le conteneur 'container'.

    Returns:
        callable: La fonction enveloppée, qui exécute la fonction d'origine après avoir réinitialisé le conteneur.
    """
    def wrapper():
        for element in container.winfo_children():
            element.destroy()
        foo = function()
        return foo
    return wrapper

# Fenêtre principale de l'application.
@config_container
@reset_container
def main_window() -> None:

    def reset() -> None:
        """
        Réinitialise l'état de l'interface principale.

        Cette fonction efface les données de la variable globale 'data'.
        Elle active le bouton de sélection des images, désactive le bouton de compression des images.
        Enfin, elle efface le texte des labels d'information dynamiques.

        Returns:
            None: Cette fonction ne retourne rien.
        """
        data.clear()
        btn_selected_images.configure(state="normal")
        btn_compressed_images.configure(state="disabled")
        label_dynamic_state_of_compression.configure(text="")
        label_dynamic_number_of_images_to_compress.configure(text="")
        label_dynamic_total_weight_before_and_after_compression.configure(text="")
        return None
    
    def select_images_to_compress() -> None:
        """
        Ouvre une boîte de dialogue pour permettre à l'utilisateur de sélectionner des fichiers images JPG ou JPEG.

        La fonction effectue les opérations suivantes :
        1.  Ouvre une boîte de dialogue de sélection de fichiers multiples.
        2.  Vérifie que tous les fichiers sélectionnés sont des images JPG ou JPEG.
        3.  Si des fichiers non valides sont sélectionnés, affiche un message d'avertissement.
        4.  Pour chaque image valide sélectionnée, extrait les informations suivantes et les stocke dans la variable globale 'data' :
            -   Extension de l'image.
            -   Nom de l'image avant compression.
            -   Chemin complet de l'image avant compression.
            -   Poids du fichier de l'image avant compression.
            -   Nom de l'image après compression (nom original avec "-compressée" ajouté).
        5.  Met à jour l'interface utilisateur :
            -   Désactive le bouton de sélection des images.
            -   Active les boutons de compression et de réinitialisation.
            -   Met à jour le label indiquant le nombre d'images sélectionnées et l'état de la compression.
        6.  Si aucune image n'est sélectionnée, affiche un message indiquant qu'aucune image n'a été sélectionnée.
        7.  Si une image est sélectionnée, affiche "1 image" et "Prêt".
        8.  Si plusieurs images sont sélectionnées, affiche le nombre d'images et "Prêt".

        Returns:
            None: Cette fonction ne retourne rien.
        """
        files = filedialog.askopenfilenames()
        extensions = [file.split(sep=".")[-1] for file in files]

        if not all([True if extension in ["jpg", "jpeg", "JPG", "JPEG"] else False for extension in extensions]):
            messagebox.showwarning(message="Attention !\nSeuls les fichiers 'JPG' et 'JPEG' sont autorisés.")
        else:
            for idx, file in enumerate(iterable=files):
                image = Image.open(fp=file)
                data[idx] = {
                    "image_extension": image.filename.split(sep=".")[-1],
                    "image_name_before_compression": image.filename.split(sep="/")[-1].split(sep=".")[0], # ajouter le separateure
                    "image_path_before_compression": image.filename,
                    "image_weight_before_compression": os.path.getsize(filename=image.filename),
                    "image_name_after_compression": f"{image.filename.split(sep="/")[-1].split(sep=".")[0]}-compressée"
                    }

        btn_selected_images.configure(state="disabled")
        btn_compressed_images.configure(state="normal")
        btn_reset.configure(state="normal")

        if len(data) == 0:
            label_dynamic_number_of_images_to_compress.configure(text="Aucune image sélectionnée")
        elif len(data) == 1:
            label_dynamic_state_of_compression.configure(text="Prêt")
            label_dynamic_number_of_images_to_compress.configure(text="1 image")
        else:
            label_dynamic_state_of_compression.configure(text="Prêt")
            label_dynamic_number_of_images_to_compress.configure(text=f"{str(len(data))} images")

        return None

    def compress_selected_images() -> None:
        """
        Compresse les images sélectionnées et stocke les résultats.

        Cette fonction effectue les opérations suivantes :
        1.  Vérifie si des images ont été sélectionnées (si la variable globale 'data' contient des données).
        2.  Si aucune image n'a été sélectionnée, affiche un message d'avertissement.
        3.  Si des images sont sélectionnées, tente de compresser chaque image :
            -   Lit le chemin du dossier d'export à partir du fichier 'export_directory.json'.
            -   Pour chaque image dans 'data' :
                -   Ouvre l'image.
                -   Construit le chemin de sauvegarde de l'image compressée.
                -   Enregistre l'image compressée avec une qualité de 50.
                -   Stocke le chemin de l'image compressée, le poids du fichier compressé et la réduction de poids dans 'data'.
            -   Met à jour l'interface utilisateur :
                -   Affiche "Terminé" dans le label d'état de compression.
                -   Efface le label du nombre d'images.
                -   Calcule et affiche le poids total avant et après compression, ainsi que la différence.
        4.  Si une exception OSError se produit (par exemple, si le dossier d'export n'existe pas) :
            -   Efface les données dans 'data'.
            -   Efface les labels d'état et de nombre d'images.
            -   Désactive les boutons de sélection et de réinitialisation.
        5.  Enfin, désactive le bouton de compression.

        Returns:
            None: Cette fonction ne retourne rien.
        """
        if len(data) < 1:
            messagebox.showwarning(message="Atttention !\nAucune image n'a été importée.\nVeuillez réinitialiser.")

        else:
            try:
                path = read_data(file="export_directory.json")
                for i in range(len(data)):
                    image = Image.open(fp=data[i]["image_path_before_compression"])
                    data[i]["image_path_after_compression"] = f"{path}/{data[i]["image_name_after_compression"]}.{data[i]["image_extension"]}".replace("\"", "")
                    image.save(fp=data[i]["image_path_after_compression"], quality=50)
                    data[i]["image_weight_after_compression"] = os.path.getsize(filename=data[i]["image_path_after_compression"])
                    data[i]["weight_reduced_by"] = data[i]["image_weight_before_compression"] - data[i]["image_weight_after_compression"]

                label_dynamic_state_of_compression.configure(text="Terminé")
                label_dynamic_number_of_images_to_compress.configure(text="")
    
                weight_before_compression = str(round(number=sum([v["image_weight_before_compression"] for k, v in data.items()]) / 1000000, ndigits=2))
                weight_after_compression = str(round(number=sum([v["image_weight_after_compression"] for k, v in data.items()]) / 1000000, ndigits=2))
   
                weight_before_compression_for_difference = float(str(round(number=sum([v["image_weight_before_compression"] for k, v in data.items()]) / 1000000, ndigits=2)))
                weight_after_compression_for_difference = float(str(round(number=sum([v["image_weight_after_compression"] for k, v in data.items()]) / 1000000, ndigits=2)))
         
                label_dynamic_total_weight_before_and_after_compression.configure(text=f"{weight_before_compression} Mo -> {weight_after_compression} Mo | Différence de {str(round(weight_before_compression_for_difference - weight_after_compression_for_difference, ndigits=2))} Mo ")

            except OSError:
                    messagebox.showerror(message="Attention !\n\nVeuillez définir un dossier d'export existant.")
                    data.clear()
                    label_dynamic_state_of_compression.configure(text="")
                    label_dynamic_number_of_images_to_compress.configure(text="")
                    btn_selected_images.configure(state="disabled")
                    btn_reset.configure(state="disabled")

            finally:
                btn_compressed_images.configure(state="disabled")

    # Première section de l'interface graphique
    first_section = ctk.CTkFrame(master=container, fg_color="transparent")
    first_section.pack(anchor="ne", fill="y", expand=True)

    btn_chosen_export_directory = ctk.CTkButton(master=first_section, width=40, height=40, text="", image=front.cogwheel_image, command=export_folder_configuration_window)
    btn_chosen_export_directory.pack(padx=(0, 5), pady=(5, 0))

    # Deuxième section de l'interface graphique
    second_section = ctk.CTkFrame(master=container, fg_color="transparent")
    second_section.pack()

    btn_selected_images = ctk.CTkButton(master=second_section, width=200, height=50, text="Importer", font=front.font16, command=select_images_to_compress)
    btn_selected_images.grid(column=1, row=1, padx=(20, 10), pady=(65, 0))

    btn_compressed_images = ctk.CTkButton(master=second_section, width=200, height=50, text="Compresser", font=front.font16, command=compress_selected_images, state="disabled")
    btn_compressed_images.grid(column=2, row=1, padx=(0, 10), pady=(65, 0))

    btn_reset= ctk.CTkButton(master=second_section, width=50, height=50, text="", command=reset, image=front.rotating_arrow)
    btn_reset.grid(column=3, row=1, pady=(65, 0))

    label_dynamic_number_of_images_to_compress = ctk.CTkLabel(master=second_section, text="", font=front.font14)
    label_dynamic_number_of_images_to_compress.grid(column=1, row=2, pady=(0, 55))

    # Troisième section de l'interface graphique
    third_section = ctk.CTkFrame(master=container, fg_color="transparent")
    third_section.pack(fill="x", padx=10)

    label_dynamic_state_of_compression = ctk.CTkLabel(master=third_section, width=50, text="", font=front.font14)
    label_dynamic_state_of_compression.grid(column=1, row=1, padx=(10, 0))

    label_dynamic_total_weight_before_and_after_compression = ctk.CTkLabel(master=third_section, width=400, text="", font=front.font14, anchor="w")
    label_dynamic_total_weight_before_and_after_compression.grid(column=2, row=1, padx=(130, 0))

    return None
    
# Fenêtre secondaire de l'application.
@config_container
@reset_container
def export_folder_configuration_window() -> None:

        def choose_the_export_directory() -> None:
            """
            Ouvre une boîte de dialogue pour permettre à l'utilisateur de choisir un dossier d'exportation.

            Cette fonction effectue les opérations suivantes :
            1.  Lit le chemin du dossier d'exportation actuel à partir du fichier 'export_directory.json'.
            2.  Ouvre une boîte de dialogue de sélection de dossier.
            3.  Si un dossier est sélectionné (et n'est pas vide), ou si un nouveau dossier est sélectionné même si l'ancien est vide :
                -   Écrit le nouveau chemin du dossier d'exportation dans le fichier 'export_directory.json'.
                -   Met à jour le champ de saisie 'entry_selected_export_folder' avec le nouveau chemin.
            4.  Si aucun dossier n'est sélectionné (et que le dossier courant existe), ne fait rien.
                -   Un commentaire indique l'ajout éventuel d'une ligne de journalisation.

            Returns:
                None: Cette fonction ne retourne rien.
            """
            current_directory = read_data(file="export_directory.json")
            directory = filedialog.askdirectory()

            if (directory != "" and current_directory != "") or directory != "":
                write_data(file="export_directory.json", data=directory)
                entry_selected_export_folder.delete(first_index=0, last_index=len(current_directory))
                entry_selected_export_folder.insert(index=0, string=directory)
            else:
                pass

            return None

        current_directory = read_data(file="export_directory.json")       
        
        # Interface graphique
        label_selected_export_folder = ctk.CTkLabel(master=container, text="Dossier d'export sélectionné", font=front.font16)
        label_selected_export_folder.grid(column=1, row=1, columnspan=2, padx=(40, 0), pady=(90, 10))

        btn_choice_of_directory = ctk.CTkButton(master=container, width=28, text="", image=front.folder, command=choose_the_export_directory)
        btn_choice_of_directory.grid(column=1, row=1, padx=(0, 215), pady=(90, 10))

        entry_selected_export_folder = ctk.CTkEntry(master=container, width=420, font=front.font14)
        entry_selected_export_folder.insert(index=0, string=current_directory)
        entry_selected_export_folder.grid(column=1, row=2, columnspan=2)

        btn_back_to_main_window = ctk.CTkButton(master=container, width=100, text="Retour", command=main_window)
        btn_back_to_main_window.grid(column=1, row=3, padx=(10, 640), pady=(85, 0))

        return None


if __name__ == "__main__":
    # Vérifie si un dossier d'exportation existe, et le crée si nécessaire.
    check_the_existence_of_an_export_directory()
    # Crée une instance de l'application Customtkinter (CTk).
    app = ctk.CTk()
    # Définit le titre de la fenêtre principale.
    app.title("")
    # Définit la taille et la position initiale de la fenêtre.
    app.geometry(f"700x280+0+0")
    # Empêche le redimensionnement de la fenêtre.
    app.resizable(width=False, height=False)
    # Crée un conteneur pour les éléments de l'interface utilisateur.
    container = ctk.CTkFrame(master=app, fg_color="gray14")
    # Place le conteneur dans la fenêtre principale et le fait remplir l'espace disponible.
    container.pack(fill="both", expand=True)
    # Appelle la fonction qui configure le contenu principal de la fenêtre.
    main_window()
    # Lance la boucle principale de l'application Customtkinter pour gérer les événements.
    app.mainloop()