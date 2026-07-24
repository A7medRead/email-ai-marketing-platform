import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../../api/client";


export default function Analytics(){

const {id} = useParams();

const [data,setData] = useState(null);


useEffect(()=>{

api.get(`/campaigns/${id}/analytics`)
.then(res=>{
setData(res.data);
});

},[id]);



if(!data){

return <h2>Loading...</h2>

}



const stats = [

["Total", data.total],

["Sent", data.sent],

["Failed", data.failed],

["Opened", data.opened],

["Clicked", data.clicked],

["Bounced", data.bounced],

];



return (

<div>


<h1>
Campaign Analytics
</h1>


<h3>
Campaign ID: {data.campaign_id}
</h3>



<div style={{
display:"grid",
gridTemplateColumns:"repeat(3,1fr)",
gap:"20px",
marginTop:"30px"
}}>


{
stats.map(item=>(

<div
key={item[0]}
style={{
border:"1px solid #444",
padding:"25px",
borderRadius:"12px"
}}
>

<h2>
{item[1]}
</h2>


<p>
{item[0]}
</p>


</div>

))
}


</div>


</div>

)

}
