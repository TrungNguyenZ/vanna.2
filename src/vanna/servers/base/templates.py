"""
HTML templates for Vanna Agents servers.
"""

from typing import Optional


def get_vanna_component_script(
    dev_mode: bool = True,
    static_path: str = "/static",
    cdn_url: str = "/static/vanna-components.js",
) -> str:
    """Get the script tag for loading Vanna web components.

    Args:
        dev_mode: If True, load from local static files (default: True)
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production (default: local path)

    Returns:
        HTML script tag for loading components
    """
    import os
    from pathlib import Path
    
    # Add cache-busting timestamp in dev mode
    cache_bust = ""
    if dev_mode:
        # Try to get file modification time for cache busting
        possible_paths = [
            Path(static_path.lstrip("/")) / "vanna-components.js",
            Path("frontends/webcomponent/dist/vanna-components.js"),
            Path(__file__).parent.parent.parent.parent / "frontends" / "webcomponent" / "dist" / "vanna-components.js",
        ]
        
        for file_path in possible_paths:
            if file_path.exists():
                try:
                    mtime = int(file_path.stat().st_mtime)
                    cache_bust = f"?v={mtime}"
                    break
                except:
                    pass
    
    if dev_mode:
        return (
            f'<script type="module" src="{static_path}/vanna-components.js{cache_bust}"></script>'
        )
    else:
        return f'<script type="module" src="{cdn_url}"></script>'


def get_index_html(
    dev_mode: bool = True,
    static_path: str = "/static",
    cdn_url: str = "/static/vanna-components.js",
    api_base_url: str = "",
) -> str:
    """Generate minimal HTML with vanna-chat component.

    Args:
        dev_mode: If True, load components from local static files (default: True)
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production components (default: local path)
        api_base_url: Base URL for API endpoints

    Returns:
        Minimal HTML page with vanna-chat component
    """
    component_script = get_vanna_component_script(dev_mode, static_path, cdn_url)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vanna Agents Chat</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }}
        vanna-chat {{
            width: 100%;
            height: 100%;
            display: block;
        }}
    </style>
    {component_script}
</head>
<body>
    <vanna-chat
        api-base="{api_base_url}"
        sse-endpoint="{api_base_url}/api/vanna/v2/chat_sse"
        ws-endpoint="{api_base_url}/api/vanna/v2/chat_websocket"
        poll-endpoint="{api_base_url}/api/vanna/v2/chat_poll">
    </vanna-chat>
</body>
</html>"""


# Backward compatibility - default production HTML
INDEX_HTML = get_index_html()
