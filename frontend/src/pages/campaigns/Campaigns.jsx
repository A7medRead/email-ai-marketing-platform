import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";


export default function Campaigns(){

const [campaigns,setCampaigns] = useState([]);
const [loading,setLoading] = useState(null);


function load(){

api.get("/campaigns/")
.then(res=>{
setCampaigns(res.data);
});

}


useEffect(()=>{

load();

},[]);



async function prepare(id){

setLoading(id);

await api.post(
`/campaigns/${id}/prepare`
);

load();

setLoading(null);

}



async function send(id){

setLoading(id);

await api.post(
`/campaigns/${id}/send`
);


setTimeout(()=>{

load();

setLoading(null);

},3000);

}



return (

<div>

<h1>
Campaigns
</h1>


<Link to="/campaigns/create">

<button>
+ Create Campaign
</button>

</Link>



<div style={{
display:"grid",
gridTemplateColumns:"repeat(3,1fr)",
gap:"20px",
marginTop:"30px"
}}>


{
campaigns.map(c=>(

<div
key={c.id}
style={{
border:"1px solid #444",
padding:"20px",
borderRadius:"12px"
}}
>


<h3>
{c.name}
</h3>


<p>
Status: {c.status}
</p>


<p>
Recipients: {c.total_recipients}
</p>


<p>
Sent: {c.sent_count}
</p>


<p>
Failed: {c.failed_count}
</p>



<button
disabled={
c.status === "COMPLETED" ||
c.status === "completed" ||
loading === c.id
}
onClick={()=>prepare(c.id)}
>

{
loading === c.id
?
"Working..."
:
"Prepare"
}

</button>



<button
disabled={
c.status === "COMPLETED" ||
c.status === "completed" ||
c.status === "FAILED" ||
c.status === "failed" ||
loading === c.id
}
onClick={()=>send(c.id)}
style={{
marginLeft:"10px"
}}
>

{
loading === c.id
?
"Sending..."
:
"Send"
}

</button>



<br/><br/>


<Link to={`/campaigns/${c.id}/analytics`}>
<button>
Analytics
</button>
</Link>


<Link to={`/campaigns/${c.id}/details`}>
<button style={{
marginLeft:"10px"
}}>
Details
</button>
</Link>


<Link to={`/campaigns/${c.id}/performance`}>
<button style={{
marginLeft:"10px"
}}>
Performance
</button>
</Link>


</div>

))
}


</div>


</div>

)

}
