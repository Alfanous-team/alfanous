using System.Collections.Generic;
using System.Linq;
using GalaSoft.MvvmLight;

namespace farid.Util
{
    public class RequestBuilder : ViewModelBase
    {
        public bool UrlIsLoding
        {
            get { return _isLoading; }
            set
            {
                if (value != _isLoading)
                {
                    _isLoading = value;
                    RaisePropertyChanged(GetPropertyName(() => UrlIsLoding));
                }
            }
        }

        public string CurrentPage
        {
            get { return Parametres["page"]; }
            set
            {
                if (value != Parametres["page"])
                {
                    Parametres["page"] = value;
                    RaisePropertyChanged(GetPropertyName(() => CurrentPage));
                }
            }
        }


        public string Url="";
        public string UrlReady = "";
        public Dictionary<string,string> Parametres = new Dictionary<string, string>();/* accepte :
                                                                                        * api_key
                                                                                        * Lat
                                                                                        * Long
                                                                                        * page
                                                                                        * search[keywords]
                                                                                        * search[conditions][wilaya]
                                                                                        * search[conditions][ville]
                                                                                        * search[refine][wilaya]
                                                                                        * search[refine][ville]
                                                                                        */

        private bool _isLoading;
      //  private bool _currentPage;

        public RequestBuilder()
        {
            Parametres.Add("api_key","");
            Parametres.Add("Lat", "");
            Parametres.Add("Long", "");
            Parametres.Add("page", "");
     
        }

        public string this[string data]
        {
            get { return Parametres[data]; }
            set { Parametres[data] = value; }
        }

        public void PrepareRequestLink()
        {
            string url = "";
            foreach (var para in Parametres.Where(para => para.Value != ""))
            {
                if (url == "")
                {
                    url += para.Key + "=" + para.Value;
                }
                else
                {
                    if (!url.Contains(para.Key))
                    {
                        url += "&" + para.Key + "=" + para.Value;
                    }
                     
                }
                 
            }
            UrlReady = Url + url; 
        }
    }
}
