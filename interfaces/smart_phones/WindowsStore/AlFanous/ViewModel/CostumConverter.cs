using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using AlFanous.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace AlFanous.ViewModel
{
    public class SingleValueArrayConverter<T> : JsonConverter
    {
        public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
        {
            throw new NotImplementedException();
        }

        public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
        {
 
            var retVal = new List<T>();
            retVal = new List<T>() { };
            // T instance = (T)serializer.Deserialize(reader, typeof(T)); 
            JObject instance = (JObject)serializer.Deserialize(reader);
            instance = instance;
            foreach (var element in instance)
            {
                var temp = JsonConvert.DeserializeObject<T>(element.Value.ToString());
                retVal.Add(temp);
            }
            return retVal;
        }

        public override bool CanConvert(Type objectType)
        {
            return false;
        }
    }
}
