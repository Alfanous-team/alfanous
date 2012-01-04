<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN"
    "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

	<title><?= $this->mt->ALFANOUS; ?></title>

	<meta http-equiv="Content-Type" content="application/xhtml+xml; 
charset=UTF-8" />
	<link rel="shortcut icon" type="image/gif" href="<?= $this->mv->theme_dir; ?>icon.gif" />

<!-- embedded css -->
<?
# CSS1(CSS2 Mobile) style / embedded to minimize number of queries
$css = file_get_contents($this->mv->theme_dir . 'basic.css');
echo "<style type=\"text/css\">\n$css\n</style>\n";
?>

</head>
<body<?= ($this->mv->rtl)?" dir=\"rtl\"":""; ?>>

	<!-- top form -->
	<form id="form_top" class="form" method="get" action="index.php">
		<div class="search_form">
			<img src="<?= $this->mv->theme_dir; ?>/icon.gif" width="32" height="32" alt="logo" />
			<span><?= $this->mt->ALFANOUS; ?></span>
			<input class="search_box" type="text" name="search" title="search" inputmode="arabic" />
			<input class="submit" type="submit" value="<?= $this->mt->SEARCH; ?>" />
			<br />
			<input name="tashkil" type="checkbox"<?= ($this->mv->tashkil)?" checked=\"checked\"":""; ?> value="yes" /> <?= $this->mt->TASHKIL; ?> | 
			<input name="fuzzy" type="checkbox"<?= ($this->mv->fuzzy)?" checked=\"checked\"":""; ?> value="yes" /> <?= $this->mt->FUZZY; ?>
			<br />
			<?= $this->mt->LANGUAGE; ?>:
			<select name="language">
				<? foreach ($this->mv->locales_list as $l ) {
					echo "<option ".(($l == $this->mv->language)?"selected=\"selected\" ":"")."value=\"$l\">$l</option>";
				}; ?>
			</select> | 
			<?= $this->mt->THEME; ?>:
			<select name="theme">
				<? foreach ($this->mv->themes_list as $t ) {
					echo "<option ".(($t == $this->mv->theme)?"selected=\"selected\" ":"")."value=\"$t\">$t</option>";
				}; ?>
			</select>
		</div>
	</form>

