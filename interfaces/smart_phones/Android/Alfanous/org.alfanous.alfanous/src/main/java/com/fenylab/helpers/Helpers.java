package com.fenylab.helpers;

import com.fenylab.alfanous.R;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.ConnectivityManager;

import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.Toast;


public class Helpers
{
	public enum KindMessageBox{OK,YesNo,Exit};
	public static Helpers Manager = new Helpers();
	private static AlertDialog.Builder messageBox;
	private static Context context ;
	
	private Helpers(){};
			
	public void Init(Context context)
	{
		Helpers.context = context;
	}
	
	public void MessageBox(String title,String text,KindMessageBox kind)
	{
		messageBox = new AlertDialog.Builder(context);
		messageBox.setMessage(text);
		messageBox.setIcon(R.drawable.ic_launcher);
		messageBox.setTitle(title);
		switch(kind)
		{
			case OK : 
				messageBox.setPositiveButton("OK", null);
				break;
			case YesNo : 
				messageBox.setNegativeButton("Oui", new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int which) {
						Toast toast = Toast.makeText(context.getApplicationContext(),"Oui",Toast.LENGTH_SHORT);
						toast.show();
					}
				});
				messageBox.setPositiveButton("Non", new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int which) {
						Toast toast = Toast.makeText(context.getApplicationContext(),"Non",Toast.LENGTH_LONG);
						toast.show();
					}
				});
				break;
			case Exit : 
				messageBox.setPositiveButton("موا�?ق", new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int which) 
					{
						((Activity)context).onBackPressed();
					}
				});
		}

		
		messageBox.setOnCancelListener(new DialogInterface.OnCancelListener() {
			public void onCancel(DialogInterface dialog) {	
			}
		});
		messageBox.create().show();
	}
	
	public void MessageBox(String title,String text)
	{
		messageBox = new AlertDialog.Builder(context);
		messageBox.setMessage(text);
		messageBox.setIcon(R.drawable.ic_launcher);
		messageBox.setTitle(title);
		messageBox.setPositiveButton("OK", null);		
		messageBox.setOnCancelListener(new DialogInterface.OnCancelListener() {
			public void onCancel(DialogInterface dialog) {
			}
		});
		messageBox.create().show();
	}
	
	public void MessageFlotant(String text)
	{
		Toast toast = Toast.makeText(context, text, Toast.LENGTH_LONG);
		toast.setGravity(Gravity.CENTER, 0, 0);
		toast.show();
	}
	
	public boolean IsOnline() 
	{
		@SuppressWarnings("unused")
		String str = "";
		try {
			ConnectivityManager cm =
			        (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);

			    return cm.getActiveNetworkInfo() != null && 
			       cm.getActiveNetworkInfo().isConnectedOrConnecting();
		} catch (Exception e) {
			return false;
		}
	    
	}
	
	public void StartActivity(Activity context, Class<?> type,String ...strings)
	{
    	Intent intent = new Intent();
        intent.setClass(context,type);
		if(strings.length==1)
		{
			String str = strings[0];
			intent.putExtra("nameCateg", str);
		}
		if(strings.length>1)
		{
			intent.putExtra("url", strings[0]);
			intent.putExtra("date", strings[1]);
			intent.putExtra("title", strings[2]);
			intent.putExtra("desc", strings[3]);
			intent.putExtra("html", strings[4]);
		}
        context.startActivity(intent);
	}
	
	
	public String removeHTML(String htmlString)
    {
          // Remove HTML tag from java String    
        String noHTMLString = htmlString.replaceAll("\\<.*?\\>", "");

        // Remove Carriage return from java String
        noHTMLString = noHTMLString.replaceAll( "<br/>","\r");

        // Remove New line from java string and replace html break
        noHTMLString = noHTMLString.replaceAll("&#39;", "\'");
        noHTMLString = noHTMLString.replaceAll("&#192;" , "À'");
        noHTMLString = noHTMLString.replaceAll( "&#224;","à");
        noHTMLString = noHTMLString.replaceAll("&#193;","�?");
        noHTMLString = noHTMLString.replaceAll( "&#225;" , "á");
        noHTMLString = noHTMLString.replaceAll("&#200;","È");
        noHTMLString = noHTMLString.replaceAll("&#232;","è");
        noHTMLString = noHTMLString.replaceAll("&#201;","É");
        noHTMLString = noHTMLString.replaceAll("&#233;","é");
        noHTMLString = noHTMLString.replaceAll("&#202;","Ê");
        noHTMLString = noHTMLString.replaceAll( "&#212;","Ô");
        noHTMLString = noHTMLString.replaceAll(  "&#8211;" , "–");
        noHTMLString = noHTMLString.replaceAll( "&#8217;","’");
        noHTMLString = noHTMLString.replaceAll( "&#8221;","\"");
        noHTMLString = noHTMLString.replaceAll( "&#8220;","\"");
        return noHTMLString;
    }
	
	 public void setListViewHeightBasedOnChildren(ListView listView) {
        ListAdapter listAdapter = listView.getAdapter(); 
        if (listAdapter == null) {
            // pre-condition
            return;
        }

        int totalHeight = 0;
        for (int i = 0; i < listAdapter.getCount(); i++) {
            View listItem = listAdapter.getView(i, null, listView);
            listItem.measure(0, 0);
            totalHeight += listItem.getMeasuredHeight();
        }

        ViewGroup.LayoutParams params = listView.getLayoutParams();
        params.height = totalHeight + (listView.getDividerHeight() * (listAdapter.getCount() - 1));
        listView.setLayoutParams(params);
        listView.requestLayout();
    }
	 
	public void AboutFenyLab()
	{
		final Dialog dialogWin = new Dialog(context);
		dialogWin.setContentView(R.layout.about);
		dialogWin.setTitle("About :");
		dialogWin.setCancelable(true);
        Button btn = (Button) dialogWin.findViewById(R.id.btn1); 
        btn.setOnClickListener(new FenyLabAboutOnClickListner(dialogWin));
        dialogWin.show();
	}
}
