using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using Windows.ApplicationModel;
using Windows.Networking.Connectivity;
using Windows.Storage;
using Windows.UI.Popups; 
using GalaSoft.MvvmLight;
using GalaSoft.MvvmLight.Command;
using AlFanous.Common;
using AlFanous.Model;
using GalaSoft.MvvmLight.Messaging; 
using Newtonsoft.Json;

namespace AlFanous.ViewModel
{
    /// <summary>
    /// This class contains properties that the main View can data bind to.
    /// <para>
    /// See http://www.galasoft.ch/mvvm
    /// </para>
    /// </summary>
    public class MainViewModel : ViewModelBase
    {

        private readonly IDataService _dataService;
        private readonly INavigationService _navigationService;

        private RelayCommand _navigateCommand;
        public Dictionary<int,string> RecitatorDictionary = new Dictionary<int, string>(); 
        public Dictionary<string,string> SoundNamesDictionary = new Dictionary<string, string>(); 

        /// <summary>
        /// Gets the NavigateCommand.
        /// </summary>
        public RelayCommand NavigateCommand
        {
            get
            {
                return _navigateCommand
                       ?? (_navigateCommand = new RelayCommand(
                           () => _navigationService.Navigate(typeof(SecondPage))));
            }
        }

        public RelayCommand ListenAyaCommand { get; set; }
        public RelayCommand GoNextPageCommand { get; set; }
        public RelayCommand GoPreviousPageCommand { get; set; }
        public int CurrentAyaIndex { get; set; }
        public AyaElement CurrentAya { get; set; }

        public bool IsPlaying { get; set; }
        /// <summary>
        /// Initializes a new instance of the MainViewModel class.
        /// </summary>
        public MainViewModel(
            IDataService dataService,
            INavigationService navigationService)
        {
            _dataService = dataService;
            _navigationService = navigationService;
            ListenAyaCommand = new RelayCommand(ListenToAyaAction);
            GoNextPageCommand = new RelayCommand(GoToNextPageAction);
            GoPreviousPageCommand = new RelayCommand(GoPreviousPageAction);
            FillRecitator();
            Initialize();
            if (IsInDesignMode)
            {
                _dataService.GetData();
            }
            SearchPage = 1;

            Messenger.Default.Register<NotificationMessage<string>>(this, SearchAction);
        }
   
        private async void GoToNextPageAction()
        {
            if (SearchPage >= TotalPages)
                return;
            SearchPage++;
            await Search(Query, SearchPage);
        }

        private  async void GoPreviousPageAction()
        {
            if (SearchPage<=1)
                return;
            SearchPage--;
            await Search(Query, SearchPage);
        }

        private void ListenToAyaAction()
        {
            if (IsPlaying)
            {  
                Messenger.Default.Send<int>(0);
            }
            else
            {
                RecitatorId = IndeConverter(RecitatorPlaceOnList);
                var name = RecitatorDictionary[RecitatorId];
                SetNewRecitator(name);
                CurrentAyaSong = CurrentAya.aya.recitation;
                Messenger.Default.Send<int>(1); 
            }
 
        }

        public ObservableCollection<string> RecitatorsNames { get; set; }
        public void FillRecitator()
        {
            RecitatorDictionary.Add(8, "عبد الرحمن السديس");
            SoundNamesDictionary.Add("عبد الرحمن السديس", "Abdurrahmaan_As-Sudais_192kbps");

            RecitatorDictionary.Add(16, "سعد الغامدي");
            SoundNamesDictionary.Add("سعد الغامدي", "Ghamadi_40kbps");

            RecitatorDictionary.Add(15, "مشاري راشد العفاسي");
            SoundNamesDictionary.Add("مشاري راشد العفاسي", "Alafasy_128kbps");


            RecitatorDictionary.Add(44, "سعود الشريم");
            SoundNamesDictionary.Add("سعود الشريم", "Saood_ash-Shuraym_128kbps");

            RecitatorDictionary.Add(13, "أحمد بن علي العجمي");
            SoundNamesDictionary.Add("أحمد بن علي العجمي", "Ahmed_ibn_Ali_al-Ajamy_128kbps_ketaballah.net");


            RecitatorDictionary.Add(3, "عبد الباسط عبد الصمد");
            SoundNamesDictionary.Add("عبد الباسط عبد الصمد", "Abdul_Basit_Mujawwad_128kbps");


            RecitatorDictionary.Add(51, "صلاح عبد الرحمن بو خاطر");
            SoundNamesDictionary.Add("صلاح عبد الرحمن بو خاطر", "Salaah_AbdulRahman_Bukhatir_128kbps");

            RecitatorDictionary.Add(33, "محمد صديق المنشاوي");
            SoundNamesDictionary.Add("محمد صديق المنشاوي", "Minshawy_Mujawwad_192kbps");


            RecitatorDictionary.Add(6, "عبد الله بسفر");
            SoundNamesDictionary.Add("عبد الله بسفر", "Abdullah_Basfar_192kbps");


            RecitatorDictionary.Add(11, "ابو بكر الشاطري");
            SoundNamesDictionary.Add("ابو بكر الشاطري", "Abu_Bakr_Ash-Shaatree_128kbps");


            RecitatorDictionary.Add(18, "هاني الرفاعي");
            SoundNamesDictionary.Add("هاني الرفاعي", "Hani_Rifai_192kbps");


            RecitatorDictionary.Add(20, "محمود خليل الحصري");
            SoundNamesDictionary.Add("محمود خليل الحصري", "Husary_128kbps");


            RecitatorDictionary.Add(25, "علي بن عبدالرحمن الحذيفي");
            SoundNamesDictionary.Add("علي بن عبدالرحمن الحذيفي", "Hudhaify_128kbps");

            RecitatorsNames = new ObservableCollection<string>(RecitatorDictionary.Values.ToList());
         
            RecitatorPlaceOnList = 0;
            RecitatorId = IndeConverter(RecitatorPlaceOnList);
            RecitatorId = RecitatorId;
        }
        public async void SearchAction(NotificationMessage<string> obj)
        {
            if (obj.Notification == "SearchQuery")
            {
                Query = obj.Content;
                SearchPage = 1;
                await Search(Query,SearchPage);
            } 
            else if (obj.Notification == "DetailPage")
            {
                _navigationService.Navigate(typeof (AyaDetail));
            }
        }

