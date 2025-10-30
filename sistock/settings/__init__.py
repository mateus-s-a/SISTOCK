import os
from .base import *


# Determina o ambiente baseado na variável ENV
ENV = os.environ.get('ENV', 'development').lower()

if ENV == 'production':
    from .production import *
elif ENV == 'development':
    from .development import *
else:
    # Fallback para development se ENV não for reconhecida
    from .development import *


try:
    from .local import *
except ImportError:
    pass
