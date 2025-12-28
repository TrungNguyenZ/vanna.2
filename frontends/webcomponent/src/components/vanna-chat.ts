import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { vannaDesignTokens } from '../styles/vanna-design-tokens.js';
import { VannaApiClient, ChatStreamChunk } from '../services/api-client.js';
import { ComponentManager, RichComponent } from './rich-component-system.js';
import './vanna-status-bar.js';
import './vanna-progress-tracker.js';
import './vanna-chat-history.js';
import './rich-card.js';
import './rich-task-list.js';
import './rich-progress-bar.js';
import './plotly-chart.js';
import './echarts-chart.js';

@customElement('vanna-chat')
export class VannaChat extends LitElement {
  static styles = [
    vannaDesignTokens,
    css`
      *, *::before, *::after {
        box-sizing: border-box;
      }

      :host {
        display: block;
        font-family: var(--vanna-font-family-default);
        --chat-primary: var(--vanna-accent-primary-default);
        --chat-primary-stronger: var(--vanna-accent-primary-stronger);
        --chat-primary-foreground: rgb(255, 255, 255);
        --chat-accent-soft: var(--vanna-accent-primary-subtle);
        --chat-outline: var(--vanna-outline-default);
        --chat-surface: var(--vanna-background-root);
        --chat-muted: var(--vanna-background-default);
        --chat-muted-stronger: var(--vanna-background-higher);
        width: 100%;
        height: 100%;
        max-width: none;
        margin: 0;
        background: var(--vanna-background-root);
        border: none;
        border-radius: 0;
        box-shadow: none;
        overflow: hidden;
        transition: box-shadow var(--vanna-duration-300) ease, transform var(--vanna-duration-300) ease, border-color var(--vanna-duration-300) ease;
        position: relative;
      }

      :host(:hover) {
        /* No hover effects for fullscreen */
      }

      :host([theme="dark"]) {
        --chat-primary: var(--vanna-accent-primary-default);
        --chat-primary-stronger: var(--vanna-accent-primary-stronger);
        --chat-primary-foreground: rgb(255, 255, 255);
        --chat-accent-soft: var(--vanna-accent-primary-subtle);
        --chat-outline: var(--vanna-outline-default);
        --chat-surface: var(--vanna-background-higher);
        --chat-muted: var(--vanna-background-default);
        --chat-muted-stronger: var(--vanna-background-highest);
        background: var(--vanna-background-higher);
        border-color: var(--vanna-outline-default);
      }

      :host(.maximized) {
        position: fixed;
        top: var(--vanna-space-6);
        left: var(--vanna-space-6);
        right: var(--vanna-space-6);
        bottom: var(--vanna-space-6);
        max-width: none;
        width: auto;
        margin: 0;
        z-index: var(--vanna-z-modal);
        border-radius: var(--vanna-border-radius-xl);
        transform: none;
        box-shadow: var(--vanna-shadow-2xl);
      }

      :host(.maximized):hover {
        transform: none;
      }

      :host(.minimized) {
        position: fixed !important;
        bottom: var(--vanna-space-6) !important;
        right: var(--vanna-space-6) !important;
        width: 64px !important;
        height: 64px !important;
        max-width: none !important;
        margin: 0 !important;
        z-index: var(--vanna-z-modal) !important;
        border-radius: var(--vanna-border-radius-full) !important;
        cursor: pointer !important;
        background: linear-gradient(135deg, var(--chat-primary-stronger), var(--chat-primary)) !important;
        border: 2px solid rgba(255, 255, 255, 0.9) !important;
        box-shadow: var(--vanna-shadow-xl) !important;
        overflow: hidden !important;
      }

      :host(.minimized):hover {
        transform: scale(1.05);
        box-shadow: var(--vanna-shadow-2xl) !important;
      }

      :host(.minimized) .chat-layout {
        display: none;
      }

      .minimized-icon {
        display: none;
      }

      :host(.minimized) .minimized-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        color: var(--chat-primary-foreground);
        font-size: 24px;
        transition: transform var(--vanna-duration-200) ease;
      }

      :host(.minimized) .minimized-icon:hover {
        transform: scale(1.1);
      }

      :host(.minimized) .minimized-icon svg {
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
      }

      .chat-layout {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 300px 320px;
        height: 100%;
        max-height: 100%;
        background: var(--chat-muted);
      }

      .chat-layout.no-history {
        grid-template-columns: minmax(0, 1fr) 300px;
      }

      :host(.maximized) .chat-layout {
        height: 100%;
        max-height: 100%;
      }

      .chat-layout.compact {
        grid-template-columns: 1fr;
      }

      .chat-main {
        display: flex;
        flex-direction: column;
        border-right: 1px solid var(--chat-outline);
        background: var(--chat-surface);
        min-height: 0;
      }

      .chat-layout.compact .chat-main {
        border-right: none;
      }

      .chat-header {
        padding: var(--vanna-space-6) var(--vanna-space-7);
        background: linear-gradient(135deg, rgba(0, 51, 102, 0.9) 0%, rgba(0, 64, 128, 0.8) 100%);
        border-bottom: 2px solid rgba(47, 110, 255, 0.3);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-4);
        color: var(--chat-primary-foreground);
        position: relative;
        overflow: hidden;
      }

      .chat-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
        opacity: 0.6;
        pointer-events: none;
      }

      :host([theme="dark"]) .chat-header {
        border-bottom-color: rgba(255, 255, 255, 0.1);
      }

      .header-top {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: var(--vanna-space-4);
        width: 100%;
      }

      .header-left {
        display: flex;
        align-items: center;
        gap: var(--vanna-space-4);
        min-width: 0;
        flex: 1;
      }

      .header-top-actions {
        display: inline-flex;
        align-items: center;
        gap: var(--vanna-space-2);
        margin-left: auto;
      }

      .chat-avatar {
        width: 44px;
        height: 44px;
        border-radius: var(--vanna-border-radius-lg);
        background: rgb(47, 110, 255);
        backdrop-filter: blur(10px);
        display: grid;
        place-items: center;
        font-weight: 700;
        font-size: 18px;
        letter-spacing: 0.08em;
        color: rgb(255, 255, 255);
        border: 2px solid rgba(47, 110, 255, 0.8);
        box-shadow: 0 2px 8px rgba(47, 110, 255, 0.3);
        text-shadow: none;
      }

      .header-text {
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-1);
        min-width: 0;
      }

      .chat-title {
        margin: 0;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: rgb(255, 255, 255);
        text-shadow: none;
        font-family: var(--vanna-font-family-default);
        line-height: 1.3;
      }

      .chat-subtitle {
        font-size: 13px;
        letter-spacing: 0.01em;
        opacity: 0.9;
        font-weight: 400;
      }

      :host([theme="dark"]) .chat-subtitle {
        opacity: 0.78;
      }

      .window-controls {
        display: inline-flex;
        gap: var(--vanna-space-2);
      }

      .window-control-btn {
        width: 32px;
        height: 32px;
        border-radius: var(--vanna-border-radius-lg);
        border: 1px solid rgba(255, 255, 255, 0.15);
        background: rgba(255, 255, 255, 0.1);
        color: var(--chat-primary-foreground);
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: all var(--vanna-duration-200) ease;
        backdrop-filter: blur(8px);
        position: relative;
        overflow: hidden;
      }

      .window-control-btn::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), transparent);
        opacity: 0;
        transition: opacity var(--vanna-duration-200) ease;
      }

      .window-control-btn:hover {
        transform: translateY(-1px) scale(1.05);
        background: rgba(255, 255, 255, 0.2);
        box-shadow: 
          0 8px 25px -8px rgba(0, 0, 0, 0.3),
          0 0 0 1px rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.3);
      }

      .window-control-btn:hover::before {
        opacity: 1;
      }

      .window-control-btn:active {
        transform: translateY(0) scale(0.95);
      }

      .window-control-btn.minimize:hover {
        background: rgba(255, 193, 7, 0.2);
        color: #ffc107;
        box-shadow: 
          0 8px 25px -8px rgba(255, 193, 7, 0.4),
          0 0 0 1px rgba(255, 193, 7, 0.3);
      }

      .window-control-btn.maximize:hover,
      .window-control-btn.restore:hover {
        background: rgba(40, 167, 69, 0.2);
        color: #28a745;
        box-shadow: 
          0 8px 25px -8px rgba(40, 167, 69, 0.4),
          0 0 0 1px rgba(40, 167, 69, 0.3);
      }

      .window-control-btn svg {
        width: 16px;
        height: 16px;
        transition: transform var(--vanna-duration-150) ease;
      }

      .window-control-btn:hover svg {
        transform: scale(1.1);
      }

      :host([theme="dark"]) .window-control-btn {
        border-color: rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.05);
      }

      :host([theme="dark"]) .window-control-btn:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.25);
      }

      .chat-messages {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: var(--vanna-space-6) var(--vanna-space-6) var(--vanna-space-5);
        background: var(--chat-muted);
        scroll-behavior: smooth;
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-4);
        min-height: 0;
        max-height: 100%;
        position: relative;
      }

      .chat-messages::-webkit-scrollbar {
        width: 10px;
      }

      .chat-messages::-webkit-scrollbar-track {
        background: rgba(225, 230, 238, 0.3);
        border-radius: 5px;
        border: 1px solid rgba(225, 230, 238, 0.5);
      }

      .chat-messages::-webkit-scrollbar-thumb {
        background: rgb(47, 110, 255);
        border-radius: 5px;
        border: 1px solid rgba(47, 110, 255, 0.6);
        box-shadow: 0 0 4px rgba(47, 110, 255, 0.3);
      }

      .chat-messages::-webkit-scrollbar-thumb:hover {
        background: rgb(0, 212, 255);
        border-color: rgba(0, 212, 255, 0.8);
        box-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
      }

      :host([theme="dark"]) .chat-messages {
        background: var(--chat-surface);
      }

      :host([theme="dark"]) .chat-messages::-webkit-scrollbar-thumb {
        background: rgb(47, 110, 255);
        border-color: rgba(47, 110, 255, 0.6);
        box-shadow: 0 0 4px rgba(47, 110, 255, 0.3);
      }

      /* Scroll indicator when there's content above */
      .chat-messages::before {
        content: '';
        position: sticky;
        top: 0;
        display: block;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--vanna-accent-primary-default), transparent);
        opacity: 0;
        transition: opacity var(--vanna-duration-300) ease;
        z-index: 10;
        margin: 0 var(--vanna-space-4) var(--vanna-space-2);
      }

      .chat-messages.has-scroll::before {
        opacity: 0.5;
      }

      .rich-components-container {
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-4);
      }

      .rich-component-wrapper {
        margin: var(--vanna-space-2) 0;
        animation: fade-in-up 0.3s ease-out;
      }

      .unknown-component {
        background: var(--vanna-background-higher);
        border: 1px solid var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-md);
        padding: var(--vanna-space-4);
        font-family: var(--vanna-font-family-mono);
        font-size: 12px;
      }

      .unknown-component p {
        margin: 0 0 var(--vanna-space-2) 0;
        color: var(--vanna-foreground-dimmer);
      }

      .unknown-component pre {
        margin: 0;
        color: var(--vanna-foreground-dimmest);
        overflow-x: auto;
      }

      .chat-input-area {
        padding: var(--vanna-space-3) var(--vanna-space-4) var(--vanna-space-4);
        background: var(--chat-surface);
        border-top: 1px solid var(--chat-outline);
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-2);
        flex-shrink: 0; /* Prevent input area from shrinking */
      }

      :host([theme="dark"]) .chat-input-area {
        border-top-color: rgba(148, 163, 184, 0.22);
      }

      .chat-input-container {
        display: flex;
        align-items: center;
        gap: var(--vanna-space-2);
        padding: 6px 8px 6px 16px;
        border-radius: var(--vanna-border-radius-xl);
        background: rgb(255, 255, 255);
        border: 1.5px solid rgba(225, 230, 238, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all var(--vanna-duration-200) ease;
      }

      .chat-input-container:focus-within {
        border-color: rgb(47, 110, 255);
        box-shadow: 0 0 0 3px rgba(47, 110, 255, 0.1);
        background: rgb(255, 255, 255);
      }

      :host([theme="dark"]) .chat-input-container {
        background: rgb(22, 32, 51);
        border-color: rgba(225, 230, 238, 0.2);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
      }

      :host([theme="dark"]) .chat-input-container:focus-within {
        border-color: rgb(47, 110, 255);
        box-shadow: 0 0 0 3px rgba(47, 110, 255, 0.15);
        background: rgb(30, 42, 65);
      }

      .message-input {
        flex: 1;
        border: none;
        background: transparent;
        font-size: 14px;
        font-family: var(--vanna-font-family-default);
        line-height: 1.5;
        color: rgb(26, 26, 26);
        resize: none;
        min-height: 40px;
        max-height: 120px;
        padding: 10px 0;
        outline: none;
        text-shadow: none;
        font-weight: 400;
      }

      :host([theme="dark"]) .message-input {
        color: rgb(255, 255, 255);
        text-shadow: none;
      }

      .message-input::placeholder {
        color: rgb(154, 166, 184);
        text-shadow: none;
      }

      :host([theme="dark"]) .message-input::placeholder {
        color: rgba(200, 210, 225, 0.65);
        text-shadow: none;
      }

      .message-input:focus {
        outline: none;
      }

      .message-input:disabled {
        color: rgba(148, 163, 184, 0.65);
        cursor: not-allowed;
      }

      :host([theme="dark"]) .message-input:disabled {
        color: rgba(100, 116, 139, 0.55);
      }

      .send-button {
        width: 40px;
        height: 40px;
        border-radius: var(--vanna-border-radius-lg);
        border: 2px solid rgb(47, 110, 255);
        background: rgb(47, 110, 255);
        color: rgb(255, 255, 255);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
        box-shadow: 0 2px 8px rgba(47, 110, 255, 0.3);
        text-shadow: none;
        font-weight: 600;
        flex-shrink: 0;
      }

      .send-button:hover {
        transform: translateY(-1px) scale(1.05);
        box-shadow: 0 4px 12px rgba(47, 110, 255, 0.4);
        border-color: rgb(0, 212, 255);
        background: rgb(0, 212, 255);
      }

      .send-button:active {
        transform: translateY(0) scale(1.0);
        box-shadow: 0 2px 6px rgba(47, 110, 255, 0.3);
      }

      .send-button:disabled {
        background: linear-gradient(135deg, rgba(100, 100, 100, 0.4), rgba(80, 80, 80, 0.4));
        color: rgba(150, 150, 150, 0.5);
        cursor: not-allowed;
        transform: none;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
        border-color: rgba(100, 100, 100, 0.4);
      }

      .send-button svg {
        width: 18px;
        height: 18px;
        filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.7));
      }

      .sidebar {
        background: linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, rgba(15, 23, 42, 0.02) 100%);
        padding: var(--vanna-space-6);
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-4);
        overflow-y: auto;
        overflow-x: hidden;
        min-height: 0;
        width: 300px;
      }

      .history-sidebar {
        width: 320px;
        padding: 0;
        background: var(--vanna-background-higher);
        border-left: 2px solid rgba(225, 230, 238, 1);
      }

      .sidebar::-webkit-scrollbar {
        width: 10px;
      }

      .sidebar::-webkit-scrollbar-track {
        background: rgba(225, 230, 238, 0.3);
        border-radius: 5px;
        border: 1px solid rgba(225, 230, 238, 0.5);
      }

      .sidebar::-webkit-scrollbar-thumb {
        background: rgb(47, 110, 255);
        border-radius: 5px;
        border: 1px solid rgba(47, 110, 255, 0.6);
        box-shadow: 0 0 4px rgba(47, 110, 255, 0.3);
      }

      .sidebar::-webkit-scrollbar-thumb:hover {
        background: rgb(0, 212, 255);
        border-color: rgba(0, 212, 255, 0.8);
        box-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
      }

      :host([theme="dark"]) .sidebar {
        background: linear-gradient(180deg, rgba(79, 70, 229, 0.22) 0%, rgba(15, 23, 42, 0.45) 100%);
      }

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: var(--vanna-space-12) var(--vanna-space-8);
        margin: var(--vanna-space-8) var(--vanna-space-6);
        font-size: 15px;
        font-weight: 500;
        line-height: 1.6;
        background: rgb(255, 255, 255);
        border-radius: var(--vanna-border-radius-2xl);
        border: 2px dashed rgba(225, 230, 238, 1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        backdrop-filter: blur(8px);
        transition: all var(--vanna-duration-300) ease;
      }

      .empty-state:hover {
        border-color: rgb(47, 110, 255);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(47, 110, 255, 0.15);
        background: rgb(255, 255, 255);
      }

      :host([theme="dark"]) .empty-state {
        background: rgb(22, 32, 51);
        border-color: rgba(225, 230, 238, 0.2);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      }

      :host([theme="dark"]) .empty-state:hover {
        border-color: rgb(47, 110, 255);
        box-shadow: 0 4px 12px rgba(47, 110, 255, 0.2);
        background: rgb(30, 42, 65);
      }

      .empty-state-icon {
        width: 64px;
        height: 64px;
        margin: 0 auto var(--vanna-space-6);
        opacity: 0.9;
        color: rgb(47, 110, 255);
        filter: none;
      }

      .empty-state-text {
        font-size: 20px;
        font-weight: 700;
        color: rgb(26, 26, 26);
        margin-bottom: var(--vanna-space-3);
        text-shadow: none;
        letter-spacing: 0.08em;
        line-height: 1.4;
      }

      .empty-state-subtitle {
        font-size: 15px;
        color: rgb(93, 107, 130);
        opacity: 1;
        font-weight: 500;
        text-shadow: none;
        letter-spacing: 0.03em;
        line-height: 1.5;
      }

      @media (max-width: 880px) {
        .chat-layout {
          grid-template-columns: 1fr;
          height: min(600px, 85vh);
          max-height: 85vh;
        }

        .sidebar {
          display: none;
        }

        .chat-main {
          border-right: none;
        }
      }

      @media (max-width: 600px) {
        :host {
          border-radius: var(--vanna-border-radius-xl);
        }

        .chat-layout {
          height: min(500px, 80vh);
          max-height: 80vh;
        }

        .chat-header {
          border-bottom-width: 0;
          padding: var(--vanna-space-5) var(--vanna-space-5) var(--vanna-space-4);
        }

        .chat-messages {
          padding: var(--vanna-space-4) var(--vanna-space-4);
        }

        .empty-state {
          padding: var(--vanna-space-10) var(--vanna-space-6);
          margin: var(--vanna-space-6) var(--vanna-space-4);
          font-size: 14px;
        }

        .empty-state-text {
          font-size: 15px;
        }

        .empty-state-icon {
          width: 56px;
          height: 56px;
          margin-bottom: var(--vanna-space-5);
        }

        .chat-input-area {
          padding: var(--vanna-space-4) var(--vanna-space-4) var(--vanna-space-5);
        }
      }
    `
  ];

