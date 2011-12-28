<?php

/*******************************************************************************

    Alfanous Web Interface for Mobiles, uses Alfanous JSON service.
    Copyright (C) 2011  Abdellah Chelli, Alfanous Team <http://www.alfanous.org>

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
   - Template engine, Savant3
*/

# Constants
define("DEBUG", 0);
define("M_EXEC", 1);
define("ROOT_DIR", realpath("./")); # or dirname(__FILE__);
define("LOCALE_DIR", ROOT_DIR ."/locale");
define("DEFAULT_LOCALE", "en");
define("THEME_DIR", "./themes/"); # absulute path didn't work with Savant3
define("DEFAULT_THEME", "std");

require_once "savant3/Savant3.php";
$tpl = new Savant3();

# variables
class MV {

	public function __construct () {

	# gettext
	$this->domain = "alfanousMWUI";
	$this->encoding = "UTF-8";
	$this->locales_list = array("en", "ar");

	# theme
	$this->themes_list = array("std");

	# Check GET parameters
	$this->search = isset($_GET["search"]) ? $_GET["search"] : "";
	$this->page = isset($_GET["page"]) ? $_GET["page"] : 1;
	$this->language = isset($_GET["language"]) ? $_GET["language"] : DEFAULT_LOCALE;
	if (! in_array($this->language, $this->locales_list)) $mv->language=DEFAULT_LOCALE;
	$this->theme = isset($_GET["theme"]) ? $_GET["theme"] : DEFAULT_THEME;
	if (! in_array($this->theme, $this->themes_list)) $mv->theme=DEFAULT_THEME;
	$this->tashkil = isset($_GET["tashkil"]) ? True : False;
	$this->fuzzy = isset($_GET["fuzzy"]) ? True : False;

	# Hidden JSON query parameters
	$this->sortedby="mushaf";
	$this->recitation="Mishary Rashid Alafasy";
	$this->translation="None";
	$this->highlight="css";

	}
}

$mv = new MV();


# Gettext
require_once("./php-gettext/gettext.inc");

# Gettext
# set language
putenv("LC_ALL=$mv->language");
T_setlocale(LC_ALL, $mv->language);
# set local
T_bindtextdomain($mv->domain, LOCALE_DIR);
T_bind_textdomain_codeset($mv->domain, $mv->encoding);
T_textdomain($mv->domain);
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
if ($mv->search) {
/*
	# Hidden JSON query parameters
	$mv->sortedby="mushaf";
	$mv->recitation="Mishary Rashid Alafasy";
	$mv->translation="None";
	$mv->highlight="css";
*/
	# Encode JSON query URL
	$mv->query_site = "http://www.alfanous.org/json?";
	$mv->query_search = "search=" . urlencode($mv->search);
	$mv->query_page = "&page=" . urlencode($mv->page);
	$mv->query_string = "&sortedby=" . urlencode($mv->sortedby)
		. "&recitation=" . urlencode($mv->recitation)
		. "&translation=" . urlencode($mv->translation)
		. "&highlight=" . urlencode($mv->highlight)
		. (($mv->fuzzy)?"&fuzzy=yes":"");

	# Custom additional options (NOT for JSON Query)
	$mv->query_custom = "&language=" . urlencode($mv->language)
		. "&theme=" . urlencode($mv->theme)
		. (($mv->tashkil)?"&tashkil=yes":"")
		. (($mv->fuzzy)?"&fuzzy=yes":"");

	# JSON query
	$handle = fopen($mv->query_site . $mv->query_search . $mv->query_page . $mv->query_string,
		"rb");
	$contents = stream_get_contents($handle);
	fclose($handle);

	$mv->json = json_decode($contents);

	if ($mv->json) {
		# Pages
		$mv->nb_pages = floor(($mv->json->interval->total- 1) / 10)+ 1;
		$mv->page_nb = floor(($mv->json->interval->start- 1) / 10)+ 1;
		# Alfanous JSON service doesn't serve more than 100 pages.
		$mv->hit_page_limit = False;
		if ($mv->nb_pages > 100) {
			$mv->hit_page_limit = True;
			$mv->nb_pages = 100;
		};
	};
};

if (DEBUG and $mv->search) var_dump($mv->json);

# pass variables to template engine
$tpl->mv = $mv;
$tpl->mt = $mt;

# display template
$tpl->display(THEME_DIR . $mv->theme . "/index.tpl.php"); 
?>
