import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { vannaDesignTokens } from "../styles/vanna-design-tokens.js";

type DatabaseType = "default" | "sqlserver" | "mysql" | "postgresql";

interface DatabaseConnection {
  type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  options?: Record<string, any>;
}

@customElement("database-settings-manager")
export class DatabaseSettingsManager extends LitElement {
  static styles = [
    vannaDesignTokens,
    css`
      :host {
        display: block;
      }

      .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.2s ease;
      }

      @keyframes fadeIn {
        from {
          opacity: 0;
        }
        to {
          opacity: 1;
        }
      }

      .modal {
        background: white;
        border-radius: var(--vanna-border-radius-xl);
        box-shadow: var(--vanna-shadow-2xl);
        width: 90%;
        max-width: 600px;
        max-height: 90vh;
        display: flex;
        flex-direction: column;
        animation: slideUp 0.3s ease;
        overflow: hidden;
      }

      @keyframes slideUp {
        from {
          transform: translateY(20px);
          opacity: 0;
        }
        to {
          transform: translateY(0);
          opacity: 1;
        }
      }

      .modal-header {
        padding: var(--vanna-space-6);
        border-bottom: 1px solid var(--vanna-outline-default);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-shrink: 0;
      }

      .modal-title {
        font-size: 20px;
        font-weight: 600;
        color: var(--vanna-foreground-default);
        margin: 0;
      }

      .close-button {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: var(--vanna-foreground-dimmer);
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--vanna-border-radius-md);
        transition: all var(--vanna-duration-200) ease;
      }

      .close-button:hover {
        background: var(--vanna-background-higher);
        color: var(--vanna-foreground-default);
      }

      .modal-content {
        flex: 1;
        overflow-y: auto;
        padding: var(--vanna-space-6);
        overflow-x: hidden;
      }

      .form-group {
        margin-bottom: var(--vanna-space-4);
      }

      .form-label {
        display: block;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: var(--vanna-space-2);
        color: var(--vanna-foreground-default);
      }

      .form-select,
      .form-input {
        width: 100%;
        padding: var(--vanna-space-3);
        border: 1px solid var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-md);
        font-size: 14px;
        font-family: inherit;
        transition: all var(--vanna-duration-200) ease;
        box-sizing: border-box;
      }

      .form-select:focus,
      .form-input:focus {
        outline: none;
        border-color: var(--vanna-navy);
        box-shadow: 0 0 0 3px rgba(47, 110, 255, 0.1);
      }

      .form-actions {
        display: flex;
        gap: var(--vanna-space-3);
        justify-content: flex-end;
        margin-top: var(--vanna-space-6);
        padding-top: var(--vanna-space-4);
        border-top: 1px solid var(--vanna-outline-default);
      }

      .form-button {
        padding: var(--vanna-space-3) var(--vanna-space-6);
        border: none;
        border-radius: var(--vanna-border-radius-md);
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
      }

      .form-button.primary {
        background: var(--vanna-navy);
        color: white;
      }

      .form-button.primary:hover:not(:disabled) {
        background: var(--vanna-accent-primary-stronger);
      }

      .form-button.secondary {
        background: var(--vanna-background-higher);
        color: var(--vanna-foreground-default);
      }

      .form-button.secondary:hover {
        background: var(--vanna-background-highest);
      }

      .form-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .status-message {
        padding: var(--vanna-space-3);
        border-radius: var(--vanna-border-radius-md);
        margin-bottom: var(--vanna-space-4);
        font-size: 14px;
      }

      .status-message.success {
        background: rgba(40, 167, 69, 0.1);
        color: #28a745;
        border: 1px solid rgba(40, 167, 69, 0.2);
      }

      .status-message.error {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
      }

      .status-message.info {
        background: rgba(47, 110, 255, 0.1);
        color: rgb(47, 110, 255);
        border: 1px solid rgba(47, 110, 255, 0.2);
      }

      .loading {
        display: inline-block;
        width: 14px;
        height: 14px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
        margin-right: var(--vanna-space-2);
      }

      @keyframes spin {
        to {
          transform: rotate(360deg);
        }
      }
    `,
  ];

  @state() private isOpen = false;
  @state() private connection: DatabaseConnection = {
    type: "default",
    host: "",
    port: 1433,
    database: "",
    username: "",
    password: "",
  };
  @state() private testing = false;
  @state() private statusMessage: { type: "success" | "error" | "info"; text: string } | null = null;
  @state() private apiBaseUrl = "";

