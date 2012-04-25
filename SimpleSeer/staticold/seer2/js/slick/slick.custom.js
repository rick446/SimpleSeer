var grid;
 var loader = new Slick.Data.RemoteModel();

 var storyTitleFormatter = function (row, cell, value, columnDef, dataContext) {
   return "<b><a href='" + dataContext["link"] + "' target=_blank>" +
       dataContext["title"] + "</a></b><br/>" + dataContext["description"];
 };


 var columns = [
   {id: "num", name: "#", field: "index", width: 40},
   {id: "story", name: "Story", width: 580, formatter: storyTitleFormatter, cssClass: "cell-story"},
   {id: "diggs", name: "Diggs", field: "diggs", width: 60, sortable: true}
 ];

 var options = {
   rowHeight: 64,
   editable: false,
   enableAddRow: false,
   enableCellNavigation: false
 };

 var loadingIndicator = null;


 $(function () {
   grid = new Slick.Grid("#myGrid", loader.data, columns, options);

   grid.onViewportChanged.subscribe(function (e, args) {
     var vp = grid.getViewport();
     loader.ensureData(vp.top, vp.bottom);
   });

   grid.onSort.subscribe(function (e, args) {
     loader.setSort(args.sortCol.field, args.sortAsc ? 1 : -1);
     var vp = grid.getViewport();
     loader.ensureData(vp.top, vp.bottom);
   });

   loader.onDataLoading.subscribe(function () {
     if (!loadingIndicator) {
       loadingIndicator = $("<span class='loading-indicator'><label>Buffering...</label></span>").appendTo(document.body);
       var $g = $("#myGrid");

       loadingIndicator
           .css("position", "absolute")
           .css("top", $g.position().top + $g.height() / 2 - loadingIndicator.height() / 2)
           .css("left", $g.position().left + $g.width() / 2 - loadingIndicator.width() / 2);
     }

     loadingIndicator.show();
   });

   loader.onDataLoaded.subscribe(function (e, args) {
     for (var i = args.from; i <= args.to; i++) {
       grid.invalidateRow(i);
     }

     grid.updateRowCount();
     grid.render();

     loadingIndicator.fadeOut();
   });

   $("#txtSearch").keyup(function (e) {
     if (e.which == 13) {
       loader.setSearch($(this).val());
       var vp = grid.getViewport();
       loader.ensureData(vp.top, vp.bottom);
     }
   });

   // load the first page
   grid.onViewportChanged.notify();
 })