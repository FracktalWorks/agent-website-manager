/* ===========================================================================
   COMPONENT: App  (window.App)
   Composition root. Reads each region component off the window global it
   exposed, then renders the full applied surface in source order:
     TopNav · Hero · ProductGrid · SpecTable · SiteFooter
   (SiteFooter carries both the red CTA banner and the dark footer band.)
   No imports/exports — Babel-in-the-browser, every component is a window global.

   Lucide: after the full tree mounts, swap every <i data-lucide="…"> placeholder
   for its inline SVG. Each region also runs its own createIcons() effect (e.g.
   ProductGrid re-runs on filter change) so icons inside re-rendered cards render
   too; this mount-time pass is the whole-tree safety net.
   =========================================================================== */
function App() {
  const { TopNav, Hero, ProductGrid, SpecTable, SiteFooter } = window;

  React.useEffect(() => { if (window.lucide) window.lucide.createIcons(); });

  return (
    <React.Fragment>
      <TopNav />
      <main id="top">
        <Hero />
        <ProductGrid />
        <SpecTable />
      </main>
      <SiteFooter />
    </React.Fragment>
  );
}

window.App = App;
