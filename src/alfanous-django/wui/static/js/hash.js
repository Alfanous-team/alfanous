/**
 * @author Mouad
 */

hash_sep = ',';
hash_kv_sep = ':';
// hash_encode = [ ' ',  '#',   ',',   ':',   ];
// hash_decode = [ '+',  '%23', '%2C', '%3A', ];

defaultParams = {
		  action:"search",
	      ident:"alfa001",
	      platform:"undefined",
	      domain:"dj.alfanous.org",
	      query:"",
	      script:"standard",
	      vocalized: "True",
	      highlight: "css",
	      recitation: "1",
	      translation: "None",
	      prev_aya: "False",
	      next_aya: "False",
	      sura_info: "True",
	      word_info: "True",
	      aya_position_info:	"True",
	      aya_theme_info:	"True",
	      aya_stat_info:	"True",
	      aya_sajda_info:	"True",
	      annotation_word:"False",
	      annotation_aya:"False",
	      sortedby:"score",
	      view: "custom",
	      page:"1", 
	      perpage:"10",
	      fuzzy:"False",
}

share_links = {
	// 'twitter_share': "http://twitter.com/home?status=%s %s",
	'twitter_share': "https://twitter.com/share?url=%s&text=%s",
	'facebook_share': "http://www.facebook.com/sharer.php?u=%s&t=%s",
	'buzz_share': "http://www.google.com/buzz/post?url=%s",
	'myspace_share': "http://www.myspace.com/Modules/PostTo/Pages/?u=%s"
};

function parse_params ( param_string ) {
	var couples = param_string.split ( "&" );
	var parsed_params = {};
	for ( var i = 0; i < couples.length; i++ ) {
		var kv = couples[i].split ( "=" );
		parsed_params[kv[0]] = decodeURIComponent ( kv[1] ); 
	}
	return parsed_params;
}

function build_params ( params ) {
	var couples = [];
	for ( var key in params ) {
		if ( params.hasOwnProperty ( key ) ) {
			if ( ! defaultParams.hasOwnProperty ( key ) || defaultParams[key] != params[key] ) {
				couples.push ( key + "=" + encodeURIComponent ( params[key] ) );
			}
		}
	}
	return couples.join ( "&" );
}

function read_params () {
	var idx = document.URL.indexOf ( "?" );
	if ( idx > -1 ) {
		var param_string = document.URL.slice ( idx + 1 );
		if ( param_string.length > 0 ) {
			var params = parse_params ( param_string );
			search_for ( params );
			return true;
		}
	}
	return false;
}

function get_url_without_params () {
	var idx = document.URL.indexOf ( "?" );
	if ( idx > -1 ) {
		return document.URL.substr ( 0, idx );
	}
	else {
		idx = document.URL.indexOf ( "#" );
		if ( idx > -1 ) {
			return document.URL.substr ( 0, idx );
		}
	}
	return document.URL;
}

function parse_hash ( hash ) {
	if ( !hash || hash.length <= 1 ) { return {}; }
	
	hash = hash.slice ( 1 );
	var hash_parts = hash.split ( hash_sep );
	var params = {};
	for ( var i in hash_parts ) {
		var key_value = hash_parts[i].split ( hash_kv_sep );
		params[key_value[0]] = decodeURIComponent ( key_value[1] );
	}
	return params;
}

function build_hash ( params ) {
	var hash_parts = [];
	for ( var key in params ) {
		if ( params.hasOwnProperty ( key ) ) {
			if ( ! defaultParams.hasOwnProperty ( key ) || defaultParams[key] != params[key] ) {
				hash_parts.push ( key + hash_kv_sep + encodeURIComponent ( params[key] ) );
			}
		}
	}
	return hash_parts.join ( hash_sep );
}

function set_search_params ( params ) {
	// parent.location.hash = build_hash ( params );
	// window.location = get_url_without_params () + "?" + build_params ( params );
	$("#search_box").val( params.query );
	$("#recitation").val( params.recitation ); 
	$("#translation").val( params.translation );
	$("#sortedby").val( params.sortedby );
	$("#view").val( params.view );
	document.title = "الفانوس | نتائج البحث عن: " + params.query;
}

function redirect_to_params ( params ) {
	window.location = get_url_without_params () + "?" + build_params ( params );
}

function search_for ( param ) {
	set_search_params ( param );
	for ( key in defaultParams ) {
		if ( defaultParams.hasOwnProperty ( key ) && ! param.hasOwnProperty ( key ) ) {
			param[key] = defaultParams[key];
		}
	}
	
	update_share_links ();
	get_results ( param );
}

function read_hash () {
	var hash = parent.location.hash;

	if ( hash.length > 1 ) {
		search_for ( parse_hash ( hash ) );
		return true;
	}
	return false;
}

function update_share_links () {
	for ( var class_name in share_links ) {
		$( ".follow-box a." + class_name ).attr ( "href", $.sprintf ( share_links[class_name], encodeURIComponent ( document.URL ), encodeURIComponent ( document.title ) ) );
	}
}
