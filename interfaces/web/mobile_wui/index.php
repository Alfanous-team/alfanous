<?php

header("Content-Type: application/xhtml+xml; charset=UTF-8");
header("Content-Language: ar");

header("Cache-Control: max-age=3600, must-revalidate");
header("Last-Modified: Mon, 13 Oct 2011 00:00:00 GMT");

if (count($_GET)<2) {
		$search = "الحمد";
		$page=1;
	}
	else {
		$search=$_GET["search"];
		$page=$_GET["page"];
	}

$sortedby="mushaf";
$recitation="Mishary Rashid Alafasy";
$translation="None";
$highlight="css";

$query_site = "http://www.alfanous.org/json?";
$query_search = "search=" . urlencode($search);
$query_page = "&page=" . urlencode($page);
$query_string =  "&sortedby=" . urlencode($sortedby)
	. "&recitation=" . urlencode($recitation)
	. "&translation=" . urlencode($translation)
	. "&highlight=" . urlencode($highlight);


$handle = fopen($query_site . $query_search . $query_page . $query_string, "rb");
$contents = stream_get_contents($handle);
fclose($handle);

$json = json_decode($contents);
#var_dump($json);

print('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN"
    "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

	<title>Alfanous | Advanced Quran Search</title>

	<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8" />
	<link rel="shortcut icon" type="image/gif" href="icon.gif" />

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
	border-bottom: 1px solid #00F;
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
	border-bottom: 1px solid #000;
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
</style>

</head>
<body dir="rtl">

	<form id="form" method="get" action="index.php">
		<div id="search_form">
			<img src="icon.gif" width="32" height="32" alt="logo" />
			<span>الفانوس</span>
			<input id="search_box" type="text" name="search" title="search" inputmode="arabic" />
			<input id="submit" type="submit" value="بحث" />
		</div>
	</form>
	');

$nb_pages = floor(($json->interval->total- 1) / 10)+ 1;
$page_nb = floor(($json->interval->start- 1) / 10)+ 1;

$results_pages = "<div class='pages'>\nالنتائج: " . $json->interval->start . "-" . $json->interval->end . "\\" . $json->interval->total . " الصفحات:";
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

$results = "<div id='search_result'>";
for( $i = $json->interval->start; $i <= $json->interval->end; $i++) {
	$results .= "<div class='result_item'>";
	$results .= "<div><span class='item_number'>" . $i . " </span>";
	$results .= "<span class='aya_info'> (" . $json->ayas->$i->sura->name . " " . $json->ayas->$i->aya->id . ") </span></div>";
	$results .= "<div class='quran'> [ " . $json->ayas->$i->aya->text . " ] </div>";
	$results .= "<div class='aya_details'>";
		$results .= "الكلمات " . $json->ayas->$i->stat->words . "\\" . $json->ayas->$i->sura->stat->words;
		$results .= " - الأحرف " . $json->ayas->$i->stat->letters . "\\" . $json->ayas->$i->sura->stat->letters;
		$results .= " - ألفاظ الجلالة " . $json->ayas->$i->stat->godnames. "\\". $json->ayas->$i->sura->stat->godnames;
		$results .= "<br /> الحزب " . $json->ayas->$i->position->hizb;
		$results .= " - الصفحة " . $json->ayas->$i->position->page;
		$results .= "</div>";
	$results .= "</div>";
};
$results .= "</div>";
print($results);

print('
</body>
</html>
');

?>

