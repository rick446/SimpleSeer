$.widget("ui.zoomify", {
  options: {image: "", zoom: 1, x: 0, y: 0, min: 100, max: 400, height: 0},
  image: {},
  loaded: false,
  viewport: {x: 0, y:0, zoom: 1},

  updateDisplay: function() {    
    var self = this;
    var content = this.element;

    if( !self.loaded ) { return false; }

    var image = content.find(".display").get(0);
    self.image = image;
    
    var ratio = image.width / image.height;
    content.find(".view").height(image.height + 2);

    var scale = (self.viewport.zoom * 100) / self.options.min;
     
    var frame = content.find(".frame");
    frame.css({"top": self.viewport.y, "left": self.viewport.x});
    frame.width(image.width / scale);
    frame.height(image.height * self.options.height / scale);

    var frameWidth = frame.css("border-bottom-width").replace(/\D/g, "");
    frameWidth *= 2;    

    if( frame.width() + self.viewport.x > image.width - frameWidth ) {
      var value = image.width - frame.width() - frameWidth;
      self.viewport.x = value;
      frame.css("left", value);
    }

    if( frame.height() + self.viewport.y > image.height - frameWidth ) {
      var value = image.height - frame.height() - frameWidth;
      self.viewport.y = value;
      frame.css("top", value);
    }

    var slider = content.find(".slider");
    slider.css("width", slider.parent().width() - slider.parent().find("input").width() - 30);

    self._trigger("update", null, {
      x: self.viewport.x / image.width,
      y: self.viewport.y / image.height,
      zoom: self.viewport.zoom
    }); 
  },
  
  _create: function() {
    var self = this;
    var options = this.options;
    var element = this.element;
    element.addClass("ui-zoomify");

    self.viewport = {zoom: options.zoom, x: options.x, y: options.y};
    
    var content = $('<div class="window"><div class="view"><div class="frame"></div><img class="display" src="'+options.image+'"></div></div><div class="settings"><input type="text" value=""><div class="slider"></div></div>').appendTo(element);
    content.find("input").attr("value", self.viewport.zoom * 100 + "%");
    content.find(".display").load(function() { self.loaded = true; self.updateDisplay(); }).bind('dragstart', function(event) { event.preventDefault(); });;

    content.find(".frame").draggable({
      containment: "parent",
      drag: function(event, ui) {
         self.viewport.x = ui.position.left;
         self.viewport.y = ui.position.top;
         self.updateDisplay();
      }
    });   
    
    content.find(".slider").slider({
      min: options.min,
      max: options.max,
      value: (options.zoom * 100),
      slide: function(event, ui) {
        $(this).parent().find("input").attr("value", ui.value + "%");
        self.viewport.zoom = content.find("input").attr("value").replace(/\%/g, "") / 100;
        self.updateDisplay();
      }
    });

    content.find("input").keypress(function(e) {
      if(e.which == 13){
        var input = $(this);
        var value = String(Math.max(input.attr("value"), self.options.min));
        
        // Set the slider's value
        $("#control .slider").slider("option", "value", value.replace(/\%/g, ""));

        // Add percent sign back in
        input.attr("value", value.replace(/\%/g, "") + "%");
        self.viewport.zoom = content.find("input").attr("value").replace(/\%/g, "") / 100;
        
        self.updateDisplay();
      }
    });
    
    $(window).resize(function() { self.updateDisplay(); });
  },

  _setOption: function(option, value) {
    var self = this;
    
    $.Widget.prototype._setOption.apply( this, arguments );

    switch(option) {
      case "image":
        self.options.image = value;
        this.element.find("#display").attr("src", value);
        break;
      case "zoom":
        self.options.zoom = value;
        self.viewport.zoom = value;
        self.options.y = self.viewport.y = self.options.x = self.viewport.x = 0;
        self.element.find(".slider").slider("option", "value", value * 100);
        self.element.find("input").attr("value", (value * 100) + "%");
        self.updateDisplay();
        break;
      case "x":
        self.options.x = value;
        self.viewport.x = value * self.image.width
        self.updateDisplay();
        break;
      case "y":
        self.options.y = value;
        self.viewport.y = value * self.image.height
        self.updateDisplay();
        break;
      case "min":
        self.options.min = value;
        self.options.y = self.viewport.y = self.options.x = self.viewport.x = 0;
        self.element.find(".slider").slider("option", "min", value);
        self.updateDisplay();
        break;
      case "max":
        self.options.max = value;
        self.options.y = self.viewport.y = self.options.x = self.viewport.x = 0;
        self.element.find(".slider").slider("option", "max", value);
        self.updateDisplay();
        break;
      case "height":
        self.options.height = value;
        self.updateDisplay();
    }
  }
});
