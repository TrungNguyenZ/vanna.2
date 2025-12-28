import { css } from 'lit';

// Vanna 2.0 design tokens - Neon Cyberpunk Theme (Black & Purple)
export const vannaDesignTokens = css`
  :host {
    /* Neon Cyberpunk Brand Colors */
    --vanna-navy: rgb(10, 10, 20);
    --vanna-cream: rgb(200, 180, 255);
    --vanna-teal: rgb(138, 43, 226);
    --vanna-orange: rgb(255, 0, 255);
    --vanna-magenta: rgb(186, 85, 211);

    /* Color Palette - Dark mode (default) - Neon Cyberpunk */
    --vanna-background-root: rgb(5, 5, 10);
    --vanna-background-default: rgb(10, 10, 20);
    --vanna-background-higher: rgb(15, 15, 30);
    --vanna-background-highest: rgb(20, 20, 40);
    --vanna-background-subtle: rgb(8, 8, 18);
    --vanna-background-lower: rgb(3, 3, 8);

    --vanna-foreground-default: rgb(200, 180, 255);
    --vanna-foreground-dimmer: rgb(150, 130, 220);
    --vanna-foreground-dimmest: rgb(120, 100, 200);

    /* Neon Purple Accent Colors */
    --vanna-accent-primary-default: rgb(138, 43, 226);
    --vanna-accent-primary-stronger: rgb(186, 85, 211);
    --vanna-accent-primary-strongest: rgb(255, 0, 255);
    --vanna-accent-primary-subtle: rgba(138, 43, 226, 0.2);
    --vanna-accent-primary-hover: rgb(186, 85, 211);

    --vanna-accent-positive-default: rgb(0, 255, 150);
    --vanna-accent-positive-stronger: rgb(0, 255, 200);
    --vanna-accent-positive-subtle: rgba(0, 255, 150, 0.2);

    --vanna-accent-negative-default: rgb(255, 0, 100);
    --vanna-accent-negative-stronger: rgb(255, 50, 150);
    --vanna-accent-negative-subtle: rgba(255, 0, 100, 0.2);

    --vanna-accent-warning-default: rgb(255, 200, 0);
    --vanna-accent-warning-stronger: rgb(255, 255, 0);
    --vanna-accent-warning-subtle: rgba(255, 200, 0, 0.2);

    /* Outline/Border colors - Neon Glow */
    --vanna-outline-default: rgba(138, 43, 226, 0.5);
    --vanna-outline-dimmer: rgba(138, 43, 226, 0.3);
    --vanna-outline-dimmest: rgba(138, 43, 226, 0.15);
    --vanna-outline-hover: rgb(186, 85, 211);

    /* Typography - Futuristic Fonts */
    --vanna-font-family-default: "Orbitron", "Rajdhani", "Exo 2", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --vanna-font-family-serif: "Orbitron", ui-serif, Georgia, serif;
    --vanna-font-family-mono: "Fira Code", "JetBrains Mono", "Space Mono", ui-monospace, SFMono-Regular, "SF Mono", Monaco, Inconsolata, "Roboto Mono", monospace;
    
    /* Neon Text Effects */
    --vanna-text-glow: 0 0 10px rgba(138, 43, 226, 0.8), 0 0 20px rgba(138, 43, 226, 0.6), 0 0 30px rgba(186, 85, 211, 0.4);
    --vanna-text-glow-strong: 0 0 15px rgba(186, 85, 211, 1), 0 0 30px rgba(186, 85, 211, 0.8), 0 0 45px rgba(255, 0, 255, 0.6);

    /* Spacing scale */
    --vanna-space-0: 0px;
    --vanna-space-1: 4px;
    --vanna-space-2: 8px;
    --vanna-space-3: 12px;
    --vanna-space-4: 16px;
    --vanna-space-5: 20px;
    --vanna-space-6: 24px;
    --vanna-space-7: 28px;
    --vanna-space-8: 32px;
    --vanna-space-10: 40px;
    --vanna-space-12: 48px;
    --vanna-space-16: 64px;

    /* Border radius */
    --vanna-border-radius-sm: 6px;
    --vanna-border-radius-md: 10px;
    --vanna-border-radius-lg: 14px;
    --vanna-border-radius-xl: 20px;
    --vanna-border-radius-2xl: 24px;
    --vanna-border-radius-full: 9999px;

    /* Shadows - Preline-inspired */
    --vanna-shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --vanna-shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    --vanna-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    --vanna-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    --vanna-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    --vanna-shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

    /* Animation durations */
    --vanna-duration-75: 75ms;
    --vanna-duration-100: 100ms;
    --vanna-duration-150: 150ms;
    --vanna-duration-200: 200ms;
    --vanna-duration-300: 300ms;
    --vanna-duration-500: 500ms;
    --vanna-duration-700: 700ms;

    /* Z-index scale */
    --vanna-z-dropdown: 1000;
    --vanna-z-sticky: 1020;
    --vanna-z-fixed: 1030;
    --vanna-z-modal: 1040;
    --vanna-z-popover: 1050;
    --vanna-z-tooltip: 1060;

    /* Chat-specific tokens */
    --vanna-chat-bubble-radius: 18px;
    --vanna-chat-bubble-radius-sm: 12px;
    --vanna-chat-spacing: 16px;
    --vanna-chat-avatar-size: 40px;
  }

  /* Dark theme - Enhanced Neon (same as default for consistency) */
  :host([theme="dark"]) {
    --vanna-background-root: rgb(5, 5, 10);
    --vanna-background-default: rgb(10, 10, 20);
    --vanna-background-higher: rgb(15, 15, 30);
    --vanna-background-highest: rgb(20, 20, 40);
    --vanna-background-subtle: rgb(8, 8, 18);
    --vanna-background-lower: rgb(3, 3, 8);

    --vanna-foreground-default: rgb(200, 180, 255);
    --vanna-foreground-dimmer: rgb(150, 130, 220);
    --vanna-foreground-dimmest: rgb(120, 100, 200);

    --vanna-accent-primary-default: rgb(138, 43, 226);
    --vanna-accent-primary-stronger: rgb(186, 85, 211);
    --vanna-accent-primary-strongest: rgb(255, 0, 255);
    --vanna-accent-primary-subtle: rgba(138, 43, 226, 0.25);
    --vanna-accent-primary-hover: rgb(186, 85, 211);

    --vanna-accent-positive-default: rgb(0, 255, 150);
    --vanna-accent-positive-stronger: rgb(0, 255, 200);
    --vanna-accent-positive-subtle: rgba(0, 255, 150, 0.25);

    --vanna-accent-negative-default: rgb(255, 0, 100);
    --vanna-accent-negative-stronger: rgb(255, 50, 150);
    --vanna-accent-negative-subtle: rgba(255, 0, 100, 0.25);

    --vanna-accent-warning-default: rgb(255, 200, 0);
    --vanna-accent-warning-stronger: rgb(255, 255, 0);
    --vanna-accent-warning-subtle: rgba(255, 200, 0, 0.25);

    --vanna-outline-default: rgba(138, 43, 226, 0.6);
    --vanna-outline-dimmer: rgba(138, 43, 226, 0.4);
    --vanna-outline-dimmest: rgba(138, 43, 226, 0.2);
    --vanna-outline-hover: rgb(186, 85, 211);

    /* Enhanced Neon Shadows */
    --vanna-shadow-xs: 0 1px 2px 0 rgba(138, 43, 226, 0.3);
    --vanna-shadow-sm: 0 1px 3px 0 rgba(138, 43, 226, 0.4), 0 1px 2px -1px rgba(186, 85, 211, 0.3);
    --vanna-shadow-md: 0 4px 6px -1px rgba(138, 43, 226, 0.5), 0 2px 4px -2px rgba(186, 85, 211, 0.4);
    --vanna-shadow-lg: 0 10px 15px -3px rgba(138, 43, 226, 0.6), 0 4px 6px -4px rgba(186, 85, 211, 0.5);
    --vanna-shadow-xl: 0 20px 25px -5px rgba(138, 43, 226, 0.7), 0 8px 10px -6px rgba(186, 85, 211, 0.6);
    --vanna-shadow-2xl: 0 25px 50px -12px rgba(138, 43, 226, 0.8), 0 0 30px rgba(186, 85, 211, 0.5);
  }
`;