  @property() title = 'AI Chat';
  @property() placeholder = 'Ask me anything...';
  @property({ type: Boolean }) disabled = false;
  @property({ type: Boolean }) showProgress = true;
  @property({ type: Boolean }) showHistory = true;
  @property({ type: Boolean }) allowMinimize = false;
  @property({ reflect: true }) theme = 'light';
  @property({ attribute: 'api-base' }) apiBaseUrl = '';
  @property({ attribute: 'sse-endpoint' }) sseEndpoint = '/api/vanna/v2/chat_sse';
  @property({ attribute: 'ws-endpoint' }) wsEndpoint = '/api/vanna/v2/chat_websocket';
  @property({ attribute: 'poll-endpoint' }) pollEndpoint = '/api/vanna/v2/chat_poll';
  @property() subtitle = '';
  @property() startingState: 'normal' | 'maximized' | 'minimized' = 'normal';

  @state() private currentMessage = '';
  @state() private status: 'idle' | 'working' | 'error' | 'success' = 'idle';
  @state() private statusMessage = '';
  @state() private statusDetail = '';
  private _windowState: 'normal' | 'maximized' | 'minimized' = 'normal';

  @property({ reflect: false })
  get windowState() {
    return this._windowState;
  }

  set windowState(value: 'normal' | 'maximized' | 'minimized') {
    console.log('windowState setter called with:', value);
    console.trace('Call stack:');
    const oldValue = this._windowState;
    this._windowState = value;
    this.requestUpdate('windowState', oldValue);
  }

