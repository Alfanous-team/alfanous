using System.Threading.Tasks;

namespace AlFanous.Model
{
    public interface IDataService
    {
        Task<FanousQueryResponse> GetData();
    }
}