Hello, I am testing <b>alfanous</b> here 

<?php

define('FACEBOOK_APP_ID', 'de5dbf3652aa669e06dc8bd5a4331515');
define('FACEBOOK_SECRET', '');

function get_facebook_cookie($app_id, $application_secret) {
    $args = array();
    parse_str(trim($_COOKIE['fbs_' . $app_id], '\\"'), $args);
    ksort($args);
    $payload = '';
    foreach ($args as $key => $value) {
        if ($key != 'sig') {
            $payload .= $key . '=' . $value;
        }
    }
    if (md5($payload . $application_secret) != $args['sig']) {
      return null;
    }
    return $args;
}


$cookie = get_facebook_cookie(FACEBOOK_APP_ID, FACEBOOK_SECRET);

?>
<br>

<html>
  <body>
    <?php if ($cookie) { ?>
<!--      
<fb:bookmark />

<fb:serverFbml>
<script type="text/fbml">
<fb:fbml>
    <fb:request-form
        method='POST'
        type='Alfanous application'
        content='Search in Quran using alfanous with lot of features'
	    <fb:req-choice url="http://apps.facebook.com/alfanous/yes.php" 
                label="Yes" />'
            <fb:req-choice url="http://apps.facebook.com/alfanous/no.php" 
                label="No" />' 
        <fb:multi-friend-selector 
            actiontext="Invite your friends to join Alfanous group.">
    </fb:request-form>
</fb:fbml>
</script>
</fb:serverFbml>

-->

	



    <?php } else { ?>
      <fb:login-button>Join Alfanous Application</fb:login-button>


    <?php } ?>
    <script src="http://connect.facebook.net/en_US/all.js"></script>
    <script>
      FB.init({appId: 'de5dbf3652aa669e06dc8bd5a4331515', xfbml: true, cookie: true});
      FB.Event.subscribe('auth.login', function(response) {
        // Reload the application in the logged-in state
        //window.top.location = 'http://apps.facebook.com/alfanous/';
      });
    </script>

<!--
<script>
  FB.ui(
   {
     method: 'stream.publish',
     message: 'Check out this great app! http://apps.facebook.com/alfanous'
   }
  );
</script>
-->


  </body>
</html>



