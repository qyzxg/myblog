//For submit articles
tinymce.init({
    selector: 'textarea',
    directionality: 'ltr',
    language: 'zh_CN',
    height: 200,
    plugins: [
        'advlist autolink link image imagetools imageupload lists charmap print preview hr anchor pagebreak spellchecker',
        'searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking',
        'save table contextmenu directionality emoticons template paste textcolor',
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


    imageupload_url: '/edit/qiniu_upload/',
    imagetools_cors_hosts: ['51datas.com', 'oooy4cly3.bkt.clouddn.com'],
    fontsize_formats: '10pt 12pt 14pt 18pt 24pt 36pt',
    nonbreaking_force_tab: true,
    style_formats_merge: true,
    codesample_dialog_width:300,
    codesample_dialog_height:200,
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
