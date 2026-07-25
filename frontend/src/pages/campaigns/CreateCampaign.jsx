import Button from "../../components/Button";
import "./CreateCampaign.css";
import {useEffect,useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../api/client";


export default function CreateCampaign(){

const navigate = useNavigate();


const [senders,setSenders]=useState([]);
const [lists,setLists]=useState([]);
const [templates,setTemplates]=useState([]);

const [error,setError]=useState("");



const [form,setForm]=useState({

sender_account_id:"",
contact_list_id:"",
template_id:"",
name:"",
subject:"",
body:"",
scheduled_at:""

});



useEffect(()=>{


api.get("/sender-accounts/")
.then(res=>setSenders(res.data));


api.get("/contact-lists/")
.then(res=>setLists(res.data));


api.get("/templates/")
.then(res=>setTemplates(res.data.items || res.data));


},[]);




function change(e){

setForm(prev=>({
...prev,
[e.target.name]:e.target.value
}));

}




function selectTemplate(e){

const template = templates.find(
t=>String(t.id)===String(e.target.value)
);


setForm(prev=>({

...prev,

template_id:e.target.value,

subject:template?.subject || "",

body:template?.body || ""

}));

}





async function submit(){

setError("");

if(
!form.sender_account_id ||
!form.contact_list_id ||
!form.name ||
!form.subject ||
!form.body
){

setError(
"Please complete all required fields."
);

return;

}



try{

const payload = {
    ...form,
    sender_account_id: Number(form.sender_account_id),
    contact_list_id: Number(form.contact_list_id),
    template_id: form.template_id
        ? Number(form.template_id)
        : null,
    scheduled_at: form.scheduled_at || null
};


await api.post(
"/campaigns/",
payload
);

navigate("/campaigns");


}
catch(err){

const detail = err.response?.data?.detail;

setError(
    typeof detail === "string"
    ? detail
    : JSON.stringify(detail)
    || "Failed to create campaign."
);

}

}





return (

<div className="page create-campaign-page">

<div className="create-campaign-card">


<Button
variant="secondary"
onClick={()=>navigate("/campaigns")}
>
← Back
</Button>


<h1>
Create Campaign
</h1>


<p className="subtitle">
Create and send email campaigns
</p>



<div
style={{
maxWidth:"700px",
background:"#16171d",
padding:"30px",
borderRadius:"16px",
marginTop:"30px"
}}
>



<h3>
Campaign Setup
</h3>


<select
name="sender_account_id"
onChange={change}
style={{width:"100%",marginBottom:"15px"}}
>

<option value="">
Select Sender
</option>


{
senders.map(s=>(

<option key={s.id} value={s.id}>

{s.name} - {s.status}

</option>

))
}


</select>



<select
name="contact_list_id"
onChange={change}
style={{width:"100%",marginBottom:"15px"}}
>

<option value="">
Select Audience List
</option>


{
lists.map(l=>(

<option key={l.id} value={l.id}>

{l.name} ({l.contacts_count ?? 0} contacts)

</option>

))
}


</select>





<h3>
Email Content
</h3>



<label className="form-label">Email Template</label>
<select
name="template_id"
onChange={selectTemplate}
style={{width:"100%",marginBottom:"15px"}}
>


<option value="">
Select Template
</option>


{
templates.map(t=>(

<option key={t.id} value={t.id}>

{t.name}

</option>

))
}


</select>




<label className="form-label">Campaign Name</label>
<input
name="name"
placeholder="Campaign Name"
value={form.name}
onChange={change}
style={{width:"100%",marginBottom:"15px"}}
/>





<label className="form-label">Email Subject</label>
<input
name="subject"
placeholder="Email Subject"
value={form.subject}
onChange={change}
style={{width:"100%",marginBottom:"15px"}}
/>





<label className="form-label">Email Body</label>
<textarea
name="body"
placeholder="Email Body"
rows="8"
value={form.body}
onChange={change}
style={{width:"100%",marginBottom:"15px"}}
/>





<h3>
Schedule
</h3>


<input
type="datetime-local"
name="scheduled_at"
onChange={change}
style={{width:"100%",marginBottom:"15px"}}
/>




{
error &&

<p>
{
 typeof error === "object"
 ? JSON.stringify(error)
 : error
}
</p>

}





<Button
onClick={submit}
>
🚀 Create Campaign
</Button>



</div>



</div>

</div>

)

}