<? if ($this->mv->search and $this->mv->json and $this->mv->json->interval->total): # case: some results ?>

	<!-- top page control -->
	<div id="pages_top" class="pages">
		" <span><a><?= $this->mv->search; ?></a></span> " | 
		<?= $this->mt->RESULTS; ?>: <span><?= $this->mv->json->interval->start; ?></span>-<span><?= $this->mv->json->interval->end; ?></span><?= ($this->mv->rtl)?"\\":"/"; ?><span><?= $this->mv->json->interval->total; ?></span> 
		<?= $this->mt->PAGES; ?>:
		<span>
		<?
			$results_pages = "";
			for ($i = 1; $i <= $this->mv->nb_pages; $i++) {
				if ($i == $this->mv->page_nb) {
					$results_pages .= " . ". $i;
				}
				else {
					$results_pages .= sprintf(" . <a href='%s'>%s</a>",
						htmlspecialchars("index.php?" . $this->mv->query_search . "&page=" . $i . $this->mv->query_custom . $this->mv->query_fuzzy),
						$i);
				};
			};

			# show a sign for pages limit '...', a part of pages are not listed
			if ($this->mv->hit_page_limit) $results_pages .= " ...";
			echo $results_pages;
		?>
		</span>
	</div>

	<!-- search result -->
	<div id='search_result'>
		<? for( $i = $this->mv->json->interval->start; $i <= $this->mv->json->interval->end; $i++): # Results listing ?>
			<div class='result_item'>
				<div dir='rtl' class='align-right'><span class='item_number'><?= $i; ?> </span>
					(<span class='aya_info'> <?= $this->mv->json->ayas->$i->sura->name; ?> <span><?= $this->mv->json->ayas->$i->aya->id; ?></span> </span>)</div>
				<div class='quran align-right' dir='rtl'> [ <?= ($this->mv->tashkil)?$this->mv->json->ayas->$i->aya->text:preg_replace("/[\x{064B}-\x{065F}]/u", "", $this->mv->json->ayas->$i->aya->text); ?> ] </div>
				<div class='aya_details <?= ($this->mv->rtl)?"align-right":"align-left"; ?>'>
		‎			<?= $this->mt->WORDS; ?> <span><?= $this->mv->json->ayas->$i->stat->words; ?></span><?= ($this->mv->rtl)?"\\":"/"; ?><?= $this->mv->json->ayas->$i->sura->stat->words; ?> 
					- <?= $this->mt->LETTERS; ?> <span><?= $this->mv->json->ayas->$i->stat->letters; ?></span><?= ($this->mv->rtl)?"\\":"/"; ?><?= $this->mv->json->ayas->$i->sura->stat->letters; ?> 
					- <?= $this->mt->GODNAMES; ?> <span><?= $this->mv->json->ayas->$i->stat->godnames; ?></span><?= ($this->mv->rtl)?"\\":"/"; ?><?= $this->mv->json->ayas->$i->sura->stat->godnames; ?>
					<br />
					<?= $this->mt->HIZB; ?> <span><?= $this->mv->json->ayas->$i->position->hizb; ?></span> 
					- <?= $this->mt->PAGE; ?> <span><?= $this->mv->json->ayas->$i->position->page; ?></span>
				</div>
			</div>
		<? endfor; ?>
	</div>

	<!-- bottom page control -->
	<div id="pages_bottom" class="pages">
		" <span><a><?= $this->mv->search; ?></a></span> "
		 | <?= $this->mt->RESULTS; ?>: <span><?= $this->mv->json->interval->start; ?></span>-<span><?= $this->mv->json->interval->end; ?></span><?= ($this->mv->rtl)?"\\":"/"; ?><span><?= $this->mv->json->interval->total; ?></span> 
		<?= $this->mt->PAGES; ?>: <span><?= $results_pages; ?></span>
	</div>

	<!-- bootom form -->
	<form id="form_bottom" class="form" method="get" action="index.php">
		<div class="search_form">
			<img src="<?= $this->mv->theme_dir; ?>/icon.gif" width="32" height="32" alt="logo" />
			<span><?= $this->mt->ALFANOUS; ?></span>
			<input class="search_box" type="text" name="search" title="search" inputmode="arabic" />
			<input class="submit" type="submit" value="<?= $this->mt->SEARCH; ?>" />
			<br />
			<input name="tashkil" type="checkbox"<?= ($this->mv->tashkil)?" checked=\"checked\"":""; ?> value="yes" /> <?= $this->mt->TASHKIL; ?> | 
			<input name="fuzzy" type="checkbox"<?= ($this->mv->fuzzy)?" checked=\"checked\"":""; ?> value="yes" /> <?= $this->mt->FUZZY; ?>
			<br />
			<?= $this->mt->LANGUAGE; ?>:
			<select name="language">
				<? foreach ($this->mv->locales_list as $l ) {
					echo "<option ".(($l == $this->mv->language)?"selected=\"selected\" ":"")."value=\"$l\">$l</option>";
				}; ?>
			</select> | 
			<?= $this->mt->THEME; ?>:
			<select name="theme">
				<? foreach ($this->mv->themes_list as $t ) {
					echo "<option ".(($t == $this->mv->theme)?"selected=\"selected\" ":"")."value=\"$t\">$t</option>";
				}; ?>
			</select>
		</div>
	</form>

<? elseif ($this->mv->search): # case: no results ?>

	<!-- no results msg -->
	<div class="message">
		<p><?= $this->mt->NORESULTS; ?></p>
	</div>

<? else: # case: no query ?>

	<!-- introduction msg -->
	<div class="message">
		<p><?= $this->mt->ALFANOUS_INTRO; ?></p>
	</div>

<? endif; ?>

<div id="footer" dir="ltr">
	<p><a href="http://wiki.alfanous.org/doku.php?id=contributers">Alfanous Team</a> © 2011-2012
	 | <a href="http://www.gnu.org/licenses/agpl.html">AGPL</a> license
	 | powered by <a href="http://wiki.alfanous.org/doku.php?id=json_web_service">Alfanous</a></p>
	<p><a href="https://bugs.launchpad.net/alfanous/">Report a Bug</a>^
	 | <a href="https://translations.launchpad.net/alfanous/trunk/+pots/alfanousmobile">Help translate</a>^
	 | <a href="https://answers.launchpad.net/alfanous/">Ask a question</a>^</p>
</div>

</body>
</html>
