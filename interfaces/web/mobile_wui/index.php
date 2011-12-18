<?php

/*******************************************************************************

    Alfanous Web Interface for Mobiles, uses Alfanous JSON service.
    Copyright (C) 2011  Alfanous Team <http://www.alfanous.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

*******************************************************************************/

/*
  Highlights:
   - Output should be valid for Mobile Web Standards (ie: XHTML1.1 Basic + CSS1)
   - There is only one exception concerning RTL support
   - <http://validator.w3.org/mobile/> helps much to check standards
   - CSS is embedded within XHTML output to avoid many requests
   - For I18n/L10n, it uses php-gettext (As fallback)
*/

# Constants
define("DEBUG", 0);
define("M_EXEC", 1);
define("ROOT_DIR", realpath("./")); # or dirname(__FILE__);
define("LOCALE_DIR", ROOT_DIR ."/locale");
define("DEFAULT_LOCALE", "en");
define("THEME_DIR", ROOT_DIR ."/themes/");
define("DEFAULT_THEME", "std");

# Gettext
require_once("./php-gettext/gettext.inc");
$domain = "AlfanousMobile";
$locales_list = array("en", "ar");
$encoding = "UTF-8";

# Theme
$themes_list = array("std");

# Check GET parameters
$search = isset($_GET["search"]) ? $_GET["search"] : "";
$page = isset($_GET["page"]) ? $_GET["page"] : 1;
$language = isset($_GET["language"]) ? $_GET["language"] : DEFAULT_LOCALE;
$tashkil = isset($_GET["tashkil"]) ? True : False;
$fazzy = isset($_GET["fazzy"]) ? True : False;


# Gettext
# set language
putenv("LC_ALL=$language");
T_setlocale(LC_ALL, $language);
# set local
T_bindtextdomain($domain, LOCALE_DIR);
T_bind_textdomain_codeset($domain, $encoding);
T_textdomain($domain);
# import localized texts
require_once "./mobiletext.php";
$mt = new MT();


# HTTP header
header("Content-Type: application/xhtml+xml; charset=UTF-8");
header("Content-Language: ar");

header("Cache-Control: max-age=3600, must-revalidate");
header(sprintf(
	"Last-Modified: %s",
	date("r", filemtime($_SERVER['SCRIPT_FILENAME']))
	));

# Query JSON service
if ($search) {

	# Hidden JSON query parameters
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
		. "&highlight=" . urlencode($highlight)
		. (($fazzy)?"&fuzzy=yes":"");

	# JSON query
	$handle = fopen($query_site . $query_search . $query_page . $query_string,
		"rb");
	$contents = stream_get_contents($handle);
	fclose($handle);

	$json = json_decode($contents);
};
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN"
    "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

	<title><? echo $mt->ALFANOUS; ?></title>

	<meta http-equiv="Content-Type" content="application/xhtml+xml; 
charset=UTF-8" />
	<link rel="shortcut icon" type="image/gif" href="./icon.gif" />

<?php
# CSS1 style
$css = file_get_contents('./basic.css');
echo "<style type=\"text/css\">\n$css\n</style>";
?>

</head>
<body<? echo ($mt->RTL)?" dir=\"rtl\"":""; ?>>

<? if (DEBUG and $search) var_dump($json); ?>

	<form id="form_top" class="form" method="get" action="index.php">
		<div class="search_form">
			<img src="./icon.gif" width="32" height="32" alt="logo" />
			<span><? echo $mt->ALFANOUS; ?></span>
			<input class="search_box" type="text" 
name="search" title="search" inputmode="arabic" />
			<input class="submit" type="submit" value="<? echo $mt->SEARCH; ?>" />
			<br />
			<input name="tashkil" type="checkbox"
<? echo ($tashkil)?" checked=\"checked\"":""; ?> value="yes" />
<? echo $mt->TASHKIL; ?> | 
			<input name="fazzy" type="checkbox"
<? echo ($fazzy)?" checked=\"checked\"":""; ?> value="yes" />
<? echo $mt->FAZZY; ?>
			<br />
			<? echo $mt->LANGUAGE; ?>:
			<select name="language">
				<? foreach ($locales_list as $l ) {
					echo "<option ".(($l == $language)?"selected=\"selected\" ":"")."value=\"$l\">$l</option>";
				}; ?>
			</select> | 
			<? echo $mt->THEME; ?>:
			<select name="theme">
				<? foreach ($themes_list as $t ) {
					echo "<option ".(($t == $theme)?"selected=\"selected\" ":"")."value=\"$t\">$t</option>";
				}; ?>
			</select>
		</div>
	</form>

<?php
if ($search and $json and $json->interval->total): # case: some results

	# Pages control
	$nb_pages = floor(($json->interval->total- 1) / 10)+ 1;
	$page_nb = floor(($json->interval->start- 1) / 10)+ 1;
	# Alfanous JSON service doesn't serve more than 100 pages.
	$hit_page_limit = False;
	if ($nb_pages > 100) {
		$hit_page_limit = True;
		$nb_pages = 100;
	};
