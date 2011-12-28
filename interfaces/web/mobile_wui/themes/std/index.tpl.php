<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN"
    "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

	<title><? echo $this->mt->ALFANOUS; ?></title>

	<meta http-equiv="Content-Type" content="application/xhtml+xml; 
charset=UTF-8" />
	<link rel="shortcut icon" type="image/gif" href="<?= THEME_DIR . $this->mv->theme; ?>/icon.gif" />

<?php
# CSS1 style
$css = file_get_contents( THEME_DIR . $this->mv->theme . '/basic.css');
echo "<style type=\"text/css\">\n$css\n</style>";
?>

</head>
<body<? echo ($this->mt->RTL)?" dir=\"rtl\"":""; ?>>

	<form id="form_top" class="form" method="get" action="index.php">
		<div class="search_form">
			<img src="<?= THEME_DIR . $this->mv->theme; ?>/icon.gif" width="32" height="32" alt="logo" />
			<span><? echo $this->mt->ALFANOUS; ?></span>
			<input class="search_box" type="text" 
name="search" title="search" inputmode="arabic" />
			<input class="submit" type="submit" value="<? echo $this->mt->SEARCH; ?>" />
			<br />
			<input name="tashkil" type="checkbox"
<? echo ($this->mv->tashkil)?" checked=\"checked\"":""; ?> value="yes" />
<? echo $this->mt->TASHKIL; ?> | 
			<input name="fuzzy" type="checkbox"
<? echo ($this->mv->fuzzy)?" checked=\"checked\"":""; ?> value="yes" />
<? echo $this->mt->FUZZY; ?>
			<br />
			<? echo $this->mt->LANGUAGE; ?>:
			<select name="language">
				<? foreach ($this->mv->locales_list as $l ) {
					echo "<option ".(($l == $this->mv->language)?"selected=\"selected\" ":"")."value=\"$l\">$l</option>";
				}; ?>
			</select> | 
			<? echo $this->mt->THEME; ?>:
			<select name="theme">
				<? foreach ($this->mv->themes_list as $t ) {
					echo "<option ".(($t == $this->mv->theme)?"selected=\"selected\" ":"")."value=\"$t\">$t</option>";
				}; ?>
			</select>
		</div>
	</form>

<? if ($this->mv->search and $this->mv->json and $this->mv->json->interval->total): # case: some results ?>

	<div class='pages'>
		<? echo $this->mt->RESULTS; ?>: <? echo $this->mv->json->interval->start; ?>-<? echo $this->mv->json->interval->end; ?><? echo ($this->mt->RTL)?"\\":"/"; ?><? echo $this->mv->json->interval->total; ?> 
		<? echo $this->mt->PAGES; ?>:
		<?php
			$results_pages = "";
			for ($i = 1; $i <= $this->mv->nb_pages; $i++) {
				if ($i == $this->mv->page_nb) {
					$results_pages .= " ". $i;
				}
				else {
					$results_pages .= sprintf(" <a href='%s'>%s</a>",
						htmlspecialchars("index.php?" . $this->mv->query_search . "&page=" . $i . $this->mv->query_custom),
						$i);
				};
			};
			# show a sign for pages limit '...', a part of pages are not listed
			if ($this->mv->hit_page_limit) $results_pages .= " ...";
			print($results_pages);
		?>
	</div>

	<div id='search_result'>
		<? for( $i = $this->mv->json->interval->start; $i <= $this->mv->json->interval->end; $i++): # Results listing ?>
			<div class='result_item'>
				<div dir='rtl' class='align-right'><span class='item_number'><? echo $i; ?> </span>
					<span class='aya_info'> (<? echo $this->mv->json->ayas->$i->sura->name; ?> <? echo $this->mv->json->ayas->$i->aya->id; ?>) </span></div>
				<div class='quran align-right' dir='rtl'> [ <? echo ($this->mv->tashkil)?$this->mv->json->ayas->$i->aya->text:preg_replace("/[\x{064B}-\x{065F}]/u", "", $this->mv->json->ayas->$i->aya->text); ?> ] </div>
				<div class='aya_details <? echo ($this->mt->RTL)?"align-right":"align-left"; ?>'>
		‎			<? echo $this->mt->WORDS; ?> <? echo $this->mv->json->ayas->$i->stat->words; ?><? echo ($this->mt->RTL)?"\\":"/"; ?><? echo $this->mv->json->ayas->$i->sura->stat->words; ?> 
					- <? echo $this->mt->LETTERS; ?> <? echo $this->mv->json->ayas->$i->stat->letters; ?><? echo ($this->mt->RTL)?"\\":"/"; ?><? echo $this->mv->json->ayas->$i->sura->stat->letters; ?> 
					- <? echo $this->mt->GODNAMES; ?> <? echo $this->mv->json->ayas->$i->stat->godnames; ?><? echo ($this->mt->RTL)?"\\":"/"; ?><? echo $this->mv->json->ayas->$i->sura->stat->godnames; ?>
					<br />
					<? echo $this->mt->HIZB; ?> <? echo $this->mv->json->ayas->$i->position->hizb; ?> 
					- <? echo $this->mt->PAGE; ?> <? echo $this->mv->json->ayas->$i->position->page; ?>
				</div>
			</div>
		<? endfor; ?>
	</div>

	<div class='pages'>
		<? echo $this->mt->RESULTS; ?>: <? echo $this->mv->json->interval->start; ?>-<? echo $this->mv->json->interval->end; ?><? echo ($this->mt->RTL)?"\\":"/"; ?><? echo $this->mv->json->interval->total; ?> 
		<? echo $this->mt->PAGES; ?>: <? print($results_pages); ?>
	</div>

	<form id="form_top" class="form" method="get" action="index.php">
		<div class="search_form">
			<img src="<?= THEME_DIR . $this->mv->theme; ?>/icon.gif" width="32" height="32" alt="logo" />
			<span><? echo $this->mt->ALFANOUS; ?></span>
			<input class="search_box" type="text" 
name="search" title="search" inputmode="arabic" />
			<input class="submit" type="submit" value="<? echo $this->mt->SEARCH; ?>" />
			<br />
			<input name="tashkil" type="checkbox"
<? echo ($this->mv->tashkil)?" checked=\"checked\"":""; ?> value="yes" />
<? echo $this->mt->TASHKIL; ?> | 
			<input name="fuzzy" type="checkbox"
<? echo ($this->mv->fuzzy)?" checked=\"checked\"":""; ?> value="yes" />
<? echo $this->mt->FUZZY; ?>
			<br />
			<? echo $this->mt->LANGUAGE; ?>:
			<select name="language">
				<? foreach ($this->mv->locales_list as $l ) {
					echo "<option ".(($l == $this->mv->language)?"selected=\"selected\" ":"")."value=\"$l\">$l</option>";
				}; ?>
			</select> | 
			<? echo $this->mt->THEME; ?>:
			<select name="theme">
				<? foreach ($this->mv->themes_list as $t ) {
					echo "<option ".(($t == $this->mv->theme)?"selected=\"selected\" ":"")."value=\"$t\">$t</option>";
				}; ?>
			</select>
		</div>
	</form>

<? elseif ($this->mv->search): # case: no results ?>

	<hr />
	<p><? echo $this->mt->NORESULTS; ?></p>

<? else: # case: no query ?>

	<hr />
	<p><? echo $this->mt->ALFANOUS_INTRO; ?></p>

<? endif; ?>

</body>
</html>
