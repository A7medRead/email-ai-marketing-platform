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



async function load(){

const c = await api.get(`/campaigns/${id}`);
setCampaign(c.data);


const d = await api.get(`/campaigns/${id}/deliveries`);
setDeliveries(d.data);

}



useEffect(()=>{

load();

},[id]);



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


<Button
onClick={prepare}
>
Prepare
</Button>


<Button
onClick={send}
>
Send Campaign
</Button>


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



</div>

)

}
