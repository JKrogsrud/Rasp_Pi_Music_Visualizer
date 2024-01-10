var buttonUp = $("#vol-up");
buttonUp.click(function() {
    console.log("Volume Up");
    $.ajax({
        url: "/vol_up",
        type: "POST",
        success: function(response) {
            console.log(response);
        }
    });
});

var buttonDown = $("#vol-down");
buttonDown.click(function() {
    console.log("Volume Down");
    $.ajax({
        url: "/vol_down",
        type: "POST",
        success: function(response) {
            console.log(response);
        }
    });
});

var buttonPlay = $("#play-pause");
var state = "play";
buttonPlay.click(function() {
	var canProceed = false;
	for (i = 1; i <= 5; i++) {
		if (document.getElementById("audio" + String(i)).textContent != "") {
			canProceed = true;
		} 
	}
	if (canProceed == true) {
	    if (state == "play") {
	        console.log("Play Audio");
	        $.ajax({
	            url: "/play",
	            type: "POST",
	            data: {
	            	Selected: selected.attr('id')
	            },
	            success: function(response) {
	            	state = "pause";
	                console.log(response);
	                console.log(buttonPlay);
	                document.getElementById("play-image").remove();
	                let pauseImg = document.createElement("img");
	                pauseImg.setAttribute("id", "pause-image");
	                pauseImg.setAttribute("src", "/static/pause.png");
	                pauseImg.setAttribute("alt", "pause");
	                document.getElementById("play-pause").appendChild(pauseImg);
	            }
	        });
	    }
	    else if (state == "pause") {
	        console.log("Pause Audio")
	        $.ajax({
	            url: "/pause",
	            type: "POST",
	            data: {
	            	Selected: selected.attr('id')
	            },
	            success: function(response) {
	            	state = "play";
	                console.log(response);
	                document.getElementById("pause-image").remove();
	                let playImg = document.createElement("img");
	                playImg.setAttribute("id", "play-image");
	                playImg.setAttribute("src", "/static/play.png");
	                playImg.setAttribute("alt", "play");
	                document.getElementById("play-pause").appendChild(playImg);
	            }
	        });
	    }
	}
});

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var buttonUpload = $("#upload");
buttonUpload.click(function() {
    console.log("Upload Start");
    // Get file for upload
    let fileInput = document.getElementById("input-upload"); //Get FileList object from input
    let file = fileInput.files[0]; //Get first file in FileList
    console.log(file);
    // Upload the file
    const formData = new FormData();
    formData.append("myFile", file)
    const uploader = new XMLHttpRequest();
    uploader.open("POST", "/uploadFile");
    uploader.send(formData);
    // Ajax file info to server and recieve it back for viewing
    $.ajax({
        url: "/uploadInfo",
        data: {
            fileName: file.name,
            fileSize: file.size,
        },
        type: "POST",
        success: function(response) {
            console.log("Success on Post");
            $.ajax({
                url: "/uploadInfo",
                type: "GET",
                success: function(response) {
                    console.log(response)
                    var filesInfo = JSON.parse(response);
                    $("#defaultMessage").text("");
                    for (let i = 0; i < filesInfo.audioFiles.length; i++) {
                        let id = "audio" + String(i+1);
                        $("#" + id).text("Name: " + filesInfo.audioFiles[i].name + " Size: " + filesInfo.audioFiles[i].size);
                        let setupButton = document.createElement("BUTTON");
                        setupButton.innerHTML = "Delete";
                        setupButton.setAttribute("class", "delete");
                        setupButton.id = "delete" + String(i+1);
                        setupButton.setAttribute("type", "button");
                        setupButton.addEventListener("click", function() {
                            console.log("Delete " + id);
                            $.ajax({
                                url: "/deleteFile",
                                type: "POST",
                                data: {
                                    position: i
                                },
                                success: function(response) {
                                    console.log(response);
                                    $("#" + id).text("");
                                    $.ajax({
                                        url: "/deleteFile",
                                        type: "GET",
                                        success: function(response) {
                                            console.log(response)
                                            var filesInfo = JSON.parse(response);
                                            for (let i = 1; i <= 5; i++) {
                                                if (getElementById("delete" + i) != null) {
                                                    document.getElementById("delete" + i).remove();
                                                    $("#audio" + i).text("");
                                                }
                                            }
                                            for (let i = 0; i < filesInfo.audioFiles.length; i++) {
                                                let id = "audio" + String(i+1);
                                                $("#" + id).text("Name: " + filesInfo.audioFiles[i].name + " Size: " + filesInfo.audioFiles[i].size);
                                                let setupButton = document.createElement("BUTTON");
                                                setupButton.innerHTML = "Delete";
                                                setupButton.id = "delete" + String(i+1);
                                                setupButton.setAttribute("type", "button");
                                                document.getElementById(id).appendChild(setupButton);
                                            }
                                        }
                                    });
                                }
                            });
                        });
                        document.getElementById(id).appendChild(setupButton);
                    }
                }
            });
        },
        error: function(response) {
            console.log("There was an error on upload post");
        }
    });
});


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var selected = $("#audio1");
selected.css("background", "#666666");

