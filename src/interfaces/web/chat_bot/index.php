
<div dir="rtl" align="right">

<?php

if ($_REQUEST['step']==1)
{

echo " <br/>  السلام عليكم ".$_REQUEST['user']."<br/><br/>";
?>
<br/>
الفانوس هو مشروع محرّك بحث قرآني يوفر للمستخدمين خدمات البحث البسيط و المتقدم في المعلومات المتنوّعة التي يزخر بها القرآن الكريم
 <br/>
هذا الروبوت هو واجهة لابراز مزايا البحث في القرآن الموجودة في  الفانوس و لم يتسنى التدقيق لجميع البيانات كالمعلومات الاحصائية...في حالة اكتشفت أخطاءا اتصل بنا 
<br/><br/>
اكتب "مساعدة" لمشاهدة نص المساعدة
<br/>
اكتب "فريق"  لمشاهدة فريق تطوير الروبوت


<br/>

<br>



<?php

$message="no msg";
if ($_REQUEST['msg']) $message=$_REQUEST['msg'];

$user="anonymos";
if ($_REQUEST['user']) $user=$_REQUEST['user'];

mail( "assem.ch@gmail.com", "Subject:alfanous",$message, "From: ".$user );
}




if ($_REQUEST['msg'])
{

if ($_REQUEST['msg']=="مساعدة")
{
?>
<b>مساعدة</b><br/>
<table>
<th colspan="2">أمثلة عن البحث المتقدم:</th>
<tr>
<th>البحث بالجملة </th><td>" رب العالمين"</td>
</tr>

<tr>
<th> العبارات المنطقية</th><td>الصلاة وليس الزكاة</td>
</tr>
<tr>
<th> المترادفات</th><td>~السعير</td>
</tr>
<tr>
<th> العبارات النمطية</th><td>*نبي*</td>
</tr>
<tr>
<th>الحقول </th><td>سورة:يس</td>
</tr>
<tr>
<th>  المجالات و الحقول </th><td>رقم_السورة:[1 الى 5] و الله</td>
</tr>
 <tr>
<th>ثنائية جذر،نوع</th><td>{قول,اسم}</td>
</tr>
<tr>
<th>البحث بالاشتقاق</th><td> >>ملك </td>
</tr>
</table>

<?php
}

elseif ($_REQUEST['msg']=="فريق")
{
?>
<b>فريق تطوير الروبوت</b><br/>
عاصم شلي (Assem Chelli)
																     <br/> Assem.ch@gmail.com
<br/>

<?php
}
else 
{

echo "<b>"."عبارة البحث: "."</b>".urldecode($_REQUEST['msg'])." ـ ";

echo "<br>";
virtual("/cgi-bin/alfanous-web.py?search_bot=".$_REQUEST['msg']);
echo "<br/>";
}
}
?>
<br/>
<br/>
الفانوس - محرك بحث قرآني (alfanous.sf.net)
<br/>
نسخة تجريبية (قيد التطوير)
<br/>

</div>

