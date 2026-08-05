import logging
import os

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


def export_to_pdf(state: dict, output_path: str):
    """
    Renders the HTML template with the graph state and exports to PDF using WeasyPrint.
    Catches missing GTK3 dependencies on Windows gracefully.
    """
    template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.html")

    html_out = template.render(state=state)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        import weasyprint

        weasyprint.HTML(string=html_out).write_pdf(output_path)
        logger.info(f"Successfully exported PDF to {output_path}")
    except (ImportError, OSError) as e:
        logger.warning(
            f"Failed to generate PDF due to missing WeasyPrint/GTK3 dependencies. Skipping PDF generation. Error: {e}"
        )
        # Save HTML instead as a fallback
        fallback_path = output_path.replace(".pdf", ".html")
        with open(fallback_path, "w", encoding="utf-8") as f:
            f.write(html_out)
        logger.info(f"Saved HTML fallback to {fallback_path}")
