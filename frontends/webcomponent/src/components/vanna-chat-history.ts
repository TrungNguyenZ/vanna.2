import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { vannaDesignTokens } from '../styles/vanna-design-tokens.js';

interface ConversationItem {
  id: string;
  title: string;
  preview: string;
  updatedAt: string;
  messageCount: number;
}

@customElement('vanna-chat-history')
export class VannaChatHistory extends LitElement {
  static styles = [
    vannaDesignTokens,
    css`
      :host {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        background: var(--vanna-background-default);
        border-left: 1px solid var(--vanna-outline-default);
        overflow: hidden;
        position: relative;
        min-height: 0;
        max-height: 100%;
      }

      .history-header {
        padding: var(--vanna-space-5);
        border-bottom: 1px solid var(--vanna-outline-default);
        background: var(--vanna-background-default);
        flex-shrink: 0;
      }

      .history-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--vanna-foreground-default);
        margin: 0;
      }

      .new-conversation-button {
        display: none;
      }


      .new-conversation-icon {
        width: 16px;
        height: 16px;
        display: inline-block;
      }

      .history-list {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: var(--vanna-space-4);
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-3);
        min-height: 0;
        max-height: 100%;
        position: relative;
      }

      .history-list::-webkit-scrollbar {
        width: 10px;
        display: block;
      }

      .history-list::-webkit-scrollbar-track {
        background: rgba(225, 230, 238, 0.3);
        border-radius: 5px;
        border: 1px solid rgba(225, 230, 238, 0.5);
        margin: 4px 0;
      }

      .history-list::-webkit-scrollbar-thumb {
        background: rgb(47, 110, 255);
        border-radius: 5px;
        border: 1px solid rgba(47, 110, 255, 0.6);
        box-shadow: 0 0 4px rgba(47, 110, 255, 0.3);
        min-height: 20px;
      }

      .history-list::-webkit-scrollbar-thumb:hover {
        background: rgb(0, 212, 255);
        border-color: rgba(0, 212, 255, 0.8);
        box-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
      }

      /* Firefox scrollbar */
      .history-list {
        scrollbar-width: thin;
        scrollbar-color: rgb(47, 110, 255) rgba(225, 230, 238, 0.3);
      }

      .conversation-item {
        padding: var(--vanna-space-3);
        border-radius: var(--vanna-border-radius-xl);
        background: var(--vanna-background-default);
        border: 1px solid var(--vanna-outline-default);
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
        position: relative;
        display: flex;
        flex-direction: column;
        min-height: auto;
      }

      .conversation-item:hover {
        border-color: rgba(47, 110, 255, 0.5);
        box-shadow: var(--vanna-shadow-md);
      }

      .conversation-item.active {
        background: rgba(229, 241, 255, 0.5);
        border: 1px solid rgba(47, 110, 255, 0.3);
        box-shadow: var(--vanna-shadow-md);
      }

      .conversation-item.active .conversation-query-number {
        color: var(--vanna-accent-primary-default);
      }

      .conversation-item.active .conversation-preview {
        color: var(--vanna-foreground-default);
      }

      .conversation-query-number {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--vanna-accent-primary-default);
      }

      .conversation-item:not(.active) .conversation-query-number {
        color: var(--vanna-foreground-dimmest);
      }

      .conversation-item:hover:not(.active) .conversation-query-number {
        color: var(--vanna-accent-primary-default);
      }

      .conversation-preview {
        font-size: 14px;
        font-weight: 500;
        color: var(--vanna-foreground-default);
        margin: 0;
        margin-bottom: var(--vanna-space-2);
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 2.8em;
      }

      .conversation-item:not(.active) .conversation-preview {
        color: var(--vanna-foreground-dimmer);
      }

      .conversation-item:hover:not(.active) .conversation-preview {
        color: var(--vanna-foreground-default);
      }

      .conversation-meta {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: var(--vanna-space-1);
      }

      .conversation-time {
        font-size: 10px;
        color: var(--vanna-foreground-dimmest);
      }

      .conversation-badges {
        display: flex;
        gap: var(--vanna-space-2);
      }

      .conversation-badge {
        font-size: 10px;
        padding: 2px 6px;
        background: var(--vanna-background-default);
        border: 1px solid rgba(47, 110, 255, 0.2);
        border-radius: 4px;
        color: var(--vanna-accent-primary-default);
      }

      .history-footer {
        padding: var(--vanna-space-4);
        border-top: 1px solid var(--vanna-outline-default);
        background: rgba(247, 249, 251, 0.3);
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
      }

      .new-session-button {
        width: 100%;
        padding: 10px;
        border-radius: var(--vanna-border-radius-lg);
        border: 1px solid var(--vanna-outline-default);
        background: var(--vanna-background-default);
        color: var(--vanna-foreground-dimmer);
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--vanna-space-2);
        text-transform: none;
        letter-spacing: normal;
      }

      .new-session-button:hover {
        color: var(--vanna-navy);
        border-color: var(--vanna-navy);
        box-shadow: var(--vanna-shadow-sm);
      }

      .new-session-icon {
        width: 12px;
        height: 12px;
        display: inline-block;
        flex-shrink: 0;
      }

      .empty-state {
        padding: var(--vanna-space-8);
        text-align: center;
        color: var(--vanna-foreground-dimmer);
      }

      .empty-state-icon {
        font-size: 48px;
        margin-bottom: var(--vanna-space-4);
        opacity: 0.5;
      }

      .empty-state-text {
        font-size: 14px;
        font-weight: 500;
      }

      .loading {
        padding: var(--vanna-space-4);
        text-align: center;
        color: var(--vanna-foreground-dimmer);
        font-size: 14px;
      }
    `
  ];

