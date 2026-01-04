import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { vannaDesignTokens } from "../styles/vanna-design-tokens.js";
import { VannaApiClient, TrainingData, TrainingDataRequest } from "../services/api-client.js";

@customElement("training-data-manager")
export class TrainingDataManager extends LitElement {
  static styles = [
    vannaDesignTokens,
    css`
      :host {
        display: block;
        overflow-x: hidden;
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
        max-width: 900px;
        max-height: 90vh;
        display: flex;
        flex-direction: column;
        animation: slideUp 0.3s ease;
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

      .tabs {
        display: flex;
        border-bottom: 1px solid var(--vanna-outline-default);
        padding: 0 var(--vanna-space-6);
        flex-shrink: 0;
      }

      .tab {
        padding: var(--vanna-space-4) var(--vanna-space-6);
        background: none;
        border: none;
        border-bottom: 2px solid transparent;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: var(--vanna-foreground-dimmer);
        transition: all var(--vanna-duration-200) ease;
        position: relative;
        top: 1px;
      }

      .tab:hover {
        color: var(--vanna-foreground-default);
        background: var(--vanna-background-higher);
      }

      .tab.active {
        color: var(--vanna-navy);
        border-bottom-color: var(--vanna-navy);
      }

      .modal-content {
        flex: 1;
        overflow-y: auto;
        padding: var(--vanna-space-6);
      }

      .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--vanna-space-4);
      }

      .add-button {
        padding: var(--vanna-space-2) var(--vanna-space-4);
        background: var(--vanna-navy);
        color: white;
        border: none;
        border-radius: var(--vanna-border-radius-md);
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
      }

      .add-button:hover {
        background: var(--vanna-accent-primary-stronger);
        box-shadow: var(--vanna-shadow-sm);
      }

      .training-list {
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-3);
      }

      .training-item {
        border: 1px solid var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-lg);
        padding: var(--vanna-space-4);
        background: var(--vanna-background-default);
        transition: all var(--vanna-duration-200) ease;
      }

      .training-item:hover {
        border-color: var(--vanna-navy);
        box-shadow: var(--vanna-shadow-sm);
      }

      .training-item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: var(--vanna-space-3);
      }

      .training-item-text {
        font-weight: 500;
        color: var(--vanna-foreground-default);
        margin: 0 0 var(--vanna-space-2) 0;
        flex: 1;
        white-space: pre-wrap;
        word-wrap: break-word;
        text-align: left;
      }
      
      .training-item-text::first-line {
        text-indent: 0;
      }

      .training-item-actions {
        display: flex;
        gap: var(--vanna-space-2);
      }

      .action-button {
        padding: var(--vanna-space-1) var(--vanna-space-3);
        background: none;
        border: 1px solid var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-md);
        font-size: 12px;
        cursor: pointer;
        transition: all var(--vanna-duration-200) ease;
        color: var(--vanna-foreground-dimmer);
      }

      .action-button:hover {
        border-color: var(--vanna-navy);
        color: var(--vanna-navy);
      }

      .action-button.delete:hover {
        border-color: #ef4444;
        color: #ef4444;
      }

      .training-item-content {
        color: var(--vanna-foreground-dimmer);
        font-size: 13px;
        line-height: 1.5;
      }

      .training-item-content p {
        margin: var(--vanna-space-2) 0;
      }

      .training-item-content code {
        background: var(--vanna-background-higher);
        padding: 2px 6px;
        border-radius: var(--vanna-border-radius-sm);
        font-family: monospace;
        font-size: 12px;
      }

      .form-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
        animation: fadeIn 0.2s ease;
        overflow-x: hidden;
        overflow-y: auto;
      }

      .form-modal {
        background: white;
        border-radius: var(--vanna-border-radius-xl);
        box-shadow: var(--vanna-shadow-2xl);
        width: calc(90% - 2 * var(--vanna-space-4));
        max-width: 600px;
        padding: var(--vanna-space-6);
        max-height: calc(90vh - 2 * var(--vanna-space-4));
        overflow-x: hidden;
        overflow-y: auto;
        animation: slideUp 0.3s ease;
        position: relative;
        box-sizing: border-box;
        margin: var(--vanna-space-4);
      }
      
      .form-modal::-webkit-scrollbar {
        width: 8px;
      }
      
      .form-modal::-webkit-scrollbar-track {
        background: var(--vanna-background-default);
        border-radius: 4px;
      }
      
      .form-modal::-webkit-scrollbar-thumb {
        background: var(--vanna-outline-default);
        border-radius: 4px;
      }
      
      .form-modal::-webkit-scrollbar-thumb:hover {
        background: var(--vanna-foreground-dimmer);
      }

      .form-title {
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 var(--vanna-space-4) 0;
      }

      .form-group {
        margin-bottom: var(--vanna-space-4);
        width: 100%;
        box-sizing: border-box;
      }

      .form-label {
        display: block;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: var(--vanna-space-2);
        color: var(--vanna-foreground-default);
      }

      .form-input,
      .form-textarea {
        width: 100%;
        padding: var(--vanna-space-3);
        border: 1px solid var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-md);
        font-size: 14px;
        font-family: inherit;
        transition: all var(--vanna-duration-200) ease;
        box-sizing: border-box;
        overflow-x: hidden;
      }

      .form-input:focus,
      .form-textarea:focus {
        outline: none;
        border-color: var(--vanna-navy);
        box-shadow: 0 0 0 3px rgba(47, 110, 255, 0.1);
      }

      .form-textarea {
        min-height: 100px;
        resize: vertical;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: pre-wrap;
      }

      .form-actions {
        display: flex;
        gap: var(--vanna-space-3);
        justify-content: flex-end;
        margin-top: var(--vanna-space-6);
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

      .form-button.primary:hover {
        background: var(--vanna-accent-primary-stronger);
      }

      .form-button.secondary {
        background: var(--vanna-background-higher);
        color: var(--vanna-foreground-default);
      }

      .form-button.secondary:hover {
        background: var(--vanna-background-highest);
      }

      .empty-state {
        text-align: center;
        padding: var(--vanna-space-10);
        color: var(--vanna-foreground-dimmer);
      }

      .loading {
        text-align: center;
        padding: var(--vanna-space-10);
        color: var(--vanna-foreground-dimmer);
      }
    `,
  ];