        public async void NextPageSearch()
        {
            if(string.IsNullOrEmpty(Query))
                return;
            if(SearchQueryResponse == null)
                return;
            else
            {
                 if(SearchQueryResponse.search.interval.nb_pages > SearchPage)
                     await Search(Query, SearchPage+1);
            }
            
        }
        public async void PreviousPageSearch()
        {
            if (string.IsNullOrEmpty(Query))
                return;
            if (SearchQueryResponse == null)
                return;
            else
            {
                if (SearchPage>1)
                    await Search(Query, SearchPage - 1);
            }
        }

        public string CurrentAyaSong { get; set; }
        public ObservableCollection<AyaElement> AyatesCollection { get; set; }

        public string SearchApiUri = "http://www.alfanous.org/jos2?action=search";
        public int TotalPages { get; set; }
        public int SearchPage { get; set; }
        public string Query { get; set; }
        public int RecitatorId
        {
            get;
            set;
        }

        public int RecitatorPlaceOnList { get; set; }
        public FanousQueryResponse SearchQueryResponse { get; set; }

        public static bool IsConnectedToInternet()
        {
            ConnectionProfile connectionProfile = NetworkInformation.GetInternetConnectionProfile();
            return (connectionProfile != null &&
                connectionProfile.GetNetworkConnectivityLevel() == NetworkConnectivityLevel.InternetAccess);
        }

        public async Task Search(string query, int page)
        {
            if (!IsConnectedToInternet())
            {
                var messageDialog = new MessageDialog("البرنامج لم يستطع الاتصال بالانترنت، يرجى التأكد من وجود الاتصال ");
                messageDialog.Commands.Add(new UICommand("موافق", delegate(IUICommand command)
                {
                    // write your business logic
                }));

                // call the ShowAsync() method to display the message dialog
                messageDialog.ShowAsync();   
            }
            else
            {
  
            ///TODO delete this code
            /// 
          //var p = Path.Combine(Package.Current.InstalledLocation.Path, "Assets/moq.json");
          //try
          //{
          //    if (SearchQueryResponse != null)
          //    {
          //        NavigateCommand.Execute(null);
          //        return;
          //    }
          //         
          //
          //    var folder = await StorageFolder.GetFolderFromPathAsync(Path.GetDirectoryName(p));
          //    using (var stream = await folder.OpenStreamForReadAsync(Path.GetFileName(p)))
          //    {
          //        using (var streamReader = new StreamReader(stream))
          //        {
          //            var content = streamReader.ReadToEnd();
          //            try
          //            {
          //                SearchQueryResponse = JsonConvert.DeserializeObject<FanousQueryResponse>(content);
          //                TotalPages = SearchQueryResponse.search.interval.nb_pages;
          //                foreach (var a in SearchQueryResponse.search.ayas)
          //                {
          //                    a.aya.keyword =
          //                        SearchQueryResponse.search.words.individual.FirstOrDefault().word;
          //                }
          //                AyatesCollection =
          //                    new ObservableCollection<AyaElement>(SearchQueryResponse.search.ayas.
          //                        OrderByDescending((x) => x.aya.text_no_highlight.Length));
          //
          //                var r = AyatesCollection.FirstOrDefault().aya.text;
          //                NavigateCommand.Execute(null);
          //                return;
          //            }
          //            catch (Exception e)
          //            {
          //                
          //                throw e;
          //            }
          //        }
          //    }
          //}
          //catch (Exception e)
          //{
          //    
          //    throw e ;
          //}
          //
          //return ;
 
            using (var client = new HttpClient())
            {
                var uri = SearchApiUri + "&unit=aya&query=" + query + "&highlight=html&page=" + page + "&sortedby=score&&translation=en.maududi";
                var respo = await client.GetAsync(uri);
                respo.EnsureSuccessStatusCode();

                var content = await respo.Content.ReadAsStringAsync();
                try
                {
                    SearchQueryResponse = JsonConvert.DeserializeObject<FanousQueryResponse>(content);
                    TotalPages = SearchQueryResponse.search.interval.nb_pages;
                    foreach (var a in SearchQueryResponse.search.ayas)
                    {
                        a.aya.keyword =
                            SearchQueryResponse.search.words.individual.FirstOrDefault().word;
                    }
                    AyatesCollection = 
                        new ObservableCollection<AyaElement>  (SearchQueryResponse.search.ayas.
                            OrderByDescending((x)=>x.aya.text_no_highlight.Length)); 
                    NavigateCommand.Execute(null);
                }
                catch (Exception e)
                {

                    throw e;
                }

            }

            }
        }
        public async Task Load( )
        {
            var p = Path.Combine(Package.Current.InstalledLocation.Path, "Assets/moq.json");
            try
            {
                var folder = await StorageFolder.GetFolderFromPathAsync(Path.GetDirectoryName(p));
                using (var stream = await folder.OpenStreamForReadAsync(Path.GetFileName(p)))
                {
                    using (var streamReader = new StreamReader(stream))
                    {
                        var content = streamReader.ReadToEnd();
                        try
                        {
                            SearchQueryResponse = JsonConvert.DeserializeObject<FanousQueryResponse>(content);
                            TotalPages = SearchQueryResponse.search.interval.nb_pages;
                            foreach (var a in SearchQueryResponse.search.ayas)
                            {
                                a.aya.keyword =
                                    SearchQueryResponse.search.words.individual.FirstOrDefault().word;
                            }
                            AyatesCollection =
                                new ObservableCollection<AyaElement>(SearchQueryResponse.search.ayas.
                                    OrderByDescending((x) => x.aya.text_no_highlight.Length));

                            var r = AyatesCollection.FirstOrDefault().aya.text;
                           
                            return;
                        }
                        catch (Exception e)
                        {

                            throw e;
                        }
                    }
                }
            }
            catch (Exception e)
            {

                throw e;
            }
        }

