/* ==========================================================
 * sugar-drawer.js v2.0.0
 * ==========================================================
 * Copyright 2012 Seer
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================== */


!function( $ ){

  "use strict"

	 /* DRAWER CLASS DEFINITION
	  * ========================= */

	  var toggle = '[data-toggle="drawer"]'
	    , Drawer = function ( element ) {
	        var $el = $(element).on('click.drawer.data-api', this.toggle)
	        $('html').on('click.drawer.data-api', function () {
	          $el.parent().removeClass('open')
	        })
	      }

	  Drawer.prototype = {

	    constructor: Drawer

	  , toggle: function ( e ) {
	      var $this = $(this)
	        , selector = $this.attr('data-target')
	        , $parent
	        , isActive

	      if (!selector) {
	        selector = $this.attr('href')
	        selector = selector && selector.replace(/.*(?=#[^\s]*$)/, '') //strip for ie7
	      }

	      $parent = $(selector)
	      $parent.length || ($parent = $this.parent())

	      isActive = $parent.hasClass('open')

	      clearMenus()
	      !isActive && $parent.toggleClass('open')

	      return false
	    }

	  }

	  function clearMenus() {
	    $(toggle).parent().removeClass('open')
	  }


	  /* DRAWER PLUGIN DEFINITION
	   * ========================== */

	  $.fn.drawer = function ( option ) {
	    return this.each(function () {
	      var $this = $(this)
	        , data = $this.data('drawer')
	      if (!data) $this.data('drawer', (data = new Drawer(this)))
	      if (typeof option == 'string') data[option].call($this)
	    })
	  }

	  $.fn.drawer.Constructor = Drawer


	  /* APPLY TO STANDARD DRAWER ELEMENTS
	   * =================================== */

	  $(function () {
	    $('html').on('click.drawer.data-api', clearMenus)
	    $('body').on('click.drawer.data-api', toggle, Drawer.prototype.toggle)
	  })

	}( window.jQuery )

