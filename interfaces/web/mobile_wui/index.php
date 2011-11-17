<?php

# Output should be valid for Mobile Web Standards (ie: XHTML1.1 Basic+CSS1)
# There is only one exception concerning RTL support

# HTTP header
header("Content-Type: application/xhtml+xml; charset=UTF-8");
header("Content-Language: ar");

header("Cache-Control: max-age=3600, must-revalidate");
header("Last-Modified: Mon, 13 Oct 2011 00:00:00 GMT");

# Check GET parameters
if (count($_GET)<1) {
		$show_result=False;
	}
	elseif (count($_GET)<2) {
		$search=$_GET["search"];
		$page=1;
		$show_result=True;
	}
	else {
		$search=$_GET["search"];
		$page=$_GET["page"];
		$show_result=True;
	}

# Hidden parameters
$sortedby="mushaf";
$recitation="Mishary Rashid Alafasy";
$translation="None";
$highlight="css";

# Encode JSON query URL
$query_site = "http://www.alfanous.org/json?";
$query_search = "search=" . urlencode($search);
$query_page = "&page=" . urlencode($page);
$query_string =  "&sortedby=" . urlencode($sortedby)
	. "&recitation=" . urlencode($recitation)
	. "&translation=" . urlencode($translation)
	. "&highlight=" . urlencode($highlight);

# JSON query
$handle = fopen($query_site . $query_search . $query_page . $query_string, "rb");
$contents = stream_get_contents($handle);
fclose($handle);

$json = json_decode($contents);
# test
#var_dump($json);

# XHTML header
print('
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN"
    "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

	<title>Alfanous</title>

	<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8" />
	<link rel="shortcut icon" type="image/gif" href="icon.gif" />
');

# CSS1 style
print('
<style type="text/css">

body {
font-size: 1em;
margin: 0px;
padding: 0px;
text-align: center;
}

/* form */
#search_form {
	background-color: #FFF;
}

#search_form img {
	vertical-align: middle;
	margin: 3px 0px 3px 0px;
}

#search_form span {
	font-weight: bold;
	vertical-align: middle;
}

#search_box {
	vertical-align: middle;
}

#submit {
	vertical-align: middle;
}

.pages {
	border-bottom: 1px solid #00F;
	border-top: 1px solid #00F;
}

/* result */
#search_result {
	text-align: right;
}

.result_item {
	background-color: #E8E8E8;
	margin-bottom: 1px;
	border-bottom: 1px solid #000;
}

.item_number {
	height: 1.5em;
}

.aya_info {
}

.quran {
	background-color: #FFF;
	font-size: 1.2em;
	padding: 3px 2px 3px 2px;
}

.match {
	color: #181;
}

.aya_details {
}

.align-left {
	text-align: left;
}
</style>
');

# Body + Search form
print('
</head>
<body dir="rtl">
');

$search_form='
	<form id="form" method="get" action="index.php">
		<div id="search_form">
			<img src="icon.gif" width="32" height="32" alt="logo" />
			<span>الفانوس</span>
			<input id="search_box" type="text" name="search" title="search" inputmode="arabic" />
			<input id="submit" type="submit" value="بحث" />
		</div>
	</form>
';

print($search_form);

if ($show_result) {

# Pages control
$nb_pages = floor(($json->interval->total- 1) / 10)+ 1;
$page_nb = floor(($json->interval->start- 1) / 10)+ 1;

$results_pages = sprintf("<div class='pages'>\nالنتائج: %s-%s\\%s الصفحات:"
	,$json->interval->start
	,$json->interval->end
	,$json->interval->total);
for ($i = 1; $i <= $nb_pages; $i++) {
	if ($i == $page_nb) {
		$results_pages .= " ". $i;
	}
	else {
		$results_pages .= sprintf(" <a href='%s'>%s</a>",htmlspecialchars("index.php?" . $query_search . "&page=" . $i),$i);
	}
}
$results_pages .= "</div>\n";
print($results_pages);

# Results listing
$results = "<div id='search_result'>";
for( $i = $json->interval->start; $i <= $json->interval->end; $i++) {
	$results .= sprintf ("
	<div class='result_item'>
		<div><span class='item_number'>%s </span>
			<span class='aya_info'> (%s %s) </span></div>
		<div class='quran'> [ %s ] </div>
		<div class='aya_details'>
‎			الكلمات %s\\%s - الأحرف %s\\%s - ألفاظ الجلالة %s\\%s
			<br /> الحزب %s - الصفحة %s</div>
	</div>"
	,$i
	,$json->ayas->$i->sura->name,$json->ayas->$i->aya->id
	,$json->ayas->$i->aya->text
	,$json->ayas->$i->stat->words,$json->ayas->$i->sura->stat->words
	,$json->ayas->$i->stat->letters,$json->ayas->$i->sura->stat->letters
	,$json->ayas->$i->stat->godnames,$json->ayas->$i->sura->stat->godnames
	,$json->ayas->$i->position->hizb,$json->ayas->$i->position->page
	);
};
$results .= "</div>";
print($results);

# Pages control again
print($results_pages);

print($search_form);
}
else {
print('
<hr />
<p class="align-left" dir="ltr">Alfanous is a Quranic search engine offers simple and advanced search services in the whole information that Holy Qur’an contains. it is based on the modern approach of information retrieval to get a good-stability and a high-speed search. We want implement some additional features like Highlight, Suggestions, Scoring …etc.</p>
');
};

# Close body
print('
</body>
</html>
');

?>

