// ----------------------------------------------------------------------------
//
// UI for Json Search Engine
//
// ----------------------------------------------------------------------------
$(document).ready(function(){
	
	// prepare db from local json.
	loadDb();  	// NOTE : test in Safari, not Chrome.
	
});

function searchInDb(){
	show();
}

function show(){
	$("#out").empty();

	// 1: output image. First !
	var childImg = '<img src="image/test.gif">';
	$("#out").append(childImg);

	// 2: output caption or debug info.
	//       id  character  title   body                      image
	//       1   KAZ(32)    ドラム     この世に存在するドラムは\n\n全て俺が叩く\n  http://...
	var cr = "<br>";
	var en = db[0]; // entry
	
	// TODO : set attr (hankaku font)
	$("#out").append(
		  cr
		+ padSpace("character:", 4) + en.character
		+ cr
		+ padSpace("title:", 8)     + en.title 
		+ cr 
		+ padSpace("body:", 9)      + en.body);
}

function padSpace(targetStr, times ) {
	var spaces = ""; var ws = "&nbsp;" 

	for (var i=0; i<times; i++){
		spaces += ws;
	}
	return targetStr + spaces;
}

//
// Utilities ...
//
var db;

function loadDb(){
	$.get("data/dummy.json", function(data){ 
		db = $.parseJSON(data); 
	});
}

// ----------------------------------------------------------------------------
//
//  UI for Google Image Search
//
// ----------------------------------------------------------------------------
var googleQuery = "&q=site:jigokuno.com"; // image search
var googleImageSearchURL = "https://www.google.co.jp/search?tbm=isch"

function search(){
	var keyword = " " + $("#keyword").val();
	var url = googleImageSearchURL + googleQuery + encodeURI(keyword);
	$(location).attr("href", url);
}
