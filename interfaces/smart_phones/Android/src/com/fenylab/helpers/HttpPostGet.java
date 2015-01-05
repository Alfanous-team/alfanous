package com.fenylab.helpers;

import java.io.IOException;

import org.apache.http.HttpResponse;
import org.apache.http.ParseException;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;

public class HttpPostGet 
{
	public static String Get(String url)
	{
        String content ="";
		DefaultHttpClient mHttpClient =  new DefaultHttpClient();			
		HttpGet mHttpGet = new HttpGet(url);		
		mHttpGet.setHeader("Cache-Control", "no-cache"); 
        HttpResponse mHttpResponse;
		try 
		{
			mHttpResponse = mHttpClient.execute(mHttpGet);
			content = EntityUtils.toString(mHttpResponse.getEntity());
		}
		catch (ClientProtocolException e) 
		{
			// TODO Auto-generated catch block
			e.getMessage();
		} 
		catch (ParseException e) 
		{
			// TODO Auto-generated catch block
			e.getMessage();
		}
		catch (IOException e) 
		{
			// TODO Auto-generated catch block
			e.getMessage();
		}	
		catch(Exception e)
		{
			e.getMessage();
		}
		return content;
	}
}
