import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { vannaDesignTokens } from '../styles/vanna-design-tokens.js';
import * as echarts from 'echarts';

// ECharts types
export interface EChartsOption {
  title?: any;
  tooltip?: any;
  legend?: any;
  grid?: any;
  xAxis?: any;
  yAxis?: any;
  series?: any[];
  color?: string[];
  backgroundColor?: string;
  textStyle?: any;
  [key: string]: any;
}

@customElement('echarts-chart')
export class EChartsChart extends LitElement {
  static styles = [
    vannaDesignTokens,
    css`
      :host {
        display: block;
        font-family: var(--vanna-font-family-default);
        width: 100%;
        height: 100%;
      }

      .echarts-container {
        width: 100%;
        min-height: 400px;
        position: relative;
      }

      .error-message {
        padding: var(--vanna-space-4);
        color: var(--vanna-accent-negative-default);
        text-align: center;
        font-style: italic;
      }

      .loading-message {
        padding: var(--vanna-space-4);
        color: var(--vanna-foreground-dimmer);
        text-align: center;
        font-style: italic;
      }
    `
  ];

  @property({ type: Object }) option: EChartsOption = {};
  @property({ type: Boolean }) loading = false;
  @property() error = '';
  @property() theme: 'light' | 'dark' = 'dark';

  private echartsInstance: any = null;
  private chartContainer?: HTMLElement;
  private resizeObserver?: ResizeObserver;

  firstUpdated() {
    try {
      this.chartContainer = this.shadowRoot?.querySelector('.echarts-container') as HTMLElement;
      
      if (this.chartContainer) {
        // Initialize ECharts instance
        this.echartsInstance = echarts.init(
          this.chartContainer,
          this.theme === 'dark' ? 'dark' : undefined,
          {
            renderer: 'svg', // Use SVG for better quality
            useDirtyRect: true // Performance optimization
          }
        );
        
        this._renderChart();
        this._setupResizeObserver();
      }
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to load ECharts';
      console.error('ECharts initialization error:', err);
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.resizeObserver?.disconnect();
    if (this.echartsInstance) {
      this.echartsInstance.dispose();
      this.echartsInstance = null;
    }
  }

  private _setupResizeObserver() {
    if (!this.chartContainer) return;

    this.resizeObserver = new ResizeObserver(() => {
      if (this.echartsInstance) {
        this.echartsInstance.resize();
      }
    });

    this.resizeObserver.observe(this.chartContainer);
  }

  updated(changedProperties: Map<string | number | symbol, unknown>) {
    if (changedProperties.has('option') || changedProperties.has('theme')) {
      this._renderChart();
    }
  }

  private async _renderChart() {
    if (!this.echartsInstance || this.loading || this.error || !this.option) {
      return;
    }

    try {
      // Apply dark theme colors if needed
      const finalOption = this._applyTheme(this.option);
      
      // Set option to ECharts instance
      this.echartsInstance.setOption(finalOption, true); // true = notMerge for complete replacement
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to render chart';
      console.error('ECharts render error:', err);
    }
  }

  private _applyTheme(option: EChartsOption): EChartsOption {
    const isDark = this.theme === 'dark';
    
    // Default dark theme colors (purple/neon theme)
    const darkColors = [
      '#BA55D3', // MediumOrchid
      '#8A2BE2', // BlueViolet
      '#FF00FF', // Magenta
      '#9370DB', // MediumPurple
      '#DA70D6', // Orchid
      '#BA55D3', // MediumOrchid
      '#8A2BE2', // BlueViolet
    ];

    const lightColors = [
      '#8A2BE2', // BlueViolet
      '#BA55D3', // MediumOrchid
      '#9370DB', // MediumPurple
      '#DA70D6', // Orchid
      '#FF00FF', // Magenta
    ];

    const mergedOption: EChartsOption = {
      ...option,
      color: option.color || (isDark ? darkColors : lightColors),
      backgroundColor: option.backgroundColor || (isDark ? 'transparent' : 'transparent'),
      textStyle: {
        color: isDark ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.9)',
        fontFamily: 'var(--vanna-font-family-default)',
        ...option.textStyle,
      },
      // Enhanced tooltip for better interactivity
      tooltip: {
        trigger: 'axis',
        backgroundColor: isDark ? 'rgba(20, 20, 30, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        borderColor: isDark ? 'rgba(186, 85, 211, 0.8)' : 'rgba(138, 43, 226, 0.8)',
        borderWidth: 2,
        textStyle: {
          color: isDark ? 'rgba(255, 255, 255, 0.95)' : 'rgba(0, 0, 0, 0.95)',
        },
        axisPointer: {
          type: 'cross',
          crossStyle: {
            color: isDark ? 'rgba(186, 85, 211, 0.8)' : 'rgba(138, 43, 226, 0.8)',
          },
        },
        ...option.tooltip,
      },
      // Enhanced legend
      legend: {
        textStyle: {
          color: isDark ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.9)',
        },
        ...option.legend,
      },
      // Enhanced grid
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
        ...option.grid,
      },
      // Enhanced xAxis
      xAxis: Array.isArray(option.xAxis) 
        ? option.xAxis.map((axis: any) => ({
            axisLine: {
              lineStyle: {
                color: isDark ? 'rgba(186, 85, 211, 0.5)' : 'rgba(138, 43, 226, 0.5)',
              },
            },
            axisLabel: {
              color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
            },
            splitLine: {
              lineStyle: {
                color: isDark ? 'rgba(186, 85, 211, 0.1)' : 'rgba(138, 43, 226, 0.1)',
              },
            },
            ...axis,
          }))
        : option.xAxis ? {
            axisLine: {
              lineStyle: {
                color: isDark ? 'rgba(186, 85, 211, 0.5)' : 'rgba(138, 43, 226, 0.5)',
              },
            },
            axisLabel: {
              color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
            },
            splitLine: {
              lineStyle: {
                color: isDark ? 'rgba(186, 85, 211, 0.1)' : 'rgba(138, 43, 226, 0.1)',
              },
            },
            ...option.xAxis,
          } : undefined,
      // Enhanced yAxis
      yAxis: Array.isArray(option.yAxis)
        ? option.yAxis.map((axis: any) => ({
            axisLine: {
              lineStyle: {
                color: isDark ? 'rgba(186, 85, 211, 0.5)' : 'rgba(138, 43, 226, 0.5)',
              },
            },
            axisLabel: {
              color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
            },
            splitLine: {
              lineStyle: {
                color: isDark ? 'rgba(186, 85, 211, 0.1)' : 'rgba(138, 43, 226, 0.1)',
              },
            },
            ...axis,
          }))
        : option.yAxis ? {
            axisLine: {
              lineStyle: {
                color: isDark ? 'rgba(186, 85, 211, 0.5)' : 'rgba(138, 43, 226, 0.5)',
              },
            },
            axisLabel: {
              color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
            },
            splitLine: {
              lineStyle: {
                color: isDark ? 'rgba(186, 85, 211, 0.1)' : 'rgba(138, 43, 226, 0.1)',
              },
            },
            ...option.yAxis,
          } : undefined,
    };

    return mergedOption;
  }

  render() {
    return html`
      ${this.loading ? html`
        <div class="loading-message">Loading chart...</div>
      ` : this.error ? html`
        <div class="error-message">Error: ${this.error}</div>
      ` : html`
        <div class="echarts-container"></div>
      `}
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'echarts-chart': EChartsChart;
  }
}

