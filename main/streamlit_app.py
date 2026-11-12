import base64
import mimetypes
import re
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Static Web App",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Remove default Streamlit margins and headers for a full-screen view
st.markdown(
    """
    <style>
        #MainMenu, header, footer, [data-testid="stToolbar"] { display: none !important; }
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100vw !important; }
        iframe { display: block; border: none; width: 100vw; height: 100vh; }
    </style>
    """,
    unsafe_allow_html=True
)

def bundle_static_site(entry_html: Path) -> str:
    base_dir = entry_html.parent
    html = entry_html.read_text(encoding="utf-8", errors="ignore")

    # 1. Inline local CSS files (<link rel="stylesheet" href="...">)
    def replace_css(match):
        rel_path = match.group(1).split("?")[0].lstrip("/")
        css_file = (base_dir / rel_path).resolve()
        if css_file.exists() and css_file.is_file():
            css_text = css_file.read_text(encoding="utf-8", errors="ignore")
            return f"<style>\n{css_text}\n</style>"
        return match.group(0)

    html = re.sub(
        r'<link[^>]+href=["\']([^"\']+\.css(?:\?[^"\']*)?)["\'][^>]*>',
        replace_css,
        html,
        flags=re.IGNORECASE
    )

    # 2. Inline local JavaScript files (<script src="..."></script>)
    def replace_js(match):
        rel_path = match.group(1).split("?")[0].lstrip("/")
        js_file = (base_dir / rel_path).resolve()
        if js_file.exists() and js_file.is_file():
            js_text = js_file.read_text(encoding="utf-8", errors="ignore")
            return f"<script>\n{js_text}\n</script>"
        return match.group(0)

    html = re.sub(
        r'<script[^>]+src=["\']([^"\']+\.js(?:\?[^"\']*)?)["\'][^>]*>\s*</script>',
        replace_js,
        html,
        flags=re.IGNORECASE
    )

    # 3. Convert local image references (<img src="...">) to Base64 data URIs
    def replace_img(match):
        prefix, rel_path, suffix = match.group(1), match.group(2), match.group(3)
        if rel_path.startswith(("http://", "https://", "data:")):
            return match.group(0)
        clean_path = rel_path.split("?")[0].lstrip("/")
        img_file = (base_dir / clean_path).resolve()
        if img_file.exists() and img_file.is_file():
            mime_type, _ = mimetypes.guess_type(img_file)
            mime_type = mime_type or "image/png"
            b64_data = base64.b64encode(img_file.read_bytes()).decode("utf-8")
            return f'{prefix}data:{mime_type};base64,{b64_data}{suffix}'
        return match.group(0)

    html = re.sub(
        r'(<img[^>]+src=["\'])([^"\']+)(["\'][^>]*>)',
        replace_img,
        html,
        flags=re.IGNORECASE
    )

    return html

# Locate index.html in the root directory or one subfolder deep
root_dir = Path(__file__).parent
html_candidates = [root_dir / "index.html"] + list(root_dir.glob("*/index.html"))
target_html = next((p for p in html_candidates if p.exists()), None)

if target_html:
    bundled_html = bundle_static_site(target_html)
    components.html(bundled_html, height=950, scrolling=True)
else:
    st.error("Could not find index.html in the repository root or immediate subfolders.")
