import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";


export default function CreateCampaign(){

const navigate = useNavigate();


const [form,setForm] = useState({

sender_account_id:4,
contact_list_id:1,
name:"",
subject:"",
body:""

});


function update(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function submit(e){

e.preventDefault();


await api.post(
"/campaigns/",
{
...form,
sender_account_id:Number(form.sender_account_id),
contact_list_id:Number(form.contact_list_id)
}
);


navigate("/campaigns");

}



return (

<div>

<h1>
Create Campaign
</h1>


<form onSubmit={submit}>


<input
name="name"
placeholder="Campaign name"
value={form.name}
onChange={update}
/>


<br/>


<input
name="subject"
placeholder="Subject"
value={form.subject}
onChange={update}
/>


<br/>


<textarea
name="body"
placeholder="Email body"
value={form.body}
onChange={update}
/>


<br/>


<button>
Create
</button>


</form>


</div>

)

}
