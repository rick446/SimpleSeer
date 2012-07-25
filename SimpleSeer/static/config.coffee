exports.config =
  # See docs at http://brunch.readthedocs.org/en/latest/config.html.

  # Edit the next line to change default build path.
  paths:
    public: 'public'

  files:
    javascripts:
      # Defines what file will be generated with `brunch generate`.
      defaultExtension: 'coffee'
      # Describes how files will be compiled & joined together.
      # Available formats:
      # * 'outputFilePath'
      # * map of ('outputFilePath': /regExp that matches input path/)
      # * map of ('outputFilePath': function that takes input path)
      joinTo:
        'javascripts/app.js': /^app/
        'javascripts/vendor.js': /^vendor/
      # Defines compilation order.
      # `vendor` files will be compiled before other ones
      # even if they are not present here.
      order:
        before: [
          'vendor/scripts/console-helper.js',
          'vendor/scripts/jquery-1.7.2.js',
          'vendor/scripts/underscore-1.3.1.js',
          'vendor/scripts/backbone-0.9.2.js',
          'vendor/scripts/bootstrap.js',
          #'vendor/scripts/jquery.jqplot.min.js',
          'vendor/scripts/highcharts.src.js',
          'vendor/scripts/ui/jquery.ui.core.js',
          'vendor/scripts/ui/jquery.ui.widget.js',
          'vendor/scripts/ui/jquery.ui.mouse.js',
          'vendor/scripts/ui/jquery.effects.core.js',
          'vendor/scripts/ui/jquery.ui.datepicker.js',
          'vendor/scripts/ui/jquery.ui.selectable.js',
          'vendor/scripts/ui/jquery.ui.combobox.js',
          'vendor/scripts/jquery-ui-timepicker-addon.js',
          'vendor/scripts/jquery.mousewheel.js',
          'vendor/scripts/moment.js',
          'vendor/scripts/jquery.tablesorter.js',
          'vendor/scripts/jquery.tablesorter.pager.js',
          'vendor/scripts/processing.js',
          'vendor/scripts/jquery.ui.zoomify.js',
          'vendor/scripts/jquery.autogrow-textarea.js']

    stylesheets:
      defaultExtension: 'less'
      joinTo: 'stylesheets/app.css'
      order:
        before: ['vendor/styles/bootstrap.css']
        after: [ 'vendor/styles/bootstrap-responsive.css',
          'vendor/styles/jquery.jqplot.min.css',
          'vendor/styles/themes/base/jquery.ui.core.css',
          'vendor/styles/tablesorter-blue.css',
          'vendor/styles/jquery.tablesorter.pager.css',
          'vendor/styles/jquery.ui.combobox.css',
          'vendor/styles/jquery.ui.zoomify.css']

    templates:
      defaultExtension: 'hbs'
      joinTo: 'javascripts/app.js'

  # Change this if you're using something other than backbone (e.g. 'ember').
  # Content of files, generated with `brunch generate` depends on the setting.
  framework: 'backbone'

  # Settings of web server that will run with `brunch watch [--server]`.
  # server:
  #   # Path to your server node.js module.
  #   # If it's commented-out, brunch will use built-in express.js server.
  #   path: 'server.coffee'
  #   port: 3333
  #   # Run even without `--server` option?
  #   run: yes
