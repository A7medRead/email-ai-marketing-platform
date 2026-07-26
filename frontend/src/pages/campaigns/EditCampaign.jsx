import Button from "../../components/Button";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../api/client";


export default function EditCampaign(){

const {id}=useParams();
const navigate=useNavigate();

const [form,setForm]=useState({
name:"",
from_name:"",
subject:"",
body:""
});

const [error,setError]=useState("");


useEffect(()=>{

api.get(`/campaigns/${id}`)
.then(res=>{

setForm({
name:res.data.name || "",
from_name:res.data.from_name || "",
subject:res.data.subject || "",
body:res.data.body || ""
});

});

},[id]);



function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function save(){

try{

await api.put(
`/campaigns/${id}`,
form
);

navigate(`/campaigns/${id}/details`);

}
catch(err){

console.log(err);

setError("Update failed");

}

}



return (

<div className="page">

<Button
variant="secondary"
onClick={()=>navigate(-1)}
>
← Back
</Button>


<h1>
Edit Campaign
</h1>


<input
name="name"
placeholder="Campaign Name"
value={form.name}
onChange={change}
/>


<input
name="from_name"
placeholder="From Name"
value={form.from_name}
onChange={change}
/>


<input
name="subject"
placeholder="Subject"
value={form.subject}
onChange={change}
/>


<textarea
name="body"
rows="10"
placeholder="Body"
value={form.body}
onChange={change}
/>


{
error &&
<p>{error}</p>
}


<Button
onClick={save}
>
Save Changes
</Button>


</div>

)

}
