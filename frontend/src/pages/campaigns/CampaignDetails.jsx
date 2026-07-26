import Button from "../../components/Button";
import "./CampaignDetails.css";
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../../api/client";


export default function CampaignDetails(){

const {id}=useParams();

const [campaign,setCampaign]=useState(null);
const [deliveries,setDeliveries]=useState([]);
const [message,setMessage]=useState("");

const [search,setSearch]=useState("");
const [status,setStatus]=useState("");




const [page, setPage] = useState(1);
const [limit] = useState(25);
const [pages, setPages] = useState(1);
const [hasNext, setHasNext] = useState(false);
const [hasPrevious, setHasPrevious] = useState(false);

async function load(){

const c = await api.get(`/campaigns/${id}`);
setCampaign(c.data);


const d = await api.get(`/campaigns/${id}/deliveries`, {
      params: {
        search,
        status,
        page,
        limit,
      },
    });

setDeliveries(d.data.items);
setPages(d.data.pages);
setHasNext(d.data.has_next);
setHasPrevious(d.data.has_previous);

}



useEffect(()=>{

load();

},[id,search,status,page]);



async function prepare(){

try{

const res = await api.post(
`/campaigns/${id}/prepare`
);

setMessage(res.data.message);

load();

}
catch(err){

console.log(err);
setMessage("Prepare failed");

}

}




async function remove(){

const ok = window.confirm(
"Are you sure you want to delete this campaign?"
);

if(!ok) return;


try{

await api.delete(
`/campaigns/${id}`
);

window.location.href="/campaigns";

}
catch(err){

console.log(err);
setMessage("Delete failed");

}

}



async function send(){

try{

const res = await api.post(
`/campaigns/${id}/send`
);

setMessage(res.data.message);

load();

}
catch(err){

console.log(err);
setMessage("Send failed");

}

}



if(!campaign)
return <h2>Loading...</h2>;



return (

<div className="page">


<Link to="/campaigns">
<Button variant="secondary">
← Back
</Button>
</Link>



<div className="campaigndetails-card"
style={{
marginTop:"30px"
}}
>


<h1>
{campaign.name}
</h1>


<p>
Status: {campaign.status}
</p>


<p>
Subject: {campaign.subject}
</p>


<h3>
Email Preview
</h3>


<div
style={{
background:"#16171d",
padding:"20px",
borderRadius:"12px",
marginBottom:"20px"
}}
dangerouslySetInnerHTML={{
__html: campaign.body || "No content"
}}
/>


<p>
Recipients: {campaign.total_recipients}
</p>


<p>
Sent: {campaign.sent_count}
</p>


<p>
Failed: {campaign.failed_count}
</p>



<div className="campaigndetails-actions">


{
(campaign.status==="draft" || campaign.status==="DRAFT") &&

<Link to={`/campaigns/${id}/edit`}>
<Button
variant="secondary"
>
✎ Edit Campaign
</Button>
</Link>

}



{
(campaign.status==="draft" || campaign.status==="DRAFT") &&

<Button
onClick={prepare}
>
Prepare
</Button>

}


{
(campaign.status==="prepared" || campaign.status==="PREPARED") &&

<Button
onClick={send}
>
Send Campaign
</Button>

}


{
(campaign.status==="running" || campaign.status==="RUNNING") &&

<Button
disabled
>
Sending...
</Button>

}


{
(campaign.status==="completed" || campaign.status==="COMPLETED") &&

<p>
Campaign completed
</p>

}


{
(campaign.status==="draft" || campaign.status==="DRAFT") &&

<Button
variant="danger"
onClick={remove}
>
Delete Campaign
</Button>

}


</div>


{
message &&
<p>
{message}
</p>
}


</div>



<h2 style={{marginTop:"40px"}}>
Email Deliveries
</h2>

<div
style={{
display:"flex",
gap:"12px",
margin:"20px 0",
flexWrap:"wrap"
}}
>

<input
placeholder="Search recipient"
value={search}
onChange={(e)=>setSearch(e.target.value)}
style={{
padding:"10px",
flex:1,
minWidth:"250px"
}}
/>

<select
value={status}
onChange={(e)=>setStatus(e.target.value)}
style={{
padding:"10px"
}}
>

<option value="">
All Statuses
</option>

<option value="pending">
Pending
</option>

<option value="queued">
Queued
</option>

<option value="sent">
Sent
</option>

<option value="failed">
Failed
</option>

<option value="opened">
Opened
</option>

<option value="clicked">
Clicked
</option>

<option value="bounced">
Bounced
</option>

</select>

</div>



<div className="campaigndetails-cards">


{
deliveries.map(d=>(

<div className="campaigndetails-card" key={d.id}>


<h2>
{d.recipient_email}
</h2>


<p>
Status: {d.status}
</p>


<p>
Sent: {d.sent_at || "-"}
</p>


<p>
Opened: {d.opened_at || "-"}
</p>


<p>
Clicked: {d.clicked_at || "-"}
</p>


</div>

))
}


</div>




<div style={{display:"flex",justifyContent:"center",alignItems:"center",gap:"12px",marginTop:"20px"}}>
  <Button
    disabled={!hasPrevious}
    onClick={() => setPage(p => Math.max(1, p - 1))}
  >
    Previous
  </Button>

  <span>Page {page} of {pages}</span>

  <Button
    disabled={!hasNext}
    onClick={() => setPage(p => p + 1)}
  >
    Next
  </Button>
</div>

</div>



)

}
