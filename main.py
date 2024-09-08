import sys
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QLabel, QGridLayout, QLineEdit, QPushButton, QMainWindow,
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox,
    QToolBar, QStatusBar, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon


# Database connection class
class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


# Main application window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(600, 500)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        # Set up the main UI components
        self.create_menus()
        self.create_table_widget()
        self.create_toolbar()
        self.create_statusbar()

    def create_menus(self):
        # Create and populate the menu bar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Create actions
        self.add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        self.search_action = QAction(QIcon("icons/search.png"), "Search", self)
        about_action = QAction("About", self)

        # Add actions to menus
        file_menu_item.addAction(self.add_student_action)
        edit_menu_item.addAction(self.search_action)
        help_menu_item.addAction(about_action)

        # Connect menu actions
        self.add_student_action.triggered.connect(self.insert)
        self.search_action.triggered.connect(self.search)
        about_action.triggered.connect(self.about)

    def create_table_widget(self):
        # Set up the main table widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def create_toolbar(self):
        # Create and populate the toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        # Add actions to the toolbar
        toolbar.addAction(self.add_student_action)
        toolbar.addAction(self.search_action)

    def create_statusbar(self):
        # Create the status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def setup_connections(self):
        # Connect signals to slots
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        # Handle cell click event
        edit_button = QPushButton("Edit Record")
        delete_button = QPushButton("Delete Record")

        edit_button.clicked.connect(self.edit)
        delete_button.clicked.connect(self.delete)

        # Clear existing buttons from the status bar
        for child in self.findChildren(QPushButton):
            self.statusbar.removeWidget(child)

        # Add new buttons to the status bar
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        # Load data from the database into the table
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")

        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    # CRUD Operations
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            dialog = EditDialog(
                self.table.item(selected_row, 0).text(),  # ID
                self.table.item(selected_row, 1).text(),  # Name
                self.table.item(selected_row, 2).text(),  # Course
                self.table.item(selected_row, 3).text()  # Mobile
            )
            dialog.exec()
        else:
            QMessageBox.information(self, "Edit Record", "Please select a record to edit.")

    def delete(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            dialog = DeleteDialog(self.table.item(selected_row, 0).text())  # ID
            dialog.exec()
        else:
            QMessageBox.information(self, "Delete Record", "Please select a record to delete.")

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


# Dialog classes for various operations
class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        A simple and intuitive app for managing student records. Easily add, search, edit, 
        and delete student information with a clean and user-friendly interface.
        """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self, student_id, name, course, mobile):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        self.student_id = student_id

        self.setup_ui(name, course, mobile)

    def setup_ui(self, name, course, mobile):
        layout = QVBoxLayout()

        # Edit student name
        self.student_name = QLineEdit(name)
        layout.addWidget(self.student_name)

        # Edit course
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course)
        layout.addWidget(self.course_name)

        # Edit mobile number
        self.mobile = QLineEdit(mobile)
        layout.addWidget(self.mobile)

        # Save button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        # Update student information in the database
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (name, course, mobile, self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self, student_id):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(150)
        self.student_id = student_id

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Confirm delete message
        label = QLabel(f"Are you sure you want to delete student ID {self.student_id}?")
        layout.addWidget(label)

        # Confirm and cancel buttons
        button_layout = QGridLayout()
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.delete_student)
        button_layout.addWidget(confirm_button, 0, 0)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button, 0, 1)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def delete_student(self):
        # Delete student record from the database
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (self.student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()
        self.close()
        QMessageBox.information(self, "Success", "The record was deleted successfully.")


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        # Insert new student record into the database
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()
        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Create input widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create search button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        # Search for a student in the database
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)

        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()

        if not rows:
            QMessageBox.information(self, "Search Result", "No matching student found.")

        self.close()


# Main entry point of the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.load_data()
    sys.exit(app.exec())