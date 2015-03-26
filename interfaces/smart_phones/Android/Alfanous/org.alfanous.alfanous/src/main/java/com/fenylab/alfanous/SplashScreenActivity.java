package com.fenylab.alfanous;

import com.fenylab.helpers.Helpers;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;

public class SplashScreenActivity extends Activity {
	// Splash screen timer
	private static int SPLASH_TIME_OUT = 1500;

	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_splashscreen);
		Helpers.Manager.Init(this);
		new Handler().postDelayed(new Runnable() {
			@Override
			public void run() {
				Helpers.Manager.StartActivity(SplashScreenActivity.this, SearchActivity.class);
				finish();
			}
		}, SPLASH_TIME_OUT);
	}
}
