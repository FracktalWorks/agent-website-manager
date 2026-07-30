/* ===========================================================================
   COMPONENT: Hero  (window.Hero)
   REGION 2 — Dark hero band (#111111 via var(--canvas-dark)), sourced from the
   single-file kit's region-hero. Overline · headline · one declarative subhead ·
   red + on-dark CTAs · real product photography · mono stat row.
   Posture: FLAT, ROUNDED (var(--radius)), single red accent (the rule + primary
   CTA). Lucide icons rendered as inline-SVG React components via window.Icon
   (arrow-right, file-text). All color/type/spacing comes from
   colors_and_type.css tokens — nothing hardcoded.
   =========================================================================== */
function Hero() {
  const { Icon } = window;

  const stats = [
    ['2013', 'Building in-house'],
    ['600×600×400', 'Max build (mm)'],
    ['500', 'mm/sec top speed'],
  ];

  return (
    <section
      data-od-id="region-hero"
      style={{
        background: 'var(--canvas-dark)',
        color: 'var(--ink-on-dark)',
        borderBottom: 'var(--border-width) solid #2a2a2a', /* region-label: near-black band edge, not a brand color */
      }}
    >
      <div className="fk-wrap">
        <div className="fk-hero-grid" style={{
          display: 'grid', gridTemplateColumns: '1.05fr 0.95fr', gap: 'var(--space-8)',
          alignItems: 'center', padding: 'var(--space-8) 0',
        }}>
          <div>
            <span style={{
              fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-strong)', fontSize: 'var(--fs-overline)',
              letterSpacing: 'var(--tracking-overline)', textTransform: 'uppercase', color: 'var(--ink-on-dark-muted)',
              display: 'inline-block', paddingLeft: 'var(--space-4)', borderLeft: '2px solid var(--accent)',
            }}>
              Original Additive Manufacturer · Bangalore · Since 2013
            </span>

            <h1 style={{
              margin: 'var(--space-4) 0',
              fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-bold)',
              fontSize: 'var(--fs-display)', lineHeight: 'var(--lh-tight)', letterSpacing: 'var(--tracking-tight)',
              color: 'var(--ink-on-dark)',
            }}>
              India's premier 3D printer manufacturer
            </h1>

            <p style={{ margin: '0 0 var(--space-6)', fontSize: 'var(--fs-body-lg)', color: 'var(--ink-on-dark-muted)', maxWidth: '46ch' }}>
              We design and build every machine in-house, from desktop precision to production-grade SLS.
            </p>

            <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
              <a className="fk-btn fk-btn--primary" href="#products" style={{ textTransform: 'uppercase', letterSpacing: '0.04em' }}>Explore Machines<Icon name="arrow-right" aria-hidden="true" /></a>
              <a className="fk-btn fk-btn--on-dark" href="#specs" style={{ textTransform: 'uppercase', letterSpacing: '0.04em' }}><Icon name="file-text" aria-hidden="true" />View Specifications</a>
            </div>

            <div style={{
              display: 'flex', gap: 'var(--space-7)', marginTop: 'var(--space-7)',
              paddingTop: 'var(--space-5)', borderTop: 'var(--border-width) solid #2a2a2a', /* region-label: band edge */
              flexWrap: 'wrap',
            }}>
              {stats.map(([n, l]) => (
                <div key={l}>
                  <div style={{ fontFamily: 'var(--ff-mono)', fontVariantNumeric: 'tabular-nums', fontSize: 'var(--fs-h3)', fontWeight: 'var(--fw-bold)', color: 'var(--ink-on-dark)' }}>{n}</div>
                  <div style={{ fontSize: 'var(--fs-caption)', color: 'var(--ink-on-dark-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{l}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Real product photography — the full machine family lineup */}
          <div
            data-od-id="hero-visual"
            style={{ border: 'var(--border-width) solid #2a2a2a', background: 'var(--surface-dark)', borderRadius: 'var(--radius)', overflow: 'hidden' }}
          >
            <img
              src="../../imagery/cover-0.webp"
              alt="The Fracktal Works machine family: FDM printers, Twin Dragon, Volterra and material dryer"
              style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
            />
          </div>
        </div>
      </div>
    </section>
  );
}

window.Hero = Hero;
