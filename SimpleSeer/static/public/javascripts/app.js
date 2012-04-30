(function(/*! Brunch !*/) {
  'use strict';

  if (!this.require) {
    var modules = {};
    var cache = {};
    var __hasProp = ({}).hasOwnProperty;

    var expand = function(root, name) {
      var results = [], parts, part;
      if (/^\.\.?(\/|$)/.test(name)) {
        parts = [root, name].join('/').split('/');
      } else {
        parts = name.split('/');
      }
      for (var i = 0, length = parts.length; i < length; i++) {
        part = parts[i];
        if (part == '..') {
          results.pop();
        } else if (part != '.' && part != '') {
          results.push(part);
        }
      }
      return results.join('/');
    };

    var getFullPath = function(path, fromCache) {
      var store = fromCache ? cache : modules;
      var dirIndex;
      if (__hasProp.call(store, path)) return path;
      dirIndex = expand(path, './index');
      if (__hasProp.call(store, dirIndex)) return dirIndex;
    };
    
    var cacheModule = function(name, path, contentFn) {
      var module = {id: path, exports: {}};
      try {
        cache[path] = module.exports;
        contentFn(module.exports, function(name) {
          return require(name, dirname(path));
        }, module);
        cache[path] = module.exports;
      } catch (err) {
        delete cache[path];
        throw err;
      }
      return cache[path];
    };

    var require = function(name, root) {
      var path = expand(root, name);
      var fullPath;

      if (fullPath = getFullPath(path, true)) {
        return cache[fullPath];
      } else if (fullPath = getFullPath(path, false)) {
        return cacheModule(name, fullPath, modules[fullPath]);
      } else {
        throw new Error("Cannot find module '" + name + "'");
      }
    };

    var dirname = function(path) {
      return path.split('/').slice(0, -1).join('/');
    };

    this.require = function(name) {
      return require(name, '');
    };

    this.require.brunch = true;
    this.require.define = function(bundle) {
      for (var key in bundle) {
        if (__hasProp.call(bundle, key)) {
          modules[key] = bundle[key];
        }
      }
    };
  }
}).call(this);
(this.require.define({
  "application": function(exports, require, module) {
    (function() {
  var Application;

  Application = {
    initialize: function() {
      var ChartView, FrameView, HomeView, Router;
      HomeView = require('views/home_view');
      FrameView = require('views/frame');
      ChartView = require('views/chart');
      Router = require('lib/router');
      this.homeView = new HomeView();
      this.chartView = new ChartView();
      this.router = new Router();
      return typeof Object.freeze === "function" ? Object.freeze(this) : void 0;
    }
  };

  module.exports = Application;

}).call(this);

  }
}));
(this.require.define({
  "initialize": function(exports, require, module) {
    (function() {
  var application;

  application = require('application');

  $(function() {
    application.initialize();
    return Backbone.history.start();
  });

}).call(this);

  }
}));
(this.require.define({
  "lib/router": function(exports, require, module) {
    (function() {
  var Router, application,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  application = require('application');

  module.exports = Router = (function(_super) {

    __extends(Router, _super);

    function Router() {
      Router.__super__.constructor.apply(this, arguments);
    }

    Router.prototype.routes = {
      '': 'home'
    };

    Router.prototype.home = function() {
      return $('#main').html(application.homeView.render().el);
    };

    return Router;

  })(Backbone.Router);

}).call(this);

  }
}));
(this.require.define({
  "lib/view_helper": function(exports, require, module) {
    (function() {



}).call(this);

  }
}));
(this.require.define({
  "models/collection": function(exports, require, module) {
    (function() {
  var Collection,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  module.exports = Collection = (function(_super) {

    __extends(Collection, _super);

    function Collection() {
      Collection.__super__.constructor.apply(this, arguments);
    }

    return Collection;

  })(Backbone.Collection);

}).call(this);

  }
}));
(this.require.define({
  "models/model": function(exports, require, module) {
    (function() {
  var Model,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  module.exports = Model = (function(_super) {

    __extends(Model, _super);

    function Model() {
      Model.__super__.constructor.apply(this, arguments);
    }

    return Model;

  })(Backbone.Model);

}).call(this);

  }
}));
(this.require.define({
  "views/chart": function(exports, require, module) {
    (function() {
  var ChartView, SubView, template, view_helper,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  SubView = require('./subview');

  template = require('./templates/chart');

  view_helper = require('lib/view_helper');

  module.exports = ChartView = (function(_super) {

    __extends(ChartView, _super);

    function ChartView() {
      this.render = __bind(this.render, this);
      this.update = __bind(this.update, this);
      ChartView.__super__.constructor.apply(this, arguments);
    }

    ChartView.prototype.id = 'chart-view';

    ChartView.prototype.template = template;

    ChartView.prototype.lastupdate = 0;

    ChartView.prototype.update = function() {
      var url,
        _this = this;
      url = "/olap/Motion";
      if (this.lastupdate) url = url + "/since/" + this.lastupdate.toString();
      return $.getJSON(url, function(data) {
        var d, _i, _len;
        setTimeout(_this.update, 1000);
        _this.lastupdate = data.data[data.data.length - 1][0];
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          d = data[_i];
          _this.ts.append(d[0] * 1000 + tz, d[1]);
        }
      });
    };

    ChartView.prototype.render = function() {
      var smoothie;
      ChartView.__super__.render.call(this);
      setTimeout(this.update, 1000);
      smoothie = new SmoothieChart({
        grid: {
          strokeStyle: 'rgb(0, 144, 214)',
          fillStyle: 'rgb(0, 0, 40)',
          lineWidth: 1
        },
        millisPerPixel: 100,
        maxValue: 100,
        minValue: 0
      });
      this.ts = new TimeSeries;
      smoothie.streamTo(this.$("#motion_canvas")[0]);
      return smoothie.addTimeSeries(this.ts, {
        strokeStyle: 'rgb(0, 255, 0)'
      });
    };

    return ChartView;

  })(SubView);

}).call(this);

  }
}));
(this.require.define({
  "views/frame": function(exports, require, module) {
    (function() {
  var FrameView, SubView, template,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  SubView = require('./subview');

  template = require('./templates/frame');

  module.exports = FrameView = (function(_super) {

    __extends(FrameView, _super);

    function FrameView() {
      this.render = __bind(this.render, this);
      this.update = __bind(this.update, this);
      FrameView.__super__.constructor.apply(this, arguments);
    }

    FrameView.prototype.id = 'frame-view';

    FrameView.prototype.template = template;

    FrameView.prototype.update = function() {
      var time;
      time = new Date().getTime().toString();
      setTimeout(this.update, 1000);
      return this.$el.find("img").attr("src", "/frame?" + time);
    };

    FrameView.prototype.render = function() {
      setTimeout(this.update, 1000);
      return FrameView.__super__.render.call(this);
    };

    return FrameView;

  })(SubView);

}).call(this);

  }
}));
(this.require.define({
  "views/home_view": function(exports, require, module) {
    (function() {
  var ChartView, FrameView, HomeView, View, template,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  View = require('./view');

  FrameView = require('./frame');

  ChartView = require('./chart');

  template = require('./templates/home');

  module.exports = HomeView = (function(_super) {

    __extends(HomeView, _super);

    function HomeView() {
      this.initialize = __bind(this.initialize, this);
      HomeView.__super__.constructor.apply(this, arguments);
    }

    HomeView.prototype.initialize = function() {
      HomeView.__super__.initialize.call(this);
      this.addSubview("frame-view", FrameView, '#frame-container');
      return this.addSubview("chart-view", ChartView, '#chart-container');
    };

    HomeView.prototype.id = 'home-view';

    HomeView.prototype.template = template;

    return HomeView;

  })(View);

}).call(this);

  }
}));
(this.require.define({
  "views/subview": function(exports, require, module) {
    (function() {
  var SubView, View,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  require('lib/view_helper');

  View = require('./view');

  module.exports = SubView = (function(_super) {

    __extends(SubView, _super);

    function SubView() {
      this.render = __bind(this.render, this);
      SubView.__super__.constructor.apply(this, arguments);
    }

    SubView.prototype.options = {
      parent: null,
      selector: null
    };

    SubView.prototype.render = function() {
      this.setElement(this.options.parent.$(this.options.selector));
      SubView.__super__.render.apply(this, arguments);
      return this;
    };

    return SubView;

  })(View);

}).call(this);

  }
}));
(this.require.define({
  "views/templates/chart": function(exports, require, module) {
    module.exports = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var foundHelper, self=this;


  return "<h2>Motion</h2>\n<div id=\"graph_motion\" class=\"graph\">\n  <canvas id=\"motion_canvas\"></canvas>\n</div>\n";});
  }
}));
(this.require.define({
  "views/templates/frame": function(exports, require, module) {
    module.exports = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var foundHelper, self=this;


  return "<h2>Live Feed</h2> \n<div id=\"frame\"> \n  <img src=\"/frame\"/> \n</div>";});
  }
}));
(this.require.define({
  "views/templates/home": function(exports, require, module) {
    module.exports = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var foundHelper, self=this;


  return "		<div id=\"content\" class=\"row\">\n		  <div id=\"frame-container\" class=\"span5\">\n\n		  </div>\n		  <div id=\"chart-container\" class=\"span7\">\n\n		  </div>\n		</div>  \n";});
  }
}));
(this.require.define({
  "views/view": function(exports, require, module) {
    (function() {
  var View,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  require('lib/view_helper');

  module.exports = View = (function(_super) {

    __extends(View, _super);

    function View() {
      this.addSubview = __bind(this.addSubview, this);
      this.renderSubviews = __bind(this.renderSubviews, this);
      this.afterRender = __bind(this.afterRender, this);
      this.render = __bind(this.render, this);
      this.getRenderData = __bind(this.getRenderData, this);
      this.template = __bind(this.template, this);
      this.initialize = __bind(this.initialize, this);
      View.__super__.constructor.apply(this, arguments);
    }

    View.prototype.subviews = null;

    View.prototype.initialize = function() {
      View.__super__.initialize.call(this);
      return this.subviews = {};
    };

    View.prototype.template = function() {};

    View.prototype.getRenderData = function() {};

    View.prototype.render = function() {
      this.$el.html(this.template(this.getRenderData()));
      this.renderSubviews();
      this.afterRender();
      return this;
    };

    View.prototype.afterRender = function() {};

    View.prototype.renderSubviews = function() {
      var name, subview, _ref, _results;
      _ref = this.subviews;
      _results = [];
      for (name in _ref) {
        subview = _ref[name];
        _results.push(subview.render());
      }
      return _results;
    };

    View.prototype.addSubview = function(name, viewClass, selector, options) {
      options = options || {};
      _.extend(options, {
        parent: this,
        selector: selector
      });
      return this.subviews[name] = new viewClass(options);
    };

    return View;

  })(Backbone.View);

}).call(this);

  }
}));
