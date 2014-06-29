=================================
Mobile Web Interface (Mobile WUI)
=================================
-----------
Requirement
-----------
(a copy already included)
	php-gettext 1.0.10
	Savant3 3.0.1


----- 
About 
-----

A very simple web interface targeting mobile browsers. It is programmed in PHP language and uses [[json_web_service|Alfanous JSON Web Service]].

Links:

[[http://mobile.alfanous.org/|mobile.alfanous.org]]\\
[[http://m.alfanous.org/|m.alfanous.org]]

----------
Highlights
----------

  * [[json_web_service|Alfanous JSON service]]: main search service.
  * Mobile web standards: [[http://www.w3.org/TR/xhtml-basic/|XHTML1.1 Basic]] + [[http://www.w3.org/TR/css-mobile/|CSS Mobile]], No JavaScript.
  * PHP: It was selected, because most shared server does not provide python.
  * RTL support: :/ Unfortunately CSS2.1 Mobile is like CSS1 does have 'direction' option and same problem with XHTML, it doesn't have 'dir' attribute. But historically XHTML comes after HTML which has 'dir' attribute. So possibly mobile browsers may support HTML before CSS2. That's why HTML way was chosen to make RTL direction.
  * 'Tashkil': This may count as a bug in mobile browsers, either due to non available glyphs in font or not supported glyphs by OS. Some browsers shows white spaces in place of Tashkil glyphs (wrong behavior, seen on a Samsung S5233 WiFi mobile: Proprietary OS, Jasmine 0.8 browser) instead of omitting them (correct behavior, seen on Android) as they are an addition to the Arabic script.
  * I18n/L10n: Done using [[https://launchpad.net/php-gettext/|php-gettext]] in fallback mode; It tries first the build-in gettext then falls back to external gettext.
  * Template: Done using [[http://phpsavant.com/|Savant3]] template engine.

-----
Tests
-----

  * [[http://m.alfanous.org/|Main Default Page]]
  * [[http://m.alfanous.org/index.php?search=|Search "", Empty Query]]
  * [[http://m.alfanous.org/index.php?search=%D8%A3%D8%AD%D9%85%D8%AF|Search "أحمد", one item in results]]
  * [[http://m.alfanous.org/index.php?search=%D8%A7%D9%84%D9%84%D9%87|Search "الله", more then limit set for results]]
  * [[http://m.alfanous.org/index.php?search=%D9%86%D8%B3%D9%8A%D9%85|Search "نسيم", empty results]]

-----------
Screenshots 
-----------
See [[http://www.alfanous.org/art/screenshot/]]