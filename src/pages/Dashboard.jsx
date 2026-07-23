import { useEffect,useState } from "react";
import api from "../api/client";
import {
BarChart,
Bar,
XAxis,
YAxis,
Tooltip,
ResponsiveContainer
} from "recharts";


export default function Dashboard(){

const [stats,setStats]=useState(null);


useEffect(()=>{

api.get("/dashboard/marketing")
.then(res=>setStats(res.data));

},[]);



if(!stats)
return <h2>Loading...</h2>



const data=[
{
name:"Sent",
value:stats.sent
},
{
name:"Failed",
value:stats.failed
},
{
name:"Opened",
value:stats.opened
},
{
name:"Clicked",
value:stats.clicked
}
];


return (

<div>

<h1>
Marketing Dashboard
</h1>


<div style={{
width:"700px",
height:"300px"
}}>

<ResponsiveContainer>

<BarChart data={data}>

<XAxis dataKey="name"/>

<YAxis/>

<Tooltip/>

<Bar
dataKey="value"
/>

</BarChart>

</ResponsiveContainer>

</div>


</div>

)

}
