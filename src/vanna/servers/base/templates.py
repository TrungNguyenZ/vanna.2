"""
HTML templates for Vanna Agents servers.
"""

from typing import Optional


def get_vanna_component_script(
    dev_mode: bool = False,
    static_path: str = "/static",
    cdn_url: str = "https://img.vanna.ai/vanna-components.js",
) -> str:
    """Get the script tag for loading Vanna web components.

    Args:
        dev_mode: If True, load from local static files
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production

    Returns:
        HTML script tag for loading components
    """
    if dev_mode:
        return (
            f'<script type="module" src="{static_path}/vanna-components.js"></script>'
        )
    else:
        return f'<script type="module" src="{cdn_url}"></script>'


def get_index_html(
    dev_mode: bool = False,
    static_path: str = "/static",
    cdn_url: str = "https://img.vanna.ai/vanna-components.js",
    api_base_url: str = "",
) -> str:
    """Generate index HTML with configurable component loading.

    Args:
        dev_mode: If True, load components from local static files
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production components
        api_base_url: Base URL for API endpoints

    Returns:
        Complete HTML page as string
    """
    component_script = get_vanna_component_script(dev_mode, static_path, cdn_url)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Data Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-3.1.1.min.js"></script>
    <script>
        window.FontAwesomeConfig = {{ autoReplaceSvg: 'nest' }};
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        navy: {{
                            DEFAULT: '#003366',
                            dark: '#0F172A',
                            light: '#162033'
                        }},
                        azure: {{
                            DEFAULT: '#2F6EFF',
                            light: '#E5F1FF',
                            hover: '#00D4FF'
                        }},
                        soft: {{
                            green: '#47C97E',
                            orange: '#FFB86B',
                            red: '#FF6B6B',
                            gray: '#F7F9FB',
                            border: '#E1E6EE',
                            text: '#5D6B82'
                        }}
                    }},
                    fontFamily: {{
                        sans: ['Inter', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    }},
                    boxShadow: {{
                        'soft': '0 4px 20px rgba(0, 0, 0, 0.03)',
                        'card': '0 2px 8px rgba(0, 0, 0, 0.04)',
                    }}
                }}
            }}
        }}
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #F7F9FB; color: #1A1A1A; }}
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #D7DEE6; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #9AA6B8; }}
        .glass-effect {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }}
        .typing-dot {{ animation: typing 1.4s infinite ease-in-out both; }}
        .typing-dot:nth-child(1) {{ animation-delay: -0.32s; }}
        .typing-dot:nth-child(2) {{ animation-delay: -0.16s; }}
        @keyframes typing {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
        
        /* Hide default vanna-chat styling and integrate into layout */
        vanna-chat {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: transparent;
            border: none;
            box-shadow: none;
        }}
        
        /* Override vanna-chat internal styles to match new design */
        vanna-chat::part(header) {{
            display: none !important;
        }}
    </style>
    {component_script}
