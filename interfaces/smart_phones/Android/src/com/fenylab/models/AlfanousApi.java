package com.fenylab.models;

public class AlfanousApi 
{
	private static String baseLink = "http://www.alfanous.org/jos2?";
	
	public static String Sugestion = baseLink+"action=suggest&query=%s";
	
	private static String Ayats = baseLink+"query=%s&&view=default&&sortedby=score&&translation=en.transliteration&&recitation=14";
	
	public static String getLinkApiAyats(String word)
	{
		return String.format(Ayats, word);
	}
	
	public static String getLinkApiAyatsSugest(String word)
	{
		return String.format(Sugestion, word);
	}
}
