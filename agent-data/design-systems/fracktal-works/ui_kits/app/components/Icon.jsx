/* ===========================================================================
   COMPONENT: Icon  (window.Icon)
   Inline-SVG Lucide icons rendered as host-React (window.React via JSX)
   components. No external icon dependency, no esm.sh / lucide-react / import
   maps — those would pull a second React and crash on the dual-React mismatch.
   Every icon is the exact Lucide path data, written as JSX with camelCase attrs.

   Usage (inside a component render body only):
     const { Icon } = window;
     <Icon name="arrow-right" />
     <Icon name="chevron-down" size={14} />

   Props: name (required), size = 16, strokeWidth = 2, style, ...rest.
   Sizing/stroke/linecap mirror Lucide's defaults; color is currentColor so an
   icon inherits the surrounding text color (and the .fk-btn helper supplies the
   inline-flex gap, so a leading/trailing icon sits beside its label).
   =========================================================================== */
function Icon({ name, size = 16, strokeWidth = 2, style, ...rest }) {
  const PATHS = {
    menu: (
      <React.Fragment>
        <path d="M4 12h16" />
        <path d="M4 6h16" />
        <path d="M4 18h16" />
      </React.Fragment>
    ),
    x: (
      <React.Fragment>
        <path d="M18 6 6 18" />
        <path d="m6 6 12 12" />
      </React.Fragment>
    ),
    'chevron-down': <path d="m6 9 6 6 6-6" />,
    'shopping-cart': (
      <React.Fragment>
        <circle cx="8" cy="21" r="1" />
        <circle cx="19" cy="21" r="1" />
        <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
      </React.Fragment>
    ),
    'arrow-right': (
      <React.Fragment>
        <path d="M5 12h14" />
        <path d="m12 5 7 7-7 7" />
      </React.Fragment>
    ),
    download: (
      <React.Fragment>
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" x2="12" y1="15" y2="3" />
      </React.Fragment>
    ),
    'file-text': (
      <React.Fragment>
        <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
        <path d="M14 2v4a2 2 0 0 0 2 2h4" />
        <path d="M16 13H8" />
        <path d="M16 17H8" />
        <path d="M10 9H8" />
      </React.Fragment>
    ),
    check: <path d="M20 6 9 17l-5-5" />,
    phone: (
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
    ),
    mail: (
      <React.Fragment>
        <rect width="20" height="16" x="2" y="4" rx="2" />
        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
      </React.Fragment>
    ),
    'circle-check': (
      <React.Fragment>
        <circle cx="12" cy="12" r="10" />
        <path d="m9 12 2 2 4-4" />
      </React.Fragment>
    ),
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={style}
      {...rest}
    >
      {PATHS[name]}
    </svg>
  );
}

window.Icon = Icon;