  connectedCallback() {
    super.connectedCallback();
    const vannaChat = document.querySelector("vanna-chat");
    if (vannaChat) {
      this.apiBaseUrl = vannaChat.getAttribute("api-base") || "";
    }
    window.addEventListener("open-database-settings", () => {
      this.open();
    });
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    window.removeEventListener("open-database-settings", () => {});
  }

  async open() {
    this.isOpen = true;
    await this.loadCurrentConnection();
  }

  close() {
    this.isOpen = false;
    this.statusMessage = null;
  }

  async loadCurrentConnection() {
    try {
      // First try to load from localStorage
      const saved = localStorage.getItem("vanna_database_connection");
      if (saved) {
        try {
          const savedConnection = JSON.parse(saved);
          this.connection = { ...this.connection, ...savedConnection };
          return;
        } catch (e) {
          console.error("Failed to parse saved connection:", e);
        }
      }
      
      // Fallback: Load from API (default connection from .env)
      const response = await fetch(`${this.apiBaseUrl}/api/vanna/v2/database/connection`);
      if (response.ok) {
        const data = await response.json();
        if (data.connection && data.connection.type === "default") {
          // Only use default if no saved connection
          this.connection = { ...this.connection, ...data.connection };
        }
      }
    } catch (error) {
      console.error("Failed to load current connection:", error);
    }
  }

  handleDatabaseTypeChange(e: Event) {
    const select = e.target as HTMLSelectElement;
    const newType = select.value as DatabaseType;
    
    if (newType === "default") {
      // Load default connection from .env (SQL Server)
      this.connection = {
        ...this.connection,
        type: newType,
      };
      this.loadDefaultConnection();
    } else {
      // Set default ports for other types
      const defaultPorts: Record<Exclude<DatabaseType, "default">, number> = {
        sqlserver: 1433,
        mysql: 3306,
        postgresql: 5432,
      };
      // Create new object to trigger LitElement reactivity
      this.connection = {
        type: newType,
        host: this.connection.host || "",
        port: defaultPorts[newType],
        database: this.connection.database || "",
        username: this.connection.username || "",
        password: this.connection.password || "",
      };
    }
    this.statusMessage = null;
  }

