/* ===========================================================================
   COMPONENT: TopNav  (window.TopNav)
   REGION 1 — Sticky top nav, sourced from the single-file kit's region-top-nav.
   IA measured from fracktal.in: Products · Manufacturing Services · Industries ·
   Materials · Resources. Working Products dropdown (useState), red BUY NOW CTA,
   mobile burger toggle (useState). Posture: FLAT, ROUNDED (var(--radius)), 1px
   rules, the single red accent reserved for the CTA. Lucide icons rendered as
   inline-SVG React components via window.Icon (chevron-down, shopping-cart,
   menu/x). No color is hardcoded — every value comes from colors_and_type.css
   tokens via var(--token) / .fk-* helpers.
   =========================================================================== */
function TopNav() {
  const { Icon } = window;
  const [productsOpen, setProductsOpen] = React.useState(false);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const linkStyle = {
    display: 'inline-flex', alignItems: 'center', gap: '6px',
    fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-medium)', fontSize: 'var(--fs-sm)',
    color: 'var(--ink)', padding: '8px 0', cursor: 'pointer',
    borderBottom: '2px solid transparent', background: 'none', border: 'none',
  };

  const dropdownGroups = [
    {
      label: 'FDM 3D Printers',
      items: [
        ['Snowflake', 'Desktop'],
        ['Julia', 'Industrial'],
        ['Twin Dragon', 'IDEX'],
        ['Volterra', 'High-temp'],
      ],
    },
    { label: 'SLS & Production', items: [['Apollo 350', 'SLS']] },
    { label: 'Consumables', items: [['PrintStick', 'Adhesive']] },
  ];

  const secondaryLinks = ['Manufacturing Services', 'Industries', 'Materials', 'Resources'];

  return (
    <header
      className="fk-nav"
      data-od-id="region-top-nav"
      style={{
        position: 'sticky', top: 0, zIndex: 100,
        background: 'var(--canvas)',
        borderBottom: 'var(--border-width) solid var(--border)',
      }}
    >
      <div className="fk-wrap">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)', height: '72px' }}>
          {/* Wordmark: dark logo for the light nav bar */}
          <a href="#top" aria-label="Fracktal Works — home" style={{ display: 'flex', alignItems: 'center' }}>
            <img src="../../logos/Website-Header_black.png" alt="Fracktal Works" style={{ height: '34px', width: 'auto', display: 'block' }} />
          </a>

          {/* Primary IA — collapses on mobile via the burger toggle */}
          <nav
            aria-label="Primary"
            className={mobileOpen ? 'fk-navlinks is-mobile-open' : 'fk-navlinks'}
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)', marginLeft: 'var(--space-4)' }}
          >
            {/* Products — working dropdown */}
            <div
              className="fk-navitem"
              data-od-id="nav-products-dropdown"
              style={{ position: 'relative' }}
            >
              <button
                type="button"
                aria-haspopup="true"
                aria-expanded={productsOpen}
                onClick={() => setProductsOpen((v) => !v)}
                style={{
                  ...linkStyle,
                  color: productsOpen ? 'var(--accent)' : 'var(--ink)',
                  borderBottom: productsOpen ? '2px solid var(--accent)' : '2px solid transparent',
                }}
              >
                Products
                <Icon name="chevron-down" size={14} aria-hidden="true" style={{ transform: productsOpen ? 'rotate(180deg)' : 'none', transition: 'transform var(--dur) var(--ease)' }} />
              </button>

              {productsOpen && (
                <div
                  role="menu"
                  style={{
                    position: 'absolute', top: 'calc(100% + 1px)', left: 0, minWidth: '280px',
                    background: 'var(--surface)',
                    border: 'var(--border-width) solid var(--border)',
                    borderTop: '2px solid var(--accent)',
                    borderRadius: 'var(--radius)',
                    padding: 'var(--space-4)', zIndex: 110,
                  }}
                >
                  {dropdownGroups.map((group, gi) => (
                    <div
                      key={group.label}
                      style={gi > 0 ? { marginTop: 'var(--space-3)', paddingTop: 'var(--space-3)', borderTop: 'var(--border-width) solid var(--border)' } : null}
                    >
                      <div style={{
                        fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-strong)', fontSize: 'var(--fs-overline)',
                        letterSpacing: 'var(--tracking-overline)', textTransform: 'uppercase', color: 'var(--ink-muted)',
                        marginBottom: 'var(--space-2)',
                      }}>{group.label}</div>
                      {group.items.map(([name, meta]) => (
                        <a
                          key={name}
                          href="#products"
                          role="menuitem"
                          onClick={() => setProductsOpen(false)}
                          style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 'var(--space-4)',
                            padding: '8px 4px', fontSize: 'var(--fs-sm)', color: 'var(--ink)', fontWeight: 'var(--fw-medium)',
                          }}
                        >
                          {name}
                          <span style={{ fontFamily: 'var(--ff-mono)', fontSize: 'var(--fs-caption)', color: 'var(--ink-subtle)' }}>{meta}</span>
                        </a>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {secondaryLinks.map((label) => (
              <a key={label} href="#products" style={linkStyle}>{label}</a>
            ))}
          </nav>

          <div style={{ marginLeft: 'auto' }} />

          {/* BUY NOW — the real site CTA, the only red button in the nav */}
          <a
            className="fk-btn fk-btn--primary fk-nav-cta"
            href="#cta"
            data-od-id="nav-buy-now"
            style={{ textTransform: 'uppercase', letterSpacing: '0.04em' }}
          >
            <Icon name="shopping-cart" aria-hidden="true" />
            Buy Now
          </a>

          {/* Mobile nav toggle */}
          <button
            type="button"
            className="fk-burger"
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((v) => !v)}
            style={{
              width: '40px', height: '40px',
              border: 'var(--border-width) solid var(--border-strong)', background: 'var(--canvas)',
              borderRadius: 'var(--radius)', color: 'var(--ink)',
              cursor: 'pointer', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <Icon name={mobileOpen ? 'x' : 'menu'} size={18} aria-hidden="true" />
          </button>
        </div>
      </div>
    </header>
  );
}

window.TopNav = TopNav;
