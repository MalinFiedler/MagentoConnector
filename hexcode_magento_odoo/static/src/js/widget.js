odoo.define('hexcode_magento_odoo.form_widgets', function (require) {
    "use strict";

    var core = require('web.core');
    var form_common = require('web.form_common');
    var Many2ManyBinary = core.form_widget_registry.get('many2many_binary');
    var _t = core._t;
    var QWeb = core.qweb;
    var Model = require('web.DataModel');

    var upload_images = [];
    var immagini = [];
    var reload = true;
    var onenter = false;
    var last_sort_number = 0;


    var multidragndrop = Many2ManyBinary.extend({
        template: "dragndropmulti_template",
        read_name_values : function () {
            var self = this;
            // don't reset know values
            var ids = this.get('value');
            var _value = ids;
            // send request for get_name
            if (_value.length) {
                return this.ds_file.call('read', [_value, ['id', 'name', 'datas_fname','extension', 'description', 'sortable']]).then(function (datas) {
                    _.each(datas, function (data) {
                        data.no_unlink = true;
                        data.url = self.session.url('/web/image', {model: 'ir.attachment', field: 'datas', filename_field: 'datas_fname', id: data.id});
                        self.data[data.id] = data;
                    });


                    function compare(a,b){
                        if (a.sortable < b.sortable)
                            return -1;
                        if (a.sortable > b.sortable)
                            return 1;
                        return 0;
                    }

                    datas = $(datas).sort(compare);

                    var ids_sorted = [];

                    for(var i=0; i<datas.length; i++){
                        ids_sorted.push(datas[i].id);
                        last_sort_number = datas[i].sortable;
                    }

                    return ids_sorted;

                });
            } else {
                return $.when(ids);
            }
        },
        render_value: function () {
            var self = this;
            this.read_name_values().then(function (ids) {

                var render = $(QWeb.render('dragndropmulti_template.images', {'widget': self, 'values': ids}));
                render.on('click', '.oe_delete', _.bind(self.on_file_delete, self));
                self.$('.oe_placeholder_files, .oe_attachments').replaceWith( render );

                var fancy_size = $('.image_gallery').size();
                if(fancy_size > 0){
                    $('.image_gallery').magnificPopup({
                        delegate: 'a', // child items selector, by clicking on it popup will open
                        type: 'image',
                        gallery:{enabled:true},
                        image: {
                            markup: '<div class="mfp-figure">'+
                            '<div class="mfp-close"></div>'+
                            '<div class="mfp-img"></div>'+
                            '<div class="mfp-bottom-bar">'+
                            '<div class="mfp-title"></div>'+
                            '<div class="mfp-counter"></div>'+
                            '</div>'+
                            '</div>',

                            titleSrc: function(item) {
                                return item.el.attr('title') +
                                    '<div style="margin-top: -45px;"><a style="padding:5px; color:black; background-color:white; text-align:center;" href="'+item.src+'" >Download</a></div>';
                            },
                            tError: "<a href='%url%'><img src='/alpha_widget/static/src/img/down.png' style='margin-top:-100px;' width='200' /><br/><p>Download File</p></a>"
                        }
                    });



                }

                // reinit input type file
                var $input = self.$('input.oe_form_binary_file');
                $input.after($input.clone(true)).remove();
                self.$(".oe_fileupload").show();

                $('.oe_form_button_save').click(function(e){
                    self.on_button_save(e,self);
                });


                $('.sortable').sortable({
                    stop: function( event, ui ) {
                        /*Salvo l'ordine di sort degli attachment*/
                        var attachments_sort = [];

                        $(this).find('li').each(function(){
                            var id_attachments = $(this).attr('id');
                            attachments_sort.push(id_attachments);
                        });

                        /*eseguo la chiamata al model per aggiornare il sortable*/
                        var model = new Model("ir.attachment");
                        model.call("update_sort_attachment", [],{ attachments_ids: attachments_sort}).then(function(result_id) {

                            //aggiorno la grafica
                            console.log('aggiornato sort nel database');

                        });
                    }
                });

                var overlay = self.$el.find('.dragndrop-overlay');
                var dragndrop_input = self.$el.find('.dragndrop-input');
                var dropfileshere = self.$el.find('.dropfileshere');

                $(overlay).on(
                    'dragover',
                    function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                    });

                $(overlay).on(
                    'dragleave',
                    function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        $(dropfileshere).css('display','initial');
                        $(overlay).css('display','none');
                    });

                $(overlay).on(
                    'dragenter',
                    function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                    });




                $(dragndrop_input).on(
                    'dragover',
                    function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        $(dropfileshere).css('display','none');
                        self.show_upload_overlay($(overlay));
                    })




                $(overlay).on('drop',function(e){
                    alert("ok");
                    if(e.originalEvent.dataTransfer){
                        if(e.originalEvent.dataTransfer.files.length) {
                            e.preventDefault();
                            e.stopPropagation();
                            /*UPLOAD FILES HERE*/
                            var files = e.originalEvent.dataTransfer.files;
                            for(var i=0; i<files.length; i++){
                                if( jQuery.inArray( files[i].name, immagini ) == -1){
                                    immagini.push(files[i].name);
                                    self.base64_image(files[i]);
                                }
                            }
                        }
                        $(overlay).css('display','none');

                    }
                });


                $('.dragndropdescription').on('change',function(){
                    var id_attachment = $(this).attr('id');
                    var description_value = $(this).val();
                    console.log('update: '+ id_attachment+ " con: "+description_value);
                    var model = new Model("ir.attachment");
                    model.call("attachment_update_description", [],{ id: id_attachment, description: description_value}).then(function(result_id) {

                        //aggiorno la grafica
                        self.render_value();

                    });
                });

            });
        },
        on_button_save: function(e, self) {
            self.render_value();
        },
        base64_image: function(file) {
            var self = this;

            var name = file.name;
            var reader = new FileReader();

            reader.onload = function(e) {
                var srcData = e.target.result;
                var base64_image = srcData.substring(srcData.lastIndexOf(",")+1, srcData.length);

                var extension_file = "";
                var extension = name.split('.').pop();

                console.log(extension);


                // https://bugzilla.mozilla.org/show_bug.cgi?id=453805
                if(extension == 'pdf'){
                    //File PDF
                    extension_file = "pdf";
                }else if(extension == 'doc' || extension == 'docx'){
                    //File WORD
                    extension_file = "word";
                }else if(extension == 'zip' || extension == 'rar'){
                    //File ZIP
                    extension_file = "zip";
                }else if(extension == 'psd'){
                    //File PHOTOSHOP
                    extension_file = "psd";
                }else if(extension == 'ppt' || extension == 'pptx'){
                    //File POWER POINT
                    extension_file = "ppt";
                }else if(extension == 'xls' || extension == 'xlsx'){
                    //File POWER POINT
                    extension_file = "xls";
                }

                var model = new Model("ir.attachment");
                model.call("upload_dragndrop", [],{ name: file.name, base64: base64_image, extension: extension_file, sortable: last_sort_number+1}).then(function(result_id) {
                    console.log(result_id);
                    var values = _.clone(self.get('value'));
                    values.push(parseInt(result_id));
                    upload_images[file.name] = parseInt(result_id);
                    console.log('file non presente, lo carico');
                    self.set({'value': values});
                });
            }
            reader.readAsDataURL(file);

        },

        on_file_delete: function (event) {
            event.stopPropagation();
            var file_id = $(event.target).data("id");
            for (var key in upload_images){

                if(upload_images[key] == file_id){
                    delete upload_images[key];
                    var indice = immagini.indexOf(key);
                    delete immagini[indice];
                    console.log("eliminato");
                }

            }

            if (file_id) {
                var files = _.filter(this.get('value'), function (id) {return id != file_id;});
                if(!this.data[file_id].no_unlink) {
                    this.ds_file.unlink([file_id]);
                }
                this.set({'value': files});
            }
        },
        show_upload_overlay: function(overlay){
            $(overlay).css('display','initial');
            var width = $(overlay).prev().width();
            var height = $(overlay).prev().height();
            $(overlay).css('width',width+4+"px");
            $(overlay).css('height',height+5+'px');
            //$(overlay).css('background-color','#5C5B80');
            $(overlay).css('margin-top',-(height+8)+"px");
            $(overlay).css('position','absolute');
            $(overlay).css('background-color','#5C5B80');
            $(overlay).css('text-align','center');
            $(overlay).css('line-height',height+'px');
            $(overlay).html('<a style="color:white; font-weight:bolder; -webkit-margin:0px; font-size: 25px;">UPLOAD</a>')
            if($.browser.mozilla){
                //fix issue 205
                $(overlay).css('right','50%');
                $(overlay).css('margin-right',-((width+4)/2)+"px");
            }
        },

    });


    core.form_widget_registry.add('multidragndrop', multidragndrop);

});