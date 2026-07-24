import {useEffect,useState} from "react";
import { Link } from "react-router-dom";
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
const [marketing,setMarketing]=useState(null);
const [campaigns,setCampaigns]=useState([]);


useEffect(()=>{

api.get("/dashboard/analytics")
.then(res=>setStats(res.data));


api.get("/dashboard/marketing")
.then(res=>setMarketing(res.data));


api.get("/dashboard/top-campaigns")
.then(res=>setCampaigns(res.data));

},[]);



if(!stats || !marketing)
return <h2>Loading...</h2>;



const data=[

{
name:"Sent",
value:stats.total_sent
},

{
name:"Failed",
value:stats.total_failed
},

{
name:"Opened",
value:marketing.opened
},

{
name:"Clicked",
value:marketing.clicked
}

];



const openRate = stats.total_sent
? ((marketing.opened / stats.total_sent) * 100).toFixed(2)
: 0;


const clickRate = stats.total_sent
? ((marketing.clicked / stats.total_sent) * 100).toFixed(2)
: 0;



const cards=[

["📣","Campaigns",stats.total_campaigns],

["✉️","Sent",stats.total_sent],

["👁","Open Rate %",openRate],

["🎯","Success %",stats.success_rate],

["🖱","Click Rate %",clickRate],

["⚠️","Failed",stats.total_failed]

];



return (

<div className="dashboard">


<div className="dashboard-header">

<div className="dashboard-title-row">

<div>

<h1>
Marketing Dashboard
</h1>

<p>
Monitor your email marketing performance
</p>

</div>


<Link to="/campaigns/create">

<button className="create-btn">
+ Create Campaign
</button>

</Link>


</div>

</div>



<div className="cards">

{cards.map(card=>(

<div className="card dashboard-card" key={card[1]}>

<div className="card-icon">
{card[0]}
</div>

<h2>
{card[2]}
</h2>

<p>
{card[1]}
</p>

</div>

))}

</div>





<div className="charts">


<div className="chart-box">

<h3>
Email Performance
</h3>

<ResponsiveContainer width="100%" height={300}>

<BarChart data={data}>

<XAxis dataKey="name"/>

<YAxis/>

<Tooltip/>

<Bar dataKey="value"/>

</BarChart>

</ResponsiveContainer>

</div>




<div className="chart-box">

<h3>
Delivery Overview
</h3>


<ResponsiveContainer width="100%" height={300}>

<PieChart>

<Pie
data={data}
dataKey="value"
outerRadius={100}
label
>

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





<div className="recent-section">


<h2>
Recent Campaigns
</h2>



<table>

<thead>

<tr>

<th>Name</th>
<th>Status</th>
<th>Sent</th>
<th>Failed</th>
<th>Success</th>
<th></th>

</tr>

</thead>



<tbody>


{campaigns.slice(0,5).map(c=>(


<tr key={c.id}>


<td>
{c.name}
</td>


<td>
<span className="status">
{c.status}
</span>
</td>


<td>
{c.sent}
</td>


<td>
{c.failed}
</td>


<td>
{c.success_rate}%
</td>


<td>

<Link to={`/campaigns/${c.id}/details`}>

<button>
View
</button>

</Link>

</td>


</tr>


))}


</tbody>


</table>


</div>



</div>

)

}