  async loadDefaultConnection() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/vanna/v2/database/connection`);
      if (response.ok) {
        const data = await response.json();
        if (data.connection) {
          this.connection = { ...this.connection, ...data.connection };
        } else {
          // If no connection found, use SQL Server defaults from .env
          this.connection = {
            type: "default",
            host: "",
            port: 1433,
            database: "",
            username: "",
            password: "",
          };
        }
      }
    } catch (error) {
      console.error("Failed to load default connection:", error);
    }
  }

  handleInputChange(field: keyof DatabaseConnection, e: Event) {
    const input = e.target as HTMLInputElement;
    // Create new object to trigger LitElement reactivity
    if (field === "port") {
      this.connection = {
        ...this.connection,
        [field]: parseInt(input.value) || 0,
      };
    } else {
      this.connection = {
        ...this.connection,
        [field]: input.value,
      };
    }
    this.statusMessage = null;
  }

  async testConnection() {
    if (this.connection.type === "default") {
      // Test default connection
      this.testing = true;
      this.statusMessage = null;

      try {
        const response = await fetch(`${this.apiBaseUrl}/api/vanna/v2/database/test-default`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        const data = await response.json();

        if (response.ok && data.success) {
          this.statusMessage = {
            type: "success",
            text: "Kết nối mặc định thành công!",
          };
        } else {
          this.statusMessage = {
            type: "error",
            text: data.message || "Kết nối mặc định thất bại.",
          };
        }
      } catch (error) {
        this.statusMessage = {
          type: "error",
          text: `Lỗi khi kiểm tra kết nối: ${error instanceof Error ? error.message : String(error)}`,
        };
      } finally {
        this.testing = false;
      }
      return;
    }

    if (!this.connection.host || !this.connection.database) {
      this.statusMessage = {
        type: "error",
        text: "Vui lòng nhập đầy đủ thông tin kết nối",
      };
      return;
    }

    this.testing = true;
    this.statusMessage = null;

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/vanna/v2/database/test`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(this.connection),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        this.statusMessage = {
          type: "success",
          text: "Kết nối thành công!",
        };
      } else {
        this.statusMessage = {
          type: "error",
          text: data.message || "Kết nối thất bại. Vui lòng kiểm tra lại thông tin.",
        };
      }
    } catch (error) {
      this.statusMessage = {
        type: "error",
        text: `Lỗi khi kiểm tra kết nối: ${error instanceof Error ? error.message : String(error)}`,
      };
    } finally {
      this.testing = false;
    }
  }

  async saveConnection() {
    if (this.connection.type === "default") {
      // Remove saved connection from localStorage to use default from .env
      localStorage.removeItem("vanna_database_connection");
      this.statusMessage = {
        type: "success",
        text: "Đã lưu cấu hình sử dụng kết nối mặc định!",
      };
      setTimeout(() => {
        this.close();
      }, 1500);
      return;
    }

    if (!this.connection.host || !this.connection.database) {
      this.statusMessage = {
        type: "error",
        text: "Vui lòng nhập đầy đủ thông tin kết nối",
      };
      return;
    }

    try {
      // Save to localStorage only
      const connectionToSave = {
        type: this.connection.type,
        host: this.connection.host,
        port: this.connection.port,
        database: this.connection.database,
        username: this.connection.username,
        password: this.connection.password,
      };
      localStorage.setItem("vanna_database_connection", JSON.stringify(connectionToSave));
      
      this.statusMessage = {
        type: "success",
        text: "Đã lưu cấu hình kết nối thành công!",
      };
      setTimeout(() => {
        this.close();
      }, 1500);
    } catch (error) {
      this.statusMessage = {
        type: "error",
        text: `Lỗi khi lưu cấu hình: ${error instanceof Error ? error.message : String(error)}`,
      };
    }
  }

  render() {
    if (!this.isOpen) {
      return html``;
    }

    return html`
      <div
        class="modal-overlay"
        @click=${(e: Event) => {
          if (e.target === e.currentTarget) {
            this.close();
          }
        }}
      >
        <div class="modal" @click=${(e: Event) => e.stopPropagation()}>
          <div class="modal-header">
            <h2 class="modal-title">Cấu hình Database</h2>
            <button class="close-button" @click=${this.close}>×</button>
          </div>

          <div class="modal-content">
            ${this.statusMessage
              ? html`
                  <div class="status-message ${this.statusMessage.type}">
                    ${this.statusMessage.text}
                  </div>
                `
              : ""}

            <div class="form-group">
              <label class="form-label">Loại Database *</label>
              <select
                class="form-select"
                .value=${this.connection.type}
                @change=${this.handleDatabaseTypeChange}
              >
                <option value="default">Mặc định (SQL Server từ .env)</option>
                <option value="sqlserver">SQL Server</option>
                <option value="mysql">MySQL</option>
                <option value="postgresql">PostgreSQL</option>
              </select>
            </div>

            ${this.connection.type !== "default"
              ? html`
                  <div class="form-group">
                    <label class="form-label">Host *</label>
                    <input
                      class="form-input"
                      type="text"
                      .value=${this.connection.host}
                      @input=${(e: Event) => this.handleInputChange("host", e)}
                      placeholder="localhost"
                    />
                  </div>

                  <div class="form-group">
                    <label class="form-label">Port *</label>
                    <input
                      class="form-input"
                      type="number"
                      .value=${this.connection.port}
                      @input=${(e: Event) => this.handleInputChange("port", e)}
                      placeholder="1433"
                    />
                  </div>

                  <div class="form-group">
                    <label class="form-label">Database *</label>
                    <input
                      class="form-input"
                      type="text"
                      .value=${this.connection.database}
                      @input=${(e: Event) => this.handleInputChange("database", e)}
                      placeholder="database_name"
                    />
                  </div>

                  <div class="form-group">
                    <label class="form-label">Username</label>
                    <input
                      class="form-input"
                      type="text"
                      .value=${this.connection.username}
                      @input=${(e: Event) => this.handleInputChange("username", e)}
                      placeholder="username"
                    />
                  </div>

                  <div class="form-group">
                    <label class="form-label">Password</label>
                    <input
                      class="form-input"
                      type="password"
                      .value=${this.connection.password}
                      @input=${(e: Event) => this.handleInputChange("password", e)}
                      placeholder="password"
                    />
                  </div>
                `
              : html`
                  <div class="status-message info">
                    Sử dụng kết nối mặc định từ file .env (SQL Server)
                  </div>
                `}

            <div class="form-actions">
              <button
                class="form-button secondary"
                @click=${this.close}
                ?disabled=${this.testing}
              >
                Hủy
              </button>
              <button
                class="form-button primary"
                @click=${this.testConnection}
                ?disabled=${this.testing || (this.connection.type !== "default" && (!this.connection.host || !this.connection.database))}
              >
                ${this.testing ? html`<span class="loading"></span>` : ""}
                Kiểm tra kết nối
              </button>
              <button
                class="form-button primary"
                @click=${this.saveConnection}
                ?disabled=${this.testing || (this.connection.type !== "default" && (!this.connection.host || !this.connection.database))}
              >
                Lưu
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
}

