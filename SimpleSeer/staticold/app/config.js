// Set the require.js configuration for your application.
require.config({
  // Initialize the application with the main application file
  deps: ["main"],

  paths: {
    // JavaScript folders
    libs: "../assets/js/libs",
    plugins: "../assets/js/plugins",

    // Libraries
    jquery: "../assets/js/libs/jquery",
    underscore: "../assets/js/libs/underscore",
    backbone: "../assets/js/libs/backbone",
    jquery_ui: "../js/jquery-ui.min",
    jqueryuiprettypiemenu: "../js/jquery.ui.prettypiemenu",
    jqueryhoverIntent: "../js/jquery.hoverIntent.minified",
    jquerytools: "../js/jquery.tools.min",
    processing: "../js/processing.min",
    jquerysparkline: "../js/jquery.sparkline",
    simpleseer: "../js/simpleseer",
    zoom: "../js/zoom",

    // Shim Plugin
    use: "../assets/js/plugins/use"
  },

  use: {
    backbone: {
      deps: ["use!underscore", "jquery"],
      attach: "Backbone"
    },

    jquery: {
      attach: "$"
    },

    underscore: {
      attach: "_"
    },
    
    jquery_ui: {
      deps: ["use!jquery"]
    },
    
    jqueryuiprettypiemenu: {
      deps: ["use!jquery_ui"]
    },
    
    jquerytools: {
      deps: ["use!jquery"]
    },
    
    jquerysparkline: {
      deps: ["use!jquery"]
    },
    
    jqueryhoverIntent: {
      deps: ["use!jquery"]
    },
    
    simpleseer: {
      deps: ["jquery", "use!jquery_ui", "use!jqueryuiprettypiemenu", "zoom", "use!jquerysparkline", "processing", "underscore", "use!jquerytools", "use!jqueryhoverIntent"],
      attach: "SimpleSeer"
    },
  }
});
