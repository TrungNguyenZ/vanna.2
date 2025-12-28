import { css } from 'lit';

// Vanna 2.0 design tokens - Professional Navy/Azure Theme
export const vannaDesignTokens = css`
  :host {
    /* Professional Brand Colors - Navy/Azure */
    --vanna-navy: rgb(0, 51, 102); /* #003366 */
    --vanna-navy-dark: rgb(15, 23, 42); /* #0F172A */
    --vanna-navy-light: rgb(22, 32, 51); /* #162033 */
    --vanna-azure: rgb(47, 110, 255); /* #2F6EFF */
    --vanna-azure-light: rgb(229, 241, 255); /* #E5F1FF */
    --vanna-azure-hover: rgb(0, 212, 255); /* #00D4FF */

    /* Color Palette - Light Professional Theme */
    --vanna-background-root: rgb(247, 249, 251); /* #F7F9FB */
    --vanna-background-default: rgb(255, 255, 255);
    --vanna-background-higher: rgb(255, 255, 255);
    --vanna-background-highest: rgb(255, 255, 255);
    --vanna-background-subtle: rgb(247, 249, 251);
    --vanna-background-lower: rgb(240, 244, 248);

    --vanna-foreground-default: rgb(26, 26, 26); /* #1A1A1A */
    --vanna-foreground-dimmer: rgb(93, 107, 130); /* #5D6B82 */
    --vanna-foreground-dimmest: rgb(154, 166, 184); /* #9AA6B8 */

    /* Azure Accent Colors */
    --vanna-accent-primary-default: rgb(47, 110, 255); /* #2F6EFF */
    --vanna-accent-primary-stronger: rgb(0, 212, 255); /* #00D4FF */
    --vanna-accent-primary-strongest: rgb(90, 141, 255); /* #5A8DFF */
    --vanna-accent-primary-subtle: rgba(47, 110, 255, 0.1);
    --vanna-accent-primary-hover: rgb(0, 212, 255);

    --vanna-accent-positive-default: rgb(71, 201, 126); /* #47C97E */
    --vanna-accent-positive-stronger: rgb(100, 220, 150);
    --vanna-accent-positive-subtle: rgba(71, 201, 126, 0.1);

    --vanna-accent-negative-default: rgb(255, 107, 107); /* #FF6B6B */
    --vanna-accent-negative-stronger: rgb(255, 130, 130);
    --vanna-accent-negative-subtle: rgba(255, 107, 107, 0.1);

    --vanna-accent-warning-default: rgb(255, 184, 107); /* #FFB86B */
    --vanna-accent-warning-stronger: rgb(255, 200, 130);
    --vanna-accent-warning-subtle: rgba(255, 184, 107, 0.1);

    /* Outline/Border colors - Soft Professional */
    --vanna-outline-default: rgb(225, 230, 238); /* #E1E6EE */
    --vanna-outline-dimmer: rgb(215, 222, 230); /* #D7DEE6 */
    --vanna-outline-dimmest: rgb(240, 244, 248);
    --vanna-outline-hover: rgb(47, 110, 255);

    /* Typography - Professional Fonts */
    --vanna-font-family-default: "Inter", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --vanna-font-family-serif: "Inter", ui-serif, Georgia, serif;
    --vanna-font-family-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, "SF Mono", Monaco, Inconsolata, "Roboto Mono", monospace;
    
    /* Subtle Text Effects */
    --vanna-text-glow: none;
    --vanna-text-glow-strong: none;

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

  /* Dark theme - Navy Dark Professional */
  :host([theme="dark"]) {
    --vanna-background-root: rgb(15, 23, 42); /* #0F172A */
    --vanna-background-default: rgb(22, 32, 51); /* #162033 */
    --vanna-background-higher: rgb(30, 42, 65);
    --vanna-background-highest: rgb(40, 55, 85);
    --vanna-background-subtle: rgb(18, 28, 45);
    --vanna-background-lower: rgb(10, 18, 30);

    --vanna-foreground-default: rgb(255, 255, 255);
    --vanna-foreground-dimmer: rgb(200, 210, 225);
    --vanna-foreground-dimmest: rgb(150, 165, 185);

    --vanna-accent-primary-default: rgb(47, 110, 255); /* #2F6EFF */
    --vanna-accent-primary-stronger: rgb(0, 212, 255); /* #00D4FF */
    --vanna-accent-primary-strongest: rgb(90, 141, 255);
    --vanna-accent-primary-subtle: rgba(47, 110, 255, 0.15);
    --vanna-accent-primary-hover: rgb(0, 212, 255);

    --vanna-accent-positive-default: rgb(71, 201, 126);
    --vanna-accent-positive-stronger: rgb(100, 220, 150);
    --vanna-accent-positive-subtle: rgba(71, 201, 126, 0.15);

    --vanna-accent-negative-default: rgb(255, 107, 107);
    --vanna-accent-negative-stronger: rgb(255, 130, 130);
    --vanna-accent-negative-subtle: rgba(255, 107, 107, 0.15);

    --vanna-accent-warning-default: rgb(255, 184, 107);
    --vanna-accent-warning-stronger: rgb(255, 200, 130);
    --vanna-accent-warning-subtle: rgba(255, 184, 107, 0.15);

    --vanna-outline-default: rgba(225, 230, 238, 0.2);
    --vanna-outline-dimmer: rgba(225, 230, 238, 0.15);
    --vanna-outline-dimmest: rgba(225, 230, 238, 0.1);
    --vanna-outline-hover: rgb(47, 110, 255);

    /* Professional Shadows */
    --vanna-shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
    --vanna-shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.15), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    --vanna-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.15);
    --vanna-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.25), 0 4px 6px -4px rgba(0, 0, 0, 0.2);
    --vanna-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.25);
    --vanna-shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
  }
`;