  @property({ type: String }) apiBase = '';
  @property({ type: String }) currentConversationId = '';
  @state() private conversations: ConversationItem[] = [];
  @state() private loading = false;
  @state() private error: string | null = null;

  connectedCallback() {
    super.connectedCallback();
    this.loadConversations();
  }

  async loadConversations() {
    this.loading = true;
    this.error = null;
    
    try {
      // Get deleted conversation IDs from localStorage
      const deletedIds = this.getDeletedConversationIds();
      
      // Try to fetch conversations from API
      const response = await fetch(`${this.apiBase}/api/vanna/v2/conversations`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const apiConversations = data.conversations || [];
        
        // Filter out deleted conversations
        const filtered = apiConversations.filter((c: any) => !deletedIds.includes(c.id));
        
        // Merge with localStorage (localStorage takes priority for deleted items)
        const localConversations = this.getLocalStorageConversations();
        
        // Combine: API conversations (excluding deleted) + localStorage conversations not in API
        const combined = [
          ...filtered,
          ...localConversations.filter((c: any) => 
            !deletedIds.includes(c.id) && !apiConversations.some((ac: any) => ac.id === c.id)
          )
        ];
        
        // Update localStorage to sync with filtered API data
        localStorage.setItem('vanna_conversations', JSON.stringify(combined));
        
        this.conversations = this.formatConversations(combined);
      } else {
        // If API not available, use localStorage as fallback
        this.loadFromLocalStorage();
      }
    } catch (error) {
      console.warn('Failed to load conversations from API, using localStorage:', error);
      this.loadFromLocalStorage();
    } finally {
      this.loading = false;
    }
  }

  private getDeletedConversationIds(): string[] {
    try {
      const stored = localStorage.getItem('vanna_deleted_conversations');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to get deleted conversation IDs:', error);
      return [];
    }
  }


  private getLocalStorageConversations(): any[] {
    try {
      const stored = localStorage.getItem('vanna_conversations');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to get localStorage conversations:', error);
      return [];
    }
  }

