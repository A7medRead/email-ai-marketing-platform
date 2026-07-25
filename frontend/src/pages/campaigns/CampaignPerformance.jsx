import Button from "../../components/Button";
import {useEffect,useState} from "react";
import {useParams} from "react-router-dom";
import api from "../../api/client";

import {
BarChart,
Bar,
XAxis,
YAxis,
Tooltip,
ResponsiveContainer,
Cell
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

<Button
variant="secondary"
onClick={()=>window.history.back()}
>
Back
</Button>


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

<div className="card">
<h2>
{data.sent ? Math.round(data.opened/data.sent*100):0}%
</h2>
<p>Open Rate</p>
</div>

<div className="card">
<h2>
{data.sent ? Math.round(data.clicked/data.sent*100):0}%
</h2>
<p>Click Rate</p>
</div>

<div className="card">
<h2>
{data.total ? Math.round(data.sent/data.total*100):0}%
</h2>
<p>Delivery Rate</p>
</div>

<div className="card">
<h2>
{data.total ? Math.round((data.sent-data.failed)/data.total*100):0}%
</h2>
<p>Success Rate</p>
</div>

</div>


<div style={{
width:"100%",
height:"350px",
marginTop:"30px"
}}>

<div style={{
width:"900px",
height:"350px",
margin:"50px auto",
border:"1px solid #333",
borderRadius:"12px",
padding:"20px"
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

<Bar dataKey="value">
{[
"#4ade80",
"#f87171",
"#60a5fa",
"#facc15"
].map((color,index)=>(
<Cell key={index} fill={color}/>
))}
</Bar>

</BarChart>

</ResponsiveContainer>

</div>

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
