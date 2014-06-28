using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using Windows.Foundation;
using Windows.Foundation.Collections;
using Windows.UI;
using Windows.UI.Text;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Controls.Primitives;
using Windows.UI.Xaml.Data;
using Windows.UI.Xaml.Documents;
using Windows.UI.Xaml.Input;
using Windows.UI.Xaml.Media;
using Windows.UI.Xaml.Navigation;

// The User Control item template is documented at http://go.microsoft.com/fwlink/?LinkId=234236
using AlFanous.Model;

namespace AlFanous.UserControll
{
    public sealed partial class HilightingControl : UserControl
    {
        private static PropertyMetadata propertymetadata = new PropertyMetadata(default(string), PropertyChangedCallback);
        private static PropertyMetadata keywordmetadata = new PropertyMetadata(default(string), KeywordPropertyChangedCallBack);

        private static void KeywordPropertyChangedCallBack(DependencyObject dependencyObject, DependencyPropertyChangedEventArgs dependencyPropertyChangedEventArgs)
        {
            var text = dependencyPropertyChangedEventArgs.NewValue as string;

            var obj = dependencyObject as HilightingControl;
        }

        private static void PropertyChangedCallback(DependencyObject dependencyObject, DependencyPropertyChangedEventArgs dependencyPropertyChangedEventArgs)
        {
            var text = dependencyPropertyChangedEventArgs.NewValue as string;

            var obj = dependencyObject as HilightingControl;
            
            if (obj != null)
                if (text != null)
                {
                   // if(string.IsNullOrEmpty(obj.KeyWord))
                   //     obj.FormatText(text.text_no_highlight, text.keyword);
                   // else
                        obj.FormatText(text, obj.KeyWord);
                }
                     
        }
        public static readonly DependencyProperty PlainTextProperty = DependencyProperty.Register(
            "PlainText", typeof(string), typeof(HilightingControl), propertymetadata);

        public string PlainText
        {
            get { return (string)GetValue(PlainTextProperty); }
            set { SetValue(PlainTextProperty, value); }
        }

        public static readonly DependencyProperty KeyWordProperty = DependencyProperty.Register(
            "KeyWord", typeof(string), typeof(HilightingControl), keywordmetadata);

        public string KeyWord
        {
            get { return (string) GetValue(KeyWordProperty); }
            set { SetValue(KeyWordProperty, value); }
        }

        public static readonly DependencyProperty KeywordColorProperty = DependencyProperty.Register(
            "KeywordColor", typeof(Color), typeof(HilightingControl), new PropertyMetadata(Colors.Red));

        public Color KeywordColor
        {
            get { return (Color) GetValue(KeywordColorProperty); }
            set { SetValue(KeywordColorProperty, value); }
        }

        public static readonly DependencyProperty TextColorProperty = DependencyProperty.Register(
            "TextColor", typeof(Color), typeof(HilightingControl), new PropertyMetadata(Colors.Black));

        public Color TextColor
        {
            get { return  (Color)GetValue(TextColorProperty); }
            set { SetValue(TextColorProperty, value); }
        }

        public static readonly DependencyProperty BraketColorProperty = DependencyProperty.Register(
            "BraketColor", typeof(Color), typeof(HilightingControl), new PropertyMetadata(Colors.Blue));

        public Color BraketColor
        {
            get { return  (Color)GetValue(BraketColorProperty); }
            set { SetValue(BraketColorProperty, value); }
        } 
        private void FormatText(string text, string keyword)
        {
            if(string.IsNullOrEmpty(keyword))
                return;
            this.Root.Children.Clear();
            var token = text.Replace(keyword,"#").Split('#');
            TextBlock textBlock = new TextBlock();
            textBlock.TextWrapping = TextWrapping.WrapWholeWords;
            textBlock.TextAlignment = TextAlignment.Center;
            var Lpar = new Run();
            Lpar.Text = "[ ";
            Lpar.Foreground = new SolidColorBrush(BraketColor);
            textBlock.Inlines.Add(Lpar);
            for (int i = 0; i < token.Length; i++)
            {
                var s = token[i];
                Run r = new Run();
                r.Text = s;
                textBlock.Inlines.Add(r);

                if (i + 1 < token.Length)
                {
                    // hilighting
                    r = new Run();
                    r.Text = " "+keyword+" ";
                    r.Foreground = new SolidColorBrush(KeywordColor);
                   
                    textBlock.Inlines.Add(r);
                }
            }  
            textBlock.HorizontalAlignment = HorizontalAlignment.Center;
            textBlock.VerticalAlignment = VerticalAlignment.Center;
            textBlock.FontFamily = new FontFamily("Assets/fonts/arabeyes-qr.ttf#ArabeyesQr");
            Lpar = new Run();
            Lpar.Text = " ]";
            Lpar.Foreground = new SolidColorBrush(BraketColor);
            textBlock.Inlines.Add(Lpar);
            this.Root.Children.Add(textBlock);
            token = token;
        }
        public HilightingControl()
        {
            this.InitializeComponent();
        }
    }
}
