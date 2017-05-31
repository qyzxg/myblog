/**
 * Created by qyzxg on 2017/5/31.
 */
// Inlite Theme Example
//For submit articles
tinymce.init({
    selector: 'textarea',
    directionality: 'ltr',
    language: 'zh_CN',
    menubar: false,
    height: 30,
    plugins: [
        'advlist autolink link lists charmap print hr anchor pagebreak spellchecker',
        'searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime nonbreaking',
        'save contextmenu directionality emoticons template paste textcolor textpattern',
        'codesample',
    ],
    toolbar: 'insertfile undo redo | \
     styleselect | \
     bold italic | \
     alignleft aligncenter alignright alignjustify | \
     bullist numlist outdent indent | \
     link | \
     forecolor backcolor emoticons |\
     codesample',


    // imageupload_url: '/edit/upload_postimg/',
    // imagetools_cors_hosts: ['51datas.com', 'oqquiobc2.bkt.clouddn.com'],
    // fontsize_formats: '10pt 12pt 14pt 18pt 24pt 36pt',
    nonbreaking_force_tab: true,

    codesample_dialog_width: 500,
    codesample_dialog_height: 300,
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

});
