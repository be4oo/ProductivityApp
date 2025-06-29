# Blitzit_App/widgets/celebration_widget.py
import os
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QPauseAnimation, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QMovie

class CelebrationWidget(QWidget):
    """A widget that shows a random celebratory GIF and fades in and out."""
    animation_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie(self)
        self.gif_label.setMovie(self.movie)
        layout.addWidget(self.gif_label)

        self.gif_folder = "assets/gifs"
        self.gif_files = [f for f in os.listdir(self.gif_folder) if f.endswith('.gif')] if os.path.exists(self.gif_folder) else []
        
        self.setWindowOpacity(0.0)
        
        self.fade_in = QPropertyAnimation(self, b"windowOpacity"); self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0); self.fade_in.setEndValue(1.0)
        self.fade_out = QPropertyAnimation(self, b"windowOpacity"); self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0); self.fade_out.setEndValue(0.0)
        self.animation_group = QSequentialAnimationGroup(self)
        self.animation_group.addAnimation(self.fade_in)
        self.animation_group.addAnimation(QPauseAnimation(2500))
        self.animation_group.addAnimation(self.fade_out)
        self.animation_group.finished.connect(self.on_finish)

    def show_celebration(self):
        """Picks a random GIF, resizes the widget to fit, and starts the animation."""
        if not self.gif_files:
            self.animation_finished.emit(); return
            
        random_gif = random.choice(self.gif_files)
        self.movie.setFileName(os.path.join(self.gif_folder, random_gif))
        
        # --- THIS IS THE FIX ---
        # Wait for the movie to load the first frame to get its size
        self.movie.jumpToFrame(0)
        gif_size = self.movie.currentPixmap().size()
        if not gif_size.isEmpty():
            self.setFixedSize(gif_size)
            self.gif_label.setFixedSize(gif_size)
        else: # Fallback size
            self.setFixedSize(QSize(256, 256))
            self.gif_label.setFixedSize(QSize(256, 256))
        
        self.movie.start()
        
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(parent_rect.center() - self.rect().center())
        
        self.show(); self.raise_(); self.animation_group.start()
        
    def on_finish(self):
        self.movie.stop(); self.hide(); self.animation_finished.emit()