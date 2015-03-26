package com.fenylab.helpers;

import android.app.Dialog;
import android.view.View;
import android.view.View.OnClickListener;

public class FenyLabAboutOnClickListner implements OnClickListener
{
	private Dialog dialogWindows;
	public FenyLabAboutOnClickListner(Dialog dialog)
	{
		this.dialogWindows = dialog;
	}
	public void onClick(View v) {
		// TODO Auto-generated method stub
		dialogWindows.cancel();
	}

}
