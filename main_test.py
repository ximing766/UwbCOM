import sys
 
from PyQt5.QtWidgets import QApplication, QMainWindow
 
import Ui_test #刚刚生成的py文件
 
if __name__ =="__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    
    ui = Ui_test.Ui_MainWindow()
    ui.setupUi(MainWindow)
 
    MainWindow.show()
    sys.exit(app.exec_())