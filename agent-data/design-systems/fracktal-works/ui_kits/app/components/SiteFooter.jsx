/* ===========================================================================
   COMPONENT: SiteFooter  (window.SiteFooter)
   REGIONS 5 + 6 — Red CTA banner ("Built in Bangalore. From the ground up.")
   followed by the dark footer band (#111111 via var(--canvas-dark)). Sourced
   from region-cta-banner + region-footer. Light wordmark on the near-black band,
   nav columns, and measured contact (+91 94296 91256, info@fracktal.in,
   www.fracktal.in). Posture: FLAT, ROUNDED (var(--radius)), 1px rules; the full
   red band is the single-accent statement surface. Lucide icons: phone, mail,
   arrow-right via inline-SVG window.Icon; globe via CDN Lucide (outside the
   inline Icon set). All color/type/spacing comes from tokens.
   =========================================================================== */
function SiteFooter() {
  const { Icon } = window;

  // The globe glyph on the website line is outside the inline window.Icon set, so
  // it still renders via the CDN Lucide pass.
  React.useEffect(() => { if (window.lucide) window.lucide.createIcons(); }, []);

  const productLinks = ['Snowflake', 'Julia', 'Twin Dragon', 'Volterra', 'Apollo 350', 'PrintStick'];
  const companyLinks = ['Manufacturing Services', 'Industries', 'Materials', 'Resources'];

  const colHead = {
    margin: '0 0 var(--space-4)', fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-strong)',
    fontSize: 'var(--fs-overline)', letterSpacing: 'var(--tracking-overline)', textTransform: 'uppercase',
    color: 'var(--ink-on-dark)',
  };
  const colLink = { display: 'block', fontSize: 'var(--fs-sm)', color: 'var(--ink-on-dark-muted)', padding: '5px 0' };
  const contactLink = { display: 'flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: 'var(--fs-sm)', color: 'var(--ink-on-dark-muted)', padding: '5px 0' };
  // Size comes from the <Icon size> prop; this only carries the accent color +
  // no-shrink so a contact icon keeps its box. (width/height live on the SVG
  // attributes via the size prop, so they are intentionally not set here.)
  const contactIcon = { flex: '0 0 auto', color: 'var(--accent)' };
  // The CDN-Lucide globe glyph still needs explicit pixel sizing on its <i>.
  const cdnContactIcon = { width: '16px', height: '16px', flex: '0 0 auto', color: 'var(--accent)' };

  return (
    <React.Fragment>
      {/* REGION 5 — RED CTA BANNER */}
      <section data-od-id="region-cta-banner" id="cta" style={{ background: 'var(--accent)', color: 'var(--on-accent)' }}>
        <div className="fk-wrap">
          <div className="fk-cta-inner" style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-6)',
            padding: 'var(--space-7) 0', flexWrap: 'wrap',
          }}>
            <div>
              <h2 style={{ margin: 0, fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-bold)', fontSize: 'var(--fs-h1)', lineHeight: 'var(--lh-tight)', color: 'var(--on-accent)', letterSpacing: 'var(--tracking-tight)' }}>
                Built in Bangalore. From the ground up.
              </h2>
              <p style={{ margin: 'var(--space-2) 0 0', color: 'var(--on-accent)', opacity: 0.92, maxWidth: '52ch' }}>
                Every machine is designed, engineered, and assembled in-house. Talk to the team that builds them.
              </p>
            </div>
            <a
              className="fk-btn"
              href="#top"
              style={{
                background: 'var(--canvas)', color: 'var(--accent-strong)',
                border: 'var(--border-width) solid var(--canvas)',
                textTransform: 'uppercase', letterSpacing: '0.04em',
              }}
            >
              Buy Now
              <Icon name="arrow-right" aria-hidden="true" />
            </a>
          </div>
        </div>
      </section>

      {/* REGION 6 — DARK FOOTER BAND (#111111) */}
      <footer data-od-id="region-footer" style={{ background: 'var(--canvas-dark)', color: 'var(--ink-on-dark-muted)' }}>
        <div className="fk-wrap">
          <div className="fk-footer-grid" style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr 1fr', gap: 'var(--space-7)', padding: 'var(--space-8) 0 var(--space-6)' }}>
            <div>
              {/* Light logo: white wordmark reads on the near-black band */}
              <img src="../../logos/Websitesd-Header.png" alt="Fracktal Works" style={{ height: '40px', width: 'auto', marginBottom: 'var(--space-4)', display: 'block' }} />
              <p style={{ fontSize: 'var(--fs-sm)', maxWidth: '34ch', color: 'var(--ink-on-dark-muted)' }}>
                India's premier 3D printer manufacturer. An Original Additive Manufacturer based in Bangalore since 2013.
              </p>
            </div>

            <div>
              <h3 style={colHead}>Products</h3>
              {productLinks.map((l) => (<a key={l} href="#products" style={colLink}>{l}</a>))}
            </div>

            <div>
              <h3 style={colHead}>Company</h3>
              {companyLinks.map((l) => (<a key={l} href="#products" style={colLink}>{l}</a>))}
            </div>

            <div>
              <h3 style={colHead}>Contact</h3>
              <a href="tel:+919429691256" style={{ ...contactLink, fontFamily: 'var(--ff-mono)' }}><Icon name="phone" size={14} aria-hidden="true" style={contactIcon} />+91 94296 91256</a>
              <a href="mailto:info@fracktal.in" style={contactLink}><Icon name="mail" size={14} aria-hidden="true" style={contactIcon} />info@fracktal.in</a>
              <a href="https://www.fracktal.in" target="_blank" rel="noopener" style={contactLink}><i data-lucide="globe" aria-hidden="true" style={cdnContactIcon}></i>www.fracktal.in</a>
              <span style={colLink}>Bangalore, India</span>
            </div>
          </div>

          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-4)',
            flexWrap: 'wrap', padding: 'var(--space-4) 0',
            borderTop: 'var(--border-width) solid #2a2a2a', /* region-label: near-black band edge, not a brand color */
            fontSize: 'var(--fs-caption)', color: 'var(--ink-subtle)',
          }}>
            <span>© 2013–2026 Fracktal Works. <span style={{ color: 'var(--accent)' }}>Make in India.</span></span>
            <span style={{ fontFamily: 'var(--ff-mono)' }}>OAM · Bangalore · Since 2013</span>
          </div>
        </div>
      </footer>
    </React.Fragment>
  );
}

window.SiteFooter = SiteFooter;
