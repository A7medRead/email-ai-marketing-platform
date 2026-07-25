import { useEffect,useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";


export default function SenderAccounts(){

const [senders,setSenders]=useState([]);
const navigate=useNavigate();


async function load(){

const res = await api.get("/sender-accounts/");
setSenders(res.data);

}


useEffect(()=>{

load();

},[]);



async function remove(id){

const ok = window.confirm(
"Are you sure you want to delete this sender account?"
);

if(!ok) return;

await api.delete(`/sender-accounts/${id}`);

load();

}



async function verify(id){

await api.post(`/sender-accounts/${id}/verify`);

load();

}



async function sendTest(id){

const email = window.prompt(
"Enter test email address"
);

if(!email) return;


await api.post(
`/sender-accounts/${id}/send-test`,
{
recipient_email:email
}
);

alert("Test email sent");

}



return (

<div className="page">


<div className="contacts-header">

<div>

<h1>
Sender Accounts
</h1>

<p className="subtitle">
Manage your email sending accounts
</p>

</div>


<button
className="add-contact-btn"
onClick={()=>navigate("/senders/create")}
>
+ Add Sender
</button>


</div>



<div className="contact-cards">


{
senders.map(sender=>(

<div className="contact-card" key={sender.id}>


<div className="contact-avatar">
✉️
</div>


<h2>
{sender.name}
</h2>


<p>
{sender.email}
</p>


<p>
Provider: {sender.provider}
</p>


<span>
Status: {sender.status}
</span>



<div className="contact-actions">


<button
onClick={()=>navigate(`/senders/${sender.id}/edit`)}
>
✎ Edit
</button>


<button
onClick={()=>verify(sender.id)}
>
✓ Verify
</button>


<button
onClick={()=>sendTest(sender.id)}
>
📨 Test
</button>


<button
onClick={()=>remove(sender.id)}
>
🗑 Delete
</button>


</div>


</div>

))
}


</div>


</div>

)

}
