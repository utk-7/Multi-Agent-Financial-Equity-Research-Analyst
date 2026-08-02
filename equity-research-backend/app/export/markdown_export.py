import os
import re
from jinja2 import Environment, FileSystemLoader

def export_to_markdown(state: dict, output_path: str):
    """
    Renders the HTML template and converts it to a basic Markdown equivalent,
    or just writes a Markdown structure directly.
    Since we use a shared HTML template, we can write a simple HTML-to-MD converter
    or just use the same Jinja template logic but for MD.
    However, the user asked to render from ONE shared HTML template. 
    So we will render the HTML and use a lightweight conversion or just save it.
    Actually, Markdown supports HTML natively! We can just save the rendered HTML 
    as a .md file and Markdown viewers will render it perfectly.
    """
    template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report.html')
    
    html_out = template.render(state=state)
    
    # Very basic HTML to Markdown for the text parts if we want pure markdown, 
    # but since MD accepts HTML, we can just save it. Let's strip the head/body tags for cleaner MD.
    body_content = re.search(r'<body>(.*?)</body>', html_out, re.DOTALL | re.IGNORECASE)
    if body_content:
        md_content = body_content.group(1).strip()
    else:
        md_content = html_out
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
