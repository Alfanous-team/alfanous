

<div dir="rtl" align="right"> 



<?php

  ##to do
  #encoding queries before sending-recieving
  #suggestionq : هل تقصد؟ كلمة
  # costumiser pour chaque messenger
  # write documentation on the wiki
  # hide/show optional information 
  
    
$message="";
if ( isset($_REQUEST['msg'])) $message=$_REQUEST['msg'];

$user="أخي";
if ( isset($_REQUEST['user'])) $user=$_REQUEST['user'];


if ($_REQUEST['step']==1)
{

#echo "سلاما يا ".$user."";
#mail( "assem.ch@gmail.com", "Subject:Chatty",$message, "From: ".$user."@chatty.alfanous.org" );
}

if (isset($_REQUEST['msg']))
{


$json=file_get_contents("http://www.alfanous.org/json?search=".$message."&highlight=bold");

$results=json_decode($json);
# Formatting the results to show
echo "الكلمات(".$results->{'words'}->{'global'}->{'nb_words'}." كلمة وردت ".$results->{'words'}->{'global'}->{'nb_matches'}." مرة )";
echo "<br/>";
$cpt = 1;
while ($cpt <= $results->{'words'}->{'global'}->{'nb_words'})
{
    echo $cpt.".".$results->{'words'}->{$cpt}->{'word'}." وردت ".$results->{'words'}->{$cpt}->{'nb_matches'}." مرة في  ".$results->{'words'}->{$cpt}->{'nb_ayas'}." آية "."<br/>";
    $cpt++;
}
echo "<br/> <br/>";
echo "النتائج(:".$results->{'interval'}->{'start'}." إلى ".$results->{'interval'}->{'end'}." من أصل ".$results->{'interval'}->{'total'}.")"; 

echo "<br>";
echo"<br/>"; 
$cpt = 1;
$limit = $results->{'interval'}->{'total'};
if ($results->{'interval'}->{'total'} > 10 ) $limit=10;
while ($cpt <= $limit)
    {
       echo "$cpt -> (".$results->{'ayas'}->{$cpt}->{'sura'}->{'name'}.$results->{'ayas'}->{$cpt}->{'aya'}->{'id'}.")"."<br/>";
       echo "{ ".$results->{'ayas'}->{$cpt}->{'aya'}->{'text'} .  "}"."<br/>";
       echo " الكلمات ".$results->{'ayas'}->{$cpt}->{'stat'}->{'words'}."\\".$results->{'ayas'}->{$cpt}->{'sura'}->{'stat'}->{'words'}." - ";
       echo " اﻷحرف ".$results->{'ayas'}->{$cpt}->{'stat'}->{'letters'}."\\".$results->{'ayas'}->{$cpt}->{'sura'}->{'stat'}->{'letters'}." - ";
       echo " ألفاظ الجلالة ".$results->{'ayas'}->{$cpt}->{'stat'}->{'godnames'}."\\".$results->{'ayas'}->{$cpt}->{'sura'}->{'stat'}->{'godnames'}."
       <br/> ";
       echo " الحزب ".$results->{'ayas'}->{$cpt}->{'position'}->{'hizb'}."-";
       echo " الصفحة ".$results->{'ayas'}->{$cpt}->{'position'}->{'page'}."<br/>";
       $cpt++ ;
     echo"<br/>";
    }



}
?>

<br/>
<b> لمزيد من التفاصيل</b>
<b><a href="http://alfanous.org/?search=<?=$message ?>"> اضغط هنا </a></b>

</div> 
