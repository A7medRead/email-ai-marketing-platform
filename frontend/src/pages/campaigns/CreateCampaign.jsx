
import {useEffect,useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../api/client";


export default function CreateCampaign(){

const navigate = useNavigate();

const [senders,setSenders]=useState([]);
const [lists,setLists]=useState([]);
const [templates,setTemplates]=useState([]);


const [form,setForm]=useState({
sender_account_id:"",
contact_list_id:"",
template_id:"",
name:"",
subject:"",
body:"",
scheduled_at:null
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



function submit(){

api.post("/campaigns/",form)
.then(()=>{
navigate("/campaigns");
})
.catch(err=>{
console.log(err);
});

}



return (

<div>

<h1>Create Campaign</h1>


<select name="sender_account_id" onChange={change}>
<option>Select Sender</option>

{senders.map(s=>
<option key={s.id} value={s.id}>
{s.name}
</option>
)}

</select>


<br/>


<select name="contact_list_id" onChange={change}>
<option>Select List</option>

{lists.map(l=>
<option key={l.id} value={l.id}>
{l.name}
</option>
)}

</select>


<br/>


<select
name="template_id"
onChange={(e)=>{

const template = templates.find(
t=>String(t.id)===String(e.target.value)
);

setForm(prev=>({
    ...prev,
    template_id:e.target.value,
    subject:template?.subject || "",
    body:template?.body || ""
}));

}}
>
<option>Select Template</option>

{templates.map(t=>
<option key={t.id} value={t.id}>
{t.name}
</option>
)}

</select>


<br/>


<input
name="name"
placeholder="Campaign Name"
onChange={change}
/>


<br/>


<input
name="subject"
placeholder="Subject"
value={form.subject}
onChange={change}
/>


<br/>


<textarea
name="body"
placeholder="Email Body"
value={form.body}
onChange={change}
/>


<br/>


<input
type="datetime-local"
name="scheduled_at"
onChange={change}
/>


<br/>


<button onClick={submit}>
Create Campaign
</button>


</div>

)

}
