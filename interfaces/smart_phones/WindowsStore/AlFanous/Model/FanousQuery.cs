using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using AlFanous.ViewModel;
using Newtonsoft.Json;

namespace AlFanous.Model
{
    public class FanousQueryResponse
    {
        public SearchQuery search;
        public Error error;
    }
    public class SearchQuery
    {
        public double runtime;
        public Words words;
        public Interval interval;

        [JsonConverter(typeof(SingleValueArrayConverter<AyaElement>))]
        public List<AyaElement> ayas;
        public Translation_Info translation_Info;
    }


    public class AyaElement
    { 
        public Theme theme { get; set; }
        public Sura sura { get; set; }
        public Sajda sajda { get; set; }
        public Position position { get; set; }
        public Identifier identifier { get; set; }
        public Aya aya { get; set; }
        public Stat stat { get; set; }
        public Annotations annotations { get; set; }
    }


    public class Theme
    {
        public string chapter { get; set; }
        public string topic { get; set; }
        public object subtopic { get; set; }
    }

    public class Sura
    {
        public Stat stat { get; set; }
        public string name { get; set; }
        public string english_name { get; set; }
        public string arabic_type { get; set; }
        public int ayas { get; set; }
        public int order { get; set; }
        public string type { get; set; }
        public int id { get; set; }
        public string arabic_name { get; set; }
    }

    public class Sajda
    {
        public object type { get; set; }
        public bool exist { get; set; }
        public object id { get; set; }
    }

    public class Position
    {
        public int manzil { get; set; }
        public int rub { get; set; }
        public int page { get; set; }
        public int page_IN { get; set; }
        public int ruku { get; set; }
        public int juz { get; set; }
        public int hizb { get; set; }
    }

    public class Identifier
    {
        public int sura_id { get; set; }
        public int gid { get; set; }
        public string sura_arabic_name { get; set; }
        public string sura_name { get; set; }
        public int aya_id { get; set; }
    }

    public class Aya
    {
        [JsonIgnore]
        public string keyword { get; set; }
        public string text { get; set; }
        public Prev_Aya prev_aya { get; set; }
        public Next_Aya next_aya { get; set; }
        public string recitation { get; set; }
        public string text_no_highlight { get; set; }
        public object translation { get; set; }
        public int id { get; set; }
    }

    public class Prev_Aya
    {
        public string text { get; set; }
        public int id { get; set; }
        public string sura_arabic { get; set; }
        public string sura { get; set; }
    }

    public class Next_Aya
    {
        public string text { get; set; }
        public int id { get; set; }
        public string sura_arabic { get; set; }
        public string sura { get; set; }
    }

    public class Stat
    {
        public int letters { get; set; }
        public int godnames { get; set; }
        public int words { get; set; }
    }

    public class Annotations
    {
    }

    public class Translation_Info
    {
    }

    public class Words
    {
        public Global global;
        [JsonConverter(typeof(SingleValueArrayConverter<IndividualWordElement>))]
        public List<IndividualWordElement> individual;

    }
    public class Global
    {
        public int nb_matches { get; set; }
        public int nb_vocalizations { get; set; }
        public int nb_words { get; set; }
    }

    public class IndividualWordElement
    {
        public int nb_derivations_extra { get; set; }
        public int nb_matches { get; set; }
        public int nb_derivations { get; set; }
        public int nb_synonyms { get; set; }
        public string[] derivations_extra { get; set; }
        public string word { get; set; }
        public int nb_vocalizations { get; set; }
        public string[] vocalizations { get; set; }
        public object[] synonyms { get; set; }
        public string lemma { get; set; }
        public object romanization { get; set; }
        public string root { get; set; }
        public int nb_ayas { get; set; }
        public string[] derivations { get; set; }
    }

    public class Interval
    {
        public int start { get; set; }
        public int total { get; set; }
        public int end { get; set; }
        public int page { get; set; }
        public int nb_pages { get; set; }
    }

    public class Error
    {
        public string msg { get; set; }
        public int code { get; set; }
    }




}
