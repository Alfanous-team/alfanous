package com.fenylab.models;

public class Ayah
{
	private String ThemeTopic;
	private String ThemeSubtopic;
	private String ThemeChapter;
	
	private String SuraName;
	private String SuraAyas;
	private String SuraType;
	
	private boolean SajdaExiste;
	
	private String PositionManzil;
	private String PositionPage;
	private String PositionPageIn;
	private String PositionHizb;
	
	private String AyaTextHtml ;
	private int AyaNumber ;
	private String AyaNext ;
	private String AyaNextName ;
	private String AyaNextNumber ;
	private String AyaPrev ;
	private String AyaPrevName ;
	private String AyaPrevNumber ;
	
	
	public String getAyaNextName() {
		return AyaNextName;
	}
	public void setAyaNextName(String ayaNextName) {
		AyaNextName = ayaNextName;
	}
	public String getAyaNextNumber() {
		return AyaNextNumber;
	}
	public void setAyaNextNumber(String ayaNextNumber) {
		AyaNextNumber = ayaNextNumber;
	}
	public String getAyaPrevName() {
		return AyaPrevName;
	}
	public void setAyaPrevName(String ayaPrevName) {
		AyaPrevName = ayaPrevName;
	}
	public String getAyaPrevNumber() {
		return AyaPrevNumber;
	}
	public void setAyaPrevNumber(String ayaPrevNumber) {
		AyaPrevNumber = ayaPrevNumber;
	}
	private String AyaRecitation ;
	private String AyaTextNoHtml ;
	private String translation;
	
	private String id;
	public String getThemeChapter() {
		return ThemeChapter;
	}
	public void setThemeChapter(String themeChapter) {
		ThemeChapter = themeChapter;
	}
	public String getThemeTopic() {
		return ThemeTopic;
	}
	public void setThemeTopic(String themeTopic) {
		ThemeTopic = themeTopic;
	}
	public String getThemeSubtopic() {
		return ThemeSubtopic;
	}
	public void setThemeSubtopic(String themeSubtopic) {
		ThemeSubtopic = themeSubtopic;
	}
	public String getSuraName() {
		return SuraName;
	}
	public void setSuraName(String suraName) {
		SuraName = suraName;
	}
	public String getSuraAyas() {
		return SuraAyas;
	}
	public void setSuraAyas(String suraAyas) {
		SuraAyas = suraAyas;
	}
	public String getSuraType() {
		return SuraType;
	}
	public void setSuraType(String suraType) {
		SuraType = suraType;
	}
	public boolean isSajdaExiste() {
		return SajdaExiste;
	}
	public void setSajdaExiste(boolean sajdaExiste) {
		SajdaExiste = sajdaExiste;
	}
	public String getPositionManzil() {
		return PositionManzil;
	}
	public void setPositionManzil(String positionManzil) {
		PositionManzil = positionManzil;
	}
	public String getPositionPage() {
		return PositionPage;
	}
	public void setPositionPage(String positionPage) {
		PositionPage = positionPage;
	}
	public String getPositionPageIn() {
		return PositionPageIn;
	}
	public void setPositionPageIn(String positionPageIn) {
		PositionPageIn = positionPageIn;
	}
	public String getPositionHizb() {
		return PositionHizb;
	}
	public void setPositionHizb(String positionHizb) {
		PositionHizb = positionHizb;
	}
	public String getAyaTextHtml() 
	{
		return AyaTextHtml;
	}
	public void setAyaTextHtml(String ayaTextHtml) {
		int i=0;
		while(ayaTextHtml.contains("<span class=\"match "))
		{
			ayaTextHtml = ayaTextHtml.replace("<span class=\"match term"+i+"\">","<font color=\"#FF0000\">");
			ayaTextHtml = ayaTextHtml.replace("</span>", "</font>");
			i++;
		}
		
		AyaTextHtml = ayaTextHtml;
	}
	public String getAyaNext() {
		return AyaNext;
	}
	public void setAyaNext(String ayaNext) {
		AyaNext = ayaNext;
	}
	public String getAyaPrev() {
		return AyaPrev;
	}
	public void setAyaPrev(String ayaPrev) {
		AyaPrev = ayaPrev;
	}
	public String getAyaRecitation() {
		return AyaRecitation;
	}
	public void setAyaRecitation(String ayaRecitation) {
		AyaRecitation = ayaRecitation;
	}
	public String getAyaTextNoHtml() {
		return AyaTextNoHtml;
	}
	public void setAyaTextNoHtml(String ayaTextNoHtml) {
		AyaTextNoHtml = ayaTextNoHtml;
	}
	public String getTranslation() {
		return translation;
	}
	public void setTranslation(String translation) {
		this.translation = translation;
	}
	public int getAyaNumber() {
		return AyaNumber;
	}
	public void setAyaNumber(int ayaNumber) {
		AyaNumber = ayaNumber;
	}
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
}
