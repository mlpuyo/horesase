// ----------------------------------------------------------------------------
//
// UI for Json Search Engine
//
// ----------------------------------------------------------------------------
$(document).ready(function(){
	
	// prepare db from local json.
	// NOTE: test in Safari, not Chrome.
	loadDb();
	
});

function searchInDb(){
	show();
}

function show(){
	$("#out").empty();

	// FIXME
	// URLをローカルのJSONからレコードを引っ張ってくる

	var childURL = '<span>aaa</span><br>';
	var childImg = '<img src="image/test.gif">';

	$("#out").append(childURL).append(childImg).append("<br>" + db[0].title + "<br>" + db[0].body);
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