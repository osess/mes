(function($){

  var DetailsPop = function(element){
    this.$element = $(element);
    this.hide = this.$element.data('hide');
    this.res_uri = this.$element.data('res-uri');
    this.edit_uri = this.$element.data('edit-uri');
    this.obj_data = null;

    this.$element.on('click', $.proxy(this.click, this));
  };

  DetailsPop.prototype = {
      constructor: DetailsPop,

      click: function(e){
        e.stopPropagation();
        e.preventDefault();
        var modal = $('#detail-modal-id');
        var el = this.$element;
        if(this.hide == "TU1"){
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<form action="'+this.edit_uri+'" method="post" enctype="multipart/form-data">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              '上传缩略图1' +'</h4></div><div hide="TU1"class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<input type="submit" class="btn btn-primary active" value="上传" /></div></div></form></div></div>');
        }
        if(this.hide == "TU2"){
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<form action="'+this.edit_uri+'" method="post" enctype="multipart/form-data">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              '上传缩略图2' +'</h4></div><div hide="TU2"class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<input type="submit" class="btn btn-primary active" value="上传" /></div></div></form></div></div>');
        }
        if(this.hide == "TU3"){
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<form action="'+this.edit_uri+'" method="post" enctype="multipart/form-data">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              '上传缩略图3' +'</h4></div><div hide="TU3"class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<input type="submit" class="btn btn-primary active" value="上传" /></div></div></form></div></div>');
        }
        if(this.hide == "T"){
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<form action="'+this.edit_uri+'" method="post" enctype="multipart/form-data">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              '上传工艺文件' +'</h4></div><div hide="T"class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<input type="submit" class="btn btn-primary active" value="上传" /></div></div></form></div></div>');
        }
        if(this.hide == "P"){
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<form action="'+this.edit_uri+'" method="post" enctype="multipart/form-data">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              '上传程式文件' +'</h4></div><div hide="P"class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<input type="submit" class="btn btn-primary active" value="上传" /></div></div></form></div></div>');
        }
        if(this.hide == "D2"){
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<form action="'+this.edit_uri+'" method="post" enctype="multipart/form-data">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              '上传二维图' +'</h4></div><div hide="D2"class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<input type="submit" class="btn btn-primary active" value="上传" /></div></div></form></div></div>');
        }
        if(this.hide == "D3"){
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<form action="'+this.edit_uri+'" method="post" enctype="multipart/form-data">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              '上传三维图' +'</h4></div><div hide="D3"class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<input type="submit" class="btn btn-primary active" value="上传" /></div></div></form></div></div>');
        }
        if(!modal.length){
          if(this.edit_uri.search("update") != -1){
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              el.attr('title') +'</h4></div><div class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<a class="btn btn-submit btn-primary edit-btn"><i class="icon-pencil"></i>编辑</a></div></div></div></div>');
          }else{
            modal = $('<div id="detail-modal-id" class="modal fade detail-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">'+
              '<form action="'+this.edit_uri+'" method="post" enctype="multipart/form-data">'+
              '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4>'+ 
              el.attr('title') +'</h4></div><div hide="' + this.hide + '"class="modal-body"></div>'+
              '<div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">关闭</button>'+
              '<input type="submit" class="btn btn-primary active" value="上传" /></div></div></form></div></div>');
          }
          $('body').append(modal);
        }
        modal.find('.modal-title').html(el.attr('title'));
        modal.find('.edit-btn').attr('href', this.edit_uri);
        modal.find('.modal-body').html('<h1 style="text-align:center;"><i class="icon-spinner icon-spin icon-large"></i></h1>');
        modal.find('.modal-body').load(this.res_uri + '?_format=html', function(response, status, xhr) {
          if (status == "error") {
            var msg = "Sorry but there was an error: ";
            modal.find('.modal-body').html(msg + xhr.status + " " + (typeof xhr === 'string' ? xhr : xhr.responseText || xhr.statusText || 'Unknown error!'));
          }
        });
        modal.modal();
      }
  };

  $.fn.details = function () {
    return this.each(function () {
      var $this = $(this), data = $this.data('details');
      if (!data) {
          $this.data('details', (data = new DetailsPop(this)));
      }
    });
  };

  $(function(){
    $('.details-handler').details();
  });

})(jQuery);


