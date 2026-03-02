"streamlit run web/__main__.py"
import os
import sys
sys.path.append(os.environ.get("PACKAGE_ROOT", os.getcwd()))

from web import main

main()
