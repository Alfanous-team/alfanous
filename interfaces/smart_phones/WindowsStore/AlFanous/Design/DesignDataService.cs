using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Windows.ApplicationModel;
using Windows.Storage;
using AlFanous.Model;
using AlFanous.ViewModel;
using Newtonsoft.Json;

namespace AlFanous.Design
{
    public class DesignDataService : IDataService
    {
        public async Task<FanousQueryResponse> GetData()
        {
            //var vm = new ViewModelLocator().Main;

            //var js = "";
            //// Use this to create design time data
            //var file = Path.Combine(Package.Current.InstalledLocation.Path, "Assets/fonts/jos2.json");
            //var jsonFolder = await StorageFolder.GetFolderFromPathAsync(Path.GetDirectoryName(file));
            //using (var jsonStream = await jsonFolder.OpenStreamForReadAsync(Path.GetFileName(file)))
            //{
            //    using (var streamReader = new StreamReader(jsonStream))
            //    {
            //        js = streamReader.ReadToEnd();
            //    }
            //}
            //var item =  JsonConvert.DeserializeObject<FanousQueryResponse>(js);

            //vm.TotalPages = vm.SearchQueryResponse.search.interval.nb_pages;
            //foreach (var a in vm.SearchQueryResponse.search.ayas)
            //{
            //    a.aya.keyword =
            //        vm.SearchQueryResponse.search.words.individual.FirstOrDefault().word;
            //}
            //vm.AyatesCollection =
            //    new ObservableCollection<AyaElement>(vm.SearchQueryResponse.search.ayas.
            //        OrderByDescending((x) => x.aya.text_no_highlight.Length));
            //return  item;
            return null;
        }

        public async Task GetFake()
        {
             
            
        }
    }
}