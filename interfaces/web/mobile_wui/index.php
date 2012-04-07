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
define("DEFAULT_THEME", "blue");
define("RESULTS_LIMIT", 15);

# Gettext
require_once("./php-gettext/gettext.inc");

# Template engine
require_once "savant3/Savant3.php";
$tpl = new Savant3();

# Variables
class MV {

	public function __construct () {

	# gettext
	$this->domain = "alfanousMWUI";
	$this->encoding = "UTF-8";
	$this->locales_list = array("ar", "en", "fr", "id", "it", "ja", "ms");

	# theme
	$this->themes_list = array("blue", "std");

	# Check GET parameters
	$this->search = isset($_GET["search"]) ? $_GET["search"] : "";
	$this->page = isset($_GET["page"]) ? $_GET["page"] : 1;
	$this->language = isset($_GET["language"]) ? $_GET["language"] : DEFAULT_LOCALE;
	$this->theme = isset($_GET["theme"]) ? $_GET["theme"] : DEFAULT_THEME;
	$this->tashkil = isset($_GET["tashkil"]) ? True : False;
	$this->fuzzy = isset($_GET["fuzzy"]) ? True : False;

	# Check if language & theme supported
		if (! in_array($this->language, $this->locales_list)) {
			# Fallback to 2 char language code and recheck
			$this->language=substr($this->language, 0, 2);
			if (! in_array($this->language, $this->locales_list)) $this->language=DEFAULT_LOCALE;
		};
		if (! in_array($this->theme, $this->themes_list)) $this->theme=DEFAULT_THEME;

	# Hidden JSON query parameters
	$this->sortedby="score";
	$this->recitation="Mishary Rashid Alafasy";
	$this->translation="None";
	$this->highlight="css";

	# Encoded JSON query URL (options)
	$this->query_site = "http://www.alfanous.org/json?";
	$this->query_search = "search=" . urlencode($this->search);
	$this->query_page = "&page=" . urlencode($this->page);
	$this->query_string = "&sortedby=" . urlencode($this->sortedby)
		. "&recitation=" . urlencode($this->recitation)
		. "&translation=" . urlencode($this->translation)
		. "&highlight=" . urlencode($this->highlight);
	$this->query_fuzzy= (($this->fuzzy)?"&fuzzy=yes":"");

	# Custom additional options (NOT for JSON Query, for links & page control)
	$this->query_custom = "&language=" . urlencode($this->language)
		. "&theme=" . urlencode($this->theme)
		. (($this->tashkil)?"&tashkil=yes":"");

	# Current theme path
	$this->theme_dir = THEME_DIR . $this->theme . "/";

	# Dynamically added variables
	/*
	$this->contents; # raw JSON
	$this->json; # decoded JSON
	$this->nb_pages; # number of pages
	$this->page_nb; # current page number
	$this->hit_page_limit; # boolian flag for page limit (currently 100 pages)
	$this->rtl; # boolian flag for RTL language
	*/
	}
}

$mv = new MV();


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

# add direction variable
$mv->rtl = ($mt->DIR == "rtl") ? True : False;

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

	# JSON query
	$handle = fopen($mv->query_site . $mv->query_search . $mv->query_page . $mv->query_string . $mv->query_fuzzy,
		"rb");
	$mv->contents = stream_get_contents($handle);
	fclose($handle);

	$mv->json = json_decode($mv->contents);

	# Pages calculation
	if ($mv->json) {
		# Pages
		$mv->nb_pages = floor(($mv->json->interval->total- 1) / 10)+ 1;
		$mv->page_nb = floor(($mv->json->interval->start- 1) / 10)+ 1;
		# Alfanous JSON service doesn't serve more than 100 pages.
		$mv->hit_page_limit = False;
		if ($mv->nb_pages > RESULTS_LIMIT) {
			$mv->hit_page_limit = True;
			$mv->nb_pages = RESULTS_LIMIT;
		};
	};
};

if (DEBUG and $mv->search) var_dump($mv->json);

# pass variables to template engine
$tpl->mv = $mv;
$tpl->mt = $mt;

# display template
$tpl->display($mv->theme_dir . "index.tpl.php"); 
?>
