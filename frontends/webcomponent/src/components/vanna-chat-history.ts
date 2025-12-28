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
        display: block;
        width: 100%;
        height: 100%;
        background: var(--vanna-background-higher);
        border-left: 2px solid rgba(225, 230, 238, 1);
        overflow: hidden;
        position: relative;
      }

      .history-header {
        padding: var(--vanna-space-4) var(--vanna-space-5);
        border-bottom: 2px solid rgba(225, 230, 238, 1);
        background: rgb(255, 255, 255);
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: var(--vanna-space-3);
      }

      .history-title {
        font-size: 18px;
        font-weight: 700;
        color: rgb(0, 51, 102);
        margin: 0;
        text-shadow: none;
        letter-spacing: 0.02em;
        flex: 1;
      }

      .new-conversation-button {
        padding: var(--vanna-space-2) var(--vanna-space-4);
        background: rgb(47, 110, 255);
        border: 2px solid rgb(47, 110, 255);
        border-radius: var(--vanna-border-radius-lg);
        color: rgb(255, 255, 255);
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
        white-space: nowrap;
        text-shadow: none;
        box-shadow: 0 2px 8px rgba(47, 110, 255, 0.3);
        display: flex;
        align-items: center;
        gap: var(--vanna-space-2);
      }

      .new-conversation-button:hover {
        background: rgb(0, 212, 255);
        border-color: rgb(0, 212, 255);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
        transform: translateY(-1px);
      }

      .new-conversation-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 6px rgba(47, 110, 255, 0.3);
      }


      .new-conversation-icon {
        width: 16px;
        height: 16px;
        display: inline-block;
      }

      .history-list {
        height: calc(100% - 100px);
        overflow-y: auto;
        padding: var(--vanna-space-2);
      }

      .history-list::-webkit-scrollbar {
        width: 10px;
      }

      .history-list::-webkit-scrollbar-track {
        background: rgba(225, 230, 238, 0.3);
        border-radius: 5px;
        border: 1px solid rgba(225, 230, 238, 0.5);
      }

      .history-list::-webkit-scrollbar-thumb {
        background: rgb(47, 110, 255);
        border-radius: 5px;
        border: 1px solid rgba(47, 110, 255, 0.6);
        box-shadow: 0 0 4px rgba(47, 110, 255, 0.3);
      }

      .history-list::-webkit-scrollbar-thumb:hover {
        background: rgb(0, 212, 255);
        border-color: rgba(0, 212, 255, 0.8);
        box-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
      }

      .conversation-item {
        padding: var(--vanna-space-3) var(--vanna-space-4);
        margin-bottom: var(--vanna-space-2);
        border-radius: var(--vanna-border-radius-lg);
        background: rgba(225, 230, 238, 0.3);
        border: 1px solid rgba(225, 230, 238, 0.5);
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-2);
      }

      .conversation-item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: var(--vanna-space-2);
      }

      .conversation-content {
        flex: 1;
      }

      .conversation-delete-btn {
        padding: var(--vanna-space-2);
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.3) 0%, rgba(185, 28, 28, 0.2) 100%);
        border: 2px solid rgba(220, 38, 38, 0.6);
        border-radius: var(--vanna-border-radius-md);
        color: rgba(255, 255, 255, 1);
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
        opacity: 0;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        box-shadow: 
          0 0 8px rgba(220, 38, 38, 0.4),
          inset 0 0 5px rgba(185, 28, 28, 0.2);
        text-shadow: 0 0 5px rgba(220, 38, 38, 0.6);
      }

      .conversation-item:hover .conversation-delete-btn {
        opacity: 1;
      }

      .conversation-delete-btn:hover {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.5) 0%, rgba(185, 28, 28, 0.4) 100%);
        border-color: rgba(220, 38, 38, 0.9);
        box-shadow: 
          0 0 15px rgba(220, 38, 38, 0.6),
          0 0 25px rgba(185, 28, 28, 0.4),
          inset 0 0 8px rgba(185, 28, 28, 0.3);
        transform: scale(1.15);
      }

      .conversation-delete-btn:active {
        transform: scale(1.0);
        box-shadow: 
          0 0 10px rgba(220, 38, 38, 0.5),
          inset 0 0 5px rgba(185, 28, 28, 0.25);
      }

      .conversation-delete-btn svg {
        width: 18px;
        height: 18px;
        filter: drop-shadow(0 0 3px rgba(220, 38, 38, 0.8));
      }

      .conversation-item:hover {
        background: rgba(229, 241, 255, 0.5);
        border-color: rgba(47, 110, 255, 0.3);
        transform: translateX(-2px);
        box-shadow: 0 2px 8px rgba(47, 110, 255, 0.15);
      }

      .conversation-item.active {
        background: rgba(229, 241, 255, 1);
        border-color: rgb(47, 110, 255);
        border-width: 2px;
        box-shadow: 0 2px 8px rgba(47, 110, 255, 0.2);
        transform: translateX(-4px);
      }

      .conversation-item.active::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: rgb(47, 110, 255);
        box-shadow: 0 0 8px rgba(47, 110, 255, 0.5);
      }

      .conversation-item.active .conversation-title {
        color: rgb(0, 51, 102);
        text-shadow: none;
        font-weight: 700;
      }

      .conversation-item.active .conversation-preview {
        color: rgb(93, 107, 130);
        text-shadow: none;
      }

      .conversation-title {
        font-size: 14px;
        font-weight: 600;
        color: rgb(26, 26, 26);
        margin: 0 0 var(--vanna-space-1) 0;
        text-shadow: none;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .conversation-preview {
        font-size: 12px;
        color: rgb(93, 107, 130);
        margin: 0 0 var(--vanna-space-1) 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.4;
      }

      .conversation-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: rgba(200, 180, 255, 0.6);
        margin-top: var(--vanna-space-1);
      }

      .conversation-time {
        font-weight: 500;
      }

      .conversation-count {
        background: rgba(47, 110, 255, 0.2);
        padding: 2px 6px;
        border-radius: var(--vanna-border-radius-sm);
        font-weight: 600;
      }

      .empty-state {
        padding: var(--vanna-space-8);
        text-align: center;
        color: rgba(200, 180, 255, 0.6);
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
        color: rgba(200, 180, 255, 0.6);
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

  private saveDeletedConversationId(conversationId: string) {
    try {
      const deletedIds = this.getDeletedConversationIds();
      if (!deletedIds.includes(conversationId)) {
        deletedIds.push(conversationId);
        // Keep only last 100 deleted IDs to prevent localStorage from growing too large
        if (deletedIds.length > 100) {
          deletedIds.shift();
        }
        localStorage.setItem('vanna_deleted_conversations', JSON.stringify(deletedIds));
      }
    } catch (error) {
      console.error('Failed to save deleted conversation ID:', error);
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
      const preview = firstUserMessage?.content || 'No messages';
      const title = preview.length > 30 ? preview.substring(0, 30) + '...' : preview;
      
      return {
        id: conv.id,
        title: title,
        preview: preview.length > 60 ? preview.substring(0, 60) + '...' : preview,
        updatedAt: this.formatDate(conv.updated_at || conv.created_at),
        messageCount: conv.messages?.length || 0,
      };
    }).sort((a, b) => {
      // Sort by updatedAt descending
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    });
  }

  private formatDate(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
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

  private async handleDeleteConversation(e: Event, conversationId: string) {
    // Stop event propagation to prevent triggering conversation selection
    e.stopPropagation();
    
    // Confirm before deleting
    if (!confirm('Bạn có chắc chắn muốn xóa cuộc hội thoại này?')) {
      return;
    }

    try {
      // Try to delete from API first (if endpoint exists)
      try {
        const response = await fetch(`${this.apiBase}/api/vanna/v2/conversations/${conversationId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (response.ok) {
          console.log(`Deleted conversation ${conversationId} from API`);
        }
      } catch (error) {
        console.warn('API delete not available, using localStorage only:', error);
      }

      // Save deleted conversation ID to prevent it from reappearing after refresh
      this.saveDeletedConversationId(conversationId);
      
      // Delete from localStorage
      const stored = localStorage.getItem('vanna_conversations');
      if (stored) {
        const conversations = JSON.parse(stored);
        const filtered = conversations.filter((c: any) => c.id !== conversationId);
        localStorage.setItem('vanna_conversations', JSON.stringify(filtered));
      }
      
      // Remove from local state
      this.conversations = this.conversations.filter(c => c.id !== conversationId);
      
      // Dispatch event to notify parent
      this.dispatchEvent(new CustomEvent('conversation-deleted', {
        detail: { conversationId },
        bubbles: true,
        composed: true,
      }));
      
      console.log(`Conversation ${conversationId} deleted successfully`);
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      alert('Không thể xóa cuộc hội thoại. Vui lòng thử lại.');
    }
  }

  render() {
    return html`
      <div class="history-header">
        <h3 class="history-title">Lịch sử chat</h3>
        <button 
          class="new-conversation-button"
          @click=${this.handleNewConversation}
          title="Tạo cuộc hội thoại mới"
        >
          <svg class="new-conversation-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          Mới
        </button>
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
        ` : this.conversations.map((conv) => html`
          <div 
            class="conversation-item ${conv.id === this.currentConversationId ? 'active' : ''}"
            @click=${() => this.handleConversationClick(conv.id)}
          >
            <div class="conversation-item-header">
              <div class="conversation-content">
                <div class="conversation-title">${conv.title}</div>
                <div class="conversation-preview">${conv.preview}</div>
                <div class="conversation-meta">
                  <span class="conversation-time">${conv.updatedAt}</span>
                  <span class="conversation-count">${conv.messageCount}</span>
                </div>
              </div>
              <button
                class="conversation-delete-btn"
                @click=${(e: Event) => this.handleDeleteConversation(e, conv.id)}
                title="Xóa cuộc hội thoại này"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
            </div>
          </div>
        `)}
      </div>
    `;
  }
}