?>

	<div class='pages'><? echo $mt->RESULTS; ?>: 
		<? echo $json->interval->start; ?>-<? echo $json->interval->end; ?><? echo ($mt->RTL)?"\\":"/"; ?><? echo $json->interval->total; ?> 
		<? echo $mt->PAGES; ?>:

<?php
	$results_pages = "";
	for ($i = 1; $i <= $nb_pages; $i++) {
		if ($i == $page_nb) {
			$results_pages .= " ". $i;
		}
		else {
			$results_pages .= sprintf(" <a href='%s'>%s</a>",
				htmlspecialchars("index.php?" . $query_search . "&page=" . $i),
				$i);
		};
	};
	# show a sign for pages limit '...', a part of pages are not listed
	if ($hit_page_limit) $results_pages .= " ...";
	print($results_pages);
?>
	</div>

	<div id='search_result'>
<?php
	# Results listing
	for( $i = $json->interval->start; $i <= $json->interval->end; $i++): ?>

		<div class='result_item'>
			<div dir='rtl' class='align-right'><span class='item_number'><? echo $i; ?> </span>
				<span class='aya_info'> (<? echo $json->ayas->$i->sura->name; ?> <? echo $json->ayas->$i->aya->id; ?>) </span></div>
			<div class='quran align-right' dir='rtl'> [ <? echo ($tashkil)?$json->ayas->$i->aya->text:preg_replace("/[\x{064B}-\x{065F}]/u", "", $json->ayas->$i->aya->text); ?> ] </div>
			<div class='aya_details <? echo ($mt->RTL)?"align-right":"align-left"; ?>'>
	‎			<? echo $mt->WORDS; ?> 
	<? echo $json->ayas->$i->stat->words; ?><? echo ($mt->RTL)?"\\":"/"; ?><? echo $json->ayas->$i->sura->stat->words; ?> 
				- <? echo $mt->LETTERS; ?> 
	<? echo $json->ayas->$i->stat->letters; ?><? echo ($mt->RTL)?"\\":"/"; ?><? echo $json->ayas->$i->sura->stat->letters; ?> 
				- <? echo $mt->GODNAMES; ?> 
	<? echo $json->ayas->$i->stat->godnames; ?><? echo ($mt->RTL)?"\\":"/"; ?><? echo $json->ayas->$i->sura->stat->godnames; ?>
				<br />
				<? echo $mt->HIZB; ?> 
	<? echo $json->ayas->$i->position->hizb; ?> 
				- <? echo $mt->PAGE; ?> 
	<? echo $json->ayas->$i->position->page; ?></div>
		</div>

<? endfor; ?>
	</div>

	<div class='pages'>
		<? echo $mt->RESULTS; ?>: 
		<? echo $json->interval->start; ?>-<? echo $json->interval->end; ?><? echo ($mt->RTL)?"\\":"/"; ?><? echo $json->interval->total; ?> 
		<? echo $mt->PAGES; ?>:
		<? print($results_pages); ?>
	</div>

	<form id="form_top" class="form" method="get" action="index.php">
		<div class="search_form">
			<img src="./icon.gif" width="32" height="32" alt="logo" />
			<span><? echo $mt->ALFANOUS; ?></span>
			<input class="search_box" type="text" 
name="search" title="search" inputmode="arabic" />
			<input class="submit" type="submit" value="<? echo $mt->SEARCH; ?>" />
			<br />
			<input name="tashkil" type="checkbox"
<? echo ($tashkil)?" checked=\"checked\"":""; ?> value="yes" />
<? echo $mt->TASHKIL; ?> | 
			<input name="fazzy" type="checkbox"
<? echo ($fazzy)?" checked=\"checked\"":""; ?> value="yes" />
<? echo $mt->FAZZY; ?>
			<br />
			<? echo $mt->LANGUAGE; ?>:
			<select name="language">
				<? foreach ($locales_list as $l ) {
					echo "<option ".(($l == $language)?"selected=\"selected\" ":"")."value=\"$l\">$l</option>";
				}; ?>
			</select> | 
			<? echo $mt->THEME; ?>:
			<select name="theme">
				<? foreach ($themes_list as $t ) {
					echo "<option ".(($t == $theme)?"selected=\"selected\" ":"")."value=\"$t\">$t</option>";
				}; ?>
			</select>
		</div>
	</form>

<? elseif ($search): # case: no results ?>

	<hr />
	<p><? echo $mt->NORESULTS; ?></p>

<? else: # case: no query ?>

	<hr />
	<p><? echo $mt->ALFANOUS_INTRO; ?></p>

<? endif; ?>

</body>
</html>
