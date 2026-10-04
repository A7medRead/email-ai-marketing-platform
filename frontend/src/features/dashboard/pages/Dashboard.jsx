import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../../shared/api/client";
import Loading from "../../../shared/ui/Loading";

import DashboardHeader from "../components/DashboardHeader";
import StatsGrid from "../components/StatsGrid";
import PerformanceChart from "../components/PerformanceChart";
import TopCampaigns from "../components/TopCampaigns";

import "./Dashboard.css";

export default function Dashboard(){

    const navigate = useNavigate();

    const [stats,setStats]=useState(null);
    const [marketing,setMarketing]=useState(null);
    const [campaigns,setCampaigns]=useState([]);
    const [activities,setActivities]=useState([]);
    const [search,setSearch]=useState("");

    useEffect(()=>{

        async function load(){

            try{

                const [
                    analytics,
                    marketingData,
                    topCampaigns,
                    activityData
                ]=await Promise.all([

                    api.get("/dashboard/analytics"),
                    api.get("/dashboard/marketing"),
                    api.get("/dashboard/top-campaigns"),
                    api.get("/dashboard/activity")

                ]);

                setStats(analytics.data);
                setMarketing(marketingData.data);
                setCampaigns(topCampaigns.data);
                setActivities(activityData.data);

            }catch(err){

                console.error(err);

            }

        }

        load();

    },[]);
    function formatTimeAgo(date){

    const diff = Math.floor((new Date() - new Date(date)) / 1000);

    if(diff < 60) return "Just now";
    if(diff < 3600) return Math.floor(diff/60) + " minutes ago";
    if(diff < 86400) return Math.floor(diff/3600) + " hours ago";

    return Math.floor(diff/86400) + " days ago";
}

    if(!stats||!marketing){

        return <Loading/>;

    }

    return(

        <div className="dashboard-page">

            <DashboardHeader search={search} setSearch={setSearch} />

            <StatsGrid
                stats={stats}
                marketing={marketing}
            />

            <div className="dashboard-grid">

                <PerformanceChart
                    stats={stats}
                    marketing={marketing}
                />

                <TopCampaigns campaigns={campaigns} search={search} />

            </div>

            <div className="dashboard-bottom">

<div className="dashboard-panel">

<div className="panel-header">

<h3>Recent Activity</h3>

</div>

<div className="activity-list">

{

activities.length ? (

activities.map((a,index)=>(

<div className="activity-item" key={index}>

<div className={`activity-icon ${a.color}`}>
    {a.icon}
</div>

<div>

<strong>
    {a.text}
</strong>

<p>
    {formatTimeAgo(a.time)}
</p>

</div>

</div>

))

) : (

<div className="activity-item">

<strong>
    No recent activity yet
</strong>

</div>

)

}

</div></div>

<div className="dashboard-panel">

<div className="panel-header">

<h3>Upcoming Campaigns</h3>

<button onClick={() => navigate("/campaigns")} className="view-all-btn">View all</button>

</div>

<div className="upcoming-list">

{

campaigns.slice(0,3).map(c=>(

<div onClick={() => navigate("/campaigns/" + c.id + "/details")} className="upcoming-card" key={c.id}>

<div>

<strong>{c.name}</strong>

<p>{c.status}</p>

</div>

<span>

{c.sent ?? 0}

</span>

</div>

))

}

</div>

</div>

<div className="dashboard-panel">

<div className="panel-header">

<h3>Quick Actions</h3>

</div>

<div className="quick-actions">

<button onClick={() => navigate("/campaigns/create")}>Create Campaign</button>

<button onClick={() => navigate("/contacts/create")}>Add Contact</button>

<button onClick={() => navigate("/contacts")}>Import Contacts</button>

<button onClick={() => navigate("/templates/create")}>Create Template</button>

<button onClick={() => navigate("/analytics")}>View Analytics</button>

</div>

</div>

</div>

</div>

);

}
