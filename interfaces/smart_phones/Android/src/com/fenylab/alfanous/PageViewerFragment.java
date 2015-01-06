package com.fenylab.alfanous;

import com.fenylab.helpers.Helpers;
import com.fenylab.models.Ayah;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.text.Html;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;

public final class PageViewerFragment extends Fragment 
{
    private Ayah aya ;
    public static PageViewerFragment newInstance(Ayah aya) 
    {
        PageViewerFragment fragment = new PageViewerFragment();
        fragment.aya = aya;
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) 
    {
        View view = inflater.inflate(R.layout.item_viewpager, null);
        
        TextView resultN= (TextView)view.findViewById(R.id.resultN);
        String str = resultN.getText().toString().replace("%s", aya.getId());
        resultN.setText(str);
        
        ImageButton btnShare = (ImageButton)view.findViewById(R.id.btnShare);
        Helpers.Manager.Init(getActivity());
        btnShare.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				if(Helpers.Manager.IsOnline())
					startActivity(Intent.createChooser(createShareIntent("Share Aya",aya.getAyaTextNoHtml())
						, "Share Aya"));
				else
					Helpers.Manager.MessageBox("No Internet", 
							"Your are not connected to the internet, please connect and try againe");
			}
		});
        
        ImageButton btnPlay = (ImageButton)view.findViewById(R.id.btnPlay);
        btnPlay.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				if(Helpers.Manager.IsOnline())
					startActivity(Intent.createChooser(createPlayIntent(aya.getAyaRecitation()),
						"Play Quran)"));
				else
					Helpers.Manager.MessageBox("No Internet", 
							"Your are not connected to the internet, please connect and try againe");
			}
		});
        
        Button more = (Button)view.findViewById(R.id.more);
        final LinearLayout moreView = (LinearLayout)view.findViewById(R.id.moreView);
        more.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) {
				if(moreView.getVisibility()==View.VISIBLE)
					moreView.setVisibility(View.GONE);
				else moreView.setVisibility(View.VISIBLE);
			}
		});
        
        TextView prevAya= (TextView)view.findViewById(R.id.prevAya);
        str = prevAya.getText().toString().replace("%h", aya.getAyaPrevName()+" "+aya.getAyaPrevNumber());
        str = str.replace("%s", aya.getAyaPrev());
        prevAya.setText(str);
        
        TextView targetAya= (TextView)view.findViewById(R.id.targetAya);
        str = targetAya.getText().toString().replace("%h", aya.getSuraName()+" "+aya.getAyaNumber());
        str = str.replace("%s", aya.getAyaTextHtml());
        targetAya.setText(Html.fromHtml(str));
        
        TextView nextAya= (TextView)view.findViewById(R.id.nextAya);
        str = nextAya.getText().toString().replace("%h", aya.getAyaNextName()+" "+aya.getAyaNextNumber());
        str = str.replace("%s", aya.getAyaNext());
        nextAya.setText(str);
        
        TextView engAya= (TextView)view.findViewById(R.id.engAya);
        engAya.setText(Html.fromHtml(aya.getTranslation()));
        
        TextView chapter= (TextView)view.findViewById(R.id.chapter);
        str = chapter.getText().toString().replace("%s", aya.getThemeChapter());
        chapter.setText(str);
        
        TextView topic= (TextView)view.findViewById(R.id.topic);
        str = topic.getText().toString().replace("%s", aya.getThemeTopic());
        topic.setText(str);
        
        TextView manzil= (TextView)view.findViewById(R.id.manzil);
        str = manzil.getText().toString().replace("%s", aya.getPositionManzil());
        manzil.setText(str);
        
        TextView hizb= (TextView)view.findViewById(R.id.hizb);
        str = hizb.getText().toString().replace("%s", aya.getPositionHizb());
        hizb.setText(str);
        
        TextView page= (TextView)view.findViewById(R.id.page);
        str = page.getText().toString().replace("%s", aya.getPositionPage());
        page.setText(str);
        
        TextView sajda= (TextView)view.findViewById(R.id.sajda);
        str = sajda.getText().toString().replace("%s", ""+aya.isSajdaExiste());
        sajda.setText(str);
        
        TextView sura= (TextView)view.findViewById(R.id.sura);
        str = sura.getText().toString().replace("%s", ""+aya.getSuraName());
        sura.setText(str);
        
        TextView suraType= (TextView)view.findViewById(R.id.suraType);
        str = suraType.getText().toString().replace("%s", ""+aya.getSuraType());
        suraType.setText(str);
        
        return view;
    }
    
    private Intent createShareIntent(String desc, String url) 
    {
    	Intent shareIntent = new Intent(Intent.ACTION_SEND);
        shareIntent.setType("text/plain");
        shareIntent.putExtra(Intent.EXTRA_SUBJECT, desc);
        shareIntent.putExtra(Intent.EXTRA_TEXT, url);
        return shareIntent;
    }
    
    private Intent createPlayIntent(String url) 
    {
    	Uri mp3Uri = Uri.parse(url);
    	Intent playIntent = new Intent(Intent.ACTION_VIEW);
    	playIntent.setDataAndType(mp3Uri, "audio/*");
        return playIntent;
    }
    
    @Override
    public void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
    }
}
