import os
import subprocess
import tempfile
from django.core.files import File


def compile_latex_to_pdf(latex_code, plan_id):
    """
    Writes LaTeX source to a temp .tex file, compiles it with pdflatex,
    and returns an open Django File object of the resulting PDF.

    Returns:
        (pdf_django_file, pdf_filename) on success
        Raises RuntimeError on compilation failure.
    """
    work_dir = tempfile.mkdtemp()

    tex_filename = f"plan_{plan_id}.tex"
    pdf_filename = f"plan_{plan_id}.pdf"
    tex_path = os.path.join(work_dir, tex_filename)
    pdf_path = os.path.join(work_dir, pdf_filename)

    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    try:
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', work_dir, tex_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
    except subprocess.TimeoutExpired:
        raise RuntimeError('pdflatex timed out after 60 seconds.')
    except FileNotFoundError:
        raise RuntimeError('pdflatex is not installed or not found in PATH.')

    if not os.path.exists(pdf_path):
        raise RuntimeError(
            'pdflatex failed to produce a PDF.\n\nSTDOUT:\n'
            f'{result.stdout}\n\nSTDERR:\n{result.stderr}'
        )

    pdf_file = open(pdf_path, 'rb')
    return File(pdf_file), pdf_filename
