import {useEffect,useState} from "react";
import {useParams} from "react-router-dom";
import api from "../../api/client";

import {
BarChart,
Bar,
XAxis,
YAxis,
Tooltip,
ResponsiveContainer
} from "recharts";


export default function CampaignPerformance(){

const {id}=useParams();

const [data,setData]=useState(null);
const [deliveries,setDeliveries]=useState([]);


useEffect(()=>{

api.get(`/campaigns/${id}/analytics`)
.then(res=>setData(res.data));

api.get(`/campaigns/${id}/deliveries`)
.then(res=>setDeliveries(res.data));

},[id]);


if(!data)
return <h2>Loading...</h2>;


return (

<div style={{
padding:"30px",
width:"100%",
boxSizing:"border-box"
}}>

<button onClick={()=>window.history.back()}>
Back
</button>


<h1>
Campaign Performance
</h1>


<div className="cards" style={{
display:"grid",
gridTemplateColumns:"repeat(4,1fr)",
gap:"20px",
marginTop:"30px",
marginBottom:"40px"
}}>

<div className="card">
<h2>{data.total}</h2>
<p>Total</p>
</div>

<div className="card">
<h2>{data.sent}</h2>
<p>Sent</p>
</div>

<div className="card">
<h2>{data.opened}</h2>
<p>Opened</p>
</div>

<div className="card">
<h2>{data.clicked}</h2>
<p>Clicked</p>
</div>

</div>


<div style={{
width:"100%",
height:"350px",
marginTop:"30px"
}}>

<ResponsiveContainer width="100%" height="100%">

<BarChart
data={[
{name:"Sent",value:data.sent},
{name:"Failed",value:data.failed},
{name:"Opened",value:data.opened},
{name:"Clicked",value:data.clicked}
]}
>

<XAxis dataKey="name"/>

<YAxis/>

<Tooltip/>

<Bar dataKey="value"/>

</BarChart>

</ResponsiveContainer>

</div>



<h2>
Deliveries
</h2>


<table style={{
width:"100%",
marginTop:"30px",
borderCollapse:"collapse"
}}>

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

{deliveries.map(d=>(

<tr key={d.id}>

<td>{d.recipient_email}</td>

<td>{d.status}</td>

<td>{d.sent_at ? "Yes":"-"}</td>

<td>{d.opened_at ? "Yes":"-"}</td>

<td>{d.clicked_at ? "Yes":"-"}</td>

</tr>

))}

</tbody>

</table>


</div>

)

}
