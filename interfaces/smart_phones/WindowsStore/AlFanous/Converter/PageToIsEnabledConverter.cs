using System;
using Windows.UI.Xaml.Data;
using AlFanous.ViewModel;

namespace AlFanous.Converter
{
    public class BoolToTextConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            var bo = value as bool?;
            if (bo == null)
                return "الإصغاء للآية";
            var b = bo.Value;
            if (b)
            {
                return "ايقاف القراءة";
            }
            else
            {
                return "الإصغاء للآية";
            }
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
    public class BoolToIconConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            var bo = value as bool?;
            if (bo == null)
                return "Play";
            var b =  bo.Value;
            if (b)
            {
                return "Pause";
            }
            else
            {
                return "Play";
            }
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
    class PageToIsEnabledConverter:IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            var vm = new ViewModelLocator().Main;
            var obj = value as int?;
            var p = parameter as string;
            switch (p)
            {
                case "p":
                    if (vm.SearchPage == 1)
                    {
                        // disable
                        return false;
                    }
                    else
                    {
                        return true;
                    }
                    break;
                case "n":
                    if (vm.SearchPage >= vm.TotalPages)
                    {
                        // disable
                        return false;
                    }
                    else
                    {
                        return true;
                    }
                    break;
                default:
                    return false;
                    break;

            }
          
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}