        private async Task Initialize()
        {
            CurrentAyaSong = "";
            try
            {
                await Load();
            }
            catch (Exception ex)
            {
                // Report error here
            }
        }

        public void SaveProfile(int recitatorId)
        {
            var composite = new ApplicationDataCompositeValue();
            RecitatorId = RecitatorId;
            composite["recitatorId"] = RecitatorId; 

            var roamingSettings = ApplicationData.Current.RoamingSettings;
            roamingSettings.Values["profile"] = composite;
        }

        public void ReadProfile()
        {
            var roamingSettings = ApplicationData.Current.RoamingSettings;

            // roamingSettings.Values["profile"] = composite;

            //check if there is already a profile
            if (roamingSettings.Values.ContainsKey("profile"))
            {
                var composite = roamingSettings.Values["profile"] as ApplicationDataCompositeValue;
                if (composite != null)
                {
                    if (composite.ContainsKey("recitatorId"))
                    {
                        var selected = composite["recitatorId"] as int?;
                        if (selected != null)
                        {
                            RecitatorId = selected.Value;
                        } 
                    } 
                }
            }
        }

        public void RefreshData(ApplicationData freshData)
        {
            var roamingSettings = freshData.RoamingSettings;
            // roamingSettings.Values["profile"] = composite;

            //check if there is already a profile
            if (roamingSettings.Values.ContainsKey("profile"))
            {
                var composite = roamingSettings.Values["profile"] as ApplicationDataCompositeValue;
                if (composite != null)
                {
                    if (composite.ContainsKey("recitatorId"))
                    {
                        var selected = composite["recitatorId"] as int?;
                        if (selected != null)
                        {
                            RecitatorId = selected.Value;
                        }
                    } 
                }
            }
            SaveProfile(RecitatorId);
        }

        public int IndeConverter(int listIndex)
        {
            int recitationIndex = 0;
            var name =  RecitatorsNames.ElementAt(listIndex);
                foreach (var key in  RecitatorDictionary)
                {
                    if (key.Value == name)
                    {
                        recitationIndex = key.Key;
                        return recitationIndex;
                    }
                        
                }
            return recitationIndex = 0;
        }

        public void SetNewRecitator(string name)
        {
            if (CurrentAya == null)
                return;
            if (string.IsNullOrEmpty(CurrentAya.aya.recitation))
                return;
            if (!SoundNamesDictionary.ContainsKey(name))
                return;

            var soundfile = SoundNamesDictionary[name];
           // CurrentAya.aya.recitation = "http://www.everyayah.com/data/Abdul_Basit_Murattal_64kbps/059004.mp3";
            var token = CurrentAya.aya.recitation.Split('/');
            token = token;
            CurrentAya.aya.recitation = "http://www.everyayah.com/data/" + soundfile + "/" + token[5];
        }
        public void ClearRoamingData()
        {
            var roamingSettings = ApplicationData.Current.RoamingSettings;
            roamingSettings.Values.Clear();
        }

    }
}