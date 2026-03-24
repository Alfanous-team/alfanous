const COOKIE_SKIN_NAME = 'skin';
const SKIN_CSS_ID = 'skin_css';

function change_skin(skin_id,skin_type) {
  var $newCSS = $('<link>', {
    rel: 'stylesheet',
    type: 'text/css',
    href: '/static/ltr/css/bootstrap_' + skin_id + '.min.css'
  }).on('load', function() {
    $('#' + SKIN_CSS_ID).remove();
    $(this).attr('id', SKIN_CSS_ID);
  });
  $('head').prepend($newCSS);

   /*
   logo_type ="dark"; // dark is the default logo type
   if (skin_type == "dark" && bidi=="ltr") { logo_type="light"; }  // RTL is not ready for skins

   $('img[alt="logo"]').attr("src", "/static/"+bidi+"/img/alfanous_"+logo_type+".png" );
	*/
   setSkinCookie(skin_id+"_"+skin_type)
}

function setSkinCookie(skin_id)
{

	var exdays = 300; // expiration time
	var exdate=new Date();
	exdate.setDate(exdate.getDate() + exdays);
  var c_value=escape(skin_id) + ((exdays==null) ? "" : ";path=/; expires="+exdate.toUTCString());
  document.cookie=COOKIE_SKIN_NAME + "=" + c_value;
}

function GetSkinCookieAndApply() {
  var cookies = document.cookie;
  var cookie_value;

  var index = cookies.indexOf(" " + COOKIE_SKIN_NAME + "=");
  if (index == -1) {
    index = cookies.indexOf(COOKIE_SKIN_NAME + "=");
  }
  if (index == -1) {
    // we don't have the cookie for skin => don't apply any skin
    return;
  }

  var start = cookies.indexOf("=", index) + 1;
  var end = cookies.indexOf(";", start);
  if (end == -1) {
    end = cookies.length;
  }
  cookie_value = unescape(cookies.substring(start, end));

  //var skin_id = cookie_value;
  var st = cookie_value.split("_");
  var skin_id = st[0];
  var type = st[1];

  if (skin_id != null && skin_id != "null" && skin_id != "default") {
    change_skin(skin_id,type);
  }
}