  @state() private isOpen = false;
  @state() private activeTab: "default" | "from_chat" = "default";
  @state() private trainingData: TrainingData[] = [];
  @state() private loading = false;
  @state() private showForm = false;
  @state() private editingItem: TrainingData | null = null;
  @state() private formData: TrainingDataRequest = {
    text: "",
    data_type: "default",
  };

  private apiClient: VannaApiClient = new VannaApiClient();

  connectedCallback() {
    super.connectedCallback();
    // Get baseUrl from vanna-chat component if available
    const vannaChat = document.querySelector("vanna-chat");
    if (vannaChat) {
      const baseUrl = vannaChat.getAttribute("api-base") || "";
      this.apiClient = new VannaApiClient({ baseUrl });
    }
    // Listen for open event
    window.addEventListener("open-training-data-manager", () => {
      this.open();
    });
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    window.removeEventListener("open-training-data-manager", () => {});
  }

  open() {
    this.isOpen = true;
    this.loadTrainingData();
  }

  close() {
    this.isOpen = false;
    this.showForm = false;
    this.editingItem = null;
    this.resetForm();
  }

  async loadTrainingData() {
    this.loading = true;
    try {
      const response = await this.apiClient.listTrainingData(
        this.activeTab,
        100,
        0
      );
      this.trainingData = response.training_data;
    } catch (error) {
      console.error("Failed to load training data:", error);
      this.trainingData = [];
    } finally {
      this.loading = false;
    }
  }

  async switchTab(tab: "default" | "from_chat") {
    this.activeTab = tab;
    await this.loadTrainingData();
  }

  openAddForm = () => {
    this.editingItem = null;
    this.formData = {
      text: "",
      data_type: this.activeTab,
    };
    this.showForm = true;
    this.requestUpdate(); // Force update to show form
  }

  openEditForm(item: TrainingData) {
    this.editingItem = item;
    this.formData = {
      text: item.text,
      data_type: item.data_type,
    };
    this.showForm = true;
  }

  resetForm() {
    this.formData = {
      text: "",
      data_type: "default",
    };
  }

