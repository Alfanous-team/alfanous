<?php

defined('M_EXEC') or die('Restricted access');

class MT {

public function __construct () {
		$this->ALFANOUS = T_("Alfanous");
		$this->ALFANOUS_INTRO = T_("Alfanous is a Quranic search engine offers 
	simple and advanced search services in the whole information that Holy Qur’an 
	contains. it is based on the modern approach of information retrieval to get a 
	good-stability and a high-speed search. We want implement some additional 
	features like Highlight, Suggestions, Scoring …etc.");
		$this->NORESULTS = T_("Oops, Nothing found.");

		$this->SEARCH = T_("Search");
		$this->TASHKIL = T_("Tashkil");
		$this->FUZZY = T_("Fuzzy");
		$this->LANGUAGE = T_("Language");
		$this->THEME = T_("Theme");
		$this->RESULTS = T_("Results");
		$this->PAGES = T_("Pages");

		$this->WORDS = T_("Words");
		$this->LETTERS = T_("Letters");
		$this->GODNAMES = T_("God's Names");

		$this->AYA = T_("Aya's");
		$this->SUBJECT = T_("Subject");
		$this->CHAPTER = T_("Chapter");
		$this->TOPIC = T_("Topic");
		$this->SUBTOPIC = T_("Subtopic");
		$this->SURA = T_("Sura");
		$this->JUZ = T_("Juz");
		$this->HIZB = T_("Hizb");
		$this->RUB = T_("Rub");
		$this->PAGE = T_("Page");
		$this->MANZIL = T_("Manzil");
		$this->RUKU = T_("Ruku");
		$this->SAJDA = T_("Sajda");

		$this->DIR = T_("ltr");
		$this->RTL = ($this->DIR == "rtl") ? True : False;
	}
}

?>
