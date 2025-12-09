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
    """Generate index HTML with custom UI.

    Args:
        dev_mode: If True, load components from local static files
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production components
        api_base_url: Base URL for API endpoints

    Returns:
        Complete HTML page as string
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Data Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-3.1.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
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
    </style>
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
                <span class="w-2 h-2 rounded-full bg-soft-green shadow-[0_0_8px_rgba(71,201,126,0.6)]"></span>
                <span class="text-xs text-white/90 font-medium">Connected</span>
            </div>
            <button class="w-8 h-8 rounded-full flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 transition-colors">
                <i class="fa-solid fa-gear"></i>
            </button>
            <button class="w-8 h-8 rounded-full flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 transition-colors">
                <i class="fa-solid fa-arrow-right-from-bracket"></i>
            </button>
        </div>
    </header>

    <!-- Main Layout -->
    <div class="flex flex-1 overflow-hidden">
        
        <!-- Main Content Area -->
        <main id="main-content" class="flex-1 flex flex-col relative min-w-0">
            
            <!-- Scrollable Content -->
            <div class="flex-1 overflow-y-auto p-6 space-y-6" id="scroll-container">
                
                <!-- System Status Card -->
                <div id="system-status-card" class="bg-white rounded-xl shadow-soft border border-soft-border p-5 animate-fade-in-up">
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
                        <span class="px-3 py-1 bg-soft-green/10 text-soft-green text-xs font-semibold rounded-full border border-soft-green/20">ADMIN VIEW</span>
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

                <!-- Chat Interaction Area -->
                <div id="chat-stream" class="space-y-6 pb-4">
                    <!-- Messages will be injected here -->
                </div>
            </div>

            <!-- Bottom Input Section -->
            <div class="p-6 bg-white/80 backdrop-blur-md border-t border-soft-border z-10 sticky bottom-0">
                <div class="max-w-4xl mx-auto space-y-3">
                    
                    <!-- Status Indicator -->
                    <div class="flex items-center justify-between px-1">
                        <div class="flex items-center gap-2">
                             <div class="w-2 h-2 rounded-full bg-soft-green animate-pulse"></div>
                             <span class="text-xs font-semibold text-soft-text uppercase tracking-wide">Assistant Ready</span>
                        </div>
                        <span class="text-xs text-gray-400">Press Enter to send, Shift+Enter for new line</span>
                    </div>

                    <!-- Input Box -->
                    <div class="relative group">
                        <div class="absolute inset-0 bg-gradient-to-r from-azure to-purple-400 rounded-xl opacity-0 group-focus-within:opacity-20 transition-opacity duration-300 -m-[2px]"></div>
                        <div class="relative flex items-center bg-white border border-soft-border rounded-xl shadow-sm focus-within:shadow-md focus-within:border-azure transition-all overflow-hidden">
                            <input type="text" 
                                id="user-input"
                                placeholder="Ask a question about your data..." 
                                class="w-full h-14 pl-5 pr-14 text-gray-800 placeholder-gray-400 bg-transparent focus:outline-none text-[15px]"
                            >
                            <button id="send-button" class="absolute right-2 w-10 h-10 rounded-lg bg-navy hover:bg-azure text-white flex items-center justify-center transition-all transform active:scale-95 shadow-md">
                                <i class="fa-solid fa-paper-plane text-sm"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Right Sidebar (Tasks/History) -->
        <aside id="right-sidebar" class="w-80 bg-white border-l border-soft-border hidden xl:flex flex-col">
            <div class="p-5 border-b border-soft-border">
                <h3 class="font-semibold text-gray-800">Session History</h3>
            </div>
            
            <div class="flex-1 overflow-y-auto p-4 space-y-3" id="history-container">
                <!-- History items -->
            </div>

            <div class="p-4 border-t border-soft-border bg-soft-gray/30">
                <button class="w-full py-2.5 rounded-lg border border-soft-border bg-white text-sm font-medium text-soft-text hover:text-navy hover:border-navy hover:shadow-sm transition-all flex items-center justify-center gap-2">
                    <i class="fa-solid fa-plus"></i> New Session
                </button>
            </div>
        </aside>

    </div>

    <script>
        const API_BASE_URL = "{api_base_url}";
        const chatStream = document.getElementById('chat-stream');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');
        const scrollContainer = document.getElementById('scroll-container');

        function scrollToBottom() {{
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }}

        function appendUserMessage(text) {{
            const div = document.createElement('div');
            div.className = 'flex justify-end gap-3 group animate-fade-in-up';
            div.innerHTML = `
                <div class="max-w-2xl">
                    <div class="bg-white border border-soft-border rounded-2xl rounded-tr-sm p-4 shadow-sm">
                        <p class="text-[15px] text-gray-800 leading-relaxed">${{text}}</p>
                    </div>
                    <div class="flex justify-end mt-1 pr-1">
                        <span class="text-xs text-gray-400">Just now</span>
                    </div>
                </div>
                <div class="w-8 h-8 rounded-full bg-navy text-white flex items-center justify-center shrink-0 shadow-sm mt-auto mb-6">
                    <i class="fa-solid fa-user text-xs"></i>
                </div>
            `;
            chatStream.appendChild(div);
            scrollToBottom();
        }}

        function createAIMessageContainer() {{
            const id = 'msg-' + Date.now();
            const div = document.createElement('div');
            div.className = 'flex gap-4 animate-fade-in-up';
            div.innerHTML = `
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-azure to-[#00D4FF] flex items-center justify-center shrink-0 shadow-md mt-1">
                    <i class="fa-solid fa-robot text-white text-sm"></i>
                </div>
                <div class="flex-1 max-w-3xl space-y-4" id="${{id}}">
                    <!-- Content will be appended here -->
                </div>
            `;
            chatStream.appendChild(div);
            return id;
        }}

        function appendTextToContainer(containerId, text) {{
            const container = document.getElementById(containerId);
            // Check if last element is a text block
            let textBlock = container.querySelector('.text-response-block:last-child');
            
            if (!textBlock) {{
                textBlock = document.createElement('div');
                textBlock.className = 'bg-azure-light border border-azure/20 rounded-2xl rounded-tl-sm p-5 shadow-sm text-response-block';
                textBlock.innerHTML = '<p class="text-[15px] text-gray-800 leading-relaxed markdown-body"></p>';
                container.appendChild(textBlock);
            }}
            
            const p = textBlock.querySelector('p');
            // Simple markdown parsing using marked.js
            p.innerHTML = marked.parse(text);
            scrollToBottom();
        }}

        function appendSQLToContainer(containerId, sql) {{
            const container = document.getElementById(containerId);
            const div = document.createElement('div');
            div.className = 'bg-white border border-soft-border rounded-xl shadow-sm overflow-hidden group mt-4';
            div.innerHTML = `
                <div class="bg-soft-gray px-4 py-2 border-b border-soft-border flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <i class="fa-solid fa-code text-azure text-xs"></i>
                        <span class="text-xs font-semibold text-soft-text uppercase tracking-wider">Generated SQL</span>
                    </div>
                    <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button class="text-gray-400 hover:text-azure transition-colors" onclick="navigator.clipboard.writeText(this.parentElement.parentElement.nextElementSibling.innerText)"><i class="fa-regular fa-copy"></i></button>
                    </div>
                </div>
                <div class="p-4 relative">
                    <div class="absolute left-0 top-0 bottom-0 w-1 bg-azure"></div>
                    <pre class="font-mono text-sm text-gray-700 overflow-x-auto"><code>${{sql}}</code></pre>
                </div>
            `;
            container.appendChild(div);
            scrollToBottom();
        }}

        function appendChartToContainer(containerId, plotData) {{
            const container = document.getElementById(containerId);
            const div = document.createElement('div');
            div.className = 'bg-white border border-soft-border rounded-xl shadow-card p-1 mt-4';
            const chartId = 'chart-' + Date.now();
            div.innerHTML = `
                <div class="p-4 flex items-center justify-between border-b border-soft-border border-dashed">
                     <h3 class="text-sm font-semibold text-gray-800">Visualization</h3>
                </div>
                <div id="${{chartId}}" class="h-[300px] w-full"></div>
            `;
            container.appendChild(div);
            
            try {{
                // plotData is already an object if passed from rich component data
                Plotly.newPlot(chartId, plotData.data, plotData.layout);
            }} catch (e) {{
                console.error('Error plotting chart:', e);
            }}
            scrollToBottom();
        }}

        function appendTableToContainer(containerId, tableData) {{
            const container = document.getElementById(containerId);
            const div = document.createElement('div');
            div.className = 'bg-white border border-soft-border rounded-xl shadow-sm overflow-hidden group mt-4 overflow-x-auto';
            
            // Basic table structure
            let html = `
                <div class="bg-soft-gray px-4 py-2 border-b border-soft-border flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <i class="fa-solid fa-table text-azure text-xs"></i>
                        <span class="text-xs font-semibold text-soft-text uppercase tracking-wider">Data Result</span>
                    </div>
                </div>
                <div class="p-0">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-gray-50 border-b border-soft-border">
            `;
            
            // Headers
            if (tableData.columns) {{
                tableData.columns.forEach(col => {{
                    html += `<th class="px-4 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">${{col}}</th>`;
                }});
            }}
            
            html += `       </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
            `;
            
            // Rows
            if (tableData.data) {{
                tableData.data.forEach(row => {{
                    html += `<tr class="hover:bg-gray-50/50 transition-colors">`;
                    tableData.columns.forEach(col => {{
                        const cellData = row[col] !== undefined ? row[col] : '';
                        html += `<td class="px-4 py-2.5 text-sm text-gray-700 whitespace-nowrap">${{cellData}}</td>`;
                    }});
                    html += `</tr>`;
                }});
            }}
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
            
            div.innerHTML = html;
            container.appendChild(div);
            scrollToBottom();
        }}

        async function sendMessage() {{
            const text = userInput.value.trim();
            if (!text) return;

            userInput.value = '';
            appendUserMessage(text);
            
            const containerId = createAIMessageContainer();
            
            try {{
                const response = await fetch(`${{API_BASE_URL}}/api/vanna/v2/chat_sse`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        message: text
                    }})
                }});

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {{
                    const {{ value, done }} = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, {{ stream: true }});
                    buffer += chunk;
                    
                    const lines = buffer.split('\\n\\n');
                    buffer = lines.pop(); // Keep the last partial line
                    
                    for (const line of lines) {{
                        if (line.startsWith('data: ')) {{
                            const dataStr = line.slice(6);
                            if (dataStr === '[DONE]') continue;
                            
                            try {{
                                const chunk = JSON.parse(dataStr);
                                console.log('Received chunk:', chunk);

                                if (chunk.rich) {{
                                    const component = chunk.rich;
                                    const type = component.type;
                                    const data = component.data;

                                    if (type === 'text') {{
                                        if (data && data.content) {{
                                            appendTextToContainer(containerId, data.content);
                                        }}
                                    }} else if (type === 'code_block' || (type === 'text' && data.code_language === 'sql')) {{
                                        if (data && data.content) {{
                                            if (data.code_language === 'sql') {{
                                                 appendSQLToContainer(containerId, data.content);
                                            }} else {{
                                                 appendTextToContainer(containerId, data.content);
                                            }}
                                        }}
                                    }} else if (type === 'chart' || type === 'plotly') {{
                                        if (data) {{
                                            appendChartToContainer(containerId, data);
                                        }}
                                    }} else if (type === 'dataframe' || type === 'table') {{
                                        if (data && data.data && data.columns) {{
                                            appendTableToContainer(containerId, data);
                                        }}
                                    }}
                                }} else if (chunk.type === 'error') {{
                                     appendTextToContainer(containerId, `Error: ${{chunk.data.message}}`);
                                }}
                            }} catch (e) {{
                                console.error('Error parsing SSE data:', e);
                            }}
                        }}
                    }}
                }}
            }} catch (e) {{
                console.error('Error sending message:', e);
                appendTextToContainer(containerId, 'Error: Could not connect to the server.');
            }}
        }}

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') sendMessage();
        }});

    </script>
</body>
</html>"""


# Backward compatibility - default production HTML
INDEX_HTML = get_index_html()
