import Button from "../../components/Button";
import "./ContactDetails.css";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../api/client";


export default function ContactDetails(){

const { id } = useParams();
const navigate = useNavigate();

const [contact,setContact] = useState(null);


useEffect(()=>{

api.get(`/contacts/${id}`)
.then(res=>{
setContact(res.data);
});

},[id]);


if(!contact){

return (
<div className="page">
<h2>Loading...</h2>
</div>
);

}



async function remove(){

if(!window.confirm("Delete this contact?")) return;

await api.delete(`/contacts/${id}`);

navigate("/contacts");

}



return (

<div className="page">


<div style={{
display:"flex",
justifyContent:"space-between",
alignItems:"center",
marginBottom:"30px"
}}>

<div>

<h1>
{contact.first_name} {contact.last_name}
</h1>

<p className="subtitle">
Contact details
</p>

</div>


<Button
variant="secondary"
onClick={()=>navigate("/contacts")}
>
← Back
</Button>


</div>



<div 
className="contactcontactdetails-details-card contactdetails-details-card"
style={{
maxWidth:"600px",
margin:"40px auto"
}}
>


<div className="contactdetails-avatar">

{contact.first_name?.[0]}
{contact.last_name?.[0]}

</div>



<h2 className="contactdetails-name">

{contact.first_name} {contact.last_name}

</h2>



<p>
📧 {contact.email}
</p>


<p>
🏢 {contact.company || "No Company"}
</p>


<p>
📞 {contact.phone || "No Phone"}
</p>


<p>
💼 {contact.position || "No Position"}
</p>



<span>

{contact.status}

</span>



<div className="contactdetails-actions">


<Button
variant="secondary"
onClick={()=>navigate(`/contacts/${id}/edit`)}
>
✎ Edit
</Button>



<Button
variant="danger"
onClick={remove}
>
🗑 Delete
</Button>


</div>


</div>


</div>

)

}
