<?php
/**
 * Plugin Name: Agent File Manager
 * Description: Secure file management for Agent Website Manager. Auto-backups before every edit.
 * Version: 1.0.0
 * Author: Agent Website Manager
 */

// Prevent direct access
if (!defined('ABSPATH')) exit;

// Register REST API endpoints
add_action('rest_api_init', function () {
    // List files in a directory
    register_rest_route('agent/v1', '/files', [
        'methods' => 'GET',
        'callback' => 'agent_list_files',
        'permission_callback' => function() { return current_user_can('manage_options'); },
    ]);

    // Read a file
    register_rest_route('agent/v1', '/files/read', [
        'methods' => 'GET',
        'callback' => 'agent_read_file',
        'permission_callback' => function() { return current_user_can('manage_options'); },
    ]);

    // Write to a file (with auto-backup)
    register_rest_route('agent/v1', '/files/write', [
        'methods' => 'POST',
        'callback' => 'agent_write_file',
        'permission_callback' => function() { return current_user_can('manage_options'); },
    ]);

    // List backups
    register_rest_route('agent/v1', '/backups', [
        'methods' => 'GET',
        'callback' => 'agent_list_backups',
        'permission_callback' => function() { return current_user_can('manage_options'); },
    ]);

    // Restore a backup
    register_rest_route('agent/v1', '/backups/restore', [
        'methods' => 'POST',
        'callback' => 'agent_restore_backup',
        'permission_callback' => function() { return current_user_can('manage_options'); },
    ]);
});

function agent_get_backup_dir() {
    $dir = WP_CONTENT_DIR . '/agent-backups';
    if (!is_dir($dir)) mkdir($dir, 0755, true);
    // Protect directory
    if (!file_exists($dir . '/.htaccess')) {
        file_put_contents($dir . '/.htaccess', "Deny from all\n");
    }
    return $dir;
}

function agent_list_files($request) {
    $dir = $request->get_param('dir') ?: ABSPATH;
    $dir = realpath($dir);
    if (!$dir || strpos($dir, ABSPATH) !== 0) {
        return new WP_Error('invalid_dir', 'Directory outside WordPress root not allowed.');
    }
    $files = scandir($dir);
    $result = [];
    foreach ($files as $f) {
        if ($f === '.' || $f === '..') continue;
        $path = $dir . '/' . $f;
        $result[] = [
            'name' => $f,
            'path' => str_replace(ABSPATH, '', $path),
            'type' => is_dir($path) ? 'dir' : 'file',
            'size' => is_file($path) ? filesize($path) : 0,
            'modified' => date('Y-m-d H:i:s', filemtime($path)),
            'writable' => is_writable($path),
        ];
    }
    return rest_ensure_response(['files' => $result, 'directory' => str_replace(ABSPATH, '', $dir)]);
}

function agent_read_file($request) {
    $path = $request->get_param('path');
    $full_path = realpath(ABSPATH . '/' . ltrim($path, '/'));
    if (!$full_path || strpos($full_path, ABSPATH) !== 0) {
        return new WP_Error('invalid_path', 'Path outside WordPress root not allowed.');
    }
    if (!file_exists($full_path)) {
        return new WP_Error('not_found', 'File not found: ' . $path);
    }
    return rest_ensure_response([
        'path' => $path,
        'content' => file_get_contents($full_path),
        'size' => filesize($full_path),
        'modified' => date('Y-m-d H:i:s', filemtime($full_path)),
    ]);
}

function agent_write_file($request) {
    $path = $request->get_param('path');
    $content = $request->get_param('content');
    $full_path = realpath(ABSPATH . '/' . ltrim($path, '/'));

    if (!$full_path || strpos($full_path, ABSPATH) !== 0) {
        return new WP_Error('invalid_path', 'Path outside WordPress root not allowed.');
    }

    // Create backup first
    $backup_dir = agent_get_backup_dir();
    $backup_name = date('Ymd_His') . '_' . preg_replace('/[^a-zA-Z0-9_-]/', '_', $path);
    $backup_path = $backup_dir . '/' . $backup_name;

    if (file_exists($full_path)) {
        copy($full_path, $backup_path);
    }

    // Write new content
    $result = file_put_contents($full_path, $content);

    if ($result === false) {
        return new WP_Error('write_failed', 'Could not write to file: ' . $path);
    }

    return rest_ensure_response([
        'written' => true,
        'path' => $path,
        'bytes' => $result,
        'backup' => $backup_name,
        'backup_path' => str_replace(ABSPATH, '', $backup_path),
    ]);
}

function agent_list_backups($request) {
    $dir = agent_get_backup_dir();
    $files = scandir($dir);
    $backups = [];
    foreach ($files as $f) {
        if ($f === '.' || $f === '..' || $f === '.htaccess') continue;
        $path = $dir . '/' . $f;
        $backups[] = [
            'name' => $f,
            'original_file' => preg_replace('/^\d{8}_\d{6}_/', '', $f),
            'size' => filesize($path),
            'date' => date('Y-m-d H:i:s', filemtime($path)),
        ];
    }
    return rest_ensure_response(['backups' => array_reverse($backups)]);
}

function agent_restore_backup($request) {
    $backup_name = $request->get_param('name');
    $backup_dir = agent_get_backup_dir();
    $backup_path = $backup_dir . '/' . basename($backup_name);

    if (!file_exists($backup_path)) {
        return new WP_Error('not_found', 'Backup not found: ' . $backup_name);
    }

    // Determine original file
    $original = preg_replace('/^\d{8}_\d{6}_/', '', $backup_name);
    $original = preg_replace('/_/', '/', $original, 1); // Undo path sanitization
    $full_path = ABSPATH . '/' . ltrim($original, '/');

    if (!file_exists(dirname($full_path))) {
        return new WP_Error('invalid_path', 'Original file directory does not exist.');
    }

    copy($backup_path, $full_path);

    return rest_ensure_response([
        'restored' => true,
        'backup' => $backup_name,
        'target' => $original,
    ]);
}
