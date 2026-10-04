import { useEffect, useState } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
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
    const { search } = useOutletContext();
    const [loadError,setLoadError]=useState(false);

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
                setLoadError(true);

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

    if(loadError){
        return <div className="dashboard-page"><div className="dashboard-panel" role="alert"><h2>Dashboard couldn’t load</h2><p>Please refresh the page to try again.</p><button onClick={() => window.location.reload()}>Refresh</button></div></div>;
    }

    if(!stats||!marketing){

        return <Loading/>;

    }

    return(

        <div className="dashboard-page">

            <DashboardHeader />

            <StatsGrid
                stats={stats}
                marketing={marketing}
            />

            <div className="dashboard-grid">

            <PerformanceChart />

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

    campaigns.filter(c => ["scheduled", "draft", "queued"].includes(String(c.status).toLowerCase())).length ? campaigns.filter(c => ["scheduled", "draft", "queued"].includes(String(c.status).toLowerCase())).slice(0,3).map(c=>(

<div onClick={() => navigate("/campaigns/" + c.id + "/details")} className="upcoming-card" key={c.id}>

<div>

<strong>{c.name}</strong>

<p>{c.status}</p>

</div>

<span>

{c.sent ?? 0}

</span>

</div>

)) : <p className="dashboard-empty">No upcoming campaigns.</p>

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

<button onClick={() => navigate("/contacts")}>Manage Contacts</button>

<button onClick={() => navigate("/templates/create")}>Create Template</button>


</div>

</div>

</div>

</div>

);

}
