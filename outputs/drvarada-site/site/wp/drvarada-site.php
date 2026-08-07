<?php
/**
 * Plugin Name: Dr Varada Site Bridge
 * Description: Serves the repo-built pages: registers their meta, prints their
 *              <head> verbatim, keeps theme and Elementor CSS off them, and
 *              handles stub-parent and retired-page redirects.
 * Version:     1.0.0
 *
 * DEPLOYED BY  outputs/drvarada-site/site/deploy.py  ("assets" step).
 * SOURCE       outputs/drvarada-site/site/wp/drvarada-site.php  <- edit here only.
 *              This is a must-use plugin: it lives in wp-content/mu-plugins/,
 *              is always active, and cannot be deactivated from wp-admin. That
 *              is deliberate — deactivating it would strip the canonical tags
 *              and stylesheets off 61 pages at once.
 *
 * WHY THE HEAD IS STORED RATHER THAN REGENERATED
 *   build.py already emits a correct <head> for every page: canonical, hreflang
 *   for the Telugu and Hindi pages, robots, og:, theme-color, icon, both
 *   stylesheet links and the JSON-LD. Re-implementing any of that in PHP means
 *   two sources of truth that drift the first time the build changes — and a
 *   missing canonical tag looks exactly like nothing being wrong. So deploy.py
 *   ships the built head as post meta and this prints it back, unmodified.
 */

if (!defined('ABSPATH')) { exit; }

const DRV_META_HEAD   = '_drv_head';
const DRV_META_OWNED  = '_drv_managed';
const DRV_META_STUB   = '_drv_stub_target';
const DRV_META_TITLE  = '_drv_title';

/**
 * Register the meta keys for REST.
 *
 * Without this, `POST /wp/v2/pages` accepts a `meta` object, returns 200, and
 * silently discards every key it does not know — which looks like a successful
 * deploy and produces 61 pages with no <head>. It is the reason deploy.py syncs
 * this file before it pushes any page.
 */
add_action('init', function () {
    $common = [
        'type'          => 'string',
        'single'        => true,
        'show_in_rest'  => true,
        'auth_callback' => function () { return current_user_can('edit_pages'); },
        // No sanitisation: the value is markup written by an authenticated
        // administrator from the repo, and esc_*() here would mangle it.
        'sanitize_callback' => null,
    ];
    foreach ([DRV_META_HEAD, DRV_META_OWNED, DRV_META_STUB,
              DRV_META_TITLE] as $key) {
        register_post_meta('page', $key, $common);
    }
});

function drv_is_managed($post_id = null) {
    $post_id = $post_id ?: get_queried_object_id();
    return $post_id && get_post_meta($post_id, DRV_META_OWNED, true) === '1';
}

/**
 * Print the built head, and remove what WordPress would otherwise duplicate.
 *
 * Priority 1 so our canonical lands before anything a theme adds later, and the
 * core emitters are unhooked rather than left to contradict us.
 */
add_action('wp_head', function () {
    if (!is_page() || !drv_is_managed()) { return; }
    remove_action('wp_head', 'rel_canonical');
    remove_action('wp_head', 'wp_shortlink_wp_head', 10);
    remove_action('wp_head', 'adjacent_posts_rel_link_wp_head', 10);
    remove_action('wp_head', 'wp_generator');
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('wp_print_styles', 'print_emoji_styles');

    $head = get_post_meta(get_queried_object_id(), DRV_META_HEAD, true);
    if ($head) {
        echo "\n<!-- drvarada-site: built head -->\n" . $head . "\n";
    }
}, 1);

/**
 * Keep the theme and Elementor off these pages.
 *
 * The pages ship a complete stylesheet of their own. The Hostinger AI theme's
 * style.css and Elementor's frontend reset both set base type, colours and box
 * sizing, so leaving them enqueued means the live render quietly differs from
 * what verify.py proved locally — the exact drift this whole pipeline exists to
 * prevent.
 */
add_action('wp_enqueue_scripts', function () {
    if (!is_page() || !drv_is_managed()) { return; }
    // Handles verified against the rendered page, not guessed. The first pass
    // used 'hostinger-ai-theme'; the real handle is 'hostinger-ai-style', so the
    // theme's style.min.css kept loading — and because our stylesheets print at
    // wp_head priority 1 and enqueued styles come later, the theme was WINNING
    // every tied selector and quietly restyling the page.
    foreach ([
        'hostinger-ai-style', 'hostinger-ai-style-inline',
        'hostinger-reach-subscription-block',
        'elementor-frontend', 'elementor-post-' . get_queried_object_id(),
        'elementor-icons', 'swiper', 'elementor-common', 'global-styles',
        'wp-block-library', 'wp-block-library-theme', 'classic-theme-styles',
        'wp-emoji-styles', 'wp-block-template-skip-link',
        'wp-img-auto-sizes-contain',
    ] as $handle) {
        wp_dequeue_style($handle);
        wp_deregister_style($handle);
    }
}, PHP_INT_MAX);

