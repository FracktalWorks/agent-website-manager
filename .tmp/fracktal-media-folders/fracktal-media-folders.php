<?php
/**
 * Plugin Name:  Fracktal Media Folders
 * Description:  Unlimited virtual media folders with full REST API.
 *               No folder limits. No license. Full programmatic control.
 * Version:      1.0.0
 * Author:       Agent Website Manager
 * License:      MIT
 *
 * Creates its own database tables for folder management.
 * Works independently — no FileBird or other plugin dependency.
 * Virtual folders only — zero filesystem changes, zero broken URLs.
 */

defined('ABSPATH') || exit;

class Fracktal_Media_Folders {

    private $table_folders;
    private $table_items;

    public function __construct() {
        global $wpdb;
        $this->table_folders = $wpdb->prefix . 'fracktal_folders';
        $this->table_items   = $wpdb->prefix . 'fracktal_folder_items';

        register_activation_hook(__FILE__, [$this, 'create_tables']);
        add_action('rest_api_init', [$this, 'register_routes']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_admin']);
        add_action('admin_menu', [$this, 'add_admin_page']);
    }

    // ── Database ──────────────────────────────────────────────

    public function create_tables() {
        global $wpdb;
        $charset = $wpdb->get_charset_collate();

        $sql_folders = "CREATE TABLE IF NOT EXISTS {$this->table_folders} (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            parent INT UNSIGNED DEFAULT 0,
            ord INT UNSIGNED DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_parent (parent)
        ) $charset;";

        $sql_items = "CREATE TABLE IF NOT EXISTS {$this->table_items} (
            folder_id INT UNSIGNED NOT NULL,
            attachment_id BIGINT UNSIGNED NOT NULL,
            PRIMARY KEY (folder_id, attachment_id),
            INDEX idx_folder (folder_id),
            INDEX idx_attachment (attachment_id)
        ) $charset;";

        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        dbDelta($sql_folders);
        dbDelta($sql_items);
    }

    // ── REST API Routes ───────────────────────────────────────

    public function register_routes() {
        $ns = 'fracktal/v1';

        // GET    /folders                              — tree of all folders
        register_rest_route($ns, '/folders', [
            'methods' => 'GET',
            'callback' => [$this, 'api_list_folders'],
            'permission_callback' => [$this, 'check_permission'],
        ]);

        // GET    /folders?flat=1                       — flat list
        // (handled inside api_list_folders)

        // POST   /folders                              — create folder
        register_rest_route($ns, '/folders', [
            'methods' => 'POST',
            'callback' => [$this, 'api_create_folder'],
            'permission_callback' => [$this, 'check_permission'],
            'args' => [
                'name'   => ['required' => true, 'sanitize_callback' => 'sanitize_text_field'],
                'parent' => ['default' => 0, 'sanitize_callback' => 'absint'],
            ],
        ]);

        // PUT    /folders/{id}                         — rename folder
        register_rest_route($ns, '/folders/(?P<id>\d+)', [
            'methods' => 'PUT',
            'callback' => [$this, 'api_rename_folder'],
            'permission_callback' => [$this, 'check_permission'],
        ]);

        // DELETE /folders/{id}                         — delete folder + contents
        register_rest_route($ns, '/folders/(?P<id>\d+)', [
            'methods' => 'DELETE',
            'callback' => [$this, 'api_delete_folder'],
            'permission_callback' => [$this, 'check_permission'],
        ]);

        // POST   /folders/{id}/assign                 — assign attachments
        register_rest_route($ns, '/folders/(?P<id>\d+)/assign', [
            'methods' => 'POST',
            'callback' => [$this, 'api_assign'],
            'permission_callback' => [$this, 'check_permission'],
            'args' => [
                'attachment_ids' => ['required' => true],
            ],
        ]);

        // GET    /folders/{id}/items                  — list attachments in folder
        register_rest_route($ns, '/folders/(?P<id>\d+)/items', [
            'methods' => 'GET',
            'callback' => [$this, 'api_list_items'],
            'permission_callback' => [$this, 'check_permission'],
        ]);

        // GET    /folders/{id}/items?per_page=100     — paginated items
        // (handled inside api_list_items)

        // POST   /folders/assign-bulk                 — bulk assign via key=value
        register_rest_route($ns, '/folders/assign-bulk', [
            'methods' => 'POST',
            'callback' => [$this, 'api_bulk_assign'],
            'permission_callback' => [$this, 'check_permission'],
            'args' => [
                'items' => ['required' => true],
            ],
        ]);
    }

    public function check_permission() {
        return current_user_can('upload_files');
    }

    // ── API Handlers ──────────────────────────────────────────

    public function api_list_folders($request) {
        global $wpdb;
        $flat = $request->get_param('flat');
        $rows = $wpdb->get_results(
            "SELECT id, name, parent, ord FROM {$this->table_folders} ORDER BY parent, ord, name",
            ARRAY_A
        );
        if ($flat) {
            return rest_ensure_response($rows);
        }
        return rest_ensure_response($this->build_tree($rows));
    }

    public function api_create_folder($request) {
        global $wpdb;
        $name   = $request->get_param('name');
        $parent = $request->get_param('parent');

        $max_ord = $wpdb->get_var($wpdb->prepare(
            "SELECT COALESCE(MAX(ord), 0) FROM {$this->table_folders} WHERE parent = %d",
            $parent
        ));

        $wpdb->insert($this->table_folders, [
            'name'   => $name,
            'parent' => $parent,
            'ord'    => $max_ord + 1,
        ], ['%s', '%d', '%d']);

        return rest_ensure_response([
            'id'     => $wpdb->insert_id,
            'name'   => $name,
            'parent' => $parent,
        ]);
    }

    public function api_rename_folder($request) {
        global $wpdb;
        $id   = (int) $request->get_param('id');
        $name = sanitize_text_field($request->get_param('name'));
        $wpdb->update($this->table_folders, ['name' => $name], ['id' => $id], ['%s'], ['%d']);
        return rest_ensure_response(['id' => $id, 'name' => $name]);
    }

    public function api_delete_folder($request) {
        global $wpdb;
        $id = (int) $request->get_param('id');

        // Delete children recursively
        $children = $wpdb->get_col($wpdb->prepare(
            "SELECT id FROM {$this->table_folders} WHERE parent = %d", $id
        ));
        foreach ($children as $cid) {
            $wpdb->delete($this->table_items, ['folder_id' => $cid], ['%d']);
            $wpdb->delete($this->table_folders, ['id' => $cid], ['%d']);
        }

        $wpdb->delete($this->table_items, ['folder_id' => $id], ['%d']);
        $wpdb->delete($this->table_folders, ['id' => $id], ['%d']);
        return rest_ensure_response(['deleted' => $id]);
    }

    public function api_assign($request) {
        global $wpdb;
        $folder_id = (int) $request->get_param('id');
        $ids = $request->get_param('attachment_ids');

        $count = 0;
        foreach ((array) $ids as $aid) {
            $aid = (int) $aid;
            // Upsert: remove then insert
            $wpdb->delete($this->table_items, [
                'attachment_id' => $aid,
            ], ['%d']);
            $result = $wpdb->insert($this->table_items, [
                'folder_id'     => $folder_id,
                'attachment_id' => $aid,
            ], ['%d', '%d']);
            if ($result) $count++;
        }

        return rest_ensure_response([
            'assigned'  => $count,
            'folder_id' => $folder_id,
        ]);
    }

    public function api_bulk_assign($request) {
        global $wpdb;
        $items = $request->get_param('items');
        // items = [ {attachment_id: N, folder_id: M}, ... ]
        $count = 0;
        foreach ((array) $items as $item) {
            $aid = (int) ($item['attachment_id'] ?? 0);
            $fid = (int) ($item['folder_id'] ?? 0);
            if (!$aid || !$fid) continue;
            $wpdb->delete($this->table_items, ['attachment_id' => $aid], ['%d']);
            $result = $wpdb->insert($this->table_items, [
                'folder_id' => $fid, 'attachment_id' => $aid,
            ], ['%d', '%d']);
            if ($result) $count++;
        }
        return rest_ensure_response(['assigned' => $count]);
    }

    public function api_list_items($request) {
        global $wpdb;
        $folder_id = (int) $request->get_param('id');
        $page      = max(1, (int) ($request->get_param('page') ?: 1));
        $per_page  = min(100, max(1, (int) ($request->get_param('per_page') ?: 50)));
        $offset    = ($page - 1) * $per_page;

        $total = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$this->table_items} WHERE folder_id = %d", $folder_id
        ));

        $ids = $wpdb->get_col($wpdb->prepare(
            "SELECT attachment_id FROM {$this->table_items} WHERE folder_id = %d LIMIT %d OFFSET %d",
            $folder_id, $per_page, $offset
        ));

        return rest_ensure_response([
            'folder_id'      => $folder_id,
            'attachment_ids' => array_map('intval', $ids),
            'total'          => (int) $total,
            'page'           => $page,
            'per_page'       => $per_page,
        ]);
    }

    // ── Admin UI ──────────────────────────────────────────────

    public function enqueue_admin($hook) {
        if ($hook !== 'upload.php') return;
        wp_enqueue_style('fracktal-folders', plugin_dir_url(__FILE__) . 'admin.css', [], '1.0');
        wp_enqueue_script('fracktal-folders', plugin_dir_url(__FILE__) . 'admin.js', ['jquery', 'wp-api-fetch'], '1.0', true);
        wp_localize_script('fracktal-folders', 'fracktalFolders', [
            'apiUrl' => rest_url('fracktal/v1/folders'),
            'nonce'  => wp_create_nonce('wp_rest'),
        ]);
    }

    public function add_admin_page() {
        // No separate page — the UI hooks into the existing media library
    }

    // ── Helpers ───────────────────────────────────────────────

    private function build_tree(array $flat, int $parent = 0): array {
        $tree = [];
        foreach ($flat as $item) {
            if ((int) $item['parent'] === $parent) {
                $item['children'] = $this->build_tree($flat, (int) $item['id']);
                $tree[] = $item;
            }
        }
        return $tree;
    }
}

new Fracktal_Media_Folders();
