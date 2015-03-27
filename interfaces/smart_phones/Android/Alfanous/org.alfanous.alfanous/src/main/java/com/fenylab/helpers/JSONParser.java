package com.fenylab.helpers;
import java.util.ArrayList;
import java.util.List;
import org.json.JSONException;
import org.json.JSONObject;

import com.fenylab.alfanous.R;
import com.fenylab.alfanous.SearchResultActivity;
import com.fenylab.models.Ayah;

import android.app.Activity;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;


public class JSONParser 
{	
	Activity activity;
	public JSONParser(Activity act)
	{
		activity = act;
	}
    public void getDataFromUrl(final String url) 
    {
    	final ProgressBar prg = (ProgressBar)activity.findViewById(R.id.progressBar1);
		prg.setVisibility(View.VISIBLE);
		prg.setIndeterminate(true);
		final TextView textError = (TextView)activity.findViewById(R.id.searchError);
		textError.setVisibility(View.GONE);
		
    	Thread thread = new Thread()
    	{
			public void run() 
			{
				try 
				{
					String content = HttpPostGet.Get(url);
					if(content.contains("success"))
					{
						List<Ayah> Ayas = new ArrayList<Ayah>();
						JSONObject jo = new JSONObject(content);
						JSONObject jSonObject = jo.getJSONObject(JSonTags.SearchAction);
						JSONObject ayas = jSonObject.getJSONObject(JSonTags.Ayas);
						
						for(int i = 0; i<ayas.names().length();i++)
						{
							Ayah aya = new Ayah();
							aya.setId(""+i);
							
							JSONObject global = ayas.getJSONObject(ayas.names().get(i).toString());
							
							JSONObject theme = global.getJSONObject("theme");
							aya.setThemeChapter(theme.getString(JSonTags.TagThemeChapter));
							aya.setThemeSubtopic(theme.getString(JSonTags.TagThemeSubtopic));
							aya.setThemeTopic(theme.getString(JSonTags.TagThemeTopic));
							
							JSONObject sura = global.getJSONObject("sura");
							aya.setSuraAyas(sura.getString(JSonTags.TagSuraAyas));
							aya.setSuraName(sura.getString(JSonTags.TagSuraName));
							aya.setSuraType(sura.getString(JSonTags.TagSuraType));
							
							JSONObject sajda = global.getJSONObject("sajda");
							aya.setSajdaExiste(sajda.getBoolean(JSonTags.TagSajdaExist));
							
							JSONObject position = global.getJSONObject("position");
							aya.setPositionHizb(position.getString(JSonTags.TagPositionHizb));
							aya.setPositionManzil(position.getString(JSonTags.TagPositionManzil));
							aya.setPositionPage(position.getString(JSonTags.TagPositionPage));
							aya.setPositionPageIn(position.getString(JSonTags.TagPositionPageIn));
							
							JSONObject ayaj = global.getJSONObject("aya");
							aya.setAyaRecitation(ayaj.getString(JSonTags.TagAyaRecitation));
							aya.setAyaTextHtml(ayaj.getString(JSonTags.TagAyaTextHtml));
							aya.setAyaTextNoHtml(ayaj.getString(JSonTags.TagAyaTextNoHtml));
							aya.setTranslation(ayaj.getString(JSonTags.TagAyaTranslation));
							aya.setAyaNumber(ayaj.getInt(JSonTags.TagAyaNumber));
							
							JSONObject ayaNext = ayaj.getJSONObject(JSonTags.TagAyaNext);
							aya.setAyaNext(ayaNext.getString(JSonTags.TagAyaTextHtml));
							aya.setAyaNextName(ayaNext.getString(JSonTags.TagAyaName));
							aya.setAyaNextNumber(ayaNext.getString(JSonTags.TagAyaNumber));
							
							JSONObject ayaPrev = ayaj.getJSONObject(JSonTags.TagAyaPrev);
							aya.setAyaPrev(ayaPrev.getString(JSonTags.TagAyaTextHtml));
							aya.setAyaPrevName(ayaPrev.getString(JSonTags.TagAyaName));
							aya.setAyaPrevNumber(ayaPrev.getString(JSonTags.TagAyaNumber));
							
							Ayas.add(aya);
						}
						//TODO : serialiser
						Serializer.Serialize(activity.getFilesDir().getPath()+"/ayahs.xml", Ayas);
						Helpers.Manager.StartActivity(activity, SearchResultActivity.class);
					}
					else
					{
						DisplayError(textError);
					}
				}
				catch (JSONException e) 
				{
					e.printStackTrace();
					DisplayError(textError);
				}
				catch (Exception e)
				{
					e.printStackTrace();
					DisplayError(textError);
				}
				
				activity.runOnUiThread(new Runnable() 
				{
					@Override
					public void run() {
						prg.setVisibility(View.GONE);
						prg.setIndeterminate(false);
						
					}
				});
			}
		};
		thread.start();
    }
    
    private void DisplayError(final TextView textError)
    {
		activity.runOnUiThread(new Runnable() 
		{
			@Override
			public void run() {
				textError.setVisibility(View.VISIBLE);
				textError.setText("Error not identified, please try againe");
				
			}
		});
    }
}
