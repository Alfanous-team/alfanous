

    $('.shareme').sharrre({
    share: {
    googlePlus: true,
    facebook: true,
    twitter: true
    },
    buttons: {
    googlePlus: {size: 'tall', annotation:'bubble'},
    facebook: {layout: 'box_count'},
    twitter: {count: 'vertical', via: 'alfanous'}
    },
    hover: function(api, options){
    $(api.element).find('.buttons').show();
    },
    hide: function(api, options){
    $(api.element).find('.buttons').hide();
    },
    enableTracking: false
    });


    $('#shareme_root').sharrre({
    	share: {
    	googlePlus: true,
    	facebook: true,
    	twitter: true,
    	digg: true,
    	delicious: true
    	},
    	enableTracking: true,
    	buttons: {
    	googlePlus: {size: 'tall', annotation:'bubble'},
    	facebook: {layout: 'box_count'},
    	twitter: {count: 'vertical'},
    	digg: {type: 'DiggMedium'},
    	delicious: {size: 'tall'}
    	},
    	hover: function(api, options){
    	$(api.element).find('.buttons').show();
    	},
    	hide: function(api, options){
    	$(api.element).find('.buttons').hide();
    	}
    	});