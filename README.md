# **Contrôle du curseur avec des gestes de la main**

## **Description du projet**
Ce projet est une application de présentation document pdf sans interraction physique avec un pc grâce à la vision par ordinateur. Nous utilisons la reconnaissance des gestes de la main via une caméra pour contrôler le curseur d'un ordinateur, défiler des pages, zoomer, et cliquer. L'application présente également des indicateurs visuels des gestes détectés pour l'utilisateur. Le système repose sur OpenCV et la bibliothèque `HandTrackingModule` pour capturer et interpréter les mouvements de la main.

## **Fonctionnalités**
- **Défilement des pages** : Utilise des gestes de la main pour défiler vers le haut ou vers le bas.
- **Zoom** : Effectue des gestes de pincement pour zoomer ou dézoomer.
- **Contrôle du curseur** : Déplace le curseur de la souris avec l'index et clique avec l'index et le majeur levés.
- **Affichage d'une preuve visuelle** : Montre une image indiquant si la main est ouverte ou fermée lors de l'utilisation des gestes.

## **Technologies utilisées**
- **Python** : Langage principal pour implémenter la logique de contrôle de la souris.
- **OpenCV** : Utilisé pour capturer des images de la caméra et reconnaître les gestes de la main.
- **PyAutoGUI** : Pour interagir avec le curseur de l'ordinateur (déplacement et clics).
- **Qt** : Framework pour l'interface utilisateur graphique (GUI).
- **MediaPipe** : Utilisé pour la détection et le suivi des mains.
  
## **Structure du projet**
Le projet est organisé autour des éléments suivants :
1. **HandTrackingModule** : Un module qui détecte la position des mains et les gestes spécifiques.
2. **Process_Gesture Function** : Une fonction gérant le défilement, le zoom et les actions basées sur les gestes, avec un intervalle de capture de 900ms.
3. **Control_Cursor Function** : Fonction séparée pour gérer le déplacement rapide du curseur avec l'index, reliée à un timer de 100ms.
4. **Affichage des gestes** : La détection des gestes affiche des images (main ouverte ou fermée) pendant 2 secondes.

## **Installation**
Pour exécuter ce projet, vous aurez besoin d'installer les dépendances suivantes :

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/username/project-name.git
   ```

2. **Installer les dépendances**
   Utilisez `pip` pour installer les packages nécessaires. Voici les bibliothèques utilisées :
   ```bash
   pip install opencv-python
   pip install PyQt5
   pip install mediapipe
   pip install numpy
   pip install pyautogui
   ```

## **Utilisation**
1. **Lancer l'application**
   Après avoir cloné le dépôt et installé les dépendances, exécutez simplement le fichier principal pour démarrer l'application :
   ```bash
   python main.py
   ```

2. **Utilisation des gestes**
   - **Déplacement du curseur** : Déplacez votre index pour contrôler le curseur en temps réel.
   - **Clic de la souris** : Relevez l'index et le majeur pour effectuer un clic gauche.
   - **Défilement des pages** : Effectuez un geste de la main (poing fermé) pour passer à la page suivante et un autre (poing ouvert) pour passer à la page précédente.
   - **Zoom** : Ne garder que l'index et le pouce debout. Augmenter la distance entre ces deux doigts pour zoomer ou dimunier celle-ci pour dézoomer.
   - **Preuve visuelle** : Un petit aperçu de votre main ouverte ou fermée sera affiché à l'écran pour confirmer le geste détecté.

## **Aperçu**
Voici une vidéo de l'application en fonctionnement :
- Affichage des gestes avec images de main
- Suivi du curseur avec l'index
- Défilement de page avec des gestes simples

![Aperçu 1](./images/screenshot1.jpg)

## **Contributions**
Les contributions sont les bienvenues ! Si vous souhaitez proposer des améliorations ou corriger des bugs, merci de soumettre une *pull request*.

