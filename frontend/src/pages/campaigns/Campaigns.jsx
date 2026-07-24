import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";


export default function Campaigns(){

const [campaigns,setCampaigns] = useState([]);
const [loading,setLoading] = useState(null);


function load(){

api.get("/campaigns/")
.then(res=>{
setCampaigns(res.data);
});

}


useEffect(()=>{
load();
},[]);



async function prepare(id){

setLoading(id);

try{
await api.post(`/campaigns/${id}/prepare`);
load();
}
finally{
setLoading(null);
}

}



async function send(id){

setLoading(id);

await api.post(`/campaigns/${id}/send`);

setTimeout(()=>{
load();
setLoading(null);
},3000);

}



async function retry(id){

setLoading(id);

try{
await api.post(`/campaigns/${id}/retry`);
load();
}
finally{
setLoading(null);
}

}



function statusClass(status){

return status.toLowerCase();

}



return (

<div className="campaign-page">


<div className="page-header">

<div>

<h1>
Campaigns
</h1>

<p>
Manage and track your email campaigns
</p>

</div>


<Link to="/campaigns/create">

<button className="create-btn">
+ Create Campaign
</button>

</Link>


</div>




<div className="campaign-grid">


{
campaigns.map(c=>(


<div className="campaign-card" key={c.id}>


<h2>
{c.name}
</h2>



<span className={`status ${statusClass(c.status)}`}>
{c.status}
</span>



<div className="campaign-stats">

<p>
👥 Recipients
<strong>{c.total_recipients}</strong>
</p>


<p>
✉ Sent
<strong>{c.sent_count}</strong>
</p>


<p>
⚠ Failed
<strong>{c.failed_count}</strong>
</p>


</div>




<div className="action-buttons">


{
(c.status==="DRAFT" || c.status==="draft") &&

<button
disabled={loading===c.id}
onClick={()=>prepare(c.id)}
>
{loading===c.id ? "Preparing..." : "Prepare"}
</button>

}



{
(c.status==="PREPARED" || c.status==="prepared") &&

<button
disabled={loading===c.id}
onClick={()=>send(c.id)}
>
{loading===c.id ? "Sending..." : "Send"}
</button>

}



{
(c.status==="FAILED" || c.status==="failed") &&

<button
disabled={loading===c.id}
onClick={()=>retry(c.id)}
>
{loading===c.id ? "Retrying..." : "Retry"}
</button>

}



<Link to={`/campaigns/${c.id}/analytics`}>
<button>
Analytics
</button>
</Link>


<Link to={`/campaigns/${c.id}/details`}>
<button>
Details
</button>
</Link>


<Link to={`/campaigns/${c.id}/performance`}>
<button>
Performance
</button>
</Link>



</div>


</div>


))
}


</div>


</div>

)

}
