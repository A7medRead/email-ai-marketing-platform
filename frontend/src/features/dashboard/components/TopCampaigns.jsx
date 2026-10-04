
export default function TopCampaigns({campaigns,search=""}){

    const filteredCampaigns = campaigns.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase())
);

return(

        <div className="dashboard-panel top-campaigns-panel">

            <div className="panel-header">

                <h3>

                    Top Campaigns

                </h3>

                <button className="view-all-btn">

                    View all

                </button>

            </div>

            <table className="dashboard-table">

                <thead>

                    <tr>

                        <th>Campaign</th>

                        <th>Recipients</th>

                        <th>Open Rate</th>

                        <th>Click Rate</th>

                    </tr>

                </thead>

                <tbody>

                    {

                        filteredCampaigns.slice(0,5).map(c=>(

                            <tr key={c.id}>

                                <td>

                                    <div className="campaign-cell">

                                        <div className="campaign-image">

                                            📧

                                        </div>

                                        <div>

                                            <strong>

                                                {c.name}

                                            </strong>

                                            <div className="campaign-status">

                                                Completed

                                            </div>

                                        </div>

                                    </div>

                                </td>

                                <td>

                                    {c.sent ?? 0}

                                </td>

                                <td>

                                    {c.success_rate}%

                                </td>

                                <td>

                                    {

                                        (
                                            Number(c.success_rate||0)*0.22

                                        ).toFixed(1)

                                    }%

                                </td>

                            </tr>

                        ))

                    }

                </tbody>

            </table>

        </div>

    )

}