  saveTrainingData = async () => {
    try {
      
      if (!this.formData.text.trim()) {
        alert("Vui lòng nhập nội dung training data");
        return;
      }
      
      if (this.editingItem) {
        await this.apiClient.updateTrainingData(
          this.editingItem.id,
          this.formData
        );
      } else {
        await this.apiClient.createTrainingData(this.formData);
      }
      
      this.showForm = false;
      this.editingItem = null;
      this.resetForm();
      await this.loadTrainingData();
    } catch (error) {
      console.error("Failed to save training data:", error);
      alert(`Lỗi khi lưu training data: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async deleteTrainingData(id: string) {
    if (!confirm("Are you sure you want to delete this training data?")) {
      return;
    }

    try {
      await this.apiClient.deleteTrainingData(id);
      await this.loadTrainingData();
    } catch (error) {
      console.error("Failed to delete training data:", error);
      alert("Failed to delete training data. Please try again.");
    }
  }

  render() {
    if (!this.isOpen) {
      return html``;
    }

    return html`
      <div class="modal-overlay" @click=${(e: Event) => {
        if (e.target === e.currentTarget) {
          this.close();
        }
      }}>
        <div class="modal" @click=${(e: Event) => e.stopPropagation()}>
          <div class="modal-header">
            <h2 class="modal-title">Quản lý Training Data</h2>
            <button class="close-button" @click=${this.close}>×</button>
          </div>

          <div class="tabs">
            <button
              class="tab ${this.activeTab === "default" ? "active" : ""}"
              @click=${() => this.switchTab("default")}
            >
              Dữ liệu mặc định
            </button>
            <button
              class="tab ${this.activeTab === "from_chat" ? "active" : ""}"
              @click=${() => this.switchTab("from_chat")}
            >
              Dữ liệu từ chat
            </button>
          </div>

          <div class="modal-content">
            <div class="toolbar">
              <div></div>
              <button class="add-button" @click=${() => this.openAddForm()}>
                + Thêm mới
              </button>
            </div>

            ${this.loading
              ? html`<div class="loading">Đang tải...</div>`
              : this.trainingData.length === 0
              ? html`<div class="empty-state">Không có dữ liệu</div>`
              : html`
                  <div class="training-list">
                    ${this.trainingData.map(
                      (item) => html`
                        <div class="training-item">
                          <div class="training-item-header">
                            <div style="flex: 1">
                              <div class="training-item-text">
                                ${item.text.trimStart()}
                              </div>
                            </div>
                            <div class="training-item-actions">
                              <button
                                class="action-button"
                                @click=${() => this.openEditForm(item)}
                              >
                                Sửa
                              </button>
                              <button
                                class="action-button delete"
                                @click=${() => this.deleteTrainingData(item.id)}
                              >
                                Xóa
                              </button>
                            </div>
                          </div>
                        </div>
                      `
                    )}
                  </div>
                `}
          </div>
        </div>
      </div>

      ${this.showForm
        ? html`
            <div
              class="form-overlay"
              @click=${(e: Event) => {
                if (e.target === e.currentTarget) {
                  this.showForm = false;
                  this.editingItem = null;
                  this.resetForm();
                }
              }}
            >
              <div class="form-modal" @click=${(e: Event) => e.stopPropagation()}>
                <h3 class="form-title">
                  ${this.editingItem ? "Sửa Training Data" : "Thêm Training Data"}
                </h3>

                <div class="form-group">
                  <label class="form-label">Nội dung *</label>
                  <textarea
                    class="form-textarea"
                    .value=${this.formData.text}
                    @input=${(e: Event) => {
                      this.formData.text = (e.target as HTMLTextAreaElement).value;
                      this.requestUpdate(); // Force update to enable/disable button
                    }}
                    placeholder="Nhập nội dung training data..."
                    style="min-height: 200px;"
                  ></textarea>
                </div>

                <div class="form-actions">
                  <button
                    class="form-button secondary"
                    @click=${() => {
                      this.showForm = false;
                      this.editingItem = null;
                      this.resetForm();
                    }}
                  >
                    Hủy
                  </button>
                  <button
                    class="form-button primary"
                    @click=${(e: Event) => {
                      e.preventDefault();
                      e.stopPropagation();
                      if (!this.formData.text.trim()) {
                        alert('Vui lòng nhập nội dung');
                        return;
                      }
                      this.saveTrainingData();
                    }}
                    ?disabled=${!this.formData.text.trim()}
                    style=${this.formData.text.trim() ? '' : 'opacity: 0.5; cursor: not-allowed;'}
                  >
                    ${this.editingItem ? "Cập nhật" : "Thêm"}
                  </button>
                </div>
              </div>
            </div>
          `
        : ""}
    `;
  }
}

