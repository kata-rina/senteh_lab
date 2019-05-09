from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('PyQt5.QtGui')
datas = collect_data_files('PyQt5.QtGui')
