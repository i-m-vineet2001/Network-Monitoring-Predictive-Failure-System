# #!/usr/bin/env python3
# # run_gui.py — start the GUI (login + monitor window) without starting monitor thread
# import sys
# import os

# # ensure project root and src are on path
# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, ROOT_DIR)  # → gives access to gui/
# sys.path.insert(0, os.path.join(ROOT_DIR, "src"))  # → gives access to other src modules

# from PySide6.QtWidgets import QApplication
# from gui.login_window import LoginWindow


# def main():
#     app = QApplication(sys.argv)

#     login = LoginWindow()
#     login.show()

#     sys.exit(app.exec())


# if __name__ == "__main__":
#     main()
