from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QLabel, QGridLayout, QLineEdit, QPushButton, QMainWindow, QTableWidget,
                             QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox)
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(600, 500)

        # Creating Menu Items
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Adding Actions to Menu Items
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # Setting Up the Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")

        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            dialog = EditDialog(self.table.item(selected_row, 0).text(),  # ID
                                self.table.item(selected_row, 1).text(),  # Name
                                self.table.item(selected_row, 2).text(),  # Course
                                self.table.item(selected_row, 3).text())  # Mobile
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


class InsertDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

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
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input widget
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)

        if rows:
            items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
            for item in items:
                main_window.table.item(item.row(), 1).setSelected(True)
        else:
            QMessageBox.information(self, "Search Result", "No matching student found.")

        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self, student_id, name, course, mobile):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        self.student_id = student_id

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
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?", (name, course, mobile, self.student_id))
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

        layout = QVBoxLayout()

        # Confirm delete message
        label = QLabel(f"Are you sure you want to delete student ID {student_id}?")
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
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (self.student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()
        QMessageBox.information(self, "Success", "The record was deleted successfully.")


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())


