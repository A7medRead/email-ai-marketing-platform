import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../../api/client";


export default function CampaignDetails(){

const {id} = useParams();

const [campaign,setCampaign] = useState(null);
const [deliveries,setDeliveries] = useState([]);


useEffect(()=>{

api.get(`/campaigns/${id}`)
.then(res=>{
setCampaign(res.data);
});


api.get(`/campaigns/${id}/deliveries`)
.then(res=>{
setDeliveries(res.data);
});


},[id]);



if(!campaign){

return <h2>Loading...</h2>

}



return (

<div>


<Link to="/campaigns">
Back
</Link>


<h1>
{campaign.name}
</h1>


<div>

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


</div>


<h2>
Email Deliveries
</h2>


<table border="1" cellPadding="10">

<thead>

<tr>
<th>Email</th>
<th>Status</th>
<th>Sent</th>
<th>Opened</th>
<th>Clicked</th>
</tr>

</thead>


<tbody>

{
deliveries.map(d=>(

<tr key={d.id}>

<td>{d.recipient_email}</td>

<td>{d.status}</td>

<td>{d.sent_at || "-"}</td>

<td>{d.opened_at || "-"}</td>

<td>{d.clicked_at || "-"}</td>

</tr>

))
}

</tbody>

</table>


</div>

)

}
