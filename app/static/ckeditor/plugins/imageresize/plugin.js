/*
 * ImageResize Plugin for CKEditor (http://github.com/nmmf/imageresize)
 * Created by ALL-INKL.COM - Neue Medien M�nnich - 18. Feb 2014
 * Licensed under the terms of GPL, LGPL and MPL licenses.
 */
CKEDITOR.plugins.add("imageresize", {
    init : function(editor){

		/* Browser Support */
		if(!this.support()) return;

		/* Config */
		this.getConfig();

		/* Resize images on paste */
		var t = this;
		editor.on("instanceReady", function(){
			editor.document.on("paste", function(e){
				var parent = e.data.getTarget();
				if(!parent) parent = editor.document;
				window.setTimeout(function(){ t.resizeAll(editor, parent); }, 500);
				window.setTimeout(function(){ t.resizeAll(editor, parent); }, 1000);
				window.setTimeout(function(){ t.resizeAll(editor, parent); }, 1500);
			});
			editor.document.on("drop", function(e){
				var parent = e.data.getTarget();
				if(!parent) parent = editor.document;
				window.setTimeout(function(){ t.resizeAll(editor, parent); }, 500);
				window.setTimeout(function(){ t.resizeAll(editor, parent); }, 1000);
				window.setTimeout(function(){ t.resizeAll(editor, parent); }, 1500);
			});
		});
	},

	/*
	 * Resize all images in a node
	 * editor: CKEDITOR Instance
	 * parent: parent node
	 * width: (integer) max width of the image
	 * height: (integer) max height of the image
	 */
	resizeAll : function(editor, parent, width, height){

		/* Browser Support */
		if(!this.support()) return;

		/* Parent Node */
		if(!parent) parent = editor.document;
		if(!parent) return;

		/* Width and Height */
		if(!width) width = this.config.maxWidth;
		if(!height) height = this.config.maxHeight;
		console.log(width+"x"+height);

		/* Parent Node is a CKEditor DOM Node */
		if("find" in parent && typeof(parent.find) == "function") {} else parent = new CKEDITOR.dom.node(parent);

		/* Find images and resize */
		if(parent && "find" in parent && typeof(parent.find) == "function") {
			var img = parent.find("img"), w, h, s, item, index;
			var l = img.count();
			for(index = 0; index < l; index++) {
				item = img.getItem(index), w = 0, h = 0, s = "";
				try { w = item.$.width, h = item.$.height, s = item.getAttribute("src"); } catch(e) { w = 0, h = 0, s = ""; }
				if(s && s.indexOf("data:") === 0 && (w > width || h > height)) this.resize(editor, item, width, height);
			}
		}

	},

	/*
	 * Resize one image
	 * editor: CKEDITOR Instance
	 * imageElement: Image Node
	 * width: (integer) max width of the image
	 * height: (integer) max height of the image
	 */
	resize : function(editor, imageElement, width, height){

		/* Browser Support */
        if(!this.support() || !imageElement) return;

		/* Width and Height */
		if(!width) width = this.config.maxWidth;
		if(!height) height = this.config.maxHeight;
		console.log(width+"x"+height);

		/* Create image and set properties */
        var img = new Image(), ns = "ckeditorimageresize";
        img[ns] = {"n":imageElement, "w":width, "h":height};

		/* Error Function */
        img.onerror = function() { this[ns] = null; delete this[ns]; };
        img.onabort = function() { this[ns] = null; delete this[ns]; };

		/* Resize function when image is loaded */
        img.onload = function() {

			/* calculate width and height */
            if(this.width <= this[ns].w && this.height <= this[ns].h) return;
            if((this[ns].w / this[ns].h) > (this.width / this.height)) this[ns].w = this[ns].h * (this.width / this.height);
            else this[ns].h = Math.round(this[ns].w / (this.width / this.height));

			/* Create canvas and draw image with new width and height */
            var cv = document.createElement("canvas");
            cv.width = this[ns].w;
            cv.height = this[ns].h;
            cv.style.width = this[ns].w+"px";
            cv.style.height = this[ns].h+"px";
            var ct = cv.getContext("2d");
            ct.drawImage(this, 0, 0, this[ns].w, this[ns].h);

			/* Get base64 image source and update image node */
            if(this[ns].n) {
				if(/^data:image\/jpeg/i.test(this.src) || /\.(jpg|jpeg)$/i.test(this.src)) {
					this[ns].n.setAttribute("src", cv.toDataURL("image/jpeg", 0.8));
				} else {
					this[ns].n.setAttribute("src", cv.toDataURL("image/png"));
				}
				this[ns].n.setAttribute("width", this[ns].w);
				this[ns].n.setAttribute("height", this[ns].h);
				try {
					this[ns].n.$.style.width = this[ns].w+"px";
					this[ns].n.$.style.height = this[ns].h+"px";
				} catch(e) {}
				try {
					editor.focus();
					editor.getSelection().scrollIntoView();
				} catch(e) {}
			}

            this[ns] = cv = ct = null;
            delete this[ns];
        };

		/* Load image */
        img.src = imageElement.getAttribute("src");

	},

	/* Browser Support */
	supportResult : null,
	support : function(){
        if(this.supportResult === null) {
            this.supportResult = false;
            var cv = document.createElement("canvas");
            if(cv && cv.getContext && cv.toDataURL && cv.getContext("2d")) {
                var ct = cv.getContext("2d");
                if(ct && ct.getImageData && ct.putImageData) this.supportResult = true;
                ct = null;
            }
            cv = null;
        }
        return this.supportResult;
	},

	/* Config */
	config : {
		 "maxWidth" 	: 800
		,"maxHeight"	: 800
	},
	getConfig : function(){
		if(CKEDITOR.config.imageResize)
		{
			for(var k in this.config)
			{
				if(CKEDITOR.config.imageResize[k])
				{
					this.config[k] = parseInt(CKEDITOR.config.imageResize[k], 10);
					if(isNaN(this.config[k]) || this.config[k] < 1)
					{
						this.config[k] = 800;
					}
				}
			}
		}
	}

});