</head>
<body class="h-screen flex flex-col overflow-hidden">

    <!-- Header -->
    <header id="header" class="h-16 bg-gradient-to-r from-navy to-[#004080] flex items-center justify-between px-6 shadow-md z-20 shrink-0">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-white backdrop-blur-sm border border-white/20">
                <i class="fa-solid fa-database text-sm"></i>
            </div>
            <h1 class="text-white font-semibold text-lg tracking-tight">AI Data Assistant</h1>
        </div>
        <div class="flex items-center gap-4">
            <div class="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full border border-white/10 backdrop-blur-md">
                <span class="w-2 h-2 rounded-full bg-soft-green shadow-[0_0_8px_rgba(71,201,126,0.6)]" id="statusIndicator"></span>
                <span class="text-xs text-white/90 font-medium" id="statusText">Connected</span>
            </div>
            <button class="w-8 h-8 rounded-full flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 transition-colors" id="settingsButton">
                <i class="fa-solid fa-gear"></i>
            </button>
            <button class="w-8 h-8 rounded-full flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 transition-colors" id="logoutButtonHeader">
                <i class="fa-solid fa-arrow-right-from-bracket"></i>
            </button>
        </div>
    </header>

    <!-- Login Form (shown by default) -->
    <div id="loginContainer" class="flex-1 flex items-center justify-center p-6">
        <div class="max-w-md w-full bg-white rounded-xl shadow-soft border border-soft-border p-8">
            <div class="text-center mb-6">
                <h2 class="text-2xl font-semibold text-gray-900 mb-2">Login to Continue</h2>
                <p class="text-sm text-soft-text">Select your email to access the chat</p>
            </div>
            <div class="mb-5">
                <label for="emailInput" class="block mb-2 text-sm font-medium text-gray-700">Email Address</label>
                <select id="emailInput" class="w-full px-4 py-3 text-sm border border-soft-border rounded-lg focus:outline-none focus:ring-2 focus:ring-azure focus:border-transparent bg-white">
                    <option value="">Select an email...</option>
                    <option value="admin@example.com">admin@example.com</option>
                    <option value="user@example.com">user@example.com</option>
                </select>
            </div>
            <button id="loginButton" class="w-full px-4 py-3 bg-navy text-white text-sm font-medium rounded-lg hover:bg-azure transition disabled:bg-gray-400 disabled:cursor-not-allowed">
                Continue
            </button>
            <div class="mt-5 p-3 bg-azure-light border-l-4 border-azure rounded text-xs text-gray-700 leading-relaxed">
                <strong>Demo Mode:</strong> This is a frontend-only authentication demo. Your email will be stored as a cookie.
            </div>
        </div>
    </div>

    <!-- Main Layout (hidden by default) -->
    <div id="mainLayout" class="flex flex-1 overflow-hidden hidden">
        
        <!-- Main Content Area -->
        <main id="main-content" class="flex-1 flex flex-col relative min-w-0">
            
            <!-- Scrollable Content -->
            <div class="flex-1 overflow-y-auto p-6 space-y-6">
                
                <!-- System Status Card -->
                <div id="system-status-card" class="bg-white rounded-xl shadow-soft border border-soft-border p-5">
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-full bg-soft-green/10 flex items-center justify-center text-soft-green">
                                <i class="fa-solid fa-check-circle text-xl"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-semibold text-gray-900">System Ready</h2>
                                <p class="text-sm text-soft-text">All data pipelines are active and synchronized.</p>
                            </div>
                        </div>
                        <span class="px-3 py-1 bg-soft-green/10 text-soft-green text-xs font-semibold rounded-full border border-soft-green/20" id="userRoleBadge">USER VIEW</span>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div class="flex items-center gap-2 p-3 bg-soft-gray rounded-lg border border-soft-border">
                            <i class="fa-solid fa-database text-azure text-sm"></i>
                            <span class="text-sm font-medium text-gray-700">SQL Engine</span>
                            <i class="fa-solid fa-check text-soft-green ml-auto text-xs"></i>
                        </div>
                        <div class="flex items-center gap-2 p-3 bg-soft-gray rounded-lg border border-soft-border">
                            <i class="fa-solid fa-brain text-azure text-sm"></i>
                            <span class="text-sm font-medium text-gray-700">Memory Context</span>
                            <i class="fa-solid fa-check text-soft-green ml-auto text-xs"></i>
                        </div>
                        <div class="flex items-center gap-2 p-3 bg-soft-gray rounded-lg border border-soft-border">
                            <i class="fa-solid fa-chart-pie text-azure text-sm"></i>
                            <span class="text-sm font-medium text-gray-700">Visualization</span>
                            <i class="fa-solid fa-check text-soft-green ml-auto text-xs"></i>
                        </div>
                    </div>

                    <div class="flex gap-3 pt-2 border-t border-soft-border">
                        <button class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-soft-text hover:text-azure hover:bg-azure-light rounded-lg transition-colors">
                            <i class="fa-regular fa-lightbulb"></i> Help Guide
                        </button>
                        <button class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-soft-text hover:text-azure hover:bg-azure-light rounded-lg transition-colors">
                            <i class="fa-solid fa-layer-group"></i> View Memories
                        </button>
                    </div>
                </div>

                <!-- Chat Container -->
                <div class="bg-white rounded-xl shadow-card border border-soft-border overflow-hidden" style="min-height: 500px;">
                    <vanna-chat
                        api-base="{api_base_url}"
                        sse-endpoint="{api_base_url}/api/vanna/v2/chat_sse"
                        ws-endpoint="{api_base_url}/api/vanna/v2/chat_websocket"
                        poll-endpoint="{api_base_url}/api/vanna/v2/chat_poll"
                        style="height: 100%; display: flex; flex-direction: column;">
                    </vanna-chat>
                </div>
            </div>
        </main>

        <!-- Right Sidebar (Tasks/History) -->
        <aside id="right-sidebar" class="w-80 bg-white border-l border-soft-border hidden xl:flex flex-col">
            <div class="p-5 border-b border-soft-border">
                <h3 class="font-semibold text-gray-800">Session History</h3>
            </div>
            
            <div class="flex-1 overflow-y-auto p-4 space-y-3" id="historyContainer">
                <!-- History items will be populated by JavaScript -->
            </div>

            <div class="p-4 border-t border-soft-border bg-soft-gray/30">
                <button class="w-full py-2.5 rounded-lg border border-soft-border bg-white text-sm font-medium text-soft-text hover:text-navy hover:border-navy hover:shadow-sm transition-all flex items-center justify-center gap-2">
                    <i class="fa-solid fa-plus"></i> New Session
                </button>
            </div>
        </aside>

    </div>

    <script>
        // Cookie helpers
        const getCookie = (name) => {{
            const value = `; ${{document.cookie}}`;
            const parts = value.split(`; ${{name}}=`);
            return parts.length === 2 ? parts.pop().split(';').shift() : null;
        }};

        const setCookie = (name, value) => {{
            const expires = new Date(Date.now() + 365 * 864e5).toUTCString();
            document.cookie = `${{name}}=${{value}}; expires=${{expires}}; path=/; SameSite=Lax`;
        }};

        const deleteCookie = (name) => {{
            document.cookie = `${{name}}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }};

        // Login/Logout functionality
        document.addEventListener('DOMContentLoaded', () => {{
            const email = getCookie('vanna_email');
            const loginContainer = document.getElementById('loginContainer');
            const mainLayout = document.getElementById('mainLayout');
            const loginButton = document.getElementById('loginButton');
            const emailInput = document.getElementById('emailInput');
            const logoutButtonHeader = document.getElementById('logoutButtonHeader');
            const userRoleBadge = document.getElementById('userRoleBadge');

            // Check if already logged in
            if (email) {{
                loginContainer.classList.add('hidden');
                mainLayout.classList.remove('hidden');
                updateUserRole(email);
            }}

            // Login button
            if (loginButton) {{
                loginButton.addEventListener('click', () => {{
                    const email = emailInput.value.trim();
                    if (!email) {{
                        alert('Please select an email address');
                        return;
                    }}
                    setCookie('vanna_email', email);
                    loginContainer.classList.add('hidden');
                    mainLayout.classList.remove('hidden');
                    updateUserRole(email);
                }});
            }}

            // Logout button in header
            if (logoutButtonHeader) {{
                logoutButtonHeader.addEventListener('click', () => {{
                    deleteCookie('vanna_email');
                    loginContainer.classList.remove('hidden');
                    mainLayout.classList.add('hidden');
                    if (emailInput) emailInput.value = '';
                }});
            }}

            // Enter key
            if (emailInput) {{
                emailInput.addEventListener('keypress', (e) => {{
                    if (e.key === 'Enter' && loginButton) loginButton.click();
                }});
            }}

            function updateUserRole(email) {{
                if (userRoleBadge) {{
                    if (email === 'admin@example.com') {{
                        userRoleBadge.textContent = 'ADMIN VIEW';
                        userRoleBadge.className = 'px-3 py-1 bg-soft-green/10 text-soft-green text-xs font-semibold rounded-full border border-soft-green/20';
                    }} else {{
                        userRoleBadge.textContent = 'USER VIEW';
                        userRoleBadge.className = 'px-3 py-1 bg-azure-light text-azure text-xs font-semibold rounded-full border border-azure/20';
                    }}
                }}
            }}

            // Settings button
            const settingsButton = document.getElementById('settingsButton');
            if (settingsButton) {{
                settingsButton.addEventListener('click', () => {{
                    alert('Settings feature coming soon!');
                }});
            }}
        }});

        // Artifact demo event listener
        document.addEventListener('DOMContentLoaded', () => {{
            const vannaChat = document.querySelector('vanna-chat');

            if (vannaChat) {{
                // Add artifact event listener to demonstrate external rendering
                vannaChat.addEventListener('artifact-opened', (event) => {{
                    const {{ artifactId, type, title, trigger }} = event.detail;
                    console.log('Artifact Event:', {{ artifactId, type, title, trigger }});
                }});
            }}
        }});

        // Fallback if web component doesn't load
        if (!customElements.get('vanna-chat')) {{
            setTimeout(() => {{
                const vannaChat = document.querySelector('vanna-chat');
                if (vannaChat && !customElements.get('vanna-chat')) {{
                    vannaChat.innerHTML = `
                        <div class="p-10 text-center text-gray-600">
                            <h3 class="text-xl font-semibold mb-2">Vanna Chat Component</h3>
                            <p class="mb-2">Web component failed to load. Please check your connection.</p>
                            <p class="text-sm text-gray-400">
                                {("Loading from: local static assets" if dev_mode else f"Loading from: {cdn_url}")}
                            </p>
                        </div>
                    `;
                }}
            }}, 2000);
        }}
    </script>
</body>
</html>"""


# Backward compatibility - default production HTML
INDEX_HTML = get_index_html()
