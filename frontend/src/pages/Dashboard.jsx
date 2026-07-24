import {useEffect,useState} from "react";
import api from "../api/client";

import {
BarChart,
Bar,
PieChart,
Pie,
Cell,
XAxis,
YAxis,
Tooltip,
ResponsiveContainer,
Legend
} from "recharts";


export default function Dashboard(){

const [stats,setStats]=useState(null);
const [campaigns,setCampaigns]=useState([]);


useEffect(()=>{

api.get("/dashboard/marketing")
.then(res=>setStats(res.data));


api.get("/campaigns")
.then(res=>setCampaigns(res.data));

},[]);


if(!stats)
return <h2>Loading...</h2>;


const data=[
{name:"Sent",value:stats.sent},
{name:"Failed",value:stats.failed},
{name:"Opened",value:stats.opened},
{name:"Clicked",value:stats.clicked}
];


return (

<div className="dashboard">


<h1>Marketing Dashboard</h1>


<div className="cards">

{[
["Campaigns",stats.campaigns],
["Recipients",stats.recipients],
["Sent",stats.sent],
["Failed",stats.failed],
["Opened",stats.opened],
["Clicked",stats.clicked]
].map(x=>(

<div className="card" key={x[0]}>
<h2>{x[1]}</h2>
<p>{x[0]}</p>
</div>

))}

</div>



<div style={{display:"flex",gap:"40px",marginTop:"40px"}}>


<div style={{height:300,width:450}}>

<ResponsiveContainer>

<BarChart data={data}>

<XAxis dataKey="name"/>

<YAxis/>

<Tooltip/>

<Bar dataKey="value"/>

</BarChart>

</ResponsiveContainer>

</div>



<div style={{height:300,width:350}}>

<ResponsiveContainer>

<PieChart>

<Pie data={data} dataKey="value" outerRadius={100} label>

{data.map((x,i)=>
<Cell key={i}/>
)}

</Pie>

<Tooltip/>

<Legend/>

</PieChart>

</ResponsiveContainer>

</div>


</div>



<h2 style={{marginTop:"50px"}}>
Recent Campaigns
</h2>


<table style={{
width:"100%",
borderCollapse:"collapse"
}}>

<thead>

<tr>
<th>Name</th>
<th>Status</th>
<th>Sent</th>
<th>Failed</th>
</tr>

</thead>


<tbody>

{campaigns.slice(0,5).map(c=>(

<tr key={c.id}>

<td>{c.name}</td>

<td>{c.status}</td>

<td>{c.sent_count}</td>

<td>{c.failed_count}</td>

</tr>

))}

</tbody>


</table>


</div>

)

}
