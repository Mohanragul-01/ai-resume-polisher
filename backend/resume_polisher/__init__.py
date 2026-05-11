# This file marks this folder as a Python package.
# It also exposes the create_app function so other files can import it easily.
from resume_polisher.factory import create_app


# __all__ controls what gets exported when someone does: from resume_polisher import *
__all__ = ["create_app"]
