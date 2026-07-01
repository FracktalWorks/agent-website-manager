<?php
/**
 * Plugin Name:  Fracktal Media API
 * Description:  REST API for managing FileBird media folders. Enables
 *               programmatic folder CRUD and bulk attachment assignment.
 * Version:      1.0.0
 * Author:       Agent Website Manager
 * License:      MIT
 *
 * This plugin extends FileBird (free) with full REST API access.
 * It writes directly to FileBird's database tables, so folders
 * created via this API appear in the FileBird UI, and vice versa.
 */

defined('ABSPATH') || exit;

class Fracktal_Media_API {

    private $table_folders;
    private $table_relations;

    public function __construct() {
        global $wpdb;
        $this->table_folders   = $wpdb->prefix . 'fbv';
        $this->table_relations = $wpdb->prefix . 'fbv_attachment';
        add_action('rest_api_init', [$this, 'register_routes']);
    }

    // ── Register REST Routes ──────────────────────────────────

    public function register_routes() {
        $namespace = 'fracktal/v1';

        // GET  /folders          — list all folders as tree
        register_rest_route($namespace, '/folders', [
            'methods'  => 'GET',
            'callback' => [$this, 'list_folders'],
            'permission_callback' => [$this, 'check_permission'],
        ]);

        // POST /folders          — create a new folder
        register_rest_route($namespace, '/folders', [
            'methods'  => 'POST',
            'callback' => [$this, 'create_folder'],
            'permission_callback' => [$this, 'check_permission'],
            'args' => [
                'name'   => ['required' => true, 'type' => 'string'],
                'parent' => ['required' => false, 'type' => 'integer', 'default' => 0],
            ],
        ]);

        // DELETE /folders/{id}   — delete folder and its children
        register_rest_route($namespace, '/folders/(?P<id>\d+)', [
            'methods'  => 'DELETE',
            'callback' => [$this, 'delete_folder'],
            'permission_callback' => [$this, 'check_permission'],
        ]);

        // PUT  /folders/{id}     — rename folder
        register_rest_route($namespace, '/folders/(?P<id>\d+)', [
            'methods'  => 'PUT',
            'callback' => [$this, 'rename_folder'],
            'permission_callback' => [$this, 'check_permission'],
            'args' => [
                'name' => ['required' => true, 'type' => 'string'],
            ],
        ]);

        // POST /folders/{id}/assign — assign attachments to folder
        register_rest_route($namespace, '/folders/(?P<id>\d+)/assign', [
            'methods'  => 'POST',
            'callback' => [$this, 'assign_attachments'],
            'permission_callback' => [$this, 'check_permission'],
            'args' => [
                'attachment_ids' => ['required' => true, 'type' => 'array'],
            ],
        ]);

        // GET  /folders/{id}/attachments — list attachments in folder
        register_rest_route($namespace, '/folders/(?P<id>\d+)/attachments', [
            'methods'  => 'GET',
            'callback' => [$this, 'list_attachments'],
            'permission_callback' => [$this, 'check_permission'],
        ]);
    }

    public function check_permission() {
        return current_user_can('upload_files');
    }

    // ── Folder CRUD ───────────────────────────────────────────

    public function list_folders() {
        global $wpdb;
        $folders = $wpdb->get_results(
            "SELECT id, name, parent FROM {$this->table_folders} ORDER BY ord, id",
            ARRAY_A
        );
        return rest_ensure_response($this->build_tree($folders));
    }

    public function create_folder($request) {
        global $wpdb;
        $name   = sanitize_text_field($request->get_param('name'));
        $parent = (int) $request->get_param('parent');

        // Get max ord for parent
        $max_ord = $wpdb->get_var($wpdb->prepare(
            "SELECT COALESCE(MAX(ord), 0) FROM {$this->table_folders} WHERE parent = %d",
            $parent
        ));

        $result = $wpdb->insert(
            $this->table_folders,
            [
                'name'   => $name,
                'parent' => $parent,
                'type'   => 0,
                'ord'    => $max_ord + 1,
            ],
            ['%s', '%d', '%d', '%d']
        );

        if ($result === false) {
            return new WP_Error('db_error', 'Failed to create folder', ['status' => 500]);
        }

        $new_id = $wpdb->insert_id;
        return rest_ensure_response([
            'id'     => $new_id,
            'name'   => $name,
            'parent' => $parent,
        ]);
    }

    public function delete_folder($request) {
        global $wpdb;
        $id = (int) $request->get_param('id');

        // Delete children first (recursive)
        $children = $wpdb->get_col($wpdb->prepare(
            "SELECT id FROM {$this->table_folders} WHERE parent = %d", $id
        ));
        foreach ($children as $child_id) {
            $child_request = clone $request;
            $child_request->set_param('id', $child_id);
            $this->delete_folder($child_request);
        }

        // Remove attachments from this folder
        $wpdb->delete($this->table_relations, ['folder_id' => $id], ['%d']);
        // Delete the folder
        $wpdb->delete($this->table_folders, ['id' => $id], ['%d']);

        return rest_ensure_response(['deleted' => $id]);
    }

    public function rename_folder($request) {
        global $wpdb;
        $id   = (int) $request->get_param('id');
        $name = sanitize_text_field($request->get_param('name'));

        $wpdb->update(
            $this->table_folders,
            ['name' => $name],
            ['id' => $id],
            ['%s'],
            ['%d']
        );

        return rest_ensure_response(['id' => $id, 'name' => $name]);
    }

    // ── Attachment Assignment ─────────────────────────────────

    public function assign_attachments($request) {
        global $wpdb;
        $folder_id = (int) $request->get_param('id');
        $attachment_ids = $request->get_param('attachment_ids');

        $count = 0;
        foreach ($attachment_ids as $attachment_id) {
            $aid = (int) $attachment_id;
            // Remove existing folder assignment
            $wpdb->delete($this->table_relations, ['attachment_id' => $aid], ['%d']);
            // Insert new assignment
            $result = $wpdb->insert(
                $this->table_relations,
                ['attachment_id' => $aid, 'folder_id' => $folder_id],
                ['%d', '%d']
            );
            if ($result) {
                $count++;
            }
        }

        return rest_ensure_response([
            'assigned' => $count,
            'folder_id' => $folder_id,
        ]);
    }

    public function list_attachments($request) {
        global $wpdb;
        $folder_id = (int) $request->get_param('id');

        $ids = $wpdb->get_col($wpdb->prepare(
            "SELECT attachment_id FROM {$this->table_relations} WHERE folder_id = %d",
            $folder_id
        ));

        return rest_ensure_response([
            'folder_id' => $folder_id,
            'attachment_ids' => array_map('intval', $ids),
            'count' => count($ids),
        ]);
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

new Fracktal_Media_API();
