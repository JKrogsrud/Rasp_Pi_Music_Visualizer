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
var applied = false;
buttonPlay.click(function() {
	var canProceed = false;
	for (i = 1; i <= 5; i++) {
		if (document.getElementById("audio" + String(i)).textContent != "") {
			canProceed = true;
		} 
	}
	if (canProceed == true && applied) {
	    if (state == "play") {
	        console.log("Play Audio");
	        state = "playing";
	        document.getElementById("play-image").remove();
	        document.getElementById("play-pause").textContent = "Playing";
	        $.ajax({
	            url: "/play",
	            type: "POST",
	            data: {
	            	Selected: selected.attr('id')
	            },
	            success: function(response) {
	                state = "play";
                    applied = false;
	                console.log(response);
	                document.getElementById("play-pause").textContent = "";
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
	if (state == "play") {
		selected.css("background", "rgb(101, 65, 201, 0.1)");
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
    	$(this).css("background", "rgb(101, 65, 201, 0.1)");
        selected.css("background", "#666666");
    }
);

var div = $("#audio2");
div.click(function() {
	if (state == "play") {
		selected.css("background", "rgb(101, 65, 201, 0.1)");
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
        $(this).css("background", "rgb(101, 65, 201, 0.1)");
        selected.css("background", "#666666");
    }
);

var div = $("#audio3");
div.click(function() {
	if (state == "play") {
		selected.css("background", "rgb(101, 65, 201, 0.1)");
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
    	$(this).css("background", "rgb(101, 65, 201, 0.5)");
        selected.css("background", "#666666");
    }
);

var div = $("#audio4");
div.click(function() {
	if (state == "play") {
		selected.css("background", "rgb(101, 65, 201, 0.1)");
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
    	$(this).css("background", "rgb(101, 65, 201, 0.1)");
        selected.css("background", "#666666");
    }
);

var div = $("#audio5");
div.click(function() {
	if (state == "play") {
		selected.css("background", "rgb(101, 65, 201, 0.1)");
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
    	$(this).css("background", "rgb(101, 65, 201, 0.1)");
        selected.css("background", "#666666");
    }
);

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var visual;

function validateInput(low, high) {
	/*if (low > 0 && low + 16 < high && high < 22000) {
        if (!isNaN(low) && !isNaN(high)) {
            low = Number(low);
            high = Number(high);
            if (Number.isInteger(low) && Number.isInteger(high)) {
                return true;
            }
            else {
                return false;
            }
        }
        else {
            return false;
        }
	}
	else {
		return false;
	}*/
    return true;
}

var buttonNext = $("#next");
buttonNext.click(function() {
	console.log("Next");

    let applyButton = document.createElement("button");
    applyButton.innerHTML = "Apply";
    applyButton.setAttribute("id", "button");
    applyButton.setAttribute("type", "button");
    applyButton.addEventListener("click", function() {
    	console.log("Apply Start");
        applied = true;
	    if (visual == "CLASSIC BARS") {
	    	var low = document.getElementById("lowInput").value;
	    	var high = document.getElementById("highInput").value;
	    	if (validateInput(low, high)) { 
	    		var barColorPicker = document.getElementById("barColor");
	    		var barColor = barColorPicker.options[barColorPicker.selectedIndex].text.toUpperCase();
		    	$.ajax({
		            url: "/applyCustom",
		            data: {
		                Selected: selected.attr('id'),
		                Visual: visual,
		                Option1: low,
		                Option2: high,
		                Option3: barColor
		            },
		            type: "POST",
		            success: function(response) {
		                console.log(response);
		            }
		        });
	    	}
	    	else {
                document.getElementById("warning").innerHTML = "You entered invalid input in one or both of the above text fields. Please try again.";
	    	}
	    }
	    else if (visual == "CELESTIAL ORBS") {
	    	var bassColorPicker = document.getElementById("bassColor");
	    	var bassColor = bassColorPicker.options[bassColorPicker.selectedIndex].text.toUpperCase();
	    	var midColorPicker = document.getElementById("midColor");
	    	var midColor = midColorPicker.options[midColorPicker.selectedIndex].text.toUpperCase();
	    	var trebleColorPicker = document.getElementById("trebleColor");
	    	var trebleColor = trebleColorPicker.options[trebleColorPicker.selectedIndex].text.toUpperCase();
	    	$.ajax({
	            url: "/applyCustom",
	            data: {
	                Selected: selected.attr('id'),
	                Visual: visual,
	                Option1: bassColor,
	                Option2: midColor,
	                Option3: trebleColor
	            },
	            type: "POST",
	            success: function(response) {
	                console.log(response);
	            }
	        });
	    }
    });

	var visualPicker = document.getElementById("visual");
    var visual = visualPicker.options[visualPicker.selectedIndex].text.toUpperCase();
    if (visual == "CLASSIC BARS") {
    	document.getElementById("next").remove();
        document.getElementById("warning").innerHTML = "";

    	lowLabel = document.createElement("label");
        lowLabel.setAttribute("for", "lowInput");
        lowLabel.innerHTML = "Select Lower Boundary (1 - 21999):";
        lowInput = document.createElement("input");
        lowInput.setAttribute("id", "lowInput");
        lowInput.setAttribute("type", "text");
        lowInput.setAttribute("name", "lowInput");

        highLabel = document.createElement("label");
        highLabel.setAttribute("for", "highInput");
        highLabel.innerHTML = "Select Higher Boundary (1 - 21999):";
        highInput = document.createElement("input");
        highInput.setAttribute("id", "highInput");
        highInput.setAttribute("type", "text");
        highInput.setAttribute("name", "highInput");

        let barText = document.createElement("div");
        barText.innerHTML = "Color: ";
        let barColorSelect = document.createElement("select");
        barColorSelect.setAttribute("id", "barColor");
        let barColorOptionRed = document.createElement("option");
        barColorOptionRed.setAttribute("id", "red");
        barColorOptionRed.innerHTML = "Red";
        let barColorOptionGreen = document.createElement("option");
        barColorOptionGreen.setAttribute("id", "green");
        barColorOptionGreen.innerHTML = "Green";
        let barColorOptionBlue = document.createElement("option");
        barColorOptionBlue.setAttribute("id", "blue");
        barColorOptionBlue.innerHTML = "Blue";

        let customForm = document.getElementById("customForm");
        document.getElementById("visual").remove();
        document.getElementById("visualReminder").innerHTML = "Visual Selection: Classic Bars";
        customForm.appendChild(document.createElement("br"));
        customForm.appendChild(lowLabel);
        customForm.appendChild(lowInput);
        customForm.appendChild(document.createElement("br"));
        customForm.appendChild(highLabel);
        customForm.appendChild(highInput);
        customForm.appendChild(barText);
        customForm.appendChild(barColorSelect);
        barColorSelect.appendChild(barColorOptionRed);
        barColorSelect.appendChild(barColorOptionGreen);
        barColorSelect.appendChild(barColorOptionBlue);
        customForm.appendChild(applyButton);

    }
    else if (visual == "CELESTIAL ORBS") {
    	document.getElementById("next").remove();
        document.getElementById("warning").innerHTML = "";

        let bassText = document.createElement("div");
        bassText.innerHTML = "Bass: ";
        let bassColorSelect = document.createElement("select");
        bassColorSelect.setAttribute("id", "bassColor");
        let bassColorOptionRed = document.createElement("option");
        bassColorOptionRed.setAttribute("id", "bassRed");
        bassColorOptionRed.innerHTML = "Red";
        let bassColorOptionGreen = document.createElement("option");
        bassColorOptionGreen.setAttribute("id", "bassGreen");
        bassColorOptionGreen.innerHTML = "Green";
        let bassColorOptionBlue = document.createElement("option");
        bassColorOptionBlue.setAttribute("id", "bassBlue");
        bassColorOptionBlue.innerHTML = "Blue";

        let midText = document.createElement("div");
        midText.innerHTML = "Midrange: ";
        let midColorSelect = document.createElement("select");
        midColorSelect.setAttribute("id", "midColor");
        let midColorOptionRed = document.createElement("option");
        midColorOptionRed.setAttribute("id", "midRed");
        midColorOptionRed.innerHTML = "Red";
        let midColorOptionGreen = document.createElement("option");
        midColorOptionGreen.setAttribute("id", "midGreen");
        midColorOptionGreen.innerHTML = "Green";
        let midColorOptionBlue = document.createElement("option");
        midColorOptionBlue.setAttribute("id", "midBlue");
        midColorOptionBlue.innerHTML = "Blue";

        let trebleText = document.createElement("div");
        trebleText.innerHTML = "Treble: ";
        let trebleColorSelect = document.createElement("select");
        trebleColorSelect.setAttribute("id", "trebleColor");
        let trebleColorOptionRed = document.createElement("option");
        trebleColorOptionRed.setAttribute("id", "trebleRed");
        trebleColorOptionRed.innerHTML = "Red";
        let trebleColorOptionGreen = document.createElement("option");
        trebleColorOptionGreen.setAttribute("id", "trebleGreen");
        trebleColorOptionGreen.innerHTML = "Green";
        let trebleColorOptionBlue = document.createElement("option");
        trebleColorOptionBlue.setAttribute("id", "trebleBlue");
        trebleColorOptionBlue.innerHTML = "Blue";

        let customForm = document.getElementById("customForm");
        document.getElementById("visual").remove();
        document.getElementById("visualReminder").innerHTML = "Visual Selection: Celestial Orbs";
        customForm.appendChild(bassText);
        customForm.appendChild(bassColorSelect);
        bassColorSelect.appendChild(bassColorOptionRed);
        bassColorSelect.appendChild(bassColorOptionGreen);
        bassColorSelect.appendChild(bassColorOptionBlue);
        customForm.appendChild(midText);
        customForm.appendChild(midColorSelect);
        midColorSelect.appendChild(midColorOptionRed);
        midColorSelect.appendChild(midColorOptionGreen);
        midColorSelect.appendChild(midColorOptionBlue);
        customForm.appendChild(trebleText);
        customForm.appendChild(trebleColorSelect);
        trebleColorSelect.appendChild(trebleColorOptionRed);
        trebleColorSelect.appendChild(trebleColorOptionGreen);
        trebleColorSelect.appendChild(trebleColorOptionBlue);
        customForm.appendChild(applyButton);
    }
    else {
        document.getElementById("warning").innerHTML = "What you selected is not an option. Please try again.";
    }
});



/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

window.addEventListener("unload", function(){
    navigator.sendBeacon("/close");
});
