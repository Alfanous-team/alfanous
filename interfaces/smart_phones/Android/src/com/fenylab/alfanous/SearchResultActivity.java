package com.fenylab.alfanous;

import java.util.List;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.support.v4.view.ViewPager;
import android.view.Menu;
import android.view.MenuItem;

import com.fenylab.helpers.Helpers;
import com.fenylab.helpers.Serializer;
import com.fenylab.models.Ayah;
import com.viewpagerindicator.PageIndicator;
import com.viewpagerindicator.UnderlinePageIndicator;
public class SearchResultActivity extends FragmentActivity {
	PageViewerFragmentAdapter mAdapter;
    ViewPager mPager;
    PageIndicator mIndicator;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search_result);
        @SuppressWarnings("unchecked")
		List<Ayah> list = (List<Ayah>)Serializer.DeSerialize(getFilesDir().getPath()+"/ayahs.xml");
        mAdapter = new PageViewerFragmentAdapter(getSupportFragmentManager(),list);

        mPager = (ViewPager)findViewById(R.id.pager);
        mPager.setAdapter(mAdapter);

        mIndicator = (UnderlinePageIndicator)findViewById(R.id.indicator);
        mIndicator.setViewPager(mPager);
    }
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
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
