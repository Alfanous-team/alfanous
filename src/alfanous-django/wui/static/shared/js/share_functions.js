

    $('.shareme').sharrre({
    share: {
    googlePlus: true,
    facebook: true,
    twitter: true
    },
    buttons: {
    googlePlus: {size: 'tall', annotation:'bubble'},
    facebook: {layout: 'box_count'},
    twitter: {count: 'vertical', via: '_JulienH'}
    },
    hover: function(api, options){
    $(api.element).find('.buttons').show();
    },
    hide: function(api, options){
    $(api.element).find('.buttons').hide();
    },
    enableTracking: false
    });

