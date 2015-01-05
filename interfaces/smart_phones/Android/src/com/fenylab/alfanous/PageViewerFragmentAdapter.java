package com.fenylab.alfanous;

import java.util.List;

import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;

import com.fenylab.models.Ayah;

class PageViewerFragmentAdapter extends FragmentPagerAdapter {
    
    private List<Ayah> ayas;
    
    
    public PageViewerFragmentAdapter(FragmentManager fm,List<Ayah> ayas) {
        super(fm);
        this.ayas = ayas;
    }

    @Override
    public Fragment getItem(int position) {
    	Ayah aya= ayas.get(position);
        return PageViewerFragment.newInstance(aya);
    }

    @Override
    public int getCount() {
        return ayas.size();
    }
}