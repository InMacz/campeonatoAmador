# Gera o Relatorio_Campeonato_Amador.pdf a partir do relatorio.html usando o Chrome instalado.
# uso: pip install playwright  ->  python gerar_pdf.py
from pathlib import Path
from playwright.sync_api import sync_playwright

pasta = Path(__file__).resolve().parent
rodape = """
<div style="font-family:'Segoe UI',Arial;font-size:8px;color:#8c959f;width:100%;padding:0 20mm;display:flex;justify-content:space-between">
  <span>Campeonato Amador — Relatório do projeto</span>
  <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>"""

with sync_playwright() as pw:
    navegador = pw.chromium.launch(channel="chrome")
    pagina = navegador.new_page()
    pagina.goto((pasta / "relatorio.html").as_uri())
    pagina.wait_for_load_state("networkidle")
    pagina.pdf(
        path=str(pasta / "Relatorio_Campeonato_Amador.pdf"),
        format="A4",
        print_background=True,
        prefer_css_page_size=True,
        display_header_footer=True,
        header_template="<span></span>",
        footer_template=rodape,
    )
    navegador.close()
print("PDF gerado em", pasta / "Relatorio_Campeonato_Amador.pdf")
