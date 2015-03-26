package com.fenylab.helpers;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;

import com.thoughtworks.xstream.XStream;


public class Serializer 
{
	public static void Serialize(String str, Object o)
	{
		XStream xStream = new XStream();
		FileOutputStream fileOut = null;
		try 
		{
			fileOut = new FileOutputStream(str);
		} 
		catch (FileNotFoundException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		xStream.toXML(o, fileOut);
	}
	
	public static Object DeSerialize(String str)
	{
		XStream xStream = new XStream();
		Object o = null;
		try
		{
			FileInputStream fin= new FileInputStream(str);
			o  = xStream.fromXML(fin);
			fin.close();
		} 
		catch(FileNotFoundException e)
		{
			e.printStackTrace();
		}
		catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return o;
	}
}
