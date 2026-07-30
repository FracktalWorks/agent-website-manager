/* ===========================================================================
   COMPONENT: SpecTable  (window.SpecTable)
   REGION 4 — Twin Dragon datasheet module, sourced from region-spec-table.
   Variants TD300 / TD500 / TD600, rendered with --ff-mono + tabular-nums so the
   numeric columns align like a real datasheet. Data is the real product brief:
     TD300  300×300×400 / 500mm·s / 1000W / 150kg
     TD500  400×400×400 / 400mm·s / 1250W / 150kg
     TD600  600×600×400 / 300mm·s / 1750W / 200kg
   Posture: FLAT, ROUNDED (var(--radius)), 1px rules; the accent only appears on
   row hover tint. Lucide icon (gauge) in the section title. All color/type/
   spacing comes from colors_and_type.css tokens.
   =========================================================================== */
function SpecTable() {
  React.useEffect(() => { if (window.lucide) window.lucide.createIcons(); }, []);

  const columns = ['Variant', 'Build volume (mm)', 'Max speed', 'Power', 'Weight'];
  const rows = [
    ['TD300', '300 × 300 × 400', '500 mm/s', '1000 W', '150 kg'],
    ['TD500', '400 × 400 × 400', '400 mm/s', '1250 W', '150 kg'],
    ['TD600', '600 × 600 × 400', '300 mm/s', '1750 W', '200 kg'],
  ];

  const thHead = {
    fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-strong)', fontSize: 'var(--fs-caption)',
    textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--ink)', background: 'var(--fill)',
    padding: '14px var(--space-5)', textAlign: 'left', borderBottom: 'var(--border-width) solid var(--border)',
  };
  const thRow = {
    fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-bold)', color: 'var(--ink)', whiteSpace: 'nowrap',
    padding: '14px var(--space-5)', textAlign: 'left', borderBottom: 'var(--border-width) solid var(--border)',
  };
  const td = {
    fontFamily: 'var(--ff-mono)', fontVariantNumeric: 'tabular-nums', fontSize: 'var(--fs-sm)', color: 'var(--ink-body)',
    padding: '14px var(--space-5)', textAlign: 'left', borderBottom: 'var(--border-width) solid var(--border)',
  };

  return (
    <section data-od-id="region-spec-table" id="specs" style={{ padding: 'var(--section) 0', background: 'var(--bg-layout)' }}>
      <div className="fk-wrap">
        {/* Section header: overline + accent rule + h2 */}
        <div style={{ marginBottom: 'var(--space-7)' }}>
          <span style={{
            fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-strong)', fontSize: 'var(--fs-overline)',
            letterSpacing: 'var(--tracking-overline)', textTransform: 'uppercase', color: 'var(--ink-muted)',
          }}>Datasheet</span>
          <div style={{ height: '4px', width: '64px', background: 'var(--accent)', margin: 'var(--space-3) 0 var(--space-4)' }} />
          <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 'var(--space-3)', fontFamily: 'var(--ff-display)', fontWeight: 'var(--fw-bold)', fontSize: 'var(--fs-h2)', lineHeight: 'var(--lh-snug)', color: 'var(--ink)', letterSpacing: 'var(--tracking-tight)' }}>
            <i data-lucide="gauge" aria-hidden="true" style={{ width: '18px', height: '18px', color: 'var(--accent)' }}></i>
            Twin Dragon series specifications.
          </h2>
        </div>

        <div className="fk-spec-frame" style={{ border: 'var(--border-width) solid var(--border-strong)', borderRadius: 'var(--radius)', background: 'var(--surface)', overflow: 'hidden', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '560px' }}>
            <caption style={{
              textAlign: 'left', padding: 'var(--space-4) var(--space-5)',
              fontFamily: 'var(--ff-mono)', fontSize: 'var(--fs-caption)', letterSpacing: '0.06em',
              textTransform: 'uppercase', color: 'var(--ink-muted)', borderBottom: 'var(--border-width) solid var(--border)',
            }}>
              Twin Dragon — dual-extruder IDEX FDM · variants 300 / 500 / 600
            </caption>
            <thead>
              <tr>
                {columns.map((c) => (<th key={c} scope="col" style={thHead}>{c}</th>))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row[0]}>
                  <th scope="row" style={thRow}>{row[0]}</th>
                  {row.slice(1).map((cell, i) => (<td key={i} style={td}>{cell}</td>))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p style={{ marginTop: 'var(--space-4)', fontSize: 'var(--fs-caption)', color: 'var(--ink-subtle)', fontFamily: 'var(--ff-mono)' }}>
          All figures are machine-rated. Speed is the maximum traverse rate; sustained print speed depends on material and geometry.
        </p>
      </div>
    </section>
  );
}

window.SpecTable = SpecTable;
