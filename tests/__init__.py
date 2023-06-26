"""ディレクトリをPythonのパッケージとして識別するための特別なファイル..

NOTE: pathの記述が無いと、importでerrorが発生する
@author: kawanoichi
"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "src"))
