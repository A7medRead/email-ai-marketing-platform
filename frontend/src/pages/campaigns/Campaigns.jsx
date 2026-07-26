import "./Campaigns.css";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Loading from "../../components/Loading";
import EmptyState from "../../components/EmptyState";


export default function Campaigns(){

const [campaigns,setCampaigns] = useState([]);
const [search,setSearch] = useState("");
const [status,setStatus] = useState("");
const [page,setPage] = useState(1);
const [hasMore,setHasMore] = useState(true);
const [loading,setLoading] = useState(null);
const [pageLoading,setPageLoading] = useState(true);


function load(){

api.get("/campaigns/",{
params:{
page,
limit:10,
search,
status
}
})
.then(res=>{
setCampaigns(res.data);
setHasMore(res.data.length === 10);
})
.finally(()=>{
setPageLoading(false);
});

}


useEffect(()=>{
load();
},[page,search,status]);



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



if(pageLoading)
return <Loading />;


return (

<div className="campaigns-page">


<div className="campaigns-header">

<div>

<h1>
Campaigns
</h1>

<p>
Manage and track your email campaigns
</p>

</div>


<Link to="/campaigns/create">

<Button>
+ Create Campaign
</Button>

</Link>


</div>




<input
placeholder="Search campaigns..."
value={search}
onChange={(e)=>{
setPage(1);
setSearch(e.target.value);
}}
className="contact-search"
/>


<select
value={status}
onChange={(e)=>{
setPage(1);
setStatus(e.target.value);
}}
>

<option value="">
All Status
</option>

<option value="DRAFT">
Draft
</option>

<option value="PREPARED">
Prepared
</option>

<option value="RUNNING">
Running
</option>

<option value="COMPLETED">
Completed
</option>

<option value="FAILED">
Failed
</option>

</select>


<div className="campaigns-grid">


{
campaigns.length === 0
?
<EmptyState
title="No campaigns yet"
message="Create your first email campaign"
/>
:
campaigns.map(c=>( 


<Card className="campaigns-card" key={c.id}>


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

<Button
disabled={loading===c.id}
onClick={()=>prepare(c.id)}
>
{loading===c.id ? "Preparing..." : "Prepare"}
</Button>

}



{
(c.status==="PREPARED" || c.status==="prepared") &&

<Button
disabled={loading===c.id}
onClick={()=>send(c.id)}
>
{loading===c.id ? "Sending..." : "Send"}
</Button>

}



{
(c.status==="FAILED" || c.status==="failed") &&

<Button
variant="secondary"
disabled={loading===c.id}
onClick={()=>retry(c.id)}
>
{loading===c.id ? "Retrying..." : "Retry"}
</Button>

}



<Link to={`/campaigns/${c.id}/analytics`}>
<Button variant="secondary">
Analytics
</Button>
</Link>


<Link to={`/campaigns/${c.id}/details`}>
<Button variant="secondary">
Details
</Button>
</Link>


<Link to={`/campaigns/${c.id}/performance`}>
<Button variant="secondary">
Performance
</Button>
</Link>



</div>


</Card>


))
}


</div>



<div className="contacts-pagination">

<Button
variant="secondary"
disabled={page===1}
onClick={()=>setPage(page-1)}
>
← Previous
</Button>


<span>
Page {page}
</span>


<Button
variant="secondary"
disabled={!hasMore}
onClick={()=>setPage(page+1)}
>
Next →
</Button>


</div>



</div>

)

}
