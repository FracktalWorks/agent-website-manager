/* ===========================================================================
   COMPONENT: ProductGrid  (window.ProductGrid)
   REGION 3 — White product section, sourced from region-product-grid. Category
   filter tabs (useState: All / FDM / SLS / Services) over flat 1px cards.
   Cards use ONLY genuine product photography (cover-0.webp, hero-1.webp,
   hero-2.png, hero-3.png, hero-6.webp). hero-4/5/7 are partner/government logos
   and are deliberately NOT used here. Posture: FLAT, ROUNDED (var(--radius)), 1px
   rules; the red accent is reserved for active tab + outline hover. Lucide icons:
   arrow-right via inline-SVG window.Icon; sliders-horizontal via CDN Lucide
   (outside the inline Icon set). Tokens drive all styling.
   =========================================================================== */
function ProductGrid() {
  const { Icon } = window;
  const [filter, setFilter] = React.useState('all');

  // Re-render the CDN Lucide icons (e.g. the sliders-horizontal filter glyph,
  // which is outside the inline window.Icon set) after the filter changes — the
  // visible cards re-mount, so any remaining <i data-lucide> need converting.
  React.useEffect(() => { if (window.lucide) window.lucide.createIcons(); }, [filter]);

  const tabs = [
    ['all', 'All', 7],
    ['fdm', 'FDM', 4],
    ['sls', 'SLS', 1],
    ['services', 'Services', 2],
  ];

  const products = [
    {
      id: 'product-card-snowflake', category: 'fdm', img: '../../imagery/hero-3.png',
      alt: 'Fracktal Snowflake desktop FDM 3D printer', tag: 'FDM · Desktop', name: 'Snowflake',
      line: 'Desktop precision FDM for prototyping and the design studio.',
      specs: [['Class', 'Desktop'], ['Process', 'FDM'], ['Use', 'Prototyping']],
    },
    {
      id: 'product-card-julia', category: 'fdm', img: '../../imagery/cover-0.webp',
      alt: 'Fracktal Julia advanced industrial FDM 3D printer', tag: 'FDM · Industrial', name: 'Julia',
      line: 'Advanced industrial FDM for repeatable engineering parts.',
      specs: [['Class', 'Industrial'], ['Process', 'FDM'], ['Use', 'Production']],
    },
    {
      id: 'product-card-twin-dragon', category: 'fdm', img: '../../imagery/hero-2.png',
      alt: 'Fracktal Twin Dragon dual-extruder IDEX FDM 3D printer', tag: 'FDM · IDEX', name: 'Twin Dragon',
      line: 'Dual-extruder IDEX FDM. Large format, fast, independent heads.',
      specs: [['Volume', '600×600×400mm'], ['Speed', 'up to 500mm/sec']],
    },
    {
      id: 'product-card-volterra', category: 'fdm', img: '../../imagery/hero-6.webp',
      alt: 'Fracktal Volterra high-temperature FFF 3D printer', tag: 'FFF · High-temp', name: 'Volterra',
      line: 'High-temperature FFF for engineering polymers like PEEK and PEI.',
      specs: [['Process', 'High-temp FFF'], ['Chamber', 'Heated']],
    },
    {
      id: 'product-card-apollo-350', category: 'sls', img: '../../imagery/cover-0.webp',
      alt: 'Fracktal Apollo 350 production-grade SLS 3D printer', tag: 'SLS · Production', name: 'Apollo 350',
      line: 'Production-grade SLS. CO2 laser sintering for functional nylon parts.',
      specs: [['Process', 'SLS'], ['Source', 'CO2 laser']],
    },
    {
      id: 'product-card-printstick', category: 'services', img: '../../imagery/hero-1.webp',
      alt: 'Fracktal PrintStick 3D printing bed adhesive', tag: 'Consumable · Adhesion', name: 'PrintStick',
      line: 'Bed adhesion for PLA, PETG, ABS and TPU. Easy to clean.',
      specs: [['Volume', '100ml'], ['Width', '30mm line']],
    },
    {
      id: 'product-card-manufacturing-services', category: 'services', img: '../../imagery/hero-2.png',
      alt: 'Fracktal on-demand additive manufacturing services', tag: 'Service · On-demand', name: 'Manufacturing Services',
      line: 'On-demand FDM and SLS parts, printed in-house in Bangalore.',
      specs: [['Process', 'FDM + SLS'], ['Made in', 'Bangalore']], cta: '#cta',
    },
  ];

  const visible = products.filter((p) => filter === 'all' || p.category === filter);

  return (
    <section data-od-id="region-product-grid" id="products" style={{ padding: 'var(--section) 0', background: 'var(--canvas)' }}>
      <div className="fk-wrap">
        {/* Section header: overline + accent rule + h2 */}
        <div style={{ marginBottom: 'var(--space-7)' }}>
          <span style={{
            fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-strong)', fontSize: 'var(--fs-overline)',
            letterSpacing: 'var(--tracking-overline)', textTransform: 'uppercase', color: 'var(--ink-muted)',
          }}>The Machines</span>
          <div style={{ height: '4px', width: '64px', background: 'var(--accent)', margin: 'var(--space-3) 0 var(--space-4)' }} />
          <h2 style={{ margin: 0, fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-bold)', fontSize: 'var(--fs-h2)', lineHeight: 'var(--lh-snug)', color: 'var(--ink)', letterSpacing: 'var(--tracking-tight)' }}>
            Built for the bench and the production floor.
          </h2>
        </div>

        {/* Category filter tabs — real React state filter */}
        <div role="tablist" aria-label="Filter products by category" style={{
          display: 'flex', alignItems: 'center', gap: 0, borderBottom: 'var(--border-width) solid var(--border)',
          marginBottom: 'var(--space-6)', flexWrap: 'wrap',
        }}>
          <i data-lucide="sliders-horizontal" aria-hidden="true" style={{ width: '18px', height: '18px', color: 'var(--ink-muted)', marginRight: 'var(--space-3)' }}></i>
          {tabs.map(([key, label, count]) => {
            const active = filter === key;
            return (
              <button
                key={key}
                type="button"
                role="tab"
                aria-selected={active}
                onClick={() => setFilter(key)}
                style={{
                  background: 'transparent', border: 0,
                  borderBottom: active ? '2px solid var(--accent)' : '2px solid transparent',
                  padding: '12px 20px', cursor: 'pointer',
                  fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-strong)', fontSize: 'var(--fs-sm)',
                  letterSpacing: '0.04em', textTransform: 'uppercase',
                  color: active ? 'var(--accent)' : 'var(--ink-muted)',
                }}
              >
                {label}
                <span style={{ fontFamily: 'var(--ff-mono)', fontSize: 'var(--fs-caption)', marginLeft: '6px', color: 'var(--ink-subtle)' }}>{count}</span>
              </button>
            );
          })}
        </div>

        {/* Flat 1px product cards */}
        <div className="fk-product-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--card-gap)' }}>
          {visible.map((p) => (
            <article
              key={p.id}
              data-od-id={p.id}
              style={{
                background: 'var(--surface)', border: 'var(--border-width) solid var(--border)',
                borderRadius: 'var(--radius)', boxShadow: 'var(--shadow)',
                display: 'flex', flexDirection: 'column',
              }}
            >
              <div style={{
                background: 'var(--fill)', aspectRatio: '4 / 3', display: 'flex',
                alignItems: 'center', justifyContent: 'center',
                borderTopLeftRadius: 'var(--radius)', borderTopRightRadius: 'var(--radius)',
                borderBottom: 'var(--border-width) solid var(--border)', overflow: 'hidden',
              }}>
                <img src={p.img} alt={p.alt} style={{ width: '100%', height: '100%', objectFit: 'contain', padding: 'var(--space-4)', display: 'block' }} />
              </div>
              <div style={{ padding: 'var(--space-5)', display: 'flex', flexDirection: 'column', flex: 1 }}>
                <span style={{
                  alignSelf: 'flex-start', fontFamily: 'var(--ff-mono)', fontSize: 'var(--fs-caption)',
                  textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--ink-muted)',
                  border: 'var(--border-width) solid var(--border)', borderRadius: 'var(--radius-sm)',
                  padding: '2px 8px', marginBottom: 'var(--space-3)',
                }}>{p.tag}</span>
                <h3 style={{ margin: '0 0 4px', fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-bold)', fontSize: 'var(--fs-h4)', color: 'var(--ink)' }}>{p.name}</h3>
                <p style={{ margin: '0 0 var(--space-4)', fontSize: 'var(--fs-sm)', color: 'var(--ink-body)' }}>{p.line}</p>
                <div style={{
                  fontFamily: 'var(--ff-mono)', fontVariantNumeric: 'tabular-nums', fontSize: 'var(--fs-caption)',
                  color: 'var(--ink-muted)', borderTop: 'var(--border-width) solid var(--border)',
                  paddingTop: 'var(--space-3)', marginBottom: 'var(--space-4)',
                  display: 'flex', flexWrap: 'wrap', gap: '4px 14px',
                }}>
                  {p.specs.map(([k, v]) => (
                    <span key={k}>{k} <b style={{ color: 'var(--ink)', fontWeight: 'var(--fw-strong)' }}>{v}</b></span>
                  ))}
                </div>
                <a
                  className="fk-btn fk-btn--outline"
                  href={p.cta || '#specs'}
                  style={{ marginTop: 'auto', alignSelf: 'flex-start', textTransform: 'uppercase', letterSpacing: '0.04em', fontSize: 'var(--fs-caption)', padding: '10px 18px' }}
                >
                  Learn More
                  <Icon name="arrow-right" size={14} aria-hidden="true" />
                </a>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

window.ProductGrid = ProductGrid;