  private loadFromLocalStorage() {
    try {
      const stored = localStorage.getItem('vanna_conversations');
      if (stored) {
        const data = JSON.parse(stored);
        this.conversations = this.formatConversations(data);
      }
    } catch (error) {
      console.error('Failed to load conversations from localStorage:', error);
      this.error = 'Failed to load conversation history';
    }
  }

  private formatConversations(convs: any[]): ConversationItem[] {
    return convs.map((conv) => {
      const firstUserMessage = conv.messages?.find((m: any) => m.role === 'user');
      const preview = firstUserMessage?.content || conv.title || 'No messages';
      const title = preview.length > 30 ? preview.substring(0, 30) + '...' : preview;
      
      // Keep ISO date string for updatedAt, use current date if invalid
      const dateStr = conv.updated_at || conv.created_at;
      let updatedAt = dateStr;
      if (!dateStr || isNaN(new Date(dateStr).getTime())) {
        updatedAt = new Date().toISOString();
      }
      
      return {
        id: conv.id,
        title: title,
        preview: preview.length > 60 ? preview.substring(0, 60) + '...' : preview,
        updatedAt: updatedAt,
        messageCount: conv.messages?.length || 0,
      };
    }).sort((a, b) => {
      // Sort by updatedAt descending, handle invalid dates
      const dateA = new Date(a.updatedAt).getTime();
      const dateB = new Date(b.updatedAt).getTime();
      if (isNaN(dateA) && isNaN(dateB)) return 0;
      if (isNaN(dateA)) return 1;
      if (isNaN(dateB)) return -1;
      return dateB - dateA;
    });
  }

  private handleConversationClick(conversationId: string) {
    this.dispatchEvent(new CustomEvent('conversation-selected', {
      detail: { conversationId },
      bubbles: true,
      composed: true,
    }));
  }

  private handleNewConversation() {
    this.dispatchEvent(new CustomEvent('new-conversation', {
      detail: {},
      bubbles: true,
      composed: true,
    }));
  }

  render() {
    return html`
      <div class="history-header">
        <h3 class="history-title">Session History</h3>
      </div>
      <div class="history-list">
        ${this.loading ? html`
          <div class="loading">Đang tải...</div>
        ` : this.error ? html`
          <div class="empty-state">
            <div class="empty-state-text">${this.error}</div>
          </div>
        ` : this.conversations.length === 0 ? html`
          <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-text">Chưa có cuộc hội thoại nào</div>
          </div>
        ` : this.conversations.map((conv, index) => {
          const queryNumber = this.conversations.length - index;
          // Check if conversation has SQL or Chart based on preview or message content
          const previewText = (conv.preview || conv.title || '').toLowerCase();
          const hasSQL = previewText.includes('sql') || previewText.includes('query') || previewText.includes('select');
          const hasChart = previewText.includes('chart') || previewText.includes('visualization') || previewText.includes('graph');
          return html`
            <div 
              class="conversation-item ${conv.id === this.currentConversationId ? 'active' : ''}"
              @click=${() => this.handleConversationClick(conv.id)}
            >
              <div class="conversation-meta">
                <span class="conversation-query-number">Query #${queryNumber}</span>
                <span class="conversation-time">${this.formatTime(conv.updatedAt)}</span>
              </div>
              <p class="conversation-preview">${conv.preview || conv.title || 'No preview'}</p>
              ${hasSQL || hasChart ? html`
                <div class="conversation-badges">
                  ${hasSQL ? html`<span class="conversation-badge">SQL</span>` : ''}
                  ${hasChart ? html`<span class="conversation-badge">Chart</span>` : ''}
                </div>
              ` : ''}
            </div>
          `;
        })}
      </div>
      <div class="history-footer">
        <button 
          class="new-session-button"
          @click=${this.handleNewConversation}
        >
          <svg class="new-session-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          <span>New Session</span>
        </button>
      </div>
    `;
  }

  private formatTime(dateString: string): string {
    if (!dateString) return 'Just now';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Just now';
    
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  }
}

