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

// The Settings Flyout item template is documented at http://go.microsoft.com/fwlink/?LinkId=273769

namespace AlFanous.ViewModel
{
    public sealed partial class SettingsFlyout1 : SettingsFlyout
    {
        public SettingsFlyout1()
        {
            this.InitializeComponent();
              var vm = new ViewModelLocator().Main;
              RecitatorNameComboBox.Loaded += RecitatorNameComboBox_Loaded;
        }

        void RecitatorNameComboBox_Loaded(object sender, RoutedEventArgs e)
        {
            RecitatorNameComboBox.SelectedIndex = new ViewModelLocator().Main.RecitatorPlaceOnList;
        }

        private void SfComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var vm = new ViewModelLocator().Main;
            if (RecitatorNameComboBox.SelectedItem != null)
            {
                var name = vm.RecitatorsNames.ElementAt(RecitatorNameComboBox.SelectedIndex);
                foreach (var key in vm.RecitatorDictionary)
                {
                    if (key.Value == name)
                    {
                        vm.RecitatorPlaceOnList = RecitatorNameComboBox.SelectedIndex;
                        vm.RecitatorId = key.Key;
                        vm.SetNewRecitator(name);
                        vm.SaveProfile(vm.RecitatorPlaceOnList);
                        return;
                    }
                        
                }
                
            }
        }
    }
}
