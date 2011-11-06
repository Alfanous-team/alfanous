


<?php

  ##to do
  #encoding queries before sending-recieving
  #suggestionq : هل تقصد؟ كلمة
  # costumiser pour chaque messenger
  # write documentation on the wiki
  # hide/show optional information 
  
    
$message="";
if ( isset($_REQUEST['msg'])) $message=rawurlencode($_REQUEST['msg']);

$user="أخي";
if ( isset($_REQUEST['user'])) $user=$_REQUEST['user'];


if ($_REQUEST['step']==1)
{

echo "Salam ".$user."!";
#mail( "assem.ch@gmail.com", "Subject:Chatty",$message, "From: ".$user."@chatty.alfanous.org" );
}

if (isset($_REQUEST['msg']))
{


echo $message;


$json=file_get_contents("http://www.alfanous.org/json?search=".$message."&highlight=bold");

$results=json_decode($json);
# Formatting the results to show
echo "words (".$results->{'words'}->{'global'}->{'nb_words'}."words in ".$results->{'words'}->{'global'}->{'nb_matches'}."times )";
echo "<br/>";
$cpt = 1;
while ($cpt <= $results->{'words'}->{'global'}->{'nb_words'})
{
    echo $cpt.".".$results->{'words'}->{$cpt}->{'word'}.":".$results->{'words'}->{$cpt}->{'nb_matches'}." times ".$results->{'words'}->{$cpt}->{'nb_ayas'}." verses "."<br/>";
    $cpt++;
}
echo "<br/> <br/>";
echo "Results (:".$results->{'interval'}->{'start'}." to ".$results->{'interval'}->{'end'}." of ".$results->{'interval'}->{'total'}.")"; 

echo "<br>";
echo"<br/>"; 
$cpt = 1;
$limit = $results->{'interval'}->{'total'};
if ($results->{'interval'}->{'total'} > 10 ) $limit=10;
while ($cpt <= $limit)
    {
       echo "$cpt -> (".$results->{'ayas'}->{$cpt}->{'sura'}->{'name'}.$results->{'ayas'}->{$cpt}->{'aya'}->{'id'}.")"."<br/>";
       echo "{ ".$results->{'ayas'}->{$cpt}->{'aya'}->{'text'} .  "}"."<br/>";
       echo " words ".$results->{'ayas'}->{$cpt}->{'stat'}->{'words'}."\\".$results->{'ayas'}->{$cpt}->{'sura'}->{'stat'}->{'words'}." - ";
       echo " letters ".$results->{'ayas'}->{$cpt}->{'stat'}->{'letters'}."\\".$results->{'ayas'}->{$cpt}->{'sura'}->{'stat'}->{'letters'}." - ";
       echo " Godnames ".$results->{'ayas'}->{$cpt}->{'stat'}->{'godnames'}."\\".$results->{'ayas'}->{$cpt}->{'sura'}->{'stat'}->{'godnames'}."
       <br/> ";
       echo " Hizb ".$results->{'ayas'}->{$cpt}->{'position'}->{'hizb'}."-";
       echo " Page ".$results->{'ayas'}->{$cpt}->{'position'}->{'page'}."<br/>";
       $cpt++ ;
     echo"<br/>";
    }



}
?>

<br/>
<b> for more results/details follow</b>
<b><a href="http://alfanous.org/?search=<?=$message ?>">  the link </a></b>

</div> 
