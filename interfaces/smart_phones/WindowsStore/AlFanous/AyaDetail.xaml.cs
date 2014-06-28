using Windows.ApplicationModel.DataTransfer;
using Windows.UI.ApplicationSettings;
using Windows.UI.Popups;
using AlFanous.Common;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using Windows.Foundation;
using Windows.Foundation.Collections;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Controls.Primitives;
using Windows.UI.Xaml.Data;
using Windows.UI.Xaml.Input;
using Windows.UI.Xaml.Media;
using Windows.UI.Xaml.Navigation;

// The Basic Page item template is documented at http://go.microsoft.com/fwlink/?LinkId=234237
using AlFanous.Model;
using AlFanous.ViewModel;
using GalaSoft.MvvmLight.Messaging;

namespace AlFanous
{
    /// <summary>
    /// A basic page that provides characteristics common to most applications.
    /// </summary>
    public sealed partial class AyaDetail : Page
    {

        private NavigationHelper navigationHelper; 
        /// <summary>
        /// NavigationHelper is used on each page to aid in navigation and 
        /// process lifetime management
        /// </summary>
        public NavigationHelper NavigationHelper
        {
            get { return this.navigationHelper; }
        }

        private MainViewModel vm = new ViewModelLocator().Main;
        public AyaDetail()
        {
            this.InitializeComponent();
            this.navigationHelper = new NavigationHelper(this);
            this.navigationHelper.LoadState += navigationHelper_LoadState;
            this.navigationHelper.SaveState += navigationHelper_SaveState;
            Messenger.Default.Register<int>(this,ListenAction);

            DataTransferManager dataTransferManager = DataTransferManager.GetForCurrentView();
            dataTransferManager.DataRequested += new TypedEventHandler<DataTransferManager,
                DataRequestedEventArgs>(this.ShareTextHandler);
        }

  
        private void ShareTextHandler(DataTransferManager sender, DataRequestedEventArgs args)
        {
            DataRequest request = args.Request;
            request.Data.Properties.Title = "نشر نص الأية";
            request.Data.Properties.Description = "ارسل نص الاية الى اصدقاءك";
            var l =  "للاصغاء الى الاية، يرجى زيارة الرابط التالي :" +"\n"+ vm.CurrentAya.aya.recitation;
            var ay = vm.CurrentAya.aya.text_no_highlight + "\n (" + vm.CurrentAya.sura.arabic_name + " - " +
                     vm.CurrentAya.aya.id+") \n";
            request.Data.SetText(ay+"   "+l);
        }

 
        private void ListenAction(int obj)
        {
            if (obj == 0)
            {
                mediaplayer.Pause();
            }
            else
            {
                vm.CurrentAyaSong = vm.CurrentAya.aya.recitation;
                var s = vm.CurrentAyaSong;
                s = s;
                if (mediaplayer.CurrentState != MediaElementState.Playing)
                {
                    mediaplayer.Play();
                }
            }
 
        }
        private void Mediaplayer_OnMediaEnded(object sender, RoutedEventArgs e)
        {
            vm.CurrentAyaSong = "";
        }

        /// <summary>
        /// Populates the page with content passed during navigation. Any saved state is also
        /// provided when recreating a page from a prior session.
        /// </summary>
        /// <param name="sender">
        /// The source of the event; typically <see cref="NavigationHelper"/>
        /// </param>
        /// <param name="e">Event data that provides both the navigation parameter passed to
        /// <see cref="Frame.Navigate(Type, Object)"/> when this page was initially requested and
        /// a dictionary of state preserved by this page during an earlier
        /// session. The state will be null the first time a page is visited.</param>
        private void navigationHelper_LoadState(object sender, LoadStateEventArgs e)
        {
        }

        /// <summary>
        /// Preserves state associated with this page in case the application is suspended or the
        /// page is discarded from the navigation cache.  Values must conform to the serialization
        /// requirements of <see cref="SuspensionManager.SessionState"/>.
        /// </summary>
        /// <param name="sender">The source of the event; typically <see cref="NavigationHelper"/></param>
        /// <param name="e">Event data that provides an empty dictionary to be populated with
        /// serializable state.</param>
        private void navigationHelper_SaveState(object sender, SaveStateEventArgs e)
        {
        }

        #region NavigationHelper registration

        /// The methods provided in this section are simply used to allow
        /// NavigationHelper to respond to the page's navigation methods.
        /// 
        /// Page specific logic should be placed in event handlers for the  
        /// <see cref="GridCS.Common.NavigationHelper.LoadState"/>
        /// and <see cref="GridCS.Common.NavigationHelper.SaveState"/>.
        /// The navigation parameter is available in the LoadState method 
        /// in addition to page state preserved during an earlier session.

        protected override void OnNavigatedTo(NavigationEventArgs e)
        {
            navigationHelper.OnNavigatedTo(e);
             
        }

        protected override void OnNavigatedFrom(NavigationEventArgs e)
        {
            vm.CurrentAyaSong = "";
            Messenger.Default.Unregister<int>(this, ListenAction);
            navigationHelper.OnNavigatedFrom(e);
        }

        #endregion

        private void AyaFlipView_Loaded(object sender, RoutedEventArgs e)
        {
            var i = vm.CurrentAyaIndex;
            AyaFlipView.SelectedItem = vm.CurrentAya;

        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
 

        }

        private void Button_Click_1(object sender, RoutedEventArgs e)
        { 
        }


        private void Mediaplayer_OnCurrentStateChanged(object sender, RoutedEventArgs e)
        {
            if (mediaplayer.CurrentState == MediaElementState.Playing)
                vm.IsPlaying = true;
            else
                vm.IsPlaying = false;
        }
    }
}
