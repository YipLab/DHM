import multiprocessing as mp
import easygui as esg
import time
import os
# from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QFileDialog, QApplication)

# def info(title):
#     print(title)
#     print('module name:', __name__)
#     print('parent process:', os.getppid())
#     print('process id:', os.getpid())

# def f(name):
#     info('function f')
#     time.sleep(1)
#     print('function f' + str(time.time()))
#     time.sleep(1)
#     print('hello', name)

# if __name__ == '__main__':
#     info('main line')
#     p = mp.Process(target=f, args=('bob',))
#     p.start()
#     time.sleep(1)
#     print('main line'+ str(time.time()))
#     time.sleep(3)
#     p.join()

# def foo(q):
#     q.put('hello')

# def selectFile(self):
#         if self.fname is not None and os.path.isfile(self.fname):
#             eeg_cap_dir = os.path.dirname(self.fname)
#         else:
#             eeg_cap_dir = QtCore.QDir.currentPath()
#         dialog = QtWidgets.QFileDialog(self)
#         dialog.setWindowTitle('Select the background image')
#         dialog.setNameFilter('(*.tiff)')
#         dialog.setDirectory(eeg_cap_dir)
#         dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
#         filename = None
#         if dialog.exec_() == QtWidgets.QDialog.Accepted:
#             filename = dialog.selectedFiles()
#         if filename:
#             self.fname = str(filename[0])
#             self.group_box.lineEdit.setText(self.fname)

if __name__ == '__main__':
    # mp.set_start_method('spawn')
    # q = mp.Queue()
    # p = mp.Process(target=foo, args=(q,))
    # p.start()
    # print(q.get())
    # p.join()

    # box = esg.fileopenbox(msg=None, title="Select the background image", \
    #     default="../../Example Images/ref.tiff", filetypes="*.tiff", multiple=False)
    # print(box)
    path = esg.diropenbox(msg=None, title="Select the background image", \
        default="../../Example Images/ref.tiff")
    print(path)
    f = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f.extend(filenames)
        break
    print(f)

