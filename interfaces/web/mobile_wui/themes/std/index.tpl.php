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
			<input name="tashkil" type="checkbox"<?= ($this->mv->tashkil)?" checked=\"checked\"":""; ?> value="yes" /><?= $this->mt->TASHKIL; ?> | 
			<input name="fuzzy" type="checkbox"<?= ($this->mv->fuzzy)?" checked=\"checked\"":""; ?> value="yes" /><?= $this->mt->FUZZY; ?>
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
	<div class='pages'>
		<?= $this->mt->RESULTS; ?>: <?= $this->mv->json->interval->start; ?>-<?= $this->mv->json->interval->end; ?><?= ($this->mv->rtl)?"\\":"/"; ?><?= $this->mv->json->interval->total; ?> 
		<?= $this->mt->PAGES; ?>:
		<?
			$results_pages = "";
			for ($i = 1; $i <= $this->mv->nb_pages; $i++) {
				if ($i == $this->mv->page_nb) {
					$results_pages .= " ". $i;
				}
				else {
					$results_pages .= sprintf(" <a href='%s'>%s</a>",
						htmlspecialchars("index.php?" . $this->mv->query_search . "&page=" . $i . $this->mv->query_custom . $this->mv->query_fuzzy),
						$i);
				};
			};
			# show a sign for pages limit '...', a part of pages are not listed
			if ($this->mv->hit_page_limit) $results_pages .= " ...";
			echo $results_pages;
		?>
	</div>

	<!-- search result -->
	<div id='search_result'>
		<? for( $i = $this->mv->json->interval->start; $i <= $this->mv->json->interval->end; $i++): # Results listing ?>
			<div class='result_item'>
				<div dir='rtl' class='align-right'><span class='item_number'><?= $i; ?> </span>
					<span class='aya_info'> (<?= $this->mv->json->ayas->$i->sura->name; ?> <?= $this->mv->json->ayas->$i->aya->id; ?>) </span></div>
				<div class='quran align-right' dir='rtl'> [ <?= ($this->mv->tashkil)?$this->mv->json->ayas->$i->aya->text:preg_replace("/[\x{064B}-\x{065F}]/u", "", $this->mv->json->ayas->$i->aya->text); ?> ] </div>
				<div class='aya_details <?= ($this->mv->rtl)?"align-right":"align-left"; ?>'>
		‎			<?= $this->mt->WORDS; ?> <?= $this->mv->json->ayas->$i->stat->words; ?><?= ($this->mv->rtl)?"\\":"/"; ?><?= $this->mv->json->ayas->$i->sura->stat->words; ?> 
					- <?= $this->mt->LETTERS; ?> <?= $this->mv->json->ayas->$i->stat->letters; ?><?= ($this->mv->rtl)?"\\":"/"; ?><?= $this->mv->json->ayas->$i->sura->stat->letters; ?> 
					- <?= $this->mt->GODNAMES; ?> <?= $this->mv->json->ayas->$i->stat->godnames; ?><?= ($this->mv->rtl)?"\\":"/"; ?><?= $this->mv->json->ayas->$i->sura->stat->godnames; ?>
					<br />
					<?= $this->mt->HIZB; ?> <?= $this->mv->json->ayas->$i->position->hizb; ?> 
					- <?= $this->mt->PAGE; ?> <?= $this->mv->json->ayas->$i->position->page; ?>
				</div>
			</div>
		<? endfor; ?>
	</div>

	<!-- bottom page control -->
	<div class='pages'>
		<?= $this->mt->RESULTS; ?>: <?= $this->mv->json->interval->start; ?>-<?= $this->mv->json->interval->end; ?><?= ($this->mv->rtl)?"\\":"/"; ?><?= $this->mv->json->interval->total; ?> 
		<?= $this->mt->PAGES; ?>: <?= $results_pages; ?>
	</div>

	<!-- bootom form -->
	<form id="form_bottom" class="form" method="get" action="index.php">
		<div class="search_form">
			<img src="<?= $this->mv->theme_dir; ?>/icon.gif" width="32" height="32" alt="logo" />
			<span><?= $this->mt->ALFANOUS; ?></span>
			<input class="search_box" type="text" name="search" title="search" inputmode="arabic" />
			<input class="submit" type="submit" value="<?= $this->mt->SEARCH; ?>" />
			<br />
			<input name="tashkil" type="checkbox"<?= ($this->mv->tashkil)?" checked=\"checked\"":""; ?> value="yes" /><?= $this->mt->TASHKIL; ?> | 
			<input name="fuzzy" type="checkbox"<?= ($this->mv->fuzzy)?" checked=\"checked\"":""; ?> value="yes" /><?= $this->mt->FUZZY; ?>
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

	<hr />
	<!-- no results msg -->
	<p><?= $this->mt->NORESULTS; ?></p>

<? else: # case: no query ?>

	<hr />
	<!-- introduction msg -->
	<p><?= $this->mt->ALFANOUS_INTRO; ?></p>

<? endif; ?>

</body>
</html>
