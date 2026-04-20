---
description: Defines the mandated visual architecture and styling philosophies for external-facing React interfaces.
glob: "ngs-variant-ui/**/*.tsx, *.css"
---

# React Glassmorphism Architecture

1. **Visual Language Requirements**: The application demands stunning, premium UI execution. You must leverage the "Vanilla CSS Glassmorphism" layout architecture implemented during Phase 6 and 14. 
2. **Component Rules**: Avoid heavy, monolithic external UI component libraries (like bloated charting tools). Utilize zero-dependency HTML/SVG rendering stacks for complex FinOps visualizations to retain microscopic load times.
3. **Aesthetics**: Implement deep, vibrant color schemas with dynamic pseudo-class micro-animations (`:hover`, `:active`) to enforce a responsive, "alive" physical presence to the clinical dashboards. Use standard CSS Variables for tokenizing the theme.
