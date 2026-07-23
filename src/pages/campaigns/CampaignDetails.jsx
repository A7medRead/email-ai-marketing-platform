import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../../api/client";


export default function CampaignDetails(){

const {id} = useParams();

const [deliveries,setDeliveries] = useState([]);


useEffect(()=>{

api.get(`/campaigns/${id}/deliveries`)
.then(res=>{
setDeliveries(res.data);
});

},[id]);



return (

<div>

<h1>
Campaign Details
</h1>


<h2>
Deliveries
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

<td>
{d.recipient_email}
</td>


<td>
{d.status}
</td>


<td>
{d.sent_at || "-"}
</td>


<td>
{d.opened_at || "-"}
</td>


<td>
{d.clicked_at || "-"}
</td>


</tr>

))

}


</tbody>


</table>


</div>

)

}