  private apiClient!: VannaApiClient;
  private conversationId: string;
  private componentManager: ComponentManager | null = null;
  private componentObserver: MutationObserver | null = null;

  constructor() {
    super();
    // Note: Don't create apiClient here - attributes haven't been set yet!
    // It will be created lazily in getApiClient() or firstUpdated()
    this.conversationId = this.generateId();
  }

  /**
   * Ensure API client is created/updated with current endpoint values
   */
  private ensureApiClient() {
    // Always recreate to ensure we have the latest endpoint values
    console.log('[VannaChat] Creating API client with:', {
      baseUrl: this.apiBaseUrl,
      sseEndpoint: this.sseEndpoint,
      wsEndpoint: this.wsEndpoint,
      pollEndpoint: this.pollEndpoint
    });

    this.apiClient = new VannaApiClient({
      baseUrl: this.apiBaseUrl,
      sseEndpoint: this.sseEndpoint,
      wsEndpoint: this.wsEndpoint,
      pollEndpoint: this.pollEndpoint
    });
  }

  firstUpdated() {
    // Create API client now that attributes have been set
    this.ensureApiClient();

    // Initialize component manager with rich components container (fallback)
    const richContainer = this.shadowRoot?.querySelector('.rich-components-container') as HTMLElement;
    if (richContainer) {
      this.componentManager = new ComponentManager(richContainer);
      
      // Watch for changes in the rich components container to manage empty state
      this.componentObserver = new MutationObserver(() => {
        // Update empty state visibility
        this.updateEmptyState();
      });
      
      this.componentObserver.observe(richContainer, {
        childList: true,
        subtree: true,
        attributes: false
      });
    }

    // Set initial window state from startingState property
    if (this.startingState !== 'normal') {
      this._windowState = this.startingState;
    }

    // Set initial CSS class
    this.classList.add(this._windowState);

    // Request starter UI from backend
    this.requestStarterUI();
  }

