# Blitzit_App/widgets/reporting_dialog.py
from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame # <--- QWidget ADDED HERE
from PyQt6.QtGui import QFont

class ReportingDialog(QDialog):
    """A dialog to display productivity statistics."""
    def __init__(self, report_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Your Productivity Report")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        
        # --- Key Stats Section ---
        stats_layout = QGridLayout()
        
        total_done_label = self.create_stat_label(f"{report_data['total_done']}", "Tasks Completed")
        total_pending_label = self.create_stat_label(f"{report_data['total_pending']}", "Tasks Pending")

        stats_layout.addWidget(total_done_label, 0, 0)
        stats_layout.addWidget(total_pending_label, 0, 1)

        layout.addLayout(stats_layout)
        
        # --- Trend Section ---
        trend_frame = QFrame()
        trend_frame.setFrameShape(QFrame.Shape.StyledPanel)
        trend_layout = QVBoxLayout(trend_frame)
        
        trend_title = QLabel("Completion Trend (Last 7 Days)")
        title_font = QFont(); title_font.setBold(True); title_font.setPointSize(12)
        trend_title.setFont(title_font)
        trend_layout.addWidget(trend_title)

        if report_data['completion_trend']:
            for row in report_data['completion_trend']:
                date = row['completion_day']
                count = row['count']
                trend_layout.addWidget(QLabel(f"{date}: {'■' * count} ({count})"))
        else:
            trend_layout.addWidget(QLabel("No tasks completed in the last 7 days."))

        layout.addWidget(trend_frame)

    def create_stat_label(self, value, description):
        """Helper to create a formatted label for a key statistic."""
        widget = QWidget() # This line will now work correctly
        layout = QVBoxLayout(widget)
        
        value_label = QLabel(value)
        value_font = QFont(); value_font.setPointSize(24); value_font.setBold(True)
        value_label.setFont(value_font)

        desc_label = QLabel(description)
        
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        
        return widget