import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { vannaDesignTokens } from '../styles/vanna-design-tokens.js';

@customElement('vanna-message')
export class VannaMessage extends LitElement {
  static styles = [
    vannaDesignTokens,
    css`
      :host {
        display: block;
        padding: 0 var(--vanna-space-2);
        margin-bottom: var(--vanna-space-4);
        font-family: var(--vanna-font-family-default);
        animation: fade-in-up 0.25s ease-out;
      }

      :host(:last-of-type) {
        margin-bottom: 0;
      }

      @keyframes fade-in-up {
        from {
          opacity: 0;
          transform: translateY(16px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .message {
        position: relative;
        padding: var(--vanna-space-5) var(--vanna-space-6);
        border-radius: 18px;
        word-wrap: break-word;
        line-height: 1.6;
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-3);
        max-width: min(85%, 600px);
        transition: all var(--vanna-duration-300) cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        box-sizing: border-box;
      }

      .message.assistant {
        background: linear-gradient(135deg, rgba(229, 241, 255, 0.95) 0%, rgba(240, 247, 255, 0.9) 100%);
        border: 1.5px solid rgba(47, 110, 255, 0.25);
        color: rgb(15, 23, 42);
        box-shadow: 
          0 2px 8px rgba(47, 110, 255, 0.1),
          0 1px 3px rgba(0, 0, 0, 0.05);
        border-radius: 18px 18px 18px 4px;
      }

      .message.user {
        margin-left: auto;
        max-width: min(80%, 550px);
        background: linear-gradient(135deg, rgb(47, 110, 255) 0%, rgb(59, 130, 246) 100%);
        color: rgb(255, 255, 255);
        box-shadow: 
          0 4px 12px rgba(47, 110, 255, 0.3),
          0 2px 4px rgba(47, 110, 255, 0.2);
        border-radius: 18px 18px 4px 18px;
        border: 1px solid rgba(255, 255, 255, 0.2);
      }

      .message:hover {
        transform: translateY(-2px);
      }

      .message.assistant:hover {
        background: linear-gradient(135deg, rgba(229, 241, 255, 1) 0%, rgba(240, 247, 255, 0.95) 100%);
        box-shadow: 
          0 6px 16px rgba(47, 110, 255, 0.15),
          0 2px 6px rgba(0, 0, 0, 0.08);
        border-color: rgba(47, 110, 255, 0.4);
      }

      .message.user:hover {
        box-shadow: 
          0 6px 20px rgba(47, 110, 255, 0.4),
          0 3px 8px rgba(47, 110, 255, 0.3);
        background: linear-gradient(135deg, rgb(59, 130, 246) 0%, rgb(37, 99, 235) 100%);
      }

      .message-content {
        margin: 0;
        font-size: 15px;
        letter-spacing: 0.01em;
        white-space: pre-wrap;
        font-weight: 400;
        line-height: 1.75;
        word-break: break-word;
      }
      
      .message.assistant .message-content {
        color: rgb(15, 23, 42);
      }
      
      .message.user .message-content {
        color: rgb(255, 255, 255);
        font-weight: 400;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
      }

      .message-content a {
        color: rgb(47, 110, 255);
        font-weight: 500;
        text-decoration: underline;
        text-decoration-thickness: 1px;
        text-underline-offset: 2px;
        opacity: 1;
      }
      
      .message.assistant .message-content a {
        color: rgb(47, 110, 255);
      }
      
      .message.assistant .message-content a:hover {
        color: rgb(0, 212, 255);
      }

      .message-content code {
        font-family: var(--vanna-font-family-mono);
        background: rgba(255, 255, 255, 0.9);
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 13px;
        border: 1px solid rgba(47, 110, 255, 0.25);
        color: rgb(15, 23, 42);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
      }
      
      .message.assistant .message-content code {
        background: rgba(255, 255, 255, 1);
        border-color: rgba(47, 110, 255, 0.35);
        color: rgb(15, 23, 42);
      }

      .message.user .message-content code {
        background: rgba(255, 255, 255, 0.25);
        border-color: rgba(255, 255, 255, 0.4);
        color: rgba(255, 255, 255, 0.95);
      }

      .message-timestamp {
        display: inline-flex;
        align-items: center;
        gap: var(--vanna-space-2);
        font-size: 11px;
        letter-spacing: 0.03em;
        margin-top: var(--vanna-space-1);
        font-family: var(--vanna-font-family-default);
        opacity: 0.65;
        font-weight: 500;
        transition: opacity var(--vanna-duration-200) ease;
      }
      
      .message:hover .message-timestamp {
        opacity: 0.85;
      }

      .message-timestamp::before {
        content: '';
        width: 4px;
        height: 4px;
        border-radius: var(--vanna-border-radius-full);
        background: currentColor;
        opacity: 0.7;
        flex-shrink: 0;
      }

      .message.assistant .message-timestamp {
        align-self: flex-start;
        color: rgb(100, 116, 139);
        opacity: 0.7;
      }

      .message.assistant .message-timestamp::before {
        background: rgb(47, 110, 255);
        opacity: 0.6;
      }

      .message.user .message-timestamp {
        align-self: flex-end;
        color: rgba(255, 255, 255, 0.85);
      }

      .message.user .message-timestamp::before {
        background: rgba(255, 255, 255, 0.85);
        opacity: 0.7;
      }

      :host([theme="dark"]) .message.assistant {
        background: #ffffff;
        border: 1.5px solid rgba(255, 255, 255, 0.1);
        color: rgb(15, 23, 42);
        box-shadow: 
          0 2px 8px rgba(0, 0, 0, 0.2),
          0 1px 3px rgba(0, 0, 0, 0.15);
      }
      
      :host([theme="dark"]) .message.assistant .message-content {
        color: rgb(15, 23, 42);
      }
      
      :host([theme="dark"]) .message.assistant:hover {
        background: #ffffff;
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 
          0 4px 12px rgba(0, 0, 0, 0.25),
          0 2px 6px rgba(0, 0, 0, 0.2);
      }

      :host([theme="dark"]) .message.assistant .message-content code {
        background: var(--vanna-background-highest);
        border-color: var(--vanna-outline-default);
      }

      :host([theme="dark"]) .message.assistant .message-timestamp {
        color: var(--vanna-foreground-dimmest);
      }

      :host([theme="dark"]) .message.assistant .message-timestamp::before {
        background: var(--vanna-accent-primary-default);
      }

      :host([theme="dark"]) .message.user {
        background: #ffffff;
        color: rgb(15, 23, 42);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        border: 1.5px solid rgba(47, 110, 255, 0.3);
      }
      
      :host([theme="dark"]) .message.user:hover {
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(47, 110, 255, 0.2);
        border-color: rgba(47, 110, 255, 0.4);
      }
      
      :host([theme="dark"]) .message.user .message-content {
        color: rgb(15, 23, 42);
      }
      
      :host([theme="dark"]) .message.user .message-content code {
        background: rgba(47, 110, 255, 0.1);
        border-color: rgba(47, 110, 255, 0.25);
        color: rgb(15, 23, 42);
      }

      :host([theme="dark"]) .message.user .message-timestamp {
        color: rgb(100, 116, 139);
      }

      :host([theme="dark"]) .message.user .message-timestamp::before {
        background: rgb(47, 110, 255);
        opacity: 0.6;
      }

      @media (max-width: 600px) {
        .message {
          max-width: 100%;
        }

        .message.user {
          max-width: 100%;
        }
      }
    `
  ];

  @property() content = '';
  @property() type: 'user' | 'assistant' = 'user';
  @property({ type: Number }) timestamp = Date.now();
  @property({ reflect: true }) theme = 'light';

  private formatTimestamp(timestamp: number): string {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  render() {
    return html`
      <div class="message ${this.type}">
        <div class="message-content">${this.content}</div>
        <div class="message-timestamp">
          ${this.formatTimestamp(this.timestamp)}
        </div>
      </div>
    `;
  }
}