var div = $("#audio1");
div.click(function() {
	if (state == "play"){
	    selected.css("background", "#ffffff");
	    $(this).css("background", "#666666");
	    selected = $(this);
	}
});
div.hover(
    function() {
        $(this).css("background", "#a8a8a8");
        selected.css("background", "#666666");
    },
    function() {
        $(this).css("background", "#ffffff");
        selected.css("background", "#666666");
    }
);

var div = $("#audio2");
div.click(function() {
    if (state == "play"){
	    selected.css("background", "#ffffff");
	    $(this).css("background", "#666666");
	    selected = $(this);
	}
});
div.hover(
    function() {
        $(this).css("background", "#a8a8a8");
        selected.css("background", "#666666");
    },
    function() {
        $(this).css("background", "#ffffff");
        selected.css("background", "#666666");
    }
);

var div = $("#audio3");
div.click(function() {
    if (state == "play"){
	    selected.css("background", "#ffffff");
	    $(this).css("background", "#666666");
	    selected = $(this);
	}
});
div.hover(
    function() {
        $(this).css("background", "#a8a8a8");
        selected.css("background", "#666666");
    },
    function() {
        $(this).css("background", "#ffffff");
        selected.css("background", "#666666");
    }
);

var div = $("#audio4");
div.click(function() {
    if (state == "play"){
	    selected.css("background", "#ffffff");
	    $(this).css("background", "#666666");
	    selected = $(this);
	}
});
div.hover(
    function() {
        $(this).css("background", "#a8a8a8");
        selected.css("background", "#666666");
    },
    function() {
        $(this).css("background", "#ffffff");
        selected.css("background", "#666666");
    }
);

var div = $("#audio5");
div.click(function() {
    if (state == "play"){
	    selected.css("background", "#ffffff");
	    $(this).css("background", "#666666");
	    selected = $(this);
	}
});
div.hover(
    function() {
        $(this).css("background", "#a8a8a8");
        selected.css("background", "#666666");
    },
    function() {
        $(this).css("background", "#ffffff");
        selected.css("background", "#666666");
    }
);

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var buttonApply = $("#apply");
buttonApply.click(function() {
    console.log("Apply Start");
    var colorPicker = document.getElementById("color");
    var color = colorPicker.options[colorPicker.selectedIndex].text;
    var visualPicker = document.getElementById("visual");
    var visual = visualPicker.options[visualPicker.selectedIndex].text;
    $.ajax({
        url: "/applyCustom",
        data: {
        	Selected: selected.attr('id'),
            Color: color,
            Visual: visual
        },
        type: "POST",
        success: function(response) {
            console.log(response);
        }
    });
});


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

window.addEventListener("unload", function(){
    navigator.sendBeacon("/close");
});
