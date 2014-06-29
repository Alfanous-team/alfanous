

function prepare_advanced_query(text, option ) {
	switch(option)
	{
		case "phrase":
		  return "\"" + text + "\"";
		  break;
		case "partofwords":
			return "*" + text.replace(/ /g,'') + "*";
		  break;
		case "allwords":
			return text.split(" ").join(" + ");
		  break;
		case "somewords":
			return text.split(" ").join(" | ");
		  break;
		case "exceptwords":
			return text.split(" ").join(" - ");
		  break;
		case "synonyms":
			return "~" +  text.replace(/ /g,'') ;
		  break;
		case "partialvocalization":
			return "aya_:'" +  text.replace(/ /g,'') + "'";
		  break;
		case "lightstemming":
			return ">" + text.replace(/ /g,'');
		  break;
		case "deepstemming":
			return ">>" + text.replace(/ /g,'');
		  break;
	default:
	  return text;
	}
	
}

function prepare_word_properties(root, type ) {
	
	return "{" + root + "،" + type + "}";
}

function prepare_topics(chapter, topic, subtopic ) {
	
	return "فصل:\"" + chapter + "\"";
}

function prepare_structures(unit, from, to ) {
	
	return unit + ":[ " + from + " to " + to + " ]";
}
function prepare_statistics(bunit,gunit,  from, to ) {
	
	return gunit+  "_" + bunit + ":[ " + from + " to " + to + " ]";
}

function prepare_search_by_id(sura_name, aya_id) {
	
	return "sura:\""  + sura_name + "\" +  aya_id:" + aya_id ;
}


function AddToSearchBar(query, relation) {

var old_query = $("#appendedInputButtons").val();
var new_query = "";
switch(relation)
{
	case "replace":
	  new_query = query;
	  break;
	case "add":
		new_query = old_query + " " +query;
	  break;
	case "and":
		new_query = "(" + old_query + ") + " +query;
	  break;
	case "or":
		new_query = "(" +old_query + ") | " +query;
	  break;
	case "andnot":
		new_query = "(" +old_query + ") - " +query;
	  break;
	default:
		  return new_query = query;
}
	
$("#appendedInputButtons").val(new_query);
	
	
}