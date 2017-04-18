/**
 * @license Copyright (c) 2003-2017, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	// The toolbar groups arrangement, optimized for two toolbar rows.
	config.toolbarGroups = [
		{ name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
		{ name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
		{ name: 'links' },
		{ name: 'insert' },
		{ name: 'forms' },
		{ name: 'tools' },
		{ name: 'document',	   groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'others' },
		'/',
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
		{ name: 'styles' },
		{ name: 'colors' },
		{ name: 'about' }
	];

	// Remove some buttons provided by the standard plugins, which are
	// not needed in the Standard(s) toolbar.
	config.removeButtons = 'Underline,Subscript,Superscript';
    config.filebrowserImageUploadUrl = "/ckupload/";
	// Set the most common block elements.
	config.format_tags = 'p;h1;h2;h3;pre';

	// Simplify the dialog windows.
	config.removeDialogTabs = 'image:advanced;link:advanced';
	config.extraPlugins = 'markdown';
	config.extraPlugins = 'wordcount';
	config.wordcount = {
        showParagraphs: false,  // 是否统计段落数
        showWordCount: false,   // 是否统计词数
        showCharCount: true,    // 是否统计字符数
        countSpacesAsChars: false,  // 是否统计空间字符
        countHTML: false,   // 是否统计包括HTML字符的字符数
        maxWordCount: -1,   // 最大允许词数，-1表示无上限
        maxCharCount: 20000, //最大允许字符数，-1表示无上限
        filter: new CKEDITOR.htmlParser.filter({        //添加筛选器添加或删除元素之前计数（CKEDITOR.htmlParser.filter），默认值：null (no filter)
            elements: {
                div: function (element) {
                    if (element.attributes.class == 'mediaembed') {
                        return false;
                    }
                }
            }
        })

    };
	
	//添加中文字体
    config.font_names = "宋体/SimSun;新宋体/NSimSun;" +
        "仿宋_GB2312/FangSong_GB2312;楷体_GB2312/KaiTi_GB2312;" +
        "黑体/SimHei;微软雅黑/Microsoft YaHei;幼圆/YouYuan;" +
        "华文彩云/STCaiyun;华文行楷/STXingkai;方正舒体/FZShuTi;" +
        "方正姚体/FZYaoti;" + config.font_names;
};
