//For submit articles
tinymce.init({
    selector: '#post_body',
    directionality: 'ltr',
    language: 'zh_CN',
    height: 200,
    plugins: [
        'advlist autolink link image imagetools imageupload lists charmap print preview hr anchor pagebreak spellchecker',
        'searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking',
        'save table contextmenu directionality emoticons template paste textcolor textpattern',
        'codesample',
    ],
    toolbar: 'insertfile undo redo | \
     styleselect | \
     bold italic | \
     alignleft aligncenter alignright alignjustify | \
     bullist numlist outdent indent | \
     link image imageupload | \
     print preview media fullpage | \
     forecolor backcolor emoticons |\
     codesample fontsizeselect fullscreen',


    imageupload_url: '/edit/upload_postimg/',
    imagetools_cors_hosts: ['51datas.com', 'oqquiobc2.bkt.clouddn.com'],
    fontsize_formats: '10pt 12pt 14pt 18pt 24pt 36pt',
    nonbreaking_force_tab: true,
    style_formats_merge: true,

    codesample_dialog_width: 600,
    codesample_dialog_height: 400,
    textpattern_patterns: [
        {start: '*', end: '*', format: 'italic'},
        {start: '**', end: '**', format: 'bold'},
        {start: '#', format: 'h1'},
        {start: '##', format: 'h2'},
        {start: '###', format: 'h3'},
        {start: '####', format: 'h4'},
        {start: '#####', format: 'h5'},
        {start: '######', format: 'h6'},
        {start: '1. ', cmd: 'InsertOrderedList'},
        {start: '* ', cmd: 'InsertUnorderedList'},
        {start: '- ', cmd: 'InsertUnorderedList'}
    ],
    style_formats: [
        {
            title: 'Image center',
            selector: 'img',
            styles: {
                'float': 'center',
                'margin': '0 10px 0 10px',
                'width': '100%',
            }
        }],

});

//For add plugin
// tinymce.init({
//     selector: '#pluginContent',
//     directionality: 'ltr',
//     language: 'zh_CN',
//     plugins: [
//         'advlist autolink link image lists charmap print preview hr anchor pagebreak spellchecker',
//         'searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking',
//         'save table contextmenu directionality emoticons template paste textcolor',
//         'codesample',
//     ],
// });


// Inlite Theme Example
// tinymce.init({
//   selector: 'div.tinymce',
//   theme: 'inlite',
//   plugins: 'image table link paste contextmenu textpattern autolink',
//   insert_toolbar: 'quickimage quicktable',
//   selection_toolbar: 'bold italic | quicklink h2 h3 blockquote',
//   inline: true,
//   paste_data_images: true,
//   content_css: [
//     '//fonts.googleapis.com/css?family=Lato:300,300i,400,400i',
//     '//www.tinymce.com/css/codepen.min.css']
// });