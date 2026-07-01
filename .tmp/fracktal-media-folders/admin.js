/**
 * Fracktal Media Folders — Admin JS
 * Renders a folder tree in the media library sidebar.
 */
(function($, wp) {
  'use strict';

  $(function() {
    var apiUrl = fracktalFolders.apiUrl + '?flat=1';

    // Fetch folders and render tree
    $.get(apiUrl, function(folders) {
      var $tree = $('<div id="fracktal-folder-tree"></div>');
      var flat = folders || [];

      function renderChildren(parentId, $container) {
        var children = flat.filter(function(f) { return f.parent == parentId; });
        if (!children.length) return;
        var $ul = $('<div class="folder-children"></div>');
        children.forEach(function(f) {
          var $item = $('<div class="folder-item" data-folder-id="' + f.id + '">'
            + '<span class="dashicons dashicons-category"></span>'
            + '<span>' + f.name + '</span>'
            + '<span class="fracktal-folder-count"></span>'
            + '</div>');
          $item.on('click', function() {
            $('.folder-item').removeClass('active');
            $(this).addClass('active');
            // Filter media grid by folder
            if (wp.media && wp.media.frame) {
              // Trigger media library filter
            }
            // Navigate to filtered upload view
            var filteredUrl = window.location.pathname + '?page=upload.php&folder_id=' + f.id;
            // Instead, just highlight for now
          });
          $ul.append($item);
          renderChildren(f.id, $ul);
        });
        $container.append($ul);
      }

      renderChildren(0, $tree);

      // Insert into media library page
      var $target = $('.media-frame .media-frame-menu, .wrap h1');
      if ($target.length) {
        $target.first().after($tree);
      } else {
        // Fallback: insert before the media grid
        $('.wp-header-end').after($tree);
      }
    }).fail(function() {
      console.log('Fracktal Folders: Could not load folder tree.');
    });
  });

})(jQuery, wp);
