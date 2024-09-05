import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QScrollArea,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtGui import QPixmap, QWheelEvent
from PySide6.QtCore import Qt, QTimer
from pdf2image import convert_from_path
import os
import cv2
import numpy as np
import cvzone
import time
from cvzone.HandTrackingModule import HandDetector
import pyautogui  # Pour contrôler le curseur de la souris

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer")

        # Définir une taille minimale pour la fenêtre
        self.setMinimumSize(800, 600)

        # Appliquer le style général
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                border: 2px solid #ccc;
                padding: 5px;
                border-radius: 5px;
            }
            QScrollArea {
                background-color: #ffffff;
                border: 1px solid #ccc;
            }
            QLabel#headerLabel {
                background-color: #333;
                color: white;
                padding: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QLabel#logoLabel {
                background-color: #f0f0f0;
                padding: 20px;
            }
        """)

        # Layout principal
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # En-tête personnalisé
        self.header_label = QLabel("PDF Viewer")
        self.header_label.setObjectName("headerLabel")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header_label)

        # Zone de défilement pour le défilement vertical et horizontal
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.layout.addWidget(self.scroll_area)

        # Widget pour afficher le contenu PDF
        self.pdf_container = QWidget()
        self.pdf_layout = QVBoxLayout()
        self.pdf_container.setLayout(self.pdf_layout)
        self.scroll_area.setWidget(self.pdf_container)

        # Ajouter un QLabel pour le logo PDF
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName("logoLabel")
        self.logo_pixmap = QPixmap("logo.png")  # Assurez-vous que le fichier 'logo.png' est disponible et spécifié le chemin d'accès
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.pdf_layout.addWidget(self.logo_label)

        # Layout pour les boutons
        self.button_layout = QHBoxLayout()

        # Bouton pour charger un PDF
        self.load_pdf_button = QPushButton("Charger PDF")
        self.load_pdf_button.clicked.connect(self.load_pdf)

        # Boutons de navigation
        self.previous_page_button = QPushButton("Précédent")
        self.previous_page_button.clicked.connect(self.go_to_previous_page)
        self.previous_page_button.setEnabled(False)

        self.next_page_button = QPushButton("Suivant")
        self.next_page_button.clicked.connect(self.go_to_next_page)
        self.next_page_button.setEnabled(False)

        # Barre de recherche pour aller à une page spécifique
        self.page_number_input = QLineEdit("1")
        self.page_number_input.setMaxLength(4)  # Pour éviter des nombres trop grands
        self.page_number_input.returnPressed.connect(self.go_to_page)
        self.page_number_input.setAlignment(Qt.AlignCenter)

        # Boutons de zoom
        self.zoom_in_button = QPushButton("Zoom +")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setEnabled(False)

        self.zoom_out_button = QPushButton("Zoom -")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_out_button.setEnabled(False)

        # Ajouter les boutons au layout
        self.button_layout.addWidget(self.load_pdf_button)
        self.button_layout.addWidget(self.previous_page_button)
        self.button_layout.addWidget(self.page_number_input)
        self.button_layout.addWidget(self.next_page_button)
        self.button_layout.addWidget(self.zoom_in_button)
        self.button_layout.addWidget(self.zoom_out_button)
        self.layout.addLayout(self.button_layout)

        # Liste des images/pages
        self.pages = []
        self.current_page_index = -1  # Index de la page actuelle
        self.zoom_factor = 1.0  # Facteur de zoom initial

        # Afficher le logo initialement
        self.show_logo()

        # Initialiser la capture vidéo et le détecteur de main
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
        self.last_gesture_time = 0

        # Configurer un timer pour capturer des images de la webcam
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_gestures)
        self.timer.start(900)  # Capturer une image toutes les 900 ms pour les gestes

        # Configurer un second timer pour contrôler le curseur
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.control_cursor)
        self.cursor_timer.start(100)  # Capturer une image toutes les 100 ms pour le contrôle du curseur

        # Charger les images de main
        self.open_hand_label = QLabel(self)
        self.closed_hand_label = QLabel(self)
        self.open_hand_label.setPixmap(QPixmap("open_hand.jpg").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)) #Assurez-vous que le fichier 'open_hand.jpg' est disponible et spécifié le chemin d'accès
        self.closed_hand_label.setPixmap(QPixmap("closed_hand.jpg").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Assurez-vous que le fichier 'closed_hand.jpg' est disponible et spécifié le chemin d'accès
        self.layout.addWidget(self.open_hand_label, alignment=Qt.AlignTop | Qt.AlignRight)
        self.layout.addWidget(self.closed_hand_label, alignment=Qt.AlignTop | Qt.AlignRight)
        self.open_hand_label.setVisible(False)
        self.closed_hand_label.setVisible(False)

    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un PDF", "", "PDF Files (*.pdf)"
        )

        if file_path:
            try:
                self.pages = convert_from_path(
                    file_path, poppler_path=os.getenv("POPLER_BIN_PATH")
                )

                # Effacer le contenu précédent
                for i in reversed(range(self.pdf_layout.count())):
                    self.pdf_layout.itemAt(i).widget().deleteLater()

                # Réinitialiser le facteur de zoom
                self.zoom_factor = 1.0

                # Charger la première page par défaut
                self.go_to_page(1)
                
                # Activer/désactiver les boutons de navigation et de zoom
                self.update_navigation_buttons()
                
                # Informer de la réussite du chargement
                QMessageBox.information(self, "Chargement réussi", "PDF chargé avec succès.")

            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur de chargement", f"Une erreur s'est produite lors du chargement du PDF: {e}"
                )

    def go_to_page(self, page_number=None):
        # Aller à une page spécifique
        if page_number is None:
            page_number = int(self.page_number_input.text())

        if 1 <= page_number <= len(self.pages):
            self.current_page_index = page_number - 1
            self.show_current_page()
            self.update_navigation_buttons()  # Mettre à jour les boutons de navigation
        else:
            QMessageBox.warning(
                self, "Page invalide", "Le numéro de page est hors limites."
            )

    def show_current_page(self):
        # Effacer le contenu précédent
        for i in reversed(range(self.pdf_layout.count())):
            self.pdf_layout.itemAt(i).widget().deleteLater()

        current_page = self.pages[self.current_page_index]
        pixmap = QPixmap.fromImage(current_page.toqimage())
        pixmap = pixmap.scaledToWidth(self.width() * self.zoom_factor - 20, Qt.SmoothTransformation)

        label = QLabel()
        label.setPixmap(pixmap)
        label.setScaledContents(True)

        self.pdf_layout.addWidget(label, alignment=Qt.AlignCenter)

        # Cacher le logo lorsque le PDF est chargé
        self.logo_label.hide()

    def show_logo(self):
        self.logo_label.setPixmap(self.logo_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.show()

    def go_to_next_page(self):
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self.show_current_page()
            self.update_navigation_buttons()

    def go_to_previous_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.show_current_page()
            self.update_navigation_buttons()

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.show_current_page()

    def zoom_out(self):
        if self.zoom_factor > 0.2:
            self.zoom_factor -= 0.1
            self.show_current_page()

    def update_navigation_buttons(self):
        # Activer/désactiver les boutons en fonction de la position de la page
        self.previous_page_button.setEnabled(self.current_page_index > 0)
        self.next_page_button.setEnabled(self.current_page_index < len(self.pages) - 1)
        self.zoom_in_button.setEnabled(True)
        self.zoom_out_button.setEnabled(self.zoom_factor > 0.2)

    def process_gestures(self):
        success, img = self.cap.read()
        if not success:
            return

        hands, img = self.detector.findHands(img, draw=True, flipType=True)

        if hands:
            for hand in hands:
                lmList = hand["lmList"]
                fingers = self.detector.fingersUp(hand)

                pouce_x, pouce_y = lmList[4][0], lmList[4][1]
                index_x, index_y = lmList[8][0], lmList[8][1]

                distance = ((pouce_x - index_x)**2 + (pouce_y - index_y)**2)**0.5

                current_time = time.time()

                if fingers == [1, 1, 0, 0, 0]:
                    if distance < 50:
                        self.zoom_out()
                        self.last_gesture_time = current_time
                        #self.show_hand_image('closed')
                    elif distance > 100:
                        self.zoom_in()
                        self.last_gesture_time = current_time
                        #self.show_hand_image('open')

                if fingers == [1, 1, 1, 1, 1]:
                    self.show_hand_image('open')
                    self.go_to_previous_page()

                if fingers == [0, 0, 0, 0, 0]:
                    self.show_hand_image('closed')
                    self.go_to_next_page()
              

    def control_cursor(self):
        success, img = self.cap.read()
        if not success:
            return

        hands, img = self.detector.findHands(img, draw=True, flipType=True)

        if hands:
            for hand in hands:
                lmList = hand["lmList"]
                fingers = self.detector.fingersUp(hand)

                index_x, index_y = lmList[8][0], lmList[8][1]

                # Contrôler le curseur avec l'index
                screen_width, screen_height = pyautogui.size() 
                cursor_x = np.interp(index_x, [0, img.shape[1]], [screen_width, 0])
                cursor_y = np.interp(index_y, [0, img.shape[0]], [0, screen_height])
                pyautogui.moveTo(cursor_x, cursor_y)

                # Vérifier si l'index et le majeur sont levés pour cliquer
                if fingers == [0, 1, 1, 0, 0]:
                    pyautogui.click()
        cv2.imshow("Image", img)  
        cv2.waitkey(1)           

    def show_hand_image(self, gesture):
        if gesture == 'open':
            self.open_hand_label.setVisible(True)
            self.closed_hand_label.setVisible(False)
        elif gesture == 'closed':
            self.closed_hand_label.setVisible(True)
            self.open_hand_label.setVisible(False)

        # Masquer les images après un certain temps
        QTimer.singleShot(500, self.hide_hand_images)

    def hide_hand_images(self):
        self.open_hand_label.setVisible(False)
        self.closed_hand_label.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec())
