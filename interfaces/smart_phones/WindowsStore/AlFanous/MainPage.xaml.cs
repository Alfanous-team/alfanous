using System;
using System.Collections.ObjectModel;
using System.Net.Http;
using System.Threading.Tasks;
using Windows.UI.Xaml.Controls;
using AlFanous.Model;
using AlFanous.ViewModel;
using GalaSoft.MvvmLight.Messaging;
using Newtonsoft.Json;

namespace AlFanous
{
    public sealed partial class MainPage
    {
        /// <summary>
        /// Gets the view's ViewModel.
        /// </summary>
        public MainViewModel Vm
        {
            get
            {
                return (MainViewModel)DataContext;
            }
        }

       
        public MainPage()
        {
            InitializeComponent(); 

        }

 

        private void SearchBox_QuerySubmitted(SearchBox sender,SearchBoxQuerySubmittedEventArgs args)
        {
            if (string.IsNullOrEmpty(args.QueryText))
                return;
            
            Messenger.Default.Send(new NotificationMessage<string>(this, args.QueryText, "SearchQuery"));
        }

        private void SearchBox_QueryChanged(SearchBox sender, SearchBoxQueryChangedEventArgs args)
        {
            int a = 0;
            a = a;
        }

        private void SearchBox_SuggestionsRequested(SearchBox sender, SearchBoxSuggestionsRequestedEventArgs args)
        {

        }

 
    }
 
}