import shutil
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    pdflatex_available = shutil.which('pdflatex') is not None
    return Response({
        'status': 'ok',
        'pdflatex': 'available' if pdflatex_available else 'NOT FOUND — run: sudo apt install texlive-latex-extra',
        'database': 'SQLite',
    })
