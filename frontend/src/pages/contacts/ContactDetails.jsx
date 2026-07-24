import { useEffect,useState } from "react";
import { useParams,useNavigate } from "react-router-dom";
import api from "../../api/client";


export default function ContactDetails(){

const {id}=useParams();
const navigate=useNavigate();

const [contact,setContact]=useState(null);


useEffect(()=>{

api.get(`/contacts/${id}`)
.then(res=>{
setContact(res.data);
});

},[id]);



if(!contact)
return <h2>Loading...</h2>;



async function remove(){

await api.delete(`/contacts/${id}`);

navigate("/contacts");

}



return (

<div>

<button onClick={()=>navigate("/contacts")}>
← Back
</button>


<h1>
{contact.first_name} {contact.last_name}
</h1>


<div className="card"
style={{
maxWidth:"500px",
marginTop:"30px"
}}>


<p>
📧 {contact.email}
</p>

<p>
🏢 {contact.company}
</p>

<p>
📞 {contact.phone}
</p>

<p>
💼 {contact.position}
</p>

<p>
Status: {contact.status}
</p>


<button onClick={()=>{console.log("EDIT CLICK", id); navigate(`/contacts/${id}/edit`)}}>
Edit
</button>


<button
style={{
marginLeft:"10px"
}}
onClick={remove}
>
Delete
</button>


</div>


</div>

)

}