  /**
   * Request starter UI (buttons, welcome messages) from backend
   */
  private async requestStarterUI(): Promise<void> {
    try {
      const request = {
        message: "",
        conversation_id: this.conversationId,
        request_id: this.generateId(),
        metadata: {
          starter_ui_request: true
        }
      };

      // Stream the starter UI response
      await this.handleStreamingResponse(request);
    } catch (error) {
      console.error('Error requesting starter UI:', error);
      // Fail silently - starter UI is optional
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    
    // Clean up mutation observer
    if (this.componentObserver) {
      this.componentObserver.disconnect();
      this.componentObserver = null;
    }
  }

  updated(changedProperties: Map<string, any>) {
    super.updated(changedProperties);

    // Update host classes based on window state
    if (changedProperties.has('windowState')) {
      console.log('windowState changed to:', this._windowState);
      this.classList.remove('normal', 'maximized', 'minimized');
      this.classList.add(this._windowState);
      console.log('Applied CSS classes:', this.className);
    }
  }

  private handleInput(e: Event) {
    const input = e.target as HTMLInputElement;
    this.currentMessage = input.value;
  }

  private handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.sendMessage();
    }
  }

  /**
   * Send a message programmatically (can be called from buttons or external code)
   * Returns a Promise that resolves with success status
   */
  sendMessage(messageText?: string): Promise<boolean> {
    console.log('sendMessage called with:', messageText);

    // Use provided message or fall back to current input
    // Check if messageText is actually a string (not an event object)
    const textToSend = (typeof messageText === 'string') ? messageText : this.currentMessage;

    console.log('Will send:', textToSend);

    if (!textToSend.trim() || this.disabled) {
      console.log('Message empty or disabled, not sending');
      return Promise.resolve(false);
    }

    return this._sendMessageInternal(textToSend);
  }

  private async _sendMessageInternal(messageText: string): Promise<boolean> {
    console.log('_sendMessageInternal called with:', messageText);

    // Create user message as a rich component and send to ComponentManager
    const userRichComponent: RichComponent = {
      id: `user-message-${Date.now()}`,
      type: 'user-message',
      lifecycle: 'create',
      data: {
        content: messageText,
        sender: 'user'
      },
      children: [],
      timestamp: new Date().toISOString(),
      visible: true,
      interactive: false
    };

    // Add user message to ComponentManager for chronological ordering
    if (this.componentManager) {
      const update = {
        operation: 'create' as const,
        target_id: userRichComponent.id,
        component: userRichComponent,
        timestamp: userRichComponent.timestamp
      };
      this.componentManager.processUpdate(update);
    }

    // Update empty state after a brief delay to let ComponentManager render
    setTimeout(() => this.updateEmptyState(), 0);

    console.log('Added user message as rich component to ComponentManager:', userRichComponent);

    // Update the view
    this.requestUpdate();

    // Update status to working (initial frontend status before backend responds)
    this.setStatus('working', 'Sending message...', '');

    // Clear input only if we're sending from the input field
    if (messageText === this.currentMessage) {
      this.currentMessage = '';
      const input = this.shadowRoot?.querySelector('.message-input') as HTMLTextAreaElement;
      if (input) {
        input.value = '';
        input.style.height = 'auto';
      }
    }

    // Dispatch event for external listeners
    this.dispatchEvent(new CustomEvent('message-sent', {
      detail: { message: { content: messageText, type: 'user' } },
      bubbles: true,
      composed: true
    }));

    try {
      // Create the request
      const request = {
        message: messageText,
        conversation_id: this.conversationId,
        request_id: this.generateId(),
        metadata: {}
      };

      // Stream the response
      await this.handleStreamingResponse(request);
      
      // Save conversation to localStorage for history
      this.saveConversationToHistory(this.conversationId, messageText);
      
      return true; // Success

    } catch (error) {
      console.error('Error sending message:', error);
      this.setStatus('error', 'Failed to send message', error instanceof Error ? error.message : 'Unknown error');

      // Add error message
      this.addMessage(
        `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'assistant'
      );
      return false; // Failure
    }
  }

  private getTitleInitials(): string {
    const title = (this.title || '').trim();
    if (!title) {
      return 'VA';
    }

    const parts = title.split(/\s+/).filter(Boolean);
    if (parts.length === 1) {
      return parts[0].charAt(0).toUpperCase() || 'V';
    }

    const first = parts[0].charAt(0);
    const last = parts[parts.length - 1].charAt(0);
    const initials = `${first}${last}`.toUpperCase();
    return initials || 'VA';
  }

  // Window control methods removed - no minimize/maximize functionality


  addMessage(content: string, type: 'user' | 'assistant') {
    // Create message as a rich component and send to ComponentManager
    const richComponent: RichComponent = {
      id: `${type}-message-${Date.now()}`,
      type: `${type}-message`,
      lifecycle: 'create',
      data: {
        content: content,
        sender: type
      },
      children: [],
      timestamp: new Date().toISOString(),
      visible: true,
      interactive: false
    };

    if (this.componentManager) {
      const update = {
        operation: 'create' as const,
        target_id: richComponent.id,
        component: richComponent,
        timestamp: richComponent.timestamp
      };
      this.componentManager.processUpdate(update);
    }
  }

  setStatus(status: typeof this.status, message: string, detail?: string) {
    this.status = status;
    this.statusMessage = message;
    this.statusDetail = detail || '';
  }

  clearStatus() {
    this.statusMessage = '';
    this.statusDetail = '';
    this.status = 'idle';
  }

  getProgressTracker(): HTMLElement | null {
    return this.shadowRoot?.querySelector('vanna-progress-tracker') || null;
  }

  private async handleStreamingResponse(request: any) {
    // Ensure API client exists and is up to date
    if (!this.apiClient || this.apiClient.baseUrl !== this.apiBaseUrl) {
      this.ensureApiClient();
    }

    // Note: Status bar updates are now controlled by backend via StatusBarUpdateComponent
    // Frontend only shows initial "Sending message..." status (set in _sendMessageInternal)
    // and handles connection errors below

    try {
      // Use SSE streaming by default
      const stream = this.apiClient.streamChat(request);

      for await (const chunk of stream) {
        await this.processChunk(chunk);
      }

      // Backend is responsible for final status via StatusBarUpdateComponent
      // No frontend status clearing here

    } catch (error) {
      console.warn('SSE streaming failed, falling back to polling:', error);

      try {
        // Fallback to polling - show user we're retrying
        this.setStatus('working', 'Connection issue, retrying...', 'Using fallback method');
        const response = await this.apiClient.sendPollMessage(request);

        for (const chunk of response.chunks) {
          await this.processChunk(chunk);
        }

        // Backend is responsible for final status via StatusBarUpdateComponent

      } catch (pollError) {
        // Only set error status if polling also fails (connection error)
        this.setStatus('error', 'Connection failed', 'Unable to reach server');
        throw pollError;
      }
    }
  }

  private async processChunk(chunk: ChatStreamChunk) {
    // Dispatch chunk event for external listeners
    this.dispatchEvent(new CustomEvent('chunk-received', {
      detail: { chunk },
      bubbles: true,
      composed: true
    }));

    console.log('Processing chunk:', chunk); // Debug log

    // Handle rich components via ComponentManager
    if (chunk.rich && this.componentManager) {
      console.log('Processing rich component via ComponentManager:', chunk.rich); // Debug log
      
      if (chunk.rich.id && chunk.rich.lifecycle) {
        // Standard rich component with lifecycle
        const component = chunk.rich as RichComponent;
        const update = {
          operation: chunk.rich.lifecycle as any,
          target_id: chunk.rich.id,
          component: component,
          timestamp: new Date().toISOString()
        };
        this.componentManager.processUpdate(update);
      } else if (chunk.rich.type === 'component_update') {
        // Component update format
        this.componentManager.processUpdate(chunk.rich as any);
      } else {
        // Generic rich component
        const component = chunk.rich as RichComponent;
        const update = {
          operation: 'create' as const,
          target_id: component.id || `component-${Date.now()}`,
          component: component,
          timestamp: new Date().toISOString()
        };
        this.componentManager.processUpdate(update);
      }
      
      return;
    }

    // Update progress tracker for legacy components (keep for backward compatibility)
    const progressTracker = this.getProgressTracker();
    if (progressTracker && 'addStep' in progressTracker) {
      (progressTracker as any).addStep({
        id: `chunk-${Date.now()}`,
        title: this.getChunkTitle(chunk),
        status: 'completed',
        timestamp: chunk.timestamp
      });
    }

    // Handle different chunk types (legacy components)
    const componentType = chunk.rich?.type;
    switch (componentType) {
      case 'text':
        // Text chunks are handled in the main loop
        break;

      case 'thinking':
        // Legacy: Status bar updates now handled by backend via StatusBarUpdateComponent
        // This case is kept for backward compatibility but doesn't update status
        break;

      case 'tool_execution':
        // Legacy: Status bar updates now handled by backend via StatusBarUpdateComponent
        // This case is kept for backward compatibility but doesn't update status
        break;

      case 'error':
        throw new Error(chunk.rich.data?.message || 'Unknown error from agent');

      default:
        // Handle other component types as needed
        console.log('Received chunk:', componentType, chunk.rich);
    }
  }


  private getChunkTitle(chunk: ChatStreamChunk): string {
    const componentType = chunk.rich?.type;
    switch (componentType) {
      case 'text':
        return 'Generating response';
      case 'thinking':
        return 'Thinking';
      case 'tool_execution':
        return `Tool: ${chunk.rich.data?.tool_name || 'Unknown'}`;
      default:
        return `Processing ${componentType || 'component'}`;
    }
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * Update the API base URL and recreate the client
   */
  updateApiBaseUrl(baseUrl: string) {
    this.apiBaseUrl = baseUrl;
    this.ensureApiClient();
  }

  /**
   * Get the API client instance for direct access
   */
  getApiClient(): VannaApiClient {
    if (!this.apiClient) {
      this.ensureApiClient();
    }
    return this.apiClient;
  }

  /**
   * Set custom headers for authentication or other purposes
   */
  setCustomHeaders(headers: Record<string, string>) {
    this.apiClient.setCustomHeaders(headers);
  }

  /**
   * Update empty state visibility based on whether there are components
   */
  private updateEmptyState() {
    const emptyState = this.shadowRoot?.querySelector('#empty-state') as HTMLElement;
    const richContainer = this.shadowRoot?.querySelector('.rich-components-container') as HTMLElement;
    
    if (emptyState && richContainer) {
      // Show empty state if rich container has no children
      const hasContent = richContainer.children.length > 0;
      emptyState.style.display = hasContent ? 'none' : 'flex';
    }
  }

  /**
   * Update scroll indicator based on scroll position
   */
  private updateScrollIndicator() {
    const messagesContainer = this.shadowRoot?.querySelector('.chat-messages');
    if (!messagesContainer) return;
    
    // Check if there's content scrolled above
    const hasScrolledContent = messagesContainer.scrollTop > 10;
    
    // Update scroll indicator class
    messagesContainer.classList.toggle('has-scroll', hasScrolledContent);
  }

  /**
   * Scroll to the top of the last message/component that was added
   * This always scrolls regardless of current scroll position
   */
  scrollToLastMessage() {
    const messagesContainer = this.shadowRoot?.querySelector('.chat-messages');
    const richContainer = this.shadowRoot?.querySelector('.rich-components-container');
    
    if (!messagesContainer || !richContainer) return;

    // Get the last child element (the most recently added component)
    const lastComponent = richContainer.lastElementChild as HTMLElement;
    if (!lastComponent) return;

    // Scroll so the top of the last component is visible
    lastComponent.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Update scroll indicator after scrolling
    setTimeout(() => this.updateScrollIndicator(), 100);
  }

  /**
   * Clear all messages (useful for testing)
   */
  clearMessages() {
    if (this.componentManager) {
      this.componentManager.clear();
    }
    this.updateEmptyState();
    this.requestUpdate();
  }

  /**
   * Add multiple messages at once (useful for testing scrolling)
   */
  addTestMessages(count: number = 10) {
    for (let i = 1; i <= count; i++) {
      setTimeout(() => {
        const type = i % 2 === 0 ? 'assistant' : 'user';
        const content = `This is test message number ${i}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.`;
        this.addMessage(content, type);
      }, i * 100); // Stagger the messages to simulate real timing
    }
  }

  render() {
    return html`
      <!-- Minimized icon removed -->

      <!-- Main chat interface -->
      <div class="chat-layout ${this.showProgress ? '' : 'compact'} ${this.showHistory ? '' : 'no-history'}">
        <div class="chat-main">
          <div class="chat-header">
            <div class="header-top">
              <div class="header-left">
                <div class="chat-avatar" aria-hidden="true">${this.getTitleInitials()}</div>
                <div class="header-text">
                  <h2 class="chat-title">${this.title}</h2>
                </div>
              </div>
              <!-- Window controls removed -->
            </div>
          </div>

          <div class="chat-messages">
            <!-- Empty state - shown when no components exist -->
            <div class="empty-state" id="empty-state">
              <div class="empty-state-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
                </svg>
              </div>
              <div class="empty-state-text">Start a conversation</div>
              <div class="empty-state-subtitle">Type your message below to begin chatting</div>
            </div>

            <!-- Rich Components Container - all content renders here via ComponentManager -->
            <div class="rich-components-container"></div>
          </div>

          <div class="chat-input-area">
            <vanna-status-bar
              .status=${this.status}
              .message=${this.statusMessage}
              .detail=${this.statusDetail}
              theme=${this.theme}>
            </vanna-status-bar>

            <div class="chat-input-container">
              <textarea
                class="message-input"
                .placeholder=${this.placeholder}
                .disabled=${this.disabled}
                @input=${this.handleInput}
                @keydown=${this.handleKeyPress}
                rows="1"
              ></textarea>
              <button
                class="send-button"
                type="button"
                aria-label="Send message"
                .disabled=${this.disabled || !this.currentMessage.trim()}
                @click=${this.sendMessage}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        ${this.showProgress ? html`
          <div class="sidebar">
            <vanna-progress-tracker theme=${this.theme}></vanna-progress-tracker>
          </div>
        ` : ''}
        ${this.showHistory ? html`
          <div class="sidebar history-sidebar">
            <vanna-chat-history 
              api-base=${this.apiBaseUrl}
              current-conversation-id=${this.conversationId}
              theme=${this.theme}
              @conversation-selected=${this.handleConversationSelected}
              @new-conversation=${this.handleNewConversation}
              @conversation-deleted=${this.handleConversationDeleted}>
            </vanna-chat-history>
          </div>
        ` : ''}
      </div>
    `;
  }

  private handleConversationSelected(e: CustomEvent) {
    const { conversationId } = e.detail;
    if (conversationId && conversationId !== this.conversationId) {
      this.conversationId = conversationId;
      // Reload conversation messages
      this.loadConversation(conversationId);
    }
  }

  private handleConversationDeleted(e: CustomEvent) {
    const { conversationId: deletedId } = e.detail;
    
    // If the deleted conversation is the current one, create a new conversation
    if (deletedId === this.conversationId) {
      // Generate new conversation ID
      this.conversationId = this.generateId();
      
      // Clear messages
      if (this.componentManager) {
        this.componentManager.clear();
        const container = this.shadowRoot?.querySelector('.rich-components-container') as HTMLElement;
        if (container) {
          container.innerHTML = '';
        }
      }
      
      // Clear input
      const textarea = this.shadowRoot?.querySelector('.message-input') as HTMLTextAreaElement;
      if (textarea) {
        textarea.value = '';
        this.currentMessage = '';
      }
      
      // Update empty state
      this.updateEmptyState();
      
      // Request starter UI
      this.requestStarterUI();
    }
  }

  private handleNewConversation() {
    // Always create new conversation when button is clicked
    // Generate new conversation ID
    this.conversationId = this.generateId();
    
    // Clear current messages
    // Note: componentManager.clear() already clears innerHTML and ensures styles are injected
    if (this.componentManager) {
      this.componentManager.clear();
      // Don't call innerHTML = '' here as it will remove the style element injected by clear()
    }
    
    // Clear input
    const textarea = this.shadowRoot?.querySelector('.message-input') as HTMLTextAreaElement;
    if (textarea) {
      textarea.value = '';
      this.currentMessage = '';
    }
    
    // Clear status
    this.clearStatus();
    
    // Update empty state
    this.updateEmptyState();
    
    // Request starter UI for the new conversation
    // Use setTimeout to ensure DOM is ready and styles are applied
    setTimeout(() => {
      this.requestStarterUI();
    }, 0);
    
    // Notify history component to refresh
    const historyComponent = this.shadowRoot?.querySelector('vanna-chat-history') as any;
    if (historyComponent && typeof historyComponent.loadConversations === 'function') {
      historyComponent.loadConversations();
    }
  }

  private async loadConversation(conversationId: string) {
    // Clear current messages
    if (this.componentManager) {
      const container = this.shadowRoot?.querySelector('.rich-components-container') as HTMLElement;
      if (container) {
        container.innerHTML = '';
      }
    }

    // Load conversation from API
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/vanna/v2/conversations/${conversationId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Render conversation messages
        if (data.messages && this.componentManager) {
          for (const msg of data.messages) {
            this.addMessage(msg.content, msg.role);
          }
        }
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
      // Try loading from localStorage as fallback
      this.loadConversationFromLocalStorage(conversationId);
    }
  }

  private saveConversationToHistory(conversationId: string, firstMessage: string) {
    try {
      const stored = localStorage.getItem('vanna_conversations');
      const conversations = stored ? JSON.parse(stored) : [];
      
      // Check if conversation already exists
      const existingIndex = conversations.findIndex((c: any) => c.id === conversationId);
      const conversationData = {
        id: conversationId,
        messages: [
          { role: 'user', content: firstMessage }
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      if (existingIndex >= 0) {
        // Update existing conversation
        conversations[existingIndex] = {
          ...conversations[existingIndex],
          updated_at: new Date().toISOString(),
        };
      } else {
        // Add new conversation
        conversations.unshift(conversationData);
        // Keep only last 50 conversations
        if (conversations.length > 50) {
          conversations.pop();
        }
      }
      
      localStorage.setItem('vanna_conversations', JSON.stringify(conversations));
      
      // Notify history component to refresh
      const historyComponent = this.shadowRoot?.querySelector('vanna-chat-history') as any;
      if (historyComponent && typeof historyComponent.loadConversations === 'function') {
        historyComponent.loadConversations();
      }
    } catch (error) {
      console.error('Failed to save conversation to history:', error);
    }
  }

  private loadConversationFromLocalStorage(conversationId: string) {
    try {
      const stored = localStorage.getItem('vanna_conversations');
      if (stored) {
        const conversations = JSON.parse(stored);
        const conversation = conversations.find((c: any) => c.id === conversationId);
        if (conversation && conversation.messages && this.componentManager) {
          for (const msg of conversation.messages) {
            this.addMessage(msg.content, msg.role);
          }
        }
      }
    } catch (error) {
      console.error('Failed to load conversation from localStorage:', error);
    }
  }
}