/**
 * Drop the theme's webfont <style> block on our pages.
 *
 * WordPress prints @font-face rules for every font the active theme registers
 * in theme.json. With the theme stylesheet dequeued nothing references DMSans,
 * so the browser never downloads it — the rules are inert, just noise in the
 * head. Removed for tidiness, not correctness.
 */
add_action('init', function () {
    add_action('wp_head', function () {
        if (is_page() && drv_is_managed()) {
            remove_action('wp_head', 'wp_print_font_faces', 50);
            // has_action() returns the ACTUAL priority. Hard-coding 1 here
            // silently failed — the hook sits elsewhere on this install, and a
            // remove_action() with the wrong priority is a no-op that reports
            // nothing. That left a second <title> on every page.
            $prio = has_action('wp_head', '_wp_render_title_tag');
            if ($prio !== false) {
                remove_action('wp_head', '_wp_render_title_tag', $prio);
            }
            add_filter('wp_robots', '__return_empty_array');
        }
    }, 0);
}, 1);

/**
 * Make WordPress's own <title> be the built one.
 *
 * The theme's header.php prints <title> literally, before wp_head() runs, so no
 * hook can remove it — printing ours as well produced three titles on the page.
 * Filtering what WordPress builds is the only route to exactly one, and this way
 * the string is the one build.py validated for length and keyword order, so it
 * agrees with the canonical and og:title sitting next to it.
 */
add_filter('pre_get_document_title', function ($title) {
    if (is_page() && drv_is_managed()) {
        $ours = get_post_meta(get_queried_object_id(), DRV_META_TITLE, true);
        if ($ours) { return html_entity_decode($ours, ENT_QUOTES, 'UTF-8'); }
    }
    return $title;
}, PHP_INT_MAX);

/**
 * Exactly one <title> in the head.
 *
 * Two things print one and neither can be unhooked: the Hostinger theme's
 * header.php emits <title> LITERALLY, before wp_head() runs, and something else
 * re-adds `_wp_render_title_tag` after we remove it. Both now carry the correct
 * string via the pre_get_document_title filter above, so this is the last step —
 * drop every <title> after the first.
 *
 * Buffering the whole document is heavier than a hook, which is why it is the
 * last resort rather than the first: it runs once per cache MISS (LiteSpeed
 * serves the stored copy afterwards), it is confined to our own pages, and the
 * regex only ever deletes a <title> element — if the match fails the page is
 * returned untouched.
 */
add_action('template_redirect', function () {
    if (!is_page() || !drv_is_managed()) { return; }
    ob_start(function ($html) {
        $head_end = stripos($html, '</head>');
        if ($head_end === false) { return $html; }
        $head = substr($html, 0, $head_end);
        $rest = substr($html, $head_end);
        $seen = false;
        $head = preg_replace_callback('#<title\b[^>]*>.*?</title>#is',
            function ($m) use (&$seen) {
                if ($seen) { return ''; }
                $seen = true;
                return $m[0];
            }, $head);

        // Exactly one <meta name="viewport">, and a known one.
        //
        // The live head carried TWO: the theme's `initial-scale=1` at the top,
        // and `initial-scale=1.0, viewport-fit=cover` from Astra/Elementor just
        // before </head>. Browsers honour the FIRST, so which one applied was
        // decided by emitter order — i.e. by luck.
        //
        // The one we want to win is the one WITHOUT viewport-fit. These pages
        // use no `env(safe-area-inset-*)` anywhere, so `viewport-fit=cover`
        // extends the layout under the notch and the home indicator with
        // nothing compensating for it — it would put the sticky booking bar
        // under the indicator on exactly the phones most patients use. If safe
        // area padding is ever added to the bar, revisit this and not before.
        $seen_vp = false;
        $head = preg_replace_callback(
            '#<meta\s+name=(["\'])viewport\1[^>]*>#i',
            function ($m) use (&$seen_vp) {
                if ($seen_vp) { return ''; }
                $seen_vp = true;
                return '<meta name="viewport" '
                     . 'content="width=device-width, initial-scale=1">';
            }, $head);
        return $head . $rest;
    });
}, 0);

/**
 * Purge LiteSpeed on demand.
 *
 * Updating a page fires save_post and LiteSpeed purges that URL by itself.
 * Replacing THIS FILE does not — nothing in WordPress knows a PHP file changed,
 * so the cache keeps serving pages rendered by the previous version. That is
 * exactly what happened during the first deploy: the theme stylesheet looked
 * like it was still enqueued after it had been dequeued, for a full cycle of
 * pointless debugging. deploy.py now calls this after every plugin upload.
 */
