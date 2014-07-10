using AlFanous.Model;
using AlFanous.ViewModel;
using GalaSoft.MvvmLight.Messaging;

namespace AlFanous
{
    public sealed partial class SecondPage
    {
        public SecondPage()
        {
            InitializeComponent();
        }

        private void ListView_SelectionChanged(object sender, Windows.UI.Xaml.Controls.SelectionChangedEventArgs e)
        {
            var vm = new ViewModelLocator().Main;

            vm.CurrentAya = AyaMListView.SelectedItem as AyaElement;
            vm.CurrentAyaIndex = AyaMListView.SelectedIndex;
            Messenger.Default.Send(new NotificationMessage<string>(this, string.Empty, "DetailPage"));
        }
    }
}