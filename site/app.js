// ----------------------------------------------------------------------------
//
// UI for Json Search Engine
//
// ----------------------------------------------------------------------------
$(document).ready(function(){
	
	// prepare db from local json.
	loadDb();  	// NOTE : test in Safari, not Chrome.

	// bind event for debug 
	$("#keyword").change(function(){
		searchInDb();
	})
	
});

function searchInDb(){
	if (true){	// FIXME
		var num = $("#keyword").val();
		var targetEntry = getEntry(num);
		
		if (typeof targetEntry == 'object'){
			show(targetEntry);
		}	
	}	
}

// returns db entry.
function getEntry(index){
	if (db[index] === void 0){ // undefined check
		showInfo("No such entry." + "... id[" + index + "]" );
		return;
	} else { // safe entry
		return db[index];
	}
}

function showInfo(str){
	$("#out").empty();
	
	var mess = '<span>' + str + '</span><br>'
	$("#out").prepend(mess);	
}

function show(entry){
	$("#out").empty();

	// 1: output image. First !
	var childImg = '<img src="image/test.gif">';
	$("#out").append(childImg);

	// 2: output caption or debug info.
	//       id  character  title   body                      image
	//       1   KAZ(32)    ドラム     この世に存在するドラムは\n\n全て俺が叩く\n  http://...
	var cr = "<br>";
	var en = entry;
	
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

// query parameta
// http://www13.plala.or.jp/bigdata/google.html

// https://www.google.co.jp/search?tbm=ischsite:jigokuno.com %E3%81%B9%E3%81%A4%E3%81%AB
// https://www.google.co.jp/search?tbm=isch&q=site:jigokuno.com%20%E5%88%A5%E3%81%AB