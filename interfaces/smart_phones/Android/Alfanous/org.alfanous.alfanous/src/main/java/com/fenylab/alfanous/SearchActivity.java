package com.fenylab.alfanous;


import java.io.File;

import com.fenylab.helpers.Helpers;
import com.fenylab.helpers.JSONParser;
import com.fenylab.models.AlfanousApi;

import android.net.Uri;
import android.os.Bundle;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;

public class SearchActivity extends Activity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_search);
		Helpers.Manager.Init(this);

		Button quickSearchBtn = (Button)findViewById(R.id.quickSearchBtn);
		quickSearchBtn.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) 
			{
				EditText edit = (EditText)findViewById(R.id.editText);
				InputMethodManager imm = (InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
	            imm.hideSoftInputFromWindow(edit.getWindowToken(), 
	                                      InputMethodManager.RESULT_UNCHANGED_SHOWN);
				if(Helpers.Manager.IsOnline())
				{
					String wordsTr = edit.getText().toString();
					final String words = wordsTr.replace(" ", "+");
					if(words.equals(""))
					{
						Helpers.Manager.MessageBox("EditBox Error", "The EditBox is empty, please fill it");
					}
					else
					{
						JSONParser jsonParser = new JSONParser(SearchActivity.this);
						jsonParser.getDataFromUrl(AlfanousApi.getLinkApiAyats(words));
					}		
				}
				else
				{
					Helpers.Manager.MessageBox("No Internet", 
							"Your are not connected to the internet, please connect and try againe");
				}
						
			}
		});
		
		Button searchAdvBtn = (Button)findViewById(R.id.searchAdvBtn);
		searchAdvBtn.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				// TODO Auto-generated method stub
				Helpers.Manager.MessageBox("Features", 
						"this feature will be available in the next version");
			}
		});
		
		Button historyBtn = (Button)findViewById(R.id.historyBtn);
		historyBtn.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				File file = new File(getFilesDir().getPath()+"/ayahs.xml");
				if(file.isFile())
					Helpers.Manager.StartActivity(SearchActivity.this, SearchResultActivity.class);
				else
					Helpers.Manager.MessageBox("History", 
							"You have no history yet");
			}
		});
	}
	
	@Override
	protected void onResume() {
		// TODO Auto-generated method stub
		super.onResume();
		Helpers.Manager.Init(this);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.menu, menu);
		return true;
	}
	
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.aboutFenous:
            	Intent browserIntent = new Intent(
            			Intent.ACTION_VIEW, Uri.parse("http://www.alfanous.org/"));
            	startActivity(browserIntent);
                return true;

            case R.id.aboutFeny:
                Helpers.Manager.AboutFenyLab();
                return true;
        }
        return super.onOptionsItemSelected(item);
    }

}