add_action('rest_api_init', function () {
    register_rest_route('drvarada/v1', '/purge', [
        'methods'  => 'POST',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function () {
            do_action('litespeed_purge_all');
            return ['purged' => true, 'plugin' => '1.1.0'];
        },
    ]);
    // Reports which hooks are actually registered, so a wrong-priority
    // remove_action() can be diagnosed instead of guessed at. Guessing cost two
    // deploy cycles on the theme stylesheet handle alone.
    register_rest_route('drvarada/v1', '/hooks', [
        'methods'  => 'GET',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function () {
            $out = [];
            foreach (['_wp_render_title_tag', 'wp_print_font_faces', 'rel_canonical',
                      'wp_robots', 'wp_site_icon'] as $fn) {
                $out[$fn] = has_action('wp_head', $fn);
            }
            $out['theme'] = get_option('stylesheet');
            $out['title_tag_support'] = current_theme_supports('title-tag');
            return $out;
        },
    ]);
});

/**
 * Keep WordPress's own thin surfaces out of the index.
 *
 * A 61-page site should present 61 indexable URLs. WordPress adds feeds, a
 * search-results page for every query string, and an author archive that
 * duplicates the post list — none of which anyone should land on from Google,
 * and all of which dilute crawl budget and can outrank a real page for a
 * long-tail query. The audit found /feed/, /comments/feed/, /?s= and
 * /author/... all returning 200 and indexable.
 *
 * noindex rather than blocking in robots.txt on purpose: a URL disallowed in
 * robots.txt can still be indexed from an external link, and Google then cannot
 * read the noindex because it is not allowed to fetch the page.
 */
add_filter('wp_robots', function ($robots) {
    if (is_feed() || is_search() || is_author() || is_date() || is_attachment()
        || is_404() || is_paged()) {
        $robots['noindex']  = true;
        $robots['nofollow'] = false;
        unset($robots['index']);
    }
    return $robots;
});

// Author archives serve no purpose on a single-doctor clinic site and leak the
// admin login name in the URL. Redirected to the doctor's page, which is what
// someone clicking an author link actually wanted.
//
// Feeds go too. The noindex filter above cannot reach them — `wp_robots` writes
// a <meta> tag into an HTML <head>, and a feed is XML, so /feed/ kept answering
// 200 with nothing telling a crawler to ignore it. With zero posts on the site
// the feeds carried nothing anyway.
add_action('template_redirect', function () {
    if (is_author()) {
        wp_safe_redirect(home_url('/about/dr-khagendra-varada/'), 301);
        exit;
    }
    if (is_feed()) {
        wp_safe_redirect(home_url('/'), 301);
        exit;
    }
});

/**
 * Stub parents exist only to hold a URL segment.
 *
 * `/vitiligo/phototherapy/` resolves only if a page with slug `vitiligo` is the
 * parent — and a *draft* parent 404s its children, so these have to be
 * published. Published and empty is a thin page Google may index, so each one
 * carries the slug it should redirect to instead.
 */
add_action('template_redirect', function () {
    if (!is_page()) { return; }
    $target = get_post_meta(get_queried_object_id(), DRV_META_STUB, true);
    if (!$target) { return; }
    // A URL path such as "/about/dr-khagendra-varada/". It used to be a slug
    // resolved with get_page_by_path(), which returned null for every nested
    // page — the slug is the leaf, the path is what WordPress indexes.
    wp_safe_redirect(home_url($target), 301);
    exit;
});

/**
 * Retired Hostinger AI starter pages.
 *
 * Trashing a page makes its URL 404. Every one of these was published for
 * months, so they are redirected to the nearest real page rather than dropped —
 * and the table lives here, next to the pages, rather than in a redirect plugin
 * nobody will remember is installed.
 */
add_action('template_redirect', function () {
    if (!is_404()) { return; }
    $map = [
        'home'       => '/',
        'home-2'     => '/',
        'home-v2'    => '/',
        'about-2'    => '/about/dr-khagendra-varada/',
        'services'   => '/treatments/',
        'services-2' => '/treatments/',
        'contact-2'  => '/contact/',
    ];
    $path = trim(parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH) ?: '', '/');
    if (isset($map[$path])) {
        wp_safe_redirect(home_url($map[$path]), 301);
        exit;
    }
});

/**
 * Serve the built sitemap and let it own hreflang.
 *
 * The build emits sitemap.xml with xhtml:link alternates for the Telugu and
 * Hindi pages. Google accepts hreflang from a sitemap, which is why none of it
 * needs injecting into <head> per page. WordPress's own wp-sitemap.xml would
 * compete for the same job with none of the alternates, so it is turned off.
 */
add_filter('wp_sitemaps_enabled', '__return_false');
