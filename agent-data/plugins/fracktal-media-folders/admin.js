/**
 * Fracktal Media Folders — Admin JS
 * Renders a folder tree panel in the Media Library page.
 */
(function($, wp) {
  'use strict';

  $(function() {
    var apiUrl = fracktalFolders.apiUrl;
    var nonce  = (wpApiSettings && wpApiSettings.nonce) || '';

    function buildTree() {
      $.get(apiUrl + '?flat=1')
        .done(function(folders) {
          var flat = folders || [];
          var $tree = $('#fracktal-folder-tree');
          if (!$tree.length) return;

          var $list = $tree.find('.fracktal-tree-list').empty();

          function renderChildren(parentId, $container, depth) {
            var children = flat.filter(function(f) { return f.parent == parentId; });
            if (!children.length && depth === 0) {
              $container.append('<div class="fracktal-empty">No folders yet. Create one below.</div>');
              return;
            }
            children.forEach(function(f) {
              var count = f.item_count || 0;
              var $item = $(
                '<div class="folder-item" data-folder-id="' + f.id + '">' +
                '<span class="dashicons dashicons-category"></span>' +
                '<span class="folder-name">' + escHtml(f.name) + '</span>' +
                '<span class="fracktal-folder-count">' + count + '</span>' +
                '<button class="fracktal-delete-btn dashicons dashicons-trash" title="Delete folder"></button>' +
                '</div>'
              );
              $item.on('click', function(e) {
                if ($(e.target).is('.fracktal-delete-btn, .dashicons-trash')) return;
                $('#fracktal-folder-tree .folder-item').removeClass('active');
                $item.addClass('active');
              });
              $item.find('.fracktal-delete-btn').on('click', function(e) {
                e.stopPropagation();
                if (!confirm('Delete folder "' + f.name + '" and all its subfolders?\n\nMedia files will NOT be deleted.')) return;
                $.ajax({
                  url: apiUrl + '/' + f.id,
                  method: 'DELETE',
                  beforeSend: function(xhr) { xhr.setRequestHeader('X-WP-Nonce', nonce); }
                }).always(function() { buildTree(); });
              });
              $container.append($item);
              renderChildren(f.id, $container, depth + 1);
            });
          }

          renderChildren(0, $list, 0);
        })
        .fail(function(xhr) {
          console.error('Fracktal Folders: Failed to load folders', xhr.status);
          var $tree = $('#fracktal-folder-tree');
          if ($tree.length) {
            $tree.find('.fracktal-tree-list').html(
              '<div class="fracktal-empty" style="color:#b32d2e">Failed to load folders. Check console.</div>'
            );
          }
        });
    }

    function escHtml(s) {
      return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // Create the panel
    var $panel = $(
      '<div id="fracktal-folder-tree">' +
      '<h3 class="fracktal-panel-title">Folders</h3>' +
      '<div class="fracktal-tree-list"></div>' +
      '<div class="fracktal-create-row">' +
      '<input type="text" id="fracktal-new-folder-name" placeholder="New folder name..." />' +
      '<button id="fracktal-create-btn" class="button button-small">Create</button>' +
      '</div>' +
      '</div>'
    );

    // Insert into media library — after the "Media Library" heading, before the grid
    var $wrap = $('.wrap');
    if ($wrap.length) {
      $wrap.prepend($panel);
    } else {
      $('.wp-header-end').after($panel);
    }

    // Create folder handler
    $panel.on('click', '#fracktal-create-btn', function() {
      var $input = $('#fracktal-new-folder-name');
      var $btn = $(this);
      var name = $.trim($input.val());
      if (!name) return;
      if ($btn.prop('disabled')) return;
      $btn.prop('disabled', true).text('Creating...');
      $.ajax({
        url: apiUrl,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ name: name, parent: 0 }),
        beforeSend: function(xhr) { xhr.setRequestHeader('X-WP-Nonce', nonce); }
      })
      .done(function() {
        $input.val('');
        buildTree();
      })
      .fail(function(xhr) {
        alert('Failed to create folder (HTTP ' + xhr.status + '). Check browser console.');
        console.error('Fracktal Folders create failed:', xhr.status, xhr.responseText);
      })
      .always(function() {
        $btn.prop('disabled', false).text('Create');
      });
    });

    $panel.on('keypress', '#fracktal-new-folder-name', function(e) {
      if (e.which === 13) $('#fracktal-create-btn').click();
    });

    // Initial load
    buildTree();
  });

})(jQuery, wp);
